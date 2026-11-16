# Inventaire des sources

J'ai utilisé le script `preuves/explorer_donnees.py`. Les résultats complets sont dans `preuves/inventaire_fichiers.csv` et `preuves/inventaire_colonnes.csv`.

## 1. Le kit de données

| Information | Valeur |
|---|---|
| Nom | `retail_project.zip` |
| Version | Non communiquée |
| Provenance | Donné par le formateur |
| Date | Non communiquée |
| Format | Fichiers texte `.dat`, colonnes séparées par `|`, sans ligne de titres |
| Volume | 283 Mo compressé, environ 1 Go décompressé |
| Nombre de fichiers | 34 : 23 dans `data/` et 11 dans `data_refresh/` |
| Outil de génération | Non communiqué |

## 2. Les fichiers de `data/`

Chemin : `retail_project/data/<nom>/<nom>.dat`

| Domaine | Fichier | Taille | Lignes | Colonnes | Identifiant |
|---|---|---|---|---|---|
| Ventes magasin | `store_sales` | 88 Mo | 667 579 | 23 | ticket + produit |
| Ventes web | `web_sales` | 128 Mo | 668 052 | 34 | commande + produit |
| Retours magasin | `store_returns` | 4 Mo | 37 902 | 20 | ticket + produit |
| Retours web | `web_returns` | 5 Mo | 38 487 | 24 | commande + produit |
| Motifs de retour | `reason` | 3 Ko | 35 | 3 | `r_reason_sk` |
| Produits | `item` | 6,5 Mo | 17 820 | 22 | `i_item_sk` |
| Prix des concurrents | `item_marketprices` | 4 Mo | 89 100 | 6 | `imp_sk` |
| Promotions | `promotion` | 45 Ko | 300 | 19 | `p_promo_sk` |
| Clients | `customer` | 19 Mo | 99 000 | 18 | `c_customer_sk` |
| Adresses | `customer_address` | 8 Mo | 49 500 | 13 | `ca_address_sk` |
| Profils clients | `customer_demographics` | 74 Mo | 1 920 800 | 9 | `cd_demo_sk` |
| Profils foyers | `household_demographics` | 151 Ko | 7 200 | 5 | `hd_demo_sk` |
| Tranches de revenus | `income_band` | 327 o | 20 | 3 | `ib_income_band_sk` |
| Magasins | `store` | 3 Ko | 12 | 29 | `s_store_sk` |
| Entrepôts | `warehouse` | 584 o | 5 | 14 | `w_warehouse_sk` |
| Stocks | `inventory` | 405 Mo | 23 255 100 | 4 | date + produit + entrepôt |
| Clics web | `web_clickstreams` | 170 Mo | 6 770 550 | 6 | aucun |
| Pages web | `web_page` | 8 Ko | 60 | 14 | `wp_web_page_sk` |
| Sites web | `web_site` | 9 Ko | 30 | 26 | `web_site_sk` |
| Livraison | `ship_mode` | 1 Ko | 20 | 6 | `sm_ship_mode_sk` |
| Avis produits | `product_reviews` | 54 Mo | 89 991 | 8 | `pr_review_sk` |
| Calendrier | `date_dim` | 15 Mo | 109 573 | 28 | `d_date_sk` |
| Heures | `time_dim` | 5 Mo | 86 400 | 10 | `t_time_sk` |

Il n'y a aucun doublon dans les identifiants des tables de référence (produits, clients, magasins…).

## 3. Les fichiers de `data_refresh/`

Ce sont les mêmes tables, mais avec **de nouvelles données à ajouter** : nouveaux clients, nouveaux produits, ventes de la fin décembre 2005.

| Fichier | Lignes |
|---|---|
| `customer` | 1 000 |
| `customer_address` | 500 |
| `item` | 180 |
| `item_marketprices` | 900 |
| `inventory` | 234 900 |
| `store_sales` | 6 632 |
| `store_returns` | 426 |
| `web_sales` | 6 879 |
| `web_returns` | 400 |
| `web_clickstreams` | 68 988 |
| `product_reviews` | 909 |

## 4. Noms des colonnes

⚠️ Les fichiers n'ont pas de ligne de titres. J'ai pris les noms dans le schéma officiel de TPCx-BB et j'ai vérifié que le nombre de colonnes correspond. Statut : **Déduit**.

