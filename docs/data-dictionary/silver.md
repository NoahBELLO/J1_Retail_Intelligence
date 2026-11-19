# Données Silver - TP Jour 3, Étape 6

La zone Silver contient les données **nettoyées et harmonisées** : les types
sont explicites, les règles de l'étape 4 sont appliquées, la provenance est
conservée, et chaque jeu est documenté.

| Notebook | Rôle |
|---|---|
| `notebooks/cleaning/nettoyage_silver.ipynb` | Produit `sales`, `products`, `stores`, `dates` et `rejects` |
| `notebooks/transformations/enrichissement_ventes.ipynb` | Produit `sales_enriched` |
| `notebooks/quality/controles_silver.ipynb` | Contrôles après écriture ; résultats dans `outputs/controles_silver.json` |

## Organisation

Seuls les domaines réellement disponibles et traités sont créés. Il n'y a ni
`customers`, ni `inventory`, ni `returns`, car ces sources n'ont pas été
retenues à l'étape 2.

```
data/silver/
+-- sales/            ventes en magasin nettoyees        (store_sales)
+-- products/         catalogue produits                 (item)
+-- stores/           magasins                           (store)
+-- dates/            calendrier                         (date_dim)
+-- sales_enriched/   ventes + date + produit + magasin  (partitionne par annee)
|   +-- annee=2001/ ... annee=2005/
+-- rejects/          lignes ecartees, avec motif_rejet
    +-- sales/  products/  stores/  dates/
```

## Convention de nommage

| Élément | Règle | Exemple |
|---|---|---|
| Dossier d'un jeu | Domaine métier, en anglais, au pluriel, en minuscules, en `snake_case` | `sales`, `products`, `sales_enriched` |
| Jeu dérivé | Domaine + suffixe qui décrit la transformation | `sales_enriched` |
| Lignes écartées | Même nom de domaine, sous `rejects/` | `rejects/sales` |
| Colonnes des jeux nettoyés | Noms d'origine TPCx-BB conservés (préfixe de table `ss_`, `i_`, `s_`, `d_`), pour garder le lien avec la source et la spécification | `ss_net_paid` |
| Colonnes ajoutées au nettoyage | Préfixe de la table + nom en français | `ss_ligne_ticket`, `ss_prix_nul`, `s_date_fermeture_invalide` |
| Colonnes du jeu enrichi | Noms métier en français, en `snake_case`, sans préfixe. Les colonnes d'origine sont citées dans la description | `montant_net_paye`, `nom_magasin` |
| Colonnes techniques (provenance) | Préfixe `_` | `_source_fichier`, `_date_traitement` |
| Clés | `_sk` pour une clé technique, `_id` pour un code métier | `produit_sk`, `produit_id` |
| Indicateurs | Booléen, nom en forme d'affirmation | `marge_negative`, `sans_promotion` |

## Format

**Parquet**, avec la compression Snappy par défaut de Spark :
- le format est colonnaire, ce qui accélère les agrégations ;
- les types sont stockés dans le fichier : `decimal(7,2)`, `date` et `bigint`
  ne sont pas perdus, contrairement à un CSV ;
- c'est le format demandé pour les fichiers analytiques.

`sales_enriched` est partitionné par `annee`, car la plupart des analyses
filtrent sur une période.

## Provenance

Chaque ligne Silver garde la trace de son origine :

| Colonne | Contenu |
|---|---|
| `_source_systeme` | `TPCx-BB` |
| `_source_table` | Table brute d'origine (`store_sales`, `item`, `store`, `date_dim`) |
| `_source_fichier` | Chemin du fichier brut lu |
| `_sources_silver` | Pour `sales_enriched` : les jeux Silver utilisés |
| `_traitement` | Notebook qui a produit la ligne |
| `_date_traitement` | Date et heure du traitement |

Avec la clé de chaque ligne, ces colonnes permettent de remonter d'un
indicateur Gold à la ligne du fichier brut d'origine.

## Jeux de données

Les types sont ceux relus dans les fichiers Parquet. Ils sont identiques aux
schémas de référence de `docs/data-dictionary/schemas/`.

### `silver/sales/` - Ventes en magasin nettoyées

| | |
|---|---|
| Source | `store_sales` (échantillon de 10 % des tickets) |
| Traitement | `notebooks/cleaning/nettoyage_silver.ipynb` |
| Granularité | 1 ligne = 1 produit dans 1 ticket |
| Clé | (`ss_ticket_number`, `ss_item_sk`, `ss_ligne_ticket`) |
| Lignes | 66 593 |
| Format | Parquet (Snappy) |
| Schéma de référence | `docs/data-dictionary/schemas/silver_sales.json` |

