"""Paramètres des scripts PySpark du TP3 (version Data Lake HDFS, fichier complet) : chemins d'entrée et de sortie, lot traité.

Tous les autres scripts lisent leurs chemins ici. Pour changer d'environnement
(autre machine, autre lot), il suffit de modifier ce fichier.
"""

# Adresse de HDFS (configuration du Jour 2)
HDFS = "hdfs://localhost:9000"
LAKE = HDFS + "/retail-lake"
HDFS_REPLICATION = "1"  # 1 seul DataNode (dfs.replication = 1 au Jour 2)

# Lot traité : "initial" (dossier data/) ou "refresh" (dossier data_refresh/)
LOT = "initial"

# Entrées : zone raw (on ne la modifie jamais)
RAW_VENTES = f"{LAKE}/raw/tpcxbb/{LOT}/store_sales/store_sales.dat"
RAW_PRODUITS = f"{LAKE}/raw/tpcxbb/{LOT}/item/item.dat"

# Sorties : zones silver, gold et quality
SILVER_VENTES = f"{LAKE}/silver/store_sales"
SILVER_PRODUITS = f"{LAKE}/silver/item"
GOLD_CA_CATEGORIE = f"{LAKE}/gold/ca_par_categorie"
QUALITY_REJETS_VENTES = f"{LAKE}/quality/rejets/store_sales"
QUALITY_REJETS_PRODUITS = f"{LAKE}/quality/rejets/item"
QUALITY_RAPPORT = f"{LAKE}/quality/rapport_qualite"

# Sorties locales (dans le dépôt, dossier outputs/ non versionné) : comparaison des formats et journaux
import os
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE_FORMATS = f"file://{RACINE}/outputs/formats_hdfs"
DOSSIER_LOGS = f"{RACINE}/outputs/logs_hdfs"

# Ressources Spark
SPARK_MASTER = "local[*]"
SPARK_MEMOIRE = "2g"
