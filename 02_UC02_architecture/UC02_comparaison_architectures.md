# Comparaison des architectures

## 1. Contraintes du projet (étape A)

| Contrainte | Constat (UC-01) | Conséquence pour l'architecture |
|---|---|---|
| **Formats** | Fichiers `.dat` séparés par `|`, sans ligne de titres. Un fichier `audit.csv` à moitié tabulaire. Le texte des avis est libre (jusqu'à 5 748 caractères) | Il faut appliquer les noms et types de colonnes à la lecture (`tpcxbb_schema.json`) et garder les fichiers d'origine tels quels |
| **Volumes** | Environ 1 Go. Plus grosses tables : `inventory` (23 millions de lignes) et `web_clickstreams` (6,8 millions). `data_refresh` = environ 1 % en plus par lot | Ça tient sur un seul ordinateur, mais le volume peut grossir : on prévoit HDFS + Spark, le format Parquet et un rangement des fichiers par date |
| **Diversité** | 8 domaines : ventes, retours, stocks, produits, clients, prix concurrents, clics, avis | On ne peut pas tout modéliser à l'avance : il faut une zone qui accepte tout, et on ne modélise que ce qui sert aux KPI |
| **Historique** | Les sources ne gardent pas d'historique (dates de fin vides). `data_refresh` ajoute des données mais corrige aussi le passé (retours de 2001 à 2007) | La plateforme doit garder elle-même l'historique : chaque lot brut daté, plusieurs versions des produits et des clients, et pouvoir recalculer une période |
| **Qualité** | Doublons ticket + produit, 778 retours sans vente, 180 produits du stock absents de `data/item`, colonnes inutilisables, 13/12/2005 en double | Il faut une étape de contrôle avant les KPI, une zone de **quarantaine** et un ordre de chargement (tables de référence avant les ventes) |
| **Usages** | 6 KPI d'UC-01, plus l'exploration des clics et des avis | Une zone Gold en étoile pour les KPI, et un accès aux données détaillées pour l'exploration |
| **Sécurité** | Données personnelles dans `customer` (nom, email, date de naissance) | Les données personnelles sont masquées dès la zone Silver et absentes de Gold. Droits par zone et par rôle. Un responsable de magasin ne voit que son magasin |
| **Évolution** | Nouveaux lots `data_refresh`, montée en volume, Azure au jour 4 | Même organisation en local et sur Azure, chargement par lots, possibilité d'ajouter de nouvelles sources |

## 2. Les trois architectures (étape B)

| | Data Warehouse | Data Lake en zones | Data Lakehouse |
|---|---|---|---|
| **Principe** | Base de données organisée à l'avance (en étoile). On transforme les données **avant** de les charger (ETL) | On stocke tous les fichiers tels quels, puis on les transforme **après** (ELT), par zones successives | Un Data Lake avec en plus les fonctions d'une base de données : mises à jour fiables, historique des versions (Delta Lake) |
| **Données** | Tableaux stables (ventes, référentiels) | Tous types : tableaux, clics, texte, CSV | Tous types |
| **Avantages** | KPI fiables, requêtes SQL rapides, adapté aux tableaux de bord | On ne perd rien, peu cher, on peut refaire les traitements, adapté à l'exploration | Les avantages des deux sur un seul stockage, mises à jour fiables pour les lots `data_refresh` |
| **Limites** | Rigide, ne garde pas le brut, pas adapté au texte et aux clics | Peut devenir un « marécage de données » sans règles. Pas de mise à jour fiable des fichiers | Plus complexe, technologies plus récentes. Delta Lake est **facultatif** dans le parcours |
| **Usages** | Tableaux de bord, rapports, KPI officiels | Exploration, data science, archivage | Les deux |
| **Gouvernance** | Simple, car le périmètre est réduit | Indispensable : catalogue, provenance, droits par dossier | Celle du Data Lake, plus la gestion des versions |
| **Pour notre projet** | Moyenne : bien pour les KPI, mais pas pour les clics, le texte et le brut | **Bonne** : accepte tous nos fichiers et utilise les outils obligatoires. Avec des zones et des contrôles, les KPI restent fiables | Intéressante **plus tard** (`data_refresh` corrige le passé), mais elle demande Delta Lake, qui est facultatif |

## 3. Notre choix

**Aujourd'hui (socle obligatoire)** : un **Data Lake en zones Bronze / Silver / Gold** (organisation « médaillon »), avec une zone Gold **organisée en étoile comme un Data Warehouse**. Il utilise HDFS, Spark et Parquet. Pour mettre à jour des données, on réécrit des dossiers entiers, et chaque lot a un numéro (`load_id`).

**Plus tard (évolution possible)** : en ajoutant **Delta Lake** (facultatif), ce Data Lake devient un **Lakehouse** : mises à jour fiables, retour à une version précédente. L'architecture fonctionne **sans** Delta Lake.

Pourquoi :
- on garde tous les fichiers d'origine, ce qui permet de refaire les traitements ;
- la zone Gold rend les KPI simples et fiables ;
- c'est cohérent avec les outils obligatoires du parcours ;
- on peut passer au Lakehouse plus tard sans tout refaire, car les zones restent les mêmes.
