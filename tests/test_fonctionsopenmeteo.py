import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import fonctionsopenmeteo as meteo_module

# Fixtures
@pytest.fixture
def mock_weather_response():
    """Mock d'une réponse OpenMeteo"""
    mock_response = Mock()
    
    # Mock de l'objet Daily
    mock_daily = Mock()
    
    # Dates simulées
    mock_daily.Time.return_value = int(datetime(2024, 1, 1).timestamp())
    mock_daily.TimeEnd.return_value = int(datetime(2024, 1, 31).timestamp())
    mock_daily.Interval.return_value = 86400  # 1 jour en secondes
    
    # Données simulées pour 31 jours
    n_days = 31
    mock_daily.Variables = Mock(side_effect=lambda i: Mock(
        ValuesAsNumpy=Mock(return_value=np.random.uniform(10, 20, n_days))
    ))
    
    mock_response.Daily.return_value = mock_daily
    
    return mock_response

@pytest.fixture
def sample_points():
    """Points d'exemple pour les tests"""
    return [
        {"lat": 48.8566, "lng": 2.3522, "species": "Balaenoptera musculus", "month": "january"},
        {"lat": 51.5074, "lng": -0.1278, "species": "Orcinus orca", "month": "july"},
    ]

class TestOpenMeteoFunctions:
    """Tests pour les fonctions OpenMeteo"""
    
    def test_month_ranges(self):
        """Test les plages de dates par mois"""
        month_ranges = meteo_module.month_ranges
        
        assert "january" in month_ranges
        assert "december" in month_ranges
        
        # Vérifier quelques mois spécifiques
        jan_start, jan_end = month_ranges["january"]
        assert jan_start == "2024-01-01"
        assert jan_end == "2024-01-31"
        
        feb_start, feb_end = month_ranges["february"]
        assert feb_start == "2024-02-01"
        assert feb_end == "2024-02-29"  # 2024 est bissextile
    
    @patch('fonctionsopenmeteo.openmeteo.weather_api')
    def test_get_weather_success(self, mock_weather_api, mock_weather_response):
        """Test la récupération des données météo réussie"""
        mock_weather_api.return_value = [mock_weather_response]
        
        result = meteo_module.get_weather(
            lat=48.8566,
            lon=2.3522,
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        
        # Vérifier que la fonction a été appelée
        mock_weather_api.assert_called_once()
        
        # Vérifier les clés dans le résultat
        assert "avg_temp" in result
        assert "avg_rain" in result
        assert "avg_wind" in result
        
        # Vérifier le format des valeurs
        assert isinstance(result["avg_temp"], str)
        assert "." in result["avg_temp"]  # Contient une décimale
    
    def test_weather_dataframe_construction(self):
        """Test la construction du DataFrame météo"""
        # Simuler des données Daily
        mock_daily = Mock()
        n_days = 7
        
        mock_daily.Time.return_value = int(datetime(2024, 1, 1).timestamp())
        mock_daily.TimeEnd.return_value = int(datetime(2024, 1, 7).timestamp())
        mock_daily.Interval.return_value = 86400
        
        # Données simulées
        temps_max = np.array([10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0])
        temps_min = np.array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0])
        pluie = np.array([0.0, 2.5, 0.0, 1.0, 3.0, 0.5, 0.0])
        vent = np.array([15.0, 20.0, 18.0, 22.0, 25.0, 19.0, 17.0])
        
        def mock_variables(i):
            mock_var = Mock()
            if i == 0:
                mock_var.ValuesAsNumpy.return_value = temps_max
            elif i == 1:
                mock_var.ValuesAsNumpy.return_value = temps_min
            elif i == 2:
                mock_var.ValuesAsNumpy.return_value = pluie
            elif i == 3:
                mock_var.ValuesAsNumpy.return_value = vent
            return mock_var
        
        mock_daily.Variables = mock_variables
        
        # Créer un mock response
        mock_response = Mock()
        mock_response.Daily.return_value = mock_daily
        
        with patch('fonctionsopenmeteo.openmeteo.weather_api', return_value=[mock_response]):
            result = meteo_module.get_weather(0, 0, "2024-01-01", "2024-01-07")
            
            # Vérifier les calculs
            avg_temp_expected = ((temps_max + temps_min) / 2).mean()
            avg_rain_expected = pluie.mean()
            avg_wind_expected = vent.mean()
            
            assert float(result["avg_temp"]) == pytest.approx(avg_temp_expected, 0.01)
            assert float(result["avg_rain"]) == pytest.approx(avg_rain_expected, 0.01)
            assert float(result["avg_wind"]) == pytest.approx(avg_wind_expected, 0.01)
    
    def test_date_range_generation(self):
        """Test la génération des plages de dates"""
        # Cette fonction est testée indirectement dans get_weather
        # mais on peut tester le calcul manuellement
        from datetime import datetime
        
        start_ts = int(datetime(2024, 1, 1).timestamp())
        end_ts = int(datetime(2024, 1, 31).timestamp())
        interval = 86400
        
        # Calculer le nombre de jours attendu
        expected_days = (end_ts - start_ts) // interval + 1
        assert expected_days == 31  # Janvier a 31 jours

if __name__ == "__main__":
    pytest.main([__file__, "-v"])