# Contribution Noah – Jour 2

## UC3

### Étape 1 – Vérifier l'environnement Hadoop

> Commandes et résultats : `03_UC03_hdfs/preuves/etape1_sorties_commandes.txt`.

#### 1. Commandes lancées

- `hadoop version` : version de Hadoop.
- `jps` : services qui tournent.
- `hdfs dfsadmin -report` : état de HDFS et des DataNodes.
- Lecture de `core-site.xml` et `hdfs-site.xml` : configuration.
- Recherche des erreurs dans les journaux de Hadoop.

#### 2. Ce que j'ai relevé

- **Système** : Ubuntu 24.04 dans WSL (Linux dans Windows 11).
- **Python** : 3.12.3.
- **Hadoop** : 3.5.0, installé dans `/opt/hadoop`, avec Java 17.
- **Configuration** : HDFS est à l'adresse `hdfs://localhost:9000`. Chaque fichier est gardé en 1 seul exemplaire et découpé en blocs de 128 Mo.
- **NameNode** : démarré.
- **DataNode** : 1 seul, démarré, état normal.
- **Espace** : environ 930 Go libres, HDFS est vide.
- **Erreurs au démarrage** : aucune, seulement quelques avertissements sans gravité.

#### 3. Rôle du NameNode et des DataNodes

- **NameNode** : c'est le « chef ». Il ne garde pas les données, mais il sait où elles sont : la liste des dossiers et des fichiers, et sur quel DataNode se trouve chaque morceau de fichier. S'il est arrêté, on ne peut plus utiliser HDFS.
- **DataNode** : c'est un « ouvrier ». Il garde les données sur son disque. Les fichiers sont découpés en morceaux (des blocs) et chaque DataNode en stocke une partie.

#### 4. Une seule machine ou plusieurs ?

Mon environnement tourne sur une seule machine : le NameNode et le DataNode sont sur le même ordinateur. C'est un environnement pour apprendre, pas pour une vraie entreprise : chaque fichier n'existe qu'en un exemplaire, donc si le disque tombe en panne, les données sont perdues.

### Étape 2 – Découvrir les commandes HDFS

> Commandes et résultats : `03_UC03_hdfs/preuves/etape2_sorties_commandes.txt`.

#### 1. Les 6 opérations demandées

1. **État de HDFS** : `hdfs fsck /` → `HEALTHY`.
2. **Informations sur les nœuds** : `hdfs dfsadmin -report` → 1 DataNode actif.
3. **Lister les dossiers** : `hdfs dfs -ls /` → rien au début, puis `/retail-lake`.
4. **Créer un dossier de travail** : `hdfs dfs -mkdir -p /retail-lake` → aucun message, donc ça a marché.
5. **Vérifier les permissions** : `hdfs dfs -ls -d /retail-lake` → `drwxr-xr-x noah supergroup`.
6. **Taille des données** : `hdfs dfs -du -s -h /retail-lake` → `0`, le dossier est vide.

#### 2. Lire les permissions `drwxr-xr-x`

- `d` : c'est un dossier.
- `rwx` : le propriétaire (`noah`) peut lire, écrire et ouvrir le dossier.
- `r-x` : le groupe peut lire et ouvrir, mais pas écrire.
- `r-x` : les autres peuvent lire et ouvrir, mais pas écrire.

#### 3. Erreurs rencontrées

Aucune vraie erreur, mais au début plusieurs commandes n'affichaient rien :
- `hdfs dfs -ls /` : HDFS était vide.
- `hdfs dfs -mkdir` : n'affiche rien quand ça marche.
- `hdfs dfs -du -h` : le dossier était vide. Avec `-s`, on a quand même le total (`0`).

### Étape 3 – Créer l'arborescence du Data Lake

> Commandes et résultats : `03_UC03_hdfs/preuves/etape3_sorties_commandes.txt`.

#### 1. Commandes lancées

```bash
hdfs dfs -mkdir -p /retail-lake/raw/tpcxbb/initial
hdfs dfs -mkdir -p /retail-lake/raw/tpcxbb/refresh
hdfs dfs -mkdir -p /retail-lake/bronze/tpcxbb
hdfs dfs -mkdir -p /retail-lake/silver
hdfs dfs -mkdir -p /retail-lake/gold
hdfs dfs -mkdir -p /retail-lake/quality
hdfs dfs -mkdir -p /retail-lake/logs
hdfs dfs -ls -R /retail-lake
```

