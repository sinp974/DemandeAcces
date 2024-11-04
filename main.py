# Point d'entrée de l'application
# Contient toute la logique de traitement des demandes d'accès
# Fichier à appeler avec une récurrence à définir


# chaine de traitement à mettre en place ici


import datetime
import APIGraphQLDS.graphql_client as gc
import APIGraphQLDS.graphql_queries as gq
import bddPostgreSQL.database as d
import bddPostgreSQL.data_processing as dp
import bddPostgreSQL.data_storage as ds
import fonctionsUtiles as fu






def getDfDossiersFromDS(date, fileConfigAPI):

    # Charger la configuration de l'API de DS
    config = fu.load_config(fileConfigAPI)

    # Créer le client GraphQL
    client = gc.create_graphql_client(config['api_url'], config['api_key'], config['proxies'])

    # Exécuter la requête
    df_dossiers = gq.getDossiersUpdatedSince(client, config['id_Demarche'], date)
    
    return df_dossiers



def getConnFromBdd(fileConfigBDD):
    
    # Charger la configuration de la BDD de Borbonica
    db_config = fu.load_config(fileConfigBDD)
        
    # Connexion à la base de données
    conn = d.connect_to_database(db_config)

    return conn


# Demande de correction générique à faire :
## \n\nPour rappel, vous ne devez fournir qu'un seul dossier, au format .zip contenant un projet qgis avec un fichier shape.



if __name__ == "__main__":

    # Variables
    fileConfigBDD = 'configBDD.json'
    fileConfigAPI = 'configAPI.json'

    
    # date = (datetime.datetime.today() - datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    date = datetime.datetime(2024, 10, 28).isoformat()

    
    df_dossiers =  getDfDossiersFromDS(date, fileConfigAPI)

    fu.save_df_to_json(df_dossiers, date[:10])
    
    dossier = df_dossiers.iloc[1]

    conn = getConnFromBdd(fileConfigBDD)

    dossier = dp.creation_demande(conn, dossier)



