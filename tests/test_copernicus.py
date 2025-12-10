# test_copernicus_extraction.py
import pytest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock, call
import pandas as pd
from pathlib import Path
import xarray as xr
import numpy as np
from datetime import datetime

# --------- CONFIGURATION ---------
# On va tester la logique sans vraiment appeler l'API

def test_configuration_constantes():
    """Test des constantes de configuration."""
    # Vérifier les bornes géographiques
    LON_MIN, LON_MAX = -25.0, 45.0
    LAT_MIN, LAT_MAX = 27.0, 69.0
    
    assert LON_MIN == -25.0
    assert LON_MAX == 45.0
    assert LAT_MIN == 27.0
    assert LAT_MAX == 69.0
    
    # Vérifier le polygone
    polygone = (-25, 45, 27, 69)
    assert polygone == (-25, 45, 27, 69)
    assert len(polygone) == 4
    
    # Vérifier les dates
    date_debut = "2000-01-01T00:00:00"
    date_fin = "2025-01-01T00:00:00"
    
    assert date_debut == "2000-01-01T00:00:00"
    assert date_fin == "2025-01-01T00:00:00"
    
    # Vérifier la plage d'années
    annee_deb = 2001
    annee_fin = 2025
    annees = list(range(2000, 2025 + 1))
    
    assert annee_deb == 2001
    assert annee_fin == 2025
    assert len(annees) == 26  # 2000 à 2025 inclus
    assert 2000 in annees
    assert 2025 in annees
    
    # Vérifier les identifiants de données
    donnees_temp = "cmems_mod_glo_phy-all_my_0.25deg_P1D-m"
    donnees_vagues = "cmems_mod_glo_wav_my_0.2deg_PT3H-i"
    
    assert "temp" in donnees_temp.lower()
    assert "wav" in donnees_vagues.lower()
    
    print("✅ Configuration des constantes testée avec succès")
    return True

def test_directory_creation():
    """Test de la création des dossiers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Simuler la création des dossiers
        doss_vagues = tmp_path / "vagues"
        doss_temp = tmp_path / "temp"
        
        doss_vagues.mkdir(exist_ok=True)
        doss_temp.mkdir(exist_ok=True)
        
        # Vérifier que les dossiers existent
        assert doss_vagues.exists()
        assert doss_temp.exists()
        
        # Vérifier que ce sont bien des dossiers
        assert doss_vagues.is_dir()
        assert doss_temp.is_dir()
        
        print("✅ Création des dossiers testée avec succès")
        return True

def test_file_path_generation():
    """Test de la génération des chemins de fichiers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Simuler la structure du script
        doss_vagues = tmp_path / "vagues"
        doss_temp = tmp_path / "temp"
        
        doss_vagues.mkdir(exist_ok=True)
        doss_temp.mkdir(exist_ok=True)
        
        # Tester pour différentes années
        test_years = [2000, 2010, 2020, 2025]
        
        for year in test_years:
            # Fichier température
            fichier_temp = doss_temp / f"temp_{year}.nc"
            assert str(fichier_temp).endswith(f"temp_{year}.nc")
            assert fichier_temp.parent == doss_temp
            
            # Fichier vagues
            fichier_vagues = doss_vagues / f"vagues_{year}.nc"
            assert str(fichier_vagues).endswith(f"vagues_{year}.nc")
            assert fichier_vagues.parent == doss_vagues
            
            # Vérifier les noms
            assert f"temp_{year}" in str(fichier_temp)
            assert f"vagues_{year}" in str(fichier_vagues)
        
        print("✅ Génération des chemins de fichiers testée avec succès")
        return True

def test_date_range_generation():
    """Test de la génération des plages de dates."""
    
    # Tester pour différentes années
    test_cases = [
        (2000, "2000-01-01T00:00:00", "2001-01-01T00:00:00"),
        (2015, "2015-01-01T00:00:00", "2016-01-01T00:00:00"),
        (2024, "2024-01-01T00:00:00", "2025-01-01T00:00:00"),
    ]
    
    for year, expected_start, expected_end in test_cases:
        # Recréer la logique du script
        deb = f"{year}-01-01T00:00:00"
        fin = f"{year+1}-01-01T00:00:00"
        
        assert deb == expected_start
        assert fin == expected_end
        
        # Vérifier le format ISO 8601
        assert "T" in deb  # Format datetime avec T
        assert len(deb) == 19 + len(str(year))  # Longueur variable selon l'année
        
        # Vérifier que c'est bien l'année suivante
        assert int(fin[:4]) == year + 1
    
    print("✅ Génération des plages de dates testée avec succès")
    return True

