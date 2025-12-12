Hello World 
==================

Hello, this is the BlueObserver documentation!
Welcome to the BlueObserver project. This documentation will guide you through the features and usage of BlueObserver. 
Here, you will find information on how to install, configure, and use BlueObserver effectively.

## Processus de création du fichier points.json
- Extraction des fichiers TSV
- Fusion avec le fichier Excel des espèces
- Nettoyage des coordonnées
- Ajout du mois depuis eventDate
- Association du nom commun
- Ajout du chemin de la photo
- Récupération des données météo
- Calcul des moyennes mensuelles
- Fusion des données observation + météo
- Sauvegarde automatique tous les 300 points
- Génération du fichier final points.json

## Processus de création des conditions limitantes ajoutées secondairement à points.json
- Extraction des fichiers NC
- Moyennage mensuel toutes années confondues en deux CSV
- Nettoyage des données

Code du projet
==============

Module main
-----------

.. automodule:: main
   :members:
   :undoc-members:
   :show-inheritance:

Module import_donnees_copernicus
--------------------------------

.. automodule:: import_donnees_copernicus
   :members:
   :undoc-members:

Module import_donnees_obis
--------------------------

.. automodule:: import_donnees_obis
   :members:
   :undoc-members:

Module exemple
--------------

.. automodule:: exemple
   :members:
   :undoc-members: