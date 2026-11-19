# Rapport de qualité des données - TP Jour 3, Étape 9

- Notebook : `notebooks/quality/controles_qualite.ipynb`
- Détail des 152 contrôles : `outputs/rapport_qualite.json`
- Date : 18/11/2026

## 1. Périmètre et méthode

| Zone | Jeux contrôlés |
|---|---|
| Silver | `sales` (échantillon de 10 % des tickets), `products`, `stores`, `dates`, `sales_enriched` |
| Gold | `ca_mensuel`, `ca_annuel`, `ca_marge_par_categorie`, `top10_produits`, `ca_marge_par_magasin`, `taux_remise_mensuel` |
| Références brutes (lecture seule) | `promotion`, `customer`, `time_dim` : servent à vérifier des clés que nous gardons sans les nettoyer |

Chaque contrôle applique une règle et reçoit un statut :

| Statut | Sens |
|---|---|
| **OK** | La règle est respectée |
| **ALERTE** | Anomalie restante, connue et acceptée : documentée, signalée par un indicateur ou corrigée |
| **KO** | La règle n'est pas respectée : une correction est nécessaire |

Ce notebook complète `notebooks/quality/controles_silver.ipynb` (étape 6, 77 contrôles
techniques : présence, format, schéma). Ici, on contrôle la **qualité du
contenu**.

## 2. Synthèse

**152 contrôles : 135 OK, 17 ALERTE, 0 KO.**

| Dimension | Contrôles | OK | ALERTE | KO |
|---|---|---|---|---|
| Complétude | 44 | 37 | 7 | 0 |
| Unicité | 15 | 15 | 0 | 0 |
| Validité des types | 15 | 15 | 0 | 0 |
| Cohérence des valeurs | 32 | 25 | 7 | 0 |
| Volumes | 19 | 17 | 2 | 0 |
| Clés candidates | 16 | 15 | 1 | 0 |
| Intégrité référentielle | 11 | 11 | 0 | 0 |
| **Total** | **152** | **135** | **17** | **0** |

Aucune règle bloquante n'est violée. Les jeux Silver et Gold sont
**utilisables** pour les analyses prévues, à condition de tenir compte des
alertes de la section 4.

## 3. Tableau de contrôle (principales règles)

