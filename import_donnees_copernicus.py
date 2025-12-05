###################################################################################################
###################### Importation des fichiers COPERNICUS par codage #############################
###################################################################################################

# ÉTAPE 1   | Importation des packages nécessaires aux téléchargements

"""
Comme le type des fichiers téléchargés et les organes qui contrôlent leur téléchargements sont
différents de ceux d'OBIS, on n'utilise pas les mêmes packages pour faire la récupération.
Ainsi, comme les satanées données copernicus sont des sortes d'images 3D (lon,lat,temps), je ne peux pas
directement les traduire en tableaux. En plus il ne ma faut pas le monde entier, seulement la
fenêtre géographique que j'ai sélectionné, donc il faut que :
1 - J'ouvre l'image
2 - j'extraie ma zone d'intérêt
3 - je convertie les dimensions en index temporel

Donc on utilise plus csv mais panda
D'ailleurs il fallait aussi encoder les paramètres dans une URL qu'on construisait pour faire les
requêtes à l'API. C'était parce qu'on récupérait un tableau JSON. Ici c'est un NetCDF (quel plaisir)
via la toolbox de Copernicus, donc on peut pas faire pareil :)))

donc tous les autres packages utilisés pour obis deviennent inutils ils servaient à construire l'URL
et appeler l'API.

# finalement, après dispute avec la documentation et défaite de ne pas pouvoir éviter de me servir de
# chatGPT, on utilse pathlib plutôt que os.path

Par contre, on utilise ce que conseille la docu du site
"""
import pprint
from pathlib import Path
import pandas as pd
import xarray as xr
import copernicusmarine as cm
import inspect
import os # Pour lire et écrire des fichiers

#________________________________________________________________________________________________


# ÉTAPE 2 | Définition des paramètres de filtration

LON_MIN, LON_MAX = -25.0, 45.0 # Ouest, Est
LAT_MIN, LAT_MAX = 27.0, 69.0 # Sud, Nord

polygone = (-25, 45, 27, 69) # Ouest, Est, Sud, Nord
# On change le format des dates pour coller à celui demandé par Copernicus, aka format ISO 8601
date_debut = "2000-01-01T00:00:00"
date_fin = "2025-01-01T00:00:00"

# Il va falloir faire une boucle qui me fabrique mes fichiers annuels, et donc les bornes de
# l'intervalle

annee_deb = 2001
annee_fin = 2025
annees = list(range(2000, 2025 + 1))

#_______________________________________________________________________________________________


# ÉTAPE 3 | Fabrication des dossiers où seront rangés les fichiers créés

doss_vagues = Path("vagues")
doss_vagues.mkdir(exist_ok = True) # Quand je fais tourner le programme, ça crée le dossier
                                   # n'existe pas déjà

doss_temp = Path("temp")
doss_temp.mkdir(exist_ok = True)

#__________________________________________________________________________________________


# ÉTAPE 4 | On récupère les adresses et les appelations qui nous intéressent

#  Inspection du fichier qui nous intéresse sur Copernicus concernant la TEMPÉRATURE :
catalogue_temp = cm.describe(product_id="GLOBAL_MULTIYEAR_PHY_ENS_001_031")
pprint.pprint(catalogue_temp)

# Inspection des datasets stockés dans ce catalogues et récupération de leurs id
for dataset in catalogue_temp.products[0].datasets:
    print(dataset.dataset_id)

# Récupération des noms des variables du premier dataset, celui qui nous intéresse
variables = catalogue_temp.products[0].datasets[0].versions[0].parts[0].services[0].variables
print(variables)

for variable in variables:
    print(f"Standard name : {variable.standard_name}")
    print(f"Shortname : {variable.short_name}")
    print(f"Unité : {variable.units}")
    print(" ")

"""
C-GLORS

Développé par le CMCC (Italie).
Assimilation d'observations via une technique variational/EnKF hybride.
Très bon sur circulation de surface et SST.

2️⃣ GLORYS2V4

Produit par Mercator Ocean International (France).
Très utilisé dans les atlas Copernicus.
Excellente représentation de la circulation de subsurface, des courants de bord ouest, et des structures fines en haute résolution.

3️⃣ ORAS5

Réanalyse océanique du ECMWF.
Très robuste pour les bilan thermiques, chaleur océanique, et la variabilité interannuelle.
Approche d'assimilation spécifique (NEMOVAR).
"""
#  Inspection du fichier qui nous intéresse sur Copernicus concernant les VAGUES :
catalogue_vagues = cm.describe(product_id="GLOBAL_MULTIYEAR_WAV_001_032")
pprint.pprint(catalogue_vagues)

# Inspection des datasets stockés dans ce catalogues et récupération de leurs id
for dataset in catalogue_vagues.products[0].datasets:
    print(dataset.dataset_id)

# Récupération des noms des variables du premier dataset, celui qui nous intéresse
variables = catalogue_vagues.products[0].datasets[0].versions[0].parts[0].services[0].variables
print(variables)

for variable in variables:
    print(f"Standard name : {variable.standard_name}")
    print(f"Shortname : {variable.short_name}")
    print(f"Unité : {variable.units}")
    print(" ")

donnees_temp = "cmems_mod_glo_phy-all_my_0.25deg_P1D-m" # identifiant du fichier pour temp,
                                                        # récupéré dans la premier tentative
                                                        # de récupération des données

donnees_vagues = "cmems_mod_glo_wav_my_0.2deg_PT3H-i" # idem mais pour waves, même si on
                                                      # abandonne le premier choix, puisque
                                                      # c'étaient des moyennes mensuelles,
                                                      # et j'ai besoin de plus précis


# copernicusmarine describe -c GLOBAL_MULTIYEAR_PHY_ENS_001_031

# copernicusmarine describe -c GLOBAL_MULTIYEAR_WAV_001_032

#print(ip.signature(cm.subset)) 


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

    produit_temp = cm.subset(dataset_id = donnees_temp,
                             variables = ["thetao_cglo"],
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


    # LES  VAGUES
    fichier_vagues = doss_vagues /f"vagues_{an}.nc"

    print(f"Téléchargement des données de l'an {2000} des vagues vers {fichier_vagues}")
    
    produit_vagues = cm.subset(dataset_id = donnees_vagues,
                             variables = ["VHM0"], # variable de surface
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
