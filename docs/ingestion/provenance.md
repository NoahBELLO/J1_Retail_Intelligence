# Provenance

Documentation de la provenance du fichier transféré par NiFi (livrable 11 – étape 11 de l'UC4).

> Preuves : `preuves/j2/nifi/etape11_provenance_evenements.jpg`, `etape11_provenance_detail_send.jpg`, `etapes9_10_11_sorties.txt` (Noah), `etape11_provenance_evenements_lorenzo.png`, `etapes10_11_lorenzo.md` (Lorenzo).

## 1. Où la trouver

Menu ☰ → *Data Provenance*. On peut ouvrir le détail d'un événement (*View Details*) pour avoir plus d'informations.

## 2. Ce qu'on a relevé

| | Noah | Lorenzo |
|---|---|---|
| Identifiant du FlowFile | `172e23a0-8a82-42c2-a0cc-54ce79146c6c` | `ea90e04a-77a9-46ea-9f42-aaf2854224bf` |
| Nom | `store.dat` (3,31 Ko) | `store.dat` (3,31 Ko) |
| Lecture (`RECEIVE`) | 17/11/2026 16:30:36 | 18/11/2026 09:27:59 |
| Envoi dans HDFS (`SEND`) | 17/11/2026 16:30:40 | 18/11/2026 09:28:02 |
| Dossier d'origine | `/data/nifi/input/` | `/data/nifi/input/` |
| Destination | `hdfs://localhost:9000/retail-lake/raw/nifi/store.dat` | `hdfs://localhost:9000/retail-lake/raw/nifi/store.dat` |

## 3. Les événements, dans l'ordre

1. **`RECEIVE`** (GetFile) : NiFi lit le fichier dans `/data/nifi/input` et crée le FlowFile.
2. **`SEND`** (PutHDFS) : le fichier est écrit dans HDFS.
3. **`DROP`** (PutHDFS) : le FlowFile est terminé (relation `success` terminée automatiquement).
4. **`ATTRIBUTES_MODIFIED`** (PutHDFS) : PutHDFS ajoute des informations au FlowFile, comme le chemin du fichier dans HDFS.

## 4. À quoi ça sert

Les 4 événements ont le même identifiant. On peut donc suivre le fichier du début à la fin : d'où il vient, quand il a été lu, par quel processeur il est passé et où il a été écrit dans HDFS. Si un fichier manquait ou était en double dans HDFS, on pourrait retrouver ce qui s'est passé.

Avec les fiches de l'inventaire (nom, taille, empreinte SHA-256), on peut aussi vérifier que le fichier arrivé dans HDFS est bien celui qui a été envoyé.
