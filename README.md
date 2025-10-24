# OceanAware

## Membres
Chloé MOMONT/
Ines BAHRAOUI/
Aly /
Oscar Bonnet

## Figure of interest & Narration

Notre figure d’intérêt principale est une **carte interactive touristique des océans**, combinant données de biodiversité marine (OBIS), conditions environnementales (Copernicus) et météo locale (Open-Meteo).  

L’objectif est de permettre aux utilisateurs — plongeurs, navigateurs, touristes ou passionnés de nature — de **découvrir quelles espèces marines sont observables selon la zone géographique, la saison et les conditions océaniques**.  

Chaque point sur la carte représente une observation d’espèce marine, avec :
- le **nom de l’espèce** (ex. *Delphinus delphis* — dauphin commun),  
- la **date d’observation**,  
- la **température et salinité** de l’eau à ce moment,  
- et un **lien d’information touristique** (spot de plongée, période recommandée, etc.).  

L’utilisateur pourra filtrer :
- une **espèce** ou un **groupe d’espèces** (ex. tortues, dauphins, poissons tropicaux),  
- une **région** (ex. Méditerranée, Caraïbes, Atlantique Nord),  
- une **période** (ex. été, hiver).  

Cette carte interactive sera accompagnée d’une légende intuitive et d’un design orienté “exploration” :
- dégradé de couleurs pour la température de surface,
- photos d’espèces ,
- info-bulles avec conseils touristiques.

---

### Exemple de scénario narratif

> Un utilisateur choisit “Tortue caouanne” 🐢 et “été” sur la carte.  
> OceanAware lui montre les zones les plus favorables à son observation en mer, avec des températures entre 20 °C et 27 °C.  
> Il découvre que la Méditerranée orientale est particulièrement propice à cette période.  
> La carte devient ainsi un **outil de planification de voyage écologique et éducatif**.

---

### Exemple de visuel attendu

![Carte touristique interactive des observations d’espèces marines](figs/map_tourism_mockup.png){width=80%}

---

### Idée générale
  
OceanAware rend la science accessible et utile aux voyageurs en valorisant :
- la **diversité marine** (OBIS),  
- la **qualité environnementale** (Copernicus),  
- et la **météo adaptée** aux activités marines (Open-Meteo).  

L’objectif est de **favoriser un tourisme responsable**, qui s’appuie sur la donnée ouverte pour encourager la découverte et la protection du milieu marin.

## Architecture
```
OceanAware/
│
├── my_module_name/                  # Core Python module
│   ├── __init__.py
│   ├── data_pipeline.py             # Data extraction, cleaning, and merging
│   ├── species_map.py               # Main class SpeciesMap for visualization
│   ├── utils.py                     # Helper functions (API requests, caching, formatting)
│   └── analysis.py                  # Optional module for ecological analysis / stats
│
├── roadmap/
│   └── README.qmd                   # Project outline and Gantt chart
│
├── slide/
│   └── OceanAware_slide.qmd         # Slide deck for the final oral presentation
│
├── figs/
│   ├── mockup_interface.png         # Mockup of the interactive map
│   └── data_flow_diagram.png        # Schema of data processing
│
├── tests/
│   ├── test_data_pipeline.py
│   └── test_species_map.py
│
├── .github/workflows/
│   └── ci.yml                       # GitHub Actions for Continuous Integration
│
├── .gitignore
├── requirements.txt
└── README.md                        # Main project description (for GitHub)
```



## Packages/software description for the project

## Dataset choices / Download / Description
