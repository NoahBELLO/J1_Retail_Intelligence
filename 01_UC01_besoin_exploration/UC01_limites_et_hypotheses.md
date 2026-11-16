# Limites et hypothèses

## 1. Limites

| # | Limite | Conséquence | Ce qu'on propose |
|---|---|---|---|
| L1 | **Une table présente n'est pas une table complète** : dates de fin toujours vides, `d_holiday` toujours `Y`, colonnes toujours `Unknown`, transporteurs et motifs de retour au hasard | Impossible d'analyser par transporteur, par motif de retour ou par jour férié | Vérifier en Silver le taux de remplissage **et** la variété des valeurs. Remplacer les identifiants vides par un membre « Inconnu » (-1) au lieu de supprimer la ligne |
| L2 | **Les ventes magasin et web ne sont pas décrites pareil** : 23 colonnes contre 34. Le web a un acheteur et un destinataire (différents dans 7 % des cas), une date d'expédition et des frais de port | Additionner les deux canaux demande de choisir les mêmes montants. Avec les frais de port, le CA web serait gonflé d'environ 55 % | Une table de ventes commune avec une colonne `canal`, et le montant `net_paid` (sans taxes ni port). Pour le web, le client est l'acheteur |
| L3 | **Une ligne de vente n'est pas une transaction** : un ticket a en moyenne 7,5 lignes. Les numéros de ticket et de commande ont la même plage (0 à 89 099) | Compter les lignes donne 7,5 fois trop de transactions | Compter les tickets et les commandes séparément, par canal |
| L4 | **Un clic n'est pas un achat** : 90 % des clics n'ont pas de vente, 42 % sont anonymes, aucun clic anonyme ne mène à un achat, pas d'action « ajout au panier » | Un « taux de conversion » d'environ 10 % ne veut rien dire | Présenter les clics comme de l'intérêt pour un produit, pas comme une intention d'achat |
| L5 | **Les retours ne sont pas des ventes** : ils sont dans des fichiers séparés, environ 3 % du CA, 20 % sont datés après la fin des ventes (jusqu'en 2008) | Le CA est calculé sans enlever les retours | Garder deux indicateurs (CA et montant des retours). Mettre de côté les retours de `data_refresh` sans vente |
| L6 | **Une corrélation n'est pas une cause** : il n'y a pas de groupe de comparaison, et les avis sont très positifs (61 % de 5/5) | « Les produits en promotion se vendent plus » ne prouve pas que la promotion en est la cause | Présenter ces liens comme des pistes, pas comme des preuves |
| L7 | **Les données sont fictives** : 50 % de remise en moyenne, bénéfice négatif sur 74 % des lignes, dates impossibles | Les résultats ne reflètent pas une vraie entreprise | Le préciser à chaque présentation des résultats |
| L8 | **Le stock est par entrepôt, pas par magasin**, et relevé une fois par semaine | Un magasin ne peut pas suivre son propre stock | Besoin non couvert : il faudrait les stocks des magasins |
| L9 | **Il n'y a pas d'objectifs de vente** | On ne peut pas comparer le réalisé à un objectif | Besoin non couvert |
| L10 | **`data_refresh` ne contient pas que des nouveautés** : le 13/12/2005 est dans les deux dossiers, et il y a des retours de 2001 à 2007 | Risque de doublons au chargement | Définir une règle pour enlever les doublons au chargement |

## 2. Hypothèses

| # | Hypothèse | À vérifier comment |
|---|---|---|
| H1 | Les noms et types des colonnes sont ceux du schéma officiel TPCx-BB (v1.7.0) | Demander la documentation au formateur |
| H2 | Les montants sont en euros | Demander au formateur |
| H3 | `data_refresh` s'ajoute à `data` (il ne le remplace pas) | Vérifier les doublons après fusion |
| H4 | `wcs_sales_sk` est un numéro de commande | Demander la documentation |
| H5 | `pr_order_sk` renvoie aux commandes web | Demander la documentation |

## 3. Ce qu'on ne peut pas calculer

| Besoin | Profil | Il manquerait |
|---|---|---|
| Réalisé vs objectif | P1 | Les objectifs de vente |
| Marge réelle | P2 | Les coûts (loyers, salaires) |
| Stock par magasin | P5 | Les stocks des magasins |
| Retards de livraison | P5 | Les dates de livraison réelles |
| Causes des retours | P6 | Des motifs de retour lisibles |
| Taux de conversion web | — | Les sessions des visiteurs |
