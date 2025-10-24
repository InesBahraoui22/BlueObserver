# Projet développement logiciel : BlueObserver

## Membres
Chloé MOMONT  
Ines BAHRAOUI 21901184  
Aly DAHOUD  
Oscar Bonnet  

## Nom du Projet
blue_observer

## Figure of interest & Narration

Notre figure d’intérêt principale est une **carte interactive touristique des océans**, combinant données de biodiversité marine (OBIS), conditions environnementales (Copernicus) et météo locale (Open-Meteo).  

L’objectif est de permettre aux utilisateurs — plongeurs, navigateurs, touristes ou passionnés de nature — de **découvrir quelles espèces marines sont observables selon la zone géographique, la saison et les conditions océaniques**.  

Chaque point sur la carte représente une observation d’espèce marine, avec :
- le **nom de l’espèce** (ex. *Delphinus delphis* — dauphin commun),  
- la **période d’observation**,  
- la **température et salinité** de l’eau à ce moment,  
- et un **lien d’information touristique** (spot de plongée, période recommandée, etc.).  

L’utilisateur pourra filtrer :
- une **espèce** ou un **groupe d’espèces** (ex.  dauphins, requin),  
- une **région** (ex. Méditerranée, Atlantique Nord),  
- une **période** (ex. été, hiver).  

Cette carte interactive sera accompagnée d’une légende intuitive et d’un design orienté “exploration” :
- dégradé de couleurs pour la température de surface,
- photos d’espèces ,
- info-bulles avec conseils touristiques.

---

### Exemple de scénario narratif

> Un utilisateur choisit “dauphin” et “été” sur la carte.  
> OceanAware lui montre les zones les plus favorables à son observation en mer, avec des températures entre 20 °C et 27 °C.  
> Il découvre que la Méditerranée orientale est particulièrement propice à cette période.  
> La carte devient ainsi un **outil de planification de voyage écologique et éducatif**.

---
### Idée générale
  
OceanAware rend la science accessible et utile aux voyageurs en valorisant :
- la **diversité marine** (OBIS),  
- la **qualité environnementale** (Copernicus),  
- et la **météo adaptée** aux activités marines (Open-Meteo).  

L’objectif est de **favoriser un tourisme responsable**, qui s’appuie sur la donnée ouverte pour encourager la découverte et la protection du milieu marin.

### Exemple de visuel attendu
 -menu déroulant pour le choix d'espèce
 -entrée utilisateur

### Logo du site
![Logo du projet](prototype_logo.jpg)

---

## Task managing
(un tableau avec les taches de chacun)
 - nettoyage de données
   - vérifier que les données temporelles sont cohérentes
   - quel est le format des données temporelles : limite temporelle 
   - matcher les coordonnées de la carte géographique : limite géographique
   - données manquantes/valeurs abérrantes/ enlever les colonnes manquantes
   - ajouter le nom vernaculaire (commun) des especes en anglais et francais
   - transformer les points en moyennes mensuelles pour les points (meteo/especes)
- programme de collaboration des données
- définitions des zones géographiques / délimiter les continents et récupération du fond de carte
- implémenatation (1semaine) mise en commun/ même environnement...
- création du site (4 jours) avec les onglets fonctionnels
- rédaction des textes explicatifs
- édition
- relecture

## Pipeline
 canva Aly




## Packages/software description for the project

numpy
pandas
scipy
matplotlib
seaborn
geopandas
shapely
folium
plotly
flask
jinja2
streamlit
dash


Le langage Python servira à traiter et analyser les données, car il est à la fois simple et efficace pour le travail scientifique. le Traitement des données qui sont aussi lourdes. Le code sera développé dans Visual Studio Code (VS Code).



Nous utilisons un environnement Python 3.10+ avec des packages spécifiques pour le traitement des données, l’analyse, et la création du site web interactif.
Pour la manipulation et l’analyse des données, nous nous appuyons sur :
numpy pour les calculs numériques et le traitement efficace des tableaux de données.
pandas pour la lecture des fichiers CSV, le nettoyage, le filtrage et l’agrégation des données.
scipy pour les analyses statistiques avancées.
matplotlib et seaborn pour visualiser les données sous forme de graphiques et de statistiques.
geopandas et shapely pour gérer les données géographiques et les manipulations de points ou polygones.
folium et plotly pour créer des cartes et visualisations interactives, intégrables au site.
Pour la création du site web, nous utilisons :
Flask et Jinja2 pour construire un site web léger avec des templates HTML.
Streamlit ou Dash pour créer un site interactif et des dashboards dynamiques.
Plotly et Folium pour rendre les graphiques et cartes interactifs directement dans le site.



## Dataset choices / Download / Description

### description des classes
