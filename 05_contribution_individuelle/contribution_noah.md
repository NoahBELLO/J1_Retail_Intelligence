# Contribution Noah

## UC1

### ETAPE A

- Direction générale :
  - Décide de la stratégie, choisit où investir (magasins ou web) et fixe les objectifs de l'année.
  - Comment évolue le chiffre d'affaires chaque mois et par rapport à l'année d'avant ?
    - Décision : revoir les objectifs de l'année, lancer des actions si les ventes baissent.
    - Priorité : **Indispensable** (indicateur principal pour suivre l'entreprise)
  - Quelle part du chiffre d'affaires vient des magasins et quelle part vient du site web ?
    - Décision : investir davantage dans les magasins ou dans le site web.
    - Priorité : **Indispensable** (décision qui engage beaucoup d'argent)

---

- Contrôleur de gestion :
  - Suit le chiffre d'affaires, les marges et les remises, et prévient la direction quand les chiffres ne sont pas bons.
  - Quelle marge fait chaque magasin, chaque canal et chaque catégorie de produits ?
    - Décision : repérer ce qui n'est pas rentable et ajuster les budgets.
    - Priorité : **Indispensable** (vérifier la rentabilité est son rôle principal)
  - Quel est le niveau moyen des remises, et augmente-t-il avec le temps ?
    - Décision : limiter les remises, fixer un maximum.
    - Priorité : **Utile** (trop de remises fait baisser la marge)

---

- Équipe Data :
  - Récupère les données, vérifie qu'elles sont correctes, les documente et les met à disposition.
  - Les données reçues sont-elles complètes et correctes (valeurs manquantes, doublons, identifiants qui ne correspondent à rien) ?
    - Décision : accepter, corriger ou refuser les données, et prévenir l'équipe qui les a envoyées.
    - Priorité : **Indispensable** (si les données sont fausses, tous les indicateurs sont faux)
  - Quand de nouvelles données arrivent, sont-elles bien ajoutées sans rien perdre et sans doublon ?
    - Décision : valider le chargement ou le refaire.
    - Priorité : **Utile** (les chiffres doivent rester cohérents d'un mois à l'autre)

## Étape B – Indicateurs

---

### 1. Chiffre d'affaires

1. **Nom** : Chiffre d'affaires
2. **Définition métier** : l'argent gagné grâce aux ventes.
3. **Formule** : `SUM(ss_net_paid) + SUM(ws_net_paid)`
4. **Unité** : euros (supposé, la devise n'est pas indiquée)
5. **Périmètre** : magasins et site web
6. **Fréquence** : chaque mois
7. **Sources** : `store_sales`, `web_sales`
8. **Données manquantes** : la devise
9. **Limites** : les produits retournés ne sont pas enlevés

---

### 2. Nombre de transactions

1. **Nom** : Nombre de transactions
2. **Définition métier** : le nombre d'achats (tickets en magasin, commandes sur le web).
3. **Formule** : `COUNT(DISTINCT ss_ticket_number) + COUNT(DISTINCT ws_order_number)`
4. **Unité** : nombre d'achats
5. **Périmètre** : magasins et site web
6. **Fréquence** : chaque mois
7. **Sources** : `store_sales`, `web_sales`
8. **Données manquantes** : aucune
9. **Limites** : il ne faut pas compter les lignes, car un ticket peut avoir plusieurs lignes

---

### 3. Panier moyen

1. **Nom** : Panier moyen
2. **Définition métier** : ce qu'un client dépense en moyenne à chaque achat.
3. **Formule** : `Chiffre d'affaires / Nombre de transactions`
4. **Unité** : euros par achat
5. **Périmètre** : magasins et site web, calculés séparément
6. **Fréquence** : chaque mois
7. **Sources** : `store_sales`, `web_sales`
8. **Données manquantes** : aucune
9. **Limites** : si le CA ou le nombre de transactions est faux, le panier moyen l'est aussi

---

### 4. Quantités vendues

1. **Nom** : Quantités vendues
2. **Définition métier** : le nombre d'articles vendus.
3. **Formule** : `SUM(ss_quantity) + SUM(ws_quantity)`
4. **Unité** : nombre d'articles
5. **Périmètre** : par produit ou par catégorie
6. **Fréquence** : chaque mois
7. **Sources** : `store_sales`, `web_sales`, `item`
8. **Données manquantes** : aucune
9. **Limites** : additionner des produits très différents n'a pas beaucoup de sens

---

### 5. Taux de remise

1. **Nom** : Taux de remise
2. **Définition métier** : la part du prix normal enlevée grâce aux remises.
3. **Formule** : `SUM(ss_ext_discount_amt) / SUM(ss_ext_list_price) × 100` (pareil pour le web avec `ws_`)
4. **Unité** : %
5. **Périmètre** : magasins et site web
6. **Fréquence** : chaque mois
7. **Sources** : `store_sales`, `web_sales`
8. **Données manquantes** : aucune
9. **Limites** : environ 50 % de remise, ce qui est très élevé : les données sont fictives

## Étape C – Examiner les données

> Contrôles faits avec `01_UC01_besoin_exploration/preuves/explorer_donnees.py` (résultats : `inventaire_fichiers.csv`, `inventaire_colonnes.csv`).
> _Script développé avec l'aide de Claude._

### 1. Répertoire et kit

- `retail_project.zip` : 283 Mo compressé, environ 1 Go décompressé.
- `data/` : 23 fichiers `.dat`, `data_refresh/` : 11 fichiers `.dat` (nouvelles données à ajouter).
- Version, date et outil de génération : non communiqués.

### 2. Formats et colonnes

- `.dat` : texte séparé par `|`, **sans ligne de titres**. Noms des colonnes repris du schéma officiel TPCx-BB (statut : déduit).
- Toutes les lignes ont le bon nombre de colonnes (0 ligne en erreur).

### 3. Identifiants

- Les identifiants des tables de référence (`*_sk`) sont uniques (0 doublon).
- Pour les ventes, le couple ticket + produit n'est pas unique (4 038 couples en double en magasin).

### 4. Valeurs vides et problèmes

- Ventes : presque aucune valeur vide (moins de 0,1 %).
- Clics : 90 % sans vente, 42 % sans utilisateur.
- `customer` et `customer_address` : espaces en trop dans toutes les valeurs.
- `c_last_review_date` : du texte au hasard au lieu d'une date.
- Dates de fin (`*_rec_end_date`) toujours vides.

### 5. Périodes

- Ventes : du 01/01/2001 au 13/12/2005 (31/12/2005 avec `data_refresh`).
- Retours : jusqu'en 2008.
- Stocks : environ une photo par semaine (259 dates).

### 6. Domaines absents

- Stock des magasins (seulement par entrepôt), sessions web, objectifs de vente, coûts (loyers, salaires).

## Étape D – Vérifier les relations possibles

> Contrôles faits avec `01_UC01_besoin_exploration/preuves/verifier_relations.py` (résultats : `resultats_relations.csv`).
> _Script développé avec l'aide de Claude._

- 20 liens testés entre les ventes, retours, stocks, clics et les tables de référence.
- **0 numéro introuvable**, sauf pour les stocks : 232 380 lignes de `inventory` utilisent 180 produits qui ne sont que dans `data_refresh/item`.
- Tous les retours de `data` correspondent à une vente (même ticket et même produit).
- Un numéro de ticket n'apparaît jamais dans deux magasins : il est unique dans toute l'entreprise.
- Un ticket contient de 1 à 14 articles (7,4 en moyenne).

## Étape E – Formaliser les limites

- Données fictives (50 % de remise, autant de tickets que de commandes web).
- Une table présente n'est pas forcément bien remplie.
- Ventes magasin et web n'ont pas les mêmes colonnes (23 contre 34).
- Une ligne de vente n'est pas une transaction.
- Un clic n'est pas un achat.
- Les retours sont séparés des ventes.
- Une corrélation n'est pas une cause.
- Stock par entrepôt seulement, pas d'objectifs de vente, 2005 incomplète dans `data/`.

## UC2

> Livrables dans `02_UC02_architecture/`. _Rédaction faite avec l'aide de Claude._

### Étape A – Contraintes

- Fichiers texte structurés (sauf le texte des avis), environ 1 Go, 23 tables, historique de 2001 à 2008, données personnelles dans `customer`.

### Étape B – Comparaison des architectures

- Comparaison Data Warehouse / Data Lake / Lakehouse : principe, données, avantages, limites, usages, gouvernance, pertinence.
- **Choix** : Data Lake en zones Bronze / Silver / Gold, avec une zone Gold organisée comme un Data Warehouse.

### Étape C – Architecture logique

- Sources → NiFi → Bronze (fichiers d'origine) → Spark → Silver (Parquet, données propres) → Spark → Gold (Parquet, données pour les KPI) → tableaux de bord.

### Étape D – Composants

- Obligatoires : Linux, Python, HDFS, NiFi, Spark, Parquet. ADLS Gen2 au jour 4.
- Étude seulement : Data Factory, Synapse. Facultatifs et non utilisés : HBase, Delta Lake.

### Étape E – Flux

- 5 flux en batch : chargement initial, nouvelles données, nettoyage, préparation des KPI, calcul des KPI.

### Étape F – Gouvernance

- Provenance, documentation, contrôles qualité, droits d'accès par zone, protection des données clients, journaux, coûts.

### Étape G – Local vers Azure

- HDFS → ADLS Gen2 (conteneurs `bronze`, `silver`, `gold`), accès avec Entra ID + RBAC + ACL, secrets dans Key Vault, alerte de budget.
