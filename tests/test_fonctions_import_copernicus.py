import pytest
import tempfile
import pandas as pd
import xarray as xr
import numpy as np
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import fonctions_import_copernicus as copernicus_module

# Fixtures
@pytest.fixture
def mock_catalogue():
    """Mock d'un catalogue Copernicus"""
    mock = Mock()
    
    # Création d'un dataset mock
    mock_dataset = Mock()
    mock_dataset.dataset_id = "cmems_mod_glo_phy-all_my_0.25deg_P1D-m"
    
    # Création d'une variable mock
    mock_var = Mock()
    mock_var.short_name = "thetao_cglo"
    mock_var.standard_name = "sea_water_temperature"
    mock_var.units = "degrees_C"
    
    mock_service = Mock()
    mock_service.variables = [mock_var]
    
    mock_part = Mock()
    mock_part.services = [mock_service]
    
    mock_version = Mock()
    mock_version.parts = [mock_part]
    
    mock_dataset.versions = [mock_version]
    
    mock_product = Mock()
    mock_product.datasets = [mock_dataset]
    mock.products = [mock_product]
    
    return mock

@pytest.fixture
def temp_nc_file():
    """Création d'un fichier NetCDF temporaire pour les tests"""
    with tempfile.NamedTemporaryFile(suffix='.nc', delete=False) as tmp:
        # Création de données d'exemple
        time = pd.date_range('2023-01-01', periods=12, freq='MS')
        lat = np.arange(27.0, 70.0, 1.0)
        lon = np.arange(-25.0, 46.0, 1.0)
        
        # Création d'un DataArray avec des données aléatoires
        data = np.random.randn(len(time), len(lat), len(lon)) + 10  # températures autour de 10°C
        
        ds = xr.Dataset(
            {
                'thetao_cglo': (['time', 'latitude', 'longitude'], data)
            },
            coords={
                'time': time,
                'latitude': lat,
                'longitude': lon
            }
        )
        
        ds.to_netcdf(tmp.name)
        yield tmp.name
        os.unlink(tmp.name)

class TestCopernicusFunctions:
    """Tests pour les fonctions d'import Copernicus"""
    
    def test_renseigner_annee_fin(self):
        """Test la fonction qui retourne l'année actuelle"""
        annee_fin, annees = copernicus_module.renseigner_annee_fin()
        
        current_year = datetime.now().year
        assert annee_fin == current_year
        assert 2000 in annees
        assert current_year in annees
        assert len(annees) == current_year - 2000 + 1
    
    def test_recuperer_product_id_temp_defaut(self):
        """Test la récupération de l'ID produit température avec valeur par défaut"""
        with patch('builtins.input', return_value=""):
            result = copernicus_module.recuperer_product_id_temp()
            assert result == "GLOBAL_MULTIYEAR_PHY_ENS_001_031"
    
    def test_recuperer_product_id_temp_personnalise(self):
        """Test la récupération de l'ID produit température avec valeur personnalisée"""
        custom_id = "CUSTOM_PRODUCT_ID"
        with patch('builtins.input', return_value=custom_id):
            result = copernicus_module.recuperer_product_id_temp()
            assert result == custom_id
    
    def test_choisir_dataset_id_defaut(self, mock_catalogue):
        """Test la sélection de dataset avec choix par défaut"""
        with patch('builtins.input', return_value=""):
            result = copernicus_module.choisir_dataset_id(mock_catalogue)
            assert result == "cmems_mod_glo_phy-all_my_0.25deg_P1D-m"
    
    def test_choisir_variable_dans_dataset_defaut(self, mock_catalogue):
        """Test la sélection de variable avec valeurs par défaut"""
        with patch('builtins.input', return_value=""):
            variable, unite = copernicus_module.choisir_variable_dans_dataset(
                catalogue=mock_catalogue,
                dataset_id="cmems_mod_glo_phy-all_my_0.25deg_P1D-m",
                type_variable="temp",
                mapping_vars_par_defaut={
                    "cmems_mod_glo_phy-all_my_0.25deg_P1D-m": "thetao_cglo"
                }
            )
            
            assert variable == "thetao_cglo"
            assert unite == "degrees_C"
    
    def test_moyennage_mensuelle(self, temp_nc_file, temp_data_dir):
        """Test le calcul des moyennes mensuelles"""
        temp_dir = Path(temp_data_dir)
        output_dir = temp_dir / "output"
        
        # Copier le fichier NC temporaire dans le dossier de test
        test_file = temp_dir / "test.nc"
        with open(temp_nc_file, 'rb') as src, open(test_file, 'wb') as dst:
            dst.write(src.read())
        
        # Exécuter la fonction de moyennage
        result_path = copernicus_module.moyennage_mensuelle_donnees_nc(
            dossier_nc=temp_dir,
            variable_interet="thetao_cglo",
            dossier_sortie=output_dir
        )
        
        # Vérifications
        assert result_path.exists()
        assert result_path.suffix == ".csv"
        
        # Lire le CSV produit
        df = pd.read_csv(result_path)
        
        # Vérifier les colonnes
        expected_columns = ["month", "month_name", "latitude", "longitude", "thetao_cglo"]
        for col in expected_columns:
            assert col in df.columns
        
        # Vérifier les mois
        assert set(df["month"].unique()) == set(range(1, 13))
        assert all(df["month_name"].notna())
    
    def test_choisir_id_dataset_sachant_par_defaut(self, mock_catalogue):
        """Test la sélection de dataset avec mapping par défaut"""
        mapping_defaut = {
            "GLOBAL_MULTIYEAR_PHY_ENS_001_031": "cmems_mod_glo_phy-all_my_0.25deg_P1D-m"
        }
        
        result = copernicus_module.choisir_id_dataset_sachant_par_defaut(
            catalogue=mock_catalogue,
            product_id="GLOBAL_MULTIYEAR_PHY_ENS_001_031",
            mapping_defaut=mapping_defaut
        )
        
        assert result == "cmems_mod_glo_phy-all_my_0.25deg_P1D-m"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])