# Tests de l'activité UC-08 – TP Jour 4 (§12.1)

## 1. Vérification avant de commencer UC-08 (§1.17)

| Point à vérifier | Lorenzo | Noah |
|---|---|---|
| JupyterLab s'ouvre | ☑ | ☑ |
| Le notebook utilise le bon environnement Python (noyau `retail-tp4`) | ☑ | ☑ |
| Import de PySpark, Pandas et Matplotlib | ☑ | ☑ |
| Création d'une session Spark | ☑ | ☑ |
| Chemins Silver et Gold connus, lecture d'un fichier du projet | ☑ (`data/`) | ☑ (HDFS) |
| Agrégation avec Spark | ☑ | ☑ |
| Affichage d'un graphique et enregistrement en PNG | ☑ | ☑ |

Preuves : README de chaque environnement (partie Jour 4 du `README.md`), `preuves/j4/installation/sorties_commandes.txt` (Noah).

## 2. Contrôles UC-08

| Contrôle | État | Preuve |
|---|---|---|
| Les jeux de données utilisés sont identifiés | ☑ | `docs/analytics/inventaire-jeux.md`, `analytics/outputs/inventaire_jeux.csv` |
| Les schémas et granularités ont été vérifiés | ☑ | `printSchema()` et clé unique vérifiée pour chaque jeu ; un ticket = un seul magasin (notebook HDFS) |
| Les KPI disposent d'une définition explicite | ☑ | `docs/analytics/kpi-dictionary.md`, `analytics/outputs/kpi_dictionnaire.csv` |
| Les calculs sont reproductibles | ☑ | les deux notebooks se relancent en entier (`nbconvert --execute`) ; KPI Silver = Gold `ca_annuel` ; CA Silver = Gold `ca_par_categorie` (écart 0,00) |
| Les statistiques sont cohérentes avec les données | ☑ | somme des tickets = CA ; N = nombre de lignes ; somme par magasin = total ; échantillon et fichier complet donnent les mêmes taux (écarts < 1 %) |
| Les visualisations sont lisibles et légendées | ☑ | 6 PNG dans `analytics/visualizations/` (titre, axes avec unité, légende, source) |
| Les interprétations sont justifiées | ☑ | `docs/analytics/interpretation.md`, commentaire sous chaque graphique |
| Les limites des données sont mentionnées | ☑ | `docs/analytics/interpretation.md`, partie « Limites générales » |

Les six premiers contrôles sont aussi vérifiés automatiquement à la fin du notebook principal (`analytics/outputs/tests_uc08.csv`, tous à `True`). Le notebook s'arrête (`assert`) si une clé n'est pas unique, si les KPI Silver diffèrent du Gold ou si un test échoue.