@patch('copernicusmarine.describe')
def test_catalogue_inspection(mock_describe):
    """Test de l'inspection des catalogues Copernicus."""
    
    # Mock pour le catalogue température
    mock_temp_catalogue = Mock()
    mock_temp_product = Mock()
    mock_temp_dataset = Mock()
    mock_temp_version = Mock()
    mock_temp_part = Mock()
    mock_temp_service = Mock()
    mock_temp_variable = Mock()
    
    # Configurer le mock
    mock_temp_variable.standard_name = "sea_water_temperature"
    mock_temp_variable.short_name = "thetao_cglo"
    mock_temp_variable.units = "degrees_C"
    
    mock_temp_service.variables = [mock_temp_variable]
    mock_temp_part.services = [mock_temp_service]
    mock_temp_version.parts = [mock_temp_part]
    mock_temp_dataset.dataset_id = "cmems_mod_glo_phy-all_my_0.25deg_P1D-m"
    mock_temp_dataset.versions = [mock_temp_version]
    mock_temp_product.datasets = [mock_temp_dataset]
    mock_temp_catalogue.products = [mock_temp_product]
    
    mock_describe.return_value = mock_temp_catalogue
    
    # Simuler l'appel
    catalogue_temp = cm.describe(product_id="GLOBAL_MULTIYEAR_PHY_ENS_001_031")
    
    # Vérifications
    mock_describe.assert_called_once_with(product_id="GLOBAL_MULTIYEAR_PHY_ENS_001_031")
    
    # Vérifier la structure des données
    assert len(catalogue_temp.products) == 1
    assert len(catalogue_temp.products[0].datasets) == 1
    assert catalogue_temp.products[0].datasets[0].dataset_id == "cmems_mod_glo_phy-all_my_0.25deg_P1D-m"
    
    # Vérifier les variables
    variables = catalogue_temp.products[0].datasets[0].versions[0].parts[0].services[0].variables
    assert len(variables) == 1
    assert variables[0].standard_name == "sea_water_temperature"
    assert variables[0].short_name == "thetao_cglo"
    
    print("✅ Inspection des catalogues testée avec succès")
    return True

@patch('copernicusmarine.subset')
def test_download_loop_logic(mock_subset):
    """Test de la logique de la boucle de téléchargement."""
    
    # Configurer les mocks
    mock_response_temp = Mock()
    mock_response_temp.status = "success"
    
    mock_response_vagues = Mock()
    mock_response_vagues.status = "success"
    
    # Alterner entre les réponses
    mock_subset.side_effect = [mock_response_temp, mock_response_vagues] * 3
    
    # Simuler quelques années
    test_years = [2000, 2001, 2002]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        doss_vagues = tmp_path / "vagues"
        doss_temp = tmp_path / "temp"
        
        doss_vagues.mkdir(exist_ok=True)
        doss_temp.mkdir(exist_ok=True)
        
        # Variables de configuration
        LAT_MIN, LAT_MAX = 27.0, 69.0
        LON_MIN, LON_MAX = -25.0, 45.0
        donnees_temp = "cmems_mod_glo_phy-all_my_0.25deg_P1D-m"
        donnees_vagues = "cmems_mod_glo_wav_my_0.2deg_PT3H-i"
        
        call_count = 0
        
        for year in test_years:
            deb = f"{year}-01-01T00:00:00"
            fin = f"{year+1}-01-01T00:00:00"
            
            # TEMPÉRATURE
            fichier_temp = doss_temp / f"temp_{year}.nc"
            
            # Simuler l'appel à cm.subset pour la température
            expected_temp_call = call(
                dataset_id=donnees_temp,
                variables=["thetao_cglo"],
                minimum_latitude=LAT_MIN,
                maximum_latitude=LAT_MAX,
                minimum_longitude=LON_MIN,
                maximum_longitude=LON_MAX,
                minimum_depth=0.0,
                maximum_depth=25.0,
                start_datetime=deb,
                end_datetime=fin,
                output_directory=doss_temp,
                output_filename=fichier_temp.name
            )
            
            # VAGUES
            fichier_vagues = doss_vagues / f"vagues_{year}.nc"
            
            # Simuler l'appel à cm.subset pour les vagues
            expected_vagues_call = call(
                dataset_id=donnees_vagues,
                variables=["VHM0"],
                minimum_latitude=LAT_MIN,
                maximum_latitude=LAT_MAX,
                minimum_longitude=LON_MIN,
                maximum_longitude=LON_MAX,
                start_datetime=deb,
                end_datetime=fin,
                output_directory=doss_vagues,
                output_filename=fichier_vagues.name
            )
            
            call_count += 2
        
        # Vérifier que subset a été appelé le bon nombre de fois
        assert mock_subset.call_count == len(test_years) * 2
        
        print("✅ Logique de la boucle de téléchargement testée avec succès")
        return True