| Colonne | Type | Description |
|---|---|---|
| `ss_sold_date_sk` | bigint | Clé de la date de vente (-> `dates.d_date_sk`) |
| `ss_store_sk` | bigint | Clé du magasin (-> `stores.s_store_sk`) |
| `ss_item_sk` | bigint | Clé du produit (-> `products.i_item_sk`) |
| `ss_sold_time_sk` | bigint | Clé de l'heure de vente (seconde de la journée, table `time_dim`) |
| `ss_customer_sk` | bigint | Clé du client (table `customer`, non traitée) |
| `ss_cdemo_sk` | bigint | Clé du profil démographique du client (facultative) |
| `ss_hdemo_sk` | bigint | Clé du profil du foyer (facultative) |
| `ss_addr_sk` | bigint | Clé de l'adresse du client (facultative) |
| `ss_promo_sk` | bigint | Clé de la promotion ; vide = vente sans promotion |
| `ss_ticket_number` | bigint | Numéro du ticket de caisse |
| `ss_quantity` | int | Quantité vendue (> 0) |
| `ss_wholesale_cost` | decimal(7,2) | Coût d'achat unitaire |
| `ss_list_price` | decimal(7,2) | Prix catalogue unitaire |
| `ss_sales_price` | decimal(7,2) | Prix de vente unitaire, après remise |
| `ss_ext_discount_amt` | decimal(7,2) | Remise totale de la ligne |
| `ss_ext_sales_price` | decimal(7,2) | Montant de vente = quantité x prix de vente |
| `ss_ext_wholesale_cost` | decimal(7,2) | Coût d'achat total de la ligne |
| `ss_ext_list_price` | decimal(7,2) | Montant au prix catalogue = quantité x prix catalogue |
| `ss_ext_tax` | decimal(7,2) | Taxes de la ligne |
| `ss_coupon_amt` | decimal(7,2) | Montant des coupons utilisés |
| `ss_net_paid` | decimal(7,2) | Montant payé, hors taxes, remises et coupons déduits (base du CA) |
| `ss_net_paid_inc_tax` | decimal(7,2) | Montant payé, taxes comprises |
| `ss_net_profit` | decimal(7,2) | Marge de la ligne (peut être négative) |
| `ss_ligne_ticket` | int | Numéro de la ligne pour un même couple (ticket, produit), ajouté par R6 |
| `ss_prix_nul` | boolean | Indicateur : prix de vente = 0 (R7) |
| `ss_marge_negative` | boolean | Indicateur : marge < 0 (R7) |
| `ss_sans_promotion` | boolean | Indicateur : aucune promotion (R3) |
| `_source_systeme` | string | Système d'origine (`TPCx-BB`) |
| `_source_table` | string | Table brute d'origine (`store_sales`, `item`...) |
| `_source_fichier` | string | Chemin du fichier brut lu |
| `_traitement` | string | Notebook qui a produit la ligne |
| `_date_traitement` | timestamp | Date et heure du traitement |

### `silver/products/` - Catalogue produits nettoyé

| | |
|---|---|
| Source | `item` |
| Traitement | `notebooks/cleaning/nettoyage_silver.ipynb` |
| Granularité | 1 ligne = 1 produit |
| Clé | `i_item_sk` |
| Lignes | 17 820 |
| Format | Parquet (Snappy) |
| Schéma de référence | `docs/data-dictionary/schemas/silver_products.json` |

| Colonne | Type | Description |
|---|---|---|
| `i_item_sk` | bigint | Clé technique du produit |
| `i_item_id` | string | Code métier du produit |
| `i_rec_start_date` | date | Début de validité de la fiche produit |
| `i_rec_end_date` | date | Fin de validité (toujours vide : version courante) |
| `i_item_desc` | string | Description libre |
| `i_current_price` | decimal(7,2) | Prix de vente courant (> 0) |
| `i_wholesale_cost` | decimal(7,2) | Coût d'achat |
| `i_brand_id` | int | Code de la marque |
| `i_brand` | string | Nom de la marque |
| `i_class_id` | int | Code de la sous-catégorie |
| `i_class` | string | Sous-catégorie |
| `i_category_id` | int | Code de la catégorie (1 à 9) |
| `i_category` | string | Catégorie (Music, Books...) |
| `i_manufact_id` | int | Code du fabricant |
| `i_manufact` | string | Nom du fabricant |
| `i_size` | string | Taille |
| `i_formulation` | string | Composition |
| `i_color` | string | Couleur |
| `i_units` | string | Unité de vente |
| `i_container` | string | Conditionnement |
| `i_manager_id` | int | Code du responsable produit |
| `i_product_name` | string | Nom du produit |
| `i_cout_superieur_prix` | boolean | Indicateur : coût d'achat > prix courant (R7) |
| `_source_systeme` | string | Système d'origine (`TPCx-BB`) |
| `_source_table` | string | Table brute d'origine (`store_sales`, `item`...) |
| `_source_fichier` | string | Chemin du fichier brut lu |
| `_traitement` | string | Notebook qui a produit la ligne |
| `_date_traitement` | timestamp | Date et heure du traitement |

