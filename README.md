# J1_Retail_Intelligence

Retail Intelligence Platform (IPSSI).

- Jour 1 : UC-01 et UC-02 (besoin, exploration, architecture).
- Jour 2 : UC-03 et UC-04 (Data Lake HDFS, ingestion NiFi). Organisation des fichiers du Jour 2 selon le §17 du TP.

## Contenu – Jour 1

### 01_UC01_besoin_exploration – Besoin métier et exploration des données
- `UC01_cadrage_metier.md` : profils utilisateurs
- `UC01_questions_decisionnelles.md` : questions, décisions et priorités
- `UC01_dictionnaire_KPI.md` : les 6 KPI
- `UC01_inventaire_sources.md` : inventaire des fichiers TPCx-BB
- `UC01_qualification_donnees.md` : qualité des données et relations entre tables
- `UC01_limites_et_hypotheses.md` : limites et hypothèses
- `UC01_schema_fonctionnel.md` : schéma utilisateurs → questions → KPI → données
- `preuves/` : scripts d'exploration et leurs résultats
  - Noah : `explorer_donnees.py` → `inventaire_fichiers.csv`, `inventaire_colonnes.csv` ; `verifier_relations.py` → `resultats_relations.csv`
  - Lorenzo : `etape_c_profilage.py` → `etape_c_profil.json` ; `etape_d_relations.py` → `etape_d_relations.json` (les deux utilisent `tpcxbb_schema.json`)
  - `arborescence_donnees.txt`, `apercu_fichiers.txt` : liste des fichiers et aperçu de leur contenu

### 02_UC02_architecture – Architecture Data
- `UC02_comparaison_architectures.md` : contraintes et comparaison DW / Data Lake / Lakehouse
- `UC02_architecture_cible.md` : architecture logique et zones Bronze / Silver / Gold
- `UC02_schema_flux.md` : flux de données
- `UC02_positionnement_composants.md` : composants et leur statut
- `UC02_gouvernance.md` : règles de gouvernance
- `UC02_local_vers_azure.md` : comparaison local / Azure
- `preuves/`

## Contenu – Jour 2

### docs/
- `operations/environnement-j2.md` : nos deux machines, Hadoop, HDFS, NiFi (livrables 1 et 2)
- `ingestion/inventaire-sources.md` : fichiers TPCx-BB utilisés (livrable 3)
- `architecture/architecture-data-lake.md` : arborescence du Data Lake (livrable 4)
- `ingestion/flux-nifi.md` : flux GetFile → PutHDFS, configuration, exécution, erreur contrôlée (livrables 7, 8, 9)
- `ingestion/provenance.md` : provenance du fichier transféré (livrable 11)
- `operations/erreurs-corrections.md` : tableau des erreurs et des corrections (livrable 10)
- `questions-recul-j2.md` : questions de recul du TP

### ingestion/
- `nifi/flux_getfile_puthdfs.json` : export du flux NiFi (*Download Flow Definition*)

### tests/
- `hdfs/tests-uc03.md` : tests HDFS, commandes et contrôle d'intégrité (livrables 5 et 6)
- `ingestion/tests-uc04.md` : tests du flux NiFi

### preuves/j2/
- `hadoop/` : étape 1
- `hdfs/` : étapes 2 à 5
- `nifi/` : étapes 6 à 11 (captures et sorties)

Les fichiers `*_lorenzo.*` sont les preuves de Lorenzo, les autres celles de Noah.

## Contributions individuelles (05_contribution_individuelle)
- `contribution_Noah.md`, `contribution_Lorenzo.md` : Jour 1
- `contribution_Noah_J2.md` : Jour 2

## Relancer les scripts d'exploration

Depuis `01_UC01_besoin_exploration/preuves/` :

```
python explorer_donnees.py <chemin vers retail_project>
python verifier_relations.py <chemin vers retail_project/data>
python etape_c_profilage.py <chemin vers retail_project> etape_c_profil.json
python etape_d_relations.py <chemin vers retail_project> etape_d_relations.json
```

Les données (`retail_project/`) ne sont pas dans le dépôt, à cause de leur taille.

## Reproduire l'ingestion du Jour 2

### Versions
- Ubuntu 24.04 (WSL chez Noah, installé directement chez Lorenzo).
- Hadoop 3.5.0 avec Java 17, mode une seule machine (`hdfs://localhost:9000`, réplication 1).
- NiFi 2.12.0 avec Java 21, plus les modules `nifi-hadoop-libraries-nar` et `nifi-hadoop-nar` 2.12.0 dans `/opt/nifi/extensions`.

### Démarrage
```bash
start-dfs.sh                                   # HDFS (Java 17)
jps                                            # NameNode, DataNode, SecondaryNameNode
hdfs dfsadmin -report
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
/opt/nifi/bin/nifi.sh start                    # NiFi (Java 21)
/opt/nifi/bin/nifi.sh status                   # doit afficher UP
```
Interface : https://localhost:8443/nifi (identifiants générés au premier démarrage, dans `nifi-app.log`, non recopiés ici).

### Chemins HDFS
- `/retail-lake/raw/tpcxbb/initial/<table>/` : dépôt manuel (UC-03), par exemple `store_sales/store_sales.dat`.
- `/retail-lake/raw/nifi/` : dépôt par NiFi (UC-04).
- `/retail-lake/{bronze,silver,gold,quality,logs}` : zones prévues pour la suite.

### Paramètres NiFi (non sensibles)
- GetFile : `Input Directory = /data/nifi/input`, `Keep Source File = false`, `Recurse Subdirectories = false`.
- PutHDFS : `Hadoop Configuration Resources = /opt/hadoop/etc/hadoop/core-site.xml,/opt/hadoop/etc/hadoop/hdfs-site.xml`, `Directory = /retail-lake/raw/nifi`, `Conflict Resolution Strategy = fail`.
- Le flux complet peut être réimporté depuis `ingestion/nifi/flux_getfile_puthdfs.json`.
- Sous WSL, laisser `nifi.web.https.host` vide dans `nifi.properties` pour ouvrir l'interface depuis Windows.

### Arrêt (dans cet ordre)
1. Arrêter les processeurs dans NiFi (clic droit → *Stop*).
2. `/opt/nifi/bin/nifi.sh stop`
3. `stop-dfs.sh`
