"""Etape C - Profilage des fichiers TPCx-BB (data + data_refresh).

Usage : python -I etape_c_profilage.py <racine_retail_project> <fichier_sortie.json>

Les fichiers .dat n'ont pas d'en-tete : les noms et types de colonnes viennent
du script de chargement Hive de la specification TPCx-BB v1.7.0 (Annexe I),
extraits dans tpcxbb_schema.json.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

CHUNK = 1_000_000
DISTINCT_CAP = 3_000_000
HERE = Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / "tpcxbb_schema.json").read_text())

NUM_TYPES = ("bigint", "int", "decimal", "double")


def kind(t):
    t = t.lower()
    if t.startswith(NUM_TYPES):
        return "num"
    if t.startswith("date"):
        return "date"
    return "str"


def field_counts(path):
    """Distribution du nombre de champs par ligne (detecte les lignes mal formees)."""
    dist = {}
    with open(path, "rb") as f:
        for line in f:
            n = line.rstrip(b"\r\n").count(b"|") + 1
            dist[n] = dist.get(n, 0) + 1
    return dist


def profile_file(path, table):
    cols = SCHEMA[table]
    names = [c[0] for c in cols]
    fc = field_counts(path)
    max_fields = max(fc)
    read_names = names + [f"_extra{i}" for i in range(max(0, max_fields - len(names)))]

    st = {n: dict(type=t, not_null_spec=nn, nulls=0, cast_fail=0, min=None, max=None,
                  neg=0, distinct=set(), capped=False, maxlen=0, cast_fail_ex=[])
          for n, t, nn in cols}
    rows = 0
    pk_vals = []
    reader = pd.read_csv(path, sep="|", header=None, names=read_names, dtype=str,
                         keep_default_na=False, quoting=3, chunksize=CHUNK,
                         engine="c", encoding="utf-8", encoding_errors="replace")
    for df in reader:
        rows += len(df)
        for n, t, _ in cols:
            s = st[n]
            v = df[n]
            empty = v == ""
            s["nulls"] += int(empty.sum())
            v = v[~empty]
            if v.empty:
                continue
            k = kind(t)
            if k == "num":
                x = pd.to_numeric(v, errors="coerce")
                bad = x.isna()
                s["cast_fail"] += int(bad.sum())
                if bad.any() and len(s["cast_fail_ex"]) < 3:
                    s["cast_fail_ex"] += v[bad].unique()[:3].tolist()
                x = x[~bad]
                if len(x):
                    s["min"] = x.min() if s["min"] is None else min(s["min"], x.min())
                    s["max"] = x.max() if s["max"] is None else max(s["max"], x.max())
                    s["neg"] += int((x < 0).sum())
            elif k == "date":
                x = pd.to_datetime(v, errors="coerce", format="%Y-%m-%d")
                bad = x.isna()
                s["cast_fail"] += int(bad.sum())
                if bad.any() and len(s["cast_fail_ex"]) < 3:
                    s["cast_fail_ex"] += v[bad].unique()[:3].tolist()
                x = x[~bad]
                if len(x):
                    s["min"] = x.min() if s["min"] is None else min(s["min"], x.min())
                    s["max"] = x.max() if s["max"] is None else max(s["max"], x.max())
            else:
                s["maxlen"] = max(s["maxlen"], int(v.str.len().max()))
            if not s["capped"]:
                s["distinct"].update(v.unique().tolist())
                if len(s["distinct"]) > DISTINCT_CAP:
                    s["capped"] = True
                    s["distinct"] = set()
        pk_vals.append(df[names[0]].values)

    out_cols = {}
    for n, s in st.items():
        d = len(s["distinct"])
        top = None
        if not s["capped"] and 0 < d <= 12 and kind(s["type"]) == "str":
            top = sorted(s["distinct"])
        out_cols[n] = dict(
            type=s["type"], not_null_spec=s["not_null_spec"], nulls=s["nulls"],
            null_pct=round(100 * s["nulls"] / rows, 3) if rows else None,
            cast_fail=s["cast_fail"], cast_fail_ex=s["cast_fail_ex"],
            min=None if s["min"] is None else str(s["min"]),
            max=None if s["max"] is None else str(s["max"]),
            neg=s["neg"], distinct=(f">{DISTINCT_CAP}" if s["capped"] else d),
            unique=(not s["capped"] and d == rows - s["nulls"] and s["nulls"] == 0),
            maxlen=s["maxlen"] or None, values=top)
    return dict(table=table, path=str(path), size_bytes=os.path.getsize(path), rows=rows,
                n_cols_spec=len(names), field_count_dist={str(k): v for k, v in fc.items()},
                columns=out_cols)


def composite_dups(path, table, key_cols):
    names = [c[0] for c in SCHEMA[table]]
    df = pd.read_csv(path, sep="|", header=None, names=names, usecols=key_cols,
                     dtype=str, keep_default_na=False, quoting=3)
    return int(df.duplicated(subset=key_cols).sum()), int(len(df))


def main():
    root = Path(sys.argv[1])
    out = Path(sys.argv[2])
    res = {"files": [], "composite_keys": {}}
    for zone in ("data", "data_refresh"):
        for d in sorted((root / zone).iterdir()):
            for f in sorted(d.iterdir()):
                entry = dict(zone=zone, folder=d.name, file=f.name, ext=f.suffix,
                             size_bytes=os.path.getsize(f))
                if f.suffix == ".dat" and d.name in SCHEMA:
                    print("profiling", zone, f.name, flush=True)
                    entry["profile"] = profile_file(f, d.name)
                else:
                    entry["preview"] = f.read_text(encoding="utf-8", errors="replace")[:1500]
                res["files"].append(entry)
    keys = {"inventory": ["inv_date_sk", "inv_item_sk", "inv_warehouse_sk"],
            "store_sales": ["ss_item_sk", "ss_ticket_number"],
            "web_sales": ["ws_item_sk", "ws_order_number"],
            "store_returns": ["sr_item_sk", "sr_ticket_number"],
            "web_returns": ["wr_item_sk", "wr_order_number"],
            "web_clickstreams": ["wcs_click_date_sk", "wcs_click_time_sk", "wcs_user_sk", "wcs_item_sk"]}
    for t, k in keys.items():
        for zone in ("data", "data_refresh"):
            p = root / zone / t / f"{t}.dat"
            if p.exists():
                print("dups", zone, t, flush=True)
                res["composite_keys"][f"{zone}/{t}"] = dict(key=k, dup_and_total=composite_dups(p, t, k))
    out.write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
