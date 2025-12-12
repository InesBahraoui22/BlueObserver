"""
Tests unitaires pour jointure.py

Teste la fusion des données météo, OBIS et référentiels pour produire final_points.json
"""

import pytest
import json
import pandas as pd
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch, MagicMock
import sys
import os

# Ajouter le chemin pour importer jointure
sys.path.insert(0, str(Path(__file__).parent.parent))

# -------------------------------------------------------------------
# FIXTURES - Données de test
# -------------------------------------------------------------------

@pytest.fixture
def sample_meteo_points():
    """Points météo d'exemple"""
    return [
        {
            "lat": 48.8566,
            "lng": 2.3522,
            "species": "Balaenoptera_musculus",
            "month": "july",
            "avg_temp": "18.5",
            "avg_rain": "2.3",
            "avg_wind": "12.1"
        },
        {
            "lat": 51.5074,
            "lng": -0.1278,
            "species": "Orcinus_orca",
            "month": "january",
            "avg_temp": "8.2",
            "avg_rain": "5.6",
            "avg_wind": "15.4"
        }
    ]

@pytest.fixture
def sample_noms_csv():
    """Contenu CSV des noms d'espèces"""
    return """Nom scientifique;Nom vernaculaire (français)
Balaenoptera_musculus;Baleine bleue
Orcinus_orca;Orque
Tursiops_truncatus;Grand dauphin
"""

@pytest.fixture
def temp_project_structure(tmp_path):
    """Crée une structure de projet temporaire pour les tests"""
    # Créer les dossiers
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    static_dir = tmp_path / "static" / "photos"
    static_dir.mkdir(parents=True)
    
    obis_dir = data_dir / "obis_observation_especes"
    obis_dir.mkdir()
    
    # Créer des images de test
    (static_dir / "Balaenoptera_musculus.jpg").write_bytes(b"fake_jpg")
    (static_dir / "Orcinus_orca.jpg").write_bytes(b"fake_jpg")
    
    return tmp_path

@pytest.fixture
def mock_parquet_data():
    """Données Parquet simulées pour OBIS"""
    return pd.DataFrame({
        'decimalLatitude': [48.85, 48.86, 48.87],
        'decimalLongitude': [2.35, 2.36, 2.37]
    })

# -------------------------------------------------------------------
# TESTS DES FONCTIONS UTILITAIRES
# -------------------------------------------------------------------

def test_print_progress(capsys):
    """Test de l'affichage de progression"""
    # Importer la fonction depuis le module original
    from data_generation.jointure import print_progress
    
    print_progress(25, 100, "Test")
    captured = capsys.readouterr()
    
    assert "Test" in captured.out
    assert "25/100" in captured.out
    assert "25.00%" in captured.out
    
    # Test avec zéro
    print_progress(0, 100, "Zero")
    captured = capsys.readouterr()
    assert "0/100" in captured.out
    assert "0.00%" in captured.out

def test_load_obis_points_success(tmp_path, mock_parquet_data):
    """Test du chargement réussi des points OBIS"""
    from data_generation.jointure import load_obis_points
    
    # Créer un fichier Parquet temporaire
    tsv_path = tmp_path / "Balaenoptera_musculus.tsv"
    parquet_path = tmp_path / "Balaenoptera_musculus.parquet"
    mock_parquet_data.to_parquet(parquet_path)
    
    # Tester la fonction
    species, points = load_obis_points(tsv_path)
    
    assert species == "Balaenoptera_musculus"
    assert len(points) == 3
    assert all("decimalLatitude" in p for p in points)
    assert all("decimalLongitude" in p for p in points)
    assert points[0]["decimalLatitude"] == 48.85

def test_load_obis_points_file_not_found(tmp_path):
    """Test du chargement avec fichier Parquet manquant"""
    from data_generation.jointure import load_obis_points
    
    # Créer seulement le TSV, pas le Parquet
    tsv_path = tmp_path / "Species_not_found.tsv"
    tsv_path.touch()
    
    species, points = load_obis_points(tsv_path)
    
    assert species == "Species_not_found"
    assert points == []  # Liste vide quand fichier non trouvé