La dernière commande montre les 10 dossiers. J'ai gardé l'arborescence proposée par le TP.

#### 2. Schéma

```
/retail-lake/
├── raw/                 Les fichiers reçus, tels quels
│   └── tpcxbb/          Source : les données TPCx-BB
│       ├── initial/     Premier envoi de données (dossier data/)
│       └── refresh/     Envoi de mise à jour (dossier data_refresh/)
├── bronze/              Les mêmes données, rangées pour être lues
│   └── tpcxbb/
├── silver/              Les données nettoyées
├── gold/                Les données prêtes pour les indicateurs
├── quality/             Les résultats des contrôles et les lignes refusées
└── logs/                Les journaux : ce qui a été fait, quand, et si ça a marché
```

Les données vont dans cet ordre : raw → bronze → silver → gold.

#### 3. Explications

- **Pourquoi garder les données sources ?** Si un traitement est faux, on peut tout refaire à partir des fichiers d'origine. Et on peut toujours retrouver d'où vient un chiffre.
- **Différence entre Raw et Bronze** : dans Raw, on met le fichier exactement comme on l'a reçu et on n'y touche plus. Dans Bronze, on a les mêmes données, mais rangées pour être lues facilement (une table par dossier, avec la date du chargement). On ne corrige encore rien.
- **Rôle de Silver et Gold** : Silver contient les données nettoyées (sans doublons, avec les bons types). Gold contient les données prêtes pour répondre aux questions du métier, par exemple le chiffre d'affaires par mois.
- **Pourquoi séparer les données, `quality` et `logs` ?** Pour ne pas mélanger les données avec les informations sur les traitements. On retrouve plus vite une erreur, et on peut donner des droits différents (par exemple, le métier lit `gold` mais pas `logs`).
- **Comment garder la provenance (l'origine des données) ?** Un dossier par source (`tpcxbb`) et par envoi (`initial`, `refresh`). On ne modifie jamais les fichiers de `raw`. Pour chaque fichier déposé, on note son nom, d'où il vient, sa taille, son nombre de lignes et la date du dépôt.

#### 4. Différence avec le Jour 1

Au Jour 1, on avait appelé « Bronze » la zone qui garde les fichiers d'origine. Au Jour 2, cette zone s'appelle `raw`, et `bronze` devient une étape en plus. La zone « Quarantaine » du Jour 1 (les lignes refusées) va dans `quality`.

### Étape 4 – Déposer les données TPCx-BB

> Commandes et résultats : `03_UC03_hdfs/preuves/etape4_sorties_commandes.txt`.

#### 1. Fichier choisi

`store_sales.dat` (les ventes en magasin), parce que c'est la table principale pour nos indicateurs du Jour 1, comme le chiffre d'affaires.

#### 2. Avant le dépôt

- **Chemin local** : `retail_project/data/store_sales/store_sales.dat` (`ls -l`).
- **Format** : texte, colonnes séparées par `|`, pas de ligne de titres (`file`, `head -n 3`).
- **Taille** : 92 764 700 octets, environ 89 Mo (`ls -l`).
- **Structure** : 23 colonnes (`head -n 1` + `awk`).
- **Nombre de lignes** : 667 579 (`wc -l`).
- **Provenance** : kit TPCx-BB fourni pour le projet, dossier `data/` (premier envoi).
- **Lisible** : oui, les premières lignes s'affichent.

Ces chiffres sont les mêmes que dans l'inventaire du Jour 1.

#### 3. Le dépôt

```bash
hdfs dfs -put retail_project/data/store_sales/store_sales.dat /retail-lake/raw/tpcxbb/initial/
```

Je l'ai mis dans `raw/tpcxbb/initial` car il vient du dossier `data/`, c'est-à-dire du premier envoi.

#### 4. Après le dépôt

- Le fichier apparaît dans HDFS (`hdfs dfs -ls`).
- Même taille qu'en local : 92 764 700 octets.
- Il est lisible : `hdfs dfs -cat … | head -n 3` affiche les mêmes lignes qu'en local.
- Le chemin est bon : `/retail-lake/raw/tpcxbb/initial/store_sales.dat`.
- L'original est toujours là : `-put` copie le fichier, il ne le déplace pas.

#### 5. Inventaire mis à jour

| Fichier | Format | Taille | Lignes | Colonnes | Chemin HDFS | Remarques |
|---|---|---|---|---|---|---|
| `store_sales.dat` | Texte, séparateur `\|` | 92 764 700 octets | 667 579 | 23 | `/retail-lake/raw/tpcxbb/initial/` | Pas de ligne de titres, fins de ligne Windows |
| `store.dat` | Texte, séparateur `\|` | 3 386 octets | 12 | 29 | `/retail-lake/raw/nifi/` | Déposé par NiFi (UC4). Pas de ligne de titres, fins de ligne Windows, certaines colonnes vides |

#### 6. Observations

- **Fins de ligne Windows** : `file` affiche `with CRLF line terminators`. Chaque ligne finit par un caractère invisible en plus. Ce n'est pas un problème pour le dépôt, mais il faudra y penser au Jour 3 en lisant les données.
- **89M en local, 88.5 M dans HDFS** : les deux outils n'arrondissent pas pareil. La taille exacte est la même : 92 764 700 octets.
- **`cat: Unable to write to output stream`** : ce n'est pas une erreur. `head` s'arrête après 3 lignes et coupe la lecture.

### Étape 5 – Vérifier le stockage

> Commandes et résultats : `03_UC03_hdfs/preuves/etape5_sorties_commandes.txt`.

#### 1. Les contrôles

1. **Dossiers attendus** : les 10 dossiers sont là (`hdfs dfs -ls -R /retail-lake`).
2. **Fichier présent** : `store_sales.dat` dans `raw/tpcxbb/initial`.
3. **Taille** : 92 764 700 octets dans HDFS et en local.
4. **Permissions** : `-rw-r--r--`, `noah` peut lire et écrire, les autres seulement lire.
5. **Récupération** : `hdfs dfs -get` vers `/tmp`, la copie fait bien 92 764 700 octets.
6. **Comparaison avec l'original** : identique (voir ci-dessous).

#### 2. Méthode de comparaison

J'ai récupéré le fichier depuis HDFS dans `/tmp` (en dehors du projet, pour ne pas toucher aux données d'origine), puis je l'ai comparé au fichier local de 3 façons :

