Introduction to BlueObserver
===========================

Projet goal
------------------

BlueObserver priority is to integrated:

1. **Observational datapoints** from OBIS (Ocean Biogeographic Information System)
2. **Two action limitin marine data** from the Copernicus Marine service
3. **Temporal meteorological data** from Open-Meteo

General Architecture
---------------------

The project follows a modular architecture:

.. mermaid::

   graph TD
       A[OBIS API] --> B[Import of species];
       C[Copernicus Marine] --> D[Import of marine data];
       E[Open-Meteo API] --> F[Meteorological implementation];
       B --> G[Join of data];
       D --> G;
       F --> G;
       G --> H[final_points.json];
       H --> I[Visualisation Flask];

Exploited data
----------------

* **Chosen species** : 28 marine mammalian species (whales, dolphins, pinnipeds)
* **Area** : North-western Europe (-25° to 45° longitude, 27° tp 69° latitude)
* **Time** : From 2000 to nowadays
* **Limiting environmental variables** :
   * Sea Surface temperature (SST)
   * Mean wave height (VHM0)
   * Mean atmospheric temperature
   * Cumulated precipitations
   * Wind speed