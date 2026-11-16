# Gouvernance

## 1. Les règles

| Règle | Ce qu'on prévoit |
|---|---|
| **Provenance** | Chaque lot a un numéro (`load_id` = date + `initial` ou `refresh`). Bronze garde le fichier d'origine et une fiche de contrôle (nom, taille, nombre de lignes, empreinte SHA-256, date de réception). En Silver et Gold, chaque ligne garde le numéro du lot, le fichier d'origine et la date de chargement. On peut ainsi retrouver d'où vient chaque chiffre. Les données complémentaires sont rangées à part |
| **Documentation** | Un dictionnaire des tables et colonnes (`tpcxbb_schema.json`, complété avec le rôle de chaque colonne et la présence de données personnelles), le dictionnaire des KPI d'UC-01, la description des zones, la liste des limites. Tout est dans Git |
| **Qualité** | Des règles vérifiées par Spark à chaque lot (tableau ci-dessous). Les résultats sont notés dans une table `quality_report` |
| **Accès** | Chacun n'a accès qu'à ce dont il a besoin (tableau ci-dessous). En local : droits des dossiers HDFS. Sur Azure : RBAC + ACL |
| **Protection des données** | Les noms, emails et identifiants de connexion des clients sont masqués dès Silver (remplacés par un code). Seule l'Équipe Data accède à Bronze, qui les contient en clair. Gold ne contient **aucune** donnée personnelle (âge par tranche, région au lieu de l'adresse). Durée de conservation définie (RGPD) |
| **Suivi des traitements** | Une table `run_log` note pour chaque traitement : le flux, le lot, l'heure de début et de fin, le statut, le nombre de lignes lues, écrites et rejetées. Alerte si un traitement échoue. On peut refaire chaque traitement depuis Bronze |
| **Coûts et volumes** | Parquet compressé, faits rangés par année et mois, suivi de la taille de chaque zone. Bronze est conservé (petit et utile pour refaire les traitements). Les anciennes versions de Silver et la quarantaine sont vidées après un certain temps |

## 2. Règles de qualité

| # | Règle | Seuil | Si la règle échoue |
|---|---|---|---|
| Q1 | Bon nombre de colonnes par ligne | 100 % | **Le lot est refusé** |
| Q2 | Chaque valeur a le bon type | 100 % | La ligne va en quarantaine |
| Q3 | Identifiants uniques dans les tables de référence | 0 doublon | **Le lot est refusé** |
| Q4 | Chaque vente a un produit, un client, un magasin et une date qui existent | 0 introuvable | Quarantaine, alerte si plus de 0,1 % |
| Q5 | Taux de valeurs vides par colonne | Moins de 2 points d'écart avec le lot d'avant | Alerte |
| Q6 | Montants cohérents (net payé = montant − coupon) | 100 % | Alerte |
| Q7 | Chaque retour correspond à une vente | 100 % | Quarantaine |
| Q8 | Pas de doublon avec le lot d'avant | 0 doublon | Doublons enlevés + alerte |

## 3. Qui accède à quoi

| Rôle | Bronze | Quarantaine | Silver | Gold |
|---|---|---|---|---|
| Équipe Data (P3) | Lecture / écriture | Lecture / écriture | Lecture / écriture | Lecture / écriture |
| Analystes | – | Lecture | Lecture (données masquées) | Lecture |
| Direction générale, contrôleur de gestion, direction commerciale (P1, P2, P4) | – | – | – | Lecture |
| Responsable des stocks (P5) | – | – | – | Lecture (stocks, logistique) |
| Responsable de magasin (P6) | – | – | – | Lecture **de son magasin seulement** |
| Comptes techniques (NiFi, Spark) | Écriture | Écriture | Écriture | Écriture |
