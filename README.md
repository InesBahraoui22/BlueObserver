# OceanAware
Description :
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
- icônes d’espèces stylisées (🐬 🐢 🐠),
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

### Narration générale

Cette figure raconte **une histoire positive de la rencontre entre tourisme durable et données scientifiques**.  
OceanAware rend la science accessible et utile aux voyageurs en valorisant :
- la **diversité marine** (OBIS),  
- la **qualité environnementale** (Copernicus),  
- et la **météo adaptée** aux activités marines (Open-Meteo).  

L’objectif est de **favoriser un tourisme responsable**, qui s’appuie sur la donnée ouverte pour encourager la découverte et la protection du milieu marin.

###Diagramme de gantt
```{mermaid}
flowchart TD
    A[User Interface 🌐] --> B[Interactive Map 🗺️]
    B --> C[Frontend - Quarto HTML JS]
    C --> D[Backend - Python Flask]

    D --> E[Data Processing Pipeline]
    E --> F1[OBIS API 🐠 - Marine species]
    E --> F2[Copernicus API 🌊 - Ocean data]
    E --> F3[Open Meteo API ☀️ - Weather data]

    F1 --> G[Data Integration and Cleaning]
    F2 --> G
    F3 --> G

    G --> H[Processed Data Storage]
    H --> I[Visualization Engine - Plotly Folium]
    I --> B

    subgraph Project Structure
        J1[/main.py/]
        J2[/data_pipeline.py/]
        J3[/visualization.py/]
        J4[/roadmap/README.qmd/]
        J5[/figs/mockup_map.png/]
    end
```

    
```gantt
    dateFormat  YYYY-MM-DD
    title OceanAware - Project Roadmap

    section Data Collection
    OBIS Data Exploration         :done,    des1, 2025-10-10, 2025-10-15
    Copernicus / Open-Meteo Setup :active,  des2, 2025-10-15, 2025-10-22

    section Data Processing
    Data Cleaning & Integration   :         des3, 2025-10-22, 2025-10-28
    Pipeline Automation (Python)  :         des4, 2025-10-28, 2025-11-03

    section Visualization
    Interactive Map Prototype     :         des5, 2025-11-03, 2025-11-10
    UI Design & Filters           :         des6, 2025-11-10, 2025-11-17

    section Documentation
    README & Report (Quarto)      :         des7, 2025-11-17, 2025-11-22
    Final Presentation            :         des8, 2025-11-22, 2025-11-25
```

