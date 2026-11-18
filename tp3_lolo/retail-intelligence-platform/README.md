# Retail Intelligence Platform - TP Jour 3

Chaine de transformation Raw/Bronze -> Silver -> Gold avec PySpark (UC-06).

Cette arborescence est une convention de projet : elle n'est pas imposee
par TPCx-BB, Hadoop ou Spark.

## Arborescence

```
retail-intelligence-platform/
+-- docs/
|   +-- data-dictionary/    dictionnaire des donnees
|   +-- transformations/    description des traitements
|   +-- quality/            controles qualite
|   +-- architecture/       fiche d'environnement, schemas
+-- data/
|   +-- samples/            petits fichiers de test
|   +-- raw/                donnees brutes (jamais modifiees)
|   +-- bronze/             donnees sources chargees
|   +-- silver/             donnees nettoyees et harmonisees
|   +-- gold/               donnees analytiques (Parquet)
+-- notebooks/
+-- transformations/
|   +-- exploration/
|   +-- cleaning/
|   +-- enrichment/
|   +-- aggregation/
+-- tests/
+-- outputs/                resultats de test
+-- README.md
```

## Etape 1 - Verifier l'environnement

Ouvrir et executer le notebook `tests/verif_environnement.ipynb`
(Jupyter lance depuis `tp3_lolo` : `.venv/bin/jupyter lab`).

Resultats consignes dans `docs/architecture/fiche_environnement.md`.

## Etape 2 - Inventaire des sources

Ouvrir et executer le notebook `transformations/exploration/inventaire_sources.ipynb`.

Sources lues (sans modification) dans `~/DEV/tpcxbb_source/retail_project/data`.
Resultats : `outputs/inventaire_sources.json`, inventaire redige dans
`docs/data-dictionary/inventaire_sources.md`.
