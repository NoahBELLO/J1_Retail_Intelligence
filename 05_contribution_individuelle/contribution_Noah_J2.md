# Contribution Noah – Jour 2

## UC-03

### Étape 1 – Environnement Hadoop

Relevés faits le 17 novembre 2026. Les sorties complètes des commandes sont dans [preuves/etape1_sorties_commandes.txt](../03_UC03_hdfs/preuves/etape1_sorties_commandes.txt).

#### 1. Commandes lancées

| Commande | Pour quoi faire |
|---|---|
| `hadoop version` | Connaître la version et le dossier d'installation |
| `jps` | Voir les programmes Java (services) qui tournent |
| `hdfs dfsadmin -report` | Voir l'état de HDFS et des DataNodes |
| `cat core-site.xml`, `cat hdfs-site.xml`, `hdfs getconf` | Lire la configuration |
| `hdfs dfsadmin -safemode get` | Vérifier que le NameNode accepte les écritures |
| `grep ERROR/FATAL/WARN` sur les journaux | Chercher des erreurs au démarrage |

#### 2. Informations relevées

| Élément | Valeur constatée |
|---|---|
| Système | Ubuntu 24.04.5 LTS sous WSL (Windows 11), machine `DESKTOP-DCTNJ6T` |
| Version de Hadoop | **3.5.0** |
| Chemin d'installation | `/opt/hadoop` (`HADOOP_HOME`) |
| Dossier de configuration | `/opt/hadoop/etc/hadoop` (`HADOOP_CONF_DIR`) |
| Java utilisé par Hadoop | Java 17 : `/usr/lib/jvm/java-17-openjdk-amd64` (dans `hadoop-env.sh`) |
| Adresse de HDFS | `hdfs://localhost:9000` (`fs.defaultFS`) |
| Facteur de réplication | **1** (`dfs.replication`) |
| Taille d'un bloc | 134 217 728 octets = **128 Mo** (valeur par défaut) |
| Dossier du NameNode | `/home/noah/hadoop-data/namenode` |
| Dossier du DataNode | `/home/noah/hadoop-data/datanode` |
| Journaux | `/opt/hadoop/logs/` |
| Interface web du NameNode | http://localhost:9870 |

#### 3. État des services

| Service | État | Preuve |
|---|---|---|
| NameNode | **Démarré**, mode sans écriture (safe mode) **désactivé** | `jps` (processus 11282), `Safe mode is OFF` |
| SecondaryNameNode | **Démarré**, il a fait une sauvegarde de l'index à 12h46 | `jps` (processus 11569), journal `Checkpoint done` |
| DataNode | **1 DataNode actif**, statut `Normal` | `jps` (processus 11393), `Live datanodes (1)` à l'adresse `127.0.0.1:9866` |
| HDFS | Sain : 0 bloc manquant, 0 bloc abîmé, 0 bloc pas assez copié | `hdfs dfsadmin -report` |
| Espace | 1006,85 Go configurés, 929,96 Go libres, 28 Ko utilisés, 0 bloc | `hdfs dfsadmin -report` |

`jps` montre aussi `NiFi` et `BootstrapProcess`. NiFi est donc déjà démarré, il servira pour l'UC-04.

Remarque : les 1006 Go correspondent au disque virtuel de WSL, pas à un vrai espace réservé à HDFS.

#### 4. Erreurs de démarrage

- **Aucune ligne `ERROR` ni `FATAL`** dans les journaux du NameNode, du DataNode et du SecondaryNameNode.
- Quelques avertissements (`WARN`) qui ne bloquent pas :
  - `Unable to initialize FileSignerSecretProvider` : aucun fichier secret n'est configuré pour l'interface web, Hadoop en génère un au hasard. Sans conséquence dans notre cas.
  - `Only one image storage directory configured. Beware of data loss` : l'index du NameNode n'est enregistré qu'à un seul endroit. Si ce dossier est perdu, tout HDFS est perdu. C'est normal sur une seule machine, mais ce serait un risque en production.

#### 5. Rôle du NameNode et des DataNodes

- **NameNode** : c'est le « chef ». Il ne stocke pas les données mais l'**index** : l'arborescence des dossiers, les noms des fichiers, les droits, et la liste des blocs de chaque fichier avec leur emplacement. Toute commande `hdfs dfs` passe d'abord par lui. S'il s'arrête, HDFS n'est plus utilisable.
- **DataNode** : c'est un « ouvrier ». Il stocke les **blocs** (morceaux de 128 Mo) sur son disque, les envoie quand on lit un fichier, et signale régulièrement au NameNode qu'il est vivant et quels blocs il possède (ligne `Last Block Report` dans le rapport).
- **SecondaryNameNode** : il aide le NameNode en fusionnant de temps en temps son index avec le journal des modifications (checkpoint). Ce **n'est pas** un NameNode de secours : il ne prend pas le relais si le NameNode tombe.

#### 6. Type de déploiement

C'est un déploiement **local sur une seule machine** (mode pseudo-distribué) :
- le NameNode, le SecondaryNameNode et l'unique DataNode tournent sur la même machine (`localhost`) ;
- la réplication est à 1, donc chaque bloc n'existe qu'en un seul exemplaire.

C'est un **environnement pédagogique**, pas un cluster de production : si la machine ou le disque tombe en panne, aucune copie ne permet de récupérer les données, et il n'y a aucun NameNode de secours.
