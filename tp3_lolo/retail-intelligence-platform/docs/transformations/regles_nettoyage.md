# Règles de nettoyage - TP Jour 3, Étape 4

Traitement : `transformations/cleaning/nettoyage_silver.ipynb`

Bilan chiffré : `outputs/bilan_nettoyage.json`

Sources : `store_sales`, `item`, `store`, ainsi que `date_dim`, qui sert de
référentiel pour valider et traduire les clés de date.

Sorties :
- `data/silver/<domaine>/` : données nettoyées, en Parquet (`sales`, `products`, `stores`, `dates`, voir `docs/data-dictionary/silver.md`) ;
- `data/silver/rejects/<domaine>/` : lignes mises à l'écart, avec leur `motif_rejet`.

> **Volume traité** : le fichier `store_sales` complet (667 579 lignes) sature
> la machine (5 Go de RAM). Le traitement porte donc sur un **échantillon de
> 10 % des tickets**, soit 66 593 lignes et 8 910 tickets complets :
> `data/samples/store_sales_echantillon.dat`. Les autres tables sont traitées
> en entier. Les règles sont les mêmes pour le fichier complet : il suffit de
> changer le chemin dans le notebook.
>
> L'échantillon a été créé une fois, sans Spark, avec :
> `awk -F'|' '$10 % 10 == 0' store_sales.dat > data/samples/store_sales_echantillon.dat`
> Il garde les tickets dont le numéro se termine par 0, donc des tickets entiers.

## Tableau des règles

| Anomalie | Règle | Action appliquée | Justification |
|---|---|---|---|
| **Valeur manquante** (colonne obligatoire) | R3 : sont obligatoires, pour une vente, la date, le produit, le magasin, le ticket, la quantité, les prix et les montants. Pour un produit, `i_item_sk`, `i_item_id`, `i_category` et `i_current_price` ; pour un magasin, `s_store_sk` et `s_store_id`. | Ligne **rejetée** (`R3_obligatoire_manquant`) | Sans ces valeurs, on ne peut calculer ni le CA ni la marge, ni rattacher la vente à un produit ou un magasin |
| **Valeur manquante** (colonne facultative) | R3 : clés client (`ss_cdemo_sk`, `ss_hdemo_sk`, `ss_addr_sk`), `ss_promo_sk`, marque et description du produit | **Conservée** en `null`. `ss_promo_sk` vide donne l'indicateur `ss_sans_promotion` | Ces informations ne servent pas aux indicateurs de CA et de marge. Un `ss_promo_sk` vide veut dire « vente sans promotion », ce n'est pas une erreur |
| **Valeur manquante** (texte vide) | R2 : `trim` sur tous les textes, chaîne vide → `null` | Valeur **harmonisée** | Une valeur manquante doit avoir une seule représentation, pour être comptée correctement |
| **Type incorrect** | R1 : schéma imposé, repris de la spécification TPCx-BB. Montants en `decimal(7,2)`, clés en `bigint`, codes (`s_zip`, `s_street_number`) en `string` | Conversion explicite. Une valeur non convertible est repérée (`_ligne_corrompue`) et la ligne est **rejetée** (`R1_type_invalide`) | L'inférence lisait les montants en `double`, ce qui crée des erreurs d'arrondi dans les sommes, et les codes postaux en nombre, ce qui fait perdre les zéros initiaux. Un rejet explicite évite qu'une conversion ratée devienne un `null` silencieux |
| **Format incohérent** | R2 : `s_zip` complété à 5 chiffres (`lpad`) | Valeur **harmonisée** | Un code postal est un code, pas un nombre |
| **Doublon** (copie exacte) | R6 : toutes les colonnes sont identiques | Doublon **supprimé**, une seule ligne gardée (`dropDuplicates`) | La définition est claire et ne fait pas perdre d'information |
| **Doublon** (même ticket et même produit) | R6 : deux lignes ont le même couple (`ss_ticket_number`, `ss_item_sk`) mais des quantités ou des prix différents | Lignes **conservées** et numérotées (`ss_ligne_ticket`) | Ce sont deux lignes de caisse différentes, par exemple le même article scanné deux fois à des prix différents (ticket 44, produit 10003). Les supprimer ferait perdre du CA. La numérotation donne une clé unique (ticket, produit, ligne) |
| **Doublon** (clé de référence) | R6 : `d_date_sk`, `i_item_sk` ou `s_store_sk` présent plusieurs fois | Lignes **rejetées** (`R6_doublon_cle`) | Une clé de référence en double multiplierait les ventes lors des jointures |
| **Identifiant invalide** (valeur) | R4 : clé `*_sk` ou numéro de ticket négatif | Ligne **rejetée** (`R4_identifiant_invalide`) | Les clés TPCx-BB sont des entiers positifs ou nuls |
| **Identifiant invalide** (référence) | R4 : le produit, le magasin ou la date d'une vente n'existe pas dans `item`, `store` ou `date_dim` | Ligne **rejetée** (`R4_produit_inconnu`, `R4_magasin_inconnu`, `R4_date_inconnue`) | Une vente sans référence ne peut pas être analysée par catégorie, magasin ou période |
| **Date incohérente** (format) | R5 : conversion en `date` au format `yyyy-MM-dd` (`d_date`, `i_rec_start_date`, `s_rec_start_date`) | Date convertie. Si le format est invalide, ligne **rejetée** (`R5_date_invalide`) | On ne convertit une colonne en date qu'une fois son format vérifié |
| **Date incohérente** (sens) | R5 : une date de fermeture (`s_closed_date_sk`) est impossible si elle tombe avant l'ouverture du magasin, ou après la dernière vente connue (13/12/2005) | Date **remplacée par `null`**, indicateur `s_date_fermeture_invalide`. Le magasin est **conservé** | Les 12 dates vont de 1917 à 2141, alors que les magasins ouvrent en 2000 et vendent jusqu'en 2005. La colonne est inutilisable, mais les ventes des magasins sont réelles |
| **Quantité / montant invalide** | R7 : quantité ≤ 0, prix ou montant payé négatif, prix de vente supérieur au prix catalogue, montant ≠ quantité × prix (tolérance 0,01) | Ligne **rejetée** (`R7_quantite_invalide`, `R7_montant_negatif`, `R7_prix_superieur_catalogue`, `R7_montant_incoherent`) | Ces cas contredisent le sens des colonnes : une vente a une quantité positive et un montant égal à quantité × prix |
| **Prix de produit invalide** | R7 : `i_current_price` ≤ 0 | Ligne **rejetée** (`R7_prix_invalide`) | Un produit au catalogue a un prix positif |
| **Marge négative** | R7 : `ss_net_profit` < 0 | **Conservée**, indicateur `ss_marge_negative` | Une valeur négative n'est pas forcément une erreur : vendre à perte est un cas métier réel (déstockage, promotion). Ici, 74 % des lignes sont concernées, ce qui vient de la génération synthétique TPCx-BB |
| **Prix de vente à 0** | R7 : `ss_sales_price` = 0 | **Conservée**, indicateur `ss_prix_nul` | Cela peut être un article offert. Le montant reste cohérent (quantité × 0 = 0) |
| **Coût d'achat supérieur au prix** (produit) | R7 : `i_wholesale_cost` > `i_current_price` | **Conservée**, indicateur `i_cout_superieur_prix` | C'est une information sur le produit, pas une erreur de saisie prouvée |
| **Valeur atypique** | R8 : montants au-delà de Q3 + 1,5 × IQR (étape 3) | **Conservée** | Ce sont de gros paniers : les maximums restent cohérents avec quantité × prix (quantité ≤ 100, prix ≤ 200). Ils représentent un cas métier réel |
| **Horaires étranges** | `s_hours` = `8AM-8AM` (magasin Buffalo) | **Conservée** telle quelle | C'est peut-être un magasin ouvert 24 h sur 24, et la colonne ne sert à aucun indicateur |

