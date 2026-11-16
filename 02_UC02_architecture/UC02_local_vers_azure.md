# Du local vers Azure

⚠️ La partie Azure est un plan : rien n'est déployé (prévu au jour 4).

## 1. Comparaison

| Couche | Local (Linux / Ubuntu) | Azure |
|---|---|---|
| Sources | Fichiers du kit sur le disque | Fichiers déposés dans le conteneur `bronze` |
| Ingestion | NiFi | Data Factory (étude) ou NiFi sur une machine virtuelle |
| Stockage | HDFS : `/bronze`, `/silver`, `/gold`, `/quarantine` | ADLS Gen2 : conteneurs `bronze`, `silver`, `gold`, `quarantine` |
| Traitements | Spark en local | Spark dans Synapse (étude) |
| Format | Parquet (Delta Lake facultatif) | Parquet (Delta Lake facultatif) |
| Exposition | Notebooks, Spark SQL | Synapse SQL (étude) + outil de tableau de bord |
| Accès | Utilisateurs Linux + droits HDFS | Entra ID + RBAC + ACL |
| Supervision | Journaux NiFi et Spark, `run_log` | Azure Monitor, suivi Data Factory, `run_log` |
| Coût | Le matériel, pas de coût à l'usage | On paie ce qu'on utilise : stockage, opérations, calcul |

Les zones et les chemins sont **les mêmes** dans les deux environnements : on peut passer du local à Azure sans tout refaire.

## 2. La cible Azure

| Élément | Ce qu'on prévoit |
|---|---|
| **Compte de stockage** | Un compte avec l'option « espace de noms hiérarchique » activée : c'est ce qui en fait un ADLS Gen2, avec de vrais dossiers |
| **Conteneurs** | Un par zone : `bronze`, `silver`, `gold`, `quarantine` |
| **Organisation** | La même qu'en local : `zone/source/table/`, avec un dossier par lot dans Bronze |
| **Identités** | Chaque personne se connecte avec Entra ID (l'annuaire d'Azure). On donne les droits à des **groupes** (un par rôle), pas à des personnes |
| **RBAC** (droits par conteneur) | Équipe Data : lecture et écriture partout. Analystes : lecture sur `silver` et `gold`. Profils métier : lecture sur `gold` seulement |
| **ACL** (droits par dossier) | Des droits plus fins, par exemple réserver le dossier des stocks au responsable des stocks |
| **Secrets** | Les mots de passe et les clés sont rangés dans Azure Key Vault, jamais dans le code ni dans Git |
| **Coûts et quotas** | Le stockage d'1 Go coûte très peu. Ce sont surtout les calculs Spark qui coûtent : on les arrête quand on ne s'en sert pas. Alerte de budget, et vérification des limites de l'abonnement étudiant |
