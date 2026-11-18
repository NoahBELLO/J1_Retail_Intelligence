# Tests UC4 – NiFi

Tests du §15.2. Le détail du flux est dans `docs/ingestion/flux-nifi.md`.

> Preuves : `preuves/j2/nifi/` (Noah et Lorenzo).

| Test | Résultat attendu | Preuve | Résultat | OK |
|---|---|---|---|---|
| Lecture source | Le fichier est lu par le flux | État du processeur : `etape9_flux_execute.jpg`, `etape9_flux_execute_lorenzo.png` | GetFile `Out 1 (3.31 KB)` | OK |
| Exécution du flux | Le FlowFile suit le chemin prévu | Capture NiFi : mêmes fichiers | Passage par `success`, PutHDFS `In 1`, file `failure` vide | OK |
| Dépôt HDFS | Le fichier est dans la destination | `hdfs dfs -ls /retail-lake/raw/nifi` (`etapes9_10_11_sorties.txt`, `etapes7_8_9_lorenzo.md`) | `store.dat`, 3 386 octets, même SHA-256 que l'original | OK |
| Erreur contrôlée | L'échec est identifiable | Journal des modifications NiFi : `etape10_historique_configuration.jpg`, `etape10_historique_detail.jpg` ; message : `etape10_erreur_dossier_inexistant.jpg` et `etape10_erreur_dossier_inexistant_lorenzo.png` | GetFile « Invalid », `Directory does not exist`, démarrage impossible | OK |
| Traçabilité | Le parcours peut être reconstitué | Provenance : `etape11_provenance_*` | 4 événements avec le même identifiant, de `RECEIVE` à `SEND` | OK |

## Refaire les tests

1. Remettre une copie de `store.dat` dans `/data/nifi/input`.
2. Retirer l'ancien dépôt, sinon PutHDFS (`fail`) l'envoie en `failure` : `hdfs dfs -rm /retail-lake/raw/nifi/store.dat`.
3. Démarrer PutHDFS puis GetFile.
4. Vérifier : `hdfs dfs -ls -h /retail-lake/raw/nifi`.
5. Arrêter les processeurs.
