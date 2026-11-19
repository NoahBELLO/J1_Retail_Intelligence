# Questions de recul – Jour 4

Réponses aux questions du §15 du TP.

## 1. Pourquoi faut-il vérifier la granularité avant de calculer un KPI ?
Pour savoir ce qu'on compte. Dans nos ventes, une ligne est une ligne de ticket, pas un ticket : il y a 7,5 lignes par ticket en moyenne. Si on avait compté les lignes comme des achats, le panier moyen aurait été 7,5 fois trop petit. On a aussi vérifié qu'un ticket appartient à un seul magasin et à une seule date : sinon, en comptant les tickets par magasin ou par année, certains auraient été comptés deux fois.

## 2. Quelle différence existe entre un nombre de lignes et un nombre de transactions ?
- **Nombre de lignes** : chaque produit d'un ticket fait une ligne (667 579 lignes sur le fichier complet, 66 593 sur l'échantillon).
- **Nombre de transactions** : le nombre de tickets différents (`ss_ticket_number`) : 89 100 sur le fichier complet, 8 910 sur l'échantillon.

Le même produit peut même apparaître deux fois sur un ticket, avec deux promotions différentes (Jour 3).

## 3. Quelles limites avez-vous rencontrées dans les données utilisées pour vos analyses ?
- **Ventes en magasin seulement** : pas de `web_sales` ni de `store_returns`.
- **Échantillon de 10 %** dans la chaîne principale. Les montants valent environ un dixième du réel, et le classement des magasins change par rapport au fichier complet.
- **Pas de dates ni de noms de magasins** dans la chaîne HDFS (fichier complet).
- **Marge non fiable** : 74 % des lignes ont une marge négative.
- **Décembre 2005 incomplet**, devise non indiquée.
- **Données inventées** : remise d'environ 50 % partout, paniers de 380 articles et d'environ 12 900 €.

## 4. Quels indicateurs n'avez-vous pas pu calculer, et pour quelles raisons ?
- **La marge** : les coûts ne sont pas fiables.
- **La part du CA magasin / web** : `web_sales` n'a pas été transformée.
- **Le taux de retour** : `store_returns` n'a pas été transformée.
- **L'évolution du CA (KPI-06) sur le fichier complet** : la chaîne HDFS n'a pas `date_dim`. Le KPI-06 a été calculé seulement sur l'échantillon.