| Contrôle | Règle | Jeu | Résultat | Statut |
|---|---|---|---|---|
| **Complétude** | Champ requis non nul : date, produit, magasin, ticket, quantité, prix, montants | `sales` | 0 vide sur 9 champs | OK |
| Complétude | Champ requis non nul : clé, code, catégorie, prix, nom | `products` | 0 vide | OK |
| Complétude | Champ requis non nul : clé, code, nom, ville, état | `stores` | 0 vide | OK |
| Complétude | Champ requis non nul : date, année, catégorie, magasin, CA, marge | `sales_enriched` | 0 vide | OK |
| Complétude | Champ facultatif : taux de vide < 1 % | `sales` | `ss_cdemo_sk` 0,03 %, `ss_hdemo_sk` 0,04 %, `ss_addr_sk` 0,11 %, `ss_promo_sk` 0,02 % | ALERTE |
| Complétude | Champ facultatif : taux de vide < 1 % | `products` | `i_brand` 6, `i_item_desc` 4 (0,03 %) | ALERTE |
| Complétude | Date de fermeture renseignée | `stores` | 12 / 12 vides (valeurs invalidées par R5) | ALERTE |
| Complétude | Aucune mesure vide | 6 tables Gold | 0 ligne incomplète | OK |
| **Unicité** | Clé candidate sans doublon | 5 jeux Silver, 6 tables Gold | 0 doublon | OK |
| Unicité | Aucune ligne entièrement dupliquée | `sales` | 0 copie | OK |
| **Validité** | Type attendu (`bigint`, `decimal(7,2)`, `date`, `boolean`) | 5 jeux Silver | Conformes | OK |
| Validité | Montants en `decimal`, jamais en `double` | 6 tables Gold | Conformes | OK |
| Validité | Format : `s_zip` `^[0-9]{5}$`, `s_state` `^[A-Z]{2}$`, `i_item_id` `^[A-Z]{16}$`, `s_hours` `hAM-hPM` | `stores`, `products` | 0 invalide | OK |
| **Cohérence** | Quantité dans le domaine [1, 100] | `sales` | 0 hors domaine | OK |
| Cohérence | Formules TPCx-BB : montant = qté × prix ; catalogue = qté × prix catalogue ; remise = catalogue − vente ; net = vente − coupon ; net TTC = net + taxe ; marge = net − coût | `sales` | 0 écart (tolérance 0,01) | OK |
| Cohérence | Un ticket = un seul magasin et une seule date | `sales` | 0 ticket incohérent | OK |
| Cohérence | Vente postérieure à l'ouverture du magasin | `sales` | 0 vente avant ouverture | OK |
| Cohérence | Catégorie parmi les 9 du référentiel, 1 code = 1 libellé | `products` | 0 écart | OK |
| Cohérence | Date de vente dans la période (2001-01-01 → 2005-12-13), taux de remise dans [0, 1] | `sales_enriched` | 0 écart | OK |
| Cohérence | Marge ≥ 0 | `sales` | 49 559 lignes (74,42 %) négatives | ALERTE |
| Cohérence | Prix de vente ≥ coût d'achat | `sales` | 46 271 lignes (69,48 %) vendues à perte | ALERTE |
| Cohérence | Prix de vente > 0 | `sales` | 356 lignes (0,53 %) à 0 | ALERTE |
| Cohérence | Coût d'achat ≤ prix courant | `products` | 7 768 produits (43,59 %) | ALERTE |
| Cohérence | Ouverture ≠ fermeture dans `s_hours` | `stores` | 1 magasin (Buffalo, `8AM-8AM`) | ALERTE |
| Cohérence | Date de fermeture fiable | `stores` | 12 / 12 invalides | ALERTE |
| Cohérence | Totaux Gold = totaux Silver (CA et marge) | 4 tables Gold | CA 115 752 176,68 et marge −55 241 252,10 identiques | OK |
| Cohérence | Somme des parts de CA = 100 % (± 0,1) | `ca_marge_par_categorie` | 100,01 % (arrondis) | OK |
| Cohérence | Top 10 exact : aucun produit hors top avec un CA supérieur | `top10_produits` | 0 | OK |
| Cohérence | Chaque mois est complet | `ca_mensuel` | Décembre 2005 incomplet | ALERTE |
| **Volume** | Lignes lues = lignes Silver + rejets | 4 jeux Silver | 66 593 / 17 820 / 12 / 109 573, 0 rejet | OK |
| Volume | Lignes enrichies = lignes de ventes | `sales_enriched` | 66 593 = 66 593 | OK |
| Volume | 60 mois et 12 magasins présents | `sales_enriched` | 60 mois (425 à 1 271 lignes), 12 magasins (5 172 à 5 891 lignes) | OK |
| Volume | Aucun mois sous 50 % de la moyenne | `sales_enriched` | 2005-12 : 425 lignes | ALERTE |
| Volume | Échantillon ≈ 10 % | `sales` | 8 910 / 89 100 tickets (10,00 %), 66 593 / 667 579 lignes (9,98 %) | ALERTE |
| Volume | Une ligne par valeur de la granularité | 6 tables Gold | 60, 5, 9, 10, 12, 60 | OK |
| **Clé candidate** | (`ss_ticket_number`, `ss_item_sk`, `ss_ligne_ticket`) unique et non nulle | `sales` | 0 doublon, 0 nulle | OK |
| Clé candidate | Clé minimale : sans `ss_item_sk`, (ticket, ligne) n'est plus unique | `sales` | 57 285 doublons sans `ss_item_sk` | OK |
| Clé candidate | (ticket, produit) suffit-il ? | `sales` | Non : 406 lignes répétées | ALERTE |
| Clé candidate | Clés technique et métier uniques : `i_item_sk` / `i_item_id`, `s_store_sk` / `s_store_id`, `d_date_sk` / `d_date` | `products`, `stores`, `dates` | 0 doublon | OK |
| **Intégrité** | `ss_item_sk` → `products`, `ss_store_sk` → `stores`, `ss_sold_date_sk` → `dates` | `sales` | 0 orpheline | OK |
| Intégrité | `ss_promo_sk` → `promotion`, `ss_customer_sk` → `customer`, `ss_sold_time_sk` → `time_dim` (tables brutes) | `sales` | 0 orpheline | OK |
| Intégrité | Dimensions Gold (catégorie, magasin, produit) → Silver | 3 tables Gold | 0 orpheline | OK |

## 4. Bilan

### Règles respectées

- **Complétude** : tous les champs requis sont remplis dans Silver et dans
  Gold.
- **Unicité et clés** : chaque jeu a une clé candidate unique, non nulle et
  minimale.
- **Types** : les montants sont en `decimal`, les dates en `date`, et les
  codes restent du texte.
- **Formules** : les 6 formules de calcul TPCx-BB sont exactes sur toutes
  les lignes, ce qui confirme la définition du CA (`ss_net_paid` = montant de
  vente − coupons) et du taux de remise du dictionnaire de KPI.
- **Intégrité référentielle** : elle est vérifiée sur 11 relations, y compris
  vers trois tables brutes non nettoyées.
- **Gold** : les tables reproduisent exactement les totaux Silver.

### Anomalies restantes (17 alertes)

