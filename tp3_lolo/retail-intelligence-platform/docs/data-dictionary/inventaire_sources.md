# Inventaire technique des sources retenues - TP Jour 3, Étape 2

Date du relevé : 18/11/2026

Script : `transformations/exploration/inventaire_sources.ipynb`

Résultats bruts : `outputs/inventaire_sources.json`

## Sources retenues et pourquoi

Les sources viennent du jeu TPCx-BB inventorié au Jour 1
(`01_UC01_besoin_exploration/preuves/inventaire_fichiers.csv`) et déposé dans
HDFS au Jour 2 (`store_sales` en dépôt manuel, `store` via NiFi).

| Source | Domaine | Questions métier du Jour 1 couvertes |
|---|---|---|
| `store_sales` | Ventes en magasin | CA mensuel, marge, niveau des remises |
| `item` | Produits | CA et marge par produit / catégorie (P2, P4) |
| `store` | Magasins | Marge par magasin (P2) |

`store_sales` est la table de faits. `item` et `store` sont les dimensions
qui permettent de l'analyser par produit et par magasin.

## Tableau d'inventaire

| Information | Source 1 : `store_sales` | Source 2 : `item` | Source 3 : `store` |
|---|---|---|---|
| Nom réel du fichier | `store_sales.dat` | `item.dat` | `store.dat` |
| Emplacement | `~/DEV/tpcxbb_source/retail_project/data/store_sales/` (HDFS : `/retail-lake/raw/tpcxbb/initial/store_sales/`) | `~/DEV/tpcxbb_source/retail_project/data/item/` | `~/DEV/tpcxbb_source/retail_project/data/store/` (HDFS : `/retail-lake/raw/nifi/`) |
| Format | Texte délimité par `\|`, sans en-tête | Texte délimité par `\|`, sans en-tête | Texte délimité par `\|`, sans en-tête |
| Taille | 92 764 700 octets (88,5 Mo) | 6 799 286 octets (6,5 Mo) | 3 386 octets |
| Nombre de lignes | 667 579 | 17 820 | 12 |
| Nombre de colonnes | 23 | 22 | 29 |
| Colonnes principales | `ss_sold_date_sk`, `ss_item_sk`, `ss_store_sk`, `ss_ticket_number`, `ss_quantity`, `ss_sales_price`, `ss_ext_sales_price`, `ss_ext_discount_amt`, `ss_net_paid`, `ss_net_profit` | `i_item_sk`, `i_item_id`, `i_product_name`, `i_category`, `i_class`, `i_brand`, `i_current_price`, `i_wholesale_cost` | `s_store_sk`, `s_store_id`, `s_store_name`, `s_city`, `s_state`, `s_number_employees`, `s_floor_space` |
| Types observés | Identifiants : `int` ; montants : `double` | Identifiants : `int` ; textes : `string` ; prix : `double` ; `i_rec_start_date` : `date` | Identifiants : `int` ; textes : `string` ; `s_zip`, `s_street_number` : `int` ; `s_gmt_offset` : `int` |
| Clé candidate | (`ss_ticket_number`, `ss_item_sk`) : **non unique** | `i_item_sk` : unique | `s_store_sk` : unique |
| Granularité | Une ligne = un produit dans un ticket de caisse | Une ligne = un produit | Une ligne = un magasin |
| Anomalies identifiées | 4 136 lignes en doublon sur la clé candidate ; valeurs nulles dans 4 clés étrangères ; 74 % des lignes avec une marge négative | 7 768 produits avec un coût d'achat supérieur au prix de vente ; quelques marques et descriptions manquantes | Les 12 magasins ont une date de fermeture, parfois en 1924 ou en 2095 ; code postal lu comme un nombre |

## Schémas

Types attendus : spécification TPCx-BB (`tpcxbb_schema.json`, Jour 1).
Types observés : types inférés par Spark (`inferSchema=True`).

### `store_sales`

