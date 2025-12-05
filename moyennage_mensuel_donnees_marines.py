import xarray as xr
import pandas as pd
import glob
import os

# Configuration
dossier_nc = r"C:/Users/chloe/OneDrive/Bureau/M1_SSD/DEVELOPPEMENT_LOGICIEL/vagues"
variable_interesse = "VHM0"

# Ouvrir tous les fichiers NetCDF d'un coup
ds = xr.open_mfdataset(
    os.path.join(dossier_nc, "*.nc"),
    chunks={'time': 100},
    combine='by_coords'
)

# On récupère uniquement la variable qui nous intéresse
da = ds[variable_interesse]

# 1) Moyennes mensuelles (on passe de données journalières/horaires à mensuelles)
da_mensuel = da.resample(time='1MS').mean()

# 2) Moyenne toutes années confondues PAR MOIS et PAR POINT GPS
#    → on regroupe par mois du calendrier (1..12) et on moyenne sur l'axe temps
da_climato = da_mensuel.groupby("time.month").mean("time")

# 3) Passage en DataFrame (avec latitude, longitude, mois)
df = da_climato.to_dataframe().reset_index()

# 4) Nom de colonne plus clair pour le mois + nom du mois en toutes lettres
df = df.rename(columns={"month": "mois"})
df["mois_nom"] = pd.to_datetime(df["mois"], format="%m").dt.month_name()

# 5) Réorganisation des colonnes (facultatif, juste pour que ce soit lisible)
colonnes = ["mois", "mois_nom"]
if "latitude" in df.columns:
    colonnes.extend(["latitude", "longitude"])
colonnes.append(variable_interesse)
df = df[colonnes]

# 6) Sauvegarde en CSV
fichier_sortie = os.path.join(dossier_nc, f"moyennes_mensuelles_par_GPS_{variable_interesse}.csv")
df.to_csv(fichier_sortie, index=False)

print(f"✓ Fichier créé : {fichier_sortie}")

ds.close()