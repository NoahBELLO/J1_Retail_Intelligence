# Environnement technique – Jour 2

Fiche d'environnement technique et fiche de découverte Hadoop / HDFS (livrables 1 et 2).

> Preuves : `preuves/j2/hadoop/etape1_sorties_commandes.txt` (Noah), `preuves/j2/hadoop/etape1_sorties_commandes_lorenzo.txt` (Lorenzo), `preuves/j2/hdfs/etape2_*`, `preuves/j2/nifi/etape6_*`.

## 1. Nos deux machines

Chacun a installé et testé l'environnement sur sa propre machine.

| | Noah | Lorenzo |
|---|---|---|
| Système | Ubuntu 24.04.5 dans WSL (Windows 11) | Ubuntu 24.04.5 installé directement |
| Utilisateur Linux | `noah` | `lolorigolo` |
| Java | 17 pour Hadoop, 21 pour NiFi | 17 pour Hadoop, 21 pour NiFi |
| Hadoop | 3.5.0, dans `/opt/hadoop` | 3.5.0, dans `/opt/hadoop` |
| NiFi | 2.12.0, dans `/opt/nifi` | 2.12.0, dans `/opt/nifi` |
| Python | 3.12.3 | Non relevé (pas de solution de repli nécessaire) |
| Espace HDFS libre | environ 930 Go | environ 365 Go |

## 2. Configuration de Hadoop

La même sur les deux machines :

- Fichiers de configuration dans `/opt/hadoop/etc/hadoop`.
- `fs.defaultFS = hdfs://localhost:9000` : adresse de HDFS.
- `dfs.replication = 1` : chaque bloc n'existe qu'en un exemplaire.
- Taille d'un bloc : 128 Mo (valeur par défaut).
- Données du NameNode et du DataNode dans `~/hadoop-data/namenode` et `~/hadoop-data/datanode`.

## 3. État des services

- `jps` montre `NameNode`, `DataNode` et `SecondaryNameNode` (et `NiFi`).
- `hdfs dfsadmin -report` : 1 DataNode actif (`127.0.0.1:9866`), état normal, 0 bloc manquant ou abîmé.
- `hdfs fsck /` : `HEALTHY`.
- Erreurs au démarrage : aucune chez Noah. Chez Lorenzo, deux erreurs corrigées au premier démarrage (voir `erreurs-corrections.md`).

## 4. Rôle du NameNode et des DataNodes

- **NameNode** : c'est le « chef ». Il ne garde pas les données, mais il sait où elles sont : la liste des dossiers et des fichiers, et sur quel DataNode se trouve chaque bloc. S'il est arrêté, on ne peut plus utiliser HDFS.
- **DataNode** : c'est un « ouvrier ». Il garde les blocs sur son disque et prévient régulièrement le NameNode qu'il fonctionne.

## 5. Une seule machine

Sur nos deux machines, le NameNode et le DataNode tournent sur le même ordinateur, avec une réplication à 1. C'est un environnement pour apprendre, pas pour une vraie entreprise : si le disque tombe en panne, les données sont perdues, et il n'y a pas de NameNode de secours.

## 6. NiFi

- **Version** : 2.12.0 (menu ☰ → *About*), avec Java 21.
- **Adresse** : https://localhost:8443/nifi.
- **État** : `nifi.sh status` → `UP`.
- **Composants** : `GetFile` et `LogAttribute` sont présents de base. `PutHDFS` n'est pas installé au départ (voir `erreurs-corrections.md`).
- **Services nécessaires à l'ingestion** : HDFS démarré, fichiers `core-site.xml` et `hdfs-site.xml` lisibles par NiFi, module Hadoop de NiFi.
- **Sécurité** : connexion en HTTPS avec un certificat créé par NiFi (avertissement du navigateur), identifiant et mot de passe générés au premier démarrage (non recopiés ici), accès seulement depuis la machine.

### Les notions de NiFi

- **FlowFile** : ce qui circule dans le flux, c'est-à-dire le contenu du fichier plus des informations dessus (attributs : nom, chemin, date…).
- **Processor** : une étape qui fait une action, par exemple `GetFile` (lire un fichier) ou `PutHDFS` (l'écrire dans HDFS).
- **Connection** : le lien entre deux processeurs. Elle transporte les FlowFiles et sert de file d'attente.
- **Process Group** : une « boîte » qui regroupe plusieurs processeurs.
- **Controller Service** : un réglage partagé par plusieurs processeurs (par exemple une connexion à une base de données).
- **Provenance Repository** : l'historique de chaque FlowFile, avec l'heure de chaque événement.
