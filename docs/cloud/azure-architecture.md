# Architecture Azure et architecture locale équivalente – TP Jour 4, UC-07 (J4-07)

## 1. Parcours choisi

On a choisi le **parcours B – local / open source**. On n'a pas d'abonnement Azure, et le TP dit que ce parcours est « une véritable modalité de réalisation » (§4.1).

| | Ce qu'on a fait |
|---|---|
| **Exécuté** (en local) | Stockage en zones (HDFS au Jour 2, disque local pour la chaîne des notebooks), ingestion NiFi (Jour 2), traitements Spark Raw → Silver → Gold (Jour 3), analyses et graphiques UC-08 (Jour 4) |
| **Proposé, non déployé** | Toute la partie Azure : aucune ressource Azure n'a été créée. La mise en œuvre est décrite dans `azure/simulation/simulation-adls-gen2.md` |
| **Étudié seulement** | Data Factory, Synapse, et les outils open source Iceberg, Trino, catalogue, Airflow, Superset, MinIO |

Autres documents UC-07 : `adls-organization.md` (zones, chemins, HNS), `security-matrix.md` (droits).

## 2. Les composants Azure et leur rôle

- **Abonnement Azure** : le « contrat » et la facture. Toutes les ressources du projet y sont rattachées. Ce n'est pas un serveur.
- **Groupe de ressources** : un dossier qui regroupe toutes les ressources du projet (`rg-retail-intelligence`). On peut suivre leur coût ensemble et tout supprimer d'un coup à la fin.
- **Compte de stockage** : la ressource qui stocke les fichiers du Data Lake (`stretailintelligence`).
- **Conteneur** : un grand dossier dans le compte de stockage. On prévoit un conteneur par zone.
- **ADLS Gen2** : ce n'est pas une ressource à part. C'est un compte de stockage dans lequel on a activé le HNS, pour qu'il soit adapté à l'analyse de gros volumes.
- **Hierarchical Namespace (HNS)** : l'option qui crée de vrais dossiers (voir `adls-organization.md`).
- **Microsoft Entra ID** : l'annuaire d'Azure. Il vérifie **qui** se connecte : une personne, un groupe ou une application.
- **Azure RBAC** : les droits donnés à une identité sur **une ressource entière** (le compte ou un conteneur).
- **ACL** : les droits **plus fins**, sur un dossier ou un fichier précis.

**Les relations entre ces composants**

```
Abonnement (paie)
└── Groupe de ressources rg-retail-intelligence
    └── Compte de stockage stretailintelligence  ← HNS activé = ADLS Gen2
        └── Conteneurs raw, bronze, silver, gold, quality, logs
            └── Dossiers et fichiers (store_sales/, item/, ...)

Entra ID  → dit QUI se connecte (personnes, groupes, applications)
RBAC      → donne des droits sur le compte ou un conteneur
ACL       → donne des droits sur un dossier ou un fichier
```

Pour lire un fichier, il faut donc une identité reconnue par Entra ID, puis un droit RBAC **ou** un droit ACL sur le chemin.

## 3. Schéma de l'architecture cible

Tout ce qui est Azure est **proposé, non déployé**. Entre crochets, l'équivalent local **exécuté**.

```
 SOURCES                         INGESTION                  STOCKAGE : ADLS Gen2 (HNS)                 TRAITEMENTS
┌──────────────────────┐      ┌─────────────────────┐     ┌──────────────────────────────┐        ┌──────────────────────┐
│ TPCx-BB (kit)        │      │ Azure Data Factory  │     │ raw     fichiers d'origine   │        │ Synapse Spark Pool   │
│ data/ (initial)      │ ───► │ copie + planning    │ ──► │ bronze  (prévu)              │ ◄────► │ nettoyage, Gold,     │
│ data_refresh/        │      │ [NiFi, scripts .sh] │     │ silver  ventes, produits...  │        │ contrôles qualité    │
│                      │      └─────────────────────┘     │ gold    CA mensuel, par      │        │ [Spark en local]     │
│ Données complément.: │                                  │         catégorie, magasin   │        └──────────────────────┘
│ aucune               │                                  │ quality rejets, rapports     │
└──────────────────────┘                                  │ logs    journaux             │
                                                          │ [HDFS /retail-lake, data/]   │
                                                          └──────────────┬───────────────┘
                                                                         │ lecture de gold
                                                          ┌──────────────▼───────────────┐
 SÉCURITÉ (toutes les couches)                            │ USAGES ANALYTIQUES           │
 Entra ID : un groupe par profil                          │ Synapse SQL,                 │
 RBAC par conteneur + ACL par dossier                     │ Power BI                     │
 Key Vault pour les secrets, alerte de budget             │ [notebooks UC-08, Matplotlib]│
 [comptes Linux + droits/ACL HDFS]                        └──────────────────────────────┘
```

