#!/bin/bash
# Version "scripts PySpark sur le Data Lake HDFS" (fichier store_sales complet).
# Lance les 4 scripts dans l'ordre et s'arrête au premier en erreur.
# Prérequis : HDFS démarré (start-dfs.sh), fichiers déposés dans /retail-lake/raw.
# Python utilisé : variable PYTHON, sinon .venv à la racine du dépôt.
set -e
ICI="$(cd "$(dirname "$0")" && pwd)"
PYTHON="${PYTHON:-$ICI/../.venv/bin/python}"

"$PYTHON" "$ICI/silver/01_silver.py"   # raw -> silver (+ lignes mises à l'écart dans quality/rejets)
"$PYTHON" "$ICI/gold/02_gold.py"       # silver -> gold (CA par catégorie)
"$PYTHON" "$ICI/03_formats.py"         # comparaison CSV / JSON / Parquet
"$PYTHON" "$ICI/04_qualite.py"         # contrôles qualité -> quality/rapport_qualite

echo "Chaîne terminée. Journaux dans outputs/logs_hdfs/"
