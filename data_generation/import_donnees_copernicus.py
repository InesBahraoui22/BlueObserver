###################################################################################################
###################### Importation des fichiers COPERNICUS par codage #############################
###################################################################################################


"""
PRÉAMBULE
Comme le type des fichiers téléchargés et les organes qui contrôlent leur téléchargements sont
différents de ceux d'OBIS, on n'utilise pas les mêmes packages pour faire la récupération.
Ainsi, comme les satanées données copernicus sont des sortes d'images 3D (lon,lat,temps), je ne peux pas
directement les traduire en tableaux. En plus il ne me faut pas le monde entier, seulement la
fenêtre géographique que nous avons pré-définie, donc il faut que :
1 - J'ouvre l'image
2 - j'extraie ma zone d'intérêt
3 - je convertie les dimensions en index temporel

Donc on utilise plus csv mais panda
D'ailleurs il fallait aussi encoder les paramètres dans une URL qu'on construisait pour faire les
requêtes à l'API. C'était parce qu'on récupérait un tableau JSON. Ici c'est un NetCDF (quel plaisir)
via la toolbox de Copernicus, donc on peut pas faire pareil :)))

donc tous les autres packages utilisés pour Obis deviennent inutiles puisqu'ils servaient à construire
l'URL et appeler l'API.

# Finalement, après dispute avec la documentation et défaite de ne pas pouvoir éviter de me servir de
# chatGPT, on utilse pathlib plutôt que os.path

Par contre, on utilise ce que conseille la docu du site, parce que chatGPT est complètement inutile.
"""

# ÉTAPE 1   | Importation des packages nécessaires aux téléchargements

import pprint
from pathlib import Path
import pandas as pd
import xarray as xr
import copernicusmarine as cm
import inspect
import os # Pour lire et écrire des fichiers
from fonctions_import_copernicus import recuperer_product_id_temp
from fonctions_import_copernicus import recuperer_product_id_vagues
from fonctions_import_copernicus import choisir_dataset_id
from fonctions_import_copernicus import choisir_id_dataset_sachant_par_defaut
from datetime import datetime

#________________________________________________________________________________________________


# ÉTAPE 2 | Définition des paramètres de filtration

LON_MIN, LON_MAX = -25.0, 45.0 # Ouest, Est
LAT_MIN, LAT_MAX = 27.0, 69.0 # Sud, Nord

polygone = (-25, 45, 27, 69) # Ouest, Est, Sud, Nord

annee_deb = 2000

annee_fin = 2025
annees = list(range(annee_deb, annee_fin + 1))
print(annees)
#_______________________________________________________________________________________________


# ÉTAPE 3 | Fabrication des dossiers où seront rangés les fichiers créés

doss_vagues = Path("vagues")
doss_vagues.mkdir(exist_ok = True) # Quand je fais tourner le programme, ça crée le dossier
                                   # n'existe pas déjà

doss_temp = Path("temp")
doss_temp.mkdir(exist_ok = True)

#__________________________________________________________________________________________


# ÉTAPE 4 | On récupère les adresses et les appelations qui nous intéressent

# Dico des outils et ressources par défaut
MAPPING_DATASETS_PAR_DEFAUT = {
    "GLOBAL_MULTIYEAR_PHY_ENS_001_031": "cmems_mod_glo_phy-all_my_0.25deg_P1D-m",
    "GLOBAL_MULTIYEAR_WAV_001_032": "cmems_mod_glo_wav_my_0.2deg_PT3H-i",
}

MAPPING_VARS_DEFAUT = {
    "cmems_mod_glo_phy-all_my_0.25deg_P1D-m": "thetao_cglo",  # adapte si besoin
    "cmems_mod_glo_wav_my_0.2deg_PT3H-i": "VHM0",
}

#       VAGUES :
produit_id_vagues = recuperer_product_id_vagues()
catalogue_vagues = cm.describe(product_id = produit_id_vagues)

#       TEMPÉRATURE :
produit_id_temp = recuperer_product_id_temp()
catalogue_temp = cm.describe(product_id = produit_id_temp)
print("Produit choisi :", produit_id_temp)


donnees_temp = choisir_id_dataset_sachant_par_defaut(
    catalogue = catalogue_temp,
    product_id = produit_id_temp,
    mapping_defaut = MAPPING_DATASETS_PAR_DEFAUT)
print(f"Le dataset utilisé pour obtenir des données sur la température de la mer est '{donnees_temp}'.")

donnees_vagues = choisir_id_dataset_sachant_par_defaut(
    catalogue = catalogue_vagues,
    product_id = produit_id_vagues,
    mapping_defaut = MAPPING_DATASETS_PAR_DEFAUT)
print(f"Le dataset utilisé pour obtenir des données sur les vagues est '{donnees_vagues}'.")

