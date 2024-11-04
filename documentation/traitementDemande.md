## Ajout d'une demande



| id  | attribut                | traitement                | Valeur par défaut           | champs à traiter                              |
|-----|-------------------------|---------------------------|-----------------------------|-----------------------------------------------|
| 1   | id                      | Par défaut                | int généré automatiquement  |                                               |
| 2   | usr_login               | Par défaut                | null                        |                                               |
| 3   | **id_acteur**           | Traitement                |                             |                                               |
| 4   | **id_organisme**        | Traitement                |                             |                                               |
| 5   | **motif**               | Extraction directe        |                             | Q2hhbXAtMzg4MzA3Nw==                          |
| 6   | **type_demande**        | Traitement                |                             | Q2hhbXAtMzg4MzA3Ng==                          |    
| 7   | **date_demande**        | Extraction / Traitement   |                             | dateDepot[:10]                                |
| 8   | **commentaire**         | Extraction / Traitement   |                             | Q2hhbXAtMzg4MzA3OQ== + Q2hhbXAtMzg4NDcxOA==   |
| 9   | **date_validit_min**    | Extraction directe        |                             | Q2hhbXAtMzg4MzY1Ng==                          |
| 10  | **date_validit_max**    | Extraction directe        |                             | Q2hhbXAtMzg4MzY1OQ==                          |
| 11  | date_creation           | Par défaut                | jour j                      |                                               |
| 12  | **libelle_geom**        | Traitement                |                             |                                               |
| 13  | geom                    | Par défaut                | null                        |                                               |
| 14  | **motif_anonyme**       | Extraction directe        |                             | Q2hhbXAtMzg4MzExMw==                          |
| 15  | statut                  | Par défaut                | "à traiter"                 |                                               |
| 16  | detail_decision         | Par défaut                | null                        |                                               |
| 17  | **critere_additionnel** | Traitement                |                             |                                               |
| 18  | perenne                 | Par défaut                | false                       |                                               |
| 19  | id_validateur           | Par défaut                | null                        |                                               |