### `silver/stores/` - Magasins nettoyés

| | |
|---|---|
| Source | `store` |
| Traitement | `notebooks/cleaning/nettoyage_silver.ipynb` |
| Granularité | 1 ligne = 1 magasin |
| Clé | `s_store_sk` |
| Lignes | 12 |
| Format | Parquet (Snappy) |
| Schéma de référence | `docs/data-dictionary/schemas/silver_stores.json` |

| Colonne | Type | Description |
|---|---|---|
| `s_store_sk` | bigint | Clé technique du magasin |
| `s_store_id` | string | Code métier du magasin |
| `s_rec_start_date` | date | Date d'ouverture / début de validité |
| `s_rec_end_date` | date | Fin de validité (toujours vide) |
| `s_store_name` | string | Nom du magasin |
| `s_number_employees` | int | Nombre d'employés |
| `s_floor_space` | int | Surface de vente |
| `s_hours` | string | Horaires d'ouverture |
| `s_manager` | string | Directeur du magasin |
| `s_market_id` | int | Code du marché |
| `s_geography_class` | string | Type de zone géographique |
| `s_market_desc` | string | Description du marché |
| `s_market_manager` | string | Responsable du marché |
| `s_division_id` | int | Code de la division |
| `s_division_name` | string | Nom de la division |
| `s_company_id` | int | Code de la société |
| `s_company_name` | string | Nom de la société |
| `s_street_number` | string | Numéro de rue (texte) |
| `s_street_name` | string | Nom de rue |
| `s_street_type` | string | Type de voie |
| `s_suite_number` | string | Complément d'adresse |
| `s_city` | string | Ville |
| `s_county` | string | Comté |
| `s_state` | string | État (code à 2 lettres) |
| `s_zip` | string | Code postal, 5 caractères (texte, R2) |
| `s_country` | string | Pays |
| `s_gmt_offset` | decimal(5,2) | Décalage horaire par rapport à GMT |
| `s_tax_precentage` | decimal(5,2) | Taux de taxe (nom d'origine conservé, avec sa faute) |
| `s_closed_date` | date | Date de fermeture ; vide si inconnue ou invalide (R5) |
| `s_date_fermeture_invalide` | boolean | Indicateur : la date de fermeture source était incohérente (R5) |
| `_source_systeme` | string | Système d'origine (`TPCx-BB`) |
| `_source_table` | string | Table brute d'origine (`store_sales`, `item`...) |
| `_source_fichier` | string | Chemin du fichier brut lu |
| `_traitement` | string | Notebook qui a produit la ligne |
| `_date_traitement` | timestamp | Date et heure du traitement |

### `silver/dates/` - Calendrier (référentiel des dates)

| | |
|---|---|
| Source | `date_dim` |
| Traitement | `notebooks/cleaning/nettoyage_silver.ipynb` |
| Granularité | 1 ligne = 1 jour |
| Clé | `d_date_sk` |
| Lignes | 109 573 |
| Format | Parquet (Snappy) |
| Schéma de référence | `docs/data-dictionary/schemas/silver_dates.json` |

| Colonne | Type | Description |
|---|---|---|
| `d_date_sk` | bigint | Clé technique de la date |
| `d_date` | date | Date calendaire |
| `d_year` | int | Année |
| `d_qoy` | int | Trimestre (1 à 4) |
| `d_moy` | int | Mois (1 à 12) |
| `d_dom` | int | Jour du mois |
| `d_day_name` | string | Nom du jour (Monday...) |
| `d_weekend` | string | Week-end (Y/N) |
| `d_holiday` | string | Jour férié (Y/N) |
| `_source_systeme` | string | Système d'origine (`TPCx-BB`) |
| `_source_table` | string | Table brute d'origine (`store_sales`, `item`...) |
| `_source_fichier` | string | Chemin du fichier brut lu |
| `_traitement` | string | Notebook qui a produit la ligne |
| `_date_traitement` | timestamp | Date et heure du traitement |

### `silver/sales_enriched/` - Ventes enrichies : date, produit et magasin, colonnes en français

| | |
|---|---|
| Source | `silver/sales` + `dates` + `products` + `stores` |
| Traitement | `notebooks/transformations/enrichissement_ventes.ipynb` |
| Granularité | 1 ligne = 1 produit dans 1 ticket |
| Clé | (`ticket_id`, `produit_sk`, `ligne_ticket`) |
| Lignes | 66 593 |
| Format | Parquet (Snappy), partitionné par `annee` |
| Schéma de référence | `docs/data-dictionary/schemas/silver_sales_enriched.json` |

| Colonne | Type | Description |
|---|---|---|
| `date_vente` | date | Date de la vente (`dates.d_date`) |
| `trimestre` | int | Trimestre |
| `mois` | int | Mois |
| `jour_semaine` | string | Nom du jour |
| `heure_sk` | bigint | Clé de l'heure de vente (`ss_sold_time_sk`) |
| `ticket_id` | bigint | Numéro du ticket (`ss_ticket_number`) |
| `ligne_ticket` | int | Numéro de ligne pour un même (ticket, produit) |
| `client_sk` | bigint | Clé du client (`ss_customer_sk`) |
| `promotion_sk` | bigint | Clé de la promotion (`ss_promo_sk`) |
| `produit_sk` | bigint | Clé du produit (`ss_item_sk`) |
| `produit_id` | string | Code métier du produit (`i_item_id`) |
| `nom_produit` | string | Nom du produit (`i_product_name`) |
| `categorie_id` | int | Code de la catégorie |
| `categorie` | string | Catégorie du produit |
| `sous_categorie` | string | Sous-catégorie (`i_class`) |
| `marque` | string | Marque (`i_brand`) |
| `magasin_sk` | bigint | Clé du magasin (`ss_store_sk`) |
| `magasin_id` | string | Code métier du magasin (`s_store_id`) |
| `nom_magasin` | string | Nom du magasin |
| `ville` | string | Ville du magasin |
| `etat` | string | État du magasin |
| `quantite` | int | Quantité vendue |
| `prix_catalogue_unitaire` | decimal(7,2) | Prix catalogue unitaire (`ss_list_price`) |
| `prix_vente_unitaire` | decimal(7,2) | Prix de vente unitaire (`ss_sales_price`) |
| `montant_catalogue` | decimal(7,2) | Montant au prix catalogue (`ss_ext_list_price`) |
| `montant_remise` | decimal(7,2) | Remise totale (`ss_ext_discount_amt`) |
| `montant_vente` | decimal(7,2) | Montant de vente (`ss_ext_sales_price`) |
| `montant_coupon` | decimal(7,2) | Coupons (`ss_coupon_amt`) |
| `montant_net_paye` | decimal(7,2) | Montant payé hors taxes = base du CA (`ss_net_paid`) |
| `cout_total` | decimal(7,2) | Coût d'achat total (`ss_ext_wholesale_cost`) |
| `marge` | decimal(7,2) | Marge (`ss_net_profit`) |
| `prix_nul` | boolean | Indicateur : prix de vente = 0 |
| `marge_negative` | boolean | Indicateur : marge < 0 |
| `sans_promotion` | boolean | Indicateur : aucune promotion |
| `_source_systeme` | string | Système d'origine (`TPCx-BB`) |
| `_source_fichier` | string | Chemin du fichier brut lu |
| `_sources_silver` | string | Jeux Silver utilisés pour construire la ligne |
| `_traitement` | string | Notebook qui a produit la ligne |
| `_date_traitement` | timestamp | Date et heure du traitement |
| `taux_marge` | decimal(12,4) | Marge ÷ montant net payé (vide si montant = 0) |
| `taux_remise` | decimal(12,4) | Remise ÷ montant catalogue (vide si montant = 0) |
| `annee` | int | Année de la vente (colonne de partition) |

## Contrôles après écriture

Les contrôles sont faits par `notebooks/quality/controles_silver.ipynb` : **77 contrôles, tous OK**.

| Contrôle | Méthode | Résultat |
|---|---|---|
| Présence | Le dossier existe, avec un fichier `_SUCCESS` et des fichiers `.parquet` | OK pour les 5 jeux |
| Format | Chaque fichier commence et se termine par la signature Parquet `PAR1` | OK |
| Lisibilité | `spark.read.parquet` relit chaque jeu sans erreur | OK |
| Nombre de lignes | Silver = lignes lues − rejets − doublons supprimés. Les lignes lues sont recomptées dans le fichier brut, sans Spark. `sales_enriched` = `sales` | OK : 66 593, 17 820, 12, 109 573, 66 593 |
| Schéma | Le schéma relu est identique au schéma de référence exporté. Les types attendus sont présents (`decimal(7,2)`, `date`, `bigint`, `s_zip` en texte). Les colonnes de provenance sont présentes | OK |
| Cohérence | Clés uniques, colonnes obligatoires remplies, provenance renseignée, aucune vente orpheline (produit, magasin, date), quantités > 0, montant = quantité × prix, codes postaux à 5 caractères, même CA dans `sales` et `sales_enriched` (115 752 176,68), période du 01/01/2001 au 13/12/2005 | OK |
