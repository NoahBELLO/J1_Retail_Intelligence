# TP3 – Transformation, qualité et Data Lakehouse (UC-06)

Chaîne PySpark qui part des fichiers TPCx-BB de la zone `raw` du Data Lake (HDFS) et produit des données nettoyées (`silver`), un jeu d'analyse (`gold`) et un rapport qualité, au format Parquet.

## Prérequis

- Ubuntu 24.04 dans WSL (Windows 11), avec au moins 8 Go de mémoire pour WSL (`C:\Users\Noah\.wslconfig` : `memory=8GB`, `processors=4`).
- Java 21 (Spark) et Java 17 (Hadoop).
- Hadoop 3.5.0 dans `/opt/hadoop`, HDFS démarré.
- Environnement Python `~/retail-intelligence/tp3/.venv` avec `pyspark` et `jupyterlab` :
  ```bash
  python3 -m venv .venv && source .venv/bin/activate && pip install pyspark jupyterlab
  ```

## Versions observées

| Outil | Version |
|---|---|
| Python | 3.12.3 |
| Spark / PySpark | 4.3.0 (mode `local[*]`) |
| JupyterLab | 4.6.6 |
| Java (Spark) | 21.0.13 |
| Hadoop | 3.5.0 |

## Emplacement des données

| Zone | Chemin HDFS | Contenu |
|---|---|---|
| raw (entrée, jamais modifiée) | `/retail-lake/raw/tpcxbb/initial/store_sales/store_sales.dat` | Ventes en magasin |
| raw (entrée, jamais modifiée) | `/retail-lake/raw/tpcxbb/initial/item/item.dat` | Produits |
| raw (entrée, contrôle) | `/retail-lake/raw/nifi/store.dat` | Magasins (déposé par NiFi au Jour 2) |
| silver | `/retail-lake/silver/store_sales/`, `/retail-lake/silver/item/` | Données nettoyées (Parquet) |
| gold | `/retail-lake/gold/ca_par_categorie/` | Chiffre d'affaires par catégorie (Parquet) |
| quality | `/retail-lake/quality/rejets/{store_sales,item}/` | Lignes mises à l'écart, avec leur motif (Parquet) |
| quality | `/retail-lake/quality/rapport_qualite/` | Rapport des contrôles (CSV) |

Sorties locales : `outputs/comparaison_formats/` (CSV, JSON et Parquet du même jeu) et `logs/` (un journal par script).

## Paramètres

Tous dans `scripts/config.py` : adresse HDFS, lot traité (`LOT = "initial"` ou `"refresh"`), chemins d'entrée et de sortie, mémoire Spark, nombre de copies HDFS (`1`).

## Ordre d'exécution

```bash
start-dfs.sh                       # 1. démarrer HDFS
cd ~/retail-intelligence/tp3/scripts
./lancer_tout.sh                   # 2. lance les 4 scripts dans l'ordre
```

| Ordre | Script | Rôle |
|---|---|---|
| 1 | `01_silver.py` | raw → silver : schéma imposé, règles de nettoyage, provenance, lignes mises à l'écart |
| 2 | `02_gold.py` | silver → gold : jointure ventes + produits, CA par catégorie |
| 3 | `03_formats.py` | Comparaison CSV / JSON / Parquet |
| 4 | `04_qualite.py` | Contrôles qualité sur silver et gold |

Les fichiers `commun.py` (session Spark, schémas, lecture, journal) et `config.py` (paramètres) sont utilisés par les 4 scripts. Durée totale : environ 3 minutes.

Les notebooks `TP3_Retail_Intelligence.ipynb` (exploration) et `TP3_Nettoyage.ipynb` (mise au point du nettoyage et des transformations) gardent le travail des étapes 1 à 5.

## Sorties produites

- `silver/store_sales` : 667 579 lignes, 27 colonnes.
- `silver/item` : 17 820 lignes, 24 colonnes.
- `gold/ca_par_categorie` : 9 lignes (une par catégorie).
- `quality/rejets` : 0 ligne pour ce lot.
- `quality/rapport_qualite` : 36 contrôles.

## Contrôles disponibles

`04_qualite.py` vérifie les volumes, la complétude, l'unicité, les types, la cohérence des valeurs et l'intégrité (produit et magasin connus). Chaque contrôle est `OK`, `KO` ou `ATTENTION`. Dernier résultat : 32 OK, 4 ATTENTION, 0 KO.

## Limites connues

- Données TPCx-BB générées au hasard : 74 % des ventes ont une marge négative, 44 % des produits coûtent plus cher à l'achat qu'à la vente.
- Les dates des ventes ne sont pas converties (`date_dim` n'est pas chargée).
- Seul le lot `initial` a été traité. Le contrôle de volume ne tient pas compte des doublons retirés (0 ici).
- Les sorties sont écrites en `overwrite` : chaque lancement remplace le résultat précédent, sans historique.
- Parquet seul n'est pas une table transactionnelle (pas de retour en arrière, pas de gestion des écritures en même temps).
- Environnement mono-machine (1 DataNode, 1 copie des données).
