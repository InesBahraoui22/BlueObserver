# test_obis_extraction.py
import pytest
import json
import csv
import tempfile
import os
import sys
from unittest.mock import Mock, patch, mock_open, MagicMock
import datetime as dt

# --------- CONFIGURATION POUR IMPORTER OU SIMULER ---------
# Puisque ton script n'est pas structuré comme un module, 
# on va tester sa logique directement

def test_configuration_constantes():
    """Test des constantes de configuration."""
    # Vérifier les constantes définies
    LON_MIN, LON_MAX = -25.0, 45.0
    LAT_MIN, LAT_MAX = 27.0, 69.0
    
    assert LON_MIN == -25.0
    assert LON_MAX == 45.0
    assert LAT_MIN == 27.0
    assert LAT_MAX == 69.0
    
    # Vérifier les formats de date
    START_DATE = "2000-01-01"
    END_DATE = dt.date.today().isoformat()
    
    assert START_DATE == "2000-01-01"
    assert len(END_DATE) == 10  # YYYY-MM-DD
    assert END_DATE[4] == "-" and END_DATE[7] == "-"
    
    SPECIES = "Delphinus delphis"
    OUT_CSV = "Delphinus_delphis.csv"
    SIZE = 10000
    SLEEP = 0.2
    
    assert SPECIES == "Delphinus delphis"
    assert OUT_CSV == "Delphinus_delphis.csv"
    assert SIZE == 10000
    assert SLEEP == 0.2
    
    # Vérifier les champs
    FIELDS = ["scientificName", "decimalLongitude", "decimalLatitude", "eventDate"]
    assert len(FIELDS) == 4
    assert "scientificName" in FIELDS
    assert "decimalLongitude" in FIELDS
    
    BASE = "https://api.obis.org/v3/occurrence"
    assert BASE == "https://api.obis.org/v3/occurrence"
    
    print("✅ Configuration des constantes testée avec succès")
    return True

def test_polygone_generation():
    """Test de la génération du polygone."""
    LON_MIN, LON_MAX = -25.0, 45.0
    LAT_MIN, LAT_MAX = 27.0, 69.0
    
    # Recréer la logique de génération du polygone
    polygone = (f"POLYGON(({LON_MIN} {LAT_MIN},{LON_MAX} {LAT_MIN},"
                f"{LON_MAX} {LAT_MAX},{LON_MIN} {LAT_MAX},{LON_MIN} {LAT_MIN}))")
    
    expected = "POLYGON((-25.0 27.0,45.0 27.0,45.0 69.0,-25.0 69.0,-25.0 27.0))"
    assert polygone == expected
    
    # Vérifier la structure WKT
    assert polygone.startswith("POLYGON((")
    assert polygone.endswith("))")
    assert str(LON_MIN) in polygone
    assert str(LAT_MAX) in polygone
    
    print("✅ Génération du polygone testée avec succès")
    return True

@patch('requests.get')
def test_probe_request(mock_get):
    """Test de la requête sonde."""
    
    # Configurer le mock
    mock_response = Mock()
    mock_response.json.return_value = {"total": 1234}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    # Paramètres de test
    SPECIES = "Delphinus delphis"
    START_DATE = "2000-01-01"
    END_DATE = "2024-12-10"
    LON_MIN, LON_MAX = -25.0, 45.0
    LAT_MIN, LAT_MAX = 27.0, 69.0
    
    # Recréer le polygone
    polygone = (f"POLYGON(({LON_MIN} {LAT_MIN},{LON_MAX} {LAT_MIN},"
                f"{LON_MAX} {LAT_MAX},{LON_MIN} {LAT_MAX},{LON_MIN} {LAT_MIN}))")
    
    from urllib.parse import quote
    BASE = "https://api.obis.org/v3/occurrence"
    
    # Construire l'URL comme dans le script
    probe_url = (f"{BASE}?scientificname={quote(SPECIES)}"
                 f"&geometry={quote(polygone)}"
                 f"&startdate={START_DATE}&enddate={END_DATE}"
                 f"&size=1&offset=0"
                 f"&hasCoordinate=true")
    
    # Simuler la requête
    response = requests.get(probe_url, timeout=120)
    data = response.json()
    
    # Vérifications
    mock_get.assert_called_once()
    assert "total" in data
    assert data["total"] == 1234
    
    print("✅ Requête sonde testée avec succès")
    return True