| Colonne | Type attendu | Type observé | Nulls |
|---|---|---|---|
| ss_sold_date_sk | bigint | int | 0 |
| ss_sold_time_sk | bigint | int | 0 |
| ss_item_sk | bigint | int | 0 |
| ss_customer_sk | bigint | int | 0 |
| ss_cdemo_sk | bigint | int | 238 |
| ss_hdemo_sk | bigint | int | 295 |
| ss_addr_sk | bigint | int | 448 |
| ss_store_sk | bigint | int | 0 |
| ss_promo_sk | bigint | int | 158 |
| ss_ticket_number | bigint | int | 0 |
| ss_quantity | int | int | 0 |
| ss_wholesale_cost | decimal(7,2) | double | 0 |
| ss_list_price | decimal(7,2) | double | 0 |
| ss_sales_price | decimal(7,2) | double | 0 |
| ss_ext_discount_amt | decimal(7,2) | double | 0 |
| ss_ext_sales_price | decimal(7,2) | double | 0 |
| ss_ext_wholesale_cost | decimal(7,2) | double | 0 |
| ss_ext_list_price | decimal(7,2) | double | 0 |
| ss_ext_tax | decimal(7,2) | double | 0 |
| ss_coupon_amt | decimal(7,2) | double | 0 |
| ss_net_paid | decimal(7,2) | double | 0 |
| ss_net_paid_inc_tax | decimal(7,2) | double | 0 |
| ss_net_profit | decimal(7,2) | double | 0 |

### `item`

| Colonne | Type attendu | Type observé | Nulls |
|---|---|---|---|
| i_item_sk | bigint | int | 0 |
| i_item_id | string | string | 0 |
| i_rec_start_date | string | date | 0 |
| i_rec_end_date | string | string | 17 820 (toutes) |
| i_item_desc | string | string | 4 |
| i_current_price | decimal(7,2) | double | 0 |
| i_wholesale_cost | decimal(7,2) | double | 0 |
| i_brand_id | int | int | 8 |
| i_brand | string | string | 6 |
| i_class_id | int | int | 0 |
| i_class | string | string | 0 |
| i_category_id | int | int | 0 |
| i_category | string | string | 0 |
| i_manufact_id | int | int | 0 |
| i_manufact | string | string | 0 |
| i_size | string | string | 0 |
| i_formulation | string | string | 0 |
| i_color | string | string | 0 |
| i_units | string | string | 0 |
| i_container | string | string | 0 |
| i_manager_id | int | int | 0 |
| i_product_name | string | string | 0 |

### `store`

| Colonne | Type attendu | Type observé | Nulls |
|---|---|---|---|
| s_store_sk | bigint | int | 0 |
| s_store_id | string | string | 0 |
| s_rec_start_date | string | date | 0 |
| s_rec_end_date | string | string | 12 (toutes) |
| s_closed_date_sk | bigint | int | 0 |
| s_store_name | string | string | 0 |
| s_number_employees | int | int | 0 |
| s_floor_space | int | int | 0 |
| s_hours | string | string | 0 |
| s_manager | string | string | 0 |
| s_market_id | int | int | 0 |
| s_geography_class | string | string | 0 |
| s_market_desc | string | string | 0 |
| s_market_manager | string | string | 0 |
| s_division_id | int | int | 0 |
| s_division_name | string | string | 0 |
| s_company_id | int | int | 0 |
| s_company_name | string | string | 0 |
| s_street_number | string | int | 0 |
| s_street_name | string | string | 0 |
| s_street_type | string | string | 0 |
| s_suite_number | string | string | 0 |
| s_city | string | string | 0 |
| s_county | string | string | 0 |
| s_state | string | string | 0 |
| s_zip | string | int | 0 |
| s_country | string | string | 0 |
| s_gmt_offset | decimal(5,2) | int | 0 |
| s_tax_precentage | decimal(5,2) | double | 0 |

## Premiers constats

- **Période couverte** : `ss_sold_date_sk` va de 36890 à 38697, soit du
  01/01/2001 au 13/12/2005 (correspondance lue dans `date_dim`).
- **Volume** : 89 100 tickets, 12 magasins et les 17 820 produits du catalogue
  apparaissent dans les ventes.
- **Relations vérifiées** : chaque `ss_item_sk` existe dans `item` et chaque
  `ss_store_sk` existe dans `store` (0 ligne sans correspondance). Les
  jointures `store_sales -> item` et `store_sales -> store` sont donc possibles.
