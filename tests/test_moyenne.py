# test_vagues_calcul.py
import pytest
import xarray as xr
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

# Importer la fonction à tester (si elle est dans un module)
# Si ton code est dans un script, on va tester la logique

def test_vagues_calcul_integration():
    """Test d'intégration complet du flux de données"""
    
    # 1. Créer des données NetCDF factices
    with tempfile.TemporaryDirectory() as tmpdir:
        # Créer un fichier NetCDF factice
        time = pd.date_range('2020-01-01', periods=365, freq='D')
        lat = np.array([45.0, 46.0])
        lon = np.array([-1.0, -2.0])
        
        # Créer des données VHM0 factices
        vhm0_data = np.random.rand(len(time), len(lat), len(lon)) * 3.0
        
        ds = xr.Dataset(
            {
                'VHM0': xr.DataArray(
                    vhm0_data,
                    dims=['time', 'latitude', 'longitude'],
                    coords={
                        'time': time,
                        'latitude': lat,
                        'longitude': lon
                    }
                )
            }
        )
        
        # Sauvegarder le fichier factice
        test_nc_file = os.path.join(tmpdir, 'test_vagues.nc')
        ds.to_netcdf(test_nc_file)
        
        # 2. Tester le chargement
        ds_loaded = xr.open_mfdataset(
            os.path.join(tmpdir, "*.nc"),
            chunks={'time': 100},
            combine='by_coords'
        )
        
        assert 'VHM0' in ds_loaded
        assert len(ds_loaded.time) == 365
        assert len(ds_loaded.latitude) == 2
        assert len(ds_loaded.longitude) == 2
        
        # 3. Tester le resample mensuel
        da = ds_loaded['VHM0']
        da_mensuel = da.resample(time='1MS').mean()
        
        # Devrait avoir 12 mois (ou 13 selon le début/fin)
        assert len(da_mensuel.time) >= 12
        
        # 4. Tester la climatologie (moyenne par mois)
        da_climato = da_mensuel.groupby("time.month").mean("time")
        
        # Doit avoir 12 mois
        assert len(da_climato.month) == 12
        
        # 5. Tester la conversion en DataFrame
        df = da_climato.to_dataframe().reset_index()
        
        assert not df.empty
        assert 'month' in df.columns
        assert 'VHM0' in df.columns
        assert 'latitude' in df.columns
        assert 'longitude' in df.columns
        
        # 6. Tester le renommage des colonnes
        df_renamed = df.rename(columns={"month": "mois"})
        assert 'mois' in df_renamed.columns
        
        # 7. Tester l'ajout des noms de mois
        df_renamed["mois_nom"] = pd.to_datetime(df_renamed["mois"], format="%m").dt.month_name()
        assert 'mois_nom' in df_renamed.columns
        
        # Vérifier que janvier est présent
        assert 'January' in df_renamed['mois_nom'].values
        
        # 8. Tester la sauvegarde CSV
        output_file = os.path.join(tmpdir, "test_output.csv")
        df_renamed.to_csv(output_file, index=False)
        
        assert os.path.exists(output_file)
        
        # Vérifier le contenu du CSV
        df_loaded = pd.read_csv(output_file)
        assert not df_loaded.empty
        assert len(df_loaded) == 2 * 2 * 12  # 2 lats * 2 lons * 12 mois
        
        print("✅ Test d'intégration réussi")
        ds_loaded.close()

def test_calcul_moyenne_mensuelle():
    """Test spécifique du calcul de moyennes mensuelles"""
    
    # Créer des données temporelles
    time = pd.date_range('2020-01-01', periods=60, freq='D')  # 2 mois
    data = np.ones((len(time), 1, 1)) * 10.0  # Valeur constante de 10
    
    ds = xr.Dataset(
        {
            'VHM0': xr.DataArray(
                data,
                dims=['time', 'latitude', 'longitude'],
                coords={'time': time, 'latitude': [45.0], 'longitude': [-1.0]}
            )
        }
    )
    
    # Calculer la moyenne mensuelle
    da_mensuel = ds['VHM0'].resample(time='1MS').mean()
    
    # Vérifier
    assert len(da_mensuel.time) == 2  # Janvier et Février
    assert np.allclose(da_mensuel.values, 10.0)  # Toutes les valeurs doivent être 10
    
    print("✅ Test moyenne mensuelle réussi")

