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
| Granularité | Une ligne = une ligne de ticket de caisse (un produit, avec sa quantité et sa promotion). Le même produit peut apparaître plusieurs fois dans un ticket | Une ligne = un produit |
| Anomalies identifiées | 4 136 lignes ont le même couple (ticket, produit) qu'une autre ligne. Valeurs nulles dans 4 colonnes (`ss_cdemo_sk` 238, `ss_hdemo_sk` 295, `ss_addr_sk` 448, `ss_promo_sk` 158). Marges négatives (`ss_net_profit` = -856,98) | `i_rec_end_date` toujours vide (17 820 nulls). Quelques nulls : `i_item_desc` 4, `i_brand_id` 8, `i_brand` 6. Les noms de produits et de marques sont des suites de lettres au hasard (données inventées) |

#### 3. Questions techniques

1. **Structurés, semi-structurés ou non structurés ?** Structurés : ce sont des tableaux avec le même nombre de colonnes sur chaque ligne et un séparateur fixe (`|`).
2. **Les colonnes sont-elles bien typées ?** Pas toutes. Spark a deviné les types tout seul (`inferSchema`), mais :
   - les montants sont en `double` alors que le schéma TPCx-BB prévoit `decimal(7,2)`. Un `double` peut donner des arrondis faux sur de l'argent ;
   - `i_rec_end_date` est en `string` parce qu'elle est toujours vide, alors que c'est une date ;
   - `ss_sold_date_sk` est un nombre, mais ce n'est pas une date : c'est l'identifiant d'un jour dans la table `date_dim`.
3. **Des colonnes contiennent-elles des valeurs nulles ?** Oui, voir le tableau. Les colonnes importantes pour notre question (`ss_item_sk`, `ss_ticket_number`, `ss_net_paid`, `i_item_sk`, `i_category`) n'ont pas de valeur nulle.
4. **Les identifiants sont-ils uniques quand c'est attendu ?** Dans `item`, oui : `i_item_sk` est unique. Dans `store_sales`, le couple (ticket, produit) devrait être unique, mais 4 136 lignes se répètent. Je regarderai à l'étape 3 si ce sont de vrais doublons ou le même produit passé deux fois en caisse.
5. **La granularité est-elle connue ?** Oui : une ligne de ticket pour `store_sales`, un produit pour `item`.
6. **Les données sont-elles adaptées aux questions du Jour 1 ?** Oui pour le chiffre d'affaires par produit et par catégorie (`ss_net_paid` + `i_category`), et aussi pour la marge par catégorie (`ss_net_profit`). En revanche, pour suivre les ventes par mois, il faudrait ajouter `date_dim`, car `ss_sold_date_sk` n'est pas une vraie date.

### Étape 3 – Explorer les données avec PySpark

> Commandes et résultats : `preuves/j3/spark/etape3_sorties_commandes.txt`. Notebook : `~/retail-intelligence/tp3/TP3_Retail_Intelligence.ipynb`.

Le chargement, le schéma, l'échantillon, le comptage et les valeurs nulles sont déjà faits à l'étape 2. Ici, j'ai ajouté l'examen des colonnes, la recherche des doublons et celle des valeurs atypiques. À cette étape, je note seulement ce que je vois. Ce qu'on en fait sera décidé à l'étape 4.

#### 1. Examen des colonnes (minimum et maximum)

- **`store_sales`** :
  - `ss_quantity` va de 1 à 100. Pas de quantité nulle ou négative.
  - `ss_store_sk` va de 0 à 11, donc 12 magasins. C'est le nombre de lignes de `store.dat` déposé par NiFi au Jour 2.
  - `ss_item_sk` va de 0 à 17 819, comme `i_item_sk` dans `item`.
  - `ss_sold_date_sk` va de 36 890 à 38 697, soit environ 1 800 jours, autour de 5 ans. Ce sont des numéros de jour, pas des dates.
  - `ss_sold_time_sk` va de 0 à 86 399, c'est-à-dire le nombre de secondes dans une journée.
- **`item`** : `i_current_price` va de 0,10 à 99,98 et `i_category_id` de 1 à 9 (9 catégories).

#### 2. Doublons

