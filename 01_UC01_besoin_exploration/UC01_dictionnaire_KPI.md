# Dictionnaire de KPI

Les ventes se trouvent dans deux fichiers :
- `store_sales` : les ventes en magasin ;
- `web_sales` : les ventes sur le site web.

Dans ces fichiers, une ligne = un article vendu (un ticket peut avoir plusieurs lignes).

| KPI | Pour quel profil |
|---|---|
| KPI-01 Chiffre d'affaires | P1 Direction générale |
| KPI-02 Nombre de transactions | Demandé par le TP |
| KPI-03 Panier moyen | Demandé par le TP |
| KPI-04 Quantités vendues | Demandé par le TP |
| KPI-05 Taux de remise | P2 Contrôleur de gestion |

---

### KPI-01 – Chiffre d'affaires

| | |
|---|---|
| Définition | L'argent gagné grâce aux ventes |
| Formule | Somme de `ss_net_paid` + somme de `ws_net_paid` |
| Unité | Euros (on suppose, car la devise n'est pas indiquée) |
| Périmètre | Magasins et site web |
| Fréquence | Chaque mois |
| Sources | `store_sales`, `web_sales` |
| Données manquantes | La devise |
| Limites | Les produits retournés ne sont pas enlevés |

### KPI-02 – Nombre de transactions

| | |
|---|---|
| Définition | Le nombre d'achats (tickets en magasin, commandes sur le web) |
| Formule | Nombre de tickets différents (`ss_ticket_number`) + nombre de commandes différentes (`ws_order_number`) |
| Unité | Nombre d'achats |
| Périmètre | Magasins et site web |
| Fréquence | Chaque mois |
| Sources | `store_sales`, `web_sales` |
| Données manquantes | Aucune |
| Limites | Il ne faut pas compter les lignes, car un ticket peut avoir plusieurs lignes |

### KPI-03 – Panier moyen

| | |
|---|---|
| Définition | Ce qu'un client dépense en moyenne à chaque achat |
| Formule | Chiffre d'affaires ÷ nombre de transactions |
| Unité | Euros par achat |
| Périmètre | Magasins et site web, calculés séparément |
| Fréquence | Chaque mois |
| Sources | `store_sales`, `web_sales` |
| Données manquantes | Aucune |
| Limites | Dépend de KPI-01 et KPI-02 : si l'un est faux, celui-ci l'est aussi |

### KPI-04 – Quantités vendues

| | |
|---|---|
| Définition | Le nombre d'articles vendus |
| Formule | Somme de `ss_quantity` + somme de `ws_quantity` |
| Unité | Nombre d'articles |
| Périmètre | Par produit ou par catégorie |
| Fréquence | Chaque mois |
| Sources | `store_sales`, `web_sales`, `item` |
| Données manquantes | Aucune |
| Limites | Additionner des produits très différents n'a pas beaucoup de sens |

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
