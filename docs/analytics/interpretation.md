# Synthèse décisionnelle : constats, limites et recommandations – TP Jour 4, UC-08 (J4-06)

Les constats ci-dessous reposent sur les deux notebooks d'analyse (chiffres détaillés dans `business-analysis.md`). Pour chaque constat, on distingue le résultat observé, l'interprétation possible, la limite et la recommandation.

> Rappel : TPCx-BB est un jeu **synthétique**. Ces constats illustrent une démarche d'analyse, ils ne décrivent pas une vraie entreprise. Une corrélation ne prouve pas une cause.

## Constat 1 – Le chiffre d'affaires des magasins est stable, sans croissance

| | |
|---|---|
| **Résultat observé** | CA annuel entre 23,0 et 23,7 M€ de 2001 à 2004 (sur l'échantillon de 10 %). Évolution annuelle sur période égale de −1,7 % à +2,8 %, et −2,5 % en 2005 (−7,2 % si on compare l'année entière). Variations mensuelles de ±15 % sans tendance. Les écarts entre mois s'expliquent par leur nombre de jours |
| **Interprétation possible** | L'activité est plate. Le −7,2 % de 2005 vient surtout du mois de décembre incomplet, pas d'une vraie baisse |
| **Limite** | Échantillon de 10 % des tickets, retours non déduits, pas de canal web, données synthétiques. Pas de vérification possible sur le fichier complet, car la chaîne HDFS n'a pas les dates |
| **Recommandation** | Toujours comparer deux années **sur une période égale**, et regarder le **CA par jour de vente** plutôt que le CA mensuel brut. Charger `date_dim` dans la chaîne HDFS pour vérifier la légère baisse de 2005 (−2,5 %) sur le fichier complet |

## Constat 2 – Deux catégories font 72 % du CA, grâce au nombre de leurs produits

| | |
|---|---|
| **Résultat observé** | Music (45,0 %) et Books (26,5 %) font 71,6 % du CA de l'échantillon, et 71,9 % sur le fichier complet. Ce sont aussi les catégories qui ont le plus de produits (75,6 % du catalogue). Leur CA par produit est plus faible que celui de Clothing, Sports ou Home & Kitchen. Le taux de remise est le même partout (environ 50 %) |
| **Interprétation possible** | Le CA dépend fortement de deux catégories, qui pèsent par leur nombre de produits plutôt que par la réussite de chaque produit |
| **Limite** | La marge n'est pas utilisable (coûts générés) : on ne sait pas si ces catégories sont rentables. Le lien entre nombre de produits et CA est une observation, pas une cause démontrée |
| **Recommandation** | Suivre ces deux catégories en priorité (alerte en cas de baisse). Avec des coûts fiables, étudier s'il serait intéressant d'ajouter des produits dans les catégories à fort CA par produit (Clothing, Sports, Home & Kitchen) |

## Constat 3 – Les magasins sont très proches, et leur classement n'est pas fiable

| | |
|---|---|
| **Résultat observé** | Sur l'échantillon : 12 magasins entre 8,91 et 10,14 M€ (max ÷ min = 1,14), tous ouverts sur toute la période. Le CA est plus lié au nombre de tickets (corrélation 0,84) qu'au panier moyen (0,74). Sur le fichier complet : seulement 5 % d'écart (94,04 à 98,95 M€), et le classement change. Sherwood, 1er sur l'échantillon, est dernier sur le fichier complet |
| **Interprétation possible** | Aucun magasin ne se détache vraiment. Les écarts vus sur l'échantillon viennent en partie du hasard de l'échantillon |
| **Limite** | 12 magasins seulement. Une corrélation n'est pas une cause. Le CA n'est rapporté ni à la surface ni au nombre d'employés |
| **Recommandation** | Ne pas classer les magasins à partir de l'échantillon. Pour une décision par magasin, utiliser le fichier complet et calculer le **CA par m²** (`s_floor_space`) et le **CA par employé** (`s_number_employees`), disponibles dans le Silver `stores` |

## Limites générales

- **Canal web absent** : `web_sales` n'a pas été transformée au Jour 3. La question P1 « part magasin / web » reste sans réponse.
- **Échantillon** de 10 % des tickets (`ss_ticket_number` multiple de 10) dans la chaîne principale. Les montants valent environ un dixième du réseau, mais les parts, les taux et les moyennes sont confirmés par le fichier complet (écarts inférieurs à 1 %).
- **Chaîne HDFS** (fichier complet) : pas de dates ni de noms de magasins.
- **Marge** non retenue (74 % de lignes à marge négative), **devise** supposée en euros, **retours** non déduits.
- **Paniers irréalistes** (380 articles et environ 12 900 € par ticket), à cause du générateur : il faut utiliser la médiane en plus de la moyenne.

## Recommandations pour la suite du projet

1. **Charger `date_dim` et `store`** dans la chaîne HDFS, pour vérifier sur le fichier complet l'évolution du CA (KPI-06) et l'analyse par magasin avec les noms.
2. **Ajouter `web_sales`**, pour comparer les magasins et le web en calculant chaque canal séparément.
3. **Garder les contrôles de cohérence** à chaque nouvelle analyse (KPI Silver = Gold, somme par dimension = total), comme dans les deux notebooks.