| Fichier | Colonnes |
|---|---|
| `store_sales` | ss_sold_date_sk, ss_sold_time_sk, ss_item_sk, ss_customer_sk, ss_cdemo_sk, ss_hdemo_sk, ss_addr_sk, ss_store_sk, ss_promo_sk, ss_ticket_number, ss_quantity, ss_wholesale_cost, ss_list_price, ss_sales_price, ss_ext_discount_amt, ss_ext_sales_price, ss_ext_wholesale_cost, ss_ext_list_price, ss_ext_tax, ss_coupon_amt, ss_net_paid, ss_net_paid_inc_tax, ss_net_profit |
| `web_sales` | ws_sold_date_sk, ws_sold_time_sk, ws_ship_date_sk, ws_item_sk, ws_bill_customer_sk, ws_bill_cdemo_sk, ws_bill_hdemo_sk, ws_bill_addr_sk, ws_ship_customer_sk, ws_ship_cdemo_sk, ws_ship_hdemo_sk, ws_ship_addr_sk, ws_web_page_sk, ws_web_site_sk, ws_ship_mode_sk, ws_warehouse_sk, ws_promo_sk, ws_order_number, ws_quantity, ws_wholesale_cost, ws_list_price, ws_sales_price, ws_ext_discount_amt, ws_ext_sales_price, ws_ext_wholesale_cost, ws_ext_list_price, ws_ext_tax, ws_coupon_amt, ws_ext_ship_cost, ws_net_paid, ws_net_paid_inc_tax, ws_net_paid_inc_ship, ws_net_paid_inc_ship_tax, ws_net_profit |
| `store_returns` | sr_returned_date_sk, sr_return_time_sk, sr_item_sk, sr_customer_sk, sr_cdemo_sk, sr_hdemo_sk, sr_addr_sk, sr_store_sk, sr_reason_sk, sr_ticket_number, sr_return_quantity, sr_return_amt, sr_return_tax, sr_return_amt_inc_tax, sr_fee, sr_return_ship_cost, sr_refunded_cash, sr_reversed_charge, sr_store_credit, sr_net_loss |
| `web_returns` | wr_returned_date_sk, wr_returned_time_sk, wr_item_sk, wr_refunded_customer_sk, wr_refunded_cdemo_sk, wr_refunded_hdemo_sk, wr_refunded_addr_sk, wr_returning_customer_sk, wr_returning_cdemo_sk, wr_returning_hdemo_sk, wr_returning_addr_sk, wr_web_page_sk, wr_reason_sk, wr_order_number, wr_return_quantity, wr_return_amt, wr_return_tax, wr_return_amt_inc_tax, wr_fee, wr_return_ship_cost, wr_refunded_cash, wr_reversed_charge, wr_account_credit, wr_net_loss |
| `reason` | r_reason_sk, r_reason_id, r_reason_desc |
| `item` | i_item_sk, i_item_id, i_rec_start_date, i_rec_end_date, i_item_desc, i_current_price, i_wholesale_cost, i_brand_id, i_brand, i_class_id, i_class, i_category_id, i_category, i_manufact_id, i_manufact, i_size, i_formulation, i_color, i_units, i_container, i_manager_id, i_product_name |
| `item_marketprices` | imp_sk, imp_item_sk, imp_competitor, imp_competitor_price, imp_start_date, imp_end_date |
| `promotion` | p_promo_sk, p_promo_id, p_start_date_sk, p_end_date_sk, p_item_sk, p_cost, p_response_target, p_promo_name, p_channel_dmail, p_channel_email, p_channel_catalog, p_channel_tv, p_channel_radio, p_channel_press, p_channel_event, p_channel_demo, p_channel_details, p_purpose, p_discount_active |
| `customer` | c_customer_sk, c_customer_id, c_current_cdemo_sk, c_current_hdemo_sk, c_current_addr_sk, c_first_shipto_date_sk, c_first_sales_date_sk, c_salutation, c_first_name, c_last_name, c_preferred_cust_flag, c_birth_day, c_birth_month, c_birth_year, c_birth_country, c_login, c_email_address, c_last_review_date |
| `customer_address` | ca_address_sk, ca_address_id, ca_street_number, ca_street_name, ca_street_type, ca_suite_number, ca_city, ca_county, ca_state, ca_zip, ca_country, ca_gmt_offset, ca_location_type |
| `customer_demographics` | cd_demo_sk, cd_gender, cd_marital_status, cd_education_status, cd_purchase_estimate, cd_credit_rating, cd_dep_count, cd_dep_employed_count, cd_dep_college_count |
| `household_demographics` | hd_demo_sk, hd_income_band_sk, hd_buy_potential, hd_dep_count, hd_vehicle_count |
| `income_band` | ib_income_band_sk, ib_lower_bound, ib_upper_bound |
| `store` | s_store_sk, s_store_id, s_rec_start_date, s_rec_end_date, s_closed_date_sk, s_store_name, s_number_employees, s_floor_space, s_hours, s_manager, s_market_id, s_geography_class, s_market_desc, s_market_manager, s_division_id, s_division_name, s_company_id, s_company_name, s_street_number, s_street_name, s_street_type, s_suite_number, s_city, s_county, s_state, s_zip, s_country, s_gmt_offset, s_tax_precentage |
| `warehouse` | w_warehouse_sk, w_warehouse_id, w_warehouse_name, w_warehouse_sq_ft, w_street_number, w_street_name, w_street_type, w_suite_number, w_city, w_county, w_state, w_zip, w_country, w_gmt_offset |
| `inventory` | inv_date_sk, inv_item_sk, inv_warehouse_sk, inv_quantity_on_hand |
| `web_clickstreams` | wcs_click_date_sk, wcs_click_time_sk, wcs_sales_sk, wcs_item_sk, wcs_web_page_sk, wcs_user_sk |
| `web_page` | wp_web_page_sk, wp_web_page_id, wp_rec_start_date, wp_rec_end_date, wp_creation_date_sk, wp_access_date_sk, wp_autogen_flag, wp_customer_sk, wp_url, wp_type, wp_char_count, wp_link_count, wp_image_count, wp_max_ad_count |
| `web_site` | web_site_sk, web_site_id, web_rec_start_date, web_rec_end_date, web_name, web_open_date_sk, web_close_date_sk, web_class, web_manager, web_mkt_id, web_mkt_class, web_mkt_desc, web_market_manager, web_company_id, web_company_name, web_street_number, web_street_name, web_street_type, web_suite_number, web_city, web_county, web_state, web_zip, web_country, web_gmt_offset, web_tax_percentage |
| `ship_mode` | sm_ship_mode_sk, sm_ship_mode_id, sm_type, sm_code, sm_carrier, sm_contract |
| `product_reviews` | pr_review_sk, pr_review_date, pr_review_time, pr_review_rating, pr_item_sk, pr_user_sk, pr_order_sk, pr_review_content |
| `date_dim` | d_date_sk, d_date_id, d_date, d_month_seq, d_week_seq, d_quarter_seq, d_year, d_dow, d_moy, d_dom, d_qoy, d_fy_year, d_fy_quarter_seq, d_fy_week_seq, d_day_name, d_quarter_name, d_holiday, d_weekend, d_following_holiday, d_first_dom, d_last_dom, d_same_day_ly, d_same_day_lq, d_current_day, d_current_week, d_current_month, d_current_quarter, d_current_year |
| `time_dim` | t_time_sk, t_time_id, t_time, t_hour, t_minute, t_second, t_am_pm, t_shift, t_sub_shift, t_meal_time |

