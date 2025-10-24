# Projet développement logiciel : OceanAware

## Membres
Chloé MOMONT/
Ines BAHRAOUI/
Aly DAHOUD/
Oscar Bonnet

## Nom du Projet
OceanAware

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


### Logo du site


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



## Packages/software description for the project

## Dataset choices / Download / Description
