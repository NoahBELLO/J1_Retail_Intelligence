# Analyses du Jour 4 (UC-08) – reproduire les analyses

## Contenu

```
~/retail-intelligence/tp4/
├── README.md                                          ce fichier
└── analytics/
    ├── notebooks/TP4_Retail_Intelligence.ipynb        notebook d'analyse (exécuté, avec ses sorties)
    ├── outputs/
    │   ├── kpi.csv                                    KPI-01 à KPI-05 (total)
    │   ├── statistiques.csv                           statistiques descriptives
    │   ├── ca_par_categorie.csv                       analyse 1
    │   └── kpi_par_magasin.csv                        analyse 2
    └── visualizations/
        ├── ca_par_categorie.png                       graphique 1
        └── ca_par_magasin.png                         graphique 2
```

## Prérequis

- Ubuntu 24.04 dans WSL (8 Go de mémoire, 4 cœurs), Hadoop 3.5.0 dans `/opt/hadoop`.
- Données Silver et Gold du Jour 3 dans HDFS, produites par `~/retail-intelligence/tp3/scripts/lancer_tout.sh` :
  - `/retail-lake/silver/store_sales`, `/retail-lake/silver/item`
  - `/retail-lake/gold/ca_par_categorie`
- Environnement Python du TP3 (`~/retail-intelligence/tp3/.venv`), avec en plus Matplotlib, Pandas et le noyau Jupyter `retail-tp4`.

## Versions utilisées

| Outil | Version |
|---|---|
| Python | 3.12.3 |
| PySpark / Spark | 4.3.0, mode `local[*]`, 2 Go |
| Java (Spark) | OpenJDK 21.0.13 |
| JupyterLab | 4.6.6 |
| Pandas | 3.1.1 |
| Matplotlib | 3.11.2 |

PySpark 4.3.0 affiche un avertissement avec Pandas 3 (« pas encore complètement supporté »). Les résultats ont été contrôlés (sommes par dimension = total), mais en cas de problème, installer `pandas<3`.

## Installation (une seule fois)

```bash
cd ~/retail-intelligence/tp3
source .venv/bin/activate
python -m pip install matplotlib pandas jupyterlab ipykernel
python -m ipykernel install --user --name retail-tp4 --display-name "Python - Retail TP4"
```

## Lancement

```bash
start-dfs.sh
hdfs dfsadmin -safemode wait        # attendre "Safe mode is OFF"
cd ~/retail-intelligence/tp4/analytics/notebooks
source ~/retail-intelligence/tp3/.venv/bin/activate
jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.kernel_name=retail-tp4 TP4_Retail_Intelligence.ipynb
```

On peut aussi ouvrir le notebook dans JupyterLab (`jupyter lab` depuis `~/retail-intelligence/tp4`), choisir le noyau « Python - Retail TP4 » et tout exécuter. Durée : environ 1 minute.

Le notebook recalcule tous les tableaux et graphiques à partir de HDFS, et les écrit dans `../outputs/` et `../visualizations/`. Il doit être lancé depuis `analytics/notebooks/` à cause de ces chemins relatifs.

## Points d'attention

- **WSL s'arrête** quand aucune fenêtre ne l'utilise, et HDFS s'arrête avec lui. Vérifier `jps` avant de lancer.
- **Une seule session Spark à la fois** (fermer les autres notebooks).
- Les données lues ne sont jamais modifiées : le notebook ne fait que lire HDFS.