## 5. Types de données

- Les identifiants (colonnes en `_sk`) : nombres entiers.
- Les prix et montants : nombres décimaux.
- Les dates : `AAAA-MM-JJ`.
- Dans les ventes, la date est un numéro qui renvoie au calendrier `date_dim` (par exemple, 36890 = 01/01/2001).
- Le reste : du texte.

## 6. Valeurs vides et problèmes

| Fichier | Ce que j'ai trouvé |
|---|---|
| `store_sales`, `web_sales` | Presque aucune valeur vide (moins de 0,1 %) |
| `web_clickstreams` | 90 % des clics n'ont pas de vente, 42 % n'ont pas d'utilisateur |
| `item`, `store`, `web_page`, `web_site` | La date de fin est toujours vide |
| `customer`, `customer_address` | Toutes les valeurs ont des espaces en trop |
| `customer` | `c_last_review_date` contient du texte au lieu d'une date : inutilisable |
| Retours | Certains sont datés jusqu'en 2008, alors que les ventes s'arrêtent en 2005 |

## 7. Périodes couvertes

| Données | Période |
|---|---|
| Ventes | 01/01/2001 → 13/12/2005 (31/12/2005 avec `data_refresh`) |
| Retours | 2001 → 2008 |
| Stocks | 2001 → 2005, environ un relevé par semaine |
| Clics web | 2001 → 2005 |
| Avis | 2001 → 2006 |

## 8. Ce qui manque

| Domaine | Constat |
|---|---|
| Stock des magasins | Absent : le stock est seulement par entrepôt |
| Sessions web | Absent : on ne sait pas quels clics font partie d'une même visite |
| Objectifs de vente | Absent |
| Coûts (loyers, salaires) | Absent |
| Documentation des colonnes | Absente |