- **Doublons exacts** (toutes les colonnes identiques) : **0** dans les deux sources (`dropDuplicates()`).
- **Couples (ticket, produit) répétés** dans `store_sales` : 4 038 couples apparaissent 2, 3 ou 4 fois, ce qui fait les 4 136 lignes en trop vues à l'étape 2.
  - Exemple : le ticket 1598 contient deux fois le produit 10003, mais avec une quantité, un prix et une promotion (`ss_promo_sk`) différents.
  - Ce ne sont donc **pas des doublons** : c'est le même produit passé deux fois en caisse, avec deux promotions différentes. Ça confirme qu'une ligne de `store_sales` est une ligne de ticket.

#### 3. Valeurs atypiques ou incohérentes

- **`store_sales`** :
  - **Quantité ≤ 0** : 0.
  - **Prix de vente = 0** : 3 324 lignes.
  - **Prix de vente plus grand que le prix catalogue** : 0.
  - **Montant payé négatif** : 0.
  - **Marge négative** (`ss_net_profit` < 0) : 495 971 lignes, soit 74 %.
  - **Montant différent de quantité × prix** : 0, les calculs sont cohérents.
- **`item`** :
  - **Prix ≤ 0** : 0.
  - **Coût d'achat plus grand que le prix de vente** : 7 768 produits, soit 44 %.
  - **Valeurs `Unknown`, `N/A` ou `NO_SUB_CAT`** : `i_container` 17 820 (toujours `Unknown`), `i_size` 2 502, `i_units` 1 767, `i_class` 1 576.
  - **Répartition des catégories** : très déséquilibrée. `Music` a 8 143 produits (46 %), `Toys & Games` seulement 405.

#### 4. Questions techniques

1. **Colonnes numériques** : la quantité (`ss_quantity`), les prix et les montants (`ss_sales_price`, `ss_net_paid`, `ss_net_profit`, `i_current_price`…). Les colonnes `_sk` sont aussi des nombres, mais ce sont des identifiants : faire une somme ou une moyenne dessus n'a pas de sens.
2. **Colonnes de dates** : `i_rec_start_date` (date) et `i_rec_end_date` (toujours vide). `ss_sold_date_sk` et `ss_sold_time_sk` ne sont pas des dates : ce sont des numéros de jour et de seconde, à relier à `date_dim` et `time_dim`.
3. **Colonnes identifiants** : toutes les colonnes `_sk` (`ss_item_sk`, `ss_store_sk`, `i_item_sk`…), plus `i_item_id` et `ss_ticket_number`.
4. **Valeurs manquantes** : les nulls de l'étape 2, plus des valeurs « vides déguisées » qui ne sont pas `NULL` mais ne donnent aucune information (`Unknown`, `N/A`, `NO_SUB_CAT`). `i_container` vaut `Unknown` sur toutes les lignes.
5. **Doublons** : aucun doublon exact. Les 4 136 lignes qui répètent un couple (ticket, produit) sont de vraies ventes différentes (promotion différente).
6. **Valeurs incohérentes** :
   - 3 324 ventes ont un prix de 0 (produit offert ? erreur ?) ;
   - 74 % des ventes ont une marge négative ;
   - 44 % des produits coûtent plus cher à l'achat qu'à la vente.

   Dans un vrai magasin, ce serait anormal. Ici, ça vient sûrement du fait que les données TPCx-BB sont générées au hasard. Il faudra en tenir compte pour interpréter la marge.

### Étape 4 – Définir les règles de nettoyage

> Commandes et résultats : `preuves/j3/spark/etape4_sorties_commandes.txt`. Notebook : `~/retail-intelligence/tp3/TP3_Nettoyage.ipynb`.

#### 1. Les règles

