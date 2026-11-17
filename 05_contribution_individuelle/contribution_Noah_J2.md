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
