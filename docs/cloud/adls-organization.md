# Organisation ADLS Gen2 et rôle du HNS – TP Jour 4, UC-07 (J4-08)

> Proposition, **non déployée** (parcours B). Les zones et les chemins sont ceux qui existent réellement dans notre HDFS (relevé : `preuves/j4/architecture/sorties_commandes.txt`).

## 1. L'organisation proposée

On reprend **exactement** les zones et les chemins de notre HDFS, avec un conteneur par zone, comme prévu au Jour 1 (`02_UC02_architecture/UC02_local_vers_azure.md`). Comme ça, le passage vers Azure ne change que le début du chemin.

```
Compte de stockage stretailintelligence (HNS activé)
├── raw/                      (conteneur)  fichiers reçus, jamais modifiés
│   ├── tpcxbb/initial/store_sales/store_sales.dat
│   ├── tpcxbb/initial/item/item.dat
│   ├── tpcxbb/refresh/        lot de mise à jour
│   └── nifi/store.dat         dépôt par le flux d'ingestion
├── bronze/                   (conteneur)  tpcxbb/ : prévu, vide pour l'instant
├── silver/                   (conteneur)  une table par dossier (Parquet)
├── gold/                     (conteneur)  ca_mensuel/, ca_par_categorie/, ... (Parquet)
├── quality/                  (conteneur)  rejets/<table>/, rapport_qualite/
└── logs/                     (conteneur)  journaux des traitements
```

En local, le chemin commence par `hdfs://localhost:9000/retail-lake/`. Sur Azure, il commencerait par l'adresse du compte de stockage. La suite du chemin (`silver/store_sales/`) reste la même.

On n'a pas mis de zone `documentation/` comme dans l'exemple du TP : notre documentation est dans Git, pas dans le Data Lake. On n'a pas repris non plus le dossier `tp3/` de HDFS, qui ne servait qu'aux tests du Jour 3.

## 2. Les zones

| Zone | Fonction | Données déposées | Utilisateurs ou traitements | Conservation et traçabilité |
|---|---|---|---|---|
| `raw` | Garder les fichiers tels qu'on les a reçus | Fichiers `.dat` TPCx-BB, par lot (`initial`, `refresh`) | Écrit par l'ingestion (NiFi, ou Data Factory sur Azure). Lu par Spark | Gardé longtemps, jamais modifié : on peut tout refaire à partir de lui. Pour chaque fichier : taille, nombre de lignes, SHA-256, date du dépôt |
| `bronze` | Les mêmes données, rangées pour être lues | Copie de `raw` avec la date du chargement | Spark | Comme `raw` |
| `silver` | Données nettoyées et typées | Une table par dossier, en Parquet | Écrit par les traitements Silver. Lu par les traitements Gold et les analystes | Remplacé à chaque traitement. Chaque ligne garde son fichier d'origine, son lot et sa date de traitement |
| `gold` | Données prêtes pour le métier | Agrégats en Parquet (`ca_mensuel`, `ca_par_categorie`…) | Écrit par les traitements Gold. Lu par les analystes, les tableaux de bord et les notebooks UC-08 | Remplacé à chaque traitement. Colonnes de provenance et date de traitement |
| `quality` | Lignes mises à l'écart et rapports de contrôle | `rejets/<table>/` avec le motif du rejet, `rapport_qualite/` | Écrit par le nettoyage et les contrôles qualité. Lu par l'équipe Data | Gardé pour vérifier les rejets, puis vidé après un certain temps |
| `logs` | Journaux des traitements | Un journal par traitement et par exécution | Écrit par les traitements. Lu par l'équipe Data | Gardé quelques mois |

## 3. Règles de nommage

- **Compte de stockage** : `stretailintelligence`, sans tiret, car Azure n'accepte que des minuscules et des chiffres.
- **Conteneurs** : le nom de la zone, en minuscules (`raw`, `silver`…).
- **Dossiers** : un dossier par table.
  - En `raw` et en `silver`, on garde le nom TPCx-BB (`store_sales`), et en `raw` le lot apparaît dans le chemin (`initial`, `refresh`).
  - En `gold`, on utilise un nom métier en français, sous la forme `<indicateur>_par_<dimension>` ou `<indicateur>_<période>` (`ca_par_categorie`, `ca_mensuel`), comme au Jour 3.
- **Fichiers** : ceux de `raw` gardent leur nom d'origine. En `silver` et en `gold`, ce sont les fichiers `part-….snappy.parquet` écrits par Spark, avec `_SUCCESS`.

## 4. Rôle du Hierarchical Namespace (HNS)

**Sans HNS**, un compte de stockage Azure (Blob) est « plat » : il n'y a pas de vrais dossiers. Un fichier s'appelle simplement `silver/store_sales/part-0.parquet`, et les `/` font partie du nom. Les dossiers qu'on voit ne sont qu'un affichage.

**Avec HNS**, les dossiers existent vraiment, comme sur un disque ou dans HDFS.

| | Sans HNS (Blob classique) | Avec HNS (ADLS Gen2) |
|---|---|---|
| **Organisation** | Une longue liste de fichiers, les dossiers sont « simulés » | Une vraie arborescence de dossiers |
| **Renommer ou supprimer un dossier** | Il faut copier puis supprimer chaque fichier un par un : c'est lent, et si ça plante au milieu, il reste un dossier à moitié déplacé | Une seule opération, instantanée, qui marche en entier ou pas du tout |
| **Droits** | Seulement sur le compte ou le conteneur (RBAC) | En plus, des ACL sur chaque dossier et chaque fichier |
| **Usage adapté** | Stocker des images, des sauvegardes, des fichiers de site web | Les traitements analytiques (Spark, Synapse), le Data Lake |

**Pourquoi c'est important pour nous**

- **Spark** écrit d'abord ses fichiers dans un dossier temporaire, puis le **renomme** quand tout est fini (d'où le fichier `_SUCCESS` vu au Jour 3). Sans HNS, ce renommage est lent et peut laisser des fichiers à moitié écrits.
- **Les ACL** permettent par exemple de donner à un analyste la lecture de `gold/` sans lui ouvrir `raw/`.

En local, **HDFS est déjà hiérarchique** : le NameNode garde l'arbre des dossiers. Au Jour 2, on a déplacé `store_sales.dat` avec `hdfs dfs -mv` en une seule opération (`docs/architecture/architecture-data-lake.md`). C'est exactement ce que le HNS apporte à Azure.
