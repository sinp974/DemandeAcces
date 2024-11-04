import json
import os
import shutil
import requests
import zipfile



def load_config(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)



def saveJSON_Dossier(responseJSON, dossierNumber):
    with open(f'results/dossier_{dossierNumber}.json', 'w', encoding='utf-8') as f:
        json.dump(responseJSON, f, ensure_ascii=False, indent=4)
    return "La réponse a bien été enregistrée dans le fichier dossier_"+str(dossierNumber)+".json."



def save_df_to_json(df, date):
    """
    Enregistre le DataFrame df au format JSON.

    Args:
        df_dossiers (pd.DataFrame): DataFrame contenant les dossiers à enregistrer
        date (str): Date à spécificier dans le nom du fichier JSON dans lequel les données seront sauvegardées
    """
    try:
        # Convertir le DataFrame en dictionnaire puis en JSON
        dossiers_dict = df.to_dict(orient='records')
        file_name = "results/dossiers_"+date+".json"
        with open(file_name, 'w', encoding='utf-8') as json_file:
            json.dump(dossiers_dict, json_file, ensure_ascii=False, indent=4)
        print(f"Données sauvegardées avec succès dans {file_name}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des données en JSON : {e}")



def get_string_value(dossier, champDescriptorId):
    for champ in dossier['champs']:
        if champ['champDescriptorId'] == champDescriptorId:

            if champ['__typename'] == 'CheckboxChamp':
                return champ.get('checked')
            
            if champ['__typename'] == 'IntegerNumberChamp':
                return champ.get('integerNumber')
            
            if champ['__typename'] == 'DateChamp':
                return champ.get('date')
            
            if champ['__typename'] == 'MultipleDropDownListChamp':
                return champ.get('values')
            
            if champ['__typename'] == 'PieceJustificativeChamp':
                return champ.get('files')
            
            else:
                return champ.get('stringValue')

    # Lever une exception si aucune correspondance n'est trouvée
    raise ValueError(f"Pas de champs trouvé pour le champDescriptorId suivant: {champDescriptorId}")




def download_zip_file(url, filename):
    print(f"Téléchargement du fichier {filename} depuis {url}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Fichier {filename} téléchargé avec succès.")
        return 0
    else:
        print(f"Erreur lors du téléchargement du fichier : {response.status_code}")
        exit()
        return 1



def unzip_file(zip_file, extract_to):
    print(f"Décompression du fichier {zip_file} dans le répertoire {extract_to}...")
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Décompression terminée.")



def find_shp_file():
    print(f"Recherche de fichiers SHP dans le répertoire fdw_geom_demande/ ...")
    for root, dirs, files in os.walk('fdw_geom_demande/'):
        for file in files:
            if file.endswith(".shp"):
                shp_path = os.path.join(root, file)
                print(f"Fichier SHP trouvé : {shp_path}")
                return 0, shp_path
    print("Aucun fichier shapefile n'a été trouvé dans le dossier zip.")
    return 1, "Aucun fichier shapefile n'a été trouvé dans le dossier zip."




def cleanup():
    """
        Nettoyer le répertoire fdw_geom_demande/ qui contient les fichiers temporaires permettant de définir le périmètre géographique d'une demande
    """
    # Parcours tous les éléments dans le répertoire
    for item in os.listdir('fdw_geom_demande/'):
        item_path = os.path.join('fdw_geom_demande/', item)
        
        # Supprime chaque fichier ou répertoire trouvé
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)
    print("Nettoyage terminé.")































def notifier_erreur(message):
    # Fonction fictive d'envoi d'un e-mail
    print("Envoi d'une notification d'erreur : ", message)