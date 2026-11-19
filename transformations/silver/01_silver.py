"""Étape 6 : raw -> silver.

Lit store_sales et item dans la zone raw, applique les règles de nettoyage de l'étape 4,
écrit les données propres dans silver (Parquet) et les lignes mises à l'écart dans quality/rejets.
Relit ensuite ce qui a été écrit pour le contrôler.
"""

from pyspark.sql import functions as F
from pyspark.sql.window import Window

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # config.py et commun.py

import config
from commun import creer_session, Journal, lire_source_raw, SCHEMA_VENTES, SCHEMA_PRODUITS

journal = Journal("01_silver")
spark = creer_session("TP3-01-Silver")

COLONNES_PROVENANCE = ["source_fichier", "source_lot", "date_traitement"]


# ---------- Lecture
ventes_brut = lire_source_raw(spark, config.RAW_VENTES, SCHEMA_VENTES)
produits_brut = lire_source_raw(spark, config.RAW_PRODUITS, SCHEMA_PRODUITS)
journal.ecrire("Lu :", config.RAW_VENTES, "->", ventes_brut.count(), "lignes")
journal.ecrire("Lu :", config.RAW_PRODUITS, "->", produits_brut.count(), "lignes")


# ---------- Règles sur les produits
def nettoyer_produits(df):
    df = df.withColumn("nb_meme_id", F.count("*").over(Window.partitionBy("i_item_sk")))
    df = df.withColumn("motif_rejet",
        F.when(F.col("_corrupt_record").isNotNull(), "type incorrect")
         .when(F.col("i_item_sk").isNull(), "identifiant manquant")
         .when(F.col("nb_meme_id") > 1, "identifiant en double")
         .when(F.col("i_category").isNull(), "catégorie manquante"))
    colonnes_texte = [c for c, t in df.dtypes
                      if t == "string" and c not in ("motif_rejet", "_corrupt_record", "source_fichier", "source_lot")]
    for c in colonnes_texte:
        df = df.withColumn(c, F.trim(F.col(c)))
    for c in ["i_size", "i_units"]:
        df = df.withColumn(c, F.when(F.col(c).isin("N/A", "Unknown", ""), None).otherwise(F.col(c)))
    propres = df.filter(F.col("motif_rejet").isNull()) \
                .drop("motif_rejet", "nb_meme_id", "_corrupt_record", "i_container")
    rejetes = df.filter(F.col("motif_rejet").isNotNull()).drop("nb_meme_id")
    return propres, rejetes


# ---------- Règles sur les ventes
def nettoyer_ventes(df, produits_propres):
    ids_produits = produits_propres.select(F.col("i_item_sk").alias("ss_item_sk"),
                                           F.lit(True).alias("produit_connu"))
    colonnes_metier = [c for c in SCHEMA_VENTES.fieldNames() if c != "_corrupt_record"]
    df = (
        df.dropDuplicates(colonnes_metier)
        .join(ids_produits, on="ss_item_sk", how="left")
        .withColumn("motif_rejet",
            F.when(F.col("_corrupt_record").isNotNull(), "type incorrect")
             .when(F.col("ss_item_sk").isNull() | F.col("ss_ticket_number").isNull()
                   | F.col("ss_sold_date_sk").isNull() | F.col("ss_store_sk").isNull(), "identifiant manquant")
             .when(F.col("produit_connu").isNull(), "produit inconnu")
             .when(F.col("ss_quantity") <= 0, "quantité <= 0")
             .when((F.col("ss_sales_price") < 0) | (F.col("ss_net_paid") < 0), "montant négatif"))
        .withColumn("prix_zero", F.col("ss_sales_price") == 0)
    )
    propres = df.filter(F.col("motif_rejet").isNull()) \
                .select(colonnes_metier + ["prix_zero"] + COLONNES_PROVENANCE)
    rejetes = df.filter(F.col("motif_rejet").isNotNull()).drop("produit_connu")
    return propres, rejetes


produits_propres, produits_rejetes = nettoyer_produits(produits_brut)
ventes_propres, ventes_rejetees = nettoyer_ventes(ventes_brut, produits_propres)


# ---------- Écriture (dossiers réservés au TP, overwrite = on remplace le résultat précédent)
def ecrire_parquet(df, chemin):
    df.write.mode("overwrite").parquet(chemin)
    journal.ecrire("Écrit :", chemin)


ecrire_parquet(produits_propres, config.SILVER_PRODUITS)
ecrire_parquet(ventes_propres, config.SILVER_VENTES)
ecrire_parquet(produits_rejetes, config.QUALITY_REJETS_PRODUITS)
ecrire_parquet(ventes_rejetees, config.QUALITY_REJETS_VENTES)


# ---------- Contrôles après écriture : on relit ce qui est dans silver
journal.ecrire("\n--- Contrôles après écriture")
for nom, chemin, df_attendu, df_brut, df_rejets in [
    ("item", config.SILVER_PRODUITS, produits_propres, produits_brut, produits_rejetes),
    ("store_sales", config.SILVER_VENTES, ventes_propres, ventes_brut, ventes_rejetees),
]:
    relu = spark.read.parquet(chemin)
    nb_relu, nb_brut, nb_rejets = relu.count(), df_brut.count(), df_rejets.count()
    journal.ecrire(f"[{nom}] relecture OK : {nb_relu} lignes, {len(relu.columns)} colonnes")
    journal.ecrire(f"[{nom}] raw {nb_brut} = silver {nb_relu} + rejets {nb_rejets} + doublons retirés {nb_brut - nb_relu - nb_rejets}")
    meme_schema = [(f.name, f.dataType) for f in relu.schema] == [(f.name, f.dataType) for f in df_attendu.schema]
    journal.ecrire(f"[{nom}] mêmes colonnes et mêmes types qu'avant l'écriture : {meme_schema}")
    journal.ecrire(f"[{nom}] schéma silver :")
    for champ in relu.schema.fields:
        journal.ecrire(f"    {champ.name:25} {champ.dataType.simpleString()}")
    journal.ecrire(f"[{nom}] provenance : {relu.select('source_fichier', 'source_lot').distinct().collect()}")

relu = spark.read.parquet(config.SILVER_VENTES)
journal.ecrire("[store_sales] ventes à prix 0 repérées (prix_zero) :", relu.filter("prix_zero").count())

spark.stop()
journal.ecrire("Fin du script 01_silver")
