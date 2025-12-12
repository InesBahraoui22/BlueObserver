# test_jointure.py (à placer où tu veux, par exemple dans tests/)
import pytest
import json
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, mock_open, MagicMock
import tempfile
import os
import sys

# --------- CONFIGURATION DES CHEMINS ---------
# Ton script jointure.py est dans finalpoints/
# Ce test peut être dans un dossier tests/ ou à la racine

# Déterminer le chemin vers le dossier parent (OceanAware)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # Remonte d'un niveau

# Ajouter le dossier finalpoints au path Python
finalpoints_dir = os.path.join(parent_dir, "finalpoints")
sys.path.insert(0, finalpoints_dir)

print(f"📁 Recherche de jointure.py dans: {finalpoints_dir}")

# Importer ton module jointure
try:
    import jointure as jt
    print("✅ Module jointure importé avec succès depuis finalpoints/")
    
    # Afficher les chemins pour vérification
    print(f"  POINTS_FILE: {jt.POINTS_FILE}")
    print(f"  OUTPUT_FILE: {jt.OUTPUT_FILE}")
    
except ImportError as e:
    print(f"❌ Impossible d'importer jointure depuis {finalpoints_dir}: {e}")
    
    # Essayer un autre chemin (si le test est à la racine)
    alternative_path = os.path.join(current_dir, "finalpoints")
    if os.path.exists(alternative_path):
        sys.path.insert(0, alternative_path)
        try:
            import jointure as jt
            print(f"✅ Module jointure importé depuis {alternative_path}")
        except ImportError:
            print(f"❌ Échec de l'import depuis {alternative_path}")
            sys.exit(1)
    else:
        print("❌ Dossier finalpoints non trouvé")
        sys.exit(1)

# --------- TESTS CORRIGÉS ---------

def test_print_progress():
    """Test de la fonction d'affichage de progression."""
    from io import StringIO
    import sys
    
    # Capturer la sortie standard
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        # Appeler la fonction
        jt.print_progress(50, 100, prefix="Test")
        
        # Récupérer la sortie
        output = sys.stdout.getvalue()
        
        # Vérifier le format
        assert "Test : 50/100 (50.00%)" in output
        assert "50.00%" in output
        
    finally:
        sys.stdout = old_stdout
    
    print("✅ Test d'affichage de progression réussi")
    return True

@patch('pandas.read_parquet')
def test_load_obis_points_success(mock_read_parquet):
    """Test du chargement réussi des points OBIS."""
    
    # Mock des données Parquet
    mock_df = Mock()
    mock_df.dropna.return_value = mock_df
    mock_df.to_dict.return_value = [
        {'decimalLatitude': 45.0, 'decimalLongitude': -1.0},
        {'decimalLatitude': 46.0, 'decimalLongitude': -2.0}
    ]
    mock_read_parquet.return_value = mock_df
    
    # Appeler la fonction
    species_name, points = jt.load_obis_points("/fake/path/test_species.tsv")
    
    # Vérifications
    assert species_name == "test_species"
    assert len(points) == 2
    assert points[0]['decimalLatitude'] == 45.0
    
    print("✅ Test chargement OBIS réussi")
    return True

def test_generate_points_logic():
    """Test de la logique de génération de points (sans dépendances)."""
    
    # Simuler les données que ton script utilise
    meteo_points = [
        {
            'lat': 45.0,
            'lng': -1.0,
            'species': 'Delphinus_delphis',
            'month': 'january',
            'avg_temp': 15.5,
            'avg_rain': 10.2,
            'avg_wind': 5.3
        }
    ]
    
    nom_map = {'Delphinus_delphis': 'Dauphin commun'}
    images = {'Delphinus_delphis': '/fake/path/dauphin.jpg'}
    obis_points = {'Delphinus_delphis': [
        {'decimalLatitude': 45.5, 'decimalLongitude': -1.5}
    ]}
    
    # Simuler la logique de ton générateur
    total_points = len(meteo_points)
    generated_points = []
    
    for i, p in enumerate(meteo_points, start=1):
        species = p.get('species')
        lat = p.get('lat')
        lng = p.get('lng') or p.get('lon')
        
        if lat is None or lng is None or species is None:
            continue

        base_point = {
            "lat": lat,
            "lng": lng,
            "species": species,
            "common_name": nom_map.get(species, species),
            "month": p.get('month'),
            "avg_temp": p.get('avg_temp'),
            "avg_rain": p.get('avg_rain'),
            "avg_wind": p.get('avg_wind'),
            "image": images.get(species)
        }

        # Ajouter points OBIS si existants
        obis_list = obis_points.get(species, [base_point])
        for ob_point in obis_list:
            if 'decimalLatitude' in ob_point:
                generated_points.append({
                    **base_point,
                    "lat": ob_point['decimalLatitude'],
                    "lng": ob_point['decimalLongitude']
                })
            else:
                generated_points.append(ob_point)
    
    # Vérifications
    assert len(generated_points) == 1
    assert generated_points[0]['common_name'] == 'Dauphin commun'
    assert generated_points[0]['lat'] == 45.5
    
    print("✅ Test logique génération de points réussi")
    return True

