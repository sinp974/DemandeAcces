# Fonctions d'intéraction avec la bdd PostgreSQL

import geopandas as gpd
import pandas as pd




def fetch_code_by_value_type_demande(conn, valeur):
    """
    Récupérer le code associé à une valeur donnée dans la table g_nomenclature.

    Args:
        conn (psycopg2.extensions.connection): Objet de connexion à la base de données
        valeur (str): valeur choisie

    Returns:
        str: code associé à la valeur fournie
    """
    # Récupère le code associé à une valeur donnée dans la table g_nomenclature.
    with conn.cursor() as cursor:
        query = """
            SELECT code 
            FROM gestion.g_nomenclature
            WHERE champ = 'type_demande' AND description = %s
        """
        cursor.execute(query, (valeur,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 'AU'






def search_id_acteur(conn, civilite, nom, prenom, courriel):
    """
    Rechercher l'ID d'un acteur dans la base de données en fonction de sa civilité, nom, prénom et email.

    Args:
        civilite (str): La civilité de l'acteur.
        nom (str): Le nom de l'acteur.
        prenom (str): Le prénom de l'acteur.
        conn: La connexion à la base de données.

    Returns:
        int or None: L'ID de l'acteur s'il est trouvé, sinon -1 (non défini / inconnu)
    """

    with conn.cursor() as cursor:
        # Exécution de la requête SQL avec ILIKE pour les correspondances insensibles à la casse
        cursor.execute("""
            SELECT id_acteur
            FROM gestion.acteur
            WHERE (civilite ILIKE %s
            AND nom ILIKE %s
            AND prenom ILIKE %s) OR courriel ILIKE %s
        """, (f"%{civilite}%", f"%{nom}%", f"%{prenom}%", f"%{courriel}%"))
        
        # Récupérer le premier résultat s'il existe
        result = cursor.fetchone()
        return result[0] if result else -1






def search_id_organisme(conn, nom_structure):
    """
    Rechercher l'ID d'un organisme dans la base de données en fonction du nom de la structure

    Args:
        nom_structure (str): Le nom de la strcuture

        conn: La connexion à la base de données.

    Returns:
        int or None: L'ID de l'organisme s'il est trouvé, sinon -1 (non défini / inconnu)
    """

    with conn.cursor() as cursor:
        # Exécution de la requête SQL avec ILIKE pour les correspondances insensibles à la casse
        cursor.execute("""
            SELECT id_organisme
            FROM occtax.organisme
            WHERE nom_organisme ILIKE %s
            OR sigle ILIKE %s
        """, (f"%{nom_structure}%", f"%{nom_structure}%"))
        
        # Récupérer le premier résultat s'il existe
        result = cursor.fetchone()
        return result[0] if result else -1
















def insert_demande(conn, demande):
    """
    Insérer la nouvelle demande dans la table 'demande' du schéma 'gestion',
    Et récupérer l'id de la demande créée, qui sera utilisé pour l'étape suivante de définition d'un périmètre géographique

    Args:
        demande (dict) : Dictionnaire contenant tous les attributs d'une demande
        conn (psycopg2.extensions.connection): Objet de connexion à la base de données

    Returns:
        int: Id de la demande créée
    """
    # Extraction des valeurs depuis le dictionnaire demande
    motif = demande.get('motif')
    date_validite_min = demande.get('date_validite_min')
    date_validite_max = demande.get('date_validite_max')
    motif_anonyme = demande.get('motif_anonyme')
    date_demande = demande.get('date_demande')
    commentaire = demande.get('commentaire')
    type_demande = demande.get('type_demande')
    id_acteur = demande.get('id_acteur')
    id_organisme = demande.get('id_organisme')
    libelle_geom = demande.get('libelle_geom')
    critere_additionnel = demande.get('critere_additionnel')

    # Insérer la nouvelle demande dans la table avec une requête SQL paramétrée
    with conn.cursor() as cursor:
        cursor.execute('''
            INSERT INTO gestion.demande 
            (motif, date_validite_min, date_validite_max, motif_anonyme, date_demande, commentaire, 
             type_demande, id_acteur, id_organisme, libelle_geom, critere_additionnel)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (motif, date_validite_min, date_validite_max, motif_anonyme, date_demande, commentaire, 
              type_demande, id_acteur, id_organisme, libelle_geom, critere_additionnel))

        # Récupérer l'id de la nouvelle demande créée
        new_id = cursor.fetchone()[0]
        conn.commit()
    return new_id






def import_shp_to_postgres(conn, dossier):
    # Lire le fichier shapefile
    shapefile_path = dossier.shpFile  # chemin d'accès au shapefile
    gdf = gpd.read_file(shapefile_path)
    
    # Ajouter la colonne id_demande avec la valeur de dossier.id_demande
    gdf['id_demande'] = dossier.id_demande
    
    # Connexion à la base de données
    with conn.cursor() as cursor:
        # Itérer sur chaque ligne de GeoDataFrame et insérer dans la table geom_demande
        for index, row in gdf.iterrows():
            # Préparer la requête d'insertion
            query = """
            INSERT INTO fdw.geom_demande (id_demande, geom)
            VALUES (%s, ST_SetSRID(ST_GeomFromText(%s), 2975))
            """
            # Extraire les valeurs à insérer
            geom_wkt = row['geometry'].wkt  # Convertir la géométrie en WKT
            id_demande_value = row['id_demande']
            
            # Exécuter la requête d'insertion
            cursor.execute(query, (id_demande_value, geom_wkt))
        
        # Valider les modifications
        conn.commit()
        print(f"{len(gdf)} enregistrements insérés dans la table geom_demande.")





def update_geom_in_demande(conn, dossier):

    # Créer la requête pour effectuer l'union des géométries tamponnées et mettre à jour gestion.demande
    query = """
    UPDATE gestion.demande
    SET geom = (
        SELECT ST_Multi(ST_Union(ST_Buffer(geom, %s)))
        FROM fdw.geom_demande
        WHERE id_demande = %s
    )
    WHERE id = %s;
    """

    # Exécuter la requête avec les valeurs appropriées
    with conn.cursor() as cursor:
        cursor.execute(query, (dossier.rayon_ajouter, dossier.id_demande, dossier.id_demande))
    
    conn.commit()
    print("La géométrie de la demande a été mise à jour avec succès.")




