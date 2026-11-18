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
- **Ressources** : 2 cœurs (`nproc`), 3,8 Go de mémoire pour WSL (`free -h`), environ 930 Go de disque libre (`df -h`). À l'étape 5, je suis passé à 4 cœurs et 8 Go, parce que WSL manquait de mémoire (voir les erreurs rencontrées de l'étape 5).
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

### Étape 5 – Réaliser les transformations

> Commandes et résultats : `preuves/j3/spark/etape5_sorties_commandes.txt`. Notebook : `~/retail-intelligence/tp3/TP3_Nettoyage.ipynb` (cellules 6 à 9).

J'ai ajouté les transformations à la suite du nettoyage, dans le même notebook, parce qu'elles partent des données nettoyées (`ventes_propres`, `produits_propres`). Ensuite, j'ai exécuté tout le notebook d'un coup (`jupyter nbconvert --execute`) pour vérifier qu'il marche du début à la fin.

#### 1. La jointure ventes + produits

- **Les deux sources** : `ventes_propres` (issues de `store_sales`) et `produits_propres` (issus de `item`).
- **Les colonnes utilisées** : `ss_item_sk` dans les ventes et `i_item_sk` dans les produits.
- **Pourquoi cette relation est sûre** : je ne me suis pas basé sur des noms de colonnes qui se ressemblent. J'ai vérifié 3 choses :
  - le schéma TPCx-BB dit que `ss_item_sk` désigne le produit vendu ;
  - `i_item_sk` est unique dans `item` (17 820 valeurs pour 17 820 lignes) ;
  - toutes les valeurs de `ss_item_sk` existent dans `item` (0 vente avec un produit inconnu).
- **Nature de la relation et cardinalité attendue** : plusieurs ventes pour un même produit, et un seul produit par vente. On s'attend donc à garder exactement le même nombre de lignes.
- **Type de jointure** : `left`, pour garder toutes les ventes même si un produit manquait.
- **Nombre de lignes** : 667 579 avant, 667 579 après. Aucune ligne en plus, donc aucun produit n'est en double.
- **Ventes non rapprochées** : 0.
- **Colonnes ajoutées aux ventes** : `i_item_id`, `i_product_name`, `i_category`, `i_class`, `i_brand`.
- **Remarque** : les 17 820 produits ont tous été vendus au moins une fois.

#### 2. L'agrégation : chiffre d'affaires par catégorie

- **Question du Jour 1** : *« Quels produits et quelles catégories génèrent le plus de chiffre d'affaires ? »* (P4, Indispensable).
- **Granularité du résultat** : une ligne = une catégorie de produits, donc 9 lignes.
- **Règles de calcul** :
  - `chiffre_affaires` = somme de `ss_net_paid` (KPI-01 du Jour 1 : remises déduites, sans les taxes) ;
  - `quantite_vendue` = somme de `ss_quantity` (KPI-04) ;
  - `nombre_lignes_vente` = nombre de lignes de ticket ;
  - `nombre_produits_vendus` = nombre de produits différents ;
  - `part_ca_pct` = CA de la catégorie ÷ CA total × 100, arrondi à 2 chiffres.
- **Renommage** : `i_category` devient `categorie`, et les mesures ont des noms en français, pour que le résultat soit lisible par le métier.

Résultat :

| Catégorie | Chiffre d'affaires | Quantité vendue | Part du CA |
|---|---|---|---|
| Music | 519 666 693,84 | 15 238 374 | 45,17 % |
| Books | 307 151 503,25 | 9 007 511 | 26,70 % |
| Movies & TV | 74 735 891,89 | 2 189 279 | 6,50 % |
| Clothing & Accessories | 56 754 855,82 | 1 640 550 | 4,93 % |
| Electronics | 55 715 087,49 | 1 632 098 | 4,84 % |
| Home & Kitchen | 41 260 511,11 | 1 226 839 | 3,59 % |
| Sports & Outdoors | 40 926 938,33 | 1 209 305 | 3,56 % |
| Toys & Games | 27 437 825,33 | 809 999 | 2,38 % |
| Tools & Home Improvement | 26 880 279,31 | 801 519 | 2,34 % |

#### 3. Contrôle du résultat

- **CA total des ventes** : 1 150 529 586,37. **Somme des 9 catégories** : 1 150 529 586,37. C'est le même montant.
- **Lignes des ventes** : 667 579. **Somme des lignes des catégories** : 667 579. C'est le même nombre.