variable_temp, unite_temp = choisir_variable_dans_dataset(
    catalogue = catalogue_temp,
    dataset_id = donnees_temp,
    type_variable = "temp",
    mapping_vars_par_defaut = MAPPING_VARS_DEFAUT)
print(f"La variable utilisée pour connaître la température est '{variable_temp}'."
      f"\n Elle est exprimée en {unite_temp}.")


variable_vagues, unite_vagues = choisir_variable_dans_dataset(
    catalogue = catalogue_vagues,
    dataset_id = donnees_vagues,
    type_variable = "vagues",
    mapping_vars_par_defaut = MAPPING_VARS_DEFAUT)
print("La variable utilisée pour connaître la hauteur des vagues"
      f"\n est '{variable_vagues}'.Elle est exprimée en {unite_vagues}.")


#__________________________________________________________________________________________


# ÉTAPE 5 | BOUCLE

for an in annees :

    deb = f"{an}-01-01T00:00:00" # f-string = f juste devant les guillements et entre {} 
                                 # c'est du Python 
    fin = f"{an+1}-01-01T00:00:00"

    # LA TEMPÉRATURE 
    fichier_temp = doss_temp / f"temp_{an}.nc" # On crée le fichier vide et on le place dans
                                               # sa destination. (Le format n'est pas encore 
                                               # celui que je veux.)

    print(f"Température : téléchargement vers {fichier_temp}")
    print(f"\nVariable choisie : {variable_temp} ({unite_temp})")

    produit_temp = cm.subset(dataset_id = donnees_temp,
                             variables = [variable_temp],
                             minimum_latitude = LAT_MIN,
                             maximum_latitude = LAT_MAX,
                             minimum_longitude = LON_MIN,
                             maximum_longitude = LON_MAX,
                             minimum_depth = 0.0,
                             maximum_depth = 25.0, # ça sert à rien de prendre très profond,
                                                   # on va garder une profondeur de baignade
                                                   # cohérente.
                             start_datetime = deb,
                             end_datetime = fin,
                             output_directory = doss_temp,
                             output_filename = fichier_temp.name,
                             )
    
    print(f"Téléchargement du fichier {an} (réponse : {produit_temp.status})")
    print(" ")

    # LES  VAGUES
    fichier_vagues = doss_vagues /f"vagues_{an}.nc"

    print(f"Téléchargement des données de l'an {2000} des vagues vers {fichier_vagues}")
    
    produit_vagues = cm.subset(dataset_id = donnees_vagues,
                             variables = [variable_vagues],
                             minimum_latitude = LAT_MIN,
                             maximum_latitude = LAT_MAX,
                             minimum_longitude = LON_MIN,
                             maximum_longitude = LON_MAX,
                             start_datetime = deb,
                             end_datetime = fin,
                             output_directory = doss_vagues,
                             output_filename = fichier_vagues.name,
                             

    )
                             
    print(f"Téléchargement du fichier {an} (réponse : {produit_vagues.status})")
    print(" ")

"""
(dataset_id: Optional[str] = None,
dataset_version: Optional[str] = None, 
dataset_part: Optional[str] = None,
username: Optional[str] = None,
password: Optional[str] = None,
variables: Optional[List[str]] = None,
minimum_longitude: Optional[float] = None, 
maximum_longitude: Optional[float] = None, 
minimum_latitude: Optional[float] = None, 
maximum_latitude: Optional[float] = None, 
minimum_depth: Optional[float] = None,
maximum_depth: Optional[float] = None, 
vertical_axis: Literal['depth', 'elevation'] = 'depth',
start_datetime: Union[datetime.datetime, pandas._libs.tslibs.timestamps.Timestamp, str, NoneType] = None,
end_datetime: Union[datetime.datetime, pandas._libs.tslibs.timestamps.Timestamp, str, NoneType] = None,
minimum_x: Optional[float] = None,
maximum_x: Optional[float] = None,
minimum_y: Optional[float] = None,
maximum_y: Optional[float] = None,
coordinates_selection_method: Literal['inside', 'strict-inside', 'nearest', 'outside'] = 'inside',
output_filename: Optional[str] = None,
file_format: Optional[Literal['netcdf', 'zarr', 'csv', 'parquet']] = None,
service: Optional[str] = None,
request_file: Union[pathlib.Path, str, NoneType] = None,
output_directory: Union[pathlib.Path, str, NoneType] = None,
credentials_file: Union[pathlib.Path, str, NoneType] = None,
motu_api_request: Optional[str] = None, overwrite: bool = False,
skip_existing: bool = False,
dry_run: bool = False,
disable_progress_bar: bool = False,
staging: bool = False,
netcdf_compression_level: int = 0,
netcdf3_compatible: bool = False,
chunk_size_limit: int = -1, 
raise_if_updating: bool = False, 
platform_ids: Optional[List[str]] = None) -> copernicusmarine.core_functions.models.ResponseSubset
"""