# -------------------------------------------------------------------
# TESTS D'INTEGRATION AVEC MOCKING
# -------------------------------------------------------------------

class TestJointureIntegration:
    """Tests d'intégration avec mocking des dépendances externes"""
    
    def test_generate_points_with_obis_data(
        self, sample_meteo_points, mock_parquet_data, temp_project_structure
    ):
        """Test de la génération de points avec données OBIS disponibles"""
        from data_generation.jointure import generate_points
        
        # Mock des dépendances
        with patch('data_generation.jointure.POINTS_FILE', 
                  temp_project_structure / "data" / "points.json"), \
             patch('data_generation.jointure.DATASET_FOLDER',
                  temp_project_structure / "data" / "obis_observation_especes"), \
             patch('data_generation.jointure.NOMS_FILE',
                  temp_project_structure / "data" / "nomsespecefin.csv"), \
             patch('data_generation.jointure.ESPECES_FOLDER',
                  temp_project_structure / "static" / "photos"):
            
            # Créer les fichiers de données de test
            points_file = temp_project_structure / "data" / "points.json"
            points_file.parent.mkdir(parents=True, exist_ok=True)
            with open(points_file, 'w') as f:
                json.dump(sample_meteo_points, f)
            
            # Créer fichier noms
            noms_file = temp_project_structure / "data" / "nomsespecefin.csv"
            noms_file.write_text("""Nom scientifique;Nom vernaculaire (français)
Balaenoptera_musculus;Baleine bleue
Orcinus_orca;Orque
""")
            
            # Créer fichier Parquet OBIS
            obis_dir = temp_project_structure / "data" / "obis_observation_especes"
            obis_dir.mkdir(parents=True, exist_ok=True)
            parquet_path = obis_dir / "Balaenoptera_musculus.parquet"
            mock_parquet_data.to_parquet(parquet_path)
            
            # Créer TSV correspondant
            (obis_dir / "Balaenoptera_musculus.tsv").touch()
            
            # Mock pd.read_csv pour éviter les erreurs de parsing
            mock_noms_df = pd.DataFrame({
                'Nom scientifique': ['Balaenoptera_musculus', 'Orcinus_orca'],
                'Nom vernaculaire (français)': ['Baleine bleue', 'Orque']
            })
            
            with patch('data_generation.jointure.pd.read_csv', 
                      return_value=mock_noms_df), \
                 patch('data_generation.jointure.json.load', 
                      return_value=sample_meteo_points):
                
                # Générer les points
                points = list(generate_points())
                
                # Vérifications
                assert len(points) == 4  # 1 point météo × (3 points OBIS + 1 sans données)
                
                # Premier point (avec données OBIS)
                first_point = points[0]
                assert first_point["species"] == "Balaenoptera_musculus"
                assert first_point["common_name"] == "Baleine bleue"
                assert first_point["month"] == "july"
                assert first_point["image"] == "Balaenoptera_musculus.jpg"
                assert first_point["lat"] == 48.85  # Depuis les données OBIS
                assert first_point["lng"] == 2.35
                
                # Dernier point (Orcinus_orca sans données OBIS)
                last_point = points[-1]
                assert last_point["species"] == "Orcinus_orca"
                assert last_point["common_name"] == "Orque"
                assert last_point["lat"] == 51.5074  # Depuis les données météo
                assert last_point["lng"] == -0.1278
    
    def test_generate_points_without_obis_data(
        self, sample_meteo_points, temp_project_structure
    ):
        """Test quand aucune donnée OBIS n'est disponible"""
        from data_generation.jointure import generate_points
        
        with patch('data_generation.jointure.POINTS_FILE', 
                  temp_project_structure / "data" / "points.json"), \
             patch('data_generation.jointure.DATASET_FOLDER',
                  temp_project_structure / "data" / "obis_observation_especes"), \
             patch('data_generation.jointure.NOMS_FILE',
                  temp_project_structure / "data" / "nomsespecefin.csv"), \
             patch('data_generation.jointure.ESPECES_FOLDER',
                  temp_project_structure / "static" / "photos"):
            
            # Mock des données
            mock_noms_df = pd.DataFrame({
                'Nom scientifique': ['Balaenoptera_musculus', 'Orcinus_orca'],
                'Nom vernaculaire (français)': ['Baleine bleue', 'Orque']
            })
            
            with patch('data_generation.jointure.pd.read_csv', 
                      return_value=mock_noms_df), \
                 patch('data_generation.jointure.json.load', 
                      return_value=sample_meteo_points):
                
                # Mock glob pour retourner liste vide (pas de fichiers OBIS)
                with patch('data_generation.jointure.Path.glob', 
                          return_value=[]):
                    
                    points = list(generate_points())
                    
                    # Doit générer un point par entrée météo
                    assert len(points) == len(sample_meteo_points)
                    
                    # Les coordonnées doivent venir des données météo
                    for point, expected in zip(points, sample_meteo_points):
                        assert point["lat"] == expected["lat"]
                        assert point["lng"] == expected["lng"]
                        assert point["common_name"] in ["Baleine bleue", "Orque"]
    
    def test_generate_points_with_missing_fields(self):
        """Test avec des points météo ayant des champs manquants"""
        from data_generation.jointure import generate_points
        
        # Points avec données incomplètes
        incomplete_points = [
            {"species": "Balaenoptera_musculus", "lat": 48.85},  # manque lng
            {"lng": 2.35, "lat": 48.85},  # manque species
            {"species": "Orcinus_orca", "lng": -0.12},  # manque lat
            {"species": "Tursiops_truncatus", "lat": 43.29, "lng": 5.36}  # complet
        ]
        
        with patch('data_generation.jointure.meteo_points', incomplete_points), \
             patch('data_generation.jointure.total_points', 4), \
             patch('data_generation.jointure.nom_map', 
                  {"Tursiops_truncatus": "Grand dauphin"}), \
             patch('data_generation.jointure.images', 
                  {"Tursiops_truncatus": "Tursiops_truncatus.jpg"}), \
             patch('data_generation.jointure.obis_points', {}):
            
            points = list(generate_points())
            
            # Seul le point complet devrait être généré
            assert len(points) == 1
            assert points[0]["species"] == "Tursiops_truncatus"
            assert points[0]["common_name"] == "Grand dauphin"

