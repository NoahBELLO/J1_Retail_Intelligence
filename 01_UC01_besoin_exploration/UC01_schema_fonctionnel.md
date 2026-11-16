# Schéma fonctionnel

Ce schéma relie les utilisateurs, leurs questions, les KPI, les domaines de données et les fichiers.
- Trait plein : source **vérifiée** (le fichier existe et a été examiné).
- Trait pointillé : source **souhaitée** mais absente ou inutilisable.

```mermaid
flowchart LR
    P1[P1 Direction générale]
    P2[P2 Contrôleur de gestion]
    P3[P3 Équipe Data]
    P4[P4 Direction commerciale]
    P5[P5 Responsable des stocks]
    P6[P6 Responsable de magasin]

    Q1[Évolution du CA]
    Q2[Part magasin / web]
    Q3[Marge par magasin]
    Q4[Niveau des remises]
    Q5[Qualité des données]
    Q6[Nouveaux chargements]
    Q7[Top produits et catégories]
    Q8[Ruptures et surstocks]
    Q9[Retards de livraison]
    Q10[CA par heure]
    Q11[Taux de retour]

    K1[KPI-01 Chiffre d'affaires]
    K2[KPI-02 Transactions]
    K3[KPI-03 Panier moyen]
    K4[KPI-04 Quantités]
    K5[KPI-05 Taux de remise]
    K6[KPI-06 Évolution du CA]

    D1[(store_sales)]
    D2[(web_sales)]
    D3[(item)]
    D4[(date_dim / time_dim)]
    D5[(inventory)]
    D6[(store_returns)]
    D7[(data_refresh/)]
    X1[Coûts des magasins]
    X2[Dates de livraison]

    P1 --> Q1 & Q2
    P2 --> Q3 & Q4
    P3 --> Q5 & Q6
    P4 --> Q7 & Q2
    P5 --> Q8 & Q9
    P6 --> Q10 & Q11

    Q1 --> K6
    Q2 --> K1
    Q4 --> K5
    Q7 --> K1 & K4
    Q10 --> K1
    Q3 -.-> X1
    Q9 -.-> X2
    Q8 --> D5
    Q11 --> D6
    Q5 --> D1 & D2 & D3
    Q6 --> D7

    K1 --> D1 & D2 & D4
    K2 --> D1 & D2
    K3 --> D1 & D2
    K4 --> D1 & D2 & D3
    K5 --> D1 & D2
    K6 --> D1 & D2 & D4
```

**Remarques**
- « Marge par magasin » (P2) et « Retards de livraison » (P5) ne sont pas couvertes : il manque les coûts et les vraies dates de livraison.
- « Ruptures et surstocks » (P5) est seulement possible par entrepôt, pas par magasin.
- KPI-02 et KPI-03 ne répondent pas à une question d'un profil : ils sont demandés par le TP.