- **Empreinte SHA-256** (`sha256sum`) : un code calculé à partir de tout le contenu. Si un seul caractère change, le code change. Les deux fichiers ont le même code : `7e0a7f16b47483741754bb641c92601dd7384dacc8331d0bcfb8abac82ed3d2e`.
- **Comparaison octet par octet** (`cmp`) : aucune différence.
- **Nombre de lignes** (`wc -l`) : 667 579 des deux côtés.

Ensuite, j'ai supprimé la copie de `/tmp`.

Le fichier dans HDFS est donc exactement le même que l'original.

#### 3. Limite de la méthode

Il faut récupérer tout le fichier pour le comparer, ce qui serait long avec de très gros fichiers. Ici, avec 89 Mo, ça va vite.

## UC4

### Étape 6 – Découvrir l'environnement NiFi

> Commandes et résultats : `04_UC04_nifi/preuves/etape6_decouverte_nifi.txt`.
> Capture : `04_UC04_nifi/preuves/etape6_puthdfs_absent.jpg` (la recherche « PutHDFS » donne « Showing 0 of 294 »).

#### 1. Ce que j'ai relevé

- **Version de NiFi** : 2.12.0 (menu ☰ → *About*), avec Java 21.
- **Adresse** : https://localhost:8443/nifi.
- **État général** : démarré (`nifi.sh status` → `UP`), 2 cœurs, environ 45 % de la mémoire utilisée.
- **Composants disponibles** : `GetFile` et `LogAttribute` sont là. `PutHDFS` est absent : aucun module Hadoop n'est installé dans NiFi.
- **Services nécessaires** : HDFS démarré, les fichiers de configuration Hadoop lisibles par NiFi, et le module Hadoop de NiFi (manquant au début).
- **Sécurité** : connexion en HTTPS avec un certificat créé par NiFi (le navigateur affiche un avertissement), identifiant et mot de passe obligatoires, accès seulement depuis la machine.

Je n'ai pas recopié les identifiants de connexion (consigne du TP).

#### 2. Les notions de NiFi

