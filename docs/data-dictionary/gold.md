# Données Gold - TP Jour 3, Étape 7

La zone Gold contient des jeux de données **orientés analyse et décision**.
Chacun répond à une question métier choisie au Jour 1
(`01_UC01_besoin_exploration/UC01_questions_decisionnelles.md`), avec les
formules du dictionnaire de KPI (`UC01_dictionnaire_KPI.md`).

- Traitement : `notebooks/transformations/agregations_gold.ipynb`
- Bilan : `outputs/bilan_gold.json`
- Résultats commentés : `docs/transformations/transformations_resultats.md`

## Vue d'ensemble

```
data/silver/sales_enriched/  (1 ligne = 1 produit dans 1 ticket)
        |
        +--> gold/ca_mensuel/              1 ligne = 1 mois       (60)
        +--> gold/ca_annuel/               1 ligne = 1 annee      (5)
        +--> gold/ca_marge_par_categorie/  1 ligne = 1 categorie  (9)
        +--> gold/top10_produits/          1 ligne = 1 produit    (10)
        +--> gold/ca_marge_par_magasin/    1 ligne = 1 magasin    (12)
        +--> gold/taux_remise_mensuel/     1 ligne = 1 mois       (60)
```

| Table Gold | Question métier | Profil |
|---|---|---|
| `ca_mensuel` | Comment évolue le CA chaque mois, et par rapport à l'année d'avant ? | P1 Direction générale |
| `ca_annuel` | Même question, vue par année | P1 Direction générale |
| `ca_marge_par_categorie` | Quelles catégories génèrent le plus de CA ? Quelle marge fait chacune ? | P4 Direction commerciale, P2 Contrôleur de gestion |
| `top10_produits` | Quels produits génèrent le plus de CA ? | P4 Direction commerciale |
| `ca_marge_par_magasin` | Quelle marge fait chaque magasin ? | P2 Contrôleur de gestion |
| `taux_remise_mensuel` | Quel est le niveau des remises, et augmente-t-il ? | P2 Contrôleur de gestion |

## Règles communes

- **Nommage** : nom métier en français, en `snake_case`, sous la forme
  `<indicateur>_par_<dimension>` ou `<indicateur>_<période>`. Le français est
  choisi parce que ces tables sont lues par les équipes métier.
- **Format** : Parquet. Les montants sont en `decimal`, arrondis à 2 décimales.
- **Les ratios sont calculés à partir des sommes** (Σ marge ÷ Σ CA), jamais
  en faisant la moyenne de taux calculés ligne par ligne. Sinon, une ligne de
  1 € pèserait autant qu'une ligne de 10 000 €.
