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

## Etape 3 - Exploration des sources

Ouvrir et executer le notebook `transformations/exploration/exploration_sources.ipynb`
(chargement, schema, echantillon, comptage, valeurs manquantes, doublons,
valeurs atypiques et reponses aux questions techniques).

## Etapes 4 et 5 - Nettoyage, transformations, agregations

Le fichier `store_sales` complet est trop lourd pour la machine : on travaille
sur un echantillon de 10 % des tickets. A creer une fois, depuis ce dossier :

```
awk -F'|' '$10 % 10 == 0' ~/DEV/tpcxbb_source/retail_project/data/store_sales/store_sales.dat > data/samples/store_sales_echantillon.dat
```

Puis executer les notebooks dans cet ordre (un seul a la fois) :

1. `transformations/cleaning/nettoyage_silver.ipynb` : Raw -> `data/silver/`
2. `transformations/enrichment/enrichissement_ventes.ipynb` : `data/silver/sales_enriched/`
3. `transformations/aggregation/agregations_gold.ipynb` : Silver -> `data/gold/`

Documentation : `docs/transformations/regles_nettoyage.md` et
`docs/transformations/transformations_resultats.md`.

## Etape 6 - Donnees Silver

Les jeux Silver (`data/silver/sales`, `products`, `stores`, `dates`, `sales_enriched`)
sont produits par les notebooks des etapes 4 et 5. Apres leur execution, lancer :

4. `tests/controles_silver.ipynb` : controles apres ecriture (presence, format,
   lisibilite, nombre de lignes, schema, coherence)

Documentation : `docs/data-dictionary/silver.md` (organisation, convention de nommage,
provenance, description de chaque colonne) et schemas de reference dans
`docs/data-dictionary/schemas/`.

## Etape 7 - Donnees Gold

Produites par `transformations/aggregation/agregations_gold.ipynb` dans `data/gold/` :
`ca_mensuel`, `ca_annuel`, `ca_marge_par_categorie`, `top10_produits`,
`ca_marge_par_magasin`, `taux_remise_mensuel`.

Documentation (finalite, sources, granularite, colonnes, mesures, regles de calcul,
limites) : `docs/data-dictionary/gold.md`. Schemas : `docs/data-dictionary/schemas/gold_*.json`.

## Etape 8 - Format Parquet

`notebooks/comparaison_formats.ipynb` : ecrit `sales_enriched` en Parquet dans
`outputs/formats/` (repertoire de test dedie), le relit et le verifie, puis compare
avec CSV et JSON (types, volume, vitesse). Comparaison argumentee :
`docs/architecture/comparaison_formats.md`.

## Etape 9 - Controles qualite

`tests/controles_qualite.ipynb` : 152 controles (completude, unicite, validite des types,
coherence, volumes, cles candidates, integrite referentielle) sur Silver et Gold.
Rapport : `docs/quality/rapport_qualite.md`.