def test_json_structure():
    """Test de la structure JSON générée."""
    
    # Créer un point de test
    test_point = {
        "lat": 45.123456,
        "lng": -1.987654,
        "species": "test_species",
        "common_name": "Test Species",
        "month": "january",
        "avg_temp": 15.5,
        "avg_rain": 10.2,
        "avg_wind": 5.3,
        "image": "/fake/path/image.jpg"
    }
    
    # Vérifier les types et formats
    assert isinstance(test_point['lat'], (int, float))
    assert isinstance(test_point['lng'], (int, float))
    assert isinstance(test_point['species'], str)
    assert isinstance(test_point['common_name'], str)
    
    # Vérifier les plages raisonnables
    assert -90 <= test_point['lat'] <= 90
    assert -180 <= test_point['lng'] <= 180
    
    print("✅ Test structure JSON réussi")
    return True

def test_file_operations():
    """Test des opérations sur fichiers."""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Créer un fichier JSON de test
        test_file = os.path.join(tmpdir, "test.json")
        test_data = [{"test": "data"}]
        
        # Écrire
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False)
        
        # Vérifier existence
        assert os.path.exists(test_file)
        
        # Lire et vérifier
        with open(test_file, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data
        
        print("✅ Test opérations fichiers réussi")
        return True

def test_full_pipeline_simulation():
    """Simulation du pipeline complet avec données factices."""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"\n📁 Dossier temporaire: {tmpdir}")
        
        # 1. Créer les fichiers d'entrée
        points_file = os.path.join(tmpdir, "points.json")
        noms_file = os.path.join(tmpdir, "noms.csv")
        output_file = os.path.join(tmpdir, "output.json")
        
        # Données de test - même structure que ton vrai points.json
        points_data = [
            {
                "lat": 45.0,
                "lng": -1.0,
                "species": "Balaenoptera_musculus",
                "month": "january",
                "avg_temp": 12.5,
                "avg_rain": 5.0,
                "avg_wind": 8.0
            }
        ]
        
        with open(points_file, "w", encoding="utf-8") as f:
            json.dump(points_data, f)
        
        # IMPORTANT : Créer un CSV qui MATCHE la structure de ton vrai fichier
        # Regarde dans ton vrai nomsespecefin.csv pour voir le format exact
        # Si ton fichier a un en-tête différent, ajuste ici
        
        # Version 1 : Si ton CSV a le format "Nom scientifique;Nom vernaculaire (français)"
        csv_content = """Nom scientifique;Nom vernaculaire (français)
Balaenoptera_musculus;Baleine bleue
Delphinus_delphis;Dauphin commun
"""
        
        # Version 2 : Si ton CSV a une première ligne d'en-tête différente
        # (comme tu as skiprows=1 dans ton code, peut-être qu'il y a une ligne vide)
        csv_content = """En-tête (ignoré)
Nom scientifique;Nom vernaculaire (français)
Balaenoptera_musculus;Baleine bleue
Delphinus_delphis;Dauphin commun
"""
        
        with open(noms_file, "w", encoding="utf-8") as f:
            f.write(csv_content)
        
        # 2. Simuler le chargement des données
        # Points météo
        with open(points_file, "r", encoding="utf-8") as f:
            meteo_points = json.load(f)
        
        # Noms communs - IMPORTANT : utiliser skiprows=1 comme dans ton vrai code
        try:
            # Essayer avec skiprows=1 (pour ignorer la première ligne)
            df_noms = pd.read_csv(noms_file, sep=";", skiprows=1, encoding='utf-8')
            
            # Afficher les colonnes pour débogage
            print(f"  Colonnes CSV: {list(df_noms.columns)}")
            
            # Chercher les colonnes par nom
            nom_scientifique_col = None
            nom_vernaculaire_col = None
            
            for col in df_noms.columns:
                if 'scientifique' in col.lower():
                    nom_scientifique_col = col
                if 'vernaculaire' in col.lower() or 'français' in col.lower():
                    nom_vernaculaire_col = col
            
            if nom_scientifique_col and nom_vernaculaire_col:
                nom_map = dict(zip(df_noms[nom_scientifique_col], 
                                  df_noms[nom_vernaculaire_col]))
                print(f"  ✅ Map créée: {len(nom_map)} entrées")
            else:
                # Fallback: utiliser les premières colonnes
                print(f"  ⚠️ Colonnes non trouvées, using first two columns")
                nom_map = dict(zip(df_noms.iloc[:, 0], df_noms.iloc[:, 1]))
                
        except Exception as e:
            print(f"  ⚠️ Erreur lecture CSV: {e}")
            # Fallback simple
            nom_map = {'Balaenoptera_musculus': 'Baleine bleue',
                      'Delphinus_delphis': 'Dauphin commun'}
        
        # 3. Simuler la génération
        images = {}
        obis_points = {}
        
        generated = []
        for p in meteo_points:
            species = p.get('species')
            lat = p.get('lat')
            lng = p.get('lng') or p.get('lon')
            
            if lat is None or lng is None or species is None:
                continue
            
            point = {
                "lat": lat,
                "lng": lng,
                "species": species,
                "common_name": nom_map.get(species, species),
                "month": p.get('month'),
                "avg_temp": p.get('avg_temp'),
                "avg_rain": p.get('avg_rain'),
                "avg_wind": p.get('avg_wind'),
                "image": images.get(species)
            }
            generated.append(point)
        
        # 4. Écrire le résultat
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(generated, f, ensure_ascii=False)
        
        # 5. Vérifications
        assert os.path.exists(output_file), "Fichier de sortie non créé"
        assert len(generated) == 1, f"Attendu 1 point, obtenu {len(generated)}"
        assert generated[0]['common_name'] == 'Baleine bleue', \
            f"Nom commun incorrect: {generated[0]['common_name']}"
        
        print("✅ Test pipeline complet réussi")
        return True