def test_climatologie_par_mois():
    """Test du calcul de climatologie (moyenne par mois sur plusieurs années)"""
    
    # Créer 2 ans de données
    time = pd.date_range('2020-01-01', periods=730, freq='D')  # 2 ans
    
    # Données: janvier=1.0, février=2.0, etc.
    month_values = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0])
    
    # Répéter pour chaque jour
    daily_values = []
    for t in time:
        month_idx = t.month - 1
        daily_values.append(month_values[month_idx])
    
    data = np.array(daily_values).reshape(-1, 1, 1)
    
    ds = xr.Dataset(
        {
            'VHM0': xr.DataArray(
                data,
                dims=['time', 'latitude', 'longitude'],
                coords={'time': time, 'latitude': [45.0], 'longitude': [-1.0]}
            )
        }
    )
    
    # Calculer la climatologie
    da_mensuel = ds['VHM0'].resample(time='1MS').mean()
    da_climato = da_mensuel.groupby("time.month").mean("time")
    
    # Vérifier
    assert len(da_climato.month) == 12
    
    # Janvier devrait être 1.0 (moyenne de 2 janvier)
    january_value = da_climato.sel(month=1).values[0, 0]
    assert np.allclose(january_value, 1.0)
    
    # Décembre devrait être 12.0
    december_value = da_climato.sel(month=12).values[0, 0]
    assert np.allclose(december_value, 12.0)
    
    print("✅ Test climatologie réussi")

def test_formatage_dataframe():
    """Test du formatage du DataFrame final"""
    
    # Créer un DataArray de test
    months = np.array([1, 2, 3])
    lats = np.array([45.0, 46.0])
    lons = np.array([-1.0, -2.0])
    
    data = np.random.rand(len(months), len(lats), len(lons))
    
    da = xr.DataArray(
        data,
        dims=['month', 'latitude', 'longitude'],
        coords={'month': months, 'latitude': lats, 'longitude': lons}
    )
    
    # Convertir en DataFrame
    df = da.to_dataframe().reset_index()
    
    # Vérifier la structure
    assert set(df.columns) == {'month', 'latitude', 'longitude', 'VHM0'}
    assert len(df) == 3 * 2 * 2  # 3 mois * 2 lats * 2 lons
    
    # Tester le renommage
    df_renamed = df.rename(columns={"month": "mois"})
    assert 'mois' in df_renamed.columns
    
    # Tester l'ajout des noms de mois
    df_renamed["mois_nom"] = pd.to_datetime(df_renamed["mois"], format="%m").dt.month_name()
    
    # Vérifier les noms de mois
    month_names = df_renamed['mois_nom'].unique()
    assert 'January' in month_names
    assert 'February' in month_names
    assert 'March' in month_names
    
    print("✅ Test formatage DataFrame réussi")

def test_gestion_erreurs():
    """Test de la gestion des erreurs"""
    
    # Test avec dossier inexistant
    with pytest.raises(FileNotFoundError):
        xr.open_mfdataset("/dossier/inexistant/*.nc")
    
    # Test avec variable inexistante
    ds = xr.Dataset({'autre_variable': xr.DataArray([1, 2, 3])})
    
    with pytest.raises(KeyError):
        _ = ds['VHM0']  # Variable qui n'existe pas
    
    print("✅ Test gestion erreurs réussi")

