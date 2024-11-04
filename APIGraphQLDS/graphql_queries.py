# Requêtes à l'API GraphQL


from gql import gql
import fonctionsUtiles as fu
import pandas as pd






def getDossiersUpdatedSince(client, numDemarche, date):
    """
    Fonction permettant de récupérer tous les dossiers 'en instruction' et 'en construction corrigé' déposés à partir d'une date donnée.

    Args:
        client (gql.client.Client): client GraphQL pour échanger avec l'API de Démarches Simplifiées
        numDemarche (int): Numéro de la démarche concernée
        date (str): Date à partir de laquelle la sélection est effectuée (format 'YYYY-MM-DD')
    
    Returns:
        <pd.DataFrame>: DataFrame concaténé avec tous les dossiers 'en instruction' et 'en construction corrigé'
    """

    # Charger les requêtes GraphQL depuis des fichiers externes gql
    with open('APIGraphQLDS/getDossiers_EnInstruction_UpdatedSince.gql', 'r') as file:
        queryEnInstruction = gql(file.read())
    with open('APIGraphQLDS/getDossiers_EnConstruction_UpdatedSince.gql', 'r') as file:
        queryEnConstruction = gql(file.read())

    # Variables pour la requête
    variables = {
        "demarcheNumber": numDemarche,
        "updatedSince": date
    }

    try:
        # Exécuter les requêtes pour obtenir les dossiers en instruction et en construction
        responseEnInstruction = client.execute(queryEnInstruction, variable_values=variables)
        responseEnConstruction = client.execute(queryEnConstruction, variable_values=variables)

        # Accéder aux dossiers dans les réponses
        dossiersEnInstruction = responseEnInstruction['demarche']['dossiers']['nodes']
        dossiersEnConstruction = responseEnConstruction['demarche']['dossiers']['nodes']

        # Transformer les données en DataFrame
        df_dossiersEnInstruction = pd.json_normalize(dossiersEnInstruction, sep='_')
        df_dossiersEnConstruction = pd.json_normalize(dossiersEnConstruction, sep='_')

        # Concaténer les deux DataFrames
        df_dossiers = pd.concat([df_dossiersEnInstruction, df_dossiersEnConstruction], ignore_index=True)
        
        # Filtrer les dossiers où 'dateDerniereCorrectionEnAttente' est null
        # pour exclure les dossiers avec la mention "en attente"
        df_dossiers = df_dossiers[
            df_dossiers['dateDerniereCorrectionEnAttente'].isnull()
        ]

        return df_dossiers

    except Exception as e:
        # Gestion d'erreur et retour d'un message explicatif
        return f"Erreur lors de l'exécution de la requête : {e}"
