# Tests de l'activité UC-07 – TP Jour 4 (§12.2)

Parcours B (local / open source) : la partie Azure est une simulation documentée, rien n'a été déployé.

| Contrôle | État | Preuve |
|---|---|---|
| Le rôle d'ADLS Gen2 est expliqué | ☑ | `docs/cloud/azure-architecture.md` (parties 2 et 3) |
| Le rôle du HNS est expliqué | ☑ | `docs/cloud/adls-organization.md` (partie 4) |
| Les zones Bronze, Silver et Gold sont organisées | ☑ | `docs/cloud/adls-organization.md` (parties 1 et 2), schéma de `azure-architecture.md` |
| Les chemins et conventions sont documentés | ☑ | arborescence et règles de nommage de `adls-organization.md` ; zones réelles dans `preuves/j4/architecture/sorties_commandes.txt` |
| La sécurité et les accès sont étudiés | ☑ | `docs/cloud/security-matrix.md` |
| Les rôles d'ADF et de Synapse sont distingués | ☑ | `docs/cloud/azure-architecture.md` (partie 4) |
| Le déploiement réel ou la simulation est clairement identifié | ☑ | `azure/simulation/simulation-adls-gen2.md` (tableau « exécuté / non exécuté ») |
| Les coûts et contraintes d'accès sont pris en compte | ☑ | `docs/cloud/azure-architecture.md` (partie 7) |
