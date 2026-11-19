# Statistiques descriptives et analyses métier (UC-08, étapes 3 à 5)

Les résultats viennent du notebook `analytics/notebooks/TP4_Retail_Intelligence.ipynb` et sont exportés dans `analytics/outputs/`.

## 1. Statistiques descriptives (`statistiques.csv`)

| Niveau | Variable | N | Vides | Min | Max | Moyenne | Médiane | Écart-type | Somme |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ligne de vente | quantité | 66 593 | 0 | 1 | 100 | 50,85 | 51 | 28,92 | 3 386 076 |
| ligne de vente | prix de vente unitaire (EUR) | 66 593 | 0 | 0,00 | 194,54 | 37,83 | 27,44 | 34,57 | *non additif* |
| ligne de vente | montant net payé (EUR) | 66 593 | 0 | 0,00 | 17 746,82 | 1 738,20 | 882,39 | 2 189,21 | 115 752 176,68 |
| ligne de vente | montant de remise (EUR) | 66 593 | 0 | 0,00 | 17 233,30 | 1 924,95 | 1 052,20 | 2 286,15 | 128 188 499,09 |
| ticket | montant du ticket (EUR) | 8 910 | 0 | 0,00 | 60 903,90 | 12 991,27 | 11 718,01 | 9 111,99 | 115 752 176,68 |
| ticket | articles par ticket | 8 910 | 0 | 1 | 1 020 | 380,03 | 373 | 217,79 | 3 386 076 |
| ticket | lignes par ticket | 8 910 | 0 | 1 | 14 | 7,47 | 7 | 4,02 | – |

**Répartition par catégorie** (`repartition_categories.csv`) : Music 45,2 % des lignes, Books 26,6 %, Movies & TV 6,5 %, et chacune des six autres entre 2,4 % et 4,9 %.

**Évolution temporelle des volumes** : de 13 381 à 13 590 lignes et de 1 799 à 1 803 tickets par an de 2001 à 2004, avec des ventes tous les jours. 2005 compte 12 755 lignes et 1 709 tickets sur 347 jours (dernière vente le 13/12/2005).

## 2. Analyses métier

### A1 – Comment évolue le CA chaque mois et par rapport à l'année d'avant ? (P1, indispensable)

* **Données** : Gold `ca_mensuel` (60 mois). Le total est vérifié égal au CA Silver.
* **Méthode** : CA mensuel ; évolution par rapport au même mois N-1 ; indice saisonnier = CA moyen du mois (2001-2004) / moyenne × 100 ; décembre 2005 exclu des comparaisons.
* **Résultats** (`analyse_ca_mensuel.csv`, `analyse_saisonnalite.csv`) : CA mensuel moyen de 1,95 M EUR, coefficient de variation de 6,1 %. Évolution N/N-1 mensuelle de −14,96 % à +14,94 % (médiane −1,22 %, 22 hausses et 25 baisses). L'indice saisonnier va de 93,5 (février) à 104,2 (mai) et suit le nombre de jours du mois (31 jours ≈ 102, 30 jours ≈ 98, février 93,5).
* **Interprétation** : le CA est stable, sans tendance ni vraie saisonnalité commerciale.
* **Limites** : l'échantillon de 10 % rend les mois plus bruités ; les données sont synthétiques.

### A2 – Quels produits et catégories génèrent le plus de CA ? (P4, indispensable)

* **Données** : Gold `ca_marge_par_categorie` et `top10_produits`.
* **Méthode** : CA, part du CA, nombre de produits vendus et CA par produit, pour chaque catégorie.
* **Résultats** (`analyse_categories.csv`) :

| Catégorie | CA (EUR) | Part | Produits vendus | CA par produit (EUR) | Taux de remise |
|---|---:|---:|---:|---:|---:|
| Music | 52 109 109,95 | 45,02 % | 7 164 | 7 273,75 | 49,99 % |
| Books | 30 720 062,81 | 26,54 % | 4 688 | 6 552,91 | 50,04 % |
| Movies & TV | 7 342 177,59 | 6,34 % | 1 121 | 6 549,67 | 50,35 % |
| Clothing & Accessories | 5 768 943,01 | 4,98 % | 528 | 10 926,03 | 49,27 % |
| Electronics | 5 682 478,05 | 4,91 % | 609 | 9 330,83 | 49,91 % |
| Home & Kitchen | 4 291 458,75 | 3,71 % | 419 | 10 242,14 | 49,50 % |
| Sports & Outdoors | 4 138 485,68 | 3,58 % | 401 | 10 320,41 | 49,41 % |
| Toys & Games | 2 901 166,65 | 2,51 % | 348 | 8 336,69 | 49,44 % |
| Tools & Home Improvement | 2 798 294,19 | 2,42 % | 358 | 7 816,46 | 51,60 % |

  Les 10 premiers produits représentent 6,92 % du CA, sur 15 636 produits vendus.
* **Interprétation** : Music et Books pèsent 71,6 % du CA grâce à leur large assortiment, mais leur CA par produit est plus faible que celui de Clothing, Sports ou Home & Kitchen.
* **Limites** : la marge n'est pas utilisable. Les 4 premiers produits, aux identifiants consécutifs, sont probablement un artefact du générateur, à vérifier.

### A3 – Quelles différences observe-t-on entre les magasins ? (P1 / P4)

* **Données** : Gold `ca_marge_par_magasin` (12 magasins) et les dates de première et de dernière vente tirées du Silver.
* **Méthode** : CA, tickets et panier moyen par magasin ; corrélation du CA avec chacun des deux facteurs.
* **Résultats** (`ventes_par_magasin.csv`) : CA de 8,91 M EUR (Egypt) à 10,14 M EUR (Sherwood), soit un rapport max / min de 1,14 et un coefficient de variation de 4,67 %. Corrélation du CA avec les transactions : 0,84 ; avec le panier moyen : 0,74. Les 12 magasins vendent de janvier 2001 à décembre 2005.
* **Interprétation** : le réseau est homogène, et les écarts viennent d'abord de la fréquentation.
* **Limites** : 12 points seulement ; CA non rapporté à la surface ni à l'effectif.

## 3. Visualisations (`analytics/visualizations/`)

| Fichier | Type | Analyse | Message |
|---|---|---|---|
| `evolution_ventes_mensuelles.png` | Courbe + moyenne mobile 12 mois | A1 | CA plat autour de 1,95 M EUR par mois ; décembre 2005 incomplet signalé en gris |
| `ca_par_categorie.png` | Barres horizontales + part du CA | A2 | Music et Books dominent (71,6 %) |
| `ventes_par_magasin.png` | Barres horizontales + ligne de moyenne | A3 | Magasins proches (écart max de 14 %) ; tickets et panier dans les barres |
| `distribution_montant_tickets.png` | Histogramme (30 classes) + moyenne / médiane | Statistiques | Distribution asymétrique : moyenne de 12 991 EUR > médiane de 11 718 EUR |

Chaque graphique a un titre explicite, des axes avec leur unité, une légende quand il y a plusieurs séries et la source en bas. Une interprétation suit chaque graphique dans le notebook.