| # | Anomalie | Jeu | Ampleur | Traitement appliqué |
|---|---|---|---|---|
| 1 | Marges négatives | `sales` | 74,42 % des lignes | Conservées, indicateur `ss_marge_negative` (R7) |
| 2 | Ventes sous le coût d'achat | `sales` | 69,48 % | Conservées (même cause que 1) |
| 3 | Coût d'achat > prix courant | `products` | 43,59 % des produits | Conservés, indicateur `i_cout_superieur_prix` |
| 4 | Prix de vente à 0 | `sales` | 356 lignes (0,53 %) | Conservés, indicateur `ss_prix_nul` |
| 5 | Dates de fermeture incohérentes (1917 à 2141), vues comme une alerte de complétude et comme une alerte de cohérence | `stores` | 12 / 12 | Remplacées par `null`, indicateur `s_date_fermeture_invalide` (R5) |
| 6 | Horaires `8AM-8AM` | `stores` | 1 magasin | Conservés, colonne non utilisée |
| 7 | Même produit deux fois dans un ticket | `sales` | 406 lignes | Conservées, numérotées par `ss_ligne_ticket` (R6) |
| 8 à 11 | Clés client et promotion vides | `sales` | 0,02 % à 0,11 % | Conservées en `null` (facultatives) |
| 12 et 13 | Marque et description vides | `products` | 10 produits | Conservées en `null` |
| 14 | Décembre 2005 incomplet (vu comme une alerte de cohérence et comme une alerte de volume) | `ca_mensuel`, `sales_enriched` | 1 mois, 425 lignes | Signalé par `mois_incomplet` |
| 15 | Traitement sur un échantillon | `sales` | 10 % des tickets | Documenté dans chaque livrable |

Les alertes 1 à 3 viennent de la **génération synthétique TPCx-BB**. Les
données sont cohérentes entre elles (marge = net − coût), mais peu réalistes
pour un vrai commerce.

### Données mises à l'écart

| Jeu | Lignes lues | Rejetées | Motifs |
|---|---|---|---|
| `sales` | 66 593 | 0 | Aucune ligne ne viole R1, R3, R4 ou R7 |
| `products` | 17 820 | 0 | - |
| `stores` | 12 | 0 | - |
| `dates` | 109 573 | 0 | - |

Aucune ligne n'a été écartée. En revanche, des **valeurs** ont été corrigées
ou signalées sans supprimer la ligne : les 12 dates de fermeture invalidées,
et les indicateurs des alertes 1 à 4. Le mécanisme de rejet
(`data/silver/rejects/<domaine>/` avec `motif_rejet`) est en place et
contrôlé : lignes lues = Silver + rejets.

### Limites des contrôles

- **Échantillon** : les contrôles sur `sales` portent sur 10 % des tickets.
  Une anomalie rare, présente dans moins de 1 ligne sur 66 593, peut passer
  inaperçue. Par exemple, l'étape 2 trouvait 158 `ss_promo_sk` vides sur le
  fichier complet, et l'échantillon en contient 15.
- **Vraisemblance non testée** : les contrôles vérifient la cohérence
  interne des données, pas leur vraisemblance réelle. Une erreur cohérente,
  comme un prix faux mais bien multiplié par la quantité, n'est pas
  détectée.
- **Seuils arbitraires** : les seuils (vide < 1 %, mois ≥ 50 % de la
  moyenne, tolérance de 0,01) sont choisis par nous. Ils ne viennent pas
  d'un engagement de qualité défini avec le métier.
- **Intégrité partielle** : elle n'est vérifiée que sur les clés des
  tables disponibles. `ss_cdemo_sk`, `ss_hdemo_sk` et `ss_addr_sk` n'ont pas
  été rapprochées de leurs tables.
- **Doublons à confirmer** : les 406 lignes répétées sont interprétées
  comme de vraies lignes de caisse. Seul le métier ou le système de caisse
  peut le confirmer.
- **Contrôles ponctuels** : ils sont faits une fois, après traitement. Ils
  ne sont pas automatisés à chaque chargement et ne surveillent pas
  l'évolution dans le temps.
- **Pas d'ACID** : Parquet ne garantit pas l'atomicité des écritures (voir
  `docs/architecture/comparaison_formats.md`). Les contrôles vérifient un
  état, pas l'absence d'écriture concurrente.

### Corrections éventuellement nécessaires

| Priorité | Correction | Pourquoi |
|---|---|---|
| 1 | Rejouer le traitement sur le `store_sales` complet (667 579 lignes), sur une machine plus puissante ou sur le cluster | Lever la limite de l'échantillon, et obtenir les vrais montants absolus |
| 2 | Obtenir du fournisseur les vraies dates de fermeture des magasins | La colonne est inutilisable en l'état |
| 3 | Confirmer avec le métier le sens des 406 lignes (ticket, produit) répétées et des 356 ventes à prix 0 | Décider de les garder, de les fusionner ou de les exclure du CA |
| 4 | Ne pas présenter la marge comme un indicateur de rentabilité réelle tant que les données sont synthétiques | 74 % de lignes à marge négative |
| 5 | Automatiser `controles_silver` et `controles_qualite` à chaque nouveau chargement, par exemple pour les données `data_refresh` | Détecter les régressions dès leur arrivée |
| 6 | Exclure ou isoler décembre 2005 dans les comparaisons d'une année sur l'autre | Mois incomplet |
