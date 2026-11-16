# Schéma fonctionnel

Ce schéma relie les utilisateurs, leurs questions, les KPI, les domaines de données et les fichiers.
- Trait plein : source **vérifiée** (le fichier existe et a été examiné).
- Trait pointillé : source **souhaitée** mais absente des données.

```mermaid
flowchart LR
    P1[P1 Direction générale]
    P2[P2 Contrôleur de gestion]
    P3[P3 Équipe Data]

    Q1[Évolution du CA]
    Q2[Part magasin / web]
    Q3[Marge par magasin]
    Q4[Niveau des remises]
    Q5[Qualité des données reçues]
    Q6[Nouveaux chargements]

    K1[KPI-01 Chiffre d'affaires]
    K2[KPI-02 Transactions]
    K3[KPI-03 Panier moyen]
    K4[KPI-04 Quantités]
    K5[KPI-05 Taux de remise]

    D1[Ventes magasin]
    D2[Ventes web]
    D3[Produits]
    D4[Dates]
    D5[Coûts des magasins]

    F1[(store_sales.dat)]
    F2[(web_sales.dat)]
    F3[(item.dat)]
    F4[(date_dim.dat)]
    F5[(data_refresh/)]
    F6[(Aucun fichier)]

    P1 --> Q1 & Q2
    P2 --> Q3 & Q4
    P3 --> Q5 & Q6

    Q1 --> K1
    Q2 --> K1
    Q4 --> K5
    Q3 -.-> D5

    K1 --> D1 & D2 & D4
    K2 --> D1 & D2
    K3 --> D1 & D2
    K4 --> D1 & D2 & D3
    K5 --> D1 & D2

    Q5 --> F1 & F2 & F3
    Q6 --> F5

    D1 --> F1
    D2 --> F2
    D3 --> F3
    D4 --> F4
    D5 -.-> F6
```

**Remarques**
- La question « marge par magasin » (P2) n'a pas de KPI parmi les 5 retenus. Elle demanderait aussi les coûts des magasins, qui ne sont pas dans les données.
- KPI-02, KPI-03 et KPI-04 ne répondent pas à une question d'un profil : ils sont demandés par le TP.
