# J1_Retail_Intelligence

Retail Intelligence Platform (IPSSI).

- Jour 1 : UC-01 et UC-02 (besoin, exploration, architecture).
- Jour 2 : UC-03 et UC-04 (Data Lake HDFS, ingestion NiFi). Organisation des fichiers du Jour 2 selon le §17 du TP.
- Jour 3 : UC-06 (transformation, qualité, Silver / Gold, Parquet). Organisation des fichiers du Jour 3 selon le §10.1 du TP.
- Jour 4 : UC-08 et UC-07 (analyse et visualisation, architecture Azure en parcours B local / open source). Organisation des fichiers du Jour 4 selon le §13.2 du TP.

## Contenu – Jour 1

### 01_UC01_besoin_exploration – Besoin métier et exploration des données
- `UC01_cadrage_metier.md` : profils utilisateurs
- `UC01_questions_decisionnelles.md` : questions, décisions et priorités
- `UC01_dictionnaire_KPI.md` : les 6 KPI
- `UC01_inventaire_sources.md` : inventaire des fichiers TPCx-BB
- `UC01_qualification_donnees.md` : qualité des données et relations entre tables
- `UC01_limites_et_hypotheses.md` : limites et hypothèses
- `UC01_schema_fonctionnel.md` : schéma utilisateurs → questions → KPI → données
- `preuves/` : scripts d'exploration et leurs résultats
  - Noah : `explorer_donnees.py` → `inventaire_fichiers.csv`, `inventaire_colonnes.csv` ; `verifier_relations.py` → `resultats_relations.csv`
  - Lorenzo : `etape_c_profilage.py` → `etape_c_profil.json` ; `etape_d_relations.py` → `etape_d_relations.json` (les deux utilisent `tpcxbb_schema.json`)
  - `arborescence_donnees.txt`, `apercu_fichiers.txt` : liste des fichiers et aperçu de leur contenu

### 02_UC02_architecture – Architecture Data
- `UC02_comparaison_architectures.md` : contraintes et comparaison DW / Data Lake / Lakehouse
- `UC02_architecture_cible.md` : architecture logique et zones Bronze / Silver / Gold
- `UC02_schema_flux.md` : flux de données
- `UC02_positionnement_composants.md` : composants et leur statut
- `UC02_gouvernance.md` : règles de gouvernance
- `UC02_local_vers_azure.md` : comparaison local / Azure
- `preuves/`

## Contenu – Jour 2

### docs/
- `operations/environnement-j2.md` : nos deux machines, Hadoop, HDFS, NiFi (livrables 1 et 2)
- `ingestion/inventaire-sources.md` : fichiers TPCx-BB utilisés (livrable 3)
- `architecture/architecture-data-lake.md` : arborescence du Data Lake (livrable 4)
- `ingestion/flux-nifi.md` : flux GetFile → PutHDFS, configuration, exécution, erreur contrôlée (livrables 7, 8, 9)
- `ingestion/provenance.md` : provenance du fichier transféré (livrable 11)
- `operations/erreurs-corrections.md` : tableau des erreurs et des corrections (livrable 10)
- `questions-recul-j2.md` : questions de recul du TP

### ingestion/
- `nifi/flux_getfile_puthdfs.json` : export du flux NiFi (*Download Flow Definition*)

### tests/
- `hdfs/tests-uc03.md` : tests HDFS, commandes et contrôle d'intégrité (livrables 5 et 6)
- `ingestion/tests-uc04.md` : tests du flux NiFi

### preuves/j2/
- `hadoop/` : étape 1
- `hdfs/` : étapes 2 à 5
- `nifi/` : étapes 6 à 11 (captures et sorties)

Les fichiers `*_lorenzo.*` sont les preuves de Lorenzo, les autres celles de Noah.

## Contenu – Jour 3 (UC-06)

Deux chaînes de traitement font la même transformation Raw → Silver → Gold :

