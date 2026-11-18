"""Étape 9 : contrôles qualité sur les données silver et gold.

Chaque contrôle donne un statut :
- OK        : la règle est respectée ;
- KO        : la règle n'est pas respectée, il faut corriger ;
- ATTENTION : la règle est respectée mais il reste une anomalie à connaître pour interpréter les résultats.
Le rapport est affiché, écrit dans logs/04_qualite.log et dans quality/rapport_qualite (CSV).
"""

from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType, IntegerType

import config
from commun import creer_session, Journal

journal = Journal("04_qualite")
spark = creer_session("TP3-04-Qualite")

ventes = spark.read.parquet(config.SILVER_VENTES).cache()
produits = spark.read.parquet(config.SILVER_PRODUITS).cache()
gold = spark.read.parquet(config.GOLD_CA_CATEGORIE).cache()
rejets_ventes = spark.read.parquet(config.QUALITY_REJETS_VENTES)
rejets_produits = spark.read.parquet(config.QUALITY_REJETS_PRODUITS)
raw_ventes = spark.read.text(config.RAW_VENTES)
raw_produits = spark.read.text(config.RAW_PRODUITS)
magasins = spark.read.option("sep", "|").csv(f"{config.LAKE}/raw/nifi/store.dat")  # déposé par NiFi au Jour 2

rapport = []


def controle(jeu, type_controle, regle, resultat, statut):
    rapport.append((jeu, type_controle, regle, str(resultat), statut))


def ok_si(condition):
    return "OK" if condition else "KO"


def nb_nulls(df, colonne):
    return df.filter(F.col(colonne).isNull()).count()


nb_ventes, nb_produits = ventes.count(), produits.count()

# ================= silver/store_sales
jeu = "silver/store_sales"
n_raw, n_rej = raw_ventes.count(), rejets_ventes.count()
controle(jeu, "Volume", "lignes raw = lignes silver + lignes mises à l'écart",
         f"{n_raw} = {nb_ventes} + {n_rej}", ok_si(n_raw == nb_ventes + n_rej))

for c in ["ss_item_sk", "ss_ticket_number", "ss_sold_date_sk", "ss_store_sk", "ss_quantity", "ss_net_paid"]:
    n = nb_nulls(ventes, c)
    controle(jeu, "Complétude", f"{c} non nul", f"{n} null", ok_si(n == 0))

for c in ["ss_promo_sk", "ss_addr_sk"]:
    n = nb_nulls(ventes, c)
    controle(jeu, "Complétude", f"{c} (non obligatoire) : part de null",
             f"{n} null ({n / nb_ventes * 100:.2f} %)", "OK" if n / nb_ventes < 0.01 else "ATTENTION")

colonnes_metier = [c for c in ventes.columns if c not in ("prix_zero", "source_fichier", "source_lot", "date_traitement")]
n_dist = ventes.dropDuplicates(colonnes_metier).count()
controle(jeu, "Unicité", "aucune ligne identique sur toutes les colonnes",
         f"{nb_ventes - n_dist} doublon(s)", ok_si(nb_ventes == n_dist))

types = dict((f.name, f.dataType) for f in ventes.schema.fields)
controle(jeu, "Validité", "montants en decimal(7,2)",
         types["ss_net_paid"].simpleString(),
         ok_si(all(types[c] == DecimalType(7, 2) for c in colonnes_metier if c.startswith("ss_") and isinstance(types[c], DecimalType))
               and types["ss_net_paid"] == DecimalType(7, 2)))
controle(jeu, "Validité", "identifiants et quantité en entier",
         types["ss_item_sk"].simpleString(),
         ok_si(all(isinstance(types[c], IntegerType) for c in colonnes_metier if c.endswith("_sk") or c in ("ss_ticket_number", "ss_quantity"))))

n = ventes.filter(F.col("ss_quantity") <= 0).count()
controle(jeu, "Cohérence", "ss_quantity > 0", f"{n} ligne(s) hors règle", ok_si(n == 0))
n = ventes.filter(F.col("ss_net_paid") < 0).count()
controle(jeu, "Cohérence", "ss_net_paid >= 0", f"{n} ligne(s) hors règle", ok_si(n == 0))
n = ventes.filter(F.col("ss_ext_sales_price") != F.col("ss_quantity") * F.col("ss_sales_price")).count()
controle(jeu, "Cohérence", "ss_ext_sales_price = ss_quantity x ss_sales_price", f"{n} ligne(s) hors règle", ok_si(n == 0))
n = ventes.filter(F.col("ss_sales_price") > F.col("ss_list_price")).count()
controle(jeu, "Cohérence", "prix de vente <= prix catalogue", f"{n} ligne(s) hors règle", ok_si(n == 0))
n = ventes.filter("prix_zero").count()
controle(jeu, "Cohérence", "ventes à prix 0 (gardées, repérées par prix_zero)", f"{n} ligne(s)", "ATTENTION" if n else "OK")
n = ventes.filter(F.col("ss_net_profit") < 0).count()
controle(jeu, "Cohérence", "ventes à marge négative (gardées)", f"{n} ligne(s) ({n / nb_ventes * 100:.1f} %)", "ATTENTION" if n else "OK")

