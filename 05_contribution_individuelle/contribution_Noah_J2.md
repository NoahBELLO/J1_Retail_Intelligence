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
