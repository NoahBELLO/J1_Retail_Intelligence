"""Étape 8 : comparer CSV, JSON et Parquet sur le même jeu de données (silver store_sales).

Écrit les mêmes lignes dans les 3 formats (dossier local de test), puis compare :
taille sur le disque, types retrouvés à la relecture, temps pour calculer un total.
"""

import os
import time

from pyspark.sql import functions as F

import config
from commun import creer_session, Journal

journal = Journal("03_formats")
spark = creer_session("TP3-03-Formats")

ventes = spark.read.parquet(config.SILVER_VENTES)
nb_lignes = ventes.count()
journal.ecrire("Jeu comparé :", config.SILVER_VENTES, "->", nb_lignes, "lignes,", len(ventes.columns), "colonnes")


def taille_dossier(chemin_file):
    dossier = chemin_file.replace("file://", "")
    total = 0
    for racine, _, fichiers in os.walk(dossier):
        for f in fichiers:
            if not f.startswith(".") and not f.startswith("_"):
                total += os.path.getsize(os.path.join(racine, f))
    return total


resultats = []
for fmt in ["csv", "json", "parquet"]:
    chemin = f"{config.SORTIE_FORMATS}/{fmt}"

    # Écriture
    ecriture = ventes.write.mode("overwrite")
    if fmt == "csv":
        ecriture.option("header", True).csv(chemin)
    elif fmt == "json":
        ecriture.json(chemin)
    else:
        ecriture.parquet(chemin)

    # Relecture sans donner de schéma : quels types retrouve-t-on ?
    if fmt == "csv":
        relu = spark.read.option("header", True).csv(chemin)
    elif fmt == "json":
        relu = spark.read.json(chemin)
    else:
        relu = spark.read.parquet(chemin)
    types = dict(relu.dtypes)

    # Temps pour calculer le total d'une seule colonne
    debut = time.time()
    total = relu.agg(F.sum(F.col("ss_net_paid").cast("decimal(17,2)"))).first()[0]
    duree = time.time() - debut

    resultats.append((fmt, taille_dossier(chemin), relu.count(), types["ss_net_paid"],
                      types["ss_quantity"], types["date_traitement"], total, duree))

taille_raw = 92764700  # store_sales.dat dans raw (relevé au Jour 2)
journal.ecrire(f"\nRéférence : fichier texte d'origine store_sales.dat = {taille_raw} octets")
journal.ecrire(f"\n{'format':9}{'taille (octets)':>17}{'% du .dat':>11}{'lignes':>9}"
               f"  {'ss_net_paid':14}{'ss_quantity':13}{'date_traitement':17}{'total ss_net_paid':>20}{'temps (s)':>10}")
for fmt, taille, lignes, t_montant, t_qte, t_date, total, duree in resultats:
    journal.ecrire(f"{fmt:9}{taille:>17}{taille / taille_raw * 100:>10.1f}%{lignes:>9}"
                   f"  {t_montant:14}{t_qte:13}{t_date:17}{str(total):>20}{duree:>10.2f}")

spark.stop()
journal.ecrire("Fin du script 03_formats")