Toute exclusion est documentée : une ligne rejetée est écrite dans
`data/silver/rejects/` avec son motif. Elle n'est jamais supprimée sans trace.

## Résultats obtenus

| Table | Lignes lues | Lignes rejetées | Lignes Silver | Remarques |
|---|---|---|---|---|
| `date_dim` | 109 573 | 0 | 109 573 | `d_date` convertie en `date` ; 9 colonnes conservées sur 28 |
| `item` | 17 820 | 0 | 17 820 | 7 768 produits signalés `i_cout_superieur_prix` |
| `store` | 12 | 0 | 12 | 12 dates de fermeture invalidées |
| `store_sales` (échantillon) | 66 593 | 0 | 66 593 | 0 doublon exact ; 406 lignes (ticket, produit) répétées et numérotées ; 356 prix à 0 ; 49 559 marges négatives ; 15 ventes sans promotion |

Contrôle après nettoyage, sur les fichiers Silver relus : aucune clé vide,
aucun doublon sur les clés (`d_date_sk`, `i_item_sk`, `s_store_sk`, et
(`ss_ticket_number`, `ss_item_sk`, `ss_ligne_ticket`)), et les montants sont
bien en `decimal(7,2)`.

Aucune ligne n'a été rejetée : les données TPCx-BB sont générées et
cohérentes sur ces points, comme l'exploration de l'étape 3 le laissait
prévoir. Les règles de rejet restent utiles pour les chargements suivants,
par exemple les données `data_refresh`, ou en cas d'erreur de production.

## Exemple guidé du sujet, appliqué aux colonnes réelles

```python
# Retirer les espaces inutiles d'une colonne texte (R2)
df_nettoye = df.withColumn("i_product_name", F.trim(F.col("i_product_name")))

# Convertir une colonne apres avoir verifie son contenu (R1)
df_nettoye = df_nettoye.withColumn("ss_quantity", F.col("ss_quantity").cast("integer"))
```

Dans le notebook, ces conversions sont faites dès la lecture, grâce au schéma
explicite. Une valeur impossible à convertir n'y devient pas un `null`
silencieux : elle est repérée par la colonne `_ligne_corrompue`.
