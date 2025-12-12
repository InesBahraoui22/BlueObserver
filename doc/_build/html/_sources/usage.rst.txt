User guide
===========

Execute the following scripts in the specific order:

1. **OBIS data** ::
   
      python data_generation/import_donnees_obis.py

2. **Copernicus data** ::
      python data_generation/fonctions_import_copernicus.py
      python data_generation/import_donnees_copernicus.py

3. **OpenMeteo data** ::
   
      python data_generation/fonctionsopenmeteo.py

4. **Final join** ::
      python data_generation/points.json.py
      python data_generation/jointure.py

5. **Visualisation** ::
   
      python app.py