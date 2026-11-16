# Positionnement des composants

| Composant | Statut | À quoi il sert chez nous | Zone / couche |
|---|---|---|---|
| Linux / Ubuntu | **Obligatoire** | Le système local (machine virtuelle ou WSL) où tournent HDFS, NiFi et Spark | Toutes |
| Python | **Obligatoire** | Explorer les fichiers (les 4 scripts d'UC-01), scripts de contrôle, PySpark | Exploration, Silver, Gold |
| Hadoop / HDFS | **Obligatoire** | Stocker les zones Bronze, Silver, Gold et la quarantaine, avec des droits par dossier | Stockage |
| Apache NiFi | **Obligatoire** | Récupérer les fichiers, faire les premiers contrôles, noter la provenance, déposer dans Bronze | Ingestion |
| Spark / PySpark | **Obligatoire** | Lire avec les bons noms de colonnes, nettoyer, contrôler, garder l'historique, construire l'étoile, calculer les KPI | Bronze → Silver → Gold |
| Parquet | **Format de référence** | Format des zones Silver, Gold et de la quarantaine | Silver, Gold |
| ADLS Gen2 | **Obligatoire** (jour 4) | Remplace HDFS sur Azure, avec les mêmes zones et les mêmes chemins. Conçu ici, déployé au jour 4 | Stockage cloud |
| Azure Data Factory | Étude seulement | Pourrait remplacer NiFi sur Azure. Non déployé | Ingestion cloud |
| Azure Synapse | Étude seulement | Requêtes SQL sur Gold et Spark sur Azure. Non déployé | Exposition cloud |
| HBase | Facultatif | Non utilisé. Pourrait servir à consulter très vite une fiche client ou le dernier stock d'un produit | Hors socle |
| Delta Lake | Facultatif | Non utilisé. Permettrait les mises à jour fiables et le retour à une version précédente (Lakehouse) | Silver, Gold (option) |
| PDGF | Selon le kit | Non utilisé : les données ont été fournies déjà générées | Sources |

**À retenir**
- L'architecture fonctionne **sans** HBase ni Delta Lake.
- Data Factory et Synapse sont décrits, pas déployés.
- L'outil de tableau de bord (Power BI, Superset…) n'est pas dans le référentiel et reste à choisir.
