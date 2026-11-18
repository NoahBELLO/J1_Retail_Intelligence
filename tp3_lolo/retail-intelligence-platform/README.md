# Retail Intelligence Platform - TP Jour 3 (UC-06)

Chaîne de transformation **Raw → Silver → Gold** avec PySpark, sur les données
de vente en magasin TPCx-BB (`store_sales`, `item`, `store`, `date_dim`).

Pour tout reproduire en une commande :

```
cd ~/DEV/J1_Retail_Intelligence/tp3_lolo/retail-intelligence-platform
./run_pipeline.sh
```

## 1. Prérequis

- **Environnement Python** `tp3_lolo/.venv`, avec `pyspark` et `jupyter`
  (`nbconvert`). Il est utilisé par tous les notebooks et par
  `run_pipeline.sh`.
- **Java 17 ou plus** pour Spark (21 observé).
- **Données TPCx-BB** générées dans `~/DEV/tpcxbb_source/retail_project/data`
  (voir la section 3).
- **Spec du Jour 1** : `01_UC01_besoin_exploration/preuves/tpcxbb_schema.json`,
  dans le dépôt. Elle sert de schéma de référence.
- **`awk`**, pour créer l'échantillon.
- **Mémoire** : environ 1,5 Go de RAM libre. Fermer les autres kernels
  Jupyter avant de lancer le pipeline (chaque session Spark réserve jusqu'à
  1 Go).
- **HDFS n'est pas nécessaire** : les fichiers sont lus sur le disque local
  (préfixe `file://`).

## 2. Versions observées

Relevées par `tests/verif_environnement.ipynb`, détail dans
`docs/architecture/fiche_environnement.md` :

| Élément | Version |
|---|---|
| Système | Ubuntu 26.04.1 LTS |
| Python | 3.14.4 |
| PySpark / Spark | 4.3.0 |
| Java | OpenJDK 21.0.13 |
| Hadoop (machine) | 3.5.0. Sa configuration est chargée par Spark : `fs.defaultFS = hdfs://localhost:9000` |
| Mode d'exécution | `local[2]` : 2 cœurs, 768 Mo pour le driver |

## 3. Emplacement des données

| Zone | Emplacement | Contenu |
|---|---|---|
| **Raw** | `~/DEV/tpcxbb_source/retail_project/data/<table>/<table>.dat` | Fichiers TPCx-BB bruts, délimités par `\|`, sans en-tête. Ils sont **lus en place, jamais modifiés**, et ont été déposés dans HDFS au Jour 2 (`/retail-lake/raw/`) |
| Échantillon | `data/samples/store_sales_echantillon.dat` | 10 % des tickets de `store_sales` (66 593 lignes), créé par `run_pipeline.sh` |
| **Silver** | `data/silver/` | `sales`, `products`, `stores`, `dates`, `sales_enriched`, et `rejects/` pour les lignes écartées. Format Parquet |
| **Gold** | `data/gold/` | `ca_mensuel`, `ca_annuel`, `ca_marge_par_categorie`, `top10_produits`, `ca_marge_par_magasin`, `taux_remise_mensuel`. Format Parquet |
| Résultats | `outputs/` | Bilans JSON, journaux (`outputs/logs/`), fichiers de test (`outputs/formats/`) |

Les dossiers `data/raw/` et `data/bronze/` restent vides : la zone Raw est
lue directement dans le dossier source, sans copie.

Les données produites (Silver, Gold, échantillon, `outputs/`) ne sont pas
versionnées (voir `tp3_lolo/.gitignore`) : `run_pipeline.sh` les recrée.

## 4. Paramètres

Tous les paramètres sont dans **`config/parametres.json`**. Aucun chemin
n'est écrit en dur dans les notebooks du pipeline : chacun lit ce fichier
dans sa première cellule.

| Paramètre | Valeur par défaut | Rôle |
|---|---|---|
| `chemins.source_tpcxbb` | `~/DEV/tpcxbb_source/retail_project/data` | Dossier des fichiers bruts. **À adapter** sur une autre machine |
| `chemins.schema_tpcxbb` | `../../01_UC01_besoin_exploration/preuves/tpcxbb_schema.json` | Schéma de référence (noms et types des colonnes) |
| `chemins.echantillon_ventes`, `silver`, `gold`, `outputs`, `logs`, `schemas` | `data/...`, `outputs/...`, `docs/...` | Entrées et sorties, relatives à la racine du projet |
| `echantillon.actif` | `true` | `false` pour traiter le `store_sales` complet (machine plus puissante nécessaire) |
| `echantillon.modulo_ticket` | `10` | Tickets gardés : numéro multiple de 10, soit 10 % des tickets |
| `spark.master`, `spark.config` | `local[2]`, 768 Mo, 4 partitions | Ressources Spark, réglées pour une machine de 5 Go de RAM |
| `periode_attendue` | du 2001-01-01 au 2005-12-13 | Utilisée par les contrôles |
| `qualite.*` | vide < 1 %, tolérance 0,01, mois ≥ 50 % de la moyenne | Seuils des contrôles qualité |

