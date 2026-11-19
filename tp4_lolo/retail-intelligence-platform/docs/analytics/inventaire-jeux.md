# Inventaire des jeux de données utilisés (UC-08, étape 1)

Les jeux de données viennent du TP3 (UC-06), sans copie : ils sont lus directement dans `tp3_lolo/retail-intelligence-platform/data/`. Le détail généré par le notebook se trouve dans `analytics/outputs/inventaire_jeux.csv`.

| Jeu de données | Zone | Format | Lignes | Granularité (clé vérifiée unique) | Usage prévu |
|---|---|---|---|---|---|
| `silver/sales_enriched` | Silver | Parquet, 10 fichiers, partitionné par `annee` (6,2 Mo) | 66 593 | une ligne d'article d'un ticket (`ticket_id + produit_sk + ligne_ticket`) | KPI recalculés, statistiques descriptives, distribution des tickets |
| `gold/ca_annuel` | Gold | Parquet, 1 fichier | 5 | une année (`annee`) | Recoupement des KPI annuels |
| `gold/ca_mensuel` | Gold | Parquet, 1 fichier | 60 | un mois (`annee + mois`) | Analyse A1 et visualisation V1 |
| `gold/ca_marge_par_categorie` | Gold | Parquet, 1 fichier | 9 | une catégorie (`categorie_id`) | Analyse A2 et visualisation V2 |
| `gold/ca_marge_par_magasin` | Gold | Parquet, 1 fichier | 12 | un magasin (`magasin_sk`) | Analyse A3 et visualisation V3 |
| `gold/top10_produits` | Gold | Parquet, 1 fichier | 10 | un produit | Complément de l'analyse A2 |

## Provenance

| Jeu | Source (colonnes de provenance écrites au TP3) | Traitement |
|---|---|---|
| `sales_enriched` | `store_sales.dat` TPCx-BB → échantillon `data/samples/store_sales_echantillon.dat` (10 % des tickets) → Silver `sales`, joint à `products`, `stores` et `dates` | `transformations/enrichment/enrichissement_ventes.ipynb` |
| Tables Gold | `silver/sales_enriched` (colonne `_sources_silver`) | `transformations/aggregation/agregations_gold.ipynb` |

Le format est vérifié par la signature `PAR1` en début et en fin de chaque fichier. Le schéma est relu par Spark : voir `printSchema()` dans le notebook et `tp3_lolo/.../docs/data-dictionary/schemas/`.

## Contrôles qualité disponibles (rapport TP3)

| Jeu | Contrôles TP3 | Alertes utiles pour l'analyse |
|---|---|---|
| `sales` / `sales_enriched` | 35 + 17 OK, 9 + 1 alertes, 0 KO | 74 % de lignes à marge négative (donc marge non retenue) ; 356 lignes à prix nul ; échantillon de 10 % ; décembre 2005 partiel |
| `gold.ca_mensuel` | 6 OK, 1 alerte | décembre 2005 incomplet (colonne `mois_incomplet`) |
| Autres tables Gold | 6 à 8 OK, 0 alerte | somme du CA = CA Silver (115 752 176,68) |

## Pourquoi ces jeux ?

* **Silver `sales_enriched`** : c'est le grain le plus fin, déjà joint aux dimensions. Il permet de recalculer tous les KPI et de descendre au niveau du ticket.
* **Gold** : ce sont les agrégats prêts pour les questions métier, en petit volume (5 à 60 lignes), donc directement utilisables pour les graphiques.

## Ce qui manque

* **`web_sales`** n'a pas été transformé au TP3. Il n'existe donc pas de jeu Silver ou Gold « web », et la question « part du CA magasin / web » n'est pas traitable. Pour la traiter, il faudrait appliquer le même nettoyage à `web_sales` (règles R1 à R8) et ajouter une colonne `canal` dans une table Gold commune.
