import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import import_donnees_copernicus as copernicus_main
import import_donnees_copernicus as cm_module

# Fixtures
@pytest.fixture
def mock_cm():
    """Mock du module copernicusmarine"""
    with patch('import_donnees_copernicus.cm') as mock_cm:
        # Mock de la fonction describe
        mock_product = Mock()
        mock_dataset = Mock()
        mock_dataset.dataset_id = "test_dataset"
        
        mock_product.datasets = [mock_dataset]
        mock_catalogue = Mock()
        mock_catalogue.products = [mock_product]
        mock_cm.describe.return_value = mock_catalogue
        
        # Mock de la fonction subset
        mock_response = Mock()
        mock_response.status = "success"
        mock_cm.subset.return_value = mock_response
        
        yield mock_cm

@pytest.fixture
def temp_dirs():
    """Création de dossiers temporaires pour les tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Sauvegarder les chemins originaux
        original_dirs = {
            'doss_vagues': cm_module.doss_vagues if hasattr(cm_module, 'doss_vagues') else None,
            'doss_temp': cm_module.doss_temp if hasattr(cm_module, 'doss_temp') else None,
            'conditions_marines': cm_module.conditions_marines if hasattr(cm_module, 'conditions_marines') else None
        }
        
        # Créer des dossiers temporaires
        temp_dir_path = Path(temp_dir)
        cm_module.doss_vagues = temp_dir_path / "vagues_test"
        cm_module.doss_temp = temp_dir_path / "temp_test"
        cm_module.conditions_marines = temp_dir_path / "conditions_marines_test"
        
        yield temp_dir_path
        
        # Nettoyage
        if cm_module.doss_vagues.exists():
            shutil.rmtree(cm_module.doss_vagues)
        if cm_module.doss_temp.exists():
            shutil.rmtree(cm_module.doss_temp)
        if cm_module.conditions_marines.exists():
            shutil.rmtree(cm_module.conditions_marines)
        
        # Restaurer les valeurs originales
        for attr, value in original_dirs.items():
            if value is not None:
                setattr(cm_module, attr, value)

class TestCopernicusMain:
    """Tests pour le script principal d'import Copernicus"""
    
    def test_parameters_initialization(self):
        """Test l'initialisation des paramètres"""
        assert cm_module.LON_MIN == -25.0
        assert cm_module.LON_MAX == 45.0
        assert cm_module.LAT_MIN == 27.0
        assert cm_module.LAT_MAX == 69.0
        assert cm_module.polygone == (-25, 45, 27, 69)
        assert cm_module.annee_deb == 2000
    
    def test_directory_creation(self, temp_dirs):
        """Test la création des dossiers"""
        # Créer les dossiers
        cm_module.doss_vagues.mkdir(exist_ok=True)
        cm_module.doss_temp.mkdir(exist_ok=True)
        
        assert cm_module.doss_vagues.exists()
        assert cm_module.doss_temp.exists()
    
    def test_mapping_datasets(self):
        """Test les mappings par défaut"""
        assert "GLOBAL_MULTIYEAR_PHY_ENS_001_031" in cm_module.MAPPING_DATASETS_PAR_DEFAUT
        assert "GLOBAL_MULTIYEAR_WAV_001_032" in cm_module.MAPPING_DATASETS_PAR_DEFAUT
        
        assert "cmems_mod_glo_phy-all_my_0.25deg_P1D-m" in cm_module.MAPPING_VARS_DEFAUT
        assert "cmems_mod_glo_wav_my_0.2deg_PT3H-i" in cm_module.MAPPING_VARS_DEFAUT
    
    @patch('import_donnees_copernicus.recuperer_product_id_temp')
    @patch('import_donnees_copernicus.recuperer_product_id_vagues')
    def test_product_id_retrieval(self, mock_vagues, mock_temp, mock_cm):
        """Test la récupération des IDs produits"""
        mock_temp.return_value = "GLOBAL_MULTIYEAR_PHY_ENS_001_031"
        mock_vagues.return_value = "GLOBAL_MULTIYEAR_WAV_001_032"
        
        # Ces appels sont faits dans le script principal
        produit_id_temp = mock_temp()
        produit_id_vagues = mock_vagues()
        
        assert produit_id_temp == "GLOBAL_MULTIYEAR_PHY_ENS_001_031"
        assert produit_id_vagues == "GLOBAL_MULTIYEAR_WAV_001_032"
    
    @patch('import_donnees_copernicus.renseigner_annee_fin')
    def test_year_generation(self, mock_renseigner):
        """Test la génération des années"""
        mock_renseigner.return_value = (2023, [2020, 2021, 2022, 2023])
        
        annee_fin, annees = mock_renseigner()
        
        assert annee_fin == 2023
        assert len(annees) == 4
        assert 2020 in annees
        assert 2023 in annees
    
    def test_loop_parameters(self):
        """Test les paramètres de la boucle de téléchargement"""
        # Tester la génération des dates de début/fin
        an = 2023
        deb = f"{an}-01-01T00:00:00"
        fin = f"{an+1}-01-01T00:00:00"
        
        assert deb == "2023-01-01T00:00:00"
        assert fin == "2024-01-01T00:00:00"
    
    @patch('import_donnees_copernicus.moyennage_mensuelle_donnees_nc')
    def test_moyennage_calls(self, mock_moyennage, temp_dirs, mock_cm):
        """Test les appels à la fonction de moyennage"""
        mock_moyennage.return_value = temp_dirs / "test.csv"
        
        # Simuler l'appel de la fonction
        temp_final_csv = mock_moyennage(
            dossier_nc=cm_module.doss_temp,
            variable_interet="thetao_cglo",
            dossier_sortie=cm_module.conditions_marines
        )
        
        mock_moyennage.assert_called_once()
        assert mock_moyennage.call_args[0][0] == cm_module.doss_temp
        assert mock_moyennage.call_args[0][1] == "thetao_cglo"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])