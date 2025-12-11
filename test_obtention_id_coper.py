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
from recup_id_donnees_marines import recuperer_product_id_temp
from recup_id_donnees_marines import recuperer_product_id_vagues
from recup_id_donnees_marines import choisir_dataset_id
from recup_id_donnees_marines import choisir_id_dataset_sachant_par_defaut
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

MAPPING_DATASETS_PAR_DEFAUT = {
    "GLOBAL_MULTIYEAR_PHY_ENS_001_031": "cmems_mod_glo_phy-all_my_0.25deg_P1D-m",
    "GLOBAL_MULTIYEAR_WAV_001_032": "cmems_mod_glo_wav_my_0.2deg_PT3H-i",
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