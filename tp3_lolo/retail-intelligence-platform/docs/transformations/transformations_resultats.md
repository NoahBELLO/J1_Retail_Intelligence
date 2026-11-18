# Transformations et résultats - TP Jour 3, Étape 5

Traitements :
- `transformations/enrichment/enrichissement_ventes.ipynb` : jointures, renommage et colonnes calculées. Il produit `data/silver/ventes_enrichies/`.
- `transformations/aggregation/agregations_gold.ipynb` : agrégations. Il produit `data/gold/<indicateur>/`.

Bilans : `outputs/bilan_jointures.json`, `outputs/bilan_gold.json`

> Les ventes viennent de l'**échantillon de 10 % des tickets** (66 593 lignes,
> voir `regles_nettoyage.md`). Les montants sont donc environ 10 fois plus
> petits que sur le fichier complet. Les parts, taux, paniers moyens et
> évolutions restent représentatifs, car les tickets sont gardés entiers.

## Chaîne de traitement

```
Raw (.dat)  --étape 4-->  Silver : store_sales, item, store, date_dim
                                     |
                          étape 5a : jointures + renommage + colonnes calculées
                                     v
                          Silver : ventes_enrichies (1 ligne = 1 produit dans 1 ticket)
                                     |
                          étape 5b : agrégations
                                     v
                          Gold : ca_mensuel, ca_annuel, ca_marge_par_categorie,
                                 ca_marge_par_magasin, top10_produits, taux_remise_mensuel
```

## 1. Opérations réalisées (`ventes_enrichies`)

| Opération | Détail |
|---|---|
| Renommage | Noms en français : `ss_net_paid` → `montant_net_paye`, `ss_net_profit` → `marge`, `i_category` → `categorie`, `s_store_name` → `nom_magasin`, etc. |
| Conversion de types | Déjà faite à l'étape 4 : montants en `decimal(7,2)`, dates en `date` |
| Colonnes calculées | `taux_marge` = marge ÷ montant net payé ; `taux_remise` = remise ÷ prix catalogue total. Une division par 0 donne `null` |
| Enrichissement | Date, année, trimestre, mois et jour (`date_dim`), produit et catégorie (`item`), magasin et ville (`store`) |
| Filtrage | Aucun à ce stade : les lignes invalides sont déjà écartées à l'étape 4. Les prix à 0 et les marges négatives sont gardés, avec leurs indicateurs |
| Stockage | Parquet, partitionné par `annee` |

## 2. Jointures

Les trois jointures sont des jointures gauches (`left`), pour conserver
toutes les ventes. Elles sont contrôlées automatiquement : la clé de la table
de référence doit être unique, et le nombre de lignes doit rester le même.

| | Ventes x dates | Ventes x produits | Ventes x magasins |
|---|---|---|---|
| Sources | `store_sales`, `date_dim` | `store_sales`, `item` | `store_sales`, `store` |
| Colonnes | `ss_sold_date_sk = d_date_sk` | `ss_item_sk = i_item_sk` | `ss_store_sk = s_store_sk` |
| Nature de la relation | Une vente a lieu à une date | Une ligne de vente porte sur un produit | Une vente a lieu dans un magasin |
| Cardinalité attendue | N:1 (`d_date_sk` unique) | N:1 (`i_item_sk` unique) | N:1 (`s_store_sk` unique) |
| Clé de référence unique | Oui | Oui | Oui |
| Lignes avant | 66 593 | 66 593 | 66 593 |
| Lignes après | 66 593 | 66 593 | 66 593 |
| Non rapprochées | 0 | 0 | 0 |

Ces relations ne sont pas supposées d'après le nom des colonnes. Elles ont été
vérifiées sur les valeurs au Jour 1 (`resultats_relations.csv`), aux étapes
2 et 4 (règle R4), puis à nouveau ici.

Les clics web (`web_clickstreams`) ne sont pas joints aux ventes en magasin :
aucun identifiant fiable ne relie ces deux sources.

## 3. Agrégations (Gold)

Les formules reprennent le dictionnaire de KPI du Jour 1
(`UC01_dictionnaire_KPI.md`). Les ratios sont calculés sur des sommes, pas en
faisant la moyenne de taux calculés ligne par ligne.

