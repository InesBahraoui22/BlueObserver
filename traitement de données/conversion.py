import xarray as xr
import pandas as pd
import os 

# Charger le fichier NetCDF
ds = xr.open_dataset("/Users/ines/Desktop/M1/wetransfer_vagues_2013-nc_2025-11-26_0951/vagues_2018.nc")

# Convertir en DataFrame
df = ds.to_dataframe().reset_index()

# Sauvegarder en CSV
df.to_csv("/Users/ines/Desktop/M1/vagues_2018.csv", index=False)
