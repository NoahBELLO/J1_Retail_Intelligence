# Qualification des données

J'ai utilisé le script `preuves/verifier_relations.py`. Les résultats sont dans `preuves/resultats_relations.csv`.

## 1. Qualité des données

| Vérification | Résultat |
|---|---|
| Toutes les lignes ont le bon nombre de colonnes ? | Oui |
| Les identifiants sont uniques ? | Oui, aucun doublon |
| Les colonnes importantes des ventes sont remplies ? | Oui (date, produit, magasin, ticket, quantité, montants) |
| Les montants sont cohérents ? | Oui : montant = quantité × prix |
| Problèmes trouvés | Espaces en trop dans `customer` et `customer_address`, et la colonne `c_last_review_date` est inutilisable |

**Conclusion** : les données sont plutôt propres. Il faudra enlever les espaces et ignorer `c_last_review_date`.

## 2. Liens entre les tables

Pour chaque lien, j'ai vérifié que chaque numéro de la table de gauche existe bien dans la table de droite.

| Lien | Vides | Introuvables |
|---|---|---|
| Ventes magasin → dates, heures, produits, clients, magasins | 0 | 0 |
| Ventes magasin → promotions | 158 | 0 |
| Ventes web → dates, produits, clients | 0 | 0 |
| Ventes web → sites, pages, entrepôts | environ 160 | 0 |
| Retours (magasin et web) → produits, magasins | 0 | 0 |
| Retours (magasin et web) → motifs | 18 | 0 |
| Stocks → entrepôts | 0 | 0 |
| Stocks → produits | 0 | **232 380** |
| Clics → produits | 0 | 0 |

À chaque fois, c'est un lien « un vers plusieurs » : par exemple, un produit peut apparaître dans plusieurs ventes.

## 3. Ce que j'ai remarqué

- **Stocks** : 180 produits du stock ne sont pas dans `data/item`, mais dans `data_refresh/item`. Il faut donc charger `data_refresh` avant de relier les stocks aux produits.
- **Retours** : chaque retour correspond bien à une vente (même ticket et même produit).
- **Tickets** : un numéro de ticket n'apparaît jamais dans deux magasins différents, il est donc unique dans toute l'entreprise. Un ticket contient de 1 à 14 articles.
- **Identifiant d'une vente** : le couple ticket + produit n'est pas unique (4 038 cas en double). On ne peut donc pas l'utiliser comme identifiant.

## 4. À vérifier plus tard

- Quel est le vrai identifiant d'une ligne de vente ?
- Les clics et les avis peuvent-ils être reliés aux clients ?
- La fusion de `data` et `data_refresh` crée-t-elle des doublons ?