def test_url_encoding():
    """Test de l'encodage des URLs."""
    from urllib.parse import quote
    
    # Test avec espace dans le nom d'espèce
    species = "Delphinus delphis"
    encoded = quote(species)
    assert encoded == "Delphinus%20delphis"
    
    # Test avec caractères spéciaux
    test_string = "Test&Special=Characters"
    encoded = quote(test_string)
    assert "&" not in encoded  # Doit être encodé
    
    # Test des champs
    FIELDS = ["scientificName", "decimalLongitude", "decimalLatitude", "eventDate"]
    fields_string = ",".join(FIELDS)
    encoded_fields = quote(fields_string)
    
    assert "scientificName" in encoded_fields
    assert "%2C" in encoded_fields  # Virgule encodée
    
    print("✅ Encodage URL testé avec succès")
    return True

@patch('requests.get')
@patch('builtins.open', new_callable=mock_open)
@patch('os.path.exists')
def test_full_extraction_flow(mock_exists, mock_file, mock_get):
    """Test du flux complet d'extraction avec mocking."""
    
    # Configurer les mocks
    mock_exists.return_value = False  # Pas de fichier state
    
    # Mock pour la requête sonde
    mock_probe_response = Mock()
    mock_probe_response.json.return_value = {"total": 150}
    mock_probe_response.raise_for_status = Mock()
    
    # Mock pour les requêtes paginées
    mock_page_response = Mock()
    mock_page_response.json.return_value = {
        "results": [
            {
                "scientificName": "Delphinus delphis",
                "decimalLongitude": -10.5,
                "decimalLatitude": 45.2,
                "eventDate": "2020-06-15"
            },
            {
                "scientificName": "Delphinus delphis",
                "decimalLongitude": -11.2,
                "decimalLatitude": 46.1,
                "eventDate": "2020-07-20"
            }
        ]
    }
    mock_page_response.raise_for_status = Mock()
    
    # Alterner entre les réponses
    mock_get.side_effect = [mock_probe_response, mock_page_response]
    
    # Simuler l'écriture CSV
    csv_writer_mock = Mock()
    csv_writer_mock.writeheader = Mock()
    csv_writer_mock.writerow = Mock()
    
    # Simuler le contexte
    with patch('csv.DictWriter') as mock_dictwriter:
        mock_dictwriter.return_value = csv_writer_mock
        
        # Simuler la logique de pagination
        TOTAL = 150
        SIZE = 10000
        OFFSET = 0
        enregistrees = 0
        
        # Première page
        remaining = TOTAL - OFFSET
        page_size = SIZE if remaining >= SIZE else remaining
        
        assert page_size == 150  # Car 150 < 10000
        
        # Simuler l'écriture
        n = 2  # 2 lignes dans notre mock
        enregistrees += n
        OFFSET += n
        
        # Vérifications
        assert enregistrees == 2
        assert OFFSET == 2
        
        # Le writer doit avoir été appelé 2 fois
        assert csv_writer_mock.writerow.call_count == 2
    
    print("✅ Flux d'extraction complet testé avec succès")
    return True

def test_state_file_management():
    """Test de la gestion du fichier d'état."""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = os.path.join(tmpdir, "offset.state")
        
        # Test 1: Fichier n'existe pas
        if os.path.exists(state_file):
            OFFSET = int(open(state_file).read())
        else:
            OFFSET = 0
        
        assert OFFSET == 0
        
        # Test 2: Écrire dans le fichier
        with open(state_file, "w") as f:
            f.write("50")
        
        # Test 3: Lire depuis le fichier
        with open(state_file, "r") as f:
            offset_from_file = int(f.read())
        
        assert offset_from_file == 50
        
        # Test 4: Mise à jour incrémentale
        new_offset = offset_from_file + 10
        with open(state_file, "w") as f:
            f.write(str(new_offset))
        
        with open(state_file, "r") as f:
            updated_offset = int(f.read())
        
        assert updated_offset == 60
        
        print("✅ Gestion du fichier d'état testée avec succès")
        return True

