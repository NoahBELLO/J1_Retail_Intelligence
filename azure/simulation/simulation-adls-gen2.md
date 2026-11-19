# Dossier de simulation ADLS Gen2 – TP Jour 4, UC-07 (J4-10)

> **Aucune ressource Azure n'a été créée.** On a choisi le parcours B (local / open source), donc il n'y a pas de captures du portail Azure. Ce dossier décrit la mise en œuvre qu'on ferait, comme le demande le TP (§9.2.3, étape 4).
>
> Preuve de ce qui est réellement exécuté en local : `preuves/j4/architecture/sorties_commandes.txt` (relevé du stockage HDFS, en lecture seule).

## 1. L'organisation cible

C'est celle de `docs/cloud/adls-organization.md` : un compte ADLS Gen2, 6 conteneurs (`raw`, `bronze`, `silver`, `gold`, `quality`, `logs`), et les mêmes chemins que dans HDFS.

## 2. Les ressources Azure nécessaires

- un **abonnement** (avec l'accord du formateur) ;
- un **groupe de ressources** `rg-retail-intelligence` ;
- un **compte de stockage** `stretailintelligence`, avec le **HNS activé** ;
- **6 conteneurs** : `raw`, `bronze`, `silver`, `gold`, `quality`, `logs` ;
- dans Entra ID, **des groupes** (un par profil de `docs/cloud/security-matrix.md`), pas des droits donnés personne par personne ;
- un coffre à secrets (**Key Vault**), si un service a besoin d'un mot de passe ;
- une **alerte de budget** sur le groupe de ressources.

## 3. Les opérations de création et de dépôt (non exécutées)

1. Se connecter au portail Azure avec son compte.
2. Créer le groupe de ressources `rg-retail-intelligence`.
3. Créer le compte de stockage `stretailintelligence`, en activant l'option **espace de noms hiérarchique** (HNS) : c'est ce qui en fait un ADLS Gen2.
4. Créer les 6 conteneurs, puis les dossiers de `adls-organization.md`.
5. Déposer le fichier de démonstration dans `gold/ca_par_categorie/`.
6. Donner les droits aux groupes (`security-matrix.md`).

Le **fichier de démonstration** serait `analytics/outputs/hdfs/ca_par_categorie.csv` (9 lignes, 629 octets). Il est petit, il ne contient aucune donnée personnelle, et ses données sont synthétiques.

## 4. Les contrôles qui seraient faits

1. **Le HNS est bien activé** : l'option apparaît comme activée dans les propriétés du compte.
2. **Le fichier est présent** : il apparaît dans le conteneur `gold`.
3. **Le fichier est intact** : même taille et même empreinte SHA-256 qu'en local, comme au Jour 2.
4. **Les droits marchent** : avec un compte du groupe « analystes », la lecture de `gold` doit marcher et l'écriture doit être refusée.
5. **Spark lit le fichier** : en changeant seulement le début du chemin dans les fichiers de paramètres.
6. **Nettoyage** : supprimer le groupe de ressources à la fin du test, pour ne rien payer.

## 5. Ce qui est réalisé et ce qui ne l'est pas

| Action | Statut |
|---|---|
| Zones `raw`, `bronze`, `silver`, `gold`, `quality`, `logs` dans HDFS | **Exécuté** (Jour 2, relevé au Jour 4) |
| Dépôt des fichiers sources dans `raw` (manuel et par NiFi) | **Exécuté** (Jour 2) |
| Traitements Spark Raw → Silver → Gold (chaîne des notebooks et chaîne HDFS) | **Exécuté** (Jour 3) |
| Analyses et graphiques depuis Silver et Gold | **Exécuté** (UC-08, Jour 4) |
| Abonnement, groupe de ressources, compte ADLS Gen2, conteneurs | **Non exécuté** (simulation) |
| Dépôt du fichier de démonstration sur Azure et contrôles | **Non exécuté** (simulation) |
| Groupes Entra ID, rôles RBAC, ACL Azure | **Non exécuté** (proposé dans `security-matrix.md`) |
| Data Factory, Synapse | **Étudié seulement** (`azure-architecture.md`) |
| Iceberg, Trino, catalogue, Airflow, Superset, MinIO | **Étudié seulement** |
