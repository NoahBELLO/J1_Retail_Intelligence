# Retail Intelligence Platform – TP Jour 4 : UC-08, analyse des données et visualisation

Parcours **B – local / open source**. Les calculs sont faits avec PySpark, les petits résultats passent dans Pandas et les graphiques sont tracés avec Matplotlib dans JupyterLab. Aucune ressource cloud n'est utilisée.

Ce dossier **réutilise l'environnement et les données du TP3** (`tp3_lolo/`) : rien n'est réinstallé ni recopié.

## 1. Environnement de référence

| Composant | Version | Emplacement |
|---|---|---|
| Python | 3.14.4 | `tp3_lolo/.venv` (environnement du TP3) |
| Java | OpenJDK 21.0.13 | système |
| PySpark / Spark | 4.3.0 (mode local `local[2]`, 768 Mo pour le driver) | `tp3_lolo/.venv` |
| Pandas | 2.3.3 (PySpark 4.3 n'accepte pas encore pandas 3) | `tp3_lolo/.venv` |
| Matplotlib | 3.11.2 | `tp3_lolo/.venv` |
| JupyterLab | 4.6.6 | `tp3_lolo/.venv` |
| Noyau Jupyter | `retail-tp4` (« Python - Retail TP4 ») | `~/.local/share/jupyter/kernels/retail-tp4` |

Installation faite au TP4, en complément du TP3 :

```bash
cd ~/DEV/J1_Retail_Intelligence/tp3_lolo
source .venv/bin/activate
python -m pip install matplotlib "pandas<3"
python -m ipykernel install --user --name retail-tp4 --display-name "Python - Retail TP4"
```

Vérifications :

```bash
python -c "import matplotlib; print(matplotlib.__version__)"
python -c "import pandas; print(pandas.__version__)"
python -c "import pyspark; print(pyspark.__version__)"
jupyter lab --version
jupyter kernelspec list
```

## 2. Données utilisées

Les données Silver et Gold du TP3 sont lues sur place. Les chemins sont définis dans `config/parametres.json` :

```
../../tp3_lolo/retail-intelligence-platform/data/silver/   sales_enriched (+ sales, products, stores, dates)
../../tp3_lolo/retail-intelligence-platform/data/gold/     ca_annuel, ca_mensuel, ca_marge_par_categorie, ca_marge_par_magasin, top10_produits
../../tp3_lolo/retail-intelligence-platform/outputs/rapport_qualite.json
```

Si ces dossiers n'existent pas (les données ne sont pas versionnées), il faut d'abord relancer le pipeline du TP3 :

```bash
cd ~/DEV/J1_Retail_Intelligence/tp3_lolo/retail-intelligence-platform
./run_pipeline.sh
```

## 3. Reproduire les analyses

Dans JupyterLab :

```bash
cd ~/DEV/J1_Retail_Intelligence/tp3_lolo && source .venv/bin/activate
cd ../tp4_lolo/retail-intelligence-platform && jupyter lab
```

Ouvrir `analytics/notebooks/TP4_Retail_Intelligence.ipynb`, choisir le noyau **Python - Retail TP4**, puis lancer *Run > Run All Cells*.

Ou sans interface (environ 1 minute) :

```bash
cd ~/DEV/J1_Retail_Intelligence/tp4_lolo/retail-intelligence-platform/analytics/notebooks
nice -n 10 ../../../../tp3_lolo/.venv/bin/jupyter nbconvert --to notebook --execute --inplace TP4_Retail_Intelligence.ipynb
```

Le notebook recrée tous les CSV et les PNG. Il s'arrête (`assert`) si une clé n'est pas unique, si les KPI Silver diffèrent du Gold ou si un test UC-08 échoue.

## 4. Organisation

```
tp4_lolo/retail-intelligence-platform/
├── README.md                                  ce fichier
├── config/parametres.json                     chemins vers le TP3, paramètres Spark et graphiques
├── analytics/
│   ├── notebooks/TP4_Retail_Intelligence.ipynb   étapes 1 à 6 de l'UC-08
│   ├── outputs/                               tableaux CSV produits par le notebook
│   │   ├── inventaire_jeux.csv                étape 1
│   │   ├── kpi_dictionnaire.csv, kpi.csv      étape 2
│   │   ├── statistiques.csv, repartition_categories.csv   étape 3
│   │   ├── analyse_ca_mensuel.csv, analyse_saisonnalite.csv, analyse_categories.csv, ventes_par_magasin.csv   étape 4
│   │   └── tests_uc08.csv                     tests du § 12.1
│   └── visualizations/                        étape 5
│       ├── evolution_ventes_mensuelles.png
│       ├── ca_par_categorie.png
│       ├── ventes_par_magasin.png
│       └── distribution_montant_tickets.png
└── docs/analytics/
    ├── inventaire-jeux.md                     jeux utilisés, provenance, granularité, qualité
    ├── kpi-dictionary.md                      dictionnaire des KPI mis à jour + valeurs
    ├── business-analysis.md                   statistiques, analyses A1 à A3, visualisations
    └── interpretation.md                      constats, limites, recommandations
```

## 5. Livrables UC-08 (§ 9.1.4)

| # | Livrable | Fichier |
|---|---|---|
| 1 | Notebook d'analyse | `analytics/notebooks/TP4_Retail_Intelligence.ipynb` |
| 2 | Inventaire des jeux de données | `docs/analytics/inventaire-jeux.md`, `analytics/outputs/inventaire_jeux.csv` |
| 3 | Dictionnaire des KPI mis à jour | `docs/analytics/kpi-dictionary.md`, `analytics/outputs/kpi_dictionnaire.csv` |
| 4 | Statistiques descriptives | `analytics/outputs/statistiques.csv`, `docs/analytics/business-analysis.md` § 1 |
| 5 | Résultats des analyses métier | `analytics/outputs/analyse_*.csv`, `docs/analytics/business-analysis.md` § 2 |
| 6 | Visualisations (4) | `analytics/visualizations/*.png` |
| 7 | Constats, limites, recommandations | `docs/analytics/interpretation.md` |
| 8 | Instructions de reproduction | ce README, § 3 |

## 6. Vérification avant UC-08 (§ 1.17) et tests UC-08 (§ 12.1)

| Point à vérifier (§ 1.17) | Validation |
|---|---|
| JupyterLab s'ouvre, le noyau `retail-tp4` utilise `tp3_lolo/.venv` | ☑ |
| Import de PySpark, Pandas et Matplotlib | ☑ |
| Création d'une session Spark, lecture du Silver / Gold, agrégation | ☑ |
| Affichage d'un graphique et enregistrement en PNG | ☑ |

| Contrôle (§ 12.1) | État | Preuve |
|---|---|---|
| Les jeux de données utilisés sont identifiés | ☑ | `inventaire_jeux.csv`, `inventaire-jeux.md` |
| Les schémas et granularités ont été vérifiés | ☑ | `printSchema()` et clé unique vérifiée pour chaque jeu (étape 1) |
| Les KPI disposent d'une définition explicite | ☑ | `kpi-dictionary.md` |
| Les calculs sont reproductibles | ☑ | notebook ; KPI Silver = Gold `ca_annuel` |
| Les statistiques sont cohérentes avec les données | ☑ | somme des tickets = CA ; N = nombre de lignes |
| Les visualisations sont lisibles et légendées | ☑ | 4 PNG (titre, axes avec unité, légende, source) |
| Les interprétations sont justifiées | ☑ | `interpretation.md`, texte sous chaque graphique |
| Les limites des données sont mentionnées | ☑ | `interpretation.md` § Limites générales |

Les six premiers contrôles sont aussi vérifiés automatiquement en fin de notebook (`analytics/outputs/tests_uc08.csv`).

## 7. Limites

* Canal **magasin seulement** : `web_sales` et `store_returns` n'ont pas été transformés au TP3.
* **Échantillon** de 10 % des tickets (machine de 5 Go de RAM) : les totaux correspondent à environ un dixième du réseau.
* Données **synthétiques** TPCx-BB, devise supposée en euros, marge non qualifiée (non utilisée), paniers irréalistes (380 articles par ticket).
* Décembre 2005 incomplet (données jusqu'au 13/12) : les comparaisons de 2005 se font sur une période égale.
