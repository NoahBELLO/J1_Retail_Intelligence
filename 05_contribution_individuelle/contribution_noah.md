# Contribution individuelle – Noah

## Utilisation d'un assistant IA

J'ai utilisé l'assistant IA Claude (Anthropic) pendant ce TP. Il m'a aidé à :
- identifier le schéma des fichiers `.dat` (ils n'ont pas d'en-tête) ;
- écrire les scripts Python d'exploration (`explorer_donnees.py`, `verifier_relations.py`) ;
- rédiger une première version des livrables d'UC-01 et d'UC-02.

J'ai relu, corrigé et fait des choix sur ce qu'il proposait (voir ci-dessous).

## Ce que j'ai fait

**Cadrage métier (UC-01, étapes A et B)**
- Première version des profils et de leurs responsabilités à partir du sujet.
- Choix des profils gardés : Direction générale, Contrôleur de gestion et Équipe Data. J'ai retiré un profil « Responsable e-commerce » proposé par l'IA, car il n'était pas dans le sujet.
- Choix de limiter le dictionnaire au minimum demandé, soit 5 KPI.
- Demande de simplification des textes, pour qu'ils restent compréhensibles et que je puisse les expliquer.
- Création et organisation des fichiers de livrables dans le dépôt Git.

**Sources examinées**
- Le kit `retail_project.zip` : les dossiers `data/` (23 fichiers) et `data_refresh/` (11 fichiers).

**Contrôles réalisés** (avec les scripts du dossier `01_UC01_besoin_exploration/preuves/`)
- Comptage des lignes, des colonnes et des valeurs vides de chaque fichier.
- Vérification que les identifiants des tables de référence sont uniques.
- Vérification des liens entre les ventes et les produits, magasins, clients et dates (valeurs sans correspondance).

**Décisions d'architecture**
- Data Lake en zones Bronze / Silver / Gold, avec une zone Gold organisée comme un Data Warehouse.
- Traitements en batch uniquement.

**Limites identifiées**
- Données fictives (50 % de remise en moyenne, nombres identiques de tickets et de commandes).
- Un clic n'est pas un achat (90 % des clics sans vente).
- Le stock est suivi par entrepôt et pas par magasin.
- 180 produits du stock n'existent que dans `data_refresh`.
