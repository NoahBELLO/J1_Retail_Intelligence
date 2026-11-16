# Gouvernance

| Règle | Ce qu'on prévoit |
|---|---|
| **Provenance** | Chaque fichier est rangé avec sa date de réception. Chaque ligne garde le nom de son fichier d'origine. Les données complémentaires sont rangées à part |
| **Documentation** | Un dictionnaire qui décrit chaque table et chaque colonne (point de départ : l'inventaire d'UC-01). Les dossiers sont nommés `zone/source/table/` |
| **Qualité** | À chaque chargement, on compte les lignes, les colonnes, les doublons et les vides. Si un contrôle échoue, le chargement est bloqué |
| **Accès** | Bronze et Silver : seulement l'Équipe Data. Gold : les profils métier (direction, contrôleur, commercial, stocks, magasins), en lecture seulement. Un responsable de magasin ne voit que son magasin |
| **Protection** | Les noms et emails des clients ne vont pas dans la zone Gold : les KPI n'en ont pas besoin |
| **Suivi** | Chaque traitement note dans un journal : la date, le fichier, le nombre de lignes et les erreurs |
| **Coûts et volumes** | Parquet prend moins de place. Les gros fichiers sont rangés par date. On surveille la taille des zones |
