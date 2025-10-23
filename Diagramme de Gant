flowchart TD
    A[User Interface 🌐] --> B[Interactive Map 🗺️]
    B --> C[Frontend - Quarto HTML JS]
    C --> D[Backend - Python Flask]
    D --> E[Data Pipeline - pandas geopandas]
    E --> F1[OBIS API 🐠 - Marine species]
    E --> F2[Copernicus API 🌊 - Ocean data]
    E --> F3[Open Meteo API ☀️ - Weather data]
    F1 --> G[Data Integration & Cleaning]
    F2 --> G
    F3 --> G
    G --> H[Processed Data Storage]
    H --> I[Visualization Engine - Plotly Folium]
    I --> B

    subgraph "Project Structure"
        J1[/main.py/]
        J2[/data_pipeline.py/]
        J3[/visualization.py/]
        J4[/roadmap/README.qmd/]
        J5[/figs/mockup_map.png/]
    end
```
  gantt
    dateFormat  YYYY-MM-DD
    title OceanAware - Development Schedule
    section Data Collection
    OBIS & Copernicus Exploration :done, des1, 2025-10-10, 2025-10-15
    Open-Meteo Setup :active, des2, 2025-10-15, 2025-10-22

    section Data Processing
    Integration & Cleaning :des3, 2025-10-22, 2025-10-28
    Python Pipeline Setup :des4, 2025-10-28, 2025-11-03

    section Visualization
    Interactive Map Prototype :des5, 2025-11-03, 2025-11-10
    UI Design & Filters :des6, 2025-11-10, 2025-11-17

    section Documentation
    README & Report Writing :des7, 2025-11-17, 2025-11-22
    Final Presentation :des8, 2025-11-22, 2025-11-25

