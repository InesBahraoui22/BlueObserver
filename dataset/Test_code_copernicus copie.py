###################################################################################################
###################### Importation des fichiers COPERNICUS par codage #############################
###################################################################################################

# ÉTAPE 1   | Importation des packages nécessaires aux téléchargements

import os # Pour lire et écrire des fichiers

# Comme le type des fichiers téléchargés et les organes qui contrôlent leur téléchargements sont
# différents de ceux d'OBIS, on n'utilise pas les mêmes packages pour faire la récupération.
# Ainsi, comme les satanées données copernicus sont des sortes d'images 3D (lon,lat,temps), je ne peux pas
# directement les traduire en tableaux. En plus il ne ma faut pas le monde entier, seulement la
# fenêtre géographique que j'ai sélectionné, donc il faut que :
# 1 - J'ouvre l'image
# 2 - j'extraie ma zone d'intérêt
# 3 - je convertie les dimensions en index temporel

# Donc on utilise plus csv mais panda
# D'ailleurs il fallait aussi encoder les paramètres dans une URL qu'on construisait pour faire les
# requêtes à l'API. C'était parce qu'on récupérait un tableau JSON. Ici c'est un NetCDF (quel plaisir)
# via la toolbox de Copernicus, donc on peut pas faire pareil :)))

# donc tous les autres packages utilisés pour obis deviennent inutils ils servaient à construire l'URL
# et appeler l'API.





