# Contribution Lorenzo

## UC1

### ETAPE A

- Direction commerciale :
  - Performance des ventes et des produits.
  - Quels sont les produits et catégories qui génèrent le plus de Chiffre d'Affaires ?
    - Décision : mettre en avant les catégories les plus rentables.
    - Priorité : **Indispensable** (indicateur de base du pilotage commercial, impact direct sur le CA)
  - Comment se répartit le Chiffre d'Affaires entre les magasins et le web ?
    - Décision : réallouer les investissements entre le web et les magasins.
    - Priorité : **Utile** (décision stratégique, mais prise sur un rythme trimestriel ou annuel)

---

- Responsable des stocks :
  - Disponibilité et mouvements de stock.
  - Quels produits sont en rupture ou en surstock ?
    - Décision : ajuster les seuils de réapprovisionnement et les quantités commandées, et déstocker les surplus.
    - Priorité : **Indispensable** (une rupture fait perdre des ventes, un surstock immobilise de l'argent)
  - Quels modes de livraison et quels entrepôts causent le plus de retards ?
    - Décision : changer de transporteur ou de mode de livraison, et réaffecter les commandes vers les entrepôts les plus performants.
    - Priorité : **Complémentaire** (concerne seulement le canal web, c'est une optimisation logistique)

---

- Responsable de magasin :
  - Suivi de son établissement
  - Comment évoluent le Chiffre d'Affaires par tranche horaire ?
    - Décision : ajuster les horaires d'ouverture et le personnel en fonction des périodes de forte affluence.
    - Priorité : **Utile** (optimise les ressources, mais n'est pas bloquant)
  - Quel est le taux de retour dans mon magasin ?
    - Décision : identifier les causes des retours et améliorer la qualité des produits ou le service client.
    - Priorité : **Complémentaire** (amélioration continue, concerne une petite part des ventes)

## Étape B – Indicateurs

---

### 1. Chiffre d'affaires (CA)

1. **Nom** : Chiffre d'affaires net
2. **Définition métier** : montant encaissé sur les ventes, remises déduites et hors taxes.
3. **Formule** : `SUM(ss_net_paid) + SUM(ws_net_paid)`
4. **Unité** : € (devise non précisée dans le jeu de données)
5. **Périmètre** : magasins + web, déclinable par canal, magasin, produit, catégorie et période
6. **Fréquence** : quotidienne, agrégée par semaine, mois et année
7. **Sources** : `store_sales`, `web_sales`, `date_dim`, `item`, `store`, `web_site`
8. **Données manquantes** : pas de canal catalogue (`catalog_sales` absent) ; certaines lignes ont des clés NULL (date, article, magasin) ; devise non renseignée
9. **Limites** : les retours ne sont pas déduits (il faudrait `store_returns` / `web_returns` pour un CA net de retours) ; un CA élevé ne veut pas dire une marge élevée

---

### 2. Nombre de transactions

1. **Nom** : Nombre de transactions
2. **Définition métier** : nombre de tickets de caisse (magasin) et de commandes (web) distincts.
3. **Formule** : `COUNT(DISTINCT ss_ticket_number) + COUNT(DISTINCT ws_order_number)`
4. **Unité** : nombre de transactions
5. **Périmètre** : magasins + web, par magasin, canal et période
6. **Fréquence** : quotidienne
7. **Sources** : `store_sales`, `web_sales`, `date_dim`, `store`
8. **Données manquantes** : pas de canal catalogue ; tickets dont le client est NULL (client anonyme)
9. **Limites** : une transaction n'est pas un client unique (un même client peut passer plusieurs fois) ; les numéros de ticket et de commande se comptent séparément par canal

---

### 3. Panier moyen

1. **Nom** : Panier moyen
2. **Définition métier** : montant moyen dépensé par transaction.
3. **Formule** : `CA net / Nombre de transactions`
4. **Unité** : € par transaction
5. **Périmètre** : par canal, magasin et période (à calculer séparément magasin / web)
6. **Fréquence** : hebdomadaire et mensuelle
7. **Sources** : `store_sales`, `web_sales`, `date_dim`, `store`
8. **Données manquantes** : mêmes que pour le CA et les transactions
9. **Limites** : sensible aux valeurs extrêmes (quelques grosses commandes font monter la moyenne) ; mélanger magasin et web fausse la lecture

---

### 4. Quantités vendues

1. **Nom** : Quantités vendues
2. **Définition métier** : nombre d'articles vendus.
3. **Formule** : `SUM(ss_quantity) + SUM(ws_quantity)`
4. **Unité** : nombre d'unités
5. **Périmètre** : par produit, catégorie, magasin, entrepôt et période
6. **Fréquence** : quotidienne
7. **Sources** : `store_sales`, `web_sales`, `item`, `date_dim`
8. **Données manquantes** : quantités NULL sur certaines lignes ; pas de canal catalogue
9. **Limites** : additionne des produits très différents (une unité de chaussette = une unité de télé) ; les retours ne sont pas déduits

---

### 5. Évolution des ventes

1. **Nom** : Taux d'évolution du CA
2. **Définition métier** : variation du CA entre une période et la même période de l'année précédente.
3. **Formule** : `(CA période N − CA période N-1) / CA période N-1 × 100`
4. **Unité** : %
5. **Périmètre** : par canal, magasin, catégorie
6. **Fréquence** : mensuelle et annuelle
7. **Sources** : `store_sales`, `web_sales`, `date_dim` (`d_year`, `d_moy`)
8. **Données manquantes** : la plage de dates couverte est limitée (vérifier les années réellement présentes dans les ventes) ; un magasin ouvert ou fermé en cours de période n'a pas d'historique comparable
9. **Limites** : sensible à la saisonnalité et aux événements ponctuels ; une hausse peut venir d'une ouverture de magasin plutôt que d'une vraie croissance