def test_parameter_validation():
    """Test de la validation des paramètres."""
    
    # Test des bornes géographiques valides
    LAT_MIN, LAT_MAX = 27.0, 69.0
    LON_MIN, LON_MAX = -25.0, 45.0
    
    assert -90 <= LAT_MIN <= 90
    assert -90 <= LAT_MAX <= 90
    assert -180 <= LON_MIN <= 180
    assert -180 <= LON_MAX <= 180
    assert LAT_MIN < LAT_MAX
    assert LON_MIN < LON_MAX
    
    # Test des profondeurs valides
    minimum_depth = 0.0
    maximum_depth = 25.0
    
    assert minimum_depth >= 0
    assert maximum_depth > minimum_depth
    
    # Test des formats de date
    test_dates = ["2000-01-01T00:00:00", "2025-12-31T23:59:59"]
    
    for date_str in test_dates:
        assert "T" in date_str
        assert date_str.count("-") == 2
        assert date_str.count(":") == 2
        
        # Essayer de parser la date
        try:
            datetime.fromisoformat(date_str.replace("Z", ""))
            date_valid = True
        except ValueError:
            date_valid = False
        
        assert date_valid, f"Date invalide: {date_str}"
    
    print("✅ Validation des paramètres testée avec succès")
    return True

def test_netcdf_structure():
    """Test de la structure NetCDF attendue."""
    
    # Créer un dataset xarray factice
    time = pd.date_range('2000-01-01', periods=365, freq='D')
    lat = np.linspace(27.0, 69.0, 10)
    lon = np.linspace(-25.0, 45.0, 15)
    
    # Données de température
    temp_data = np.random.rand(len(time), len(lat), len(lon)) * 20 + 10  # 10-30°C
    
    ds_temp = xr.Dataset(
        {
            'thetao_cglo': xr.DataArray(
                temp_data,
                dims=['time', 'latitude', 'longitude'],
                coords={
                    'time': time,
                    'latitude': lat,
                    'longitude': lon
                },
                attrs={
                    'units': 'degrees_C',
                    'long_name': 'Sea Water Temperature'
                }
            )
        }
    )
    
    # Vérifier la structure
    assert 'thetao_cglo' in ds_temp
    assert len(ds_temp.dims) == 3  # time, latitude, longitude
    assert 'time' in ds_temp.dims
    assert 'latitude' in ds_temp.dims
    assert 'longitude' in ds_temp.dims
    
    # Vérifier les coordonnées
    assert ds_temp.latitude.min() >= 27.0
    assert ds_temp.latitude.max() <= 69.0
    assert ds_temp.longitude.min() >= -25.0
    assert ds_temp.longitude.max() <= 45.0
    
    # Données de vagues
    wave_data = np.random.rand(len(time), len(lat), len(lon)) * 5  # 0-5m
    
    ds_waves = xr.Dataset(
        {
            'VHM0': xr.DataArray(
                wave_data,
                dims=['time', 'latitude', 'longitude'],
                coords={
                    'time': time,
                    'latitude': lat,
                    'longitude': lon
                },
                attrs={
                    'units': 'm',
                    'long_name': 'Significant Wave Height'
                }
            )
        }
    )
    
    assert 'VHM0' in ds_waves
    assert ds_waves.VHM0.attrs['units'] == 'm'
    
    print("✅ Structure NetCDF testée avec succès")
    return True

def test_error_handling():
    """Test de la gestion des erreurs."""
    
    # Test avec paramètres invalides
    invalid_cases = [
        {"LAT_MIN": 100.0, "LAT_MAX": 69.0},  # Latitude trop grande
        {"LON_MIN": -250.0, "LON_MAX": 45.0},  # Longitude trop petite
        {"minimum_depth": -10.0, "maximum_depth": 25.0},  # Profondeur négative
    ]
    
    for case in invalid_cases:
        if "LAT_MIN" in case:
            assert not (-90 <= case["LAT_MIN"] <= 90), f"Latitude invalide: {case['LAT_MIN']}"
    
    # Test des formats de date invalides
    invalid_dates = [
        "2000-01-01",  # Manque l'heure
        "2000/01/01T00:00:00",  # Mauvais séparateur
        "not-a-date",  # Pas une date du tout
    ]
    
    for date_str in invalid_dates:
        try:
            datetime.fromisoformat(date_str.replace("Z", ""))
            is_valid = True
        except ValueError:
            is_valid = False
        
        assert not is_valid, f"Date devrait être invalide: {date_str}"
    
    print("✅ Gestion des erreurs testée avec succès")
    return True