- **Jeux Gold** : `ca_annuel`, `ca_mensuel`, `ca_marge_par_categorie`, `ca_marge_par_magasin`, `top10_produits`, `taux_remise_mensuel` (chaîne des notebooks) et `ca_par_categorie` (chaîne HDFS).
- **Données complémentaires** : aucune pour l'instant. Si on en ajoute, elles iront dans un dossier à part de `raw` (par exemple `raw/complementaire/`), pour ne pas les confondre avec TPCx-BB.

## 4. Rôle d'ADF et de Synapse

C'est seulement de l'étude : on n'a créé ni pipeline ni Workspace.

- **Azure Data Factory (ADF)** : il déplace les données et lance les traitements dans le bon ordre, à heure fixe ou quand un fichier arrive. On suit chaque exécution dans un tableau de bord. Il ne stocke pas les données et ne fait pas les gros calculs.
- **Azure Synapse Analytics** : un espace de travail qui regroupe plusieurs outils d'analyse (Spark, SQL, pipelines) au même endroit.
- **Synapse Studio** : l'interface web de Synapse, où l'on écrit les notebooks et les requêtes SQL.
- **Spark Pools** : des machines Spark gérées par Azure, qu'on allume pour un traitement. On paie le temps où elles tournent.
- **Capacités SQL** : interroger les données du Data Lake en SQL, par exemple les fichiers Parquet de `gold`.

**Qui fait quoi**

- **ADLS Gen2** : stocke les données.
- **Data Factory** : déplace les données et enchaîne les traitements.
- **Synapse** : l'environnement où l'on analyse et traite les données.
- **Spark** : le moteur qui fait les calculs, dans Synapse ou ailleurs.

**Dans notre projet**

- **ADF** remplacerait NiFi (copier les fichiers du kit dans `raw`) et nos scripts de lancement (`run_pipeline.sh`, `transformations/lancer_tout.sh`), en s'arrêtant si une étape échoue.
- **Un Spark Pool** exécuterait nos notebooks et scripts PySpark presque sans changement. Il suffirait de changer le début des chemins dans `config/parametres.json` et `transformations/config.py`.
- **Synapse SQL** permettrait aux analystes d'interroger `gold` en SQL, et de brancher Power BI dessus.

## 5. L'architecture sans Azure (parcours B)

1. **Zone de stockage** : on n'a pas utilisé MinIO.
   - **Chaîne HDFS** (Noah) : HDFS à l'adresse `hdfs://localhost:9000/retail-lake`, avec 1 NameNode et 1 DataNode sur une seule machine, et 1 seule copie de chaque fichier. Taille : 95 Mo dans `raw`, 42 Mo dans `silver`, 3 Ko dans `gold` (relevé : `preuves/j4/architecture/sorties_commandes.txt`).
   - **Chaîne des notebooks** (Lorenzo) : le disque local, dans les dossiers `data/silver/` et `data/gold/` du dépôt.
2. **Les zones** : ce sont des **dossiers** : `raw`, `bronze`, `silver`, `gold`, `quality`, `logs` dans HDFS, et `data/raw`, `data/bronze`, `data/silver`, `data/gold` sur le disque. Il y a un dossier par table à l'intérieur.
3. **Iceberg et Parquet** :
   - **Parquet** est un **format de fichier** : les données sont rangées par colonne et compressées. On l'utilise pour Silver et Gold.
   - **Apache Iceberg** est un **format de table** posé au-dessus des fichiers Parquet. Il ajoute un journal des modifications, qui donne un historique des versions, des écritures qui marchent en entier ou pas du tout, et la possibilité de faire évoluer le schéma.
   - Iceberg n'est pas installé, seulement étudié. Aujourd'hui, un `overwrite` remplace nos tables sans garder l'ancienne version.
4. **Traitement** : Apache Spark / PySpark 4.3.0 en local. Il fait tous les calculs : nettoyage, Gold, contrôles et analyses UC-08. **Exécuté.**
5. **Requêtes analytiques** : Spark SQL, déjà inclus dans PySpark. Nos calculs utilisent les fonctions DataFrame (`groupBy`, `agg`), qui font la même chose que du SQL. Trino n'est pas installé : il est étudié comme moteur SQL pour plusieurs utilisateurs à la fois.
6. **Catalogue** : on n'en a pas. On lit les données avec leur chemin, écrit dans les fichiers de paramètres. On propose un **Hive Metastore** ou **Nessie** si on veut écrire `SELECT * FROM gold.ca_mensuel` sans connaître le chemin.
7. **Orchestration** : aujourd'hui, `run_pipeline.sh` et `transformations/lancer_tout.sh` enchaînent les traitements, lancés à la main. NiFi fait l'ingestion (Jour 2). Une tâche `cron` pourrait les lancer chaque nuit, ou **Apache Airflow** pour avoir un vrai suivi des exécutions et des relances.
8. **Sécurité en local** : voir `security-matrix.md`, partie 3.

