# Du local vers Azure

⚠️ La partie Azure est un plan : rien n'est déployé (prévu au jour 4).

## 1. Comparaison

| | Local | Azure |
|---|---|---|
| Ingestion | NiFi | NiFi ou Data Factory |
| Stockage | HDFS | ADLS Gen2 |
| Traitements | Spark | Spark dans Synapse |
| Format | Parquet | Parquet |
| Accès | Droits des dossiers HDFS | Entra ID + RBAC + ACL |
| Mots de passe | Fichiers de configuration | Key Vault |

## 2. La cible Azure

| Élément | Ce qu'on prévoit |
|---|---|
| **Compte de stockage** | Un compte avec l'option « espace de noms hiérarchique » : c'est ce qui permet d'avoir de vrais dossiers (ADLS Gen2) |
| **Conteneurs** | Un par zone : `bronze`, `silver`, `gold` |
| **Organisation** | La même qu'en local : `zone/source/table/` |
| **Identités** | Chaque personne se connecte avec son compte Entra ID (l'annuaire d'Azure) |
| **RBAC** | Des rôles par conteneur. Équipe Data : lecture et écriture partout. Direction et contrôleur : lecture sur `gold` seulement |
| **ACL** | Des droits par dossier. Exemple : bloquer le dossier des clients |
| **Secrets** | Les mots de passe et les clés sont rangés dans Key Vault, jamais dans le code |
| **Coûts et quotas** | Le stockage coûte peu, mais les calculs Spark coûtent cher : on les arrête quand on ne s'en sert pas. On met une alerte de budget et on vérifie les limites de l'abonnement étudiant |

## 3. Ce qui change

- **Pareil** : les zones, le format Parquet, les règles de qualité.
- **Différent** : le lieu de stockage, la gestion des accès, et des coûts qui dépendent de l'utilisation.
