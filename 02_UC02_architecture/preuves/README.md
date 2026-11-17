# Preuves UC-02

UC-02 est un travail de conception : rien n'est encore déployé. Les preuves demandées par le TP (§5.2.16) se trouvent dans les livrables :

| Preuve demandée | Où la trouver |
|---|---|
| Schéma d'architecture | `architecture_tpcxbb_medallion.png` (ce dossier) et `UC02_architecture_cible.md`, section 1 |
| Schéma des flux | `UC02_schema_flux.md`, section 1 |
| Tableau de comparaison des architectures | `UC02_comparaison_architectures.md`, section 2 |
| Matrice de positionnement des composants | `UC02_positionnement_composants.md` |
| Description des zones de données | `UC02_architecture_cible.md`, section 3 |
| Règles de gouvernance | `UC02_gouvernance.md` |
| Comparaison local / cloud | `UC02_local_vers_azure.md` |

Les schémas sont écrits en Mermaid : ils s'affichent directement sur GitHub ou dans VS Code. On peut les exporter en image sur https://mermaid.live.

## Manipulations réellement effectuées

Au Jour 1, **aucun composant n'a été installé** : ni Hadoop / HDFS, ni NiFi, ni Spark, ni Azure. Ce n'était pas demandé par le TP (§3.1 : « Aucune installation de Hadoop, HBase, NiFi ou Spark n'est demandée » ; §5.2.8 : « Aucun déploiement technique complet n'est demandé »). L'architecture de ce dossier est donc une **conception**.

Les seules manipulations réellement faites sont l'exploration des données avec Python (4 scripts et leurs résultats). Elles sont décrites dans `01_UC01_besoin_exploration/preuves/README.md`.

Les preuves d'installation et de traitement (stockage HDFS, flux NiFi, fichiers Parquet, ADLS Gen2) seront ajoutées aux jours 2 à 4, quand ces outils seront mis en place.
