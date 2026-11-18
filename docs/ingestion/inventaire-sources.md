# Inventaire des fichiers TPCx-BB utilisés

Livrable 3. L'inventaire complet des 23 tables du kit est dans `01_UC01_besoin_exploration/UC01_inventaire_sources.md` (Jour 1). Ici, seulement les fichiers utilisés au Jour 2.

> Preuves : `preuves/j2/hdfs/etape4_sorties_commandes.txt` (Noah), `preuves/j2/hdfs/etape4_depot_donnees_lorenzo.txt` (Lorenzo), `preuves/j2/nifi/etape7_preparation.txt`.

## 1. Matrice d'inventaire

| Fichier | Format | Taille | Lignes | Colonnes | Utilisé pour | Chemin HDFS |
|---|---|---|---|---|---|---|
| `store_sales.dat` | Texte, séparateur `\|` | 92 764 700 octets (89 Mo) | 667 579 | 23 | Dépôt manuel (UC3) | `/retail-lake/raw/tpcxbb/initial/store_sales/` |
| `store.dat` | Texte, séparateur `\|` | 3 386 octets | 12 | 29 | Test du flux NiFi (UC4) | `/retail-lake/raw/nifi/` |

## 2. Détail par fichier

### `store_sales.dat` (ventes en magasin)

- **Chemin local** : `retail_project/data/store_sales/store_sales.dat`.
- **Provenance** : kit TPCx-BB fourni pour le projet (`retail_project.zip`), dossier `data/` (premier envoi).
- **Structure** : 23 colonnes (`ss_sold_date_sk` … `ss_net_profit`, noms repris du schéma TPCx-BB), toutes les lignes ont 23 colonnes.
- **Empreinte SHA-256** : `7e0a7f16b47483741754bb641c92601dd7384dacc8331d0bcfb8abac82ed3d2e`.
- **Pourquoi ce fichier** : c'est la table principale pour nos indicateurs du Jour 1 (chiffre d'affaires, panier moyen…).
- **Limites** : pas de ligne de titres, fins de ligne Windows (`CRLF`), à gérer au Jour 3 en lisant les données.

### `store.dat` (magasins)

- **Chemin local** : `retail_project/data/store/store.dat`.
- **Provenance** : même kit, dossier `data/`.
- **Structure** : 29 colonnes (`s_store_sk` … `s_tax_precentage`).
- **Empreinte SHA-256** : `a936bc38692bdddc222cf86d08ed9d0feb761af26769212d789cf6729d1808ef`.
- **Pourquoi ce fichier** : le TP demande un petit fichier pour le premier test NiFi. On a utilisé une copie de travail, car GetFile retire le fichier du dossier d'entrée.
- **Limites** : pas de ligne de titres, fins de ligne Windows, certaines colonnes vides (par exemple `s_rec_end_date`).

Les tailles, colonnes et nombres de lignes sont les mêmes chez Noah et chez Lorenzo, et les mêmes que dans l'inventaire du Jour 1.
