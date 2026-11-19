# Dictionnaire des KPI mis à jour (UC-08, étape 2)

Ce dictionnaire part de `01_UC01_besoin_exploration/UC01_dictionnaire_KPI.md`, adapté aux données **réellement disponibles** après le TP3. Seul le canal magasin est disponible, et les colonnes portent les noms de `sales_enriched`. La version CSV se trouve dans `analytics/outputs/kpi_dictionnaire.csv`.

**Filtres communs** : canal magasin uniquement, échantillon de 10 % des tickets (`ss_ticket_number` multiple de 10), période du 01/01/2001 au 13/12/2005, retours non déduits.

| KPI | Définition métier | Formule | Champs (nom d'origine) | Granularité | Unité | Limites d'interprétation |
|---|---|---|---|---|---|---|
| **KPI-01 Chiffre d'affaires** | Argent encaissé, remises déduites, hors taxes | `SUM(montant_net_paye)` | `ss_net_paid` | global, année, mois, magasin, catégorie | EUR (supposé) | Un CA élevé ne signifie pas une marge élevée ; c'est le total de l'échantillon, pas du réseau entier |
| **KPI-02 Nombre de transactions** | Nombre de tickets de caisse | `COUNT(DISTINCT ticket_id)` | `ss_ticket_number` | global, année, mois, magasin | tickets | Ne jamais compter les lignes (7,5 lignes par ticket) ; un ticket n'est pas un client |
| **KPI-03 Panier moyen** | Montant moyen par ticket | KPI-01 / KPI-02 | `ss_net_paid`, `ss_ticket_number` | global, année, magasin | EUR par ticket | Moyenne tirée vers le haut par les gros tickets : à lire avec la médiane (11 718 EUR) |
| **KPI-04 Quantités vendues** | Nombre d'articles vendus | `SUM(quantite)` | `ss_quantity` | global, année, catégorie | articles | Additionne des articles très différents |
| **KPI-05 Taux de remise** | Part du prix catalogue enlevée par les remises | `SUM(montant_remise) / SUM(montant_catalogue) × 100` | `ss_ext_discount_amt`, `ss_ext_list_price` | global, année, mois, catégorie | % | Environ 50 % partout (données générées) : à comparer dans le temps, pas à juger |
| **KPI-06 Évolution du CA** | Variation par rapport à la même période N-1 | `(CA N − CA N-1) / CA N-1 × 100` | `ss_net_paid`, `d_year`, `d_moy` | année, mois | % | Pas de N-1 pour 2001. **2005 doit être comparée sur une période égale** (1/1 au 13/12), sinon −7,21 % au lieu de −2,53 % |

## Indicateurs non retenus

| Indicateur | Raison |
|---|---|
| Marge (`ss_net_profit`) | Les coûts existent mais ne sont pas qualifiés : 74 % des lignes ont une marge négative (alerte qualité TP3). On ne l'utilise pas pour conclure. |
| Part du CA web / magasin | `web_sales` n'a pas été transformé au TP3 : le canal n'est pas identifiable. |
| Taux de retour | `store_returns` n'a pas été transformé au TP3. |

## Valeurs calculées (`analytics/outputs/kpi.csv`)

| Période | CA (EUR) | Transactions | Panier moyen (EUR) | Quantités | Taux de remise | Évol. CA brute | Évol. CA période égale (1/1 au 13/12) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2001 | 23 404 661,59 | 1 800 | 13 002,59 | 677 319 | 50,05 % | – | – |
| 2002 | 23 037 968,91 | 1 799 | 12 805,99 | 681 325 | 50,26 % | −1,57 % | −1,68 % |
| 2003 | 23 591 448,60 | 1 799 | 13 113,65 | 686 147 | 49,67 % | +2,40 % | +2,83 % |
| 2004 | 23 713 771,57 | 1 803 | 13 152,40 | 695 055 | 50,05 % | +0,52 % | +0,19 % |
| 2005 (jusqu'au 13/12) | 22 004 326,01 | 1 709 | 12 875,56 | 646 230 | 49,85 % | −7,21 % | −2,53 % |
| **2001-2005** | **115 752 176,68** | **8 910** | **12 991,27** | **3 386 076** | **49,98 %** | | |

**Contrôle** : les KPI recalculés depuis le Silver sont **identiques** à ceux de la table Gold `ca_annuel` (CA, transactions, quantités, panier moyen, taux de remise). La somme des transactions annuelles est égale au total (8 910), car un ticket n'a qu'une seule date.
