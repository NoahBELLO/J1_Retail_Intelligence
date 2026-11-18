# Architecture du Data Lake

Arborescence HDFS et explications (livrable 4).

> Preuves : `preuves/j2/hdfs/etape3_sorties_commandes.txt` (Noah), `preuves/j2/hdfs/etape3_sorties_commandes_lorenzo.txt` (Lorenzo).

## 1. Arborescence

On a gardé l'arborescence proposée par le TP. On ajoute un sous-dossier par table dans `raw/tpcxbb/initial` et `raw/tpcxbb/refresh`, et un dossier `raw/nifi` pour le dépôt fait par NiFi.

```
/retail-lake/
├── raw/                       Les fichiers reçus, tels quels
│   ├── tpcxbb/                Source : les données TPCx-BB
│   │   ├── initial/           Premier envoi (dossier data/ du kit)
│   │   │   └── store_sales/   Un sous-dossier par table
│   │   └── refresh/           Envoi de mise à jour (dossier data_refresh/)
│   └── nifi/                  Fichiers déposés par le flux NiFi (UC4)
├── bronze/                    Les mêmes données, rangées pour être lues (Jour 3)
│   └── tpcxbb/
├── silver/                    Les données nettoyées (Jour 3)
├── gold/                      Les données prêtes pour les indicateurs (Jour 3)
├── quality/                   Les résultats des contrôles et les lignes refusées
└── logs/                      Les journaux des traitements
```

Commandes de création :

```bash
hdfs dfs -mkdir -p /retail-lake/raw/tpcxbb/initial
hdfs dfs -mkdir -p /retail-lake/raw/tpcxbb/refresh
hdfs dfs -mkdir -p /retail-lake/bronze/tpcxbb
hdfs dfs -mkdir -p /retail-lake/silver
hdfs dfs -mkdir -p /retail-lake/gold
hdfs dfs -mkdir -p /retail-lake/quality
hdfs dfs -mkdir -p /retail-lake/logs
hdfs dfs -mkdir -p /retail-lake/raw/nifi
hdfs dfs -ls -R /retail-lake
```

Les données vont dans cet ordre : raw → bronze → silver → gold.

## 2. Pourquoi un sous-dossier par table

On a choisi de ranger chaque table dans son propre dossier (`raw/tpcxbb/initial/store_sales/store_sales.dat`) :
- quand les 23 tables seront déposées, chacune sera à part et facile à retrouver ;
- au Jour 3, on pourra lire une table juste en donnant le nom de son dossier ;
- si une table arrive en plusieurs fichiers, ils restent ensemble.

Lors du premier test, Noah avait déposé le fichier directement dans `initial/` (`raw/tpcxbb/initial/store_sales.dat`). Lorenzo a utilisé le sous-dossier. On garde la version de Lorenzo comme règle du groupe, et Noah a ensuite déplacé son fichier dans le sous-dossier avec `hdfs dfs -mv` (même empreinte SHA-256 avant et après, voir `preuves/j2/hdfs/deplacement_store_sales.txt`).

## 3. Explications

- **Pourquoi garder les données sources ?** Si un traitement est faux, on peut tout refaire à partir des fichiers d'origine, sans redemander les données. On peut aussi retrouver d'où vient un chiffre.
- **Différence entre Raw et Bronze** : dans Raw, on met le fichier exactement comme on l'a reçu et on n'y touche plus jamais. Dans Bronze, on a les mêmes données, mais rangées pour être lues facilement (avec la date du chargement). On ne corrige encore rien.
- **Rôle de Silver et Gold** : Silver contient les données nettoyées (sans doublons, avec les bons types). Gold contient les données prêtes pour répondre aux questions du métier, par exemple le chiffre d'affaires par mois.
- **Pourquoi séparer les données, `quality` et `logs` ?** Pour ne pas mélanger les données avec les informations sur les traitements. On retrouve plus vite une erreur, et on peut donner des droits différents (le métier lit `gold` mais pas `logs`).
- **Comment garder la provenance ?** Un dossier par source (`tpcxbb`), par envoi (`initial`, `refresh`) et par table. Les fichiers de `raw` ne sont jamais modifiés. Pour chaque fichier, on note son nom, son origine, sa taille, son nombre de lignes, son empreinte SHA-256 et la date du dépôt (voir `docs/ingestion/inventaire-sources.md`). NiFi garde aussi l'historique de chaque fichier transféré (voir `docs/ingestion/provenance.md`).

## 4. Différence avec le Jour 1

| Jour 1 (`UC02_architecture_cible.md`) | Jour 2 (HDFS) |
|---|---|
| Bronze : fichiers d'origine, un dossier par lot | `raw/tpcxbb/initial` et `raw/tpcxbb/refresh` |
| (pas de zone équivalente) | `bronze/tpcxbb` : étape en plus, remplie au Jour 3 |
| Quarantaine : lignes rejetées | `quality/` |
| Silver, Gold | `silver/`, `gold/` |
| Journaux, `run_log` | `logs/` |

On a gardé le nom `raw` du TP pour les fichiers d'origine.
