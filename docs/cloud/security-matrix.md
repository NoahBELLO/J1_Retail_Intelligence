# Matrice des droits et principes d'accès – TP Jour 4, UC-07 (J4-09)

> Proposition pour Azure, **non déployée** (parcours B). La partie 3 décrit ce qui existe réellement en local.

## 1. Matrice des droits

On a adapté l'exemple du TP aux profils du Jour 1 (`02_UC02_architecture/UC02_gouvernance.md`), en suivant le principe du **moindre privilège** : chacun a seulement ce dont il a besoin.

| Profil | `raw` / `bronze` | `silver` | `gold` | `quality` / `logs` |
|---|---|---|---|---|
| Ingestion (compte technique NiFi ou Data Factory) | Écriture contrôlée (ajout de fichiers seulement) | Aucun accès | Aucun accès | Écriture des journaux |
| Équipe Data Engineering (et comptes techniques Spark) | Lecture | Lecture / écriture | Écriture contrôlée (par les traitements) | Lecture / écriture |
| Analyste | Aucun accès par défaut | Lecture | Lecture | Lecture de `quality` |
| Profils métier (P1, P2, P4) | Aucun accès | Aucun accès | Lecture | Aucun accès |
| Administrateur | Gestion selon habilitation | Gestion selon habilitation | Gestion selon habilitation | Gestion selon habilitation |

**Différences avec le Jour 1** : au Jour 1, l'équipe Data avait « lecture / écriture partout ». Ici, on est plus strict, comme le propose le TP : personne n'écrit à la main dans `raw` (seule l'ingestion y dépose), et `gold` n'est modifié que par les traitements.

**Sur Azure**, on donnerait les droits larges avec le RBAC (par exemple : les analystes lisent les conteneurs `silver` et `gold`), et les droits plus fins avec des ACL (par exemple : un responsable de magasin lit seulement le dossier de son magasin).

## 2. Les différences à connaître

- **RBAC** : des droits **larges**, donnés à une identité sur une ressource entière (le compte ou un conteneur). Exemple : « les analystes lisent tout le conteneur `gold` ».
- **ACL** : des droits **fins**, sur un dossier ou un fichier (lire, écrire, ouvrir), comme les droits `rwx` sous Linux. Exemple : « ce groupe lit seulement `gold/ca_marge_par_magasin/` ».
- **Identités et authentification** : Entra ID vérifie qui se connecte, une personne avec son compte ou un service comme Data Factory. On donne les droits à des groupes, pas personne par personne.
- **Secrets** : les mots de passe, les clés d'accès au stockage, les jetons. Ils ne doivent **jamais** être écrits dans le code ni dans Git : on les range dans un coffre à secrets (Key Vault sur Azure).

On ne donne pas de droits trop larges par simplicité (par exemple « tout le monde contributeur »).

## 3. Sécurité en local (ce qui existe vraiment)

Relevé sur la machine de Noah : `preuves/j4/architecture/sorties_commandes.txt`.

- **Comptes** : un seul compte Linux par machine, qui a aussi les droits administrateur (`sudo`).
- **Droits HDFS** : activés (`dfs.permissions.enabled = true`). Tous les dossiers sont en `drwxr-xr-x` et appartiennent au même utilisateur : lui seul peut écrire, tout le monde peut lire.
- **ACL HDFS** : elles sont activées (`dfs.namenode.acls.enabled = true`), mais aucune n'est posée (`getfacl` ne montre que les droits de base). On pourrait en poser comme sur Azure, par exemple pour donner la lecture de `gold` à un groupe « analystes ».
- **Vérification de l'identité** : HDFS croit le nom d'utilisateur Linux sans le vérifier. C'est acceptable seulement sur une machine personnelle.
- **Secrets** : aucun mot de passe dans le code (recherche `grep` : aucun fichier trouvé). Les identifiants de NiFi ne sont pas dans Git (`README.md`, partie Jour 2).
- **Séparation des environnements** : il n'y en a qu'un seul. Le dossier de test `tp3/` est même rangé dans le Data Lake HDFS. Il faudrait au moins séparer « test » et « production ».

## 4. Lien avec la protection des données (Jour 1)

Les règles prévues au Jour 1 restent valables : masquer les données personnelles des clients dès Silver, réserver Bronze à l'équipe Data, et n'avoir **aucune** donnée personnelle dans Gold. Nos jeux Gold actuels (CA par mois, par catégorie, par magasin) n'en contiennent pas, et la table des clients n'a pas encore été chargée.
