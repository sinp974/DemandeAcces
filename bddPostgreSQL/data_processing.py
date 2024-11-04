# Traitement des données

import subprocess
import bddPostgreSQL.data_storage as ds
import fonctionsUtiles as fu



def creation_demande(conn, dossier):

    # Variable permettant de gérer les erreurs
    etat = {}
    
    code, message = check_fichier_periGeo(dossier)
    etat[code] = message

    # Dictionnaire qui va contenir tous les attribus nécessaires à l'insertion d'une demande
    demande = {}

    demande['motif'] = fu.get_string_value(dossier, 'Q2hhbXAtMzg4MzA3Nw==')
    demande['date_validite_min'] = fu.get_string_value(dossier, 'Q2hhbXAtMzg4MzY1Ng==')
    demande['date_validite_max'] = fu.get_string_value(dossier, 'Q2hhbXAtMzg4MzY1OQ==')
    demande['motif_anonyme'] = fu.get_string_value(dossier, 'Q2hhbXAtMzg4MzExMw==')
    demande['date_demande'] = dossier['dateDepot'][:10]
    
    description = fu.get_string_value(dossier, 'Q2hhbXAtMzg4MzA3OQ==')
    demande['commentaire'] = (f'Description aménagements et impacts : {description}' if description != '' else '')
    
    remarque = fu.get_string_value(dossier, 'Q2hhbXAtMzg4NDcxOA==')
    demande['commentaire'] += (f' ; ' if remarque != '' and demande['commentaire'] != '' else '')
    demande['commentaire'] += (f'Remarque : {remarque}' if remarque != '' else '')

    demande['type_demande'] = getTypeDemande(conn, dossier)

    if demande['type_demande'] == 'AU' :
        typeDemandeAutre = fu.get_string_value(dossier, 'Q2hhbXAtMzg4MzA3Ng==')
        demande['commentaire'] += (f' ; ' if typeDemandeAutre != '' and demande['commentaire'] != '' else '')
        demande['commentaire'] += (f'Autre type de demande : {typeDemandeAutre}' if typeDemandeAutre != '' else '')

    demande['id_acteur'] = getIdActeur(conn, dossier)

    demande['id_organisme'] = getIdOrganisme(conn, dossier)

    dossier, demande['libelle_geom'] = getLibelleGeom(dossier)

    demande = getCritereAdditionnel(conn, dossier, demande)

    # En cas d'erreur, on ne procède à aucune insertion en bdd
    # et on retourne l'etat du dossier (i.e. la liste des erreurs) pour demande de correction(s)
    print(etat)
    if 1 in etat:
        fu.cleanup()
        return etat, dossier
    
    # Si tout va bien, insérer la demande en bdd et récupérer l'id
    id_demande = ds.insert_demande(conn, demande)
    dossier.id_demande = id_demande

    # Dans le cas où il n'y a pas de périmètre géographique défini,
    # le traitement est terminé
    if 'geom' in dossier:
        fu.cleanup()
        return etat, dossier

    # Sinon, il faut traiter la géométrie :
    # 1 - Importer la géométrie dans la table fdw.geom_demande
    ds.import_shp_to_postgres(conn, dossier)

    # 2 - Insérer la ou les geom à la demande
    ds.update_geom_in_demande(conn, dossier)

    fu.cleanup()
    return etat, dossier






def getTypeDemande(conn, dossier):
    """
    Récupérer le code associé au type de demande

    Args:
        dossier (pandas.core.series.Series) : Objet contenant toutes les informations d'un dossier, récupéré de l'API GraphQL de Démarches Simplifiées
        conn (psycopg2.extensions.connection): Objet de connexion à la base de données

    Returns:
        str: attribut type_demande de la demarche à ajouter
    """

    valeur = fu.get_string_value(dossier, 'Q2hhbXAtMzg4MzA3Ng==')

    type_demande = ds.fetch_code_by_value_type_demande(conn, valeur)

    return type_demande




def getIdActeur(conn, dossier):
    """
    Récupérer l'id_acteur associé à (civilite, nom, prenom)

    Args:
        dossier (_type_): _description_
        conn (_type_): _description_

    Returns:
        _type_: _description_
    """
    civilite = dossier['demandeur_civilite']
    nom = dossier['demandeur_nom']
    prenom = dossier['demandeur_prenom']
    courriel = fu.get_string_value(dossier, 'Q2hhbXAtMzg4MzU1MQ==') 

    id_acteur = ds.search_id_acteur(conn, civilite, nom, prenom, courriel)

    return id_acteur



def getIdOrganisme(conn, dossier):
    nom_structure = fu.get_string_value(dossier, 'Q2hhbXAtMzg4MzM2Mg==')

    id_organisme = ds.search_id_organisme(conn, nom_structure)

    return id_organisme