## 5. Comment avez-vous vérifié la cohérence des résultats ?
- Les KPI recalculés depuis le Silver sont identiques à ceux du Gold (`ca_annuel` pour l'échantillon, `ca_par_categorie` pour le fichier complet, écart 0,00).
- La somme par magasin, par année ou par catégorie est égale au total, en CA comme en tickets.
- Les clés sont uniques, et aucune vente n'a de produit inconnu.
- L'échantillon et le fichier complet donnent les mêmes taux et les mêmes moyennes (écarts inférieurs à 1 %).
- Le notebook principal s'arrête tout seul (`assert`) si un de ces contrôles échoue.
- On a affiché chaque tableau avant de faire le graphique.

## 6. Quelle différence existe entre un constat statistique et une conclusion causale ?
- Un **constat** décrit ce qu'on voit : « Sherwood a le plus gros CA sur l'échantillon ».
- Une **conclusion causale** dit pourquoi : « Sherwood vend plus parce qu'il est mieux géré ».

Pour la deuxième, il faudrait des informations qu'on n'a pas (surface, emplacement, prix, nombre de clients) et éliminer les autres explications. Notre propre exemple le montre : sur le fichier complet, Sherwood est dernier. Le premier constat venait en partie du hasard de l'échantillon.

## 7. Pourquoi les données synthétiques doivent-elles être identifiées dans la restitution ?
Parce que les résultats ne décrivent pas une vraie entreprise. On voit des choses qui n'existeraient pas dans un vrai magasin : 50 % de remise partout, des tickets à 12 900 €, des magasins presque identiques. Si on ne le dit pas, quelqu'un pourrait prendre une décision sur de faux chiffres. C'est pour ça que c'est écrit en haut des notebooks, en source sur chaque graphique et dans chaque constat.

## 8. Quel est le rôle d'ADLS Gen2 dans votre architecture ?
C'est l'endroit où seraient stockées toutes les données du projet, de `raw` à `gold`, avec un conteneur par zone. Il ne calcule rien : Spark lit et écrit dedans. Dans notre parcours local, c'est HDFS (et le disque local pour la chaîne des notebooks) qui joue ce rôle, avec les mêmes zones. Sur Azure, ADLS Gen2 reste une proposition.

## 9. Quel intérêt apporte le Hierarchical Namespace ?
Il crée de vrais dossiers dans le stockage Azure. Sans lui, les dossiers sont seulement simulés dans le nom des fichiers. Grâce à lui :
- on peut renommer ou supprimer un dossier en une seule opération, ce dont Spark a besoin pour écrire ses résultats proprement (le dossier temporaire est renommé à la fin) ;
- on peut mettre des droits (ACL) sur un dossier ou un fichier précis.

HDFS fonctionne déjà comme ça.

## 10. Quelle différence existe entre RBAC et ACL ?
- **RBAC** : des droits larges, donnés à une identité sur une ressource entière (le compte de stockage, un conteneur). Exemple : « les analystes lisent le conteneur `gold` ».
- **ACL** : des droits fins, sur un dossier ou un fichier, comme `rwx` sous Linux. Exemple : « un responsable de magasin lit seulement le dossier de son magasin ».

## 11. Dans quels cas Azure Data Factory serait-il utile ?
Quand il faut automatiser le chargement et l'enchaînement des traitements :
- copier les nouveaux fichiers (le lot `refresh`) dans `raw` dès qu'ils arrivent, ou chaque nuit ;
- lancer ensuite le nettoyage, le Gold et les contrôles qualité dans l'ordre, et s'arrêter si une étape échoue ;
- suivre chaque exécution et prévenir en cas d'erreur.

Aujourd'hui, NiFi et nos scripts `run_pipeline.sh` et `lancer_tout.sh`, lancés à la main, font une partie de ce travail.

## 12. Quel rôle pourrait jouer Synapse Analytics ?
Ce serait l'endroit où l'on traite et analyse les données :
- un **Spark Pool** exécuterait nos notebooks et scripts PySpark presque sans changement, en changeant seulement les chemins ;
- **Synapse SQL** permettrait aux analystes d'interroger `gold` en SQL, et de brancher Power BI ;
- **Synapse Studio** remplacerait notre JupyterLab.

## 13. Quels éléments de votre architecture sont réellement déployés et lesquels restent théoriques ?
- **Déployés (en local)** :
  - HDFS avec les zones `raw`, `bronze`, `silver`, `gold`, `quality`, `logs` (Jour 2) ;
  - l'ingestion avec NiFi (Jour 2) ;
  - les deux chaînes de traitement Spark Raw → Silver → Gold et les contrôles qualité (Jour 3) ;
  - les deux notebooks d'analyse UC-08 (Jour 4) ;
  - le format Parquet.
- **Théoriques** :
  - **toute la partie Azure** : abonnement, ADLS Gen2, conteneurs, Entra ID, RBAC, ACL, Key Vault, Data Factory, Synapse, Power BI ;
  - **les outils open source étudiés** : Iceberg, Trino, catalogue (Nessie / Hive Metastore), Airflow, Superset, MinIO.

## 14. Quels seraient les principaux risques de coût ou de sécurité dans une mise en production ?
- **Coût** :
  - un Spark Pool ou un service SQL oublié et laissé allumé ;
  - des requêtes SQL qui lisent beaucoup de données ;
  - les données téléchargées hors d'Azure ;
  - une facture une fois le crédit gratuit épuisé.

  Il faut une alerte de budget, l'arrêt automatique et la suppression des ressources de test.
- **Sécurité** :
  - donner trop de droits par simplicité (par exemple « contributeur » à tout le monde) ;
  - laisser une clé d'accès ou un mot de passe dans le code ou dans Git ;
  - ouvrir le compte de stockage à tout Internet ;
  - laisser des données personnelles dans `silver` ou `gold`.

  Il faut le moindre privilège, des groupes Entra ID, un coffre à secrets (Key Vault), et masquer les données personnelles dès Silver (règle du Jour 1).
