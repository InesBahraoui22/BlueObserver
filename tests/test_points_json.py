import pytest
import tempfile
import json
import pandas as pd
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import points_json as points_module

# Fixtures
@pytest.fixture
def sample_obis_tsv(tmp_path):
    """Créer un fichier TSV OBIS temporaire"""
    tsv_path = tmp_path / "Balaenoptera_musculus.tsv"
    
    data = {
        'decimalLongitude': [-10.5, 2.3522, 15.3],
        'decimalLatitude': [45.2, 48.8566, 55.7],
        'eventDate': ['2023-07-15T12:00:00Z', '2023-01-20T10:30:00Z', None]
    }
    df = pd.DataFrame(data)
    df.to_csv(tsv_path, sep='\t', index=False)
    
    return str(tsv_path)

@pytest.fixture
def existing_points_file(tmp_path):
    """Créer un fichier points.json existant"""
    points_file = tmp_path / "points.json"
    
    existing_data = [
        {
            "lat": 48.8566,
            "lng": 2.3522,
            "species": "Balaenoptera musculus",
            "month": "january",
            "avg_temp": "10.5",
            "avg_rain": "2.3",
            "avg_wind": "15.2"
        }
    ]
    
    with open(points_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f)
    
    return str(points_file)

@pytest.fixture
def mock_weather_response():
    """Mock d'une réponse OpenMeteo"""
    mock_response = Mock()
    mock_daily = Mock()
    
    mock_daily.Time.return_value = int(pd.Timestamp('2024-01-01').timestamp())
    mock_daily.TimeEnd.return_value = int(pd.Timestamp('2024-01-31').timestamp())
    mock_daily.Interval.return_value = 86400
    
    # Données simulées
    mock_daily.Variables = Mock(side_effect=lambda i: Mock(
        ValuesAsNumpy=Mock(return_value=np.full(31, 10.0 + i))  # Différentes valeurs pour chaque variable
    ))
    
    mock_response.Daily.return_value = mock_daily
    return mock_response

class TestPointsJson:
    """Tests pour le script points.json"""
    
    def test_path_creation(self):
        """Test la création des chemins"""
        # Vérifier que les chemins sont définis
        assert hasattr(points_module, 'OBIS_DIR')
        assert hasattr(points_module, 'OUTPUT_DIR')
        assert hasattr(points_module, 'OUTPUT_JSON')
        
        # Vérifier que DATA_DIR est un Path
        assert isinstance(points_module.DATA_DIR, Path)
    
    def test_month_ranges_completeness(self):
        """Test la complétude des plages de mois"""
        month_ranges = points_module.month_ranges
        
        # Vérifier tous les mois
        months = ["january", "february", "march", "april", "may", "june",
                 "july", "august", "september", "october", "november", "december"]
        
        for month in months:
            assert month in month_ranges
        
        # Vérifier quelques plages spécifiques
        assert month_ranges["january"] == ("2024-01-01", "2024-01-31")
        assert month_ranges["february"] == ("2024-02-01", "2024-02-29")
        assert month_ranges["december"] == ("2024-12-01", "2024-12-31")