| Table Gold | Question métier (Jour 1) | Granularité | Règles de calcul | Lignes |
|---|---|---|---|---|
| `ca_mensuel` | P1 : évolution mensuelle du CA par rapport à l'année d'avant | 1 ligne = 1 mois (année, mois) | CA = Σ `montant_net_paye` ; transactions = nb de tickets distincts ; panier moyen = CA ÷ transactions ; évolution = (CA N − CA N-1) ÷ CA N-1 × 100, même mois | 60 |
| `ca_annuel` | P1 : même question, vue par année | 1 ligne = 1 année | Mêmes formules, évolution par rapport à l'année précédente | 5 |
| `ca_marge_par_categorie` | P4 : catégories qui génèrent le plus de CA ; P2 : marge par catégorie | 1 ligne = 1 catégorie | Part du CA = CA catégorie ÷ CA total × 100 ; taux de marge = Σ marge ÷ CA × 100 | 9 |
| `top10_produits` | P4 : produits qui génèrent le plus de CA | 1 ligne = 1 produit | Les 10 premiers produits par CA | 10 |
| `ca_marge_par_magasin` | P2 : marge par magasin | 1 ligne = 1 magasin | CA, part du CA, transactions, panier moyen, marge, taux de marge | 12 |
| `taux_remise_mensuel` | P2 : niveau des remises et évolution dans le temps | 1 ligne = 1 mois | KPI-05 : Σ remises ÷ Σ prix catalogue × 100 | 60 |

### Résultats obtenus

**CA annuel**

| Année | CA | Évolution | Transactions | Panier moyen | Taux de marge | Taux de remise |
|---|---|---|---|---|---|---|
| 2001 | 23 404 661,59 | - | 1 800 | 13 002,59 | -47,66 % | 50,05 % |
| 2002 | 23 037 968,91 | -1,57 % | 1 799 | 12 805,99 | -48,22 % | 50,26 % |
| 2003 | 23 591 448,60 | +2,40 % | 1 799 | 13 113,65 | -47,06 % | 49,67 % |
| 2004 | 23 713 771,57 | +0,52 % | 1 803 | 13 152,40 | -47,82 % | 50,05 % |
| 2005 | 22 004 326,01 | -7,21 % | 1 709 | 12 875,56 | -47,88 % | 49,85 % |

- **CA** : il est stable entre 2001 et 2004, à ±2,5 % par an. La baisse de 2005
  s'explique en partie par décembre 2005, incomplet (dernière vente le
  13/12/2005, indicateur `mois_incomplet`).
- **Remises** : le taux reste proche de 50 % chaque année. Il n'augmente pas
  avec le temps.

**CA et marge par catégorie**

| Catégorie | CA | Part du CA | Taux de marge |
|---|---|---|---|
| Music | 52 109 109,95 | 45,02 % | -48,15 % |
| Books | 30 720 062,81 | 26,54 % | -48,02 % |
| Movies & TV | 7 342 177,59 | 6,34 % | -48,77 % |
| Clothing & Accessories | 5 768 943,01 | 4,98 % | -44,47 % |
| Electronics | 5 682 478,05 | 4,91 % | -46,43 % |
| Home & Kitchen | 4 291 458,75 | 3,71 % | -46,67 % |
| Sports & Outdoors | 4 138 485,68 | 3,58 % | -44,82 % |
| Toys & Games | 2 901 166,65 | 2,51 % | -44,84 % |
| Tools & Home Improvement | 2 798 294,19 | 2,42 % | -52,02 % |

- **Concentration** : Music et Books font 71,6 % du CA, car ce sont aussi les
  catégories qui ont le plus de produits (7 164 et 4 688 produits vendus).
- **Marge** : la marge la moins mauvaise est celle de Clothing & Accessories
  (-44,47 %), la pire celle de Tools & Home Improvement (-52,02 %).

**CA et marge par magasin**

- **CA** : les 12 magasins pèsent entre 7,70 % (Egypt) et 8,76 % (Sherwood) du
  CA. Le CA est donc très réparti.
- **Taux de marge** : il va de -44,51 % (Forest) à -52,06 % (Hillside).
- **Panier moyen** : il va de 12 519,78 (Egypt) à 13 706,30 (Pioneer).

### Limites à signaler

- **Marge négative partout** : les données TPCx-BB sont générées, et les
  articles sont souvent vendus sous leur coût d'achat. Ces marges permettent
  de comparer les catégories ou les magasins entre eux, pas de juger la
  rentabilité réelle.
- **Panier moyen très élevé** : environ 13 000 par ticket, car un ticket
  compte en moyenne 7,5 lignes et environ 50 unités par ligne. C'est propre
  aux données générées.
- **Devise inconnue** : on suppose que les montants sont en euros (voir le
  dictionnaire de KPI).
- **Retours non déduits** : le CA ne tient pas compte des retours
  (`store_returns` n'est pas traité ici).
- **Échantillon** : les montants absolus valent environ 10 % du total réel.

## 4. Contrôles qualité des résultats

Vérifiés automatiquement à la fin du notebook d'agrégation :

| Contrôle | Résultat |
|---|---|
| Σ CA de `ca_mensuel` = CA total Silver (115 752 176,68) | Écart 0,00 |
| Σ CA de `ca_annuel` = CA total Silver | Écart 0,00 |
| Σ CA de `ca_marge_par_categorie` = CA total Silver | Écart 0,00 |
| Σ CA de `ca_marge_par_magasin` = CA total Silver | Écart 0,00 |
| Indicateurs vides (CA ou marge) | 0 |
