# Fiche d'environnement - TP Jour 3, Étape 1

Date du relevé : 18/11/2026

Script de vérification : `tests/verif_environnement.ipynb`

## Versions observées

| Élément           | Valeur observée               |
|-------------------|-------------------------------|
| Système           | Ubuntu 26.04.1 LTS            |
| Python            | 3.14.4 (environnement `.venv`) |
| PySpark           | 4.3.0                         |
| Spark             | 4.3.0                         |
| Java              | OpenJDK 21.0.13               |
| Hadoop (machine)  | 3.5.0                         |

## Mode d'exécution

| Élément              | Valeur observée                          |
|----------------------|------------------------------------------|
| Mode                 | `local[*]` (Spark local, sans cluster)   |
| Cœurs utilisés       | 8                                        |
| Mémoire du driver    | 1g (valeur par défaut)                   |
| Mémoire de la machine| 5,2 Gio                                  |
| Système de fichiers par défaut | `hdfs://localhost:9000` (lu dans `HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop`) |

Point d'attention : comme la configuration Hadoop est chargée, un chemin sans
préfixe est envoyé vers HDFS. Pour lire ou écrire sur le disque local, les
chemins sont préfixés par `file://`.

## Chemins utilisés

| Rôle               | Chemin                                       |
|--------------------|----------------------------------------------|
| Espace de travail  | `tp3_lolo/retail-intelligence-platform/`     |
| Fichier de test    | `data/samples/magasins_test.csv`             |
| Données sources    | `data/raw/`, `data/bronze/`                  |
| Données nettoyées  | `data/silver/`                               |
| Données analytiques| `data/gold/`                                 |
| Sortie de test     | `outputs/test_environnement/` (Parquet)      |

## Vérifications réalisées

| Vérification                                   | Résultat |
|------------------------------------------------|----------|
| Lancer un interpréteur Python                  | OK       |
| Initialiser une session Spark                  | OK       |
| Lire un fichier de test (CSV, 3 lignes)        | OK       |
| Afficher le schéma                             | OK (`magasin: string`, `ville: string`, `chiffre_affaires: double`) |
| Écrire un résultat de test (Parquet, `outputs/`) | OK, relu : 3 lignes |

Le fichier source `data/samples/magasins_test.csv` n'est pas modifié :
le résultat de test est écrit dans le répertoire distinct `outputs/`.