- **FlowFile** : un fichier qui circule dans NiFi. Il contient les données et des informations sur ces données, appelées attributs (nom, chemin, date…).
- **Processor** : une étape qui fait une seule action. Par exemple, `GetFile` lit un fichier et `PutHDFS` l'écrit dans HDFS.
- **Connection** : le lien entre deux processeurs. Elle transporte les FlowFiles et sert de file d'attente.
- **Process Group** : une « boîte » qui regroupe plusieurs processeurs pour ranger un flux.
- **Controller Service** : un réglage partagé que plusieurs processeurs peuvent utiliser, par exemple une connexion à une base de données.
- **Provenance Repository** : l'historique de chaque FlowFile, avec l'heure de chaque événement. On peut retrouver le parcours d'un fichier.

Dans mon flux : `GetFile` lit le fichier et crée un FlowFile, la Connection l'amène à `PutHDFS`, qui l'écrit dans HDFS. Tout est noté dans le Provenance Repository.

#### 3. Erreurs rencontrées

| Erreur | Cause | Correction |
|---|---|---|
| NiFi ne démarre plus : `Both nifi.web.https.port and nifi.web.http.port specified` | Dans `nifi.properties`, les ports `http` et `https` étaient remplis tous les deux. NiFi n'en accepte qu'un | J'ai vidé les lignes `nifi.web.http.host` et `nifi.web.http.port`, puis relancé NiFi |
| NiFi démarré, mais la page ne s'ouvre pas dans le navigateur Windows | NiFi n'écoutait que sur `localhost` à l'intérieur de WSL, et WSL ne transmettait pas cette adresse à Windows | J'ai vidé `nifi.web.https.host` puis relancé NiFi. L'interface s'ouvre, et NiFi refuse toujours les autres adresses que `localhost` |
| `PutHDFS` n'existe pas | Depuis NiFi 2, le module Hadoop n'est plus installé de base | Corrigé à l'étape 8 |

### Étape 7 – Comprendre les éléments de l'interface NiFi

> Commandes et résultats : `04_UC04_nifi/preuves/etape7_preparation.txt`.

#### 1. Préparation

