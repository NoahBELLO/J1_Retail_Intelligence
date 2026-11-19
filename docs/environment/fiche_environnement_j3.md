# Fiche d'environnement - TP Jour 3, Étape 1

Date du relevé : 18/11/2026

Chacun a installé et testé l'environnement sur sa propre machine.

- Lorenzo : `tests/environnement/verif_environnement.ipynb`
- Noah : `preuves/j3/spark/etape1_sorties_commandes.txt`

## Versions observées

| Élément | Lorenzo | Noah |
|---|---|---|
| Système | Ubuntu 26.04.1 LTS | Ubuntu 24.04.5 dans WSL (Windows 11) |
| Python | 3.14.4 (environnement `.venv`) | 3.12.3 (environnement `.venv`) |
| PySpark / Spark | 4.3.0 | 4.3.0 |
| Java (Spark) | OpenJDK 21.0.13 | OpenJDK 21.0.13 |
| Hadoop (machine) | 3.5.0 | 3.5.0 (Java 17) |
| JupyterLab | installé (`nbconvert`) | 4.6.6 |

## Mode d'exécution

| Élément | Lorenzo | Noah |
|---|---|---|
| Mode | `local[*]` pour le test, `local[2]` pour le pipeline (Spark local, sans cluster) | `local[*]` (Spark local, sans cluster) |
| Cœurs utilisés | 8 au test, 2 pour le pipeline | 2, puis 4 |
| Mémoire du driver | 1g au test, 768 Mo pour le pipeline | 1g, puis 2g pour les scripts |
| Mémoire de la machine | 5,2 Gio | 3,8 Gio pour WSL, puis 8 Gio (voir ci-dessous) |
| Système de fichiers par défaut | `hdfs://localhost:9000` (lu dans `HADOOP_CONF_DIR`) | `hdfs://localhost:9000` dans Jupyter |

Point d'attention commun : comme la configuration Hadoop est chargée, un chemin
sans préfixe est envoyé vers HDFS. On écrit donc toujours le préfixe :
`file://` pour un fichier sur le disque, `hdfs://localhost:9000/` pour un
fichier dans HDFS.

Mémoire : avec 4 Go, le WSL de Noah s'est bloqué quand plusieurs sessions Spark
tournaient en même temps que HDFS et NiFi. La limite a été passée à 8 Go et 4
cœurs (`C:\Users\Noah\.wslconfig`). Chez Lorenzo, `store_sales` complet saturait
la machine : le pipeline des notebooks travaille donc sur un échantillon de 10 %
des tickets.

## Chemins utilisés

| Rôle | Pipeline des notebooks (Lorenzo) | Scripts PySpark sur HDFS (Noah) |
|---|---|---|
| Espace de travail | racine du dépôt | racine du dépôt (`transformations/`) |
| Fichier de test | `data/samples/magasins_test.csv` | `hdfs:///retail-lake/raw/tpcxbb/initial/item/item.dat` |
| Données sources | `~/DEV/tpcxbb_source/retail_project/data/` (fichiers bruts, lus sans être modifiés) | `/retail-lake/raw/tpcxbb/initial/` dans HDFS |
| Données nettoyées | `data/silver/` | `/retail-lake/silver/` |
| Données analytiques | `data/gold/` | `/retail-lake/gold/` |
| Sortie de test | `outputs/test_environnement/` (Parquet) | `~/retail-intelligence/tp3/outputs/test_ecriture/` (CSV) |

## Vérifications réalisées

| Vérification | Lorenzo | Noah |
|---|---|---|
| Lancer un interpréteur Python ou un notebook | OK | OK |
| Initialiser une session Spark | OK | OK |
| Lire un fichier de test | OK (CSV, 3 lignes) | OK (`item.dat` depuis HDFS, 17 820 lignes) |
| Afficher le schéma | OK (`magasin: string`, `ville: string`, `chiffre_affaires: double`) | OK (22 colonnes, `integer`, `string`, `date`, `double`) |
| Écrire un résultat de test | OK (Parquet dans `outputs/`, relu : 3 lignes) | OK (CSV dans `outputs/test_ecriture/`, relu : 10 lignes) |

Les fichiers sources ne sont jamais modifiés : les résultats de test sont
écrits dans des répertoires distincts.