Aucune vente n'a été perdue ni comptée deux fois.

#### 4. Ce que je retiens

- `Music` et `Books` font à elles deux 72 % du chiffre d'affaires. Mais ce sont aussi les catégories qui ont le plus de produits (46 % et 30 % des produits, étape 3). Le CA suit donc surtout le nombre de produits, ce qui vient sûrement de la façon dont les données ont été générées.
- L'unité est supposée être l'euro, comme au Jour 1 : la devise n'est pas indiquée.

#### 5. Erreurs rencontrées

| Erreur | Cause | Correction |
|---|---|---|
| WSL ne répond plus (`Wsl/Service/0x8007274c`) | WSL n'avait droit qu'à 4 Go de mémoire, alors que HDFS, NiFi et plusieurs sessions Spark tournaient en même temps | Mémoire de WSL passée à 8 Go et 4 cœurs dans `C:\Users\Noah\.wslconfig`, puis `wsl --shutdown` et relance de HDFS (`start-dfs.sh`). NiFi n'est plus relancé, il ne sert pas au TP3. Je ferme aussi le notebook d'exploration quand je ne m'en sers plus |

### Étape 6 – Produire les données Silver

> Commandes et résultats : `preuves/j3/spark/etape6_sorties_commandes.txt`. Script : `scripts/01_silver.py`.

#### 1. Ce que fait le script

Pour que le traitement puisse être relancé, j'ai repris le nettoyage du notebook (étape 4) dans un script :

1. Il lit `store_sales` et `item` dans la zone `raw`, avec les schémas écrits à la main.
2. Il applique les règles de nettoyage de l'étape 4.
3. Il écrit les données propres dans `silver`, et les lignes mises à l'écart dans `quality/rejets`, avec leur motif.
4. Il relit ce qu'il vient d'écrire pour le contrôler.

#### 2. Organisation et convention de nommage

```
/retail-lake/
├── silver/
│   ├── store_sales/       Ventes nettoyées (Parquet)
│   └── item/              Produits nettoyés (Parquet)
└── quality/
    └── rejets/
        ├── store_sales/   Ventes mises à l'écart + motif_rejet
        └── item/          Produits mis à l'écart + motif_rejet
```