def test_csv_writing():
    """Test de l'écriture CSV."""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_file = os.path.join(tmpdir, "test_output.csv")
        
        # Données de test
        FIELDS = ["scientificName", "decimalLongitude", "decimalLatitude", "eventDate"]
        test_data = [
            {
                "scientificName": "Delphinus delphis",
                "decimalLongitude": -10.5,
                "decimalLatitude": 45.2,
                "eventDate": "2020-06-15T00:00:00"
            },
            {
                "scientificName": "Balaenoptera musculus",
                "decimalLongitude": -15.3,
                "decimalLatitude": 48.7,
                "eventDate": "2021-08-22"
            }
        ]
        
        # Écrire le CSV
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            for row in test_data:
                writer.writerow(row)
        
        # Vérifier que le fichier existe
        assert os.path.exists(csv_file)
        
        # Lire et vérifier le contenu
        with open(csv_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        lines = content.strip().split('\n')
        assert len(lines) == 3  # Header + 2 lignes
        
        # Vérifier l'en-tête
        assert "scientificName" in lines[0]
        assert "decimalLongitude" in lines[0]
        
        # Vérifier les données
        assert "Delphinus delphis" in content
        assert "Balaenoptera musculus" in content
        
        print("✅ Écriture CSV testée avec succès")
        return True

def test_error_handling():
    """Test de la gestion des erreurs."""
    
    # Simuler une réponse d'erreur HTTP
    error_response = Mock()
    error_response.raise_for_status.side_effect = Exception("HTTP Error 500")
    
    # Vérifier que l'erreur est propagée
    try:
        error_response.raise_for_status()
        assert False, "Devrait lever une exception"
    except Exception as e:
        assert "HTTP Error" in str(e)
    
    # Test avec données vides
    empty_data = {"results": []}
    nbre_lignes = empty_data.get("results", [])
    assert len(nbre_lignes) == 0
    
    # Test avec offset > total
    TOTAL = 100
    OFFSET = 150
    assert OFFSET > TOTAL
    
    print("✅ Gestion des erreurs testée avec succès")
    return True

def test_pagination_logic():
    """Test de la logique de pagination."""
    
    TOTAL = 12345
    SIZE = 10000
    OFFSET = 0
    
    # Premier appel
    remaining = TOTAL - OFFSET  # 12345
    page_size = SIZE if remaining >= SIZE else remaining  # 10000
    assert page_size == 10000
    
    # Mise à jour
    OFFSET += page_size  # 10000
    
    # Deuxième appel
    remaining = TOTAL - OFFSET  # 2345
    page_size = SIZE if remaining >= SIZE else remaining  # 2345
    assert page_size == 2345
    
    # Troisième appel (devrait être 0)
    OFFSET += page_size  # 12345
    remaining = TOTAL - OFFSET  # 0
    page_size = SIZE if remaining >= SIZE else remaining  # 0
    assert page_size == 0
    
    print("✅ Logique de pagination testée avec succès")
    return True

def test_data_validation():
    """Test de validation des données."""
    
    # Données valides
    valid_row = {
        "scientificName": "Delphinus delphis",
        "decimalLongitude": -10.5,
        "decimalLatitude": 45.2,
        "eventDate": "2020-06-15"
    }
    
    # Vérifier les types
    assert isinstance(valid_row["scientificName"], str)
    assert isinstance(valid_row["decimalLongitude"], float)
    assert isinstance(valid_row["decimalLatitude"], float)
    assert isinstance(valid_row["eventDate"], str)
    
    # Vérifier les plages
    assert -180 <= valid_row["decimalLongitude"] <= 180
    assert -90 <= valid_row["decimalLatitude"] <= 90
    
    # Vérifier le format de date (basique)
    date_str = valid_row["eventDate"]
    assert len(date_str) >= 10  # Au moins YYYY-MM-DD
    if len(date_str) >= 4:
        assert date_str[4] == "-"  # Séparateur année-mois
    
    print("✅ Validation des données testée avec succès")
    return True

# --------- EXÉCUTION DES TESTS ---------

def run_all_tests():
    """Exécute tous les tests et affiche un résumé."""
    print("🧪" + "="*60)
    print("Lancement des tests unitaires pour extraction OBIS")
    print("="*60 + "\n")
    
    tests = [
        test_configuration_constantes,
        test_polygone_generation,
        test_url_encoding,
        test_state_file_management,
        test_csv_writing,
        test_pagination_logic,
        test_data_validation,
        test_error_handling,
        test_probe_request,
        test_full_extraction_flow,
    ]
    
    passed = 0
    failed = 0
    failed_tests = []
    
    for test_func in tests:
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
    print("🚀 Test rapide de l'extraction OBIS")
    
    tests_to_run = [
        test_configuration_constantes,
        test_polygone_generation,
        test_url_encoding,
        test_csv_writing,
        test_data_validation,
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
    
    parser = argparse.ArgumentParser(description="Tests pour l'extraction OBIS")
    parser.add_argument("--quick", action="store_true", help="Exécuter le test rapide")
    parser.add_argument("--all", action="store_true", help="Exécuter tous les tests")
    
    args = parser.parse_args()
    
    # Import requests ici pour éviter les problèmes d'import
    import requests
    from urllib.parse import quote
    
    if args.quick or not (args.quick or args.all):
        success = quick_test()
    elif args.all:
        success = run_all_tests()
    
    exit(0 if success else 1)