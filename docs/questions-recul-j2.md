# Questions de recul – Jour 2

Réponses aux questions du §19 du TP.

## 1. Quel est le rôle du NameNode dans HDFS ?
C'est le « chef » de HDFS. Il ne garde pas les données, mais il sait où elles sont : la liste des dossiers et des fichiers, et sur quel DataNode se trouve chaque bloc. Toutes les commandes `hdfs dfs` passent par lui. S'il s'arrête, on ne peut plus utiliser HDFS.

## 2. Quelle différence existe entre un NameNode et un DataNode ?
Le NameNode garde la liste des fichiers et sait où sont les blocs. Le DataNode garde les données elles-mêmes sur son disque. Il y a un seul NameNode mais il peut y avoir beaucoup de DataNodes (chez nous, un seul sur chaque machine).

## 3. Pourquoi HDFS découpe-t-il les fichiers en blocs ?
Pour pouvoir ranger un gros fichier sur plusieurs machines, et pour lire plusieurs morceaux en même temps. Chez nous un bloc fait 128 Mo, donc `store_sales.dat` (89 Mo) tient dans un seul bloc.

## 4. Quel est l'intérêt de la réplication ?
Chaque bloc est copié sur plusieurs DataNodes (3 en général). Si une machine tombe en panne, il reste une copie ailleurs et on ne perd rien. Chez nous la réplication est à 1, donc il n'y a pas de copie de secours.

## 5. Pourquoi organiser un Data Lake en plusieurs zones ?
Pour séparer les données selon leur état : reçues (`raw`), rangées (`bronze`), nettoyées (`silver`), prêtes pour les indicateurs (`gold`). Comme ça on sait si une donnée est fiable, et on ne mélange pas les données brutes avec les données corrigées.

## 6. Pourquoi conserver les données sources dans Raw ?
Pour pouvoir tout refaire si un traitement est faux, sans redemander les données. Ça permet aussi de retrouver d'où vient un chiffre. C'est pour ça qu'on ne modifie jamais les fichiers de `raw`.

## 7. Quel est le rôle d'un FlowFile dans NiFi ?
C'est ce qui circule dans le flux : le contenu du fichier plus des informations dessus (nom, chemin, taille…). Dans notre flux, GetFile a créé un FlowFile avec `store.dat`, puis PutHDFS l'a écrit dans HDFS.

## 8. Quelle différence existe entre un Processor et une Connection ?
Le Processor fait une action (lire un fichier, écrire dans HDFS). La Connection relie deux processeurs : elle transporte les FlowFiles et sert de file d'attente.

## 9. Pourquoi la provenance est-elle importante ?
Elle permet de savoir ce qui est arrivé à un fichier : quand il a été lu, par où il est passé et où il a été écrit. Si un fichier manque ou est en double, on peut retrouver ce qui s'est passé. Pour `store.dat`, on voit 4 événements, de la lecture (`RECEIVE`) à l'envoi dans HDFS (`SEND`).

## 10. Comment distinguer un échec technique d'un rejet métier ?
Un échec technique vient de l'outil : dossier introuvable, HDFS arrêté, problème de droits. Le fichier peut être bon, on règle le problème et on relance. Un rejet métier vient des données elles-mêmes : valeur impossible, colonne manquante. Là, relancer ne sert à rien, il faut corriger ou mettre les données de côté.

## 11. Quels risques apparaissent si un flux est relancé sans contrôle des doublons ?
Le même fichier peut être déposé deux fois, et les chiffres seraient faux (par exemple un chiffre d'affaires compté deux fois). Un fichier peut aussi être écrasé. Dans notre flux, PutHDFS est réglé sur `fail` : si le fichier existe déjà, il ne l'écrase pas et passe en erreur.

## 12. Quelles limites présente un environnement mono-nœud ?
Tout est sur une seule machine : si elle tombe en panne, tout s'arrête et on peut perdre les données (il n'y a qu'une copie). On ne peut pas non plus répartir le travail sur plusieurs machines. C'est bien pour apprendre, mais pas pour une vraie entreprise.

## 13. Pourquoi une copie locale ne constitue-t-elle pas une preuve de dépôt HDFS ?
Parce qu'un fichier sur le disque de l'ordinateur n'est pas dans HDFS : le NameNode ne le connaît pas. Pour prouver le dépôt, il faut voir le fichier avec une commande HDFS (`hdfs dfs -ls`) et vérifier son contenu, comme on l'a fait à l'étape 5.

## 14. Quelles informations doivent être conservées pour reproduire une ingestion ?
- Le fichier source et d'où il vient.
- Sa taille, son nombre de lignes et son empreinte.
- Le chemin d'arrivée dans HDFS.
- Les versions des outils.
- La configuration du flux NiFi.
- Les commandes lancées, dans l'ordre.
- La date du dépôt et la provenance.
- Les erreurs et leurs corrections.
