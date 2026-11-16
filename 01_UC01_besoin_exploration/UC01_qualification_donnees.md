# Qualification des données

Nous avons utilisé deux scripts :
- `preuves/verifier_relations.py` (Noah), dont les résultats sont dans `preuves/resultats_relations.csv` ;
- `05_contribution_individuelle/scripts/etape_d_relations.py` (Lorenzo), qui fait aussi les tests avec `data_refresh`.

## 1. Qualité des données

| Vérification | Résultat |
|---|---|
| Toutes les lignes ont le bon nombre de colonnes ? | Oui |
| Les identifiants des tables de référence sont uniques ? | Oui, aucun doublon, même après ajout de `data_refresh` |
| Les colonnes importantes des ventes sont remplies ? | Oui (date, produit, magasin, ticket, quantité, montants) |
| Les montants sont cohérents ? | Oui : montant = quantité × prix |
| Les types sont les mêmes des deux côtés d'un lien ? | Oui : tous les identifiants sont des nombres entiers |
| Problèmes trouvés | Voir `UC01_inventaire_sources.md` section 6 (espaces en trop, colonnes inutilisables, valeurs impossibles) |

## 2. Liens entre les tables

Pour chaque lien, on a vérifié que chaque numéro de la table de gauche existe dans la table de droite.

| Lien | Vides | Introuvables |
|---|---|---|
| Ventes magasin → dates, heures, produits, clients, magasins | 0 | 0 |
| Ventes magasin → promotions | 158 | 0 |
| Ventes web → dates, produits, clients | 0 | 0 |
| Ventes web → sites, pages, entrepôts, modes de livraison | environ 160 | 0 |
| Retours (magasin et web) → produits, magasins | 0 | 0 |
| Retours (magasin et web) → motifs | 18 | 0 |
| Retours `data` → ventes (même ticket et même produit) | 0 | 0 |
| Stocks → entrepôts | 0 | 0 |
| Stocks → produits (avec `data` seul) | 0 | **232 380** |
| Stocks → produits (avec `data_refresh`) | 0 | 0 |
| Retours de `data_refresh` → ventes | 0 | **407 en magasin, 371 sur le web** |
| Clics → produits | 0 | 0 |

À chaque fois, c'est un lien « un vers plusieurs » : par exemple, un produit peut apparaître dans plusieurs ventes. Tous les produits et tous les magasins ont au moins une vente. 60 434 clients sur 100 000 ont fait au moins un achat.

## 3. Ce que nous avons remarqué

- **Stocks** : 180 produits du stock (numéros 17 820 à 17 999) n'existent que dans `data_refresh/item`. Il faut donc charger les produits de `data_refresh` avant les stocks.
- **Tickets** : un ticket est toujours dans un seul magasin, à une seule date, pour un seul client. Il contient de 1 à 14 articles.
- **Tickets et commandes** : les numéros de ticket (magasin) et de commande (web) vont tous les deux de 0 à 89 099, mais ce sont deux séries différentes. Il ne faut **jamais** relier un ticket et une commande par leur numéro.
- **Retours** : le couple ticket + produit n'étant pas unique, 909 retours (470 en magasin, 439 sur le web) correspondent à **deux** lignes de vente. Une jointure mal faite doublerait leur montant.
- **Client du retour** : c'est le même client que l'acheteur dans 90 % des cas en magasin et 86 % sur le web.
- **`c_first_sales_date_sk`** (date du premier achat du client) ne correspond jamais au vrai premier achat : cette colonne n'est pas fiable.
- **Stocks et magasins** : aucune colonne ne relie un entrepôt à un magasin. On ne peut pas savoir quel magasin est livré par quel entrepôt.

## 4. Liens à confirmer

| Lien | Ce que nous avons trouvé | Statut |
|---|---|---|
| Clics → ventes web | Les 668 052 clics avec achat correspondent exactement aux 668 052 lignes de `web_sales`. `wcs_sales_sk` est en fait un numéro de commande | Confirmé par les données, mais pas documenté |
| Avis → ventes web (`pr_order_sk`) | 99 % des avis retrouvent leur commande, mais l'auteur n'est l'acheteur que dans 92 % des cas | Probable |
| Clics et avis → clients (`wcs_user_sk`, `pr_user_sk`) | Aucun numéro introuvable | Probable, à confirmer |
| Prix concurrents → dates (`imp_start_date`) | Aucun numéro introuvable | Probable |
| Retours de `data_refresh` → ventes | 778 retours sans vente | À demander au formateur. En attendant, les mettre de côté |
| Identifiant unique d'une ligne de vente | Le couple ticket + produit ne suffit pas | Il faudra ajouter un numéro de ligne |

## 5. Modèle retenu

Les liens vérifiés (aucun numéro introuvable) permettent d'organiser les données en étoile :
- `store_sales` → `item`, `customer`, `store`, `date_dim`, `time_dim`, `promotion` ;
- `web_sales` → `item`, `customer`, `web_site`, `date_dim`, `time_dim`, `warehouse`, `ship_mode`, `promotion` ;
- `inventory` → `item`, `warehouse`, `date_dim` (à condition de charger `data_refresh/item`).
