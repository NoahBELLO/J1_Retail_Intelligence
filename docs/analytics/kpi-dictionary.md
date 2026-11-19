# Dictionnaire des KPI mis à jour – TP Jour 4, UC-08 (J4-02)

Ce dictionnaire part de celui du Jour 1 (`01_UC01_besoin_exploration/UC01_dictionnaire_KPI.md`), adapté aux données **réellement disponibles** après le Jour 3. Seul le canal magasin est disponible. Les colonnes portent les noms de `sales_enriched`, avec le nom TPCx-BB d'origine entre parenthèses. La version CSV est dans `analytics/outputs/kpi_dictionnaire.csv`.

**Filtres communs** : canal magasin uniquement, période du 01/01/2001 au 13/12/2005, retours non déduits. Le notebook principal travaille sur un échantillon de 10 % des tickets (`ss_ticket_number` multiple de 10), le notebook HDFS sur le fichier complet.

## 1. Les KPI

| KPI | Définition métier | Formule | Champs (nom d'origine) | Granularité | Unité | Limites d'interprétation |
|---|---|---|---|---|---|---|
| **KPI-01 Chiffre d'affaires** | Argent encaissé, remises déduites, hors taxes | `SUM(montant_net_paye)` | `ss_net_paid` | global, année, mois, magasin, catégorie | EUR (supposé) | Un CA élevé ne veut pas dire une marge élevée. Sur l'échantillon, c'est environ un dixième du CA réel |
| **KPI-02 Nombre de transactions** | Nombre de tickets de caisse | `COUNT(DISTINCT ticket_id)` | `ss_ticket_number` | global, année, mois, magasin | tickets | Ne jamais compter les lignes (7,5 lignes par ticket). Un ticket n'est pas un client |
| **KPI-03 Panier moyen** | Montant moyen par ticket | KPI-01 ÷ KPI-02 | `ss_net_paid`, `ss_ticket_number` | global, année, magasin | EUR par ticket | Moyenne tirée vers le haut par les gros tickets : à lire avec la médiane (11 718 €) |
| **KPI-04 Quantités vendues** | Nombre d'articles vendus | `SUM(quantite)` | `ss_quantity` | global, année, catégorie | articles | Additionne des articles très différents |
| **KPI-05 Taux de remise** | Part du prix catalogue enlevée par les remises | `SUM(montant_remise) ÷ SUM(montant_catalogue) × 100` | `ss_ext_discount_amt`, `ss_ext_list_price` | global, année, mois, catégorie | % | Environ 50 % partout (données générées) : à comparer dans le temps, pas à juger |
| **KPI-06 Évolution du CA** | Variation par rapport à la même période de l'année d'avant | `(CA N − CA N-1) ÷ CA N-1 × 100` | `ss_net_paid`, `d_year`, `d_moy` | année, mois | % | Pas d'année d'avant pour 2001. **2005 doit être comparée sur une période égale** (du 1/1 au 13/12), sinon on trouve −7,21 % au lieu de −2,53 %. Calculable seulement dans le notebook principal (le notebook HDFS n'a pas `date_dim`) |

Les taux sont toujours calculés à partir des **sommes**, et pas en faisant la moyenne des taux ligne par ligne.

## 2. Indicateurs non retenus

| Indicateur | Raison |
|---|---|
| Marge (`ss_net_profit`) | Les coûts existent mais ne sont pas fiables : 74 % des lignes ont une marge négative (alerte qualité du Jour 3). On ne l'utilise pas pour conclure |
| Part du CA web / magasin | `web_sales` n'a pas été transformée au Jour 3 : le canal n'est pas identifiable |
| Taux de retour | `store_returns` n'a pas été transformée au Jour 3 |

## 3. Valeurs calculées – notebook principal (`analytics/outputs/kpi.csv`)

| Période | CA (EUR) | Transactions | Panier moyen (EUR) | Quantités | Taux de remise | Évol. CA brute | Évol. CA période égale (1/1 au 13/12) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2001 | 23 404 661,59 | 1 800 | 13 002,59 | 677 319 | 50,05 % | – | – |
| 2002 | 23 037 968,91 | 1 799 | 12 805,99 | 681 325 | 50,26 % | −1,57 % | −1,68 % |
| 2003 | 23 591 448,60 | 1 799 | 13 113,65 | 686 147 | 49,67 % | +2,40 % | +2,83 % |
| 2004 | 23 713 771,57 | 1 803 | 13 152,40 | 695 055 | 50,05 % | +0,52 % | +0,19 % |
| 2005 (jusqu'au 13/12) | 22 004 326,01 | 1 709 | 12 875,56 | 646 230 | 49,85 % | −7,21 % | −2,53 % |
| **2001-2005** | **115 752 176,68** | **8 910** | **12 991,27** | **3 386 076** | **49,98 %** | | |

**Contrôle** : les KPI recalculés depuis le Silver sont **identiques** à ceux de la table Gold `ca_annuel`. La somme des transactions des années est égale au total (8 910), parce qu'un ticket n'a qu'une seule date.

## 4. Comparaison avec le fichier complet (`analytics/outputs/hdfs/kpi.csv`)

| KPI | Échantillon 10 % | Fichier complet | Écart |
|---|---:|---:|---|
| KPI-01 Chiffre d'affaires | 115 752 176,68 € | 1 150 529 586,37 € | l'échantillon fait 10,06 % du total |
| KPI-02 Transactions | 8 910 | 89 100 | exactement 10 % |
| KPI-03 Panier moyen | 12 991,27 € | 12 912,79 € | +0,6 % |
| KPI-04 Quantités vendues | 3 386 076 | 33 755 474 | l'échantillon fait 10,03 % du total |
| KPI-05 Taux de remise | 49,98 % | 49,99 % | 0,01 point |
| KPI-06 Évolution du CA | calculée | non calculable | – |

L'échantillon est donc fiable pour les taux et les moyennes. Pour les montants, il faut multiplier par environ 10.

**Contrôle du notebook HDFS** : le CA calculé sur le Silver est égal à la somme du Gold `ca_par_categorie` (écart 0,00), et un ticket appartient à un seul magasin (89 100 couples ticket-magasin pour 89 100 tickets).
