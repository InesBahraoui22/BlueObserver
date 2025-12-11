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

#       VAGUES

#  Inspection du fichier qui nous intéresse sur Copernicus concernant les VAGUES :
produit_id_vagues = recuperer_product_id_vagues()
catalogue_vagues = cm.describe(product_id = produit_id_vagues)
#pprint.pprint(catalogue_vagues)

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

dataset_ids = []

for product in catalogue_vagues.products:

    for dataset in product.datasets:
        dataset_ids.append(dataset.dataset_id)

for ds in dataset_ids:
    print(ds)

#       TEMPÉRATURE

#  Inspection du fichier qui nous intéresse sur Copernicus concernant la TEMPÉRATURE :
produit_id_temp = recuperer_product_id_temp()
catalogue_temp = cm.describe(product_id = produit_id_temp)
#pprint.pprint(catalogue_temp)
print("Produit choisi :", produit_id_temp)


# Inspection des datasets stockés dans ce catalogues et récupération de leurs id
for dataset in catalogue_temp.products[0].datasets:
    print(dataset.dataset_id)

# Récupération des noms des variables du premier dataset, celui qui nous intéresse
variables = catalogue_temp.products[0].datasets[0].versions[0].parts[0].services[0].variables
# print(variables)

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


donnees_temp = "cmems_mod_glo_phy-all_my_0.25deg_P1D-m" # identifiant du fichier pour temp,
                                                        # récupéré dans la premier tentative
                                                        # de récupération des données

donnees_vagues = "cmems_mod_glo_wav_my_0.2deg_PT3H-i" # idem mais pour waves, même si on
                                                      # abandonne le premier choix, puisque
                                                      # c'étaient des moyennes mensuelles,
                                                      # et j'ai besoin de plus précis