- **Toutes les lignes Silver sont incluses**, y compris les prix à 0 et les
  marges négatives : ce sont des ventes réelles (règle R7 de l'étape 4).
- **Provenance** : `_sources_silver`, `_traitement` et `_date_traitement`
  sur chaque ligne.
- **Contrôle** : la somme des CA de `ca_mensuel`, `ca_annuel`,
  `ca_marge_par_categorie` et `ca_marge_par_magasin` est égale au CA total
  Silver (115 752 176,68), avec un écart de 0,00. Aucun CA ni aucune marge
  n'est vide.

## Limites communes

- Les ventes viennent d'un **échantillon de 10 % des tickets** : les montants sont environ 10 fois plus petits que la réalité. Les taux, parts, paniers moyens et évolutions restent représentatifs.
- **Magasins seulement** : le web (`web_sales`) n'est pas inclus.
- **Retours non déduits** : `store_returns` n'est pas traité.
- La **devise** n'est pas indiquée dans les données : on suppose l'euro.
- La **marge est négative** sur environ 74 % des lignes, à cause des données générées par TPCx-BB. Elle permet de comparer, pas de juger la rentabilité réelle.

## 1. `gold/ca_mensuel/` - Synthèse des ventes par mois

| Élément | Description |
|---|---|
| Nom | Synthèse des ventes par mois |
| Finalité métier | Suivre l'évolution du CA chaque mois et la comparer au même mois de l'année précédente, pour revoir les objectifs et réagir à une baisse. |
| Question du Jour 1 | P1 Direction générale : « Comment évolue le chiffre d'affaires chaque mois et par rapport à l'année d'avant ? » |
| Sources | `data/silver/sales_enriched/` (vérifié par `notebooks/quality/controles_silver.ipynb`), construit à partir de `sales`, `dates`, `products` et `stores` |
| Granularité | 1 ligne = 1 mois (`annee`, `mois`), de janvier 2001 à décembre 2005 |
| Clé | (`annee`, `mois`) |
| Dimensions | Période (année, mois) |
| Mesures | `chiffre_affaires`, `nb_transactions`, `quantites_vendues`, `marge`, `remises`, `montant_catalogue`, `nb_lignes`, `panier_moyen`, `taux_marge_pct`, `taux_remise_pct`, `ca_annee_precedente`, `evolution_ca_pct` |
| Lignes | 60 |
| Usage | Courbe du CA mensuel ; tableau de bord de la direction |
| Schéma | `docs/data-dictionary/schemas/gold_ca_mensuel.json` |

**Colonnes et règles de calcul**

| Colonne | Type | Rôle | Description | Règle de calcul |
|---|---|---|---|---|
| `annee` | int | Dimension | Année de la vente | `annee` de `sales_enriched` |
| `mois` | int | Dimension | Mois de la vente (1 à 12) | `mois` de `sales_enriched` |
| `chiffre_affaires` | decimal(18,2) | Mesure | KPI-01 : chiffre d'affaires hors taxes, remises et coupons déduits | Σ `montant_net_paye` |
| `nb_transactions` | bigint | Mesure | KPI-02 : nombre d'achats | Nombre de `ticket_id` distincts |
| `quantites_vendues` | bigint | Mesure | KPI-04 : articles vendus | Σ `quantite` |
| `marge` | decimal(18,2) | Mesure | Marge totale (peut être négative) | Σ `marge` |
| `remises` | decimal(18,2) | Mesure | Remises accordées | Σ `montant_remise` |
| `montant_catalogue` | decimal(18,2) | Mesure | Montant au prix catalogue, avant remise | Σ `montant_catalogue` |
| `nb_lignes` | bigint | Mesure | Lignes de vente agrégées (sert au contrôle) | Nombre de lignes |
| `panier_moyen` | decimal(19,2) | Mesure calculée | KPI-03 : dépense moyenne par achat | `chiffre_affaires` ÷ `nb_transactions` |
| `taux_marge_pct` | decimal(25,2) | Mesure calculée | Taux de marge en % | `marge` ÷ `chiffre_affaires` × 100 |
| `taux_remise_pct` | decimal(25,2) | Mesure calculée | KPI-05 : taux de remise en % | `remises` ÷ `montant_catalogue` × 100 |
| `ca_annee_precedente` | decimal(18,2) | Mesure calculée | CA du même mois l'année d'avant | `chiffre_affaires` de (annee − 1, même mois) |
| `evolution_ca_pct` | decimal(26,2) | Mesure calculée | KPI-06 : évolution du CA en % | (CA − CA N-1) ÷ CA N-1 × 100 ; vide s'il n'y a pas d'année précédente |
| `mois_incomplet` | boolean | Indicateur | Mois dont les données sont partielles | Vrai pour décembre 2005 (dernière vente le 13/12/2005) |
| `_sources_silver` | string | Provenance | Jeu Silver utilisé | `silver/sales_enriched` |
| `_traitement` | string | Provenance | Notebook qui a produit la table | `agregations_gold.ipynb` |
| `_date_traitement` | timestamp | Provenance | Date et heure du calcul | Horodatage de l'écriture |

**Limites d'interprétation**

- L'évolution est vide pour les 12 mois de 2001, faute d'année précédente.
- Décembre 2005 est **incomplet** (`mois_incomplet` = vrai) : sa baisse n'a pas de sens commercial.
- Une évolution mensuelle dépend des saisons et des calendriers (nombre de week-ends dans le mois).
- Et les limites communes à toutes les tables Gold (voir plus haut).

## 2. `gold/ca_annuel/` - Synthèse des ventes par année

| Élément | Description |
|---|---|
| Nom | Synthèse des ventes par année |
| Finalité métier | Donner la vue annuelle du CA, de la marge et des remises, pour le bilan de l'année et les objectifs. |
| Question du Jour 1 | P1 Direction générale : évolution du chiffre d'affaires par rapport à l'année d'avant |
| Sources | `data/silver/sales_enriched/` (vérifié par `notebooks/quality/controles_silver.ipynb`), construit à partir de `sales`, `dates`, `products` et `stores` |
| Granularité | 1 ligne = 1 année (2001 à 2005) |
| Clé | `annee` |
| Dimensions | Année |
| Mesures | `chiffre_affaires`, `nb_transactions`, `quantites_vendues`, `marge`, `remises`, `montant_catalogue`, `nb_lignes`, `panier_moyen`, `taux_marge_pct`, `taux_remise_pct`, `evolution_ca_pct` |
| Lignes | 5 |
| Usage | Bilan annuel ; comparaison d'une année à l'autre |
| Schéma | `docs/data-dictionary/schemas/gold_ca_annuel.json` |

**Colonnes et règles de calcul**

| Colonne | Type | Rôle | Description | Règle de calcul |
|---|---|---|---|---|
| `annee` | int | Dimension | Année de la vente | `annee` de `sales_enriched` |
| `chiffre_affaires` | decimal(18,2) | Mesure | KPI-01 : chiffre d'affaires hors taxes, remises et coupons déduits | Σ `montant_net_paye` |
| `nb_transactions` | bigint | Mesure | KPI-02 : nombre d'achats | Nombre de `ticket_id` distincts |
| `quantites_vendues` | bigint | Mesure | KPI-04 : articles vendus | Σ `quantite` |
| `marge` | decimal(18,2) | Mesure | Marge totale (peut être négative) | Σ `marge` |
| `remises` | decimal(18,2) | Mesure | Remises accordées | Σ `montant_remise` |
| `montant_catalogue` | decimal(18,2) | Mesure | Montant au prix catalogue, avant remise | Σ `montant_catalogue` |
| `nb_lignes` | bigint | Mesure | Lignes de vente agrégées (sert au contrôle) | Nombre de lignes |
| `panier_moyen` | decimal(19,2) | Mesure calculée | KPI-03 : dépense moyenne par achat | `chiffre_affaires` ÷ `nb_transactions` |
| `taux_marge_pct` | decimal(25,2) | Mesure calculée | Taux de marge en % | `marge` ÷ `chiffre_affaires` × 100 |
| `taux_remise_pct` | decimal(25,2) | Mesure calculée | KPI-05 : taux de remise en % | `remises` ÷ `montant_catalogue` × 100 |
| `evolution_ca_pct` | decimal(26,2) | Mesure calculée | KPI-06 : évolution du CA en % | (CA − CA N-1) ÷ CA N-1 × 100 ; vide s'il n'y a pas d'année précédente |
| `_sources_silver` | string | Provenance | Jeu Silver utilisé | `silver/sales_enriched` |
| `_traitement` | string | Provenance | Notebook qui a produit la table | `agregations_gold.ipynb` |
| `_date_traitement` | timestamp | Provenance | Date et heure du calcul | Horodatage de l'écriture |

**Limites d'interprétation**

- 2005 ne couvre que jusqu'au 13/12 : la baisse de -7,21 % est en partie due à ce mois incomplet.
- L'évolution est vide pour 2001.
- Et les limites communes à toutes les tables Gold (voir plus haut).

## 3. `gold/ca_marge_par_categorie/` - Synthèse des ventes et de la marge par catégorie

| Élément | Description |
|---|---|
| Nom | Synthèse des ventes et de la marge par catégorie |
| Finalité métier | Repérer les catégories qui font le plus de CA et celles dont la marge est la plus faible, pour décider de leur mise en avant ou ajuster les budgets. |
| Question du Jour 1 | P4 Direction commerciale : « Quels produits et quelles catégories génèrent le plus de chiffre d'affaires ? » ; P2 Contrôleur de gestion : « Quelle marge fait chaque catégorie ? » |
| Sources | `data/silver/sales_enriched/` (vérifié par `notebooks/quality/controles_silver.ipynb`), construit à partir de `sales`, `dates`, `products` et `stores` |
| Granularité | 1 ligne = 1 catégorie de produits (9 catégories), toute la période |
| Clé | `categorie_id` |
| Dimensions | Catégorie |
| Mesures | `chiffre_affaires`, `nb_transactions`, `quantites_vendues`, `marge`, `remises`, `montant_catalogue`, `nb_lignes`, `nb_produits_vendus`, `panier_moyen`, `taux_marge_pct`, `taux_remise_pct`, `part_ca_pct` |
| Lignes | 9 |
| Usage | Classement des catégories ; arbitrage commercial |
| Schéma | `docs/data-dictionary/schemas/gold_ca_marge_par_categorie.json` |

**Colonnes et règles de calcul**

| Colonne | Type | Rôle | Description | Règle de calcul |
|---|---|---|---|---|
| `categorie_id` | int | Dimension | Code de la catégorie | `categorie_id` |
| `categorie` | string | Dimension | Catégorie de produits | `categorie` |
| `chiffre_affaires` | decimal(18,2) | Mesure | KPI-01 : chiffre d'affaires hors taxes, remises et coupons déduits | Σ `montant_net_paye` |
| `nb_transactions` | bigint | Mesure | KPI-02 : nombre d'achats | Nombre de `ticket_id` distincts |
| `quantites_vendues` | bigint | Mesure | KPI-04 : articles vendus | Σ `quantite` |
| `marge` | decimal(18,2) | Mesure | Marge totale (peut être négative) | Σ `marge` |
| `remises` | decimal(18,2) | Mesure | Remises accordées | Σ `montant_remise` |
| `montant_catalogue` | decimal(18,2) | Mesure | Montant au prix catalogue, avant remise | Σ `montant_catalogue` |
| `nb_lignes` | bigint | Mesure | Lignes de vente agrégées (sert au contrôle) | Nombre de lignes |
| `nb_produits_vendus` | bigint | Mesure | Produits différents vendus | Nombre de `produit_sk` distincts |
| `panier_moyen` | decimal(19,2) | Mesure calculée | KPI-03 : dépense moyenne par achat | `chiffre_affaires` ÷ `nb_transactions` |
| `taux_marge_pct` | decimal(25,2) | Mesure calculée | Taux de marge en % | `marge` ÷ `chiffre_affaires` × 100 |
| `taux_remise_pct` | decimal(25,2) | Mesure calculée | KPI-05 : taux de remise en % | `remises` ÷ `montant_catalogue` × 100 |
| `part_ca_pct` | decimal(25,2) | Mesure calculée | Part du CA total en % | `chiffre_affaires` ÷ Σ `chiffre_affaires` de toutes les lignes × 100 |
| `_sources_silver` | string | Provenance | Jeu Silver utilisé | `silver/sales_enriched` |
| `_traitement` | string | Provenance | Notebook qui a produit la table | `agregations_gold.ipynb` |
| `_date_traitement` | timestamp | Provenance | Date et heure du calcul | Horodatage de l'écriture |

**Limites d'interprétation**

- `nb_transactions` compte les tickets qui contiennent **au moins un** produit de la catégorie : un ticket avec plusieurs catégories est compté dans chacune. La somme des transactions n'est donc pas égale au total, et `panier_moyen` est la dépense **dans la catégorie** par ticket concerné.
- Les catégories n'ont pas le même nombre de produits (Music : 7 164, Toys & Games : 348) : une part de CA élevée vient d'abord de la taille de l'offre.
- Additionner des quantités de produits très différents a peu de sens (KPI-04).
- Et les limites communes à toutes les tables Gold (voir plus haut).

## 4. `gold/top10_produits/` - Top 10 des produits par chiffre d'affaires

| Élément | Description |
|---|---|
| Nom | Top 10 des produits par chiffre d'affaires |
| Finalité métier | Identifier les produits qui rapportent le plus, pour les mettre en avant ou sécuriser leur stock. |
| Question du Jour 1 | P4 Direction commerciale : « Quels produits génèrent le plus de chiffre d'affaires ? » |
| Sources | `data/silver/sales_enriched/` (vérifié par `notebooks/quality/controles_silver.ipynb`), construit à partir de `sales`, `dates`, `products` et `stores` |
| Granularité | 1 ligne = 1 produit, les 10 premiers par CA sur toute la période |
| Clé | `produit_sk` |
| Dimensions | Produit (et sa catégorie) |
| Mesures | `chiffre_affaires`, `nb_transactions`, `quantites_vendues`, `marge`, `remises`, `montant_catalogue`, `nb_lignes` |
| Lignes | 10 |
| Usage | Liste des produits phares |
| Schéma | `docs/data-dictionary/schemas/gold_top10_produits.json` |

**Colonnes et règles de calcul**

| Colonne | Type | Rôle | Description | Règle de calcul |
|---|---|---|---|---|
| `produit_sk` | bigint | Dimension | Clé technique du produit | `produit_sk` |
| `produit_id` | string | Dimension | Code métier du produit | `produit_id` |
| `nom_produit` | string | Dimension | Nom du produit | `nom_produit` |
| `categorie` | string | Dimension | Catégorie de produits | `categorie` |
| `chiffre_affaires` | decimal(18,2) | Mesure | KPI-01 : chiffre d'affaires hors taxes, remises et coupons déduits | Σ `montant_net_paye` |
| `nb_transactions` | bigint | Mesure | KPI-02 : nombre d'achats | Nombre de `ticket_id` distincts |
| `quantites_vendues` | bigint | Mesure | KPI-04 : articles vendus | Σ `quantite` |
| `marge` | decimal(18,2) | Mesure | Marge totale (peut être négative) | Σ `marge` |
| `remises` | decimal(18,2) | Mesure | Remises accordées | Σ `montant_remise` |
| `montant_catalogue` | decimal(18,2) | Mesure | Montant au prix catalogue, avant remise | Σ `montant_catalogue` |
| `nb_lignes` | bigint | Mesure | Lignes de vente agrégées (sert au contrôle) | Nombre de lignes |
| `_sources_silver` | string | Provenance | Jeu Silver utilisé | `silver/sales_enriched` |
| `_traitement` | string | Provenance | Notebook qui a produit la table | `agregations_gold.ipynb` |
| `_date_traitement` | timestamp | Provenance | Date et heure du calcul | Horodatage de l'écriture |

**Limites d'interprétation**

- Ce n'est qu'un classement : les 17 810 autres produits ne sont pas dans la table.
- Sur un échantillon de 10 % des tickets, le classement des produits est moins stable que celui des catégories : un produit peut entrer ou sortir du top 10 sur les données complètes.
- Les noms de produits sont des chaînes générées aléatoirement par TPCx-BB.
- Et les limites communes à toutes les tables Gold (voir plus haut).

## 5. `gold/ca_marge_par_magasin/` - Synthèse des ventes et de la marge par magasin

| Élément | Description |
|---|---|
| Nom | Synthèse des ventes et de la marge par magasin |
| Finalité métier | Comparer les 12 magasins sur leur CA, leur fréquentation, leur panier moyen et leur marge, pour repérer ceux qui sont moins rentables. |
| Question du Jour 1 | P2 Contrôleur de gestion : « Quelle marge fait chaque magasin ? » |
| Sources | `data/silver/sales_enriched/` (vérifié par `notebooks/quality/controles_silver.ipynb`), construit à partir de `sales`, `dates`, `products` et `stores` |
| Granularité | 1 ligne = 1 magasin (12 magasins), toute la période |
| Clé | `magasin_sk` |
| Dimensions | Magasin (nom, ville, état) |
| Mesures | `chiffre_affaires`, `nb_transactions`, `quantites_vendues`, `marge`, `remises`, `montant_catalogue`, `nb_lignes`, `panier_moyen`, `taux_marge_pct`, `taux_remise_pct`, `part_ca_pct` |
| Lignes | 12 |
| Usage | Classement des magasins ; pilotage du réseau |
| Schéma | `docs/data-dictionary/schemas/gold_ca_marge_par_magasin.json` |

**Colonnes et règles de calcul**

| Colonne | Type | Rôle | Description | Règle de calcul |
|---|---|---|---|---|
| `magasin_sk` | bigint | Dimension | Clé technique du magasin | `magasin_sk` |
| `magasin_id` | string | Dimension | Code métier du magasin | `magasin_id` |
| `nom_magasin` | string | Dimension | Nom du magasin | `nom_magasin` |
| `ville` | string | Dimension | Ville du magasin | `ville` |
| `etat` | string | Dimension | État du magasin | `etat` |
| `chiffre_affaires` | decimal(18,2) | Mesure | KPI-01 : chiffre d'affaires hors taxes, remises et coupons déduits | Σ `montant_net_paye` |
| `nb_transactions` | bigint | Mesure | KPI-02 : nombre d'achats | Nombre de `ticket_id` distincts |
| `quantites_vendues` | bigint | Mesure | KPI-04 : articles vendus | Σ `quantite` |
| `marge` | decimal(18,2) | Mesure | Marge totale (peut être négative) | Σ `marge` |
| `remises` | decimal(18,2) | Mesure | Remises accordées | Σ `montant_remise` |
| `montant_catalogue` | decimal(18,2) | Mesure | Montant au prix catalogue, avant remise | Σ `montant_catalogue` |
| `nb_lignes` | bigint | Mesure | Lignes de vente agrégées (sert au contrôle) | Nombre de lignes |
| `panier_moyen` | decimal(19,2) | Mesure calculée | KPI-03 : dépense moyenne par achat | `chiffre_affaires` ÷ `nb_transactions` |
| `taux_marge_pct` | decimal(25,2) | Mesure calculée | Taux de marge en % | `marge` ÷ `chiffre_affaires` × 100 |
| `taux_remise_pct` | decimal(25,2) | Mesure calculée | KPI-05 : taux de remise en % | `remises` ÷ `montant_catalogue` × 100 |
| `part_ca_pct` | decimal(25,2) | Mesure calculée | Part du CA total en % | `chiffre_affaires` ÷ Σ `chiffre_affaires` de toutes les lignes × 100 |
| `_sources_silver` | string | Provenance | Jeu Silver utilisé | `silver/sales_enriched` |
| `_traitement` | string | Provenance | Notebook qui a produit la table | `agregations_gold.ipynb` |
| `_date_traitement` | timestamp | Provenance | Date et heure du calcul | Horodatage de l'écriture |

**Limites d'interprétation**

- Les magasins ont des surfaces et des effectifs différents : comparer le CA brut, sans le ramener à la surface, favorise les grands magasins.
- Les dates de fermeture étant inutilisables (étape 4), on suppose que les 12 magasins sont ouverts sur toute la période.
- Et les limites communes à toutes les tables Gold (voir plus haut).

## 6. `gold/taux_remise_mensuel/` - Taux de remise par mois

| Élément | Description |
|---|---|
| Nom | Taux de remise par mois |
| Finalité métier | Suivre le niveau des remises et vérifier s'il augmente avec le temps, pour décider de fixer un maximum. |
| Question du Jour 1 | P2 Contrôleur de gestion : « Quel est le niveau moyen des remises, et augmente-t-il avec le temps ? » |
| Sources | `data/silver/sales_enriched/` (vérifié par `notebooks/quality/controles_silver.ipynb`), construit à partir de `sales`, `dates`, `products` et `stores` |
| Granularité | 1 ligne = 1 mois (`annee`, `mois`) |
| Clé | (`annee`, `mois`) |
| Dimensions | Période (année, mois) |
| Mesures | `montant_catalogue`, `remises`, `taux_remise_pct`, `nb_lignes` |
| Lignes | 60 |
| Usage | Courbe du taux de remise ; contrôle de la politique commerciale |
| Schéma | `docs/data-dictionary/schemas/gold_taux_remise_mensuel.json` |

**Colonnes et règles de calcul**

| Colonne | Type | Rôle | Description | Règle de calcul |
|---|---|---|---|---|
| `annee` | int | Dimension | Année de la vente | `annee` de `sales_enriched` |
| `mois` | int | Dimension | Mois de la vente (1 à 12) | `mois` de `sales_enriched` |
| `montant_catalogue` | decimal(18,2) | Mesure | Montant au prix catalogue, avant remise | Σ `montant_catalogue` |
| `remises` | decimal(18,2) | Mesure | Remises accordées | Σ `montant_remise` |
| `taux_remise_pct` | decimal(25,2) | Mesure calculée | KPI-05 : taux de remise en % | `remises` ÷ `montant_catalogue` × 100 |
| `nb_lignes` | bigint | Mesure | Lignes de vente agrégées (sert au contrôle) | Nombre de lignes |
| `_sources_silver` | string | Provenance | Jeu Silver utilisé | `silver/sales_enriched` |
| `_traitement` | string | Provenance | Notebook qui a produit la table | `agregations_gold.ipynb` |
| `_date_traitement` | timestamp | Provenance | Date et heure du calcul | Horodatage de l'écriture |

**Limites d'interprétation**

- Le taux se calcule sur les sommes, pas en faisant la moyenne de taux par ligne : une grosse ligne pèse plus qu'une petite.
- Un taux proche de 50 % est très élevé pour un vrai commerce : c'est propre aux données générées (voir le dictionnaire de KPI).
- Les coupons (`montant_coupon`) ne sont pas comptés dans les remises.
- Et les limites communes à toutes les tables Gold (voir plus haut).

