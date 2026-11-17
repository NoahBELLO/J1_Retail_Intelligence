# Cadrage métier

## Contexte

Retail Intelligence est une enseigne de distribution qui vend à la fois en magasin (12 magasins) et sur un site web. Ses données viennent de plusieurs systèmes : ventes, produits, clients, magasins, stocks, mais aussi navigation web et avis clients. Les directions commerciale et financière veulent des indicateurs cohérents pour comparer les performances et comprendre l'évolution de l'activité.

Les données utilisées viennent du jeu TPCx-BB : ce sont des données **fictives**, qui servent de support au projet.

## Objectifs métier

- Suivre les ventes et leur évolution dans le temps.
- Comparer les magasins et les canaux (magasin et web).
- Connaître les produits et les catégories qui se vendent le mieux.
- Suivre les remises, les retours et les stocks.
- Disposer de données fiables pour toutes ces analyses.

## Utilisateurs concernés

| # | Profil | Ce qu'il fait | Ce qu'il regarde | À quelle fréquence |
|---|---|---|---|---|
| P1 | Direction générale | Décide de la stratégie de l'entreprise, choisit où investir (magasins ou site web) et fixe les objectifs de l'année | Toute l'entreprise, magasin et web | Chaque mois et chaque année |
| P2 | Contrôleur de gestion | Suit le chiffre d'affaires, les marges et les remises, et prévient la direction quand les chiffres ne sont pas bons | L'entreprise, chaque magasin, chaque catégorie de produits | Chaque mois |
| P3 | Équipe Data | Récupère les données des différents systèmes, vérifie qu'elles sont correctes, les documente et les met à disposition des autres équipes | Les fichiers et les tables de données | À chaque nouveau chargement de données |
| P4 | Direction commerciale | Suit la performance des ventes et des produits, décide quels produits et quelles catégories mettre en avant | Les produits, les catégories, les canaux (magasin et web) | Chaque semaine et chaque mois |
| P5 | Responsable des stocks | Suit la disponibilité des produits et les mouvements de stock, décide des réapprovisionnements | Les produits et les entrepôts | Chaque semaine |
| P6 | Responsable de magasin | Suit l'activité de son magasin, organise le personnel et les horaires | Son magasin | Chaque jour et chaque semaine |
