# Du local vers Azure

⚠️ La partie Azure est un plan : rien n'est déployé (prévu au jour 4).

## 1. Comparaison

| Couche | Local (Linux / Ubuntu) | Azure |
|---|---|---|
| Sources | Fichiers du kit sur le disque | Dépôt dans un conteneur `landing` |
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
| **Compte de stockage** | Un compte avec l'option « espace de noms hiérarchique » activée : c'est ce qui en fait un ADLS Gen2 (vrais dossiers et droits par dossier). Région France Central. Copie des données dans un seul centre (LRS) pour la formation. Accès public désactivé, HTTPS obligatoire. Nom proposé : `stretailinteldev` |
| **Conteneurs** | Un par zone : `landing` (dépôt temporaire), `bronze`, `silver`, `gold`, `quarantine`, plus `logs` pour les journaux |
| **Organisation** | `bronze/tpcxbb/<table>/load_id=<date>_<initial ou refresh>/`, `silver/<domaine>/<table>/year=AAAA/month=MM/`, `gold/<sujet>/…`, `quarantine/<table>/load_id=…/` |
| **Identités** | Microsoft Entra ID (l'annuaire d'Azure). Un **groupe** par rôle (`grp-data-engineers`, `grp-analysts`, `grp-business-commercial`, `grp-business-stock`, `grp-store-managers`) : on ne donne jamais de droits à une personne directement. Data Factory et Synapse utilisent une identité managée, sans mot de passe |
| **RBAC** (droits par conteneur) | Ingestion : écriture sur `landing` et `bronze`. Traitements : écriture sur `silver`, `gold` et `quarantine`. Analystes : lecture sur `silver` et `gold`. Personne n'a les droits « propriétaire » sur les données |
| **ACL** (droits par dossier) | Les groupes métier ne lisent que `gold`. Le dossier `gold/stock` est réservé au responsable des stocks. Les nouveaux dossiers reçoivent automatiquement les mêmes droits. Le filtrage par magasin se fait dans l'outil de tableau de bord, car les ACL fonctionnent par fichier et pas par ligne |
| **Secrets** | Dans Azure Key Vault (par exemple le code utilisé pour masquer les données personnelles). Les clés d'accès du compte de stockage sont désactivées. Aucun secret dans le code ni dans Git |
| **Coûts** | Le stockage d'1 Go coûte quelques centimes par mois. Ce qui coûte, ce sont les opérations (beaucoup de petits fichiers) et les calculs (Synapse facture les données lues, d'où l'intérêt de Parquet et du rangement par date). Bronze passe en stockage « froid » (moins cher) après 30 jours. `landing` et `quarantine` sont vidés automatiquement |
| **Quotas** | Budget Azure avec alertes à 50 %, 80 % et 100 %. Étiquettes `projet` et `env` pour suivre les coûts. Vérifier les limites de l'abonnement étudiant pour Spark |