- **Un dossier par table**, avec le nom de la table TPCx-BB (`store_sales`, `item`). On retrouve tout de suite d'où viennent les données.
- **Les colonnes gardent les noms TPCx-BB** (`ss_…`, `i_…`), pour pouvoir les comparer avec la documentation du jeu de données. Les noms en français sont réservés au Gold, qui est fait pour le métier.
- **Format Parquet** : il garde les types (`decimal`, `date`) et prend peu de place (voir l'étape 8).
- Je n'ai créé que les 2 domaines traités, comme le demande le TP.

#### 3. Colonnes et provenance

- **Types explicites** : identifiants et quantité en `int`, montants en `decimal(7,2)`, dates en `date`.
- **Colonnes ajoutées** :
  - `prix_zero` (vrai / faux) : repère les ventes à prix 0 (étape 4) ;
  - `source_fichier` : le fichier `raw` d'où vient la ligne, par exemple `hdfs://localhost:9000/retail-lake/raw/tpcxbb/initial/item/item.dat` ;
  - `source_lot` : `initial` (premier envoi) ;
  - `date_traitement` : le jour et l'heure du traitement.
- **Colonne retirée** : `i_container` (toujours `Unknown`).

Avec ces colonnes, chaque ligne de Silver permet de retrouver sa source et le moment où elle a été traitée.

#### 4. Contrôles après écriture

- **Fichiers présents** : 4 fichiers `part-….snappy.parquet` par table, plus `_SUCCESS` qui veut dire que l'écriture est allée jusqu'au bout (`hdfs dfs -ls -R`).
- **Format et lisibilité** : les deux dossiers se relisent avec `spark.read.parquet`.
- **Nombre de lignes** :
  - `store_sales` : 667 579 en raw = 667 579 en silver + 0 mise à l'écart ;
  - `item` : 17 820 en raw = 17 820 en silver + 0 mise à l'écart.
- **Schéma** : mêmes colonnes et mêmes types qu'avant l'écriture (27 colonnes pour `store_sales`, 24 pour `item`).
- **Cohérence** : les 3 324 ventes à prix 0 sont bien repérées par `prix_zero`.
- **Taille** : 40,6 Mo pour `store_sales` (contre 88,5 Mo pour le fichier texte), 3,6 Mo pour `item`.
- **État de HDFS** : `HEALTHY`, 0 bloc sous-répliqué (`hdfs fsck /retail-lake`).

#### 5. Erreurs rencontrées

| Erreur | Cause | Correction |
|---|---|---|
| Les fichiers écrits par Spark ont 3 copies (`-rw-r--r--   3`) alors que HDFS n'a qu'un DataNode | PySpark installé avec `pip` ne lit pas `hdfs-site.xml`, il prend la valeur par défaut (3 copies) | J'ai mis `spark.hadoop.dfs.replication = 1` dans la session Spark (`commun.py`) et j'ai relancé. Les fichiers ont maintenant 1 copie |
| Le contrôle « schéma identique » répondait `False` | Après relecture, Spark marque toutes les colonnes comme pouvant être vides, ce qui n'était pas le cas de `source_lot` | Je compare seulement les noms et les types des colonnes : `True` |

### Étape 7 – Produire les données Gold

> Commandes et résultats : `preuves/j3/spark/etape7_sorties_commandes.txt`. Script : `scripts/02_gold.py`.

Le script lit les deux tables Silver, vérifie la clé, fait la jointure de l'étape 5, calcule les indicateurs et écrit le résultat dans `/retail-lake/gold/ca_par_categorie/` (Parquet), puis le relit.

#### 1. Fiche du jeu Gold

| Élément | Description |
|---|---|
| Nom | `ca_par_categorie` – Synthèse des ventes par catégorie |
| Finalité métier | Répondre à la question P4 du Jour 1 (Indispensable) : *« Quels produits et quelles catégories génèrent le plus de chiffre d'affaires ? »*, pour mettre en avant les catégories qui rapportent le plus |
| Sources | `silver/store_sales` et `silver/item`, reliées par `ss_item_sk` = `i_item_sk` (jointure vérifiée à l'étape 5) |
| Granularité | Une ligne = une catégorie de produits (9 lignes), sur toute la période des ventes |
| Dimension | `categorie` (venant de `i_category`) |
| Mesures | `chiffre_affaires`, `quantite_vendue`, `nombre_lignes_vente`, `nombre_produits_vendus`, `part_ca_pct` |
| Règles de calcul | `chiffre_affaires` = somme de `ss_net_paid` (KPI-01 : remises déduites, sans taxes). `quantite_vendue` = somme de `ss_quantity` (KPI-04). `nombre_lignes_vente` = nombre de lignes de ticket. `nombre_produits_vendus` = nombre de `ss_item_sk` différents. `part_ca_pct` = CA de la catégorie ÷ CA total × 100, arrondi à 2 chiffres |
| Colonnes de traçabilité | `source` (tables Silver utilisées), `date_traitement` |
| Usage | Analyse descriptive et graphiques du Jour 4 |
| Limites d'interprétation | Ventes en magasin seulement (pas le web). Pas de découpage par période (`date_dim` non chargée). Devise supposée en euros. Données inventées : le CA suit surtout le nombre de produits de chaque catégorie. Les retours (`store_returns`) ne sont pas déduits |

#### 2. Colonnes

- `categorie` : `string`
- `chiffre_affaires` : `decimal(17,2)`
- `quantite_vendue`, `nombre_lignes_vente`, `nombre_produits_vendus` : `bigint`
- `part_ca_pct` : `decimal(5,2)`
- `source` : `string`
- `date_traitement` : `timestamp`

#### 3. Résultat

- **Relecture** : 9 lignes, 8 colonnes.
- **Classement** : `Music` (45,17 %), puis `Books` (26,70 %), puis `Movies & TV` (6,50 %). Le détail est dans le tableau de l'étape 5.
- **Contrôle** : le CA total de Silver (1 150 529 586,37) est égal à la somme du Gold.

### Étape 8 – Utiliser le format Parquet

> Commandes et résultats : `preuves/j3/spark/etape8_sorties_commandes.txt`. Script : `scripts/03_formats.py`.

#### 1. Parquet produit et relu

- **Silver et Gold sont en Parquet** : `silver/store_sales`, `silver/item` et `gold/ca_par_categorie`.
- **Relecture** : elle fonctionne (`spark.read.parquet`) et le schéma est conservé, avec les montants toujours en `decimal(7,2)` et les dates en `date`.
- **Nombre de lignes** : identique avant et après l'écriture (étapes 6 et 7).
- **Valeurs** : exploitables, puisque le Gold est calculé directement à partir du Silver relu.
- **Répertoires** : bien identifiés, un dossier par table, avec des fichiers `part-….snappy.parquet` (`snappy` = compression).

#### 2. Comparaison des formats

J'ai écrit le même jeu (`silver/store_sales`, 667 579 lignes, 27 colonnes) en CSV, en JSON et en Parquet dans `outputs/comparaison_formats/`. Ensuite, j'ai relu chaque version **sans donner de schéma** et j'ai calculé le total de `ss_net_paid`.

| | CSV | JSON | Parquet |
|---|---|---|---|
| Organisation | Lignes de texte, valeurs séparées par des virgules | Un objet `{"colonne": valeur}` par ligne | Données rangées par colonne, compressées |
| Lisibilité | Lisible avec un éditeur de texte | Lisible, mais le nom des colonnes est répété sur chaque ligne | Pas lisible à l'œil, il faut un outil (Spark) |
| Taille observée | 175,5 Mo (189 % du fichier `.dat`) | 480,6 Mo (518 %) | **40,6 Mo (44 %)** |
| Types à la relecture | Tout est en `string` | Montants en `double`, dates en `string` | Types conservés : `decimal(7,2)`, `int`, `timestamp` |
| Total `ss_net_paid` | 1 150 529 586,37 | 1 150 529 586,37 | 1 150 529 586,37 |
| Temps pour ce total | 2,58 s | 2,66 s | **0,45 s** |
| Usages adaptés | Échanger avec un tableur ou un autre outil | Échanger avec une application web ou une API | Stocker et analyser de gros volumes (Silver, Gold) |
| Avantages | Simple, ouvert partout | Souple, peut contenir des données imbriquées | Petit, rapide, garde les types |
| Limites | Pas de types, gros fichiers | Encore plus gros, types approximatifs | Illisible sans outil, ne se modifie pas ligne par ligne |

Remarques :

- Le CSV est plus gros que le fichier `.dat` d'origine à cause des colonnes de provenance. Le chemin du fichier source (`source_fichier`, environ 90 caractères) est répété sur chacune des 667 579 lignes. Parquet range les valeurs par colonne et compresse les répétitions, donc elles ne prennent presque plus de place.
- Parquet est le plus rapide parce que Spark ne lit que la colonne `ss_net_paid`, alors qu'en CSV et en JSON il doit lire toutes les lignes en entier.
- Parquet seul n'est **pas** une table transactionnelle. Si une écriture plante au milieu, il n'y a pas de retour en arrière possible, et il n'y a pas d'historique des versions. Avec `overwrite`, l'ancienne version est perdue.

### Étape 9 – Mettre en œuvre les contrôles qualité

> Commandes et résultats : `preuves/j3/spark/etape9_sorties_commandes.txt`. Script : `scripts/04_qualite.py`.

#### 1. Comment j'ai fait

Le script fait 36 contrôles sur `silver/store_sales`, `silver/item` et `gold/ca_par_categorie`. Chaque contrôle a un statut :

- **OK** : la règle est respectée ;
- **KO** : la règle n'est pas respectée, il faut corriger ;
- **ATTENTION** : la règle est respectée, mais il reste une anomalie à connaître pour interpréter les chiffres.

Le rapport est enregistré dans `/retail-lake/quality/rapport_qualite/` (CSV), avec la date du contrôle.

#### 2. Les contrôles

| Contrôle | Règle | Résultat | Statut |
|---|---|---|---|
| Volume | Lignes raw = lignes silver + lignes mises à l'écart | `store_sales` : 667 579 = 667 579 + 0. `item` : 17 820 = 17 820 + 0 | OK |
| Volume | Gold : une ligne par catégorie | 9 lignes | OK |
| Complétude | `ss_item_sk`, `ss_ticket_number`, `ss_sold_date_sk`, `ss_store_sk`, `ss_quantity`, `ss_net_paid`, `i_item_sk`, `i_category`, `categorie` non nuls | 0 null partout | OK |
| Complétude | Colonnes non obligatoires | `ss_promo_sk` 0,02 %, `ss_addr_sk` 0,07 % de nulls | OK |
| Complétude | `i_size` (non obligatoire) | 14 % de nulls (anciens `N/A`/`Unknown`) | ATTENTION |
| Unicité | Aucune vente en double exact | 0 doublon | OK |
| Clé candidate | `i_item_sk` unique dans `item`, `categorie` unique dans le Gold | 17 820 pour 17 820, 9 pour 9 | OK |
| Validité | Montants en `decimal(7,2)`, identifiants et quantité en entier, `i_rec_start_date` en `date` | Types conformes | OK |
| Cohérence | `ss_quantity` > 0, `ss_net_paid` ≥ 0, prix de vente ≤ prix catalogue, montant = quantité × prix, `i_current_price` > 0, CA Gold ≥ 0 | 0 ligne hors règle | OK |
| Cohérence | 9 catégories dans `item` | 9 | OK |
| Cohérence | Somme du CA Gold = CA Silver, somme des lignes Gold = lignes Silver | 1 150 529 586,37 = 1 150 529 586,37 et 667 579 = 667 579 | OK |
| Cohérence | Somme des parts = 100 % (à 0,05 près) | 100,01 % (arrondis) | OK |
| Cohérence | Ventes à prix 0 | 3 324 lignes, gardées | ATTENTION |
| Cohérence | Ventes à marge négative | 495 971 lignes (74,3 %), gardées | ATTENTION |
| Cohérence | Coût d'achat > prix de vente | 7 768 produits (43,6 %), gardés | ATTENTION |
| Intégrité | Chaque `ss_item_sk` existe dans `silver/item` | 0 vente sans produit | OK |
| Intégrité | Chaque `ss_store_sk` existe dans `store.dat` (déposé par NiFi au Jour 2) | 0 vente sans magasin | OK |

#### 3. Bilan

- **Règles respectées** : 32 contrôles OK sur 36, aucun KO.
- **Anomalies restantes** (4 ATTENTION) : les ventes à prix 0, les marges négatives, les produits vendus à perte et les tailles manquantes. Je les ai gardées, parce qu'elles peuvent être de vrais cas et que le TP interdit de supprimer sans règle. Mais il faut les signaler à côté des indicateurs de marge.
- **Données mises à l'écart** : 0 vente et 0 produit pour ce lot.
- **Limites des contrôles** :
  - le contrôle de volume ne compte pas les doublons retirés (0 ici, mais il faudrait l'ajouter pour le lot `refresh`) ;
  - les dates des ventes ne sont pas contrôlées, car `date_dim` n'est pas chargée ;
  - les contrôles sont relancés à la main, ils ne bloquent pas automatiquement la chaîne en cas de KO.
- **Corrections possibles** : ajouter `date_dim` pour vérifier les dates, et arrêter la chaîne quand un contrôle est KO.

### Étape 10 – Organiser les traitements

> Commandes et résultats : `preuves/j3/spark/etape10_sorties_commandes.txt` (arborescence, exécution complète et copie des scripts).
> Copie du code dans le dépôt : `preuves/j3/code/` (scripts, notebooks, README et journaux). Le dossier de travail reste `~/retail-intelligence/tp3/` dans WSL.

#### 1. Organisation

```
~/retail-intelligence/tp3/
├── README.md                         Procédure de reproduction
├── TP3_Retail_Intelligence.ipynb     Exploration (étapes 1 à 3)
├── TP3_Nettoyage.ipynb               Mise au point du nettoyage et des transformations (étapes 4 et 5)
├── scripts/
│   ├── config.py                     Paramètres : chemins d'entrée et de sortie, lot, mémoire
│   ├── commun.py                     Session Spark, schémas, fonction de lecture, journal
│   ├── 01_silver.py                  raw -> silver (+ rejets)
│   ├── 02_gold.py                    silver -> gold
│   ├── 03_formats.py                 Comparaison CSV / JSON / Parquet
│   ├── 04_qualite.py                 Contrôles qualité
│   └── lancer_tout.sh                Lance les 4 scripts dans l'ordre
├── logs/                             Un journal par script
└── outputs/comparaison_formats/      Sorties de test (CSV, JSON, Parquet)
```

Ce qui est séparé, comme demandé :

- **Paramètres et chemins** : tout est dans `config.py`. Pour traiter le lot `refresh`, il suffit de changer `LOT`.
- **Fonctions de lecture** : `lire_source_raw` dans `commun.py`, utilisée pour les deux sources.
- **Transformations** : `01_silver.py` (nettoyage) et `02_gold.py` (jointure et agrégation).
- **Contrôles qualité** : `04_qualite.py`.
- **Écritures** : à la fin de chaque script, dans un dossier réservé.
- **Journaux** : chaque script écrit ce qu'il fait dans `logs/<script>.log`.

#### 2. Ordre d'exécution

1. `01_silver.py` d'abord, parce que les autres scripts lisent `silver`.
2. `02_gold.py` ensuite, parce qu'il a besoin de `silver`.
3. `03_formats.py`, qui a besoin de `silver/store_sales`.
4. `04_qualite.py` en dernier, parce qu'il contrôle `silver`, `gold` et les rejets.

J'ai relancé toute la chaîne avec `./lancer_tout.sh` : les 4 scripts sont passés, en environ 3 minutes, et donnent les mêmes résultats. Le traitement est donc reproductible.

## Reproduire les traitements (README)

Le README complet est dans `~/retail-intelligence/tp3/README.md`, avec une copie dans le dépôt : `preuves/j3/code/README.md`.

### Prérequis

- Ubuntu 24.04 dans WSL, avec 8 Go de mémoire et 4 cœurs (`C:\Users\Noah\.wslconfig`).
- Hadoop 3.5.0 (`/opt/hadoop`), HDFS démarré.
- Environnement Python `~/retail-intelligence/tp3/.venv` avec `pyspark` et `jupyterlab`.

### Versions

- Python 3.12.3
- Spark / PySpark 4.3.0, en mode `local[*]`
- JupyterLab 4.6.6
- Java 21 pour Spark, Java 17 pour Hadoop

### Emplacement des données

- **Entrée** (zone `raw`, jamais modifiée) :
  - `/retail-lake/raw/tpcxbb/initial/store_sales/store_sales.dat`
  - `/retail-lake/raw/tpcxbb/initial/item/item.dat`
  - `/retail-lake/raw/nifi/store.dat` (pour le contrôle des magasins)
- **Sorties** :
  - `/retail-lake/silver/{store_sales,item}/`
  - `/retail-lake/gold/ca_par_categorie/`
  - `/retail-lake/quality/rejets/{store_sales,item}/`
  - `/retail-lake/quality/rapport_qualite/`

### Paramètres

Dans `scripts/config.py` : l'adresse HDFS, le lot (`initial` ou `refresh`), les chemins, la mémoire Spark (2 Go) et le nombre de copies HDFS (1).

### Lancement

```bash
start-dfs.sh
cd ~/retail-intelligence/tp3/scripts
./lancer_tout.sh
```

### Sorties produites

- `silver/store_sales` : 667 579 lignes ;
- `silver/item` : 17 820 lignes ;
- `gold/ca_par_categorie` : 9 lignes ;
- 0 ligne mise à l'écart ;
- un rapport qualité de 36 contrôles ;
- un journal par script dans `logs/`.

### Contrôles disponibles

`04_qualite.py` vérifie les volumes, la complétude, l'unicité, les types, la cohérence et l'intégrité. Dernier résultat : 32 OK, 4 ATTENTION, 0 KO.

### Limites connues

- Les données sont inventées : la marge n'est pas réaliste.
- Pas de dates réelles pour les ventes, car `date_dim` n'est pas chargée.
- Seul le lot `initial` a été traité.
- `overwrite` remplace le résultat précédent, sans historique.
- Une seule machine, avec 1 copie des données.

## Questions de recul

### 1. Pourquoi est-il nécessaire de vérifier les schémas avant de commencer les transformations ?

Parce que les calculs dépendent des types. Si on ne vérifie pas, on peut additionner du texte, faire des arrondis faux sur de l'argent (`double` au lieu de `decimal`) ou prendre un identifiant pour un nombre. Dans notre cas, `inferSchema` avait mis les montants en `double` et `i_rec_end_date` en `string` : il a fallu écrire le schéma à la main.

### 2. Quelle différence existe entre une donnée brute, une donnée Silver et une donnée Gold ?

- **Brute** (`raw`) : le fichier tel qu'on l'a reçu, sans titres ni types, qu'on ne modifie jamais.
- **Silver** : les mêmes données nettoyées, avec les bons types, des règles appliquées et la provenance. Une ligne de vente reste une ligne de vente.
- **Gold** : des données regroupées pour répondre à une question du métier, par exemple le CA par catégorie (9 lignes au lieu de 667 579).

### 3. Pourquoi faut-il connaître la granularité d'une table avant de réaliser une agrégation ?

Pour savoir ce qu'on compte. Une ligne de `store_sales` est une ligne de ticket, pas un ticket : compter les lignes ne donne donc pas le nombre de tickets. Et si on joint une table à la mauvaise granularité, des lignes peuvent être dupliquées et les sommes deviennent fausses.

### 4. Quels risques présente une jointure réalisée sur une clé supposée ?

- Des lignes **en double** si la clé n'est pas unique de l'autre côté : le CA serait alors compté plusieurs fois.
- Des lignes **perdues ou sans correspondance** si les valeurs ne correspondent pas.
- Un **résultat faux sans message d'erreur**.

C'est pour ça que j'ai vérifié que `i_item_sk` était unique et que toutes les ventes trouvaient leur produit, puis comparé le nombre de lignes avant et après la jointure (667 579 des deux côtés).

### 5. Pourquoi ne faut-il pas supprimer automatiquement les valeurs atypiques ?

Parce qu'une valeur bizarre peut être un vrai cas : un produit offert (prix 0), une vente à perte (marge négative), une promotion. Les supprimer fausserait les résultats et ferait disparaître une information. Il faut d'abord comprendre ce qu'elles veulent dire. En attendant, je les garde et je les repère (`prix_zero`, statut ATTENTION).

### 6. Quels contrôles permettent de vérifier la cohérence d'un jeu de données transformé ?

- Comparer les **volumes** : lignes en entrée = lignes gardées + lignes mises à l'écart.
- Vérifier que les **totaux** ne changent pas : CA Silver = somme du CA Gold.
- Vérifier les **règles métier** : quantité > 0, montant = quantité × prix.
- Vérifier les **clés** : unicité, aucun null, chaque vente a un produit connu.
- **Relire** les fichiers écrits et vérifier leur schéma.

### 7. Pourquoi Parquet est-il adapté aux usages analytiques ?

Les données sont rangées par colonne et compressées. Pour une analyse, on lit souvent quelques colonnes sur beaucoup de lignes : Spark ne lit que celles dont il a besoin. Dans notre test, Parquet prend 40,6 Mo contre 175,5 Mo en CSV, et calcule le total en 0,45 s contre 2,58 s. En plus, il garde les types.

### 8. Pourquoi Parquet seul ne fournit-il pas les garanties d'une table transactionnelle Lakehouse ?

Un dossier Parquet n'est qu'un ensemble de fichiers :
- si une écriture plante au milieu, il peut rester des fichiers à moitié écrits, sans retour en arrière ;
- deux écritures en même temps peuvent se mélanger ;
- il n'y a pas d'historique : avec `overwrite`, l'ancienne version est perdue ;
- on ne peut pas modifier ou supprimer une seule ligne.

Des formats comme Delta Lake ou Apache Iceberg ajoutent un journal des modifications au-dessus des fichiers Parquet pour apporter ces garanties.

### 9. Dans quels cas une base NoSQL pourrait-elle compléter une architecture Data Lake ?

Quand on a besoin de lire ou d'écrire **une seule information très vite**, par exemple afficher l'historique d'achats d'un client sur le site, ou le stock d'un produit en temps réel. Le Data Lake est fait pour analyser beaucoup de données d'un coup, pas pour répondre en quelques millisecondes à une question sur une seule ligne. Une base comme HBase peut stocker ce genre de données, avec une clé bien choisie.

### 10. Quelles limites des données TPCx-BB doivent être prises en compte lors de l'interprétation des résultats ?

- Les données sont **inventées** (générées au hasard) : 74 % des ventes ont une marge négative et 44 % des produits coûtent plus cher à l'achat qu'à la vente, ce qui n'arrive pas dans un vrai magasin.
- Les noms de produits et de marques sont des suites de lettres au hasard.
- La répartition des catégories est très déséquilibrée (`Music` = 46 % des produits), et c'est ce qui fait sa part de CA.
- La devise n'est pas indiquée.
- Ce n'est pas un benchmark officiel : on ne peut tirer aucune conclusion sur les performances.

Les résultats servent à montrer que la chaîne fonctionne, pas à prendre de vraies décisions commerciales.
