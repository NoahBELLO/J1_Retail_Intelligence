# Contribution Lorenzo

## UC1

### ETAPE A

- Direction commerciale :
  - Performance des ventes et des produits.
  - Quels sont les produits et catégories qui génèrent le plus de Chiffre d'Affaires ?
    - Décision : mettre en avant les catégories les plus rentables.
    - Priorité : **Indispensable** (indicateur de base du pilotage commercial, impact direct sur le CA)
  - Comment se répartit le Chiffre d'Affaires entre les magasins et le web ?
    - Décision : réallouer les investissements entre le web et les magasins.
    - Priorité : **Utile** (décision stratégique, mais prise sur un rythme trimestriel ou annuel)

---

- Responsable des stocks :
  - Disponibilité et mouvements de stock.
  - Quels produits sont en rupture ou en surstock ?
    - Décision : ajuster les seuils de réapprovisionnement et les quantités commandées, et déstocker les surplus.
    - Priorité : **Indispensable** (une rupture fait perdre des ventes, un surstock immobilise de l'argent)
  - Quels modes de livraison et quels entrepôts causent le plus de retards ?
    - Décision : changer de transporteur ou de mode de livraison, et réaffecter les commandes vers les entrepôts les plus performants.
    - Priorité : **Complémentaire** (concerne seulement le canal web, c'est une optimisation logistique)

---

- Responsable de magasin :
  - Suivi de son établissement
  - Comment évoluent le Chiffre d'Affaires par tranche horaire ?
    - Décision : ajuster les horaires d'ouverture et le personnel en fonction des périodes de forte affluence.
    - Priorité : **Utile** (optimise les ressources, mais n'est pas bloquant)
  - Quel est le taux de retour dans mon magasin ?
    - Décision : identifier les causes des retours et améliorer la qualité des produits ou le service client.
    - Priorité : **Complémentaire** (amélioration continue, concerne une petite part des ventes)

## Étape B – Indicateurs

---

### 1. Chiffre d'affaires (CA)

1. **Nom** : Chiffre d'affaires net
2. **Définition métier** : montant encaissé sur les ventes, remises déduites et hors taxes.
3. **Formule** : `SUM(ss_net_paid) + SUM(ws_net_paid)`
4. **Unité** : € (devise non précisée dans le jeu de données)
5. **Périmètre** : magasins + web, déclinable par canal, magasin, produit, catégorie et période
6. **Fréquence** : quotidienne, agrégée par semaine, mois et année
7. **Sources** : `store_sales`, `web_sales`, `date_dim`, `item`, `store`, `web_site`
8. **Données manquantes** : pas de canal catalogue (`catalog_sales` absent) ; certaines lignes ont des clés NULL (date, article, magasin) ; devise non renseignée
9. **Limites** : les retours ne sont pas déduits (il faudrait `store_returns` / `web_returns` pour un CA net de retours) ; un CA élevé ne veut pas dire une marge élevée

---

### 2. Nombre de transactions

1. **Nom** : Nombre de transactions
2. **Définition métier** : nombre de tickets de caisse (magasin) et de commandes (web) distincts.
3. **Formule** : `COUNT(DISTINCT ss_ticket_number) + COUNT(DISTINCT ws_order_number)`
4. **Unité** : nombre de transactions
5. **Périmètre** : magasins + web, par magasin, canal et période
6. **Fréquence** : quotidienne
7. **Sources** : `store_sales`, `web_sales`, `date_dim`, `store`
8. **Données manquantes** : pas de canal catalogue ; tickets dont le client est NULL (client anonyme)
9. **Limites** : une transaction n'est pas un client unique (un même client peut passer plusieurs fois) ; les numéros de ticket et de commande se comptent séparément par canal

---

### 3. Panier moyen

1. **Nom** : Panier moyen
2. **Définition métier** : montant moyen dépensé par transaction.
3. **Formule** : `CA net / Nombre de transactions`
4. **Unité** : € par transaction
5. **Périmètre** : par canal, magasin et période (à calculer séparément magasin / web)
6. **Fréquence** : hebdomadaire et mensuelle
7. **Sources** : `store_sales`, `web_sales`, `date_dim`, `store`
8. **Données manquantes** : mêmes que pour le CA et les transactions
9. **Limites** : sensible aux valeurs extrêmes (quelques grosses commandes font monter la moyenne) ; mélanger magasin et web fausse la lecture

---

### 4. Quantités vendues

1. **Nom** : Quantités vendues
2. **Définition métier** : nombre d'articles vendus.
3. **Formule** : `SUM(ss_quantity) + SUM(ws_quantity)`
4. **Unité** : nombre d'unités
5. **Périmètre** : par produit, catégorie, magasin, entrepôt et période
6. **Fréquence** : quotidienne
7. **Sources** : `store_sales`, `web_sales`, `item`, `date_dim`
8. **Données manquantes** : quantités NULL sur certaines lignes ; pas de canal catalogue
9. **Limites** : additionne des produits très différents (une unité de chaussette = une unité de télé) ; les retours ne sont pas déduits

---

### 5. Évolution des ventes

1. **Nom** : Taux d'évolution du CA
2. **Définition métier** : variation du CA entre une période et la même période de l'année précédente.
3. **Formule** : `(CA période N − CA période N-1) / CA période N-1 × 100`
4. **Unité** : %
5. **Périmètre** : par canal, magasin, catégorie
6. **Fréquence** : mensuelle et annuelle
7. **Sources** : `store_sales`, `web_sales`, `date_dim` (`d_year`, `d_moy`)
8. **Données manquantes** : la plage de dates couverte est limitée (vérifier les années réellement présentes dans les ventes) ; un magasin ouvert ou fermé en cours de période n'a pas d'historique comparable
9. **Limites** : sensible à la saisonnalité et aux événements ponctuels ; une hausse peut venir d'une ouverture de magasin plutôt que d'une vraie croissance

## Étape C – Examiner les données

### 1. Répertoire de données

`retail_project/retail_project/` contient deux zones :

- `data/` : chargement initial (historique).
- `data_refresh/` : lot de rafraîchissement (incrémental).

Un dossier par table, un fichier `<table>.dat` par dossier.

---

### 2. Recensement des fichiers et 8. Volumes

| Table                    | Rôle                           | Lignes `data` | Taille `data` | Lignes `data_refresh` |
| ------------------------ | ------------------------------ | ------------: | ------------: | --------------------: |
| `store_sales`            | Fait – ventes magasin          |       667 579 |         89 Mo |                 6 632 |
| `web_sales`              | Fait – ventes web              |       668 052 |        128 Mo |                 6 879 |
| `store_returns`          | Fait – retours magasin         |        37 902 |        4,2 Mo |                   426 |
| `web_returns`            | Fait – retours web             |        38 487 |        5,2 Mo |                   400 |
| `inventory`              | Fait – stock (photo hebdo)     |    23 255 100 |        406 Mo |               234 900 |
| `web_clickstreams`       | Fait – clics web               |     6 770 550 |        171 Mo |                68 988 |
| `product_reviews`        | Avis clients (texte libre)     |        89 991 |         54 Mo |                   909 |
| `item_marketprices`      | Prix concurrents               |        89 100 |        4,1 Mo |                   900 |
| `customer`               | Dimension client               |        99 000 |         13 Mo |                 1 000 |
| `customer_address`       | Dimension adresse              |        49 500 |        5,2 Mo |                   500 |
| `customer_demographics`  | Dimension démographie          |     1 920 800 |         75 Mo |                     – |
| `household_demographics` | Dimension foyer                |         7 200 |        152 Ko |                     – |
| `income_band`            | Tranches de revenus            |            20 |          4 Ko |                     – |
| `item`                   | Dimension produit              |        17 820 |        6,5 Mo |                   180 |
| `date_dim`               | Dimension date                 |       109 573 |         15 Mo |                     – |
| `time_dim`               | Dimension heure (à la seconde) |        86 400 |        4,9 Mo |                     – |
| `store`                  | Dimension magasin              |            12 |          4 Ko |                     – |
| `warehouse`              | Dimension entrepôt             |             5 |          4 Ko |                     – |
| `web_site`               | Dimension site web             |            30 |         12 Ko |                     – |
| `web_page`               | Dimension page web             |            60 |          8 Ko |                     – |
| `promotion`              | Dimension promotion            |           300 |         48 Ko |                     – |
| `reason`                 | Motifs de retour               |            35 |          4 Ko |                     – |
| `ship_mode`              | Modes de livraison             |            20 |          4 Ko |                     – |

Fichier annexe : `item_marketprices/item_marketprices_audit.csv` (rapport de contrôle du générateur : nombre de concurrents par article), présent dans les deux zones.

_Trouver grâce un script, développé par claude._

### 3. Formats

- `.dat` : texte délimité par `|`, **sans ligne d'en-tête**, encodage ASCII (UTF-8 pour `customer`, qui contient des caractères non-ASCII).
- Dates au format `AAAA-MM-JJ`.
- `.csv` (audit) : CSV avec en-tête, suivi de listes texte libres → pas un fichier tabulaire propre.
- `product_reviews.pr_review_content` : texte libre long (jusqu'à 5 748 caractères), contient des entités HTML (`&quot;`) → donnée **semi-structurée**.

---

### 4. Noms exacts des colonnes (tables utiles aux indicateurs)

- **`store_sales`** (23) : `ss_sold_date_sk`, `ss_sold_time_sk`, `ss_item_sk`, `ss_customer_sk`, `ss_cdemo_sk`, `ss_hdemo_sk`, `ss_addr_sk`, `ss_store_sk`, `ss_promo_sk`, `ss_ticket_number`, `ss_quantity`, `ss_wholesale_cost`, `ss_list_price`, `ss_sales_price`, `ss_ext_discount_amt`, `ss_ext_sales_price`, `ss_ext_wholesale_cost`, `ss_ext_list_price`, `ss_ext_tax`, `ss_coupon_amt`, `ss_net_paid`, `ss_net_paid_inc_tax`, `ss_net_profit`
- **`web_sales`** (34) : `ws_sold_date_sk`, `ws_sold_time_sk`, `ws_ship_date_sk`, `ws_item_sk`, `ws_bill_customer_sk`, `ws_bill_cdemo_sk`, `ws_bill_hdemo_sk`, `ws_bill_addr_sk`, `ws_ship_customer_sk`, `ws_ship_cdemo_sk`, `ws_ship_hdemo_sk`, `ws_ship_addr_sk`, `ws_web_page_sk`, `ws_web_site_sk`, `ws_ship_mode_sk`, `ws_warehouse_sk`, `ws_promo_sk`, `ws_order_number`, `ws_quantity`, `ws_wholesale_cost`, `ws_list_price`, `ws_sales_price`, `ws_ext_discount_amt`, `ws_ext_sales_price`, `ws_ext_wholesale_cost`, `ws_ext_list_price`, `ws_ext_tax`, `ws_coupon_amt`, `ws_ext_ship_cost`, `ws_net_paid`, `ws_net_paid_inc_tax`, `ws_net_paid_inc_ship`, `ws_net_paid_inc_ship_tax`, `ws_net_profit`
- **`store_returns`** (20) : `sr_returned_date_sk`, `sr_return_time_sk`, `sr_item_sk`, `sr_customer_sk`, `sr_cdemo_sk`, `sr_hdemo_sk`, `sr_addr_sk`, `sr_store_sk`, `sr_reason_sk`, `sr_ticket_number`, `sr_return_quantity`, `sr_return_amt`, `sr_return_tax`, `sr_return_amt_inc_tax`, `sr_fee`, `sr_return_ship_cost`, `sr_refunded_cash`, `sr_reversed_charge`, `sr_store_credit`, `sr_net_loss`
- **`web_returns`** (24) : `wr_returned_date_sk`, `wr_returned_time_sk`, `wr_item_sk`, `wr_refunded_customer_sk`, `wr_refunded_cdemo_sk`, `wr_refunded_hdemo_sk`, `wr_refunded_addr_sk`, `wr_returning_customer_sk`, `wr_returning_cdemo_sk`, `wr_returning_hdemo_sk`, `wr_returning_addr_sk`, `wr_web_page_sk`, `wr_reason_sk`, `wr_order_number`, `wr_return_quantity`, `wr_return_amt`, `wr_return_tax`, `wr_return_amt_inc_tax`, `wr_fee`, `wr_return_ship_cost`, `wr_refunded_cash`, `wr_reversed_charge`, `wr_account_credit`, `wr_net_loss`
- **`inventory`** (4) : `inv_date_sk`, `inv_item_sk`, `inv_warehouse_sk`, `inv_quantity_on_hand`
- **`item`** (22) : `i_item_sk`, `i_item_id`, `i_rec_start_date`, `i_rec_end_date`, `i_item_desc`, `i_current_price`, `i_wholesale_cost`, `i_brand_id`, `i_brand`, `i_class_id`, `i_class`, `i_category_id`, `i_category`, `i_manufact_id`, `i_manufact`, `i_size`, `i_formulation`, `i_color`, `i_units`, `i_container`, `i_manager_id`, `i_product_name`
- **`date_dim`** (28) : `d_date_sk`, `d_date_id`, `d_date`, `d_month_seq`, `d_week_seq`, `d_quarter_seq`, `d_year`, `d_dow`, `d_moy`, `d_dom`, `d_qoy`, `d_fy_year`, `d_fy_quarter_seq`, `d_fy_week_seq`, `d_day_name`, `d_quarter_name`, `d_holiday`, `d_weekend`, `d_following_holiday`, `d_first_dom`, `d_last_dom`, `d_same_day_ly`, `d_same_day_lq`, `d_current_day`, `d_current_week`, `d_current_month`, `d_current_quarter`, `d_current_year`
- **`time_dim`** (10) : `t_time_sk`, `t_time_id`, `t_time`, `t_hour`, `t_minute`, `t_second`, `t_am_pm`, `t_shift`, `t_sub_shift`, `t_meal_time`
- **`store`** (29) : `s_store_sk`, `s_store_id`, `s_rec_start_date`, `s_rec_end_date`, `s_closed_date_sk`, `s_store_name`, `s_number_employees`, `s_floor_space`, `s_hours`, `s_manager`, `s_market_id`, `s_geography_class`, `s_market_desc`, `s_market_manager`, `s_division_id`, `s_division_name`, `s_company_id`, `s_company_name`, `s_street_number`, `s_street_name`, `s_street_type`, `s_suite_number`, `s_city`, `s_county`, `s_state`, `s_zip`, `s_country`, `s_gmt_offset`, `s_tax_precentage`
- **`warehouse`** (14) : `w_warehouse_sk`, `w_warehouse_id`, `w_warehouse_name`, `w_warehouse_sq_ft`, `w_street_number`, `w_street_name`, `w_street_type`, `w_suite_number`, `w_city`, `w_county`, `w_state`, `w_zip`, `w_country`, `w_gmt_offset`
- **`ship_mode`** (6) : `sm_ship_mode_sk`, `sm_ship_mode_id`, `sm_type`, `sm_code`, `sm_carrier`, `sm_contract`
- **`reason`** (3) : `r_reason_sk`, `r_reason_id`, `r_reason_desc`
- **`customer`** (18) : `c_customer_sk`, `c_customer_id`, `c_current_cdemo_sk`, `c_current_hdemo_sk`, `c_current_addr_sk`, `c_first_shipto_date_sk`, `c_first_sales_date_sk`, `c_salutation`, `c_first_name`, `c_last_name`, `c_preferred_cust_flag`, `c_birth_day`, `c_birth_month`, `c_birth_year`, `c_birth_country`, `c_login`, `c_email_address`, `c_last_review_date`
- **`web_site`** (26) : `web_site_sk`, `web_site_id`, `web_rec_start_date`, `web_rec_end_date`, `web_name`, `web_open_date_sk`, `web_close_date_sk`, `web_class`, `web_manager`, `web_mkt_id`, `web_mkt_class`, `web_mkt_desc`, `web_market_manager`, `web_company_id`, `web_company_name`, `web_street_number`, `web_street_name`, `web_street_type`, `web_suite_number`, `web_city`, `web_county`, `web_state`, `web_zip`, `web_country`, `web_gmt_offset`, `web_tax_percentage`

---

### 5. Identifiants potentiels

| Table                                                                                                                                      | Identifiant                                                                               | Vérification                                                                                                                      |
| ------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Dimensions (`customer`, `item`, `store`, `date_dim`, `time_dim`, `warehouse`, `promotion`, `web_site`, `web_page`, `reason`, `ship_mode`…) | clé technique `*_sk` (entier) + clé métier `*_id` (16 caractères, ex. `AAAAAAAAAAAAAAAB`) | **uniques**, aucune valeur nulle                                                                                                  |
| `store_sales`                                                                                                                              | `ss_ticket_number` = n° de ticket ; ligne = (`ss_ticket_number`, `ss_item_sk`)            | **non unique** : 4 136 doublons (même article 2 fois sur un ticket, quantité/promo différentes). Aucun doublon de ligne complète. |
| `web_sales`                                                                                                                                | `ws_order_number` + `ws_item_sk`                                                          | **non unique** : 4 076 doublons, même cas                                                                                         |
| `store_returns` / `web_returns`                                                                                                            | (`sr_ticket_number`, `sr_item_sk`) / (`wr_order_number`, `wr_item_sk`)                    | 158 / 150 doublons                                                                                                                |
| `inventory`                                                                                                                                | (`inv_date_sk`, `inv_item_sk`, `inv_warehouse_sk`)                                        | **unique** (0 doublon sur 23,3 M lignes)                                                                                          |
| `product_reviews`                                                                                                                          | `pr_review_sk`                                                                            | unique                                                                                                                            |
| `item_marketprices`                                                                                                                        | `imp_sk`                                                                                  | unique                                                                                                                            |

Un ticket est rattaché à un seul magasin, une seule date et un seul client (vérifié). Les clés `*_sk` des dates (`*_date_sk`) renvoient à `date_dim.d_date_sk` (ex. 36890 = 2001-01-01).

→ **Grain des faits de vente** : 1 ligne = 1 ligne d'article sur un ticket/commande, mais la paire (ticket, article) ne suffit pas comme clé ; il faudra une clé technique (n° de ligne) dans la zone Silver.

---

### 6. Types et valeurs

- Types déclarés : `bigint` (clés), `int` (quantités, compteurs), `decimal(7,2)` (montants), `string`/`char` (libellés), `date`. **Aucun échec de conversion** vers le type déclaré.
- Plusieurs colonnes "date" sont typées `string` (`i_rec_start_date`, `s_rec_start_date`, `pr_review_date`) et `imp_start_date` / `imp_end_date` sont des `bigint` (clé de date, pas une date) → à convertir en Silver.
- Période des ventes : `ss_sold_date_sk` / `ws_sold_date_sk` de **2001-01-01 au 2005-12-13** (≈135 000 lignes/an, 2005 incomplète). Refresh : 2005-12-13 → 2005-12-31.
- Retours : jusqu'au 2008-03-18 (retours postérieurs aux ventes, cohérent).
- Stock : 259 photos **hebdomadaires** (pas de 7 jours) du 2001-01-01 au 2005-12-12, 18 000 articles × 5 entrepôts, quantité 0 à 1 000.
- Livraison web : délai `ws_ship_date_sk − ws_sold_date_sk` de 1 à 120 jours (médiane 60).
- Montants cohérents entre eux (0 écart sur 667 579 lignes) :
  - `ss_ext_sales_price = ss_quantity × ss_sales_price`
  - `ss_net_paid = ss_ext_sales_price − ss_coupon_amt`
  - `ss_net_profit = ss_net_paid − ss_ext_wholesale_cost`
  - `ss_sales_price ≤ ss_list_price`
- `ss_net_profit` négatif sur **74 %** des lignes magasin (61 % web) : marge très souvent négative (données synthétiques).
- Catégories produit : 9 valeurs propres (`Books`, `Electronics`, `Music`…). 12 magasins dans 8 États US, tous `United States`.

---

### 7. Valeurs nulles ou incohérentes

**Nulls (taux faibles, < 0,2 %)** sur la plupart des clés étrangères secondaires : `ss_cdemo_sk`, `ss_hdemo_sk`, `ss_addr_sk`, `ss_promo_sk`, `ws_web_site_sk`, `ws_warehouse_sk`, `ws_ship_mode_sk`, `sr_reason_sk`, `inv_quantity_on_hand` (5 999 lignes)…

**Correction de l'étape B** : dans `store_sales` et `web_sales`, les colonnes `*_sold_date_sk`, `*_item_sk`, `ss_store_sk`, `ss_customer_sk`, `*_ticket/order_number` et `*_quantity` n'ont **aucune valeur nulle**. Les NULL concernent `ws_web_site_sk` (154), `ws_warehouse_sk` (158) et les dimensions démographiques.

**Nulls "normaux"** (à documenter, pas à corriger) :

- `wcs_sales_sk` nul à 90 % (clic sans achat) et `wcs_user_sk` nul à 42 % (visiteur anonyme)
- `t_meal_time` nul à 58 % (heures hors repas)
- `i_rec_end_date`, `s_rec_end_date`, `web_rec_end_date`, `wp_rec_end_date` nuls à 100 % : une seule version par produit/magasin → **pas d'historique (SCD)** malgré les colonnes prévues

**Incohérences** :

- `d_holiday = 'Y'` pour **100 %** des dates → colonne inutilisable
- `s_closed_date_sk` renseigné pour les 12 magasins, avec des dates de fermeture entre 1917 et 2141, parfois **avant l'ouverture** (`s_rec_start_date` en 2000) → aucun magasin n'est réellement fermé sur la période
- `web_open_date_sk` / `web_close_date_sk` : de 1900 à 2198, non réalistes
- `hd_vehicle_count = -1` sur 282 foyers
- `customer` : 1 717 dates de naissance impossibles (ex. 31 février), 322 e-mails en doublon, `c_last_review_date` contient des chaînes aléatoires (`gdMmGdU9`) au lieu de dates
- Libellés aléatoires sans sens métier : `ship_mode` (`sm_type`, `sm_carrier`), `reason.r_reason_desc`, `warehouse.w_warehouse_name`, `promotion.p_promo_name`
- Valeurs constantes `Unknown` : `i_container`, `p_purpose`, `s_geography_class`, `s_division_name`, `s_company_name`, `web_class`
- `store_returns` : 64 retours avec une quantité retournée > quantité vendue
- 3 954 lignes de vente magasin avec `ss_net_paid = 0`
- Chevauchement d'un jour entre `data` et `data_refresh` (2005-12-13 présent dans les deux, avec des tickets différents) → règle de dédoublonnage à définir au chargement
- `data_refresh/store_returns` et `web_returns` contiennent des retours datés de 2001 à 2007 → le refresh n'est pas uniquement "nouvelles dates", il peut corriger l'historique

---

### 9. Domaines absents ou incomplets

| Domaine                      | Constat                                                                                    | Indicateur / question impacté(e)                           |
| ---------------------------- | ------------------------------------------------------------------------------------------ | ---------------------------------------------------------- |
| Stock magasin                | `inventory` ne contient que les **entrepôts** (5), pas les magasins                        | Ruptures / surstock par magasin impossibles (Resp. stocks) |
| Mouvements de stock          | Seulement une mise à jour hebdomadaire, pas d'entrées/sorties ni de commandes fournisseurs | Rotation, réapprovisionnement approximés                   |
| Livraison réelle             | Seule la date d'expédition existe, pas de date de livraison ni de délai promis             | "Retards de livraison" non mesurables directement          |
| Transporteurs                | `ship_mode` a des libellés aléatoires                                                      | Analyse par transporteur illisible                         |
| Motifs de retour             | `r_reason_desc` aléatoire                                                                  | Causes des retours non interprétables (Resp. magasin)      |
| Personnel / horaires         | Pas de planning, seulement `s_number_employees` et `s_hours` (3 valeurs)                   | Ajustement des effectifs par tranche horaire limité        |
| Devise                       | Aucune colonne devise                                                                      | Unité des montants supposée                                |
| Historique produit / magasin | Pas de versions (`rec_end_date` vide)                                                      | Évolution des prix / attributs non suivie                  |
