# Inventaire des jeux de données utilisés – TP Jour 4, UC-08 (J4-01)

Comme au Jour 3, on a **deux chaînes** qui analysent les mêmes ventes :

- **Notebook principal** (Lorenzo) : `analytics/notebooks/TP4_Retail_Intelligence.ipynb`. Il lit les données Silver et Gold du pipeline des notebooks du Jour 3 (`data/silver/`, `data/gold/`), sur un **échantillon de 10 % des tickets**, avec les dates, les magasins et les produits. C'est la chaîne principale.
- **Notebook HDFS** (Noah) : `analytics/notebooks/TP4_HDFS_fichier_complet.ipynb`. Il lit les données des scripts PySpark du Jour 3 dans HDFS, sur le **fichier complet**, mais sans les dates. Il sert à vérifier que l'échantillon donne les mêmes résultats.

Le détail généré par le notebook principal est dans `analytics/outputs/inventaire_jeux.csv`.

## 1. Jeux du notebook principal (échantillon de 10 %)

| Jeu de données | Zone | Format | Lignes | Granularité (clé vérifiée unique) | Usage prévu |
|---|---|---|---|---|---|
| `silver/sales_enriched` | Silver | Parquet, 10 fichiers, rangé par `annee` (6,2 Mo) | 66 593 | une ligne d'article d'un ticket (`ticket_id + produit_sk + ligne_ticket`) | KPI recalculés, statistiques, distribution des tickets |
| `gold/ca_annuel` | Gold | Parquet, 1 fichier | 5 | une année (`annee`) | Vérification des KPI annuels |
| `gold/ca_mensuel` | Gold | Parquet, 1 fichier | 60 | un mois (`annee + mois`) | Analyse A1 et graphique V1 |
| `gold/ca_marge_par_categorie` | Gold | Parquet, 1 fichier | 9 | une catégorie (`categorie_id`) | Analyse A2 et graphique V2 |
| `gold/ca_marge_par_magasin` | Gold | Parquet, 1 fichier | 12 | un magasin (`magasin_sk`) | Analyse A3 et graphique V3 |
| `gold/top10_produits` | Gold | Parquet, 1 fichier | 10 | un produit | Complément de l'analyse A2 |

**Provenance**

| Jeu | Source | Traitement (Jour 3) |
|---|---|---|
| `sales_enriched` | `store_sales.dat` TPCx-BB → échantillon `data/samples/store_sales_echantillon.dat` (10 % des tickets) → Silver `sales`, joint à `products`, `stores` et `dates` | `notebooks/transformations/enrichissement_ventes.ipynb` |
| Tables Gold | `silver/sales_enriched` (colonne `_sources_silver`) | `notebooks/transformations/agregations_gold.ipynb` |

Le format est vérifié par la signature `PAR1` au début et à la fin de chaque fichier Parquet. Le schéma est relu par Spark (`printSchema()` dans le notebook, et `docs/data-dictionary/schemas/`).

## 2. Jeux du notebook HDFS (fichier complet)

| Jeu de données | Zone | Format | Lignes | Granularité (vérifiée) | Usage prévu |
|---|---|---|---|---|---|
| `/retail-lake/silver/store_sales` | Silver | Parquet dans HDFS (38,7 Mo) | 667 579 | une ligne de ticket. 89 100 tickets, et un ticket appartient à un seul magasin | KPI, statistiques, analyse par magasin, graphique H2 |
| `/retail-lake/silver/item` | Silver | Parquet dans HDFS (3,5 Mo) | 17 820 | un produit (`i_item_sk` unique) | Nombre de produits par catégorie |
| `/retail-lake/gold/ca_par_categorie` | Gold | Parquet dans HDFS (3,0 Ko) | 9 | une catégorie | Analyse par catégorie, graphique H1 |

- **Provenance** : zone `raw` de HDFS (déposée au Jour 2), nettoyée par `transformations/silver/01_silver.py`, puis agrégée par `transformations/gold/02_gold.py`.
- **Ce qui manque dans cette chaîne** : `date_dim` (pas d'analyse par mois) et `store` (les magasins n'ont qu'un numéro, de 0 à 11).

## 3. Contrôles qualité disponibles (rapports du Jour 3)

| Jeu | Contrôles du Jour 3 | Alertes utiles pour l'analyse |
|---|---|---|
| `sales` / `sales_enriched` | 35 + 17 OK, 9 + 1 alertes, 0 KO | 74 % de lignes à marge négative (donc marge non retenue) ; 356 lignes à prix nul ; échantillon de 10 % ; décembre 2005 partiel |
| `gold/ca_mensuel` | 6 OK, 1 alerte | décembre 2005 incomplet (colonne `mois_incomplet`) |
| Autres tables Gold | 6 à 8 OK, 0 alerte | somme du CA = CA Silver (115 752 176,68) |
| HDFS : `silver/store_sales`, `silver/item`, `gold/ca_par_categorie` | 36 contrôles : 32 OK, 4 ATTENTION, 0 KO | ventes à prix 0 (3 324), marges négatives, produits vendus à perte ; CA Gold = CA Silver (1 150 529 586,37) |

## 4. Pourquoi ces jeux ?

- **Silver `sales_enriched`** : c'est le niveau le plus fin, déjà joint aux produits, aux magasins et aux dates. Il permet de recalculer tous les KPI et de descendre au niveau du ticket.
- **Gold** : ce sont des résultats déjà regroupés pour les questions métier, en petit volume (5 à 60 lignes), donc directement utilisables pour les graphiques.
- **HDFS (fichier complet)** : il permet de vérifier que l'échantillon ne déforme pas les résultats.

## 5. Ce qui manque

- **`web_sales`** n'a pas été transformée au Jour 3 : il n'y a pas de jeu « web ». La question « part du CA magasin / web » n'est donc pas traitable. Pour la traiter, il faudrait appliquer le même nettoyage à `web_sales` (règles R1 à R8) et ajouter une colonne `canal` dans une table Gold commune.
- **`store_returns`** n'a pas été transformée : pas de taux de retour.
- **Chaîne HDFS** : pas de `date_dim` ni de `store`.

## 6. Données complémentaires

Aucune : toutes les données utilisées viennent de TPCx-BB.