## 5. Ordre d'exécution

### Étapes préalables (1 à 3), lancées à la main une fois

Ces notebooks lisent les fichiers **complets**, ils sont donc plus lourds.
Ils ne font pas partie du pipeline.

| Étape | Notebook | Rôle |
|---|---|---|
| 1 | `tests/verif_environnement.ipynb` | Versions, session Spark, lecture et écriture d'un fichier de test |
| 2 | `transformations/exploration/inventaire_sources.ipynb` | Inventaire technique des sources retenues |
| 3 | `transformations/exploration/exploration_sources.ipynb` | Exploration : schémas, valeurs manquantes, doublons, valeurs atypiques |

### Pipeline (étapes 4 à 9) : `./run_pipeline.sh`

Le script crée l'échantillon s'il n'existe pas, puis exécute les notebooks
**un par un, dans cet ordre**. Chaque notebook lit ce que le précédent a
écrit :

```
Raw (.dat)
  |  1. transformations/cleaning/nettoyage_silver.ipynb          etape 4 et 6
  v
silver/sales, products, stores, dates  (+ silver/rejects/)
  |  2. transformations/enrichment/enrichissement_ventes.ipynb   etape 5
  v
silver/sales_enriched
  |  3. transformations/aggregation/agregations_gold.ipynb       etapes 5 et 7
  v
gold/*
     4. tests/controles_silver.ipynb                             etape 6 : controles techniques
     5. tests/controles_qualite.ipynb                            etape 9 : rapport de qualite
     6. notebooks/comparaison_formats.ipynb                      etape 8 (option --formats)
```

- `./run_pipeline.sh` lance les notebooks 1 à 5 du schéma ci-dessus.
- `./run_pipeline.sh --formats` ajoute la comparaison des formats.
- Le script s'arrête au premier notebook en échec.
- Pour lancer un notebook seul (dans le même ordre), on peut l'ouvrir dans
  Jupyter (`.venv/bin/jupyter lab` depuis `tp3_lolo`), ou exécuter :
  `../.venv/bin/jupyter nbconvert --to notebook --execute --inplace <notebook>`
  depuis son dossier.

### Organisation interne des notebooks du pipeline

Chaque notebook suit la même structure. Une cellule « Organisation » au
début indique le rôle de chaque partie :

| Partie | Contenu |
|---|---|
| **0. Paramètres** | Lecture de `config/parametres.json`, chemins d'entrée et de sortie, session Spark, fonction `journal` |
| **Fonctions** | Lecture (`lire_brut` avec schéma explicite), rejets (`appliquer_rejets`), jointure contrôlée (`joindre`), mesures (`indicateurs`, `ratios`), écriture avec provenance (`ecrire`, `ecrire_gold`) |
| **Transformations** | Une section par table ou par indicateur, avec la règle appliquée (R1 à R8) |
| **Contrôles** | Relecture après écriture, comptages, clés, totaux |
| **Écritures** | Parquet dans `data/silver/` ou `data/gold/`, et schéma de référence exporté dans `docs/data-dictionary/schemas/` |
| **Journal et résultats** | Bilan JSON dans `outputs/`, journal dans `outputs/logs/<notebook>.log` |

## 6. Sorties produites

