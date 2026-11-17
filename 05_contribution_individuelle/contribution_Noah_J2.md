# Contribution Noah – Jour 2

## UC-03

### Étape 1 – Environnement Hadoop

Fait le 17 novembre 2026. Les résultats complets des commandes sont dans [preuves/etape1_sorties_commandes.txt](../03_UC03_hdfs/preuves/etape1_sorties_commandes.txt).

#### Commandes lancées

- `hadoop version` : voir la version de Hadoop.
- `jps` : voir les services qui tournent.
- `hdfs dfsadmin -report` : voir l'état de HDFS et des DataNodes.
- lecture des fichiers de configuration `core-site.xml` et `hdfs-site.xml`.
- recherche des erreurs dans les journaux (fichiers de log) de Hadoop.

#### Ce qu'on a relevé

| Élément | Valeur |
|---|---|
| Système | Ubuntu 24.04 dans WSL (Linux dans Windows 11) |
| Version de Hadoop | 3.5.0 |
| Chemin d'installation | `/opt/hadoop` |
| Configuration | Fichiers dans `/opt/hadoop/etc/hadoop`. HDFS est à l'adresse `hdfs://localhost:9000`, chaque fichier est gardé en **1 seul exemplaire**, découpé en blocs de **128 Mo** |
| NameNode | Démarré |
| DataNode | 1 seul DataNode, démarré et en état normal |
| Espace | Environ 930 Go libres, presque rien d'utilisé (HDFS est vide) |
| Erreurs au démarrage | Aucune erreur. Seulement quelques avertissements sans gravité |

#### Rôle du NameNode et des DataNodes

- **NameNode** : c'est le « chef ». Il ne garde pas les données, mais il sait où elles sont : la liste des dossiers et des fichiers, et sur quel DataNode se trouve chaque morceau de fichier. Si le NameNode est arrêté, on ne peut plus utiliser HDFS.
- **DataNode** : c'est un « ouvrier ». Il garde réellement les données sur son disque. Les fichiers sont découpés en morceaux (des **blocs**), et chaque DataNode stocke une partie de ces blocs. Il prévient régulièrement le NameNode qu'il fonctionne.

#### Une seule machine ou plusieurs ?

Notre environnement tourne sur **une seule machine** : le NameNode et le seul DataNode sont sur le même ordinateur. C'est un environnement pour apprendre, pas un vrai système d'entreprise : chaque fichier n'existe qu'en un seul exemplaire, donc si le disque tombe en panne, les données sont perdues.

---

### Étape 2 – Découverte des commandes HDFS

Fait le 17 novembre 2026. Les résultats complets sont dans [preuves/etape2_sorties_commandes.txt](../03_UC03_hdfs/preuves/etape2_sorties_commandes.txt).

#### Les 6 opérations demandées