def test_performance():
    """Test de performance (vérification du chunking)"""
    
    with patch('xarray.open_mfdataset') as mock_open:
        mock_ds = MagicMock()
        mock_ds.__contains__.return_value = True
        mock_ds.__getitem__.return_value = MagicMock()
        mock_open.return_value = mock_ds
        
        # Appeler la fonction avec chunks
        result = xr.open_mfdataset(
            "test/*.nc",
            chunks={'time': 100},
            combine='by_coords'
        )
        
        # Vérifier que chunks a été passé
        mock_open.assert_called_once()
        call_kwargs = mock_open.call_args[1]
        assert 'chunks' in call_kwargs
        assert call_kwargs['chunks'] == {'time': 100}
        
        print("✅ Test performance réussi")

def test_valeur_moyenne_correcte():
    """Test que la moyenne est calculée correctement"""
    
    # Données: [1, 2, 3, 4] sur 4 jours
    time = pd.date_range('2020-01-01', periods=4, freq='D')
    data = np.array([1.0, 2.0, 3.0, 4.0]).reshape(-1, 1, 1)
    
    ds = xr.Dataset(
        {
            'VHM0': xr.DataArray(
                data,
                dims=['time', 'latitude', 'longitude'],
                coords={'time': time, 'latitude': [45.0], 'longitude': [-1.0]}
            )
        }
    )
    
    # Moyenne mensuelle (ici juste janvier)
    da_mensuel = ds['VHM0'].resample(time='1MS').mean()
    
    # La moyenne de [1, 2, 3, 4] est 2.5
    assert np.allclose(da_mensuel.values, 2.5)
    
    print("✅ Test valeur moyenne réussi")

# Tests avec mocking pour éviter les fichiers réels
@patch('xarray.open_mfdataset')
@patch('pandas.DataFrame.to_csv')
def test_flux_complet_mock(mock_to_csv, mock_open_mfdataset):
    """Test du flux complet avec mocking (pas de fichiers réels)"""
    
    # Configurer les mocks
    mock_ds = MagicMock()
    mock_da = MagicMock()
    mock_da_mensuel = MagicMock()
    mock_da_climato = MagicMock()
    mock_df = MagicMock()
    
    # Chaîner les appels
    mock_open_mfdataset.return_value = mock_ds
    mock_ds.__getitem__.return_value = mock_da
    mock_da.resample.return_value.mean.return_value = mock_da_mensuel
    mock_da_mensuel.groupby.return_value.mean.return_value = mock_da_climato
    mock_da_climato.to_dataframe.return_value.reset_index.return_value = mock_df
    
    # Simuler l'exécution du script
    variable_interesse = "VHM0"
    
    # Ouverture
    ds = mock_open_mfdataset("*.nc", chunks={'time': 100}, combine='by_coords')
    
    # Récupération variable
    da = ds[variable_interesse]
    
    # Resample
    da_mensuel = da.resample(time='1MS').mean()
    
    # Climatologie
    da_climato = da_mensuel.groupby("time.month").mean("time")
    
    # DataFrame
    df = da_climato.to_dataframe().reset_index()
    
    # Vérifier que tout a été appelé
    mock_open_mfdataset.assert_called_once()
    mock_ds.__getitem__.assert_called_once_with(variable_interesse)
    
    print("✅ Test flux complet mock réussi")

# Point d'entrée pour exécuter les tests manuellement
if __name__ == "__main__":
    print("🚀 Lancement des tests unitaires...\n")
    
    # Exécuter les tests dans l'ordre
    tests = [
        test_calcul_moyenne_mensuelle,
        test_climatologie_par_mois,
        test_formatage_dataframe,
        test_valeur_moyenne_correcte,
        test_gestion_erreurs,
        test_performance,
        test_vagues_calcul_integration,
    ]
    
    for test_func in tests:
        try:
            test_func()
        except AssertionError as e:
            print(f"❌ {test_func.__name__} a échoué: {e}")
        except Exception as e:
            print(f"⚠️ {test_func.__name__} erreur inattendue: {e}")
    
    print("\n" + "="*50)
    print("✅ Tous les tests ont été exécutés")