- **Pipeline des notebooks** (Lorenzo) : 4 sources (`store_sales`, `item`, `store`, `date_dim`), 6 jeux Gold. Il lit les fichiers bruts sur le disque et travaille sur un échantillon de 10 % des tickets. C'est la chaîne principale.
- **Scripts PySpark sur le Data Lake HDFS** (Noah) : 2 sources (`store_sales`, `item`) et 1 jeu Gold, sur le fichier **complet**. Ils lisent la zone `raw` de HDFS du Jour 2 et écrivent dans `silver`, `gold` et `quality`. Ils confirment les résultats de l'échantillon (part de `Music` : 45,02 % sur l'échantillon, 45,17 % sur le fichier complet).

### Livrables obligatoires (§10.2)

| N° | Livrable | Fichiers |
|---|---|---|
| 1 | Fiche environnement | `docs/environment/fiche_environnement_j3.md`, `tests/environnement/` |
| 2 | Inventaire technique | `docs/data-dictionary/inventaire_sources.md`, `notebooks/exploration/inventaire_sources.ipynb` |
| 3 | Notebook d'exploration | `notebooks/exploration/exploration_sources.ipynb` |
| 4 | Règles de nettoyage | `docs/transformations/regles_nettoyage.md`, `notebooks/cleaning/nettoyage_silver.ipynb` |
| 5 | Scripts PySpark | `notebooks/cleaning/`, `notebooks/transformations/`, `run_pipeline.sh` ; scripts `transformations/silver/`, `transformations/gold/` |
| 6 | Données Silver | `data/silver/` (régénérées), `docs/data-dictionary/silver.md`, `docs/data-dictionary/schemas/silver_*.json` |
| 7 | Données Gold | `data/gold/` (régénérées), `docs/data-dictionary/gold.md`, `docs/data-dictionary/schemas/gold_*.json` |
| 8 | Données Parquet | `docs/architecture/comparaison_formats.md`, `notebooks/transformations/comparaison_formats.ipynb` |
| 9 | Rapport qualité | `docs/quality/rapport_qualite.md`, `notebooks/quality/` |
| 10 | README | ce fichier, section « Reproduire les traitements du Jour 3 » |
| 11 | Preuves | sorties enregistrées dans les notebooks, `preuves/j3/` |
| – | Questions de recul | `docs/questions-recul-j3.md` |

### Arborescence du Jour 3

```
docs/
  environment/          étape 1 : fiche environnement (nos deux machines)
  data-dictionary/      étapes 2, 6, 7 : inventaire, Silver, Gold, schemas/
  transformations/      étapes 4, 5 : règles de nettoyage, transformations et résultats
  quality/              étape 9 : rapport de qualité
  architecture/         étape 8 : comparaison des formats
  questions-recul-j3.md
notebooks/
  exploration/          étapes 2, 3 : inventaire, exploration
  cleaning/             étapes 4, 6 : Raw -> Silver
  transformations/      étapes 5, 7, 8 : jointures, Gold, comparaison des formats
  quality/              étapes 6, 9 : contrôles Silver, rapport de qualité
transformations/
  silver/  gold/        scripts PySpark sur HDFS (Raw -> Silver -> Gold)
  config.py  commun.py  03_formats.py  04_qualite.py  lancer_tout.sh
config/parametres.json  paramètres du pipeline des notebooks
data/
  samples/              fichier de test, échantillon de store_sales (régénéré)
  raw/  bronze/         vides : Raw est lu dans le dossier source ou dans HDFS
  silver/  gold/        produits par le pipeline (Parquet, non versionnés)
tests/environnement/    étape 1 : tests d'installation et de l'environnement
outputs/                bilans, journaux, fichiers de test (non versionnés)
run_pipeline.sh         lance le pipeline des notebooks
preuves/j3/             preuves de Noah (sorties des étapes 1 à 10, copie de son espace de travail)
```

Les dossiers `docs/lakehouse/` et `docs/nosql/` du §10.1 correspondent aux parties facultatives (partie avancée et UC-05), qui n'ont pas été réalisées.

## Contenu – Jour 4 (UC-08 et UC-07)

Comme au Jour 3, deux notebooks font la même analyse UC-08 :

- **Notebook principal** (Lorenzo) : `analytics/notebooks/TP4_Retail_Intelligence.ipynb`. Il lit `data/silver/` et `data/gold/` du pipeline des notebooks, sur un échantillon de 10 % des tickets, avec les dates, les produits et les magasins. 3 analyses, 4 graphiques. C'est la chaîne principale.
- **Notebook HDFS** (Noah) : `analytics/notebooks/TP4_HDFS_fichier_complet.ipynb`. Il lit les Silver et Gold des scripts HDFS, sur le **fichier complet**, sans les dates. Il confirme les résultats de l'échantillon (mêmes taux et moyennes à moins de 1 % près), et montre que le classement des magasins n'est pas fiable sur l'échantillon.

