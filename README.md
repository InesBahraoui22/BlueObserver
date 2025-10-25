# Projet développement logiciel : BlueObserver

## Membres
Chloé MONMONT 22513053                        
Ines BAHRAOUI 21901184     
Aly DAHOUD    
Oscar BONNET  



## Nom du Projet
Blue_Observer

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

<img width="2215" height="1256" alt="image" src="https://github.com/user-attachments/assets/3c319a23-5008-47a3-a43e-fcace7c18854" />


<img width="2208" height="1252" alt="image" src="https://github.com/user-attachments/assets/17957a88-38bb-43c7-8645-d2de015a5dad" />


<img width="2208" height="1252" alt="image" src="https://github.com/user-attachments/assets/42ef5783-4bad-49fc-9243-c6f8a09745cc" />

<img width="2204" height="1252" alt="image" src="https://github.com/user-attachments/assets/7066eca4-f904-4492-baf5-d4edbc3be18f" />
 -menu déroulant pour le choix d'espèce
 -entrée utilisateur

#### Maquette du site

Suivre le lien ci-dessous :
https://www.canva.com/design/DAG20mu9XhQ/tUndsWOyFw9X-NQNDNyi1w/edit?ui=e30

### Logo du site
![Logo du projet](prototype_logo.jpg)

---

## Task managing

(un tableau avec les tâches de chacun)

 - Nettoyage de données
   - Vérifier que les données temporelles sont cohérentes
   - Quel est le format des données temporelles : limite temporelle 
   - Matcher les coordonnées de la carte géographique : limite géographique
   - Données manquantes/valeurs abérrantes/ enlever les colonnes manquantes
   - Ajouter le nom vernaculaire (commun) des especes en anglais et francais
   - Transformer les points en moyennes mensuelles pour les points (meteo/especes)
- Programme de collaboration des données
- Définitions des zones géographiques / délimiter les continents et récupération du fond de carte
- Implémenatation (1semaine) mise en commun/ même environnement...
- Création du site (4 jours) avec les onglets fonctionnels
- Rédaction des textes explicatifs
- Édition
- Relecture

## Pipeline

Lien vers : https://www.canva.com/design/DAG2r11zahc/DXjEfuwUDvOmZ7Sz-p8m5Q/edit?utm_content=DAG2r11zahc&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton

## Packages/software description for the project

Le langage **Python** servira à traiter et analyser les données, car il est à la fois simple et efficace pour le travail scientifique, y compris pour des **données lourdes**.  
Le code sera développé dans **Visual Studio Code (VS Code)**.

Nous utilisons un environnement **Python 3.10+** avec des packages spécifiques pour le traitement des données, l’analyse, et la création du site web interactif.

### Manipulation et analyse des données

- **numpy** : calculs numériques et traitement efficace des tableaux de données  
- **pandas** : lecture des fichiers CSV, nettoyage, filtrage et agrégation des données  
- **scipy** : analyses statistiques avancées  
- **matplotlib** et **seaborn** : visualisation des données sous forme de graphiques et statistiques  
- **geopandas** et **shapely** : gestion des données géographiques et manipulations de points ou polygones  
- **folium** et **plotly** : création de cartes et visualisations interactives, intégrables au site

### Création du site web

- **Flask** et **Jinja2** 
- **Plotly** et **Folium** : intégration de graphiques et cartes interactives directement dans le site


## Dataset choices / Download / Description

### Description des classes

#### Espèces et groupe d'espèces : OBIS 

Les données compilant les localisations datées de chaque espèce retenue sont ordonnées dans des tableaux de données téléchargeables sur **OBIS**, en sélectionnant deux conditions de récupération : les données d'observation doivent datées de la **période comprise entre 01/01/2000 et au plus proche, 25/10/2025**. 
Elles doivent secondairement être restreinte à la zone géographique délimitée arbitrairement par le groupe de travail comme "les mers et océans de l'Europe occidentale". Soit : **lon −25 → 45, lat 27 → 69.**
Cela inclut :
- tout l’Atlantique Nord-Est depuis les Açores et Madère jusqu’à la mer de Norvège,
  - la mer du Nord, la mer Baltique,
  - la mer Celtique, la mer d’Irlande,
- la mer Méditerranée occidentale et centrale (mais pas la Méditerranée orientale au-delà d’environ 45°E).
Cela excepte :
- l’Arctique profond,
- - la mer de Barents entière
  - les zones groenlandaises.