| Sortie | Produite par | Description |
|---|---|---|
| `data/silver/{sales,products,stores,dates}/` | `nettoyage_silver` | Données nettoyées, types explicites, provenance |
| `data/silver/rejects/<domaine>/` | `nettoyage_silver` | Lignes écartées, avec `motif_rejet` |
| `data/silver/sales_enriched/` | `enrichissement_ventes` | Ventes + date + produit + magasin, partitionné par `annee` |
| `data/gold/*/` (6 tables) | `agregations_gold` | Indicateurs qui répondent aux questions du Jour 1 |
| `docs/data-dictionary/schemas/*.json` | nettoyage, enrichissement, agrégations | Schémas de référence Silver et Gold |
| `outputs/bilan_nettoyage.json`, `bilan_jointures.json`, `bilan_gold.json` | pipeline | Bilans chiffrés de chaque étape |
| `outputs/controles_silver.json`, `rapport_qualite.json` | contrôles | Résultat de chaque contrôle |
| `outputs/formats/`, `comparaison_formats.json` | `comparaison_formats` | Même jeu en Parquet, CSV et JSON, avec les mesures |
| `outputs/logs/pipeline_<date>.log` | `run_pipeline.sh` | Début, fin, durée et statut de chaque notebook |
| `outputs/logs/<notebook>.log` et `<notebook>_<date>.out` | notebooks et script | Journal de chaque notebook, et sortie technique de Jupyter (utile en cas d'erreur) |

Documentation :

| Document | Contenu |
|---|---|
| `docs/architecture/fiche_environnement.md` | Étape 1 : versions, mode d'exécution, chemins |
| `docs/data-dictionary/inventaire_sources.md` | Étape 2 : inventaire des sources |
| `docs/transformations/regles_nettoyage.md` | Étape 4 : règles R1 à R8 (anomalie, règle, action, justification) |
| `docs/transformations/transformations_resultats.md` | Étape 5 : jointures, agrégations, résultats |
| `docs/data-dictionary/silver.md` | Étape 6 : organisation, nommage, provenance, colonnes Silver |
| `docs/data-dictionary/gold.md` | Étape 7 : finalité, granularité, mesures, règles et limites de chaque table Gold |
| `docs/architecture/comparaison_formats.md` | Étape 8 : CSV / JSON / Parquet, et pourquoi Parquet n'est pas ACID |
| `docs/quality/rapport_qualite.md` | Étape 9 : rapport de qualité |

## 7. Contrôles disponibles

| Contrôle | Où | Résultat actuel |
|---|---|---|
| Contrôles intégrés au traitement | Fin de `nettoyage_silver` (clés uniques et non nulles), `enrichissement_ventes` (lignes avant = après chaque jointure), `agregations_gold` (totaux Gold = Silver) | Arrêt du notebook (`assert`) en cas d'écart |
| Contrôles techniques Silver | `tests/controles_silver.ipynb` | 77 contrôles : présence, format `PAR1`, lisibilité, nombre de lignes, schéma, cohérence. Tous OK |
| Contrôles qualité | `tests/controles_qualite.ipynb` | 152 contrôles : complétude, unicité, validité des types, cohérence, volumes, clés candidates, intégrité référentielle. 135 OK, 17 ALERTE, 0 KO |
| Lecture Parquet | `notebooks/comparaison_formats.ipynb` | Relecture, schéma, lignes, valeurs et répertoire : OK |

## 8. Limites connues

- **Échantillon** : `store_sales` est réduit à 10 % des tickets, car le
  fichier complet sature une machine de 5 Go. Les montants absolus valent
  environ 10 % du réel. Les taux, parts et évolutions restent représentatifs.
  Passer `echantillon.actif` à `false` sur une machine plus puissante.
- **Périmètre** : uniquement les ventes en magasin. Il manque le web
  (`web_sales`), les retours (`store_returns`) et les stocks (`inventory`).
  Certaines questions du Jour 1 restent donc sans réponse : part magasin /
  web, taux de retour, ruptures de stock.
- **Données synthétiques** : 74 % des lignes ont une marge négative, les
  remises tournent autour de 50 %, et les dates de fermeture des magasins
  sont incohérentes (remplacées par `null`). La devise n'est pas indiquée.
- **Décembre 2005 incomplet** : la dernière vente date du 13/12/2005.
- **Parquet n'est pas ACID** : un `overwrite` interrompu peut laisser un
  répertoire partiel. Relancer le notebook concerné, puis les contrôles.
- **Exécution locale** : `local[2]`, un notebook à la fois. Le pipeline
  n'est pas planifié et n'est pas exécuté sur le cluster.
- **Chemin de la source** : `chemins.source_tpcxbb` désigne un dossier de
  cette machine. Il faut l'adapter ailleurs.
- **Étapes 1 à 3** : elles gardent leurs chemins dans le notebook et lisent
  les fichiers complets. Ce sont des explorations ponctuelles, hors
  pipeline.

## Arborescence

Cette arborescence est une convention de projet : elle n'est imposée ni par
TPCx-BB, ni par Hadoop, ni par Spark.

```
retail-intelligence-platform/
+-- run_pipeline.sh          lance le pipeline (etapes 4 a 9)
+-- config/
|   +-- parametres.json      chemins, echantillon, Spark, seuils qualite
+-- transformations/
|   +-- exploration/         etapes 2-3 : inventaire, exploration
|   +-- cleaning/            etape 4 : Raw -> Silver
|   +-- enrichment/          etape 5 : jointures -> sales_enriched
|   +-- aggregation/         etapes 5 et 7 : Silver -> Gold
+-- tests/                   etapes 1, 6, 9 : environnement, controles Silver, qualite
+-- notebooks/               etape 8 : comparaison des formats
+-- docs/
|   +-- architecture/        environnement, comparaison des formats
|   +-- data-dictionary/     inventaire, Silver, Gold, schemas/
|   +-- transformations/     regles de nettoyage, resultats
|   +-- quality/             rapport de qualite
+-- data/
|   +-- samples/             fichier de test, echantillon store_sales
|   +-- raw/  bronze/        vides (Raw lu dans le dossier source)
|   +-- silver/  gold/       produits par le pipeline (Parquet)
+-- outputs/                 bilans, journaux, fichiers de test
+-- README.md
```
