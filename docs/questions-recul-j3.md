# Questions de recul – Jour 3

Réponses aux questions du §11 du TP.

## 1. Pourquoi est-il nécessaire de vérifier les schémas avant de commencer les transformations ?
Parce que les calculs dépendent des types. Sans vérification, on peut additionner du texte, avoir des arrondis faux sur de l'argent (`double` au lieu de `decimal`) ou prendre un identifiant pour un nombre. Chez nous, `inferSchema` lisait les montants en `double`, `i_rec_end_date` en `string` et le code postal des magasins en nombre (les zéros du début disparaissaient). On a donc écrit les schémas à la main (règle R1).

## 2. Quelle différence existe entre une donnée brute, une donnée Silver et une donnée Gold ?
- **Brute** (Raw) : le fichier tel qu'on l'a reçu, sans titres ni types. On ne le modifie jamais.
- **Silver** : les mêmes données nettoyées, avec les bons types, les règles appliquées et la provenance. Une ligne de vente reste une ligne de vente.
- **Gold** : des données regroupées pour répondre à une question du métier, par exemple le CA par catégorie (9 lignes) ou par mois (60 lignes) au lieu de 667 579 lignes de ventes.

## 3. Pourquoi faut-il connaître la granularité d'une table avant de réaliser une agrégation ?
Pour savoir ce qu'on compte. Une ligne de `store_sales` est une ligne de ticket, pas un ticket : le même produit peut apparaître plusieurs fois dans un ticket (4 136 lignes). Compter les lignes ne donne donc pas le nombre de tickets : il faut compter les tickets différents. Et si on joint une table à la mauvaise granularité, des lignes sont dupliquées et les sommes deviennent fausses.

## 4. Quels risques présente une jointure réalisée sur une clé supposée ?
- Des lignes **en double** si la clé n'est pas unique de l'autre côté : le CA serait compté plusieurs fois.
- Des lignes **perdues ou sans correspondance** si les valeurs ne correspondent pas.
- Un **résultat faux sans message d'erreur**.

C'est pour ça qu'avant chaque jointure (ventes × produits, magasins, dates), on a vérifié que la clé de la table de référence est unique, et que le nombre de lignes est le même avant et après la jointure (0 vente non rapprochée).

## 5. Pourquoi ne faut-il pas supprimer automatiquement les valeurs atypiques ?
Parce qu'une valeur bizarre peut être un vrai cas : un produit offert (prix à 0), une vente à perte (marge négative), un gros panier. Les supprimer fausserait le CA et ferait disparaître une information. On les a gardées et repérées par un indicateur (`ss_prix_nul`, `ss_marge_negative`, `i_cout_superieur_prix`), et le rapport qualité les signale en ALERTE.

## 6. Quels contrôles permettent de vérifier la cohérence d'un jeu de données transformé ?
- Comparer les **volumes** : lignes lues = lignes gardées + lignes mises à l'écart.
- Vérifier que les **totaux** ne changent pas : CA Silver = somme du CA Gold.
- Vérifier les **règles métier** : quantité > 0, montant = quantité × prix.
- Vérifier les **clés** : unicité, aucun vide, chaque vente a un produit, un magasin et une date connus.
- **Relire** les fichiers écrits et comparer leur schéma.

## 7. Pourquoi Parquet est-il adapté aux usages analytiques ?
Les données sont rangées par colonne et compressées. Une analyse lit souvent quelques colonnes sur beaucoup de lignes : Spark ne lit que celles dont il a besoin. Sur `store_sales` complet, Parquet prend 40,6 Mo contre 175,5 Mo en CSV et 480,6 Mo en JSON, et calcule le total en 0,45 s contre environ 2,6 s. C'est aussi le seul des trois formats qui garde les types (`decimal`, `date`) à la relecture.

## 8. Pourquoi Parquet seul ne fournit-il pas les garanties d'une table transactionnelle Lakehouse ?
Un dossier Parquet n'est qu'un ensemble de fichiers :
- si une écriture plante au milieu, il peut rester un dossier à moitié écrit, sans retour en arrière ;
- deux écritures en même temps peuvent se mélanger ;
- il n'y a pas d'historique : avec `overwrite`, l'ancienne version est perdue ;
- on ne peut pas modifier ou supprimer une seule ligne.

Des formats comme Delta Lake ou Apache Iceberg ajoutent un journal des modifications au-dessus des fichiers Parquet pour apporter ces garanties.

## 9. Dans quels cas une base NoSQL pourrait-elle compléter une architecture Data Lake ?
Quand on a besoin de lire ou d'écrire **une seule information très vite**, par exemple afficher l'historique d'achats d'un client sur le site, ou le stock d'un produit en temps réel. Le Data Lake est fait pour analyser beaucoup de données d'un coup, pas pour répondre en quelques millisecondes à une question sur une seule ligne. Une base comme HBase peut stocker ce genre de données, avec une clé bien choisie.

## 10. Quelles limites des données TPCx-BB doivent être prises en compte lors de l'interprétation des résultats ?
- Les données sont **inventées** : 74 % des ventes ont une marge négative, 44 % des produits coûtent plus cher à l'achat qu'à la vente, et les remises tournent autour de 50 %. Ça n'arrive pas dans un vrai magasin.
- Les noms de produits et de marques sont des suites de lettres au hasard, et les dates de fermeture des magasins sont incohérentes (de 1917 à 2141).
- La répartition des catégories est très déséquilibrée (`Music` = 46 % des produits), et c'est ce qui fait sa part de CA.
- Décembre 2005 est incomplet (dernière vente le 13/12/2005) et la devise n'est pas indiquée.
- Ce n'est pas un benchmark officiel : on ne peut tirer aucune conclusion sur les performances.

Les résultats servent à montrer que la chaîne fonctionne, pas à prendre de vraies décisions commerciales.