Les colonnes de chacun de ces fichiers, actuellement sous format tsv, sont les mêmes pour tous les fichiers . Il y en a 15. La majorité de ces colonnes sont téléchargées automatiquement lorsqu'on n'utilise pas de code pour télécharger ces fichiers, et seront supprimées ultérieurement puisqu'elle ne sont ici pas utiles . On a au total :
- scientificName   → retenue et exploitée
-	taxonRank        → inutile, bientôt supprimée
- aphiaID          → inutile, bientôt supprimée
- species          → inutile, bientôt supprimée
- decimalLongitude → retenue et exploitée
- decimalLatitude  → retenue et exploitée	
- eventDate	       → retenue et exploitée, va être très utile par la suite
- date_year	       → inutile, bientôt supprimée
- basisOfRecord    → inutile, bientôt supprimée	
- datasetID	       → inutile, bientôt supprimée
- datasetName	     → inutile, bientôt supprimée
- occurrenceID	   → inutile, bientôt supprimée
- institutionCode  → inutile, bientôt supprimée	
- country	         → inutile, bientôt supprimée
- depth	           → inutile, bientôt supprimée

Le format est amené à évoluer pour prendre l'extension .csv ou .xlsx grâce au code qui est en cours de rédaction depuis que les contributeurs de ce projet ont appris qu'ils peuvent faire une telle manipulation. Le programme en question est le suivant : https://github.com/InesBahraoui22/BlueObserver/blob/base_de_donnees/Test_code_obis.py

Les classes prévues sont espèces et groupes d'espèces, auxquelles seront associées :
- nom espèce vernaculaire
- nom espèce scientifique
- longitude
- latitude
- date d'observation, qui donnera deux sous-catégories
  - mois d'observation
  - saison d'observation
 
Les longitudes et latitudes permettront de créer deux nouvelles variables : le pays et la région.

#### Données océanographiques : COPERNICUS

Les paramètres climatologiques liées à l'océan qui nous permettront de jauger des périodes idéales (= hors tempêtes) pour observer les espèces sont trouvables sur COPERNICUS. Les paramètres retenues ont été choisis sur des critères de tolérance humaine et de règlementation navale. Très simplement, l'ulitisateur ne sera pas inviter à sortir lorsque l'eau est trop froide pour s'y baigner et/ou lorsque les vagues sont trop hautes pour naviguer ou se baigner.
Ainsi les paramètres en question sont :
- la température de surface
- la hauteur significative des vagues

La grille des données océanographiques de Copernicus couvre la planète entière (≈ 1800×899 points), avec des longitudes qu'il faudra corriger pour faire correspondre à celles des fichiers expèces (exemple : min lat = -89.800). La résolution est de 0.2°.

L’axe time de la première base de données comporte 12 mois (janvier → décembre), ce qui indique une climatologie (moyenne mensuelle multi-annuelle). Les données couvrent la période allant de 1993 à 2025, ce qui demande éventuellement un ajustement de la fenêtre temporelle sur les fichiers espèces. Deux paramètres ont été retenus pour décrire la force des vagues : la hauteur significative des vagues de surface (en m) et la période moyenne des vagues (en s).

La deuxième base de données comporte aussi 12 mois (janvier → décembre), pour obtenir une climatologie identique. Les données couvrent la période allant de 1980 à 2020, ce qui demande éventuellement un ajustement de la fenêtre temporelle sur les fichiers espèces. 
Plusieurs paramètres ont été retenus pour décrire la physique des mers et océans retenues :
- la température de surface (en °C)
- la vitesse des courants venant d'est (en m.s^(1), positive quand la direction est l'est, négative quand la direction est l'ouest)
- la vitesse des courants venant du nord (en m.s^(1), positive quand la direction est le Nord, négative quand la direction est le Sud)
- hauteur des vagues au-dessus de la géoïde (= la hauteur de l'eau) (en m).

#### Données météorologiques : KAGGEL (abandon de Open-Meteo)

Les paramètres météorologiques retenus pour proposer une expérience d'écotourisme agréable à l'utilisateur sont donc l'abscence de tempêtes, mais d'un point de vue atmosphérique plutôt qu'océaniques. Ainsi sont retenues la température atmosphérique (en °C), la force du vent (en km/h) et la quantité de précipitations (pluie ou neige, en mm/j). Ceci, afin d'isoler les jours et les endroits où on peut non seulement observer les espèces, mais le faire sans être gêner par un rideau de pluie ou de neige, sans que les températures extérieures soient intolérables.

La composante du vent permettra de faire une double vérification des conditions de navigation avec les paramètres retenus dans la base de données Copernicus.

N'ayant pas réussi à ce jour à obtenir les plages de données temporelles et spatiales désirées via open-meteo, volet Historical weather, pour une raison encore inconnue, l'équipe de travail va tenter de trouver un équivalent via KAGGEL, avec les mêmes paramètres que pour les autres bases de données.


