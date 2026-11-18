# Tests UC3 – HDFS

Tests du §15.1, commandes HDFS et contrôles de stockage (livrables 5 et 6).

> Preuves : `preuves/j2/hadoop/` (étape 1) et `preuves/j2/hdfs/` (étapes 2 à 5), pour Noah et pour Lorenzo (`*_lorenzo.txt`).

## 1. Résultats des tests

| Test | Résultat attendu | Commande | Résultat | OK |
|---|---|---|---|---|
| Accès HDFS | HDFS accessible | `hdfs dfsadmin -report`, `hdfs fsck /` | 1 DataNode actif, `HEALTHY` | OK |
| Création de répertoires | Arborescence présente | `hdfs dfs -ls -R /retail-lake` | Tous les dossiers de `docs/architecture/architecture-data-lake.md` | OK |
| Dépôt de fichier | Fichier présent | `hdfs dfs -ls` | `store_sales.dat`, 92 764 700 octets | OK |
| Lecture ou récupération | Fichier accessible | `hdfs dfs -cat … \| head`, `hdfs dfs -get` | Mêmes lignes qu'en local, copie récupérée de même taille | OK |
| Permissions | Droits cohérents | `hdfs dfs -ls -d`, `hdfs dfs -ls` | Dossiers `drwxr-xr-x`, fichier `-rw-r--r--`, le propriétaire est celui qui a lancé HDFS | OK |

## 2. Commandes HDFS utilisées

```bash
# État et nœuds
hdfs dfsadmin -report
hdfs fsck /

# Dossiers
hdfs dfs -ls /
hdfs dfs -mkdir -p /retail-lake
hdfs dfs -ls -d /retail-lake          # permissions du dossier
hdfs dfs -du -s -h /retail-lake       # taille totale

# Dépôt (convention du groupe : un sous-dossier par table)
hdfs dfs -mkdir -p /retail-lake/raw/tpcxbb/initial/store_sales
hdfs dfs -put retail_project/data/store_sales/store_sales.dat /retail-lake/raw/tpcxbb/initial/store_sales/

# Vérifications
hdfs dfs -ls /retail-lake/raw/tpcxbb/initial/store_sales
hdfs dfs -cat /retail-lake/raw/tpcxbb/initial/store_sales/store_sales.dat | head -n 3
hdfs dfs -get /retail-lake/raw/tpcxbb/initial/store_sales/store_sales.dat /tmp/store_sales_depuis_hdfs.dat
```

## 3. Contrôle d'intégrité (étape 5)

Méthode : on récupère le fichier depuis HDFS dans un dossier temporaire (en dehors du projet), puis on le compare au fichier d'origine.

```bash
sha256sum retail_project/data/store_sales/store_sales.dat /tmp/store_sales_depuis_hdfs.dat
cmp retail_project/data/store_sales/store_sales.dat /tmp/store_sales_depuis_hdfs.dat && echo "IDENTIQUES"
wc -l retail_project/data/store_sales/store_sales.dat /tmp/store_sales_depuis_hdfs.dat
rm /tmp/store_sales_depuis_hdfs.dat
```

| Contrôle | Noah | Lorenzo |
|---|---|---|
| Taille | 92 764 700 = 92 764 700 | 92 764 700 = 92 764 700 |
| SHA-256 | `7e0a7f16…3d2e` identique | `7e0a7f16…3d2e` identique |
| Comparaison octet par octet (`cmp`) | identique | identique (aussi vérifié avec `md5sum`) |
| Nombre de lignes | 667 579 | 667 579 |
| Blocs (`hdfs fsck … -blocks`) | — | `HEALTHY`, 1 bloc, 0 abîmé |

Conclusion : le fichier stocké dans HDFS est exactement le même que l'original, sur nos deux machines.

Limite : il faut récupérer tout le fichier pour le comparer, ce qui serait long avec de très gros fichiers.
