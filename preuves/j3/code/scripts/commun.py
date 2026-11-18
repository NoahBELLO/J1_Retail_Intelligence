"""Fonctions communes : session Spark, schémas, lecture des sources, journal."""

import os
from datetime import datetime

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import (StructType, StructField, IntegerType, StringType,
                               DecimalType, DateType)

import config


# ---------- Session Spark
def creer_session(nom):
    spark = (
        SparkSession.builder
        .appName(nom)
        .master(config.SPARK_MASTER)
        .config("spark.driver.memory", config.SPARK_MEMOIRE)
        # PySpark (installé avec pip) ne lit pas hdfs-site.xml : on impose 1 copie, comme notre HDFS à 1 DataNode
        .config("spark.hadoop.dfs.replication", config.HDFS_REPLICATION)
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    return spark


# ---------- Journal : chaque script écrit ce qu'il fait dans logs/<script>.log
class Journal:
    def __init__(self, nom_script):
        os.makedirs(config.DOSSIER_LOGS, exist_ok=True)
        self.fichier = os.path.join(config.DOSSIER_LOGS, nom_script + ".log")
        with open(self.fichier, "w", encoding="utf-8") as f:
            f.write(f"=== {nom_script} - lancé le {datetime.now():%Y-%m-%d %H:%M:%S}\n")

    def ecrire(self, *message):
        texte = " ".join(str(m) for m in message)
        print(texte)
        with open(self.fichier, "a", encoding="utf-8") as f:
            f.write(texte + "\n")


# ---------- Schémas écrits à la main (noms du schéma TPCx-BB, types vérifiés aux étapes 2 et 3)
def montant(nom):
    return StructField(nom, DecimalType(7, 2))


SCHEMA_VENTES = StructType([
    StructField("ss_sold_date_sk", IntegerType()),
    StructField("ss_sold_time_sk", IntegerType()),
    StructField("ss_item_sk", IntegerType()),
    StructField("ss_customer_sk", IntegerType()),
    StructField("ss_cdemo_sk", IntegerType()),
    StructField("ss_hdemo_sk", IntegerType()),
    StructField("ss_addr_sk", IntegerType()),
    StructField("ss_store_sk", IntegerType()),
    StructField("ss_promo_sk", IntegerType()),
    StructField("ss_ticket_number", IntegerType()),
    StructField("ss_quantity", IntegerType()),
    montant("ss_wholesale_cost"), montant("ss_list_price"), montant("ss_sales_price"),
    montant("ss_ext_discount_amt"), montant("ss_ext_sales_price"), montant("ss_ext_wholesale_cost"),
    montant("ss_ext_list_price"), montant("ss_ext_tax"), montant("ss_coupon_amt"),
    montant("ss_net_paid"), montant("ss_net_paid_inc_tax"), montant("ss_net_profit"),
    StructField("_corrupt_record", StringType()),
])

SCHEMA_PRODUITS = StructType([
    StructField("i_item_sk", IntegerType()),
    StructField("i_item_id", StringType()),
    StructField("i_rec_start_date", DateType()),
    StructField("i_rec_end_date", DateType()),
    StructField("i_item_desc", StringType()),
    montant("i_current_price"), montant("i_wholesale_cost"),
    StructField("i_brand_id", IntegerType()),
    StructField("i_brand", StringType()),
    StructField("i_class_id", IntegerType()),
    StructField("i_class", StringType()),
    StructField("i_category_id", IntegerType()),
    StructField("i_category", StringType()),
    StructField("i_manufact_id", IntegerType()),
    StructField("i_manufact", StringType()),
    StructField("i_size", StringType()),
    StructField("i_formulation", StringType()),
    StructField("i_color", StringType()),
    StructField("i_units", StringType()),
    StructField("i_container", StringType()),
    StructField("i_manager_id", IntegerType()),
    StructField("i_product_name", StringType()),
    StructField("_corrupt_record", StringType()),
])


# ---------- Lecture d'un fichier .dat de la zone raw
def lire_source_raw(spark, chemin, schema):
    """Lit un fichier TPCx-BB (séparateur |, sans ligne de titres) avec un schéma imposé.
    Les lignes qui ne se convertissent pas arrivent dans la colonne _corrupt_record.
    On ajoute la provenance : fichier d'origine, lot et date du traitement."""
    df = (
        spark.read
        .option("header", False)
        .option("sep", "|")
        .option("mode", "PERMISSIVE")
        .option("columnNameOfCorruptRecord", "_corrupt_record")
        .schema(schema)
        .csv(chemin)
        .withColumn("source_fichier", F.col("_metadata.file_path"))
        .withColumn("source_lot", F.lit(config.LOT))
        .withColumn("date_traitement", F.current_timestamp())
    )
    return df.cache()
