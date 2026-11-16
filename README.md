# J1_Retail_Intelligence

TP Jour 1 – Retail Intelligence Platform (IPSSI). Socle obligatoire : UC-01 et UC-02.

## Contenu

### 01_UC01_besoin_exploration – Besoin métier et exploration des données
- `UC01_cadrage_metier.md` : profils utilisateurs
- `UC01_questions_decisionnelles.md` : questions, décisions et priorités
- `UC01_dictionnaire_KPI.md` : les 5 KPI
- `UC01_inventaire_sources.md` : inventaire des fichiers TPCx-BB
- `UC01_qualification_donnees.md` : qualité des données et relations entre tables
- `UC01_limites_et_hypotheses.md` : limites et hypothèses
- `UC01_schema_fonctionnel.md` : schéma utilisateurs → questions → KPI → données
- `preuves/` : scripts d'exploration et résultats

### 02_UC02_architecture – Architecture Data
- `UC02_comparaison_architectures.md` : contraintes et comparaison DW / Data Lake / Lakehouse
- `UC02_architecture_cible.md` : architecture logique et zones Bronze / Silver / Gold
- `UC02_schema_flux.md` : flux de données
- `UC02_positionnement_composants.md` : composants et leur statut
- `UC02_gouvernance.md` : règles de gouvernance
- `UC02_local_vers_azure.md` : comparaison local / Azure
- `preuves/`

### 05_contribution_individuelle
- `contribution_noah.md`
- `contribution_Lorenzo.md`
- `scripts/` : scripts de profilage et de vérification des relations (Lorenzo)

## Relancer les scripts d'exploration

Depuis `01_UC01_besoin_exploration/preuves/` :

```
python explorer_donnees.py <chemin vers retail_project>
python verifier_relations.py <chemin vers retail_project/data>
```

Les données (`retail_project/`) ne sont pas dans le dépôt, à cause de leur taille.
