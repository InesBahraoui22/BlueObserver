# creer_fichiers_tests_nc.py

import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path


def creer_fichiers_test_nc(dossier_base: Path) -> None:
    """
    Crée des petits fichiers NetCDF de test pour :
    - la température de mer (thetao_cglo)
    - la hauteur significative des vagues (VHM0)

    Arborescence créée :

        dossier_base/
            temp/
                temp_2000.nc
                temp_2001.nc
            vagues/
                vagues_2000.nc
                vagues_2001.nc
    """

    dossier_base = Path(dossier_base)
    doss_temp = dossier_base / "temp"
    doss_vagues = dossier_base / "vagues"

    doss_temp.mkdir(parents=True, exist_ok=True)
    doss_vagues.mkdir(parents=True, exist_ok=True)

    # On fait un mini-grillage 2x2
    latitudes = np.array([42.0, 43.0])   # par ex. Méditerranée
    longitudes = np.array([5.0, 6.0])

    # On crée de petites séries mensuelles sur 2 ans seulement
    annees = [2000, 2001]

    for an in annees:
        # Une date par mois (fin de mois)
        temps = pd.date_range(f"{an}-01-01", f"{an}-12-31", freq="M")

        # ---------- TEMPÉRATURE (thetao_cglo) ----------
        # Données artificielles : 15°C +/- bruit
        data_temp = 15 + 5 * np.random.randn(len(temps), len(latitudes), len(longitudes))

        ds_temp = xr.Dataset(
            {
                "thetao_cglo": (("time", "latitude", "longitude"), data_temp)
            },
            coords={
                "time": temps,
                "latitude": latitudes,
                "longitude": longitudes
            },
        )

        fichier_temp = doss_temp / f"temp_{an}.nc"
        ds_temp.to_netcdf(fichier_temp)
        print(f"Créé : {fichier_temp}")

        # ---------- VAGUES (VHM0) ----------
        # Données artificielles : 1 m +/- bruit
        data_vagues = 1 + 0.5 * np.random.randn(len(temps), len(latitudes), len(longitudes))

        ds_vagues = xr.Dataset(
            {
                "VHM0": (("time", "latitude", "longitude"), data_vagues)
            },
            coords={
                "time": temps,
                "latitude": latitudes,
                "longitude": longitudes
            },
        )

        fichier_vagues = doss_vagues / f"vagues_{an}.nc"
        ds_vagues.to_netcdf(fichier_vagues)
        print(f"Créé : {fichier_vagues}")

    print("\n✅ Fichiers NetCDF de test créés.")


if __name__ == "__main__":
    # 🔧 ADAPTE CE CHEMIN À TON PROJET
    # Par exemple : Path("conditions_limitantes_sortie/conditions_marines")
    base = Path("conditions_limitantes_sortie/conditions_marines")
    creer_fichiers_test_nc(base)
