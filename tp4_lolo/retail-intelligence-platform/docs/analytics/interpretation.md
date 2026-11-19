# Interprétation : constats, limites et recommandations (UC-08, étape 6)

Les constats ci-dessous reposent sur les résultats du notebook `analytics/notebooks/TP4_Retail_Intelligence.ipynb` (chiffres détaillés dans `business-analysis.md`). Pour chaque constat, on distingue le résultat observé, l'interprétation possible, la limite et la recommandation.

Rappel : TPCx-BB est un jeu **synthétique**. Ces constats illustrent une démarche d'analyse et ne décrivent pas une entreprise réelle. Une corrélation ne démontre pas une causalité.

## Constat 1 – Le chiffre d'affaires des magasins est stable, sans croissance

| | |
|---|---|
| **Résultat observé** | CA annuel entre 23,0 et 23,7 M EUR (2001-2004). Évolution annuelle sur période égale de −1,7 % à +2,8 %, et −2,5 % en 2005 (−7,2 % en brut). Variations mensuelles de ±15 % sans tendance. Les écarts entre mois s'expliquent par leur nombre de jours. |
| **Interprétation possible** | Activité plate. Le −7,2 % de 2005 vient surtout du mois de décembre incomplet, pas d'un décrochage. |
| **Limite** | Échantillon de 10 % des tickets, retours non déduits, canal web absent, données synthétiques. |
| **Recommandation** | Toujours présenter l'évolution N/N-1 **sur période égale** et le **CA par jour de vente** plutôt que le CA mensuel brut. Confirmer la légère baisse de 2005 (−2,5 %) sur le fichier complet avant d'en tirer une conclusion. |

## Constat 2 – Deux catégories font 72 % du CA, grâce à leur assortiment

| | |
|---|---|
| **Résultat observé** | Music 45,0 % et Books 26,5 % du CA. Ce sont aussi les catégories avec le plus de produits (7 164 et 4 688 sur 15 636). Leur CA par produit est inférieur à celui de Clothing, Sports ou Home & Kitchen. Le taux de remise est identique partout (≈ 50 %). |
| **Interprétation possible** | Forte dépendance à deux catégories, qui pèsent par leur largeur de gamme plutôt que par la performance de chaque produit. |
| **Limite** | Marge inutilisable (coûts générés) : on ne sait pas si ces catégories sont rentables. Le lien assortiment → CA est une observation, pas une cause démontrée. |
| **Recommandation** | Suivre ces deux catégories en priorité (alerte en cas de baisse). Étudier, avec des coûts fiables, si élargir l'offre des catégories à fort CA par produit (Clothing, Sports, Home & Kitchen) serait intéressant. |

## Constat 3 – Les magasins sont homogènes, leurs écarts viennent de la fréquentation

| | |
|---|---|
| **Résultat observé** | 12 magasins entre 8,91 et 10,14 M EUR (max / min = 1,14 ; coefficient de variation 4,7 %), tous actifs sur toute la période. Le CA est plus lié au nombre de tickets (r = 0,84) qu'au panier moyen (r = 0,74). |
| **Interprétation possible** | Aucun magasin ne décroche. Le meilleur magasin attire un peu plus de tickets. |
| **Limite** | 12 points seulement, une corrélation qui n'est pas une causalité, et un CA non rapporté à la surface ni à l'effectif. |
| **Recommandation** | Avant tout classement ou toute décision par magasin, calculer le **CA par m²** (`s_floor_space`) et le **CA par employé** (`s_number_employees`), disponibles dans le Silver `stores`. |

## Limites générales

* **Canal web absent** : `web_sales` n'a pas été transformé au TP3, donc la question P1 « part magasin / web » reste sans réponse.
* **Échantillon** de 10 % des tickets (`ss_ticket_number` multiple de 10). Les totaux correspondent à environ un dixième du réseau.
* **Marge** non retenue (74 % de lignes à marge négative), **devise** supposée en euros, **retours** non déduits.
* **Paniers irréalistes** (380 articles par ticket) dus au générateur : utiliser la médiane en plus de la moyenne.