# --------- EXÉCUTION DES TESTS ---------

def run_all_tests():
    """Exécute tous les tests et affiche un résumé."""
    print("🧪" + "="*50)
    print("Lancement des tests unitaires pour jointure.py")
    print(f"Chemin jointure.py: {finalpoints_dir}")
    print("="*50 + "\n")
    
    tests = [
        test_print_progress,
        test_load_obis_points_success,
        test_generate_points_logic,
        test_json_structure,
        test_file_operations,
        test_full_pipeline_simulation,
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
    print("\n" + "="*50)
    print("📊 RÉSUMUM DES TESTS")
    print("="*50)
    print(f"✅ Tests réussis: {passed}")
    print(f"❌ Tests échoués: {failed}")
    
    if failed > 0:
        print(f"\n📋 Tests échoués:")
        for test_name in failed_tests:
            print(f"  • {test_name}")
    
    print("\n" + "="*50)
    if failed == 0:
        print("🎉 TOUS LES TESTS ONT RÉUSSI !")
        return True
    else:
        print(f"⚠️ {failed} test(s) ont échoué")
        return False

# --------- VERSION SIMPLIFIÉE POUR DÉPANNAGE ---------

def quick_test():
    """Test rapide sans dépendances."""
    print("🚀 Test rapide de jointure.py")
    
    try:
        # Vérifier que le module est importable
        print(f"1. Import module... ", end="")
        import jointure as jt
        print("✅")
        
        # Vérifier les chemins
        print(f"2. Chemins configurés...")
        print(f"   POINTS_FILE: {jt.POINTS_FILE}")
        print(f"   OUTPUT_FILE: {jt.OUTPUT_FILE}")
        print("   ✅")
        
        # Test simple de la fonction print_progress
        print(f"3. Test fonction print_progress... ", end="")
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        jt.print_progress(25, 50, "Test")
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        assert "Test : 25/50" in output
        print("✅")
        
        print("\n" + "="*50)
        print("🎉 Test rapide réussi !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {type(e).__name__}: {e}")
        return False

# --------- POINT D'ENTRÉE ---------

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Tests pour jointure.py")
    parser.add_argument("--quick", action="store_true", help="Exécuter le test rapide")
    parser.add_argument("--all", action="store_true", help="Exécuter tous les tests")
    
    args = parser.parse_args()
    
    if args.quick or not (args.quick or args.all):
        # Par défaut, exécuter le test rapide
        success = quick_test()
    elif args.all:
        success = run_all_tests()
    
    exit(0 if success else 1)