UC-07 est fait en **parcours B (local / open source)** : la partie Azure est étudiée et simulée, **aucune ressource Azure n'a été créée**.

### Livrables obligatoires (§13.1)

| Code | Livrable | Fichiers |
|---|---|---|
| J4-01 | Inventaire analytique | `docs/analytics/inventaire-jeux.md`, `analytics/outputs/inventaire_jeux.csv` |
| J4-02 | Dictionnaire des KPI | `docs/analytics/kpi-dictionary.md`, `analytics/outputs/kpi_dictionnaire.csv`, `analytics/outputs/kpi.csv`, `analytics/outputs/hdfs/kpi.csv` |
| J4-03 | Analyses statistiques | `docs/analytics/business-analysis.md` (partie 1), `analytics/outputs/statistiques.csv`, `analytics/outputs/hdfs/statistiques.csv` |
| J4-04 | Analyses métier | `docs/analytics/business-analysis.md` (partie 2), `analytics/outputs/analyse_*.csv`, `ventes_par_magasin.csv`, `hdfs/ca_par_categorie.csv`, `hdfs/kpi_par_magasin.csv` |
| J4-05 | Visualisations | `analytics/visualizations/` (4 PNG) et `analytics/visualizations/hdfs/` (2 PNG), décrites dans `business-analysis.md` (partie 3) |
| J4-06 | Synthèse décisionnelle | `docs/analytics/interpretation.md` |
| J4-07 | Architecture Azure | `docs/cloud/azure-architecture.md` (composants, schéma, ADF / Synapse, architecture locale, correspondance, coûts) |
| J4-08 | Organisation ADLS Gen2 | `docs/cloud/adls-organization.md` (zones, chemins, nommage, HNS) |
| J4-09 | Sécurité | `docs/cloud/security-matrix.md` |
| J4-10 | Preuves Azure | `azure/simulation/simulation-adls-gen2.md` (simulation documentée) ; preuve du stockage local : `preuves/j4/architecture/sorties_commandes.txt` |
| J4-11 | README J4 | ce fichier : cette partie et « Reproduire les analyses du Jour 4 » |
| – | Tests (§12) | `tests/analytics/tests-uc08.md`, `tests/cloud/tests-uc07.md`, `analytics/outputs/tests_uc08.csv` |
| – | Questions de recul (§15) | `docs/questions-recul-j4.md` |

### Arborescence du Jour 4

```
analytics/
  notebooks/            TP4_Retail_Intelligence.ipynb (principal), TP4_HDFS_fichier_complet.ipynb
  outputs/              tableaux CSV du notebook principal
    hdfs/               tableaux CSV du notebook HDFS
  visualizations/       graphiques PNG du notebook principal
    hdfs/               graphiques PNG du notebook HDFS
docs/
  analytics/            J4-01 à J4-06 : inventaire, KPI, analyses, synthèse
  cloud/                J4-07 à J4-09 : architecture, organisation ADLS Gen2, sécurité
  questions-recul-j4.md
azure/
  simulation/           J4-10 : simulation de la mise en œuvre ADLS Gen2
config/parametres_tp4.json   paramètres du notebook principal (chemins, Spark, graphiques)
tests/
  analytics/            tests UC-08 (§12.1)
  cloud/                tests UC-07 (§12.2)
preuves/j4/             preuves de Noah (installation, sorties du notebook, relevé HDFS, copie de son espace de travail)
```

Les dossiers `azure/architecture/`, `azure/configuration/` et `azure/evidence/` du §13.2 n'ont pas été créés : rien n'a été déployé sur Azure, il n'y a donc ni configuration ni capture. Le dossier `analytics/scripts/` n'a pas été créé non plus : toute l'analyse est dans les notebooks. Les parties complémentaires et avancées (CO-01 à CO-05, AV-01 à AV-04) n'ont pas été réalisées.

