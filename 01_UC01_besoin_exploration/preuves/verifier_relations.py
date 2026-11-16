"""Étape D - Vérification des relations entre tables.

Usage : python verifier_relations.py <dossier retail_project/data>
Pour chaque relation : nombre de valeurs vides, nombre de valeurs
sans correspondance (orphelines) dans la table de référence.
"""
import os
import sys
from collections import defaultdict

DATA = sys.argv[1]


def lire(table):
    with open(os.path.join(DATA, table, table + ".dat"), encoding="utf-8", errors="replace") as f:
        for ligne in f:
            yield [v.strip() for v in ligne.rstrip("\r\n").split("|")]


def cles(table, pos=0):
    return {c[pos] for c in lire(table)}


REF = {t: cles(t) for t in ["item", "store", "customer", "date_dim", "time_dim",
                            "promotion", "warehouse", "web_site", "web_page", "reason"]}

# (table de faits, position de la colonne, nom de la colonne, table de référence)
RELATIONS = [
    ("store_sales", 0, "ss_sold_date_sk", "date_dim"),
    ("store_sales", 1, "ss_sold_time_sk", "time_dim"),
    ("store_sales", 2, "ss_item_sk", "item"),
    ("store_sales", 3, "ss_customer_sk", "customer"),
    ("store_sales", 7, "ss_store_sk", "store"),
    ("store_sales", 8, "ss_promo_sk", "promotion"),
    ("web_sales", 0, "ws_sold_date_sk", "date_dim"),
    ("web_sales", 3, "ws_item_sk", "item"),
    ("web_sales", 4, "ws_bill_customer_sk", "customer"),
    ("web_sales", 13, "ws_web_site_sk", "web_site"),
    ("web_sales", 12, "ws_web_page_sk", "web_page"),
    ("web_sales", 15, "ws_warehouse_sk", "warehouse"),
    ("store_returns", 2, "sr_item_sk", "item"),
    ("store_returns", 7, "sr_store_sk", "store"),
    ("store_returns", 8, "sr_reason_sk", "reason"),
    ("web_returns", 2, "wr_item_sk", "item"),
    ("web_returns", 12, "wr_reason_sk", "reason"),
    ("inventory", 1, "inv_item_sk", "item"),
    ("inventory", 2, "inv_warehouse_sk", "warehouse"),
    ("web_clickstreams", 3, "wcs_item_sk", "item"),
]

print("relation;lignes;vides;sans_correspondance")
par_table = defaultdict(list)
for t, pos, nom, ref in RELATIONS:
    par_table[t].append((pos, nom, ref))
for t, rels in par_table.items():
    n = 0
    vides = defaultdict(int)
    orph = defaultdict(int)
    for c in lire(t):
        n += 1
        for pos, nom, ref in rels:
            v = c[pos]
            if v == "":
                vides[nom] += 1
            elif v not in REF[ref]:
                orph[nom] += 1
    for pos, nom, ref in rels:
        print(f"{t}.{nom} -> {ref};{n};{vides[nom]};{orph[nom]}")

# Le numéro de ticket est-il unique dans toute l'entreprise ?
magasins_par_ticket = defaultdict(set)
lignes_par_ticket_item = defaultdict(int)
ventes = set()
for c in lire("store_sales"):
    magasins_par_ticket[c[9]].add(c[7])
    lignes_par_ticket_item[(c[9], c[2])] += 1
    ventes.add((c[9], c[2]))
print()
print("tickets présents dans plusieurs magasins;",
      sum(1 for s in magasins_par_ticket.values() if len(s) > 1))
print("couples (ticket, produit) en double dans store_sales;",
      sum(1 for v in lignes_par_ticket_item.values() if v > 1))
tailles = defaultdict(int)
for (ticket, _item) in ventes:
    tailles[ticket] += 1
v = list(tailles.values())
print(f"lignes par ticket (min / moyenne / max);{min(v)};{sum(v)/len(v):.1f};{max(v)}")

# Les retours magasin correspondent-ils à une vente ?
sans_vente = sum(1 for c in lire("store_returns") if (c[9], c[2]) not in ventes)
print("retours magasin sans vente correspondante (ticket + produit);", sans_vente)

commandes = {(c[17], c[3]) for c in lire("web_sales")}
sans_cmd = sum(1 for c in lire("web_returns") if (c[13], c[2]) not in commandes)
print("retours web sans vente correspondante (commande + produit);", sans_cmd)