n = ventes.join(produits, ventes.ss_item_sk == produits.i_item_sk, "left_anti").count()
controle(jeu, "Intégrité", "chaque ss_item_sk existe dans silver/item", f"{n} vente(s) sans produit", ok_si(n == 0))
ids_magasins = magasins.select(F.col("_c0").cast("int").alias("s_store_sk"))
n = ventes.join(ids_magasins, ventes.ss_store_sk == ids_magasins.s_store_sk, "left_anti").count()
controle(jeu, "Intégrité", "chaque ss_store_sk existe dans raw/nifi/store.dat", f"{n} vente(s) sans magasin", ok_si(n == 0))

# ================= silver/item
jeu = "silver/item"
n_raw, n_rej = raw_produits.count(), rejets_produits.count()
controle(jeu, "Volume", "lignes raw = lignes silver + lignes mises à l'écart",
         f"{n_raw} = {nb_produits} + {n_rej}", ok_si(n_raw == nb_produits + n_rej))
n_dist = produits.select("i_item_sk").distinct().count()
controle(jeu, "Clé candidate", "i_item_sk unique", f"{n_dist} valeurs pour {nb_produits} lignes", ok_si(n_dist == nb_produits))
for c in ["i_item_sk", "i_category"]:
    n = nb_nulls(produits, c)
    controle(jeu, "Complétude", f"{c} non nul", f"{n} null", ok_si(n == 0))
n = nb_nulls(produits, "i_size")
controle(jeu, "Complétude", "i_size (non obligatoire) : part de null", f"{n} null ({n / nb_produits * 100:.1f} %)", "ATTENTION")
types = dict((f.name, f.dataType) for f in produits.schema.fields)
controle(jeu, "Validité", "i_current_price en decimal(7,2), i_rec_start_date en date",
         f"{types['i_current_price'].simpleString()}, {types['i_rec_start_date'].simpleString()}",
         ok_si(types["i_current_price"] == DecimalType(7, 2) and types["i_rec_start_date"].simpleString() == "date"))
n = produits.filter(F.col("i_current_price") <= 0).count()
controle(jeu, "Cohérence", "i_current_price > 0", f"{n} ligne(s) hors règle", ok_si(n == 0))
n = produits.filter(F.col("i_wholesale_cost") > F.col("i_current_price")).count()
controle(jeu, "Cohérence", "coût d'achat > prix de vente (gardés)", f"{n} produit(s) ({n / nb_produits * 100:.1f} %)", "ATTENTION" if n else "OK")
n = produits.select("i_category").distinct().count()
controle(jeu, "Cohérence", "nombre de catégories = 9 (i_category_id de 1 à 9)", n, ok_si(n == 9))

# ================= gold/ca_par_categorie
jeu = "gold/ca_par_categorie"
nb_gold = gold.count()
controle(jeu, "Volume", "une ligne par catégorie de silver/item", f"{nb_gold} lignes", ok_si(nb_gold == produits.select("i_category").distinct().count()))
n = gold.select("categorie").distinct().count()
controle(jeu, "Unicité", "categorie unique", f"{n} valeurs pour {nb_gold} lignes", ok_si(n == nb_gold))
n = nb_nulls(gold, "categorie")
controle(jeu, "Complétude", "categorie non nulle", f"{n} null", ok_si(n == 0))
ca_silver = ventes.agg(F.sum("ss_net_paid")).first()[0]
ca_gold = gold.agg(F.sum("chiffre_affaires")).first()[0]
controle(jeu, "Cohérence", "somme du CA gold = CA total silver", f"{ca_gold} = {ca_silver}", ok_si(ca_gold == ca_silver))
lignes_gold = gold.agg(F.sum("nombre_lignes_vente")).first()[0]
controle(jeu, "Cohérence", "somme des lignes gold = lignes silver", f"{lignes_gold} = {nb_ventes}", ok_si(lignes_gold == nb_ventes))
somme_parts = gold.agg(F.sum("part_ca_pct")).first()[0]
controle(jeu, "Cohérence", "somme des parts = 100 % (à 0,05 près, à cause des arrondis)", f"{somme_parts} %", ok_si(abs(float(somme_parts) - 100) <= 0.05))
n = gold.filter(F.col("chiffre_affaires") < 0).count()
controle(jeu, "Cohérence", "chiffre_affaires >= 0", f"{n} ligne(s) hors règle", ok_si(n == 0))


# ---------- Affichage et écriture du rapport
journal.ecrire(f"{'Jeu':24}{'Contrôle':15}{'Règle':62}{'Résultat':38}Statut")
for jeu, type_controle, regle, resultat, statut in rapport:
    journal.ecrire(f"{jeu:24}{type_controle:15}{regle:62}{resultat:38}{statut}")

bilan = {s: sum(1 for r in rapport if r[4] == s) for s in ["OK", "ATTENTION", "KO"]}
journal.ecrire(f"\nBilan : {len(rapport)} contrôles - {bilan['OK']} OK, {bilan['ATTENTION']} ATTENTION, {bilan['KO']} KO")

df_rapport = spark.createDataFrame(rapport, ["jeu", "controle", "regle", "resultat", "statut"]) \
                  .withColumn("date_controle", F.current_timestamp())
df_rapport.coalesce(1).write.mode("overwrite").option("header", True).csv(config.QUALITY_RAPPORT)
journal.ecrire("Écrit :", config.QUALITY_RAPPORT)

spark.stop()
journal.ecrire("Fin du script 04_qualite")
