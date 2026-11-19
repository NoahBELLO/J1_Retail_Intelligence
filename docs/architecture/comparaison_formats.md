# Comparaison des formats CSV, JSON et Parquet - TP Jour 3, Étape 8

- Notebook : `notebooks/transformations/comparaison_formats.ipynb`
- Mesures : `outputs/comparaison_formats.json`

## Ce qui a été fait

1. Le résultat Silver `sales_enriched` (66 593 lignes, 39 colonnes une fois la
   provenance retirée) a été **écrit en Parquet** dans
   `outputs/formats/ventes_parquet/`, puis **relu et vérifié**.
2. Le **même résultat** a été écrit en CSV (`outputs/formats/ventes_csv/`) et en
   JSON (`outputs/formats/ventes_json/`), un seul fichier par format, puis les
   trois versions ont été relues et comparées.

`mode("overwrite")` n'est utilisé que sur `outputs/formats/`, un répertoire de
test dédié. Le notebook vérifie le chemin avant d'écrire. Les données
sources, Silver et Gold ne sont jamais la cible d'une écriture.

## Vérification du fichier Parquet relu

| Vérification | Méthode | Résultat |
|---|---|---|
| La lecture fonctionne | `spark.read.parquet(...)` | OK |
| Le schéma est conservé | Même nom et même type pour les 39 colonnes que le DataFrame écrit | OK : `decimal(7,2)`, `date`, `bigint` et `boolean` sont retrouvés tels quels |
| Le nombre de lignes est cohérent | Lignes relues = lignes écrites | OK : 66 593 |
| Les valeurs sont exploitables | Aucune ligne différente (`exceptAll`), et même CA recalculé | OK : 115 752 176,68 |
| Le répertoire de sortie est identifié | Le fichier `_SUCCESS` est présent dans `outputs/formats/ventes_parquet/` | OK |

## Mesures observées (même jeu, 66 593 lignes × 39 colonnes)

| | CSV | JSON | Parquet (Snappy) |
|---|---|---|---|
| **Volume sur disque** | 28,03 Mo | 66,18 Mo | **4,95 Mo** |
| Rapport au Parquet | × 5,7 | × 13,4 | 1 |
| Colonnes qui perdent leur type à la relecture | 27 / 39 sans `inferSchema`, 17 / 39 avec | 18 / 39 | **0 / 39** |
| CA recalculé après relecture | 115 752 176,68000033 | 115 752 176,6800006 | **115 752 176,68** |
| Ordre des colonnes conservé | Oui | Non (ordre alphabétique) | Oui |
| Colonne vide (`null`) | Champ vide | **Champ absent** de la ligne | Valeur `null` typée |
| Écriture | 1,62 s | 1,20 s | 2,43 s |
| Lecture de 2 colonnes sur 39 (CA par catégorie) | 0,49 s | 0,66 s | **0,43 s** |

À ce petit volume, les temps sont des ordres de grandeur. Une bonne partie
est le coût fixe de Spark, et les écarts grandiraient avec le volume. Le
volume sur disque et la conservation des types, eux, sont des mesures
exactes.

Ce que montre la relecture des types :

| Colonne | Type d'origine | CSV (défaut) | CSV (`inferSchema`) | JSON | Parquet |
|---|---|---|---|---|---|
| `date_vente` | date | string | date | string | date |
| `ticket_id` | bigint | string | int | bigint | bigint |
| `quantite` | int | string | int | bigint | int |
| `montant_net_paye` | decimal(7,2) | string | **double** | **double** | decimal(7,2) |
| `taux_remise` | decimal(12,4) | string | double | double | decimal(12,4) |
| `prix_nul` | boolean | string | boolean | boolean | boolean |

## Comparaison argumentée

### Organisation des données

- **CSV** : texte organisé **en lignes**. Une ligne correspond à un
  enregistrement, et les valeurs sont séparées par une virgule (ou par `|`
  dans les fichiers bruts TPCx-BB). Il y a au plus une ligne d'en-tête avec
  les noms des colonnes.
- **JSON** : texte organisé **en lignes**, avec un objet par ligne (JSON
  Lines). Chaque valeur est précédée du nom de sa colonne, et le format permet
  des structures imbriquées (listes, sous-objets).
