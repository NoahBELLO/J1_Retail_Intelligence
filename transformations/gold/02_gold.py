"""Étape 7 : silver -> gold.

Jeu Gold « chiffre d'affaires par catégorie » (question P4 du Jour 1).
Lit les ventes et les produits dans silver, vérifie la clé, fait la jointure,
calcule les indicateurs et écrit le résultat dans gold (Parquet), puis le relit.
"""

from pyspark.sql import functions as F

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # config.py et commun.py

import config
from commun import creer_session, Journal

journal = Journal("02_gold")
spark = creer_session("TP3-02-Gold")

ventes = spark.read.parquet(config.SILVER_VENTES)
produits = spark.read.parquet(config.SILVER_PRODUITS)
journal.ecrire("Lu :", config.SILVER_VENTES, "->", ventes.count(), "lignes")
journal.ecrire("Lu :", config.SILVER_PRODUITS, "->", produits.count(), "lignes")


# ---------- Vérifier la clé avant la jointure
nb_produits = produits.count()
nb_ids = produits.select("i_item_sk").distinct().count()
nb_sans_produit = ventes.join(produits, ventes.ss_item_sk == produits.i_item_sk, "left_anti").count()
journal.ecrire(f"i_item_sk unique : {nb_produits == nb_ids} ({nb_ids} valeurs pour {nb_produits} lignes)")
journal.ecrire(f"Ventes dont le produit est inconnu : {nb_sans_produit}")


# ---------- Jointure ventes + produits (plusieurs ventes -> un produit)
ventes_enrichies = ventes.join(
    produits.select("i_item_sk", "i_category"),
    ventes.ss_item_sk == produits.i_item_sk,
    "left",
)
nb_avant, nb_apres = ventes.count(), ventes_enrichies.count()
nb_non_rapprochees = ventes_enrichies.filter(F.col("i_item_sk").isNull()).count()
journal.ecrire(f"Jointure : {nb_avant} lignes avant, {nb_apres} après, {nb_non_rapprochees} non rapprochées")


# ---------- Agrégation : une ligne = une catégorie
ca_total = ventes.agg(F.sum("ss_net_paid")).first()[0]
ca_par_categorie = (
    ventes_enrichies
    .groupBy(F.col("i_category").alias("categorie"))
    .agg(
        F.sum("ss_net_paid").alias("chiffre_affaires"),
        F.sum("ss_quantity").alias("quantite_vendue"),
        F.count("*").alias("nombre_lignes_vente"),
        F.countDistinct("ss_item_sk").alias("nombre_produits_vendus"),
    )
    .withColumn("part_ca_pct", F.round(F.col("chiffre_affaires") / F.lit(ca_total) * 100, 2).cast("decimal(5,2)"))
    .withColumn("source", F.lit("silver/store_sales + silver/item"))
    .withColumn("date_traitement", F.current_timestamp())
    .orderBy(F.desc("chiffre_affaires"))
)


# ---------- Écriture et relecture
ca_par_categorie.write.mode("overwrite").parquet(config.GOLD_CA_CATEGORIE)
journal.ecrire("Écrit :", config.GOLD_CA_CATEGORIE)

relu = spark.read.parquet(config.GOLD_CA_CATEGORIE)
journal.ecrire(f"Relecture OK : {relu.count()} lignes, {len(relu.columns)} colonnes")
journal.ecrire("Schéma gold :")
for champ in relu.schema.fields:
    journal.ecrire(f"    {champ.name:25} {champ.dataType.simpleString()}")

lignes = relu.orderBy(F.desc("chiffre_affaires")).collect()
journal.ecrire(f"\n{'categorie':26}{'chiffre_affaires':>18}{'quantite':>12}{'lignes':>9}{'produits':>10}{'part_%':>8}")
for l in lignes:
    journal.ecrire(f"{l.categorie:26}{l.chiffre_affaires:>18}{l.quantite_vendue:>12}"
                   f"{l.nombre_lignes_vente:>9}{l.nombre_produits_vendus:>10}{l.part_ca_pct:>8}")

journal.ecrire("\nCA total silver :", ca_total, "| somme gold :", relu.agg(F.sum("chiffre_affaires")).first()[0])

spark.stop()
journal.ecrire("Fin du script 02_gold")