## Contributions individuelles (05_contribution_individuelle)
- `contribution_Noah.md`, `contribution_Lorenzo.md` : Jour 1
- `contribution_Noah_J2.md` : Jour 2
- `contribution_Noah_J3.md` : Jour 3
- `contribution_Noah_J4.md` : Jour 4

## Relancer les scripts d'exploration

Depuis `01_UC01_besoin_exploration/preuves/` :

```
python explorer_donnees.py <chemin vers retail_project>
python verifier_relations.py <chemin vers retail_project/data>
python etape_c_profilage.py <chemin vers retail_project> etape_c_profil.json
python etape_d_relations.py <chemin vers retail_project> etape_d_relations.json
```

Les données (`retail_project/`) ne sont pas dans le dépôt, à cause de leur taille.

## Reproduire l'ingestion du Jour 2

### Versions
- Ubuntu 24.04 (WSL chez Noah, installé directement chez Lorenzo).
- Hadoop 3.5.0 avec Java 17, mode une seule machine (`hdfs://localhost:9000`, réplication 1).
- NiFi 2.12.0 avec Java 21, plus les modules `nifi-hadoop-libraries-nar` et `nifi-hadoop-nar` 2.12.0 dans `/opt/nifi/extensions`.

### Démarrage
```bash
start-dfs.sh                                   # HDFS (Java 17)
jps                                            # NameNode, DataNode, SecondaryNameNode
hdfs dfsadmin -report
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
/opt/nifi/bin/nifi.sh start                    # NiFi (Java 21)
/opt/nifi/bin/nifi.sh status                   # doit afficher UP
```
Interface : https://localhost:8443/nifi (identifiants générés au premier démarrage, dans `nifi-app.log`, non recopiés ici).

### Chemins HDFS
- `/retail-lake/raw/tpcxbb/initial/<table>/` : dépôt manuel (UC-03), par exemple `store_sales/store_sales.dat`.
- `/retail-lake/raw/nifi/` : dépôt par NiFi (UC-04).
- `/retail-lake/{bronze,silver,gold,quality,logs}` : zones prévues pour la suite.

### Paramètres NiFi (non sensibles)
- GetFile : `Input Directory = /data/nifi/input`, `Keep Source File = false`, `Recurse Subdirectories = false`.
- PutHDFS : `Hadoop Configuration Resources = /opt/hadoop/etc/hadoop/core-site.xml,/opt/hadoop/etc/hadoop/hdfs-site.xml`, `Directory = /retail-lake/raw/nifi`, `Conflict Resolution Strategy = fail`.
- Le flux complet peut être réimporté depuis `ingestion/nifi/flux_getfile_puthdfs.json`.
- Sous WSL, laisser `nifi.web.https.host` vide dans `nifi.properties` pour ouvrir l'interface depuis Windows.

### Arrêt (dans cet ordre)
1. Arrêter les processeurs dans NiFi (clic droit → *Stop*).
2. `/opt/nifi/bin/nifi.sh stop`
3. `stop-dfs.sh`

## Reproduire les traitements du Jour 3

### Prérequis
- **Environnement Python** `.venv` à la racine du dépôt, avec `pyspark` et `jupyter` (`nbconvert`) :
  ```bash
  python3 -m venv .venv && .venv/bin/pip install pyspark jupyterlab
  ```
  Un autre environnement peut être utilisé en définissant les variables `JUPYTER` et `PYTHON`.
- **Java 17 ou plus** pour Spark (21 observé).
- **Données TPCx-BB** (`retail_project/data`), hors du dépôt à cause de leur taille.
- **Schéma du Jour 1** : `01_UC01_besoin_exploration/preuves/tpcxbb_schema.json`, schéma de référence (noms et types des colonnes).
- **`awk`**, pour créer l'échantillon.
- **Mémoire** : environ 1,5 Go de RAM libre pour le pipeline des notebooks, 2 Go pour les scripts HDFS. Une seule session Spark à la fois (fermer les autres notebooks).
- **HDFS** : seulement pour les scripts de `transformations/` (`start-dfs.sh`).

### Versions observées
Détail dans `docs/environment/fiche_environnement_j3.md`.

