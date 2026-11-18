# Contribution Noah – Jour 3

## UC6

### Étape 1 – Préparer l'environnement

> Commandes et résultats : `preuves/j3/spark/etape1_sorties_commandes.txt`.

#### 1. Installation

J'ai tout installé dans WSL (Ubuntu), pas dans Windows, parce que HDFS tourne déjà dans WSL depuis le Jour 2.

```bash
sudo apt install -y python3-venv python3-pip
mkdir -p ~/retail-intelligence/tp3
cd ~/retail-intelligence/tp3
python3 -m venv .venv
source .venv/bin/activate
pip install pyspark jupyterlab
```

L'environnement virtuel (`.venv`) garde PySpark et Jupyter à part, sans toucher au Python du système.

#### 2. Ce que j'ai relevé

- **Système** : Ubuntu 24.04 dans WSL (Windows 11).
- **Python** : 3.12.3 (`python --version`).
- **Spark / PySpark** : 4.3.0, avec Java 21 (`pyspark --version`).
- **JupyterLab** : 4.6.6 (`jupyter lab --version`).
- **Mode d'exécution** : `local[*]` (`spark.sparkContext.master`), c'est-à-dire que Spark tourne sur ma machine seule et utilise tous les cœurs disponibles (pas de cluster).
- **Ressources** : 2 cœurs (`nproc`), 3,8 Go de mémoire pour WSL (`free -h`), environ 930 Go de disque libre (`df -h`).
- **HDFS** : démarré, `NameNode` et `DataNode` sont visibles (`jps`).

#### 3. Les chemins

- **Espace de travail du TP** : `~/retail-intelligence/tp3` (notebook, scripts, `.venv`).
- **Données d'entrée** : dans HDFS, zone `raw` du Data Lake du Jour 2 :
  - `/retail-lake/raw/tpcxbb/initial/store_sales/store_sales.dat` (déposé au Jour 2) ;
  - `/retail-lake/raw/tpcxbb/initial/item/item.dat` (déposé pour ce TP, 17 820 lignes, même taille et même nombre de lignes que le fichier local).
- **Sorties de test** : `~/retail-intelligence/tp3/outputs/`, un dossier à part pour ne pas toucher aux données sources.
- **Sorties du TP** : les zones `silver` et `gold` de HDFS (`/retail-lake/silver`, `/retail-lake/gold`).

#### 4. Les vérifications

Dans le notebook `TP3_Retail_Intelligence.ipynb` :

1. **Lancer un notebook** : JupyterLab s'ouvre dans le navigateur Windows.
2. **Créer une session Spark** : Spark 4.3.0, mode `local[*]`, 2 cœurs.
3. **Lire un fichier de test** : `item.dat` lu depuis HDFS, 17 820 lignes, 22 colonnes.
4. **Afficher un schéma** : `printSchema()` donne les colonnes `_c0` à `_c21` avec leur type (`integer`, `string`, `date`, `double`). Les noms `_c0`, `_c1`… viennent du fait que le fichier n'a pas de ligne d'en-tête.
5. **Écrire un résultat de test** : 10 lignes écrites dans `outputs/test_ecriture/`, puis relues (10 lignes).

#### 5. Erreurs rencontrées

| Erreur | Cause | Correction |
|---|---|---|
| Spark ne trouve pas mon fichier local (`Path does not exist: hdfs://localhost:9000/mnt/c/...`) | Hadoop est configuré sur la machine, donc un chemin sans préfixe est cherché dans HDFS | J'ai ajouté `file:///` devant le chemin |
| `hdfs dfs -put` ne trouve pas le fichier local (`No such file or directory`) | Même cause : sans préfixe, `hdfs` ne retrouve pas le chemin local | J'ai ajouté `file:///` devant le chemin |

Depuis, j'écris toujours le préfixe : `file:///` pour un fichier sur le disque, `hdfs:///` pour un fichier dans HDFS. Comme ça, on sait clairement d'où vient chaque donnée.

### Étape 2 – Inventorier les sources disponibles

> Commandes et résultats : `preuves/j3/spark/etape2_sorties_commandes.txt`.

#### 1. Sources choisies

- **`store_sales`** (les ventes en magasin) et **`item`** (les produits).
- Elles sont déjà dans HDFS, dans la zone `raw` du Data Lake du Jour 2.
- Elles répondent à une question **Indispensable** du Jour 1 : *« Quels produits et quelles catégories génèrent le plus de chiffre d'affaires ? »*.
- Elles ont une colonne qui pourrait les relier (`ss_item_sk` dans les ventes, `i_item_sk` dans les produits). Il faudra le vérifier avant de faire une jointure.