- **Calculs cohérents** : aucune quantité nulle ou négative, aucun prix négatif,
  aucun prix de vente supérieur au prix catalogue, et
  `ss_ext_sales_price = ss_quantity x ss_sales_price` sur toutes les lignes.
- **Doublons de vente** : 4 136 lignes partagent un couple (ticket, produit)
  déjà présent, sans être des copies exactes (0 ligne entièrement dupliquée).
  Le Jour 1 avait déjà repéré ce point (4 038 couples concernés). Il faudra
  décider en Silver s'il s'agit de doublons à retirer ou de lignes légitimes
  (même produit scanné deux fois).
- **Marge** : 495 971 lignes (74 %) ont un `ss_net_profit` négatif. C'est
  propre aux données générées par TPCx-BB, mais il faut le signaler avant de
  présenter une marge.
- **Dimensions sans historique** : `i_rec_end_date` et `s_rec_end_date` sont
  vides partout, et `i_item_id` / `s_store_id` sont uniques. Il n'y a qu'une
  version de chaque produit et de chaque magasin.
- **Dates de fermeture incohérentes** : les 12 magasins ont un
  `s_closed_date_sk` renseigné, entre 1924 et 2095, alors qu'ils ouvrent en
  2000 et enregistrent des ventes jusqu'en 2005. Cette colonne n'est pas fiable.

## Réponses aux questions techniques

**1. Les fichiers sont-ils structurés, semi-structurés ou non structurés ?**
Structurés : texte délimité par `|`, avec un nombre de colonnes fixe sur
toutes les lignes. Il n'y a pas d'en-tête : les noms de colonnes viennent de la
spécification TPCx-BB. Seule `i_item_desc` contient du texte libre.

**2. Les colonnes sont-elles correctement typées ?**
Pas tout à fait. Spark infère `double` pour les montants alors que la
spécification attend `decimal(7,2)`, ce qui peut créer des erreurs d'arrondi sur
les sommes. Les identifiants sont lus en `int` au lieu de `bigint` (sans
conséquence à ce volume). Certains codes sont lus comme des nombres : `s_zip`
perdrait ses zéros initiaux et `s_street_number` doit rester du texte. En
Silver, il faudra imposer un schéma explicite plutôt que l'inférence.

**3. Certaines colonnes contiennent-elles des valeurs nulles ?**
Oui. Dans `store_sales`, les clés vers les données client (`ss_cdemo_sk`,
`ss_hdemo_sk`, `ss_addr_sk`) et vers la promotion (`ss_promo_sk`) : moins de
0,1 % des lignes. Dans `item`, quelques marques et descriptions. Les colonnes
`*_rec_end_date` sont vides partout, ce qui est normal sans historique. Aucune
colonne utile au CA ou à la marge n'est nulle.

**4. Les identifiants sont-ils uniques lorsque cela est attendu ?**
Oui pour les dimensions : `i_item_sk` (17 820 valeurs distinctes sur 17 820) et
`s_store_sk` (12 sur 12). Non pour `store_sales` : le couple
(`ss_ticket_number`, `ss_item_sk`) a 4 136 doublons, et la table n'a pas de
clé technique propre.

**5. La granularité est-elle connue ?**
Oui. `store_sales` : une ligne par produit et par ticket de caisse. `item` : une
ligne par produit. `store` : une ligne par magasin.

**6. Les données sont-elles adaptées aux questions métier du Jour 1 ?**
En partie.

- Elles conviennent pour :
  - le CA mensuel, avec une jointure sur `date_dim` ;
  - le CA et la marge par produit, par catégorie (9 catégories) et par magasin ;
  - le niveau des remises (`ss_ext_discount_amt`).
- Elles ne suffisent pas pour :
  - la part magasin / web, qui demande d'ajouter `web_sales` ;
  - le taux de retour, qui demande `store_returns` ;
  - les ruptures de stock, qui demandent `inventory`.
- Point d'attention : la marge doit être interprétée avec prudence, car elle
  est négative sur la majorité des lignes.