def getLibelleGeom(dossier):
    periGeo = fu.get_string_value(dossier, 'Q2hhbXAtNDYxNTU5Mw==')

    if periGeo == False:
        dossier.geom = None
        libelle_geom = 'Justification pas de périmètre géographique :' + fu.get_string_value(dossier, 'Q2hhbXAtNDYxNTYwOA==')
    
    else:
        descriptionGeom = fu.get_string_value(dossier, 'Q2hhbXAtMzg4Mzk1Nw==')

        if fu.get_string_value(dossier, 'Q2hhbXAtMzg4Mzk2Mg==') == True:
            rayon = fu.get_string_value(dossier, 'Q2hhbXAtMzg4Mzk2Mw==')
            tampon = f' - intégrant un tampon de {rayon} m de rayon'
            dossier.rayon_ajouter = 0
        else:
            rayon = fu.get_string_value(dossier, 'Q2hhbXAtMzg4Mzk2NA==')
            tampon = f" - avec l'ajout d'un tampon de {rayon} m de rayon"
            dossier.rayon_ajouter = rayon

        libelle_geom = descriptionGeom + tampon

    return dossier, libelle_geom





def getCritereAdditionnel(conn, dossier, demande):

    periTaxo = fu.get_string_value(dossier, 'Q2hhbXAtNDYxNTU4Ng==')

    # Si il n'y a pas de périmètre taxonomique défini,
    # Alors critere_additionnel prend la valeur null par défaut à l'insertion (il n'y a rien à faire)
    if periTaxo != 'Toutes les espèces':

        # Ajouter la remarque sur le périmètre taxonomique (s'il y en a un) au commentaire de la demande
        libelle_taxo = fu.get_string_value(dossier, 'Q2hhbXAtMzg4Mzg2OQ==')
        demande['commentaire'] += (f' ; ' if libelle_taxo != '' and demande['commentaire'] != '' else '')
        demande['commentaire'] += (f'Informations supplémentaire sur le périmètre taxonomique  : {libelle_taxo}' if libelle_taxo != '' else '')

        if periTaxo == 'Seulement un ou plusieurs groupes taxonomiques':
            values = fu.get_string_value(dossier, 'Q2hhbXAtMzg4MzY2MQ==')
            values_sql = ", ".join([f"'{valeur}'" for valeur in values])
            critere_additionnel = f'group1_inpn IN ({values_sql}) OR group2_inpn IN ({values_sql})'
        
        elif periTaxo == 'Seulement une ou plusieurs espèces':

            typeTransmission = fu.get_string_value(dossier, 'Q2hhbXAtNDYxNTU4OA==')
            if typeTransmission == 'Saisir une liste' :

                critere_additionnel = 0
            else :

                critere_additionnel = 0

            # cd_ref IN (784115, 695969, -12, 458690, 442280, 215079, 418806, 773944, 728081, 418762)
            # msg d'erreur liés au fichier déposé à gérer ici aussi
            # On leur demande de renseigner les cd_nom :
            # Vérifier que le cd_nom et existe bien sinon erreur
    

        demande['critere_additionnel'] = critere_additionnel

    return demande





def check_fichier_periGeo(dossier):

    periGeo = fu.get_string_value(dossier, 'Q2hhbXAtNDYxNTU5Mw==')

    if periGeo == True:

        files = fu.get_string_value(dossier, 'Q2hhbXAtMzg4Mzk1OA==')

        if len(files) != 1:
            return 1, "Vous avez fourni plusieurs fichiers pour définir le périmètre géographique. Merci de ne fournir qu'un seul fichier pour spécifier le périmètre géographique." ## retourne une erreur

        filename = files[0]["filename"]

        # Vérifie l'extension du fichier
        if not filename.endswith('.zip'):
            return 1, "Le fichier fourni pour le périmètre géographique n'est pas au format .zip." ## retourne une erreur
    
        url = files[0]["url"]
        downloadzipfile = fu.download_zip_file(url, 'fdw_geom_demande/'+filename)

        if downloadzipfile == 1:
            return 1, "Nous ne parvenons pas à télécharger le fichier fourni pour le périmètre géographique. Merci d'en déposer un nouveau, en supprimant l'ancien."

        fu.unzip_file('fdw_geom_demande/'+filename, 'fdw_geom_demande/')

        # Si tout va bien, retourner 0 avec le nom du fichier shapefile à importer
        # Sinon, retourner 1 avec un message d'erreur
        findShpFile = fu.find_shp_file()
        if findShpFile[0] == 1:
            return findShpFile
        else:
            dossier.shpFile = findShpFile[1]
            return 0, "Le fichier de périmètre géographique fourni est valide."

    else:
        # Cas où il n'y a pas de périmètre géographique défini
        return 0, "Pas de périmètre géographique défini"


