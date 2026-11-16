# Limites et hypothèses

## 1. Limites

| # | Limite | Conséquence |
|---|---|---|
| L1 | Les données sont fictives (50 % de remise en moyenne, autant de tickets que de commandes web) | Les résultats ne reflètent pas une vraie entreprise |
| L2 | Un fichier présent n'est pas forcément bien rempli (dates de fin vides, colonne inutilisable) | Certaines analyses sont impossibles |
| L3 | Les ventes magasin et web n'ont pas les mêmes colonnes (23 contre 34) | Il faut faire attention en les additionnant |
| L4 | Une ligne de vente n'est pas une transaction : un ticket contient plusieurs articles | Il faut compter les tickets, pas les lignes |
| L5 | Un clic n'est pas un achat : 90 % des clics n'ont pas de vente | On ne peut pas calculer un vrai taux de conversion |
| L6 | Les retours sont séparés des ventes | Le CA ne tient pas compte des retours |
| L7 | Une corrélation n'est pas une cause | Exemple : une promotion n'est pas forcément la raison d'une hausse des ventes |
| L8 | Le stock est par entrepôt, pas par magasin | Un magasin ne peut pas suivre son stock |
| L9 | Il n'y a pas d'objectifs de vente | On ne peut pas comparer le réalisé à un objectif |
| L10 | 2005 est incomplète dans `data/` | Il faut charger `data_refresh` |

## 2. Hypothèses

| # | Hypothèse | À vérifier comment |
|---|---|---|
| H1 | Les noms des colonnes sont ceux du schéma officiel TPCx-BB | Demander la documentation au formateur |
| H2 | Les montants sont en euros | Demander au formateur |
| H3 | `data_refresh` s'ajoute à `data` (il ne le remplace pas) | Vérifier les doublons après fusion |
| H4 | `net_profit` est le bénéfice après le prix d'achat | Demander la documentation |

## 3. Ce qu'on ne peut pas calculer

| Besoin | Il manquerait |
|---|---|
| Réalisé vs objectif | Les objectifs de vente |
| Stock par magasin | Les stocks des magasins |
| Taux de conversion web | Les sessions des visiteurs |
| Marge réelle | Les coûts (loyers, salaires) |
