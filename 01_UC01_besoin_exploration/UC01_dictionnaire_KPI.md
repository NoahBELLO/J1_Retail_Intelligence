# Dictionnaire de KPI

Les ventes se trouvent dans deux fichiers :
- `store_sales` : les ventes en magasin ;
- `web_sales` : les ventes sur le site web.

Dans ces fichiers, une ligne = un article vendu (un ticket a en moyenne 7,5 lignes).

| KPI | Pour quel profil |
|---|---|
| KPI-01 Chiffre d'affaires | P1 Direction générale, P4 Direction commerciale |
| KPI-02 Nombre de transactions | Demandé par le TP |
| KPI-03 Panier moyen | Demandé par le TP |
| KPI-04 Quantités vendues | P4 Direction commerciale |
| KPI-05 Taux de remise | P2 Contrôleur de gestion |
| KPI-06 Évolution du chiffre d'affaires | P1 Direction générale |

---

### KPI-01 – Chiffre d'affaires

| | |
|---|---|
| Définition | L'argent gagné grâce aux ventes, remises déduites, sans les taxes |
| Formule | Somme de `ss_net_paid` + somme de `ws_net_paid` |
| Unité | Euros (on suppose, car la devise n'est pas indiquée) |
| Périmètre | Magasins et site web, par canal, magasin, produit, catégorie ou période |
| Fréquence | Chaque jour, regroupé par semaine, mois et année |
| Sources | `store_sales`, `web_sales`, `date_dim`, `item`, `store` |
| Données manquantes | La devise. Pas de ventes par catalogue (`catalog_sales` absent) |
| Limites | Les produits retournés ne sont pas enlevés. Un CA élevé ne veut pas dire une marge élevée. Pour le web, il ne faut pas prendre `ws_net_paid_inc_ship` (avec les frais de port), sinon le CA web est gonflé d'environ 55 % |

### KPI-02 – Nombre de transactions

| | |
|---|---|
| Définition | Le nombre d'achats (tickets en magasin, commandes sur le web) |
| Formule | Nombre de tickets différents (`ss_ticket_number`) + nombre de commandes différentes (`ws_order_number`) |
| Unité | Nombre d'achats |
| Périmètre | Magasins et site web, par magasin, canal et période |
| Fréquence | Chaque jour |
| Sources | `store_sales`, `web_sales`, `date_dim`, `store` |
| Données manquantes | Aucune valeur vide dans ces colonnes |
| Limites | Il ne faut pas compter les lignes, car un ticket a plusieurs lignes. Il faut compter les tickets et les commandes **séparément** : le ticket n°44 et la commande web n°44 sont deux achats différents. Une transaction n'est pas un client (un client peut acheter plusieurs fois) |

### KPI-03 – Panier moyen

| | |
|---|---|
| Définition | Ce qu'un client dépense en moyenne à chaque achat |
| Formule | Chiffre d'affaires ÷ nombre de transactions |
| Unité | Euros par achat |
| Périmètre | Magasins et site web, calculés séparément, par magasin et période |
| Fréquence | Chaque semaine et chaque mois |
| Sources | `store_sales`, `web_sales`, `date_dim`, `store` |
| Données manquantes | Les mêmes que pour KPI-01 et KPI-02 |
| Limites | Quelques très grosses commandes font monter la moyenne. Mélanger magasin et web fausse le résultat |

### KPI-04 – Quantités vendues

| | |
|---|---|
| Définition | Le nombre d'articles vendus |
| Formule | Somme de `ss_quantity` + somme de `ws_quantity` |
| Unité | Nombre d'articles |
| Périmètre | Par produit, catégorie, magasin, entrepôt et période |
| Fréquence | Chaque jour |
| Sources | `store_sales`, `web_sales`, `item`, `date_dim` |
| Données manquantes | Aucune valeur vide |
| Limites | Additionner des produits très différents n'a pas beaucoup de sens (une chaussette = une télé). Les retours ne sont pas enlevés |

### KPI-05 – Taux de remise

| | |
|---|---|
| Définition | La part du prix normal enlevée grâce aux remises |
| Formule | Somme des remises (`ss_ext_discount_amt`) ÷ somme des prix normaux (`ss_ext_list_price`) × 100 |
| Unité | % |
| Périmètre | Magasins (et pareil pour le web avec `ws_`) |
| Fréquence | Chaque mois |
| Sources | `store_sales`, `web_sales` |
| Données manquantes | Aucune |
| Limites | On trouve environ 50 % de remise, ce qui est très élevé : les données sont fictives |

### KPI-06 – Évolution du chiffre d'affaires

| | |
|---|---|
| Définition | De combien le CA a augmenté ou baissé par rapport à la même période de l'année d'avant |
| Formule | (CA période N − CA période N-1) ÷ CA période N-1 × 100 |
| Unité | % |
| Périmètre | Par canal, magasin, catégorie |
| Fréquence | Chaque mois et chaque année |
| Sources | `store_sales`, `web_sales`, `date_dim` (`d_year`, `d_moy`) |
| Données manquantes | Les ventes vont de 2001 à 2005 : pas d'année d'avant pour 2001 |
| Limites | Décembre 2005 est incomplet dans `data/`. Le résultat dépend des saisons et des événements. Une hausse peut venir d'une ouverture de magasin plutôt que d'une vraie croissance |
