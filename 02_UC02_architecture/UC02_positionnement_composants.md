# Positionnement des composants

| Composant | Statut | À quoi il sert chez nous |
|---|---|---|
| Linux / Ubuntu | Obligatoire | Le système où tout tourne |
| Python | Obligatoire | Explorer les fichiers (déjà fait dans UC-01) |
| Hadoop / HDFS | Obligatoire | Stocker les zones Bronze, Silver et Gold |
| Apache NiFi | Obligatoire | Déposer les fichiers dans Bronze |
| Spark / PySpark | Obligatoire | Nettoyer les données et calculer les KPI |
| Parquet | Format de référence | Format des zones Silver et Gold |
| ADLS Gen2 | Obligatoire (jour 4) | Remplace HDFS sur Azure |
| Azure Data Factory | Étude seulement | Pourrait remplacer NiFi sur Azure |
| Azure Synapse | Étude seulement | Pourrait remplacer Spark sur Azure |
| HBase | Facultatif | Non utilisé |
| Delta Lake | Facultatif | Non utilisé (permettrait de passer en Lakehouse) |
| PDGF | Selon le kit | Non utilisé : les données étaient déjà générées |

Notre architecture fonctionne **sans** HBase ni Delta Lake.