| Anomalie | Règle | Action appliquée | Justification |
|---|---|---|---|
| Type incorrect | Lire avec un schéma écrit à la main, sans `inferSchema`. Montants en `decimal(7,2)`, dates en `date`. Une ligne qui ne se convertit pas arrive dans la colonne `_corrupt_record`. | Ligne mise à l'écart (« type incorrect ») | `inferSchema` devine les types mais ne les vérifie pas. Un `double` peut donner des arrondis faux sur de l'argent. |
| Valeur manquante (colonne obligatoire) | `ss_item_sk`, `ss_ticket_number`, `ss_sold_date_sk`, `ss_store_sk`, `i_item_sk` et `i_category` ne doivent pas être nuls. | Ligne mise à l'écart (« identifiant manquant », « catégorie manquante ») | Sans ces colonnes, on ne peut pas rattacher une vente à un produit, un ticket, un jour, un magasin ou une catégorie. |
| Valeur manquante (colonne non obligatoire) | Nulls de `ss_cdemo_sk`, `ss_hdemo_sk`, `ss_addr_sk`, `ss_promo_sk`, `i_brand`, `i_item_desc`. | Gardés à `NULL`, pas remplacés par 0 | Une vente sans promotion est normale. `0` est un vrai identifiant (`ss_promo_sk` commence à 0), donc remplacer un null par 0 inventerait une information. |
| Valeur manquante déguisée | `N/A` et `Unknown` dans `i_size` et `i_units`. `i_container` vaut `Unknown` sur toutes les lignes. | Remplacés par `NULL`. Colonne `i_container` retirée. `NO_SUB_CAT` gardé | Toutes les valeurs manquantes s'écrivent alors de la même façon et sont comptées comme manquantes. `i_container` n'apporte aucune information. `NO_SUB_CAT` veut dire « pas de sous-catégorie », c'est une vraie valeur. |
| Format du texte | Espaces au début et à la fin des colonnes texte. | Retirés (`trim`) | Évite que `"Books"` et `"Books "` soient comptés comme deux catégories. |
| Doublon | Lignes identiques sur toutes les colonnes. | Supprimées (`dropDuplicates`) | C'est le seul cas où on est sûr que c'est un doublon. Les couples (ticket, produit) répétés sont gardés, ce sont de vraies ventes (étape 3). |
| Identifiant invalide | `i_item_sk` doit être unique. Chaque `ss_item_sk` doit exister dans `item`. | Ligne mise à l'écart (« identifiant en double », « produit inconnu ») | Une vente d'un produit inconnu ne peut pas être rangée dans une catégorie. |
| Date incohérente | `i_rec_end_date` vide = produit toujours en vente. `ss_sold_date_sk` est gardé tel quel. | `i_rec_end_date` convertie en `date` (reste `NULL`) | On ne peut pas vérifier les vraies dates des ventes sans `date_dim`, que nous n'avons pas chargée. |
| Valeur atypique impossible | Quantité ≤ 0, prix de vente ou montant payé négatif. | Ligne mise à l'écart (« quantité <= 0 », « montant négatif ») | Une vente ne peut pas avoir une quantité nulle ou un montant payé négatif. Les retours sont dans une autre table (`store_returns`). |
| Valeur atypique possible | Prix de vente = 0 (3 324 lignes), marge négative (74 %), coût d'achat > prix (44 %). | Gardées. Les ventes à prix 0 sont repérées avec une nouvelle colonne `prix_zero` (vrai / faux) | Une valeur négative n'est pas forcément une erreur. Un prix à 0 peut être un produit offert. Je ne supprime pas une valeur sans savoir ce qu'elle veut dire. |

Une ligne mise à l'écart n'est pas supprimée : elle part dans un tableau à part (`ventes_rejetees`, `produits_rejetes`) avec la raison (`motif_rejet`), pour pouvoir la vérifier.

#### 2. Mise en œuvre

J'ai mis le nettoyage dans un notebook à part (`TP3_Nettoyage.ipynb`), séparé de l'exploration, comme le demande le TP :

1. Session Spark et schémas des deux sources.
2. Lecture depuis la zone `raw` de HDFS avec les schémas.
3. Règles sur les produits.
4. Règles sur les ventes (en utilisant les produits nettoyés pour vérifier `ss_item_sk`).
5. Bilan : nombre de lignes avant et après, et lignes mises à l'écart par raison.

#### 3. Résultats

- **Lecture** : 667 579 ventes et 17 820 produits. Aucune ligne mal convertie. Aucun caractère de fin de ligne Windows (`\r`) n'est resté dans la dernière colonne.
- **Mises à l'écart** : 0 vente et 0 produit. C'était attendu, puisque l'exploration n'avait trouvé ni identifiant manquant, ni quantité ≤ 0, ni montant négatif. Les règles restent utiles pour les prochains chargements (dossier `refresh`).
- **Doublons exacts** : 0 supprimé.
- **Ventes à prix 0** : 3 324, gardées et repérées par `prix_zero`.
- **Vides déguisés** : 2 502 `i_size` et 1 767 `i_units` sont maintenant à `NULL`.
- **Types** : les montants sont passés de `double` à `decimal(7,2)`, `i_rec_end_date` de `string` à `date`. `i_container` a été retirée.

Les données nettoyées restent pour l'instant en mémoire. Elles seront écrites dans `silver` à l'étape 6.
