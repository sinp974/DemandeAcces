# Connexion à PostgreSQL


import psycopg2
from psycopg2 import sql



def connect_to_database(db_config):
    """
    Fonction permettant de se connecter à une base de données PostgreSQL en utilisant les paramètres de configuration fournis.

    Args:
        db_config (dict): Dictionnaire contenant les paramètres de connexion à la base de données. 
                          Les clés attendues incluent :
                          - 'dbname' (str) : Nom de la base de données
                          - 'user' (str) : Nom d'utilisateur pour la connexion
                          - 'password' (str) : Mot de passe de l'utilisateur
                          - 'host' (str) : Adresse du serveur de la base de données
                          - 'port' (int, optionnel) : Port d'accès à la base de données (par défaut, 5432 pour PostgreSQL)

    Returns:
        psycopg2.extensions.connection: Objet de connexion à la base de données si la connexion est réussie.
        None: Retourne None en cas d'échec de la connexion, avec une erreur imprimée dans la console.

    Raises:
        Exception: Capture toute exception liée à la connexion à la base de données et l'affiche dans la console.
    """
    
    try:
        conn = psycopg2.connect(**db_config)
        print("Connexion réussie à la base de données")
        return conn
    except Exception as e:
        print(f"Erreur lors de la connexion à la base de données : {e}")
        return None