La démonstration du traitement local, demandée par le TP, est faite par les deux notebooks UC-08 (`analytics/notebooks/`), qui lisent Silver et Gold avec Spark.

## 6. Correspondance Azure / open source

| Rôle fonctionnel | Azure | Retenu chez nous | Non déployé | Limites de l'équivalence |
|---|---|---|---|---|
| Stockage Data Lake | ADLS Gen2 (HNS) | HDFS et disque local, dossiers par zone | MinIO | Une seule machine et une seule copie : si le disque casse, tout est perdu. ADLS garde plusieurs copies et grandit sans limite |
| Tables analytiques | Tables du Lakehouse (Delta / Parquet) | Parquet seul | Iceberg | Parquet seul n'a ni historique ni écriture « tout ou rien » |
| Traitement distribué | Synapse Spark Pool | Spark en local (`local[2]` et `local[*]`) | – | Même moteur et même code, mais une seule machine : pas de vraie répartition sur plusieurs serveurs |
| Requêtes SQL | Synapse SQL | Spark SQL / DataFrames | Trino | Pas de serveur SQL toujours disponible pour plusieurs analystes |
| Catalogue / métadonnées | Catalogue de Synapse | Chemins dans les fichiers de paramètres | Hive Metastore, Nessie | Il faut connaître le chemin, il n'y a pas de liste des tables |
| Intégration / orchestration | Azure Data Factory | NiFi (Jour 2) + scripts `.sh` | Airflow | Lancement à la main, pas de relance automatique ni d'alerte |
| Visualisation | Power BI | Matplotlib dans Jupyter | Superset | Graphiques fixes (PNG), pas de tableau de bord interactif |
| Identités et permissions | Entra ID, RBAC, ACL | Comptes Linux, droits HDFS | ACL HDFS, comptes séparés | Un seul utilisateur par machine, aucun vrai contrôle d'identité |
| Environnement d'exécution | Services gérés par Azure | WSL (Noah), Ubuntu installé (Lorenzo) | Docker, machine virtuelle | On doit tout installer, démarrer et réparer soi-même |

**Pourquoi il faut plusieurs outils pour remplacer Synapse** : Synapse est un seul service qui regroupe plusieurs fonctions déjà branchées entre elles (Spark pour calculer, SQL pour interroger, des pipelines pour enchaîner, un catalogue et un studio web). En open source, chaque fonction est un outil séparé :

- **Spark** pour les calculs ;
- **Trino** ou Spark SQL pour le SQL ;
- **Iceberg** pour les tables ;
- un **catalogue** (Nessie ou Hive Metastore) ;
- **Airflow** pour l'orchestration ;
- **Superset** pour les tableaux de bord.

Il faut les installer, les configurer et les faire marcher ensemble soi-même. C'est pour ça qu'« Iceberg = Synapse open source » est faux : Iceberg ne remplace qu'une seule de ces fonctions.

## 7. Justification des choix, coûts et limites

**Nos choix**

- **Parcours B** : pas d'abonnement Azure. Ça évite aussi tout risque de facture, et le TP l'autorise.
- **Mêmes zones et mêmes chemins** en local et sur Azure : le passage vers Azure ne change que le début des chemins dans les fichiers de paramètres.
- **Un conteneur par zone** : on peut donner les droits RBAC zone par zone, sans ACL compliquées.

**Coûts à surveiller sur Azure**

- **Le stockage** de nos quelques centaines de Mo coûterait très peu.
- **Ce qui coûte le plus**, ce sont les calculs : un Spark Pool ou un service SQL oublié et laissé allumé.
- **Les opérations et les sorties de données** sont aussi payantes : chaque lecture et écriture, et les données téléchargées hors d'Azure.
- **Les précautions** : une alerte de budget, l'arrêt automatique des Spark Pools, et la suppression du groupe de ressources à la fin.
- Le crédit gratuit n'empêche pas une facture une fois qu'il est épuisé.

**Limites**

- **Rien n'a été testé sur Azure** : les opérations sont seulement décrites (`azure/simulation/`).
- **La sécurité locale n'est pas représentative** : un seul utilisateur par machine, sans contrôle d'identité.
- **Iceberg, Trino, Airflow, MinIO et le catalogue** restent des composants étudiés, pas installés.
