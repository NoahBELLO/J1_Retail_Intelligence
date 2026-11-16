"""Etape D - Verification des relations entre tables TPCx-BB.

Usage : python -I etape_d_relations.py <racine_retail_project> <fichier_sortie.json>

Pour chaque relation candidate (colonne enfant -> colonne parent) :
presence des colonnes, types declares, valeurs distinctes, doublons cote parent,
valeurs sans correspondance (orphelins), sur data seul et sur data + data_refresh.
"""
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / "tpcxbb_schema.json").read_text())
TYPES = {t: {c[0]: c[1] for c in cols} for t, cols in SCHEMA.items()}

# (table enfant, colonne(s) enfant, table parent, colonne(s) parent, domaine)
RELATIONS = [
    # Ventes magasin
    ("store_sales", ["ss_item_sk"], "item", ["i_item_sk"], "ventes-produits"),
    ("store_sales", ["ss_customer_sk"], "customer", ["c_customer_sk"], "ventes-clients"),
    ("store_sales", ["ss_store_sk"], "store", ["s_store_sk"], "ventes-magasins"),
    ("store_sales", ["ss_sold_date_sk"], "date_dim", ["d_date_sk"], "ventes-dates"),
    ("store_sales", ["ss_sold_time_sk"], "time_dim", ["t_time_sk"], "ventes-dates"),
    ("store_sales", ["ss_promo_sk"], "promotion", ["p_promo_sk"], "ventes-autres"),
    ("store_sales", ["ss_addr_sk"], "customer_address", ["ca_address_sk"], "ventes-clients"),
    ("store_sales", ["ss_cdemo_sk"], "customer_demographics", ["cd_demo_sk"], "ventes-clients"),
    ("store_sales", ["ss_hdemo_sk"], "household_demographics", ["hd_demo_sk"], "ventes-clients"),
    # Ventes web
    ("web_sales", ["ws_item_sk"], "item", ["i_item_sk"], "ventes-produits"),
    ("web_sales", ["ws_bill_customer_sk"], "customer", ["c_customer_sk"], "ventes-clients"),
    ("web_sales", ["ws_ship_customer_sk"], "customer", ["c_customer_sk"], "ventes-clients"),
    ("web_sales", ["ws_sold_date_sk"], "date_dim", ["d_date_sk"], "ventes-dates"),
    ("web_sales", ["ws_ship_date_sk"], "date_dim", ["d_date_sk"], "ventes-dates"),
    ("web_sales", ["ws_sold_time_sk"], "time_dim", ["t_time_sk"], "ventes-dates"),
    ("web_sales", ["ws_web_site_sk"], "web_site", ["web_site_sk"], "ventes-magasins"),
    ("web_sales", ["ws_web_page_sk"], "web_page", ["wp_web_page_sk"], "ventes-autres"),
    ("web_sales", ["ws_warehouse_sk"], "warehouse", ["w_warehouse_sk"], "ventes-autres"),
    ("web_sales", ["ws_ship_mode_sk"], "ship_mode", ["sm_ship_mode_sk"], "ventes-autres"),
    ("web_sales", ["ws_promo_sk"], "promotion", ["p_promo_sk"], "ventes-autres"),
    ("web_sales", ["ws_bill_addr_sk"], "customer_address", ["ca_address_sk"], "ventes-clients"),
    # Retours
    ("store_returns", ["sr_item_sk", "sr_ticket_number"], "store_sales", ["ss_item_sk", "ss_ticket_number"], "retours-ventes"),
    ("store_returns", ["sr_customer_sk"], "customer", ["c_customer_sk"], "retours-ventes"),
    ("store_returns", ["sr_store_sk"], "store", ["s_store_sk"], "retours-ventes"),
    ("store_returns", ["sr_returned_date_sk"], "date_dim", ["d_date_sk"], "retours-ventes"),
    ("store_returns", ["sr_reason_sk"], "reason", ["r_reason_sk"], "retours-ventes"),
    ("web_returns", ["wr_item_sk", "wr_order_number"], "web_sales", ["ws_item_sk", "ws_order_number"], "retours-ventes"),
    ("web_returns", ["wr_returning_customer_sk"], "customer", ["c_customer_sk"], "retours-ventes"),
    ("web_returns", ["wr_returned_date_sk"], "date_dim", ["d_date_sk"], "retours-ventes"),
    ("web_returns", ["wr_reason_sk"], "reason", ["r_reason_sk"], "retours-ventes"),
    # Stock, prix, avis, clics
    ("inventory", ["inv_item_sk"], "item", ["i_item_sk"], "stock"),
    ("inventory", ["inv_warehouse_sk"], "warehouse", ["w_warehouse_sk"], "stock"),
    ("inventory", ["inv_date_sk"], "date_dim", ["d_date_sk"], "stock"),
    ("item_marketprices", ["imp_item_sk"], "item", ["i_item_sk"], "produits"),
    ("product_reviews", ["pr_item_sk"], "item", ["i_item_sk"], "produits"),
    ("product_reviews", ["pr_user_sk"], "customer", ["c_customer_sk"], "clients"),
    ("web_clickstreams", ["wcs_item_sk"], "item", ["i_item_sk"], "produits"),
    ("web_clickstreams", ["wcs_user_sk"], "customer", ["c_customer_sk"], "clients"),
    ("web_clickstreams", ["wcs_click_date_sk"], "date_dim", ["d_date_sk"], "ventes-dates"),
    # Client -> referentiels
    ("customer", ["c_current_addr_sk"], "customer_address", ["ca_address_sk"], "clients"),
    ("customer", ["c_current_cdemo_sk"], "customer_demographics", ["cd_demo_sk"], "clients"),
    ("customer", ["c_current_hdemo_sk"], "household_demographics", ["hd_demo_sk"], "clients"),
    ("customer", ["c_first_sales_date_sk"], "date_dim", ["d_date_sk"], "clients"),
    ("household_demographics", ["hd_income_band_sk"], "income_band", ["ib_income_band_sk"], "clients"),
    # Relations implicites (non declarees, a confirmer)
    ("product_reviews", ["pr_order_sk"], "web_sales", ["ws_order_number"], "a-confirmer"),
    ("product_reviews", ["pr_order_sk"], "store_sales", ["ss_ticket_number"], "a-confirmer"),
    ("web_clickstreams", ["wcs_sales_sk"], "web_sales", ["ws_order_number"], "a-confirmer"),
    ("item_marketprices", ["imp_start_date"], "date_dim", ["d_date_sk"], "a-confirmer"),
    ("store", ["s_closed_date_sk"], "date_dim", ["d_date_sk"], "a-confirmer"),
]