Les fichiers n'ont pas de ligne de titres. J'ai donc donné aux colonnes les noms du schéma TPCx-BB relevé au Jour 1 (`01_UC01_besoin_exploration/preuves/tpcxbb_schema.json`). Spark lit bien 23 et 22 colonnes, comme attendu.

#### 2. Inventaire technique

| Information | Source 1 : `store_sales` | Source 2 : `item` |
|---|---|---|
| Nom réel du fichier | `store_sales.dat` | `item.dat` |
| Emplacement | `hdfs:///retail-lake/raw/tpcxbb/initial/store_sales/` | `hdfs:///retail-lake/raw/tpcxbb/initial/item/` |
| Format | Texte, colonnes séparées par `\|`, pas de ligne de titres, encodage ASCII, fins de ligne Windows (CRLF) | Pareil |
| Taille | 92 764 700 octets (88,5 Mo) | 6 799 286 octets (6,5 Mo) |
| Nombre de lignes | 667 579 | 17 820 |
| Nombre de colonnes | 23 | 22 |
| Colonnes principales | `ss_sold_date_sk` (jour de la vente), `ss_item_sk` (produit), `ss_store_sk` (magasin), `ss_ticket_number` (ticket), `ss_quantity`, `ss_sales_price`, `ss_net_paid` (montant payé), `ss_net_profit` (marge) | `i_item_sk` (identifiant), `i_item_id`, `i_product_name`, `i_category`, `i_class`, `i_brand`, `i_current_price` |
| Types observés | Identifiants et quantité : `integer`. Montants : `double` | Identifiants : `integer`. Textes : `string`. `i_rec_start_date` : `date`. `i_rec_end_date` : `string`. Prix : `double` |
| Clé candidate | Aucune colonne seule. Le couple (`ss_ticket_number`, `ss_item_sk`) n'est pas unique non plus (voir anomalies) | `i_item_sk` (17 820 valeurs différentes pour 17 820 lignes). `i_item_id` est aussi unique |
| Granularité | Une ligne = un produit acheté dans un ticket de caisse | Une ligne = un produit |
| Anomalies identifiées | 4 136 lignes ont le même couple (ticket, produit) qu'une autre ligne. Valeurs nulles dans 4 colonnes (`ss_cdemo_sk` 238, `ss_hdemo_sk` 295, `ss_addr_sk` 448, `ss_promo_sk` 158). Marges négatives (`ss_net_profit` = -856,98) | `i_rec_end_date` toujours vide (17 820 nulls). Quelques nulls : `i_item_desc` 4, `i_brand_id` 8, `i_brand` 6. Les noms de produits et de marques sont des suites de lettres au hasard (données inventées) |

#### 3. Questions techniques

1. **Structurés, semi-structurés ou non structurés ?** Structurés : ce sont des tableaux avec le même nombre de colonnes sur chaque ligne et un séparateur fixe (`|`).
2. **Les colonnes sont-elles bien typées ?** Pas toutes. Spark a deviné les types tout seul (`inferSchema`), mais :
   - les montants sont en `double` alors que le schéma TPCx-BB prévoit `decimal(7,2)`. Un `double` peut donner des arrondis faux sur de l'argent ;
   - `i_rec_end_date` est en `string` parce qu'elle est toujours vide, alors que c'est une date ;
   - `ss_sold_date_sk` est un nombre, mais ce n'est pas une date : c'est l'identifiant d'un jour dans la table `date_dim`.
3. **Des colonnes contiennent-elles des valeurs nulles ?** Oui, voir le tableau. Les colonnes importantes pour notre question (`ss_item_sk`, `ss_ticket_number`, `ss_net_paid`, `i_item_sk`, `i_category`) n'ont pas de valeur nulle.
4. **Les identifiants sont-ils uniques quand c'est attendu ?** Dans `item`, oui : `i_item_sk` est unique. Dans `store_sales`, le couple (ticket, produit) devrait être unique, mais 4 136 lignes se répètent. Je regarderai à l'étape 3 si ce sont de vrais doublons ou le même produit passé deux fois en caisse.
5. **La granularité est-elle connue ?** Oui : un produit dans un ticket pour `store_sales`, un produit pour `item`.
6. **Les données sont-elles adaptées aux questions du Jour 1 ?** Oui pour le chiffre d'affaires par produit et par catégorie (`ss_net_paid` + `i_category`), et aussi pour la marge par catégorie (`ss_net_profit`). En revanche, pour suivre les ventes par mois, il faudrait ajouter `date_dim`, car `ss_sold_date_sk` n'est pas une vraie date.