| Élément | Lorenzo | Noah |
|---|---|---|
| Système | Ubuntu 26.04.1 LTS | Ubuntu 24.04.5 (WSL) |
| Python | 3.14.4 | 3.12.3 |
| PySpark / Spark | 4.3.0 | 4.3.0 |
| Java (Spark) | OpenJDK 21.0.13 | OpenJDK 21.0.13 |
| Hadoop | 3.5.0 | 3.5.0 |
| Mode d'exécution | `local[2]`, 768 Mo | `local[*]`, 2 Go |

### Emplacement des données

| Zone | Pipeline des notebooks | Scripts HDFS |
|---|---|---|
| **Raw** (jamais modifiée) | `<retail_project>/data/<table>/<table>.dat`, lu sur place | `/retail-lake/raw/tpcxbb/initial/<table>/` (déposé au Jour 2) |
| Échantillon | `data/samples/store_sales_echantillon.dat` (10 % des tickets, 66 593 lignes) | – (fichier complet) |
| **Silver** | `data/silver/` : `sales`, `products`, `stores`, `dates`, `sales_enriched`, `rejects/` | `/retail-lake/silver/store_sales`, `/retail-lake/silver/item` |
| **Gold** | `data/gold/` : `ca_mensuel`, `ca_annuel`, `ca_marge_par_categorie`, `top10_produits`, `ca_marge_par_magasin`, `taux_remise_mensuel` | `/retail-lake/gold/ca_par_categorie` |
| Rejets et rapport | `data/silver/rejects/`, `outputs/rapport_qualite.json` | `/retail-lake/quality/rejets/`, `/retail-lake/quality/rapport_qualite/` |
| Journaux | `outputs/logs/` | `outputs/logs_hdfs/` |

Tout est en Parquet, sauf le rapport qualité (JSON ou CSV). Les données produites et `outputs/` ne sont pas versionnées (voir `.gitignore`) : les commandes ci-dessous les recréent.

### Paramètres
- Pipeline des notebooks : **`config/parametres.json`**. Aucun chemin n'est écrit en dur dans les notebooks du pipeline : chacun lit ce fichier dans sa première cellule.

  | Paramètre | Valeur par défaut | Rôle |
  |---|---|---|
  | `chemins.source_tpcxbb` | `~/DEV/tpcxbb_source/retail_project/data` | Dossier des fichiers bruts. **À adapter** sur une autre machine |
  | `chemins.schema_tpcxbb` | `01_UC01_besoin_exploration/preuves/tpcxbb_schema.json` | Schéma de référence |
  | `chemins.echantillon_ventes`, `silver`, `gold`, `outputs`, `logs`, `schemas` | `data/...`, `outputs/...`, `docs/...` | Entrées et sorties, relatives à la racine du dépôt |
  | `echantillon.actif` | `true` | `false` pour traiter `store_sales` complet (machine plus puissante) |
  | `echantillon.modulo_ticket` | `10` | Tickets gardés : numéro multiple de 10, soit 10 % |
  | `spark.master`, `spark.config` | `local[2]`, 768 Mo, 4 partitions | Ressources Spark |
  | `periode_attendue` | du 2001-01-01 au 2005-12-13 | Utilisée par les contrôles |
  | `qualite.*` | vide < 1 %, tolérance 0,01, mois ≥ 50 % de la moyenne | Seuils des contrôles qualité |

- Scripts HDFS : **`transformations/config.py`** (adresse HDFS, lot `initial` ou `refresh`, chemins, mémoire, 1 copie HDFS).

### Ordre d'exécution

**Étapes 1 à 3** (lancées à la main une fois, sur les fichiers complets) :
1. `tests/environnement/verif_environnement.ipynb` : versions, session Spark, lecture et écriture d'un fichier de test.
2. `notebooks/exploration/inventaire_sources.ipynb` : inventaire technique.
3. `notebooks/exploration/exploration_sources.ipynb` : exploration (schémas, valeurs manquantes, doublons, valeurs atypiques).

