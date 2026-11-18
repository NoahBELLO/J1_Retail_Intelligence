# Flux d'ingestion NiFi

Schéma du flux, configuration, exécution et erreur contrôlée (livrables 7, 8 et 9 – étapes 7 à 10 de l'UC4).

> Export du flux : `ingestion/nifi/flux_getfile_puthdfs.json` (menu clic droit sur le canvas → *Download Flow Definition*).
> Preuves : `preuves/j2/nifi/` (captures et sorties de Noah ; `etapes7_8_9_lorenzo.md` et `etapes10_11_lorenzo.md` pour Lorenzo).

## 1. Pourquoi NiFi après le dépôt manuel

À l'UC3, on a déposé le fichier à la main avec `hdfs dfs -put` pour apprendre les commandes HDFS. Avec NiFi, le transfert est automatique : quand un fichier arrive dans un dossier, NiFi le prend et l'envoie dans HDFS, sans relancer de commande. Le dépôt NiFi va dans un dossier à part (`/retail-lake/raw/nifi`) pour ne pas écraser celui de l'UC3.

## 2. Préparation

```bash
hdfs dfs -mkdir -p /retail-lake/raw/nifi
sudo mkdir -p /data/nifi/input /data/nifi/archive /data/nifi/error
sudo chown -R <utilisateur>:<utilisateur> /data/nifi      # l'utilisateur qui fait tourner NiFi
cp retail_project/data/store/store.dat /data/nifi/input/   # une copie, jamais l'original
```

Le fichier de test est une copie de `store.dat` (3 386 octets, 12 lignes), car le TP demande un petit fichier et GetFile retire le fichier du dossier après l'avoir lu.

## 3. Schéma du flux

```
GetFile  --success-->  PutHDFS  --failure-->  LogAttribute
(lit /data/nifi/input)  (écrit dans /retail-lake/raw/nifi)  (note l'erreur dans les journaux)
```

> Captures : `etape8_flux_getfile_puthdfs.jpg` (Noah), `etape8_flux_getfile_puthdfs_lorenzo.png` (Lorenzo).

## 4. Configuration

> Captures : `etape8_proprietes_getfile.jpg`, `etape8_proprietes_puthdfs.jpg`, `etape8_proprietes_puthdfs_lorenzo.png`.

### GetFile

| Propriété | Valeur | Pourquoi |
|---|---|---|
| Input Directory | `/data/nifi/input` | Le dossier où on dépose le fichier |
| Keep Source File | `false` | Le fichier est retiré après lecture (l'original est gardé ailleurs) |
| Recurse Subdirectories | `false` | On ne lit pas les sous-dossiers |

### PutHDFS

| Propriété | Valeur | Pourquoi |
|---|---|---|
| Hadoop Configuration Resources | `/opt/hadoop/etc/hadoop/core-site.xml,/opt/hadoop/etc/hadoop/hdfs-site.xml` | Pour que NiFi sache où est HDFS |
| Directory | `/retail-lake/raw/nifi` | Dossier séparé de l'UC3 |
| Conflict Resolution Strategy | `fail` | Si le fichier existe déjà, rien n'est écrasé : le FlowFile part en `failure` |

### Relations

- `success` de GetFile → PutHDFS.
- `success` de PutHDFS → terminée automatiquement (le fichier est déposé).
- `failure` de PutHDFS → LogAttribute, pour voir l'erreur dans les journaux.
- `success` de LogAttribute → terminée automatiquement.

Les 3 processeurs sont valides avant le démarrage.

## 5. Exécution (étape 9)

1. Vérifier que `store.dat` est dans `/data/nifi/input` et que `/retail-lake/raw/nifi` existe.
2. Démarrer PutHDFS, puis GetFile (clic droit → *Start*).
3. Le FlowFile passe par la file `success`, puis PutHDFS l'écrit dans HDFS.

> Captures : `etape9_flux_execute.jpg` (Noah), `etape9_flux_execute_lorenzo.png` (Lorenzo).

Résultat, identique sur nos deux machines :

| Vérification | Résultat |
|---|---|
| Compteurs NiFi | GetFile `Out 1 (3.31 KB)`, PutHDFS `In 1 (3.31 KB)`, files `success` et `failure` vides |
| Fichier dans HDFS | `hdfs dfs -ls /retail-lake/raw/nifi` → `store.dat`, 3 386 octets |
| Même contenu | `hdfs dfs -cat … \| sha256sum` → même empreinte que l'original (`a936bc38…08ef`), 12 lignes |
| Dossier d'entrée | Vide : GetFile a retiré la copie |
| Original | Toujours présent dans `retail_project/data/store/` |
| Dépôt de l'UC3 | Intact (NiFi écrit dans `raw/nifi`) |

Ce dépôt a été fait par NiFi, sans `hdfs dfs -put`.

## 6. Erreur contrôlée (étape 10)

Test choisi : un dossier source qui n'existe pas.

1. Arrêter GetFile.
2. Changer `Input Directory` en `/data/nifi/dossier_inexistant`.
3. Observer.
4. Remettre `/data/nifi/input`.

Ce qu'on observe :
- GetFile passe en « Invalid » (triangle jaune) avec le message : `'Input Directory' validated against '/data/nifi/dossier_inexistant' is invalid because Directory does not exist`.
- Le bouton « Start » disparaît : NiFi refuse de démarrer un processeur mal configuré. Aucun FlowFile n'est créé et rien n'est envoyé dans HDFS.
- Le journal des modifications de NiFi (menu ☰ → *Flow Configuration History*) garde la trace : ancienne valeur `/data/nifi/input`, nouvelle valeur `/data/nifi/dossier_inexistant`, puis la correction.

> Captures : `etape10_erreur_dossier_inexistant.jpg`, `etape10_historique_configuration.jpg`, `etape10_historique_detail.jpg` (Noah), `etape10_erreur_dossier_inexistant_lorenzo.png` (Lorenzo).

Correction : `Input Directory` remis à `/data/nifi/input`, GetFile redevient valide. On n'a pas touché aux droits des dossiers HDFS.

## 7. Limites

- Un seul fichier testé, comme le demande le TP pour le premier essai.
- Les dossiers `/data/nifi/archive` et `/data/nifi/error` sont créés mais pas encore utilisés.
- Avec `fail`, relancer le même fichier envoie le FlowFile en `failure` : pour refaire le test, il faut d'abord retirer `store.dat` de `/retail-lake/raw/nifi`.