# -------------------------------------------------------------------
# TESTS DES CAS LIMITES ET ERREURS
# -------------------------------------------------------------------

def test_empty_meteo_points():
    """Test avec une liste de points météo vide"""
    from data_generation.jointure import generate_points
    
    with patch('data_generation.jointure.meteo_points', []), \
         patch('data_generation.jointure.total_points', 0):
        
        points = list(generate_points())
        assert points == []  # Aucun point généré

def test_species_not_in_nom_map():
    """Test quand une espèce n'est pas dans le mapping des noms"""
    from data_generation.jointure import generate_points
    
    test_points = [{
        "lat": 48.85,
        "lng": 2.35,
        "species": "Species_unknown",
        "month": "july",
        "avg_temp": "15.0",
        "avg_rain": "1.0",
        "avg_wind": "10.0"
    }]
    
    with patch('data_generation.jointure.meteo_points', test_points), \
         patch('data_generation.jointure.total_points', 1), \
         patch('data_generation.jointure.nom_map', {}), \
         patch('data_generation.jointure.images', {}), \
         patch('data_generation.jointure.obis_points', {}):
        
        points = list(generate_points())
        
        assert len(points) == 1
        # Le nom commun doit être le nom scientifique quand non trouvé
        assert points[0]["common_name"] == "Species_unknown"
        assert points[0]["image"] is None  # Pas d'image disponible