**Pipeline des notebooks (étapes 4 à 9)** :
```bash
./run_pipeline.sh              # notebooks 1 à 5
./run_pipeline.sh --formats    # + comparaison des formats
```
Le script crée l'échantillon s'il n'existe pas, puis exécute les notebooks un par un. Chaque notebook lit ce que le précédent a écrit, et le script s'arrête au premier en échec :
```
Raw (.dat)
  |  1. notebooks/cleaning/nettoyage_silver.ipynb                  étapes 4 et 6
  v
silver/sales, products, stores, dates (+ silver/rejects/)
  |  2. notebooks/transformations/enrichissement_ventes.ipynb      étape 5
  v
silver/sales_enriched
  |  3. notebooks/transformations/agregations_gold.ipynb           étapes 5 et 7
  v
gold/*
     4. notebooks/quality/controles_silver.ipynb                   étape 6 : contrôles techniques
     5. notebooks/quality/controles_qualite.ipynb                  étape 9 : rapport de qualité
     6. notebooks/transformations/comparaison_formats.ipynb        étape 8 (option --formats)
```
Pour lancer un notebook seul : `.venv/bin/jupyter nbconvert --to notebook --execute --inplace <notebook>`, ou l'ouvrir dans Jupyter (`.venv/bin/jupyter lab`).

Chaque notebook du pipeline suit la même structure : paramètres, fonctions (lecture avec schéma explicite, rejets, jointure contrôlée, écriture avec provenance), transformations (règles R1 à R8), contrôles, écritures, journal.

**Scripts PySpark sur HDFS** (fichier complet) :
```bash
start-dfs.sh
bash transformations/lancer_tout.sh
```
Ordre : `silver/01_silver.py` (Raw → Silver + rejets), `gold/02_gold.py` (Silver → Gold), `03_formats.py` (CSV / JSON / Parquet), `04_qualite.py` (contrôles).

### Sorties produites
- Pipeline des notebooks : Silver (5 jeux et rejets), Gold (6 jeux), schémas de référence dans `docs/data-dictionary/schemas/`, bilans JSON dans `outputs/`, un journal par notebook dans `outputs/logs/`.
- Scripts HDFS : `silver/store_sales` (667 579 lignes), `silver/item` (17 820 lignes), `gold/ca_par_categorie` (9 lignes), rapport de 36 contrôles, journaux dans `outputs/logs_hdfs/`.

### Contrôles disponibles

| Contrôle | Où | Résultat |
|---|---|---|
| Contrôles intégrés au traitement | `nettoyage_silver` (clés uniques et non nulles), `enrichissement_ventes` (lignes avant = après), `agregations_gold` (totaux Gold = Silver) | Arrêt du notebook en cas d'écart |
| Contrôles techniques Silver | `notebooks/quality/controles_silver.ipynb` | 77 contrôles, tous OK |
| Contrôles qualité | `notebooks/quality/controles_qualite.ipynb` | 152 contrôles : 135 OK, 17 ALERTE, 0 KO |
| Contrôles qualité (fichier complet, HDFS) | `transformations/04_qualite.py` | 36 contrôles : 32 OK, 4 ATTENTION, 0 KO |
| Lecture Parquet | `notebooks/transformations/comparaison_formats.ipynb`, `transformations/03_formats.py` | Relecture, schéma, lignes et valeurs OK |

### Limites connues
- **Échantillon** : le pipeline des notebooks réduit `store_sales` à 10 % des tickets. Les montants valent environ 10 % du réel, mais les taux, les parts et les évolutions restent représentatifs : les scripts HDFS sur le fichier complet donnent les mêmes parts par catégorie.
- **Périmètre** : uniquement les ventes en magasin. Il manque le web, les retours et les stocks, donc certaines questions du Jour 1 restent sans réponse (part magasin / web, taux de retour, ruptures de stock).
- **Données synthétiques** : 74 % des lignes ont une marge négative, les remises tournent autour de 50 %, et les dates de fermeture des magasins sont incohérentes (remplacées par `null`). La devise n'est pas indiquée.
- **Décembre 2005 incomplet** : dernière vente le 13/12/2005.
- **Parquet n'est pas ACID** : un `overwrite` interrompu peut laisser un dossier partiel, sans historique. Il faut relancer le traitement concerné, puis les contrôles.
- **Exécution locale** : une seule machine, un traitement à la fois, pas de planification.
- **Chemin de la source** : `chemins.source_tpcxbb` désigne un dossier de la machine de Lorenzo. Il faut l'adapter ailleurs.

## Reproduire les analyses du Jour 4

