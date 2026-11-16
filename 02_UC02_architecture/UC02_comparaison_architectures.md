# Comparaison des architectures

## 1. Contraintes du projet

| Contrainte | Constat |
|---|---|
| Format | Fichiers texte `.dat` en tableau. Seul le texte des avis est libre |
| Volume | Environ 1 Go. Le plus gros fichier fait 405 Mo (`inventory`) |
| Diversité | 23 tables : ventes, retours, produits, clients, stocks, clics, avis… |
| Historique | 2001 à 2008, avec de nouvelles données qui arrivent (`data_refresh`) |
| Qualité | Un peu de nettoyage à faire (espaces, colonne inutilisable) |
| Usages | Calculer les KPI et faire des tableaux de bord |
| Sécurité | Les fichiers clients contiennent des noms et des emails |
| Évolution | Le parcours prévoit Hadoop, NiFi, Spark puis Azure |

## 2. Les trois architectures

| | Data Warehouse | Data Lake | Data Lakehouse |
|---|---|---|---|
| **Principe** | Base de données qui reçoit des données déjà propres | Grand espace où l'on stocke les fichiers tels quels, puis on les nettoie par étapes | Data Lake avec en plus les fonctions d'une base de données |
| **Données** | Tableaux uniquement | Tous types (tableaux, texte, JSON…) | Tous types |
| **Avantages** | Rapide et fiable pour les KPI | Pas cher, garde les données brutes, accepte tout | Les avantages des deux |
| **Limites** | Rigide, pas adapté au texte et aux clics | Peut devenir désorganisé sans règles | Plus complexe à mettre en place |
| **Usages** | Tableaux de bord, reporting | Exploration, data science | Les deux |
| **Gouvernance** | Simple | Indispensable (règles, droits, catalogue) | Indispensable |
| **Pour notre projet** | Bien pour les ventes, pas pour les clics et les avis | Bien : accepte tous nos fichiers et utilise les outils du parcours | Intéressant, mais Delta Lake est facultatif |

## 3. Notre choix

Un **Data Lake en 3 zones (Bronze, Silver, Gold)**, dont la zone Gold est organisée comme un Data Warehouse.

Pourquoi :
- on peut stocker tous nos fichiers au même endroit ;
- on garde les fichiers d'origine en cas d'erreur ;
- la zone Gold permet de calculer facilement les KPI ;
- ça correspond aux outils obligatoires du parcours.