| # | Opération | Commande | Résultat |
|---|---|---|---|
| 1 | État de HDFS | `hdfs fsck /` | `HEALTHY` : HDFS est en bon état |
| 2 | Informations sur les nœuds | `hdfs dfsadmin -report` | 1 DataNode actif (déjà vu à l'étape 1) |
| 3 | Lister les dossiers | `hdfs dfs -ls /` | Au début : rien. Après la création : `/retail-lake` |
| 4 | Créer un dossier de travail | `hdfs dfs -mkdir -p /retail-lake` | Aucun message, donc ça a marché |
| 5 | Vérifier les permissions | `hdfs dfs -ls -d /retail-lake` | `drwxr-xr-x   noah supergroup` |
| 6 | Taille des données | `hdfs dfs -du -s -h /retail-lake` | `0` : le dossier est vide |

#### Lire les permissions `drwxr-xr-x`

- `d` : c'est un dossier.
- `rwx` : le propriétaire (`noah`) peut lire, écrire et ouvrir le dossier.
- `r-x` : le groupe (`supergroup`) peut lire et ouvrir, mais pas écrire.
- `r-x` : les autres utilisateurs peuvent lire et ouvrir, mais pas écrire.

#### Erreurs rencontrées

Aucune vraie erreur. Mais au début, plusieurs commandes n'affichaient rien :
- `hdfs dfs -ls /` : HDFS était encore vide, il n'y avait rien à afficher.
- `hdfs dfs -mkdir` : cette commande n'affiche rien quand elle réussit.
- `hdfs dfs -du -h` : le dossier était vide. Avec l'option `-s`, la commande affiche quand même le total (`0`).

---

### Étape 3 – Création de l'arborescence du Data Lake

Fait le 17 novembre 2026. Les résultats complets sont dans [preuves/etape3_sorties_commandes.txt](../03_UC03_hdfs/preuves/etape3_sorties_commandes.txt).

#### Commandes lancées

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

La dernière commande affiche tous les dossiers créés : les 10 dossiers sont bien là. On a gardé l'arborescence proposée par le TP.

#### Schéma

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

#### Explications

- **Pourquoi garder les données sources ?** Si on fait une erreur plus tard dans un traitement, on peut tout refaire à partir des fichiers d'origine. Et on peut toujours retrouver d'où vient un chiffre.
- **Différence entre Raw et Bronze** : dans **Raw**, on met le fichier exactement comme on l'a reçu, et on n'y touche plus jamais. Dans **Bronze**, on a les mêmes données, mais rangées pour pouvoir les lire facilement (une table par dossier, avec la date du chargement). On ne corrige encore rien.
- **Rôle de Silver et Gold** : **Silver** contient les données nettoyées (sans doublons, avec les bons types, sans valeurs incorrectes). **Gold** contient les données organisées pour répondre aux questions du métier, par exemple le chiffre d'affaires par mois.
- **Pourquoi séparer les données, `quality` et `logs` ?** Pour ne pas mélanger les données avec les informations sur les traitements. Comme ça, on retrouve plus facilement une erreur, et on peut donner des droits différents : par exemple, les équipes métier peuvent lire `gold` sans voir `logs`.
- **Comment garder la provenance (l'origine des données) ?** Un dossier par source (`tpcxbb`) et par envoi (`initial`, `refresh`). On ne modifie jamais les fichiers de `raw`. Pour chaque fichier déposé, on note son nom, d'où il vient, sa taille, son nombre de lignes et la date du dépôt.

#### Différence avec le Jour 1

Au Jour 1, on avait appelé « Bronze » la zone qui garde les fichiers d'origine. Au Jour 2, cette zone s'appelle **`raw`**, et `bronze` devient une étape en plus. La zone « Quarantaine » du Jour 1 (les lignes refusées) va dans **`quality`**. Le document `UC02_architecture_cible.md` sera à mettre à jour lors de la mise en commun.

---

### Étape 4 – Dépôt des données TPCx-BB

Fait le 17 novembre 2026. Les résultats complets sont dans [preuves/etape4_sorties_commandes.txt](../03_UC03_hdfs/preuves/etape4_sorties_commandes.txt).

#### Fichier choisi

`store_sales.dat` (les ventes en magasin). C'est la table principale pour nos indicateurs du Jour 1, comme le chiffre d'affaires.

#### Avant le dépôt : examen du fichier

| Élément | Résultat | Commande |
|---|---|---|
| Chemin local | `retail_project/data/store_sales/store_sales.dat` | `ls -l` |
| Format | Fichier texte, colonnes séparées par `\|`, pas de ligne de titres | `file`, `head -n 3` |
| Taille | 92 764 700 octets (environ 89 Mo) | `ls -l`, `ls -lh` |
| Structure | 23 colonnes | `head -n 1` + `awk` |
| Nombre de lignes | 667 579 | `wc -l` |
| Provenance | Kit TPCx-BB fourni pour le projet, dossier `data/` (premier envoi) | — |
| Lisible | Oui, les premières lignes s'affichent | `head -n 3` |

La taille, le nombre de colonnes et le nombre de lignes sont les mêmes que dans l'inventaire du Jour 1.

#### Le dépôt

```bash
hdfs dfs -put retail_project/data/store_sales/store_sales.dat /retail-lake/raw/tpcxbb/initial/
```

Le fichier va dans `raw/tpcxbb/initial`, car il vient du dossier `data/`, c'est-à-dire du premier envoi de données.

#### Après le dépôt : vérifications

| Vérification | Résultat |
|---|---|
| Le fichier apparaît dans HDFS | Oui : `hdfs dfs -ls` montre `store_sales.dat` |
| La taille est cohérente | Oui : **92 764 700 octets** dans HDFS comme en local |
| Le fichier est accessible | Oui : `hdfs dfs -cat … \| head -n 3` affiche les mêmes 3 lignes qu'en local |
| Le chemin est correct | Oui : `/retail-lake/raw/tpcxbb/initial/store_sales.dat` |
| La source est conservée | Oui : le fichier local est toujours là, avec la même taille (`-put` copie le fichier, il ne le déplace pas) |

#### Fiche d'inventaire mise à jour

| Fichier | Format | Taille | Lignes | Colonnes | Chemin local | Chemin HDFS | Remarques |
|---|---|---|---|---|---|---|---|
| `store_sales.dat` | Texte, séparateur `\|` | 92 764 700 octets | 667 579 | 23 | `retail_project/data/store_sales/` | `/retail-lake/raw/tpcxbb/initial/` | Pas de ligne de titres. Fins de ligne Windows (voir plus bas) |

#### Observations

- **Fins de ligne Windows** : `file` indique `with CRLF line terminators`. Chaque ligne se termine par un caractère invisible en plus, comme les fichiers créés sous Windows. Ce n'est pas un problème pour le dépôt, car on copie le fichier tel quel. Il faudra y penser au Jour 3 au moment de lire les données, sinon la dernière colonne aura un caractère en trop.
- **Taille affichée différente (89M en local, 88.5 M dans HDFS)** : les deux outils n'arrondissent pas de la même façon. La taille exacte en octets est la même : 92 764 700.
- **`cat: Unable to write to output stream`** : ce n'est pas une erreur du dépôt. `head` s'arrête après 3 lignes et coupe la lecture, donc `cat` ne peut plus écrire la suite. C'est normal.

---

### Étape 5 – Vérification du stockage

Fait le 17 novembre 2026. Les résultats complets sont dans [preuves/etape5_sorties_commandes.txt](../03_UC03_hdfs/preuves/etape5_sorties_commandes.txt).

#### Les contrôles

| Contrôle | Commande | Résultat |
|---|---|---|
| Les dossiers attendus sont là | `hdfs dfs -ls -R /retail-lake` | Oui, les 10 dossiers de l'étape 3 |
| Le fichier est là | `hdfs dfs -ls` | Oui, `store_sales.dat` dans `raw/tpcxbb/initial` |
| La taille est la même | `hdfs dfs -ls` et `ls -l` | Oui, 92 764 700 octets des deux côtés |
| Les permissions | `hdfs dfs -ls` | `-rw-r--r--` : `noah` peut lire et écrire, les autres peuvent seulement lire |
| On peut récupérer le fichier | `hdfs dfs -get` vers `/tmp` | Oui, la copie récupérée fait 92 764 700 octets |
| Le fichier est identique à l'original | `sha256sum`, `cmp`, `wc -l` | Oui (détail ci-dessous) |

#### Méthode de comparaison utilisée

On a récupéré le fichier depuis HDFS dans `/tmp` (en dehors du projet, pour ne pas toucher aux données d'origine), puis on l'a comparé au fichier local de 3 façons :

1. **Empreinte SHA-256** (`sha256sum`) : un code calculé à partir de tout le contenu du fichier. Si un seul caractère change, le code change. Les deux fichiers ont le même code :
   `7e0a7f16b47483741754bb641c92601dd7384dacc8331d0bcfb8abac82ed3d2e`
2. **Comparaison octet par octet** (`cmp`) : aucune différence, la commande affiche `IDENTIQUES`.
3. **Nombre de lignes** (`wc -l`) : 667 579 lignes en local et dans HDFS.

Ensuite, on a supprimé la copie de `/tmp`.

**Conclusion** : le fichier stocké dans HDFS est exactement le même que le fichier d'origine. Rien n'a été perdu ni modifié pendant le dépôt.

#### Erreurs rencontrées

Aucune.

#### Limite de la méthode

On compare le fichier avec sa copie récupérée. C'est fiable, mais il faut récupérer tout le fichier, ce qui serait long avec de très gros fichiers. Ici, avec 89 Mo, ça va vite.

---

## UC-04

### Étape 6 – Découverte de l'environnement NiFi

Fait le 17 novembre 2026. Les résultats complets sont dans [preuves/etape6_decouverte_nifi.txt](../04_UC04_nifi/preuves/etape6_decouverte_nifi.txt).

#### Ce qu'on a relevé

| Élément | Valeur |
|---|---|
| Version de NiFi | 2.12.0 (menu ☰ → *About*) |
| Java utilisé par NiFi | Java 21 |
| Adresse de l'interface | https://localhost:8443/nifi |
| État général | Démarré (`nifi.sh status` → `UP`). 2 cœurs, environ 45 % de la mémoire utilisée, 8 % du disque utilisé |
| Composants disponibles | `GetFile` et `LogAttribute` sont présents. **`PutHDFS` est absent** : aucun module Hadoop n'est installé dans NiFi |
| Services nécessaires à l'ingestion | HDFS démarré, fichiers de configuration Hadoop (`core-site.xml`, `hdfs-site.xml`) lisibles par NiFi, et le module Hadoop de NiFi (manquant) |
| Contraintes de sécurité | Connexion en HTTPS avec un certificat créé par NiFi (le navigateur affiche un avertissement), identifiant et mot de passe obligatoires, accès seulement depuis la machine (`localhost`) |

Capture : [preuves/etape6_puthdfs_absent.jpg](../04_UC04_nifi/preuves/etape6_puthdfs_absent.jpg). Dans la fenêtre *Add Processor*, la recherche « PutHDFS » donne « Showing 0 of 294 » : aucun des 294 processeurs installés ne s'appelle PutHDFS.

Les identifiants de connexion ne sont pas recopiés ici (consigne du TP : pas de mot de passe dans le rendu).

#### Les notions de NiFi

- **FlowFile** : un fichier qui circule dans NiFi. Il contient les données (le contenu du fichier) et des informations sur ces données, appelées **attributs** (nom du fichier, chemin, date…).
- **Processor** : une étape du traitement, qui fait une seule action. Par exemple, `GetFile` lit un fichier dans un dossier et `PutHDFS` l'écrit dans HDFS.
- **Connection** : le lien entre deux processeurs. Elle transporte les FlowFiles de l'un à l'autre et sert de **file d'attente** quand le processeur suivant n'a pas encore traité les FlowFiles.
- **Process Group** : une « boîte » qui regroupe plusieurs processeurs et connexions, pour ranger un flux et le rendre plus lisible.
- **Controller Service** : un réglage partagé, que plusieurs processeurs peuvent utiliser. Par exemple, une connexion à une base de données, configurée une seule fois.
- **Provenance Repository** : l'historique de chaque FlowFile. NiFi y note tout ce qui lui est arrivé (créé, envoyé, supprimé…), avec l'heure. On peut ainsi retrouver le parcours d'un fichier.

Dans notre flux : `GetFile` (Processor) lit le fichier et crée un FlowFile, la Connection l'amène à `PutHDFS` (Processor), qui l'écrit dans HDFS. Tout ce parcours est noté dans le Provenance Repository.

#### Erreurs rencontrées

| Erreur | Cause | Correction |
|---|---|---|
| NiFi ne démarre plus : `Both nifi.web.https.port and nifi.web.http.port specified` | Dans `nifi.properties`, les ports `http` et `https` étaient tous les deux remplis (8443). NiFi n'accepte qu'un seul des deux | Lignes `nifi.web.http.host` et `nifi.web.http.port` vidées, puis redémarrage avec `nifi.sh start` |
| NiFi démarré, mais la page ne s'ouvre pas dans le navigateur Windows | NiFi écoutait seulement sur `localhost` *à l'intérieur* de WSL, et WSL ne transmettait pas cette adresse à Windows (alors que Hadoop, qui écoute sur toutes les adresses, était accessible) | `nifi.web.https.host` vidé pour que NiFi écoute sur toutes les adresses de WSL, puis redémarrage. L'interface s'ouvre. NiFi reste accessible seulement depuis le PC : il refuse toute autre adresse que `localhost` |
| `PutHDFS` n'existe pas dans NiFi | Depuis NiFi 2, le module Hadoop n'est plus installé de base | Corrigé à l'étape 8 en installant le module Hadoop de NiFi (on n'a pas remplacé le transfert par une commande, comme le demande le TP) |

---

### Préparation et étape 7 – Comprendre les éléments de l'interface NiFi

Fait le 17 novembre 2026. Les résultats complets sont dans [preuves/etape7_preparation.txt](../04_UC04_nifi/preuves/etape7_preparation.txt).

#### Préparation

| Action | Commande | Résultat |
|---|---|---|
| Dossier d'arrivée dans HDFS pour NiFi | `hdfs dfs -mkdir -p /retail-lake/raw/nifi` | Créé. Il est séparé du dépôt de l'UC-03 pour ne pas l'écraser et pouvoir comparer les deux méthodes |
| Dossiers locaux pour NiFi | `sudo mkdir -p /data/nifi/input /data/nifi/archive /data/nifi/error` puis `sudo chown -R noah:noah /data/nifi` | Créés, et `noah` (l'utilisateur qui fait tourner NiFi) en est propriétaire pour pouvoir les lire |
| Fichier de test | `cp …/retail_project/data/store/store.dat /data/nifi/input/` | Copie de `store.dat` : 3 386 octets, 12 lignes, même empreinte que l'original |

On a choisi `store.dat` (la liste des magasins) parce que le TP demande un **petit fichier** pour le premier test. C'est une **copie** : GetFile va supprimer le fichier du dossier d'entrée après l'avoir lu, donc on ne met jamais l'original dans ce dossier.

#### Les éléments de l'interface

| Élément | Où on le voit |
|---|---|
| **Processor** | Le rectangle `GetFile` placé sur le canvas. On l'ajoute en faisant glisser le bouton *Processor* de la barre d'outils, puis en le cherchant dans la fenêtre *Add Processor* |
| **Process Group** | On travaille dans le groupe principal, appelé « NiFi Flow » (écrit en bas à gauche) |
| **FlowFile** | Il apparaîtra quand GetFile lira `store.dat` : le contenu du fichier plus ses attributs (nom, chemin, date) |
| **Connection** et **Queue** | Pas encore visibles : elles apparaissent quand on relie deux processeurs (GetFile → PutHDFS, étape 8). La Queue est le nombre de FlowFiles en attente affiché sur la flèche |

#### Erreurs rencontrées

| Erreur | Cause | Correction |
|---|---|---|
| GetFile affiche un triangle jaune : `'Input Directory' … is invalid because Directory does not exist` | Le dossier `/data/nifi/input` n'existait pas encore | Création du dossier (voir préparation) |
| `sudo: a password is required` | Créer un dossier dans `/data` demande les droits administrateur | Commande lancée avec les droits administrateur |

---

### Étape 8 – Construire le flux GetFile vers PutHDFS

Fait le 17 novembre 2026, dans l'interface NiFi. Captures : [flux complet](../04_UC04_nifi/preuves/etape8_flux_getfile_puthdfs.jpg), [propriétés de PutHDFS](../04_UC04_nifi/preuves/etape8_proprietes_puthdfs.jpg), [PutHDFS disponible après installation](../04_UC04_nifi/preuves/etape8_puthdfs_disponible.jpg).

#### Le flux construit

```
GetFile  --success-->  PutHDFS  --failure-->  LogAttribute
(lit le fichier local)  (écrit dans HDFS)      (note l'erreur dans les journaux)
```

#### A. GetFile

| Propriété | Valeur | Pourquoi |
|---|---|---|
| Input Directory | `/data/nifi/input` | Le dossier où on dépose le fichier à envoyer |
| Keep Source File | `false` | Le fichier est retiré du dossier après lecture (on a gardé l'original ailleurs) |
| Recurse Subdirectories | `false` | On ne lit pas les sous-dossiers (la valeur par défaut était `true`, on l'a changée) |

#### B. PutHDFS

| Propriété | Valeur | Pourquoi |
|---|---|---|
| Hadoop Configuration Resources | `/opt/hadoop/etc/hadoop/core-site.xml,/opt/hadoop/etc/hadoop/hdfs-site.xml` | Pour que NiFi sache où se trouve HDFS (`hdfs://localhost:9000`) |
| Directory | `/retail-lake/raw/nifi` | Le dossier d'arrivée, séparé de celui de l'UC-03 |
| Conflict Resolution Strategy | `fail` | Si un fichier du même nom existe déjà, NiFi n'écrase rien : le FlowFile part en `failure` |

#### C. Les relations

| Processeur | Relation | Où elle va |
|---|---|---|
| GetFile | `success` | Vers PutHDFS (la flèche entre les deux) |
| PutHDFS | `success` | Terminée automatiquement : le fichier est déposé, le FlowFile n'a plus besoin d'aller ailleurs |
| PutHDFS | `failure` | Vers LogAttribute, pour voir l'erreur dans les journaux de NiFi |
| LogAttribute | `success` | Terminée automatiquement après avoir écrit dans les journaux |

À la fin, les 3 processeurs sont valides (aucun triangle jaune) et arrêtés. Le flux n'est pas encore démarré (c'est l'étape 9).

#### Erreurs rencontrées

| Erreur | Cause | Correction |
|---|---|---|
| `PutHDFS` absent de la liste des processeurs (« Showing 0 of 294 ») | Depuis NiFi 2, le module Hadoop n'est plus installé de base | Installation des 2 modules officiels `nifi-hadoop-libraries-nar` et `nifi-hadoop-nar` (version 2.12.0, depuis Maven Central) dans `/opt/nifi/extensions`. NiFi les charge tout seul (`Loaded extensions … nifi-hadoop-nar:2.12.0`). Après rechargement de la page : 304 processeurs, dont PutHDFS |
| PutHDFS toujours absent juste après l'installation | La page NiFi gardait l'ancienne liste en mémoire | Rechargement complet de la page (F5) |

---

### Étape 9 – Démarrer et tester le flux

Fait le 17 novembre 2026 vers 16h30. Les résultats complets sont dans [preuves/etapes9_10_11_sorties.txt](../04_UC04_nifi/preuves/etapes9_10_11_sorties.txt). Capture : [flux après le transfert](../04_UC04_nifi/preuves/etape9_flux_execute.jpg).

#### Ce qu'on a fait

1. Vérifié que `store.dat` était bien dans `/data/nifi/input` et que `/retail-lake/raw/nifi` existait dans HDFS.
2. Démarré **PutHDFS d'abord**, puis **GetFile**. Comme ça, quand GetFile envoie le fichier, PutHDFS est déjà prêt à le recevoir.
3. Regardé le canvas : un FlowFile de 3,31 Ko est passé dans la file `success`, puis PutHDFS l'a traité.

#### Ce qu'on a observé dans NiFi

| Élément | Résultat |
|---|---|
| GetFile | A lu 3,31 Ko et envoyé 1 FlowFile (`Out 1`) |
| PutHDFS | A reçu 1 FlowFile (`In 1`) et l'a écrit dans HDFS |
| File `success` | Vide à la fin : le FlowFile est bien passé |
| File `failure` | Vide : aucune erreur |

#### Vérification dans le terminal

```bash
hdfs dfs -ls -h /retail-lake/raw/nifi
hdfs dfs -du -h /retail-lake/raw/nifi
```

| Vérification | Résultat |
|---|---|
| Le fichier est dans HDFS | Oui : `/retail-lake/raw/nifi/store.dat` |
| La taille est la même | Oui : 3 386 octets, comme l'original |
| Le contenu est le même | Oui : même empreinte SHA-256 (`a936bc38…08ef`) et 12 lignes |
| Le dossier d'entrée est vide | Oui : GetFile a retiré la copie (`Keep Source File = false`) |
| L'original est conservé | Oui : `retail_project/data/store/store.dat` est toujours là |
| Le dépôt de l'UC-03 n'est pas touché | Oui : NiFi a écrit dans `raw/nifi`, pas dans `raw/tpcxbb/initial` |

Ce dépôt a été fait **par NiFi**, sans `hdfs dfs -put`.

#### Erreurs rencontrées

Aucune.

---

### Étape 10 – Tester une erreur simple

Fait le 17 novembre 2026 vers 16h32. Capture : [message d'erreur](../04_UC04_nifi/preuves/etape10_erreur_dossier_inexistant.jpg).

#### Le test

On a choisi l'erreur « dossier source qui n'existe pas » :

1. Arrêt de GetFile.
2. Changement de `Input Directory` : `/data/nifi/input` remplacé par `/data/nifi/dossier_inexistant`.
3. Observation du résultat.
4. Remise de la bonne valeur tout de suite après.

On n'a pas touché aux droits des dossiers HDFS, comme le demande le TP.

#### Ce qu'on a observé

- GetFile passe en **Invalid** (triangle jaune).
- Le message affiché est : `'Input Directory' validated against '/data/nifi/dossier_inexistant' is invalid because Directory does not exist`.
- Dans le menu du clic droit, le bouton **Start n'apparaît plus** : NiFi refuse de démarrer un processeur mal configuré. L'erreur est donc repérée **avant** de lancer le flux, et aucun fichier n'est perdu.

#### La correction

`Input Directory` remis à `/data/nifi/input`. GetFile redevient valide (carré rouge = arrêté, sans triangle).

---

### Étape 11 – Traçabilité et provenance

Fait le 17 novembre 2026 (menu ☰ → *Data Provenance*). Captures : [liste des événements](../04_UC04_nifi/preuves/etape11_provenance_evenements.jpg), [détail de l'envoi vers HDFS](../04_UC04_nifi/preuves/etape11_provenance_detail_send.jpg).

#### Ce qu'on a relevé

| Élément | Valeur |
|---|---|
| Identifiant du FlowFile (UUID) | `172e23a0-8a82-42c2-a0cc-54ce79146c6c` |
| Nom du fichier | `store.dat` |
| Taille | 3,31 Ko |
| Dossier d'origine | `/data/nifi/input/` |
| Destination | `hdfs://localhost:9000/retail-lake/raw/nifi/store.dat` |
| Durée totale du parcours | environ 3,3 secondes |

#### Les événements, dans l'ordre

| Heure | Événement | Processeur | Ce que ça veut dire |
|---|---|---|---|
| 16:30:36.889 | `RECEIVE` | GetFile | NiFi a lu le fichier dans le dossier local et créé le FlowFile |
| 16:30:40.169 | `SEND` | PutHDFS | Le fichier a été envoyé dans HDFS |
| 16:30:40.178 | `DROP` | PutHDFS | Le FlowFile est terminé (relation `success` terminée automatiquement) |
| 16:30:40.179 | `ATTRIBUTES_MODIFIED` | PutHDFS | PutHDFS a ajouté des informations au FlowFile (par exemple le chemin dans HDFS) |

#### Commentaire

Les 4 événements ont le **même identifiant**. On peut donc suivre le fichier du début à la fin : d'où il vient (`/data/nifi/input/store.dat`), à quelle heure il a été lu, par quel processeur il est passé, où il a été écrit dans HDFS et à quelle heure. S'il y avait un problème, par exemple un fichier manquant ou en double dans HDFS, on pourrait retrouver grâce à ces informations quand et par où il est passé.

---

### Reproduire l'ingestion (README)

#### Versions utilisées

| Composant | Version |
|---|---|
| Système | Ubuntu 24.04 dans WSL (Windows 11) |
| Hadoop | 3.5.0 (Java 17) |
| NiFi | 2.12.0 (Java 21) + modules `nifi-hadoop-nar` et `nifi-hadoop-libraries-nar` 2.12.0 |

#### Démarrage

```bash
start-dfs.sh                                   # HDFS (Java 17)
jps                                            # NameNode, DataNode, SecondaryNameNode
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
/opt/nifi/bin/nifi.sh start                    # NiFi (Java 21)
/opt/nifi/bin/nifi.sh status                   # doit afficher UP
```

Interface : https://localhost:8443/nifi (identifiants générés au premier démarrage, non recopiés ici).

#### Chemins

| Chemin | Rôle |
|---|---|
| `/retail-lake/raw/tpcxbb/initial/store_sales.dat` | Dépôt manuel (UC-03) |
| `/retail-lake/raw/nifi/` | Dépôt par NiFi (UC-04) |
| `/data/nifi/input` | Dossier lu par GetFile (y mettre une **copie**) |
| `/data/nifi/archive`, `/data/nifi/error` | Créés, pas encore utilisés |

#### Paramètres NiFi

- GetFile : `Input Directory = /data/nifi/input`, `Keep Source File = false`, `Recurse Subdirectories = false`.
- PutHDFS : `Hadoop Configuration Resources = /opt/hadoop/etc/hadoop/core-site.xml,/opt/hadoop/etc/hadoop/hdfs-site.xml`, `Directory = /retail-lake/raw/nifi`, `Conflict Resolution Strategy = fail`.
- `nifi.properties` : `nifi.web.https.host` vide et `nifi.web.https.port=8443` (pour accéder à l'interface depuis Windows).

#### Arrêt (dans cet ordre)

1. Arrêter les processeurs dans NiFi (clic droit → *Stop*).
2. Arrêter NiFi : `/opt/nifi/bin/nifi.sh stop`
3. Arrêter HDFS : `stop-dfs.sh`