### Prérequis
- Les traitements du Jour 3 ont été lancés (voir la partie précédente) :
  - `./run_pipeline.sh` pour le notebook principal (il crée `data/silver/`, `data/gold/` et `outputs/rapport_qualite.json`) ;
  - HDFS démarré et `transformations/lancer_tout.sh` pour le notebook HDFS.
- Environnement Python du Jour 3, avec en plus Matplotlib, Pandas et un noyau Jupyter `retail-tp4` :
  ```bash
  python -m pip install matplotlib "pandas<3" ipykernel
  python -m ipykernel install --user --name retail-tp4 --display-name "Python - Retail TP4"
  ```
  PySpark 4.3 affiche un avertissement avec Pandas 3 : Lorenzo a installé `pandas<3`. Chez Noah, Pandas 3.1.1 marche, et les contrôles (sommes = total) sont bons.
- **Mémoire** : une seule session Spark à la fois (fermer les autres notebooks).

### Versions observées

| Élément | Lorenzo | Noah |
|---|---|---|
| Système | Ubuntu 26.04.1 LTS | Ubuntu 24.04.5 (WSL) |
| Python | 3.14.4 | 3.12.3 |
| PySpark / Spark | 4.3.0, `local[2]`, 768 Mo | 4.3.0, `local[*]`, 2 Go |
| Java (Spark) | OpenJDK 21.0.13 | OpenJDK 21.0.13 |
| Pandas | 2.3.3 | 3.1.1 |
| Matplotlib | 3.11.2 | 3.11.2 |
| JupyterLab | 4.6.6 | 4.6.6 |

### Paramètres
- Notebook principal : `config/parametres_tp4.json` (chemins vers `data/silver/`, `data/gold/` et `outputs/`, ressources Spark, mois incomplet `2005-12`, réglages des graphiques). Le notebook trouve ce fichier en remontant les dossiers : il faut le lancer depuis le dépôt.
- Notebook HDFS : les chemins sont dans sa 2e cellule de code (`hdfs://localhost:9000/retail-lake/...`).

### Lancement
Depuis `analytics/notebooks/`, environ 1 minute par notebook :
```bash
cd analytics/notebooks
jupyter nbconvert --to notebook --execute --inplace TP4_Retail_Intelligence.ipynb

start-dfs.sh && hdfs dfsadmin -safemode wait
jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.kernel_name=retail-tp4 TP4_HDFS_fichier_complet.ipynb
```
On peut aussi ouvrir les notebooks dans JupyterLab, choisir le noyau « Python - Retail TP4 » et lancer *Run > Run All Cells*.

### Sorties produites
- Notebook principal : 10 CSV dans `analytics/outputs/` (inventaire, KPI, statistiques, analyses A1 à A3, tests) et 4 PNG dans `analytics/visualizations/`.
- Notebook HDFS : 4 CSV dans `analytics/outputs/hdfs/` (KPI, statistiques, catégories, magasins) et 2 PNG dans `analytics/visualizations/hdfs/`.

### Contrôles disponibles
- Notebook principal : il s'arrête (`assert`) si une clé n'est pas unique, si les KPI Silver diffèrent du Gold `ca_annuel` ou si un test UC-08 échoue. Résultat : `analytics/outputs/tests_uc08.csv`, 7 tests à `True`.
- Notebook HDFS : CA Silver = CA Gold `ca_par_categorie` (écart 0,00), somme par magasin = total (CA et tickets), un ticket = un seul magasin.

### Limites connues
- **Magasins seulement** : pas de `web_sales` ni de `store_returns`.
- **Échantillon** de 10 % dans le notebook principal : les montants valent environ un dixième du réel, et le classement des magasins n'est pas fiable.
- **Pas de dates ni de noms de magasins** dans le notebook HDFS.
- **Données synthétiques** : marge non utilisée, remise d'environ 50 %, paniers irréalistes, devise supposée en euros.
- **Azure** : rien n'est déployé, la partie Azure est une simulation documentée.
- **Sorties enregistrées du notebook principal** : il a été exécuté par Lorenzo avant la mise en commun, quand le projet était encore dans `tp4_lolo/`. Les chemins affichés dans ses sorties sont donc les anciens. Seuls les chemins de `config/parametres_tp4.json` et du notebook ont été changés, pas les calculs.