- **Dossier d'arrivée dans HDFS** : `hdfs dfs -mkdir -p /retail-lake/raw/nifi`. Il est séparé du dépôt de l'UC3 pour ne pas l'écraser et pouvoir comparer les deux méthodes.
- **Dossiers locaux** : `sudo mkdir -p /data/nifi/input /data/nifi/archive /data/nifi/error`, puis `sudo chown -R noah:noah /data/nifi` pour que NiFi (qui tourne avec `noah`) puisse les lire.
- **Fichier de test** : copie de `store.dat` dans `/data/nifi/input` (3 386 octets, 12 lignes, même empreinte que l'original).

J'ai choisi `store.dat` (la liste des magasins) parce que le TP demande un petit fichier pour le premier test. J'ai mis une copie, car GetFile supprime le fichier du dossier après l'avoir lu.

#### 2. Les éléments de l'interface

- **Processor** : le rectangle `GetFile` sur le canvas. On l'ajoute en faisant glisser le bouton *Processor*, puis en le cherchant dans *Add Processor*.
- **Process Group** : je travaille dans le groupe principal, « NiFi Flow » (écrit en bas à gauche).
- **FlowFile** : il apparaît quand GetFile lit `store.dat`.
- **Connection** et **Queue** : elles apparaissent quand on relie deux processeurs (étape 8). La Queue est le nombre de FlowFiles en attente, affiché sur la flèche.

#### 3. Erreurs rencontrées

| Erreur | Cause | Correction |
|---|---|---|
| GetFile en triangle jaune : `'Input Directory' … is invalid because Directory does not exist` | Le dossier `/data/nifi/input` n'existait pas encore | Création du dossier |
| `sudo: a password is required` | Créer un dossier dans `/data` demande les droits administrateur | Commande lancée avec les droits administrateur |

### Étape 8 – Construire le flux GetFile vers PutHDFS

> Captures : `04_UC04_nifi/preuves/etape8_flux_getfile_puthdfs.jpg` (le flux), `etape8_proprietes_getfile.jpg` et `etape8_proprietes_puthdfs.jpg` (les propriétés), `etape8_puthdfs_disponible.jpg` (PutHDFS après installation).

#### 1. Le flux

```
GetFile  --success-->  PutHDFS  --failure-->  LogAttribute
(lit le fichier local)  (écrit dans HDFS)      (note l'erreur dans les journaux)
```

#### 2. GetFile

- **Input Directory** : `/data/nifi/input`, le dossier où on dépose le fichier.
- **Keep Source File** : `false`, le fichier est retiré du dossier après lecture.
- **Recurse Subdirectories** : `false`, on ne lit pas les sous-dossiers (c'était `true` par défaut).

#### 3. PutHDFS

- **Hadoop Configuration Resources** : `/opt/hadoop/etc/hadoop/core-site.xml,/opt/hadoop/etc/hadoop/hdfs-site.xml`, pour que NiFi sache où est HDFS.
- **Directory** : `/retail-lake/raw/nifi`, séparé du dossier de l'UC3.
- **Conflict Resolution Strategy** : `fail`, si un fichier du même nom existe déjà, NiFi n'écrase rien et le FlowFile part en `failure`.

#### 4. Les relations

- `success` de GetFile → PutHDFS.
- `success` de PutHDFS → terminée automatiquement, le fichier est déposé.
- `failure` de PutHDFS → LogAttribute, pour voir l'erreur dans les journaux.
- `success` de LogAttribute → terminée automatiquement.

À la fin, les 3 processeurs sont valides et arrêtés.

#### 5. Erreurs rencontrées

| Erreur | Cause | Correction |
|---|---|---|
| `PutHDFS` absent (« Showing 0 of 294 ») | Depuis NiFi 2, le module Hadoop n'est plus installé de base | J'ai copié les 2 modules officiels `nifi-hadoop-libraries-nar` et `nifi-hadoop-nar` (2.12.0) dans `/opt/nifi/extensions`. NiFi les charge tout seul (`Loaded extensions … nifi-hadoop-nar:2.12.0`). Ensuite, 304 processeurs, dont PutHDFS |
| PutHDFS toujours absent juste après | La page gardait l'ancienne liste en mémoire | Rechargement de la page (F5) |

### Étape 9 – Démarrer et tester le flux

> Résultats : `04_UC04_nifi/preuves/etapes9_10_11_sorties.txt`.
> Capture : `04_UC04_nifi/preuves/etape9_flux_execute.jpg`.

#### 1. Ce que j'ai fait

1. Vérifié que `store.dat` était dans `/data/nifi/input` et que `/retail-lake/raw/nifi` existait.
2. Démarré PutHDFS d'abord, puis GetFile, pour que PutHDFS soit prêt quand le fichier arrive.
3. Regardé le canvas : un FlowFile de 3,31 Ko est passé dans la file `success`, puis PutHDFS l'a traité.

#### 2. Ce que j'ai vu dans NiFi

- GetFile : `Out 1 (3.31 KB)`, il a envoyé 1 FlowFile.
- PutHDFS : `In 1 (3.31 KB)`, il l'a reçu et écrit dans HDFS.
- Files `success` et `failure` vides à la fin : pas d'erreur.

#### 3. Vérification dans le terminal

```bash
hdfs dfs -ls -h /retail-lake/raw/nifi
hdfs dfs -du -h /retail-lake/raw/nifi
```

- Le fichier est dans HDFS : `/retail-lake/raw/nifi/store.dat`.
- Même taille que l'original : 3 386 octets.
- Même contenu : même empreinte SHA-256 et 12 lignes.
- Le dossier d'entrée est vide : GetFile a retiré la copie.
- L'original est toujours dans `retail_project/data/store/`.
- Le dépôt de l'UC3 n'est pas touché (NiFi écrit dans `raw/nifi`).

Ce dépôt a été fait par NiFi, sans `hdfs dfs -put`.

### Étape 10 – Tester une erreur simple

> Captures : `04_UC04_nifi/preuves/etape10_erreur_dossier_inexistant.jpg` (le message), `etape10_historique_configuration.jpg` et `etape10_historique_detail.jpg` (le journal des modifications de NiFi).

#### 1. Le test

J'ai choisi l'erreur « dossier source qui n'existe pas » :
1. Arrêt de GetFile.
2. `Input Directory` changé en `/data/nifi/dossier_inexistant`.
3. Observation.
4. Remise de `/data/nifi/input` juste après.

Je n'ai pas touché aux droits des dossiers HDFS, comme demandé dans le TP.

#### 2. Ce que j'ai vu

- GetFile passe en « Invalid » (triangle jaune) avec le message : `'Input Directory' validated against '/data/nifi/dossier_inexistant' is invalid because Directory does not exist`.
- Dans le clic droit, le bouton « Start » n'apparaît plus : NiFi refuse de démarrer un processeur mal configuré. On voit donc l'erreur avant de lancer le flux.
- Dans le journal des modifications (menu ☰ → *Flow Configuration History*), on retrouve la modification de 16:32:41 : ancienne valeur `/data/nifi/input`, nouvelle valeur `/data/nifi/dossier_inexistant`, puis la correction à 16:33:18.

#### 3. La correction

J'ai remis `Input Directory` à `/data/nifi/input`. GetFile redevient valide.

### Étape 11 – Traçabilité et provenance

> Captures : `04_UC04_nifi/preuves/etape11_provenance_evenements.jpg` (la liste), `etape11_provenance_detail_send.jpg` (le détail de l'envoi vers HDFS).

#### 1. Ce que j'ai relevé (menu ☰ → *Data Provenance*)

- **Identifiant du FlowFile** : `172e23a0-8a82-42c2-a0cc-54ce79146c6c`.
- **Nom du fichier** : `store.dat` (3,31 Ko).
- **Dossier d'origine** : `/data/nifi/input/`.
- **Destination** : `hdfs://localhost:9000/retail-lake/raw/nifi/store.dat`.
- **Durée totale** : environ 3,3 secondes.

#### 2. Les événements

1. **16:30:36 – `RECEIVE`** (GetFile) : NiFi a lu le fichier et créé le FlowFile.
2. **16:30:40 – `SEND`** (PutHDFS) : le fichier a été envoyé dans HDFS.
3. **16:30:40 – `DROP`** (PutHDFS) : le FlowFile est terminé (relation `success` terminée automatiquement).
4. **16:30:40 – `ATTRIBUTES_MODIFIED`** (PutHDFS) : PutHDFS a ajouté des informations, comme le chemin dans HDFS.

#### 3. Commentaire

Les 4 événements ont le même identifiant, donc je peux suivre le fichier du début à la fin : d'où il vient, à quelle heure il a été lu, par quel processeur il est passé et où il a été écrit dans HDFS. Si un fichier manquait ou était en double dans HDFS, on pourrait retrouver ce qui s'est passé.

## Reproduire l'ingestion (README)

### Versions

- Ubuntu 24.04 dans WSL (Windows 11).
- Hadoop 3.5.0 (Java 17).
- NiFi 2.12.0 (Java 21), avec les modules `nifi-hadoop-nar` et `nifi-hadoop-libraries-nar` 2.12.0.
- Python 3.12.3 (pas utilisé : pas besoin de solution de repli).

### Démarrage

```bash
start-dfs.sh                                   # HDFS (Java 17)
jps                                            # NameNode, DataNode, SecondaryNameNode
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
/opt/nifi/bin/nifi.sh start                    # NiFi (Java 21)
/opt/nifi/bin/nifi.sh status                   # doit afficher UP
```

Interface : https://localhost:8443/nifi (identifiants générés au premier démarrage, non recopiés ici).

### Chemins

- `/retail-lake/raw/tpcxbb/initial/store_sales.dat` : dépôt manuel (UC3).
- `/retail-lake/raw/nifi/` : dépôt par NiFi (UC4).
- `/data/nifi/input` : dossier lu par GetFile (y mettre une copie, jamais l'original).
- `/data/nifi/archive`, `/data/nifi/error` : créés, pas encore utilisés.

### Paramètres NiFi

- GetFile : `Input Directory = /data/nifi/input`, `Keep Source File = false`, `Recurse Subdirectories = false`.
- PutHDFS : `Hadoop Configuration Resources = /opt/hadoop/etc/hadoop/core-site.xml,/opt/hadoop/etc/hadoop/hdfs-site.xml`, `Directory = /retail-lake/raw/nifi`, `Conflict Resolution Strategy = fail`.
- Dans `nifi.properties`, `nifi.web.https.host` est laissé vide pour pouvoir ouvrir l'interface depuis le navigateur Windows.

### Arrêt (dans cet ordre)

1. Arrêter les processeurs dans NiFi (clic droit → *Stop*).
2. Arrêter NiFi : `/opt/nifi/bin/nifi.sh stop`.
3. Arrêter HDFS : `stop-dfs.sh`.

## Questions de recul

### 1. Quel est le rôle du NameNode dans HDFS ?
C'est le « chef » de HDFS. Il ne garde pas les données, mais il sait où elles sont : la liste des dossiers et des fichiers, et sur quel DataNode se trouve chaque bloc. Toutes les commandes `hdfs dfs` passent par lui. S'il s'arrête, on ne peut plus utiliser HDFS.

### 2. Quelle différence existe entre un NameNode et un DataNode ?
Le NameNode garde la liste des fichiers et sait où sont les blocs. Le DataNode garde les données elles-mêmes sur son disque. Il y a un seul NameNode mais il peut y avoir beaucoup de DataNodes (chez moi, un seul).

### 3. Pourquoi HDFS découpe-t-il les fichiers en blocs ?
Pour pouvoir ranger un gros fichier sur plusieurs machines, et pour lire plusieurs morceaux en même temps. Chez moi un bloc fait 128 Mo, donc `store_sales.dat` (89 Mo) tient dans un seul bloc.

### 4. Quel est l'intérêt de la réplication ?
Chaque bloc est copié sur plusieurs DataNodes (3 en général). Si une machine tombe en panne, il reste une copie ailleurs et on ne perd rien. Chez moi la réplication est à 1, donc il n'y a pas de copie de secours.

### 5. Pourquoi organiser un Data Lake en plusieurs zones ?
Pour séparer les données selon leur état : reçues (`raw`), rangées (`bronze`), nettoyées (`silver`), prêtes pour les indicateurs (`gold`). Comme ça on sait si une donnée est fiable, et on ne mélange pas les données brutes avec les données corrigées.

### 6. Pourquoi conserver les données sources dans Raw ?
Pour pouvoir tout refaire si un traitement est faux, sans redemander les données. Ça permet aussi de retrouver d'où vient un chiffre. C'est pour ça qu'on ne modifie jamais les fichiers de `raw`.

### 7. Quel est le rôle d'un FlowFile dans NiFi ?
C'est ce qui circule dans le flux : le contenu du fichier plus des informations dessus (nom, chemin, taille…). Dans mon flux, GetFile a créé un FlowFile avec `store.dat`, puis PutHDFS l'a écrit dans HDFS.

### 8. Quelle différence existe entre un Processor et une Connection ?
Le Processor fait une action (lire un fichier, écrire dans HDFS). La Connection relie deux processeurs : elle transporte les FlowFiles et sert de file d'attente.

### 9. Pourquoi la provenance est-elle importante ?
Elle permet de savoir ce qui est arrivé à un fichier : quand il a été lu, par où il est passé et où il a été écrit. Si un fichier manque ou est en double, on peut retrouver ce qui s'est passé. Pour `store.dat`, j'ai vu 4 événements, de la lecture (`RECEIVE`) à l'envoi dans HDFS (`SEND`).

### 10. Comment distinguer un échec technique d'un rejet métier ?
Un échec technique vient de l'outil : dossier introuvable, HDFS arrêté, problème de droits. Le fichier peut être bon, on règle le problème et on relance. Un rejet métier vient des données elles-mêmes : valeur impossible, colonne manquante. Là, relancer ne sert à rien, il faut corriger ou mettre les données de côté.

### 11. Quels risques apparaissent si un flux est relancé sans contrôle des doublons ?
Le même fichier peut être déposé deux fois, et les chiffres seraient faux (par exemple un chiffre d'affaires compté deux fois). Un fichier peut aussi être écrasé. Dans mon flux, PutHDFS est réglé sur `fail` : si le fichier existe déjà, il ne l'écrase pas et passe en erreur.

### 12. Quelles limites présente un environnement mono-nœud ?
Tout est sur une seule machine : si elle tombe en panne, tout s'arrête et on peut perdre les données (il n'y a qu'une copie). On ne peut pas non plus répartir le travail sur plusieurs machines. C'est bien pour apprendre, mais pas pour une vraie entreprise.

### 13. Pourquoi une copie locale ne constitue-t-elle pas une preuve de dépôt HDFS ?
Parce qu'un fichier sur le disque de l'ordinateur n'est pas dans HDFS : le NameNode ne le connaît pas. Pour prouver le dépôt, il faut voir le fichier avec une commande HDFS (`hdfs dfs -ls`) et vérifier son contenu, comme je l'ai fait à l'étape 5.

### 14. Quelles informations doivent être conservées pour reproduire une ingestion ?
- Le fichier source et d'où il vient.
- Sa taille, son nombre de lignes et son empreinte.
- Le chemin d'arrivée dans HDFS.
- Les versions des outils.
- La configuration du flux NiFi.
- Les commandes lancées, dans l'ordre.
- La date du dépôt et la provenance.
- Les erreurs et leurs corrections.