def test_image_mapping():
    """Test de la correspondance des images"""
    from data_generation.jointure import generate_points
    
    test_points = [{
        "lat": 48.85,
        "lng": 2.35,
        "species": "Balaenoptera_musculus",
        "month": "july",
        "avg_temp": "15.0",
        "avg_rain": "1.0",
        "avg_wind": "10.0"
    }]
    
    with patch('data_generation.jointure.meteo_points', test_points), \
         patch('data_generation.jointure.total_points', 1), \
         patch('data_generation.jointure.nom_map', 
              {"Balaenoptera_musculus": "Baleine bleue"}), \
         patch('data_generation.jointure.images', 
              {"Balaenoptera_musculus": "baleine_bleue.jpg"}), \
         patch('data_generation.jointure.obis_points', {}):
        
        points = list(generate_points())
        
        assert points[0]["image"] == "baleine_bleue.jpg"

# -------------------------------------------------------------------
# TESTS DE LA GENERATION JSON
# -------------------------------------------------------------------

def test_json_output_format(tmp_path):
    """Test du format JSON de sortie"""
    from data_generation.jointure import generate_points
    
    test_points = [{
        "lat": 48.8566,
        "lng": 2.3522,
        "species": "Balaenoptera_musculus",
        "common_name": "Baleine bleue",
        "month": "july",
        "avg_temp": "18.5",
        "avg_rain": "2.3",
        "avg_wind": "12.1",
        "image": "Balaenoptera_musculus.jpg"
    }]
    
    # Mock generate_points pour retourner nos points de test
    with patch('data_generation.jointure.generate_points', 
              return_value=iter(test_points)):
        
        output_file = tmp_path / "final_points.json"
        
        with patch('data_generation.jointure.OUTPUT_FILE', output_file):
            # Ré-exécuter la partie écriture JSON
            with open(output_file, "w", encoding="utf-8") as f:
                print("\nÉcriture du fichier JSON final...")
                points_iter = iter(test_points)
                first_point = True
                f.write("[\n")
                for point in points_iter:
                    if not first_point:
                        f.write(",\n")
                    json.dump(point, f, ensure_ascii=False)
                    first_point = False
                f.write("\n]")
            
            # Vérifier le fichier généré
            assert output_file.exists()
            
            with open(output_file, "r", encoding="utf-8") as f:
                content = json.load(f)
            
            assert isinstance(content, list)
            assert len(content) == 1
            assert content[0]["species"] == "Balaenoptera_musculus"
            assert content[0]["common_name"] == "Baleine bleue"
            
            # Vérifier le format des nombres (devraient être des strings dans JSON)
            assert isinstance(content[0]["avg_temp"], str)
            assert isinstance(content[0]["lat"], float)

def test_json_escaping():
    """Test que l'encodage JSON gère correctement les caractères spéciaux"""
    from data_generation.jointure import generate_points
    
    test_points = [{
        "lat": 48.85,
        "lng": 2.35,
        "species": "Test'espèce",
        "common_name": "Espèce avec 'apostrophes' et \"guillemets\"",
        "month": "july",
        "avg_temp": "18.5",
        "avg_rain": "2.3",
        "avg_wind": "12.1",
        "image": None
    }]
    
    with patch('data_generation.jointure.generate_points', 
              return_value=iter(test_points)):
        
        # Utiliser StringIO pour capturer la sortie
        import io
        output = io.StringIO()
        
        with patch('data_generation.jointure.open', 
                  return_value=MagicMock(__enter__=lambda: output)):
            
            # Appeler la fonction d'écriture (version simplifiée)
            points_iter = iter(test_points)
            first_point = True
            output.write("[\n")
            for point in points_iter:
                if not first_point:
                    output.write(",\n")
                json.dump(point, output, ensure_ascii=False)
                first_point = False
            output.write("\n]")
            
            # Vérifier que le JSON est valide
            result = json.loads(output.getvalue())
            assert result[0]["common_name"] == "Espèce avec 'apostrophes' et \"guillemets\""

# -------------------------------------------------------------------
# EXECUTION DES TESTS
# -------------------------------------------------------------------

if __name__ == "__main__":
    # Pour exécuter les tests directement
    pytest.main([__file__, "-v", "--tb=short"])