- **Parquet** : binaire organisé **en colonnes**.
  - **Groupes de lignes** : les lignes sont découpées en groupes (*row
    groups*). Dans chaque groupe, toutes les valeurs d'une même colonne sont
    stockées ensemble et compressées (Snappy).
  - **Pied de fichier** : le schéma, le nombre de lignes et des statistiques
    par colonne y sont stockés (min, max, nombre de `null`). Lu par le
    notebook : `date_vente` va du 2001-01-01 au 2005-12-13, avec 0 `null`.
  - **Lecture sélective** : Spark ne lit que les colonnes utiles. Le plan
    d'exécution le montre (`ReadSchema: struct<categorie:string,
    montant_net_paye:decimal(7,2)>`) : 2 colonnes lues sur 39.

### Lisibilité

- **CSV** : très lisible. Il s'ouvre dans un éditeur de texte, un tableur ou
  avec `head`.
- **JSON** : lisible, et chaque valeur dit à quelle colonne elle appartient.
  En revanche, il est très verbeux.
- **Parquet** : il n'est pas lisible par un humain. Le fichier commence par
  `PAR1` puis contient des données binaires. Il faut un outil pour le lire
  (Spark, pandas, DuckDB...).

### Gestion des types

- **CSV** : il n'y a **aucun type** dans le fichier. Tout est relu comme du
  texte. `inferSchema` devine les types, mais au prix d'une passe de plus sur
  les données, et il se trompe : les `decimal` deviennent `double` et les
  `bigint` deviennent `int`. Un code postal serait lu comme un nombre et
  perdrait ses zéros initiaux, comme vu à l'étape 3.
- **JSON** : il distingue texte, nombre et booléen, mais il n'a ni date ni
  décimal exact. Les dates deviennent du texte, les montants des `double`,
  tous les entiers des `bigint`. Une valeur `null` est **omise** de la ligne.
- **Parquet** : le **schéma est stocké dans le fichier**. Les types relus
  sont exactement ceux écrits, y compris `decimal(7,2)` et `date`.
- **Conséquence mesurée** : relu en CSV ou en JSON, le CA est calculé en
  `double` et vaut 115 752 176,6800006 au lieu de 115 752 176,68. Pour des
  montants financiers, cette erreur d'arrondi est inacceptable.

### Volume de stockage

- **Parquet** : 4,95 Mo, soit **5,7 fois moins** que le CSV et **13,4 fois
  moins** que le JSON. Stocker les valeurs d'une colonne ensemble se
  compresse bien, car ces valeurs se ressemblent (même catégorie, même
  magasin, dates qui se suivent).
- **JSON** : c'est le plus gros des trois, car le nom de chaque colonne est
  répété sur chaque ligne, 39 fois.

### Usages adaptés

| Format | Usage adapté | Dans ce projet |
|---|---|---|
| CSV | Échange simple de données, ouverture dans un tableur, petits fichiers, export pour un utilisateur métier | Les fichiers sources TPCx-BB (`.dat` délimités par `\|`) en zone Raw. Le fichier de test `magasins_test.csv` |
| JSON | Données semi-structurées ou imbriquées, API, journaux d'événements, configuration | Bilans et schémas de référence (`outputs/*.json`, `docs/data-dictionary/schemas/*.json`) |
| Parquet | Stockage analytique : gros volumes, agrégations sur quelques colonnes, conservation des types | Toutes les zones **Silver** et **Gold** |

### Avantages et limites

| Format | Avantages | Limites |
|---|---|---|
| CSV | Universel, lisible, simple à produire, rapide à écrire | Pas de types, aucun schéma garanti. Sensible au séparateur, à l'encodage, aux guillemets et aux retours à la ligne dans les textes. Volumineux. Il faut tout lire, même pour une seule colonne |
| JSON | Lisible, porte le nom des champs, gère les structures imbriquées | Très volumineux (× 13 ici). Pas de date ni de décimal exact. Les champs `null` sont omis. L'ordre des colonnes n'est pas garanti. Lent à analyser |
| Parquet | Compact (compression par colonne), types conservés, schéma intégré. Lecture des seules colonnes utiles. Statistiques min/max qui permettent d'ignorer des blocs entiers lors d'un filtre. Partitionnement possible (`sales_enriched` par `annee`) | Illisible sans outil. Écriture un peu plus coûteuse. Un fichier ne se modifie pas : pour changer une ligne, on réécrit le fichier. Peu adapté aux petites écritures fréquentes ligne par ligne |

## Parquet n'est pas une table transactionnelle

Un répertoire Parquet est un **ensemble de fichiers**, pas une table
transactionnelle **ACID**. Concrètement, dans ce TP :

- **Pas d'atomicité** : `mode("overwrite")` supprime d'abord l'ancien
  contenu, puis écrit le nouveau. Si le traitement échoue au milieu, le
  répertoire peut rester vide ou à moitié écrit. Le fichier `_SUCCESS` dit
  seulement que l'écriture est allée au bout. C'est pour cela que
  `notebooks/quality/controles_silver.ipynb` vérifie sa présence, sans que cela suffise à
  garantir l'intégrité.
- **Pas d'isolation** : un lecteur qui lit pendant une écriture peut voir un
  état intermédiaire, et deux écritures en même temps peuvent se mélanger.
- **Pas de mise à jour ni de suppression ligne par ligne** (`UPDATE`,
  `DELETE`, `MERGE`) : il faut réécrire le jeu ou la partition.
- **Pas d'historique des versions** : on ne peut pas revenir à l'état
  d'avant un `overwrite`.
- **Pas de contrôle du schéma à l'écriture** : rien n'empêche d'ajouter dans
  le même répertoire un fichier qui a un schéma différent.

Ces garanties sont apportées par les **formats de table Lakehouse**, comme
Delta Lake, Apache Iceberg ou Apache Hudi. Ils gardent les données en
**fichiers Parquet**, mais ajoutent un **journal de transactions**, ce qui
donne :
- des écritures atomiques ;
- des lectures cohérentes ;
- `MERGE`, `UPDATE` et `DELETE` ;
- le voyage dans le temps (lire une version passée de la table) ;
- l'évolution contrôlée du schéma.

Dans ce TP, Silver et Gold sont des **répertoires Parquet** produits par des
traitements rejouables (`overwrite` à partir des sources). Ce ne sont pas des
tables ACID.