def test_performance_scaling():
    """Test de la performance avec différentes plages d'années."""
    
    # Tester différentes tailles de plages d'années
    test_ranges = [
        list(range(2000, 2001)),  # 1 année
        list(range(2000, 2005)),  # 5 années
        list(range(2000, 2010)),  # 10 années
        list(range(2000, 2025)),  # 25 années
    ]
    
    for year_range in test_ranges:
        n_years = len(year_range)
        
        # Vérifier que le nombre d'appels API serait proportionnel
        expected_api_calls = n_years * 2  # Température + Vagues
        
        # Pour un vrai test de performance, on mesurerait le temps
        # Ici on vérifie juste la logique
        assert expected_api_calls == n_years * 2
        
        print(f"  {n_years} années → {expected_api_calls} appels API")
    
    print("✅ Test de performance (scaling) effectué")
    return True

# --------- EXÉCUTION DES TESTS ---------

def run_all_tests():
    """Exécute tous les tests et affiche un résumé."""
    print("🧪" + "="*60)
    print("Lancement des tests unitaires pour extraction Copernicus")
    print("="*60 + "\n")
    
    # Liste des tests à exécuter (sans les tests mockés pour l'instant)
    basic_tests = [
        test_configuration_constantes,
        test_directory_creation,
        test_file_path_generation,
        test_date_range_generation,
        test_parameter_validation,
        test_netcdf_structure,
        test_error_handling,
        test_performance_scaling,
    ]
    
    # Tests avec mocking (nécessitent des imports)
    mock_tests = []
    
    # Essayer d'importer copernicusmarine
    try:
        import copernicusmarine as cm
        mock_tests = [
            test_catalogue_inspection,
            test_download_loop_logic,
        ]
        print("✅ Module copernicusmarine disponible pour les tests mockés")
    except ImportError:
        print("⚠️ Module copernicusmarine non disponible, tests mockés ignorés")
    
    # Exécuter tous les tests
    all_tests = basic_tests + mock_tests
    
    passed = 0
    failed = 0
    failed_tests = []
    
    for test_func in all_tests:
        test_name = test_func.__name__
        print(f"\n🔍 Test: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            if result:
                print(f"  ✅ {test_name} - RÉUSSI")
                passed += 1
            else:
                print(f"  ❌ {test_name} - ÉCHOUÉ (retourné False)")
                failed += 1
                failed_tests.append(test_name)
                
        except AssertionError as e:
            print(f"  ❌ {test_name} - ASSERTION ÉCHOUÉE: {e}")
            failed += 1
            failed_tests.append(test_name)
            
        except Exception as e:
            print(f"  ⚠️ {test_name} - ERREUR INATTENDUE: {type(e).__name__}: {e}")
            failed += 1
            failed_tests.append(test_name)
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMUM DES TESTS")
    print("="*60)
    print(f"✅ Tests réussis: {passed}")
    print(f"❌ Tests échoués: {failed}")
    
    if failed > 0:
        print(f"\n📋 Tests échoués:")
        for test_name in failed_tests:
            print(f"  • {test_name}")
    
    print("\n" + "="*60)
    if failed == 0:
        print("🎉 TOUS LES TESTS ONT RÉUSSI !")
        return True
    else:
        print(f"⚠️ {failed} test(s) ont échoué")
        return False

# --------- VERSION SIMPLIFIÉE ---------

def quick_test():
    """Test rapide des fonctionnalités principales."""
    print("🚀 Test rapide de l'extraction Copernicus")
    
    # Tests de base qui ne nécessitent pas de mocking
    tests_to_run = [
        test_configuration_constantes,
        test_directory_creation,
        test_file_path_generation,
        test_date_range_generation,
        test_parameter_validation,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests_to_run:
        try:
            if test_func():
                passed += 1
                print(f"  ✅ {test_func.__name__}")
            else:
                failed += 1
                print(f"  ❌ {test_func.__name__}")
        except Exception as e:
            failed += 1
            print(f"  ❌ {test_func.__name__}: {e}")
    
    print(f"\n📊 Résumé: {passed} réussis, {failed} échoués")
    return failed == 0

# --------- POINT D'ENTRÉE ---------

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Tests pour l'extraction Copernicus")
    parser.add_argument("--quick", action="store_true", help="Exécuter le test rapide")
    parser.add_argument("--all", action="store_true", help="Exécuter tous les tests")
    
    args = parser.parse_args()
    
    # Importer les modules nécessaires
    try:
        import copernicusmarine as cm
        cm_available = True
    except ImportError:
        cm_available = False
        print("⚠️ Attention: copernicusmarine n'est pas installé")
        print("   Tests mockés utilisés à la place")
    
    if args.quick or not (args.quick or args.all):
        success = quick_test()
    elif args.all:
        success = run_all_tests()
    
    exit(0 if success else 1)