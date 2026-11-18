#!/bin/bash
# Lance toute la chaîne du TP3 dans l'ordre. S'arrête au premier script en erreur.
# Prérequis : HDFS démarré (start-dfs.sh), fichiers déposés dans /retail-lake/raw.
set -e
cd "$(dirname "$0")"
source ../.venv/bin/activate

python 01_silver.py     # raw -> silver (+ lignes mises à l'écart dans quality/rejets)
python 02_gold.py       # silver -> gold (CA par catégorie)
python 03_formats.py    # comparaison CSV / JSON / Parquet
python 04_qualite.py    # contrôles qualité -> quality/rapport_qualite

echo "Chaîne terminée. Journaux dans ../logs/"