_cache = {}


def load(root, zone, table, cols):
    key = (zone, table, tuple(cols))
    if key not in _cache:
        p = root / zone / table / f"{table}.dat"
        if not p.exists():
            _cache[key] = None
        else:
            names = [c[0] for c in SCHEMA[table]]
            _cache[key] = pd.read_csv(p, sep="|", header=None, names=names, usecols=cols,
                                      dtype="Int64", quoting=3)
    return _cache[key]


def both(root, table, cols):
    parts = [d for d in (load(root, z, table, cols) for z in ("data", "data_refresh")) if d is not None]
    return pd.concat(parts, ignore_index=True)


def check(root, child, ccols, parent, pcols):
    missing = [c for c in ccols if c not in TYPES[child]] + [c for c in pcols if c not in TYPES[parent]]
    if missing:
        return dict(missing_columns=missing)
    res = dict(
        child_types=[TYPES[child][c] for c in ccols],
        parent_types=[TYPES[parent][c] for c in pcols],
    )
    res["types_ok"] = res["child_types"] == res["parent_types"]
    for scope in ("data", "data+refresh"):
        if scope == "data":
            ch = load(root, "data", child, ccols)
            pa = load(root, "data", parent, pcols)
        else:
            ch = both(root, child, ccols)
            pa = both(root, parent, pcols)
        ch_nn = ch.dropna()
        pa_keys = pa.dropna().drop_duplicates()
        pa_keys.columns = ccols
        m = ch_nn.merge(pa_keys.assign(_ok=1), on=ccols, how="left")
        orph = m[m["_ok"].isna()]
        ch_dist = ch_nn.drop_duplicates()
        res[scope] = dict(
            child_rows=int(len(ch)),
            child_nulls=int(len(ch) - len(ch_nn)),
            child_distinct=int(len(ch_dist)),
            parent_rows=int(len(pa)),
            parent_distinct=int(len(pa_keys)),
            parent_duplicates=int(len(pa.dropna()) - len(pa_keys)),
            orphan_rows=int(len(orph)),
            orphan_pct=round(100 * len(orph) / len(ch_nn), 3) if len(ch_nn) else None,
            orphan_distinct=int(len(orph[ccols].drop_duplicates())),
            orphan_examples=orph[ccols].drop_duplicates().head(5).astype(str).values.tolist(),
            parent_unused=int(len(pa_keys) - len(ch_dist.merge(pa_keys, on=ccols))),
        )
    return res


def main():
    root = Path(sys.argv[1])
    out = []
    for child, ccols, parent, pcols, dom in RELATIONS:
        print(f"{child}.{'+'.join(ccols)} -> {parent}.{'+'.join(pcols)}", flush=True)
        out.append(dict(domain=dom, child=child, child_cols=ccols, parent=parent, parent_cols=pcols,
                        **check(root, child, ccols, parent, pcols)))
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
