# Preuves UC-01

Ces fichiers montrent les observations et les contrôles **réellement faits** sur les données du kit `retail_project.zip`. Les données elles-mêmes ne sont pas dans le dépôt, à cause de leur taille (environ 1 Go).

## 1. Documentation des sources

| Fichier | Ce qu'il montre |
|---|---|
| `arborescence_donnees.txt` | La liste des 34 fichiers `.dat` des dossiers `data/` et `data_refresh/`, avec la taille de chacun. Sert de capture de l'arborescence des données |
| `apercu_fichiers.txt` | Les 3 premières lignes de 5 fichiers (`store_sales`, `web_sales`, `customer`, `item`, `web_clickstreams`). Montre le format : colonnes séparées par `|`, pas de ligne de titres, espaces en trop dans `customer` |
| `tpcxbb_schema.json` | Les noms et les types des colonnes de chaque table, repris du schéma officiel TPCx-BB. Les fichiers n'ayant pas de ligne de titres, c'est ce schéma qui permet de nommer les colonnes |

## 2. Résultats de l'exploration (fichiers, formats, volumes)

| Fichier | Produit par | Ce qu'il montre |
|---|---|---|
| `inventaire_fichiers.csv` | `explorer_donnees.py` (Noah) | Pour chaque fichier : dossier, taille, nombre de lignes, nombre de colonnes, lignes avec un mauvais nombre de colonnes (0 partout), doublons dans l'identifiant des tables de référence (0 partout) |
| `etape_c_profil.json` | `etape_c_profilage.py` (Lorenzo) | Le profil détaillé de chaque colonne : type, minimum, maximum, nombre de valeurs différentes, unicité. Contient aussi les tests de doublons sur les identifiants composés (par exemple 4 136 lignes en trop pour ticket + produit dans `store_sales`) |

## 3. Contrôles qualité (valeurs vides, doublons, cohérence)

| Fichier | Produit par | Ce qu'il montre |
|---|---|---|
| `inventaire_colonnes.csv` | `explorer_donnees.py` (Noah) | Pour chaque colonne : type observé, nombre et pourcentage de valeurs vides, nombre de valeurs avec des espaces en trop. Par exemple : 90 % de `wcs_sales_sk` vides, espaces dans toutes les valeurs de `customer` |
| `etape_c_profil.json` | `etape_c_profilage.py` (Lorenzo) | Les valeurs vides, les valeurs qui ne peuvent pas être converties dans le bon type, et les doublons |

## 4. Justification des relations entre les tables et des KPI

| Fichier | Produit par | Ce qu'il montre |
|---|---|---|
| `resultats_relations.csv` | `verifier_relations.py` (Noah) | Pour 20 liens entre tables : nombre de valeurs vides et de valeurs introuvables. Seul problème : 232 380 lignes de `inventory` avec un produit absent de `data/item`. Montre aussi qu'un ticket n'est jamais dans deux magasins, et que chaque retour correspond à une vente |
| `etape_d_relations.json` | `etape_d_relations.py` (Lorenzo) | Les mêmes vérifications sur plus de liens, sur `data` seul puis sur `data` + `data_refresh`. Avec `data_refresh`, les produits du stock sont tous retrouvés, mais 407 retours magasin et 371 retours web n'ont pas de vente |

Ces résultats justifient les KPI : les colonnes utilisées dans les formules (`ss_net_paid`, `ss_quantity`, `ss_ticket_number`…) sont toujours remplies et reliées aux produits, magasins et dates. La cohérence des montants (montant = quantité × prix) est décrite dans `UC01_qualification_donnees.md`.

## 5. Les scripts

| Script | Auteur | Comment le relancer (depuis ce dossier) |
|---|---|---|
| `explorer_donnees.py` | Noah | `python explorer_donnees.py <chemin vers retail_project>` |
| `verifier_relations.py` | Noah | `python verifier_relations.py <chemin vers retail_project/data>` |
| `etape_c_profilage.py` | Lorenzo | `python etape_c_profilage.py <chemin vers retail_project> etape_c_profil.json` |
| `etape_d_relations.py` | Lorenzo | `python etape_d_relations.py <chemin vers retail_project> etape_d_relations.json` |

`etape_d_relations.py` a été légèrement modifié pour enlever les espaces en trop dans `customer` et `customer_address` avant de convertir les valeurs. Sans cette modification, il ne fonctionnait pas sur notre copie des données.
