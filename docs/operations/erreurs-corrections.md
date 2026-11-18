# Erreurs et corrections – Jour 2

Tableau des erreurs rencontrées et de leurs corrections (livrable 10).

| # | Étape | Qui | Erreur | Cause | Correction |
|---|---|---|---|---|---|
| 1 | 1 – Hadoop | Lorenzo | NameNode : `Invalid URI for NameNode address (check fs.defaultFS): file:/// has no authority`. DataNode et SecondaryNameNode ne démarrent pas | `fs.defaultFS` absent de `core-site.xml` | Ajout de `fs.defaultFS = hdfs://localhost:9000` |
| 2 | 1 – Hadoop | Lorenzo | NameNode : `NameNode is not formatted` | Premier démarrage, espace HDFS jamais initialisé | `hdfs namenode -format` (une seule fois, HDFS encore vide) |
| 3 | 6 – NiFi | Noah | NiFi ne démarre plus : `Both nifi.web.https.port and nifi.web.http.port specified` | Les ports `http` et `https` étaient remplis tous les deux dans `nifi.properties` | Lignes `nifi.web.http.host` et `nifi.web.http.port` vidées, puis `nifi.sh start` |
| 4 | 6 – NiFi | Noah | NiFi démarré, mais la page ne s'ouvre pas dans le navigateur Windows | NiFi n'écoutait que sur `localhost` dans WSL, et WSL ne transmettait pas cette adresse à Windows | `nifi.web.https.host` vidé, puis redémarrage. NiFi refuse toujours les autres adresses que `localhost` |
| 5 | 6 – NiFi | Les deux | `PutHDFS` absent de la liste des processeurs (« Showing 0 of 294 ») | Depuis NiFi 2, le module Hadoop n'est plus installé de base | Copie des modules officiels `nifi-hadoop-libraries-nar` et `nifi-hadoop-nar` 2.12.0 (Maven Central, empreinte vérifiée) dans `/opt/nifi/extensions`. NiFi les charge tout seul (`Loaded extensions …`) |
| 6 | 8 – NiFi | Noah | PutHDFS toujours absent juste après l'installation | La page gardait l'ancienne liste en mémoire | Rechargement de la page (F5) : 304 processeurs, dont PutHDFS |
| 7 | 7 – NiFi | Noah | GetFile invalide : `Directory does not exist` | `/data/nifi/input` pas encore créé | Création des dossiers `/data/nifi/…` |
| 8 | 7 – NiFi | Noah | `sudo: a password is required` | Créer un dossier dans `/data` demande les droits administrateur | Commande lancée avec les droits administrateur |
| 9 | 10 – NiFi | Les deux | GetFile invalide : `Directory does not exist` (erreur provoquée) | Test volontaire avec `/data/nifi/dossier_inexistant` | `Input Directory` remis à `/data/nifi/input` |

Ce qui n'était pas une erreur :
- `hdfs dfs -ls`, `-mkdir` et `-du` n'affichent rien quand HDFS est vide ou que la commande réussit.
- `cat: Unable to write to output stream` avec `hdfs dfs -cat … | head` : `head` coupe la lecture après quelques lignes.
- Taille affichée 89M en local et 88.5 M dans HDFS : arrondis différents, la taille exacte est la même.

Aucune solution de repli n'a été nécessaire : HDFS et NiFi ont fonctionné sur nos deux machines.
