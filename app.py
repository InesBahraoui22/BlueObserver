from flask import Flask, render_template, send_from_directory, jsonify
import os
import json # <-- Ajout de l'importation de la librairie json
import csv

app = Flask(__name__)

# --- CHEMIN ABSOLU VERS VOTRE FICHIER JSON ---
# IMPORTANT: Utilisez ce chemin ABSOLU uniquement pour le fichier de données
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # dossier contenant app.py
DATA_FILE_PATH = os.path.join(BASE_DIR, "data", "final_points.json")

# Charger les données au démarrage
# S'assure que le fichier existe avant de le charger
if os.path.exists(DATA_FILE_PATH):
    try:
        with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
            points = json.load(f)
        print(f"Données chargées avec succès depuis: {DATA_FILE_PATH}")
    except json.JSONDecodeError:
        print(f"Erreur de décodage JSON dans {DATA_FILE_PATH}")
        points = {}
else:
    print(f"Fichier de données non trouvé à l'emplacement: {DATA_FILE_PATH}. Les points seront vides.")
    points = {}

@app.route('/about') #about us
def about():
    """Route pour la page 'À propos de nous'."""
    return render_template('about.html')

@app.route('/')
def index():
    """Route principale affichant la page HTML."""
    return render_template('index.html')


@app.route('/data/observations.json')
def observations_data():
    """
    Fusionne final_points.json avec moyennes_mensuelles_par_GPS_VHM0.csv.
    Gère les fichiers Git LFS.
    """
    # --- 1. Charger le JSON principal ---
    directory = os.path.dirname(DATA_FILE_PATH)
    filename = os.path.basename(DATA_FILE_PATH)
    
    with open(os.path.join(directory, filename), "r", encoding="utf-8") as f:
        observations = json.load(f)
    
    print(f"Observations JSON chargées: {len(observations)}")
    
    # --- 2. Charger le CSV des vagues ---
    csv_path = os.path.join(directory, "conditions_marines", "moyennes_mensuelles_par_GPS_VHM0.csv")
    
    waves = {}
    
    if os.path.exists(csv_path):
        print(f"Tentative de lecture du CSV (peut être Git LFS)...")
        
        with open(csv_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            
            if first_line.startswith('version https://git-lfs.github.com/spec/v1'):
                print("❌ Fichier Git LFS détecté ! Ce n'est pas le vrai CSV.")
                print("   Solution 1: Téléchargez le vrai CSV depuis GitHub")
                print("   Solution 2: Exécutez 'git lfs pull' dans le terminal")
                print("   Solution 3: Utilisez des données factices pour tester")
                
                # Créer des données factices pour tester
                waves = create_fake_wave_data(observations)
                
            else:
                # C'est un vrai CSV, lire normalement
                f.seek(0)  # Retourner au début du fichier
                reader = csv.DictReader(f)
                print(f"Colonnes CSV réelles: {reader.fieldnames}")
                
                # ... votre code de lecture CSV normal ...
    
    # --- 3. Fusion JSON + CSV ---
    enriched = []
    
    for obs in observations:
        enriched_obs = obs.copy()
        
        # Ajouter les données de vagues (factices ou réelles)
        if obs.get('lat') and obs.get('lng'):
            lat = round(float(obs['lat']), 2)
            lng = round(float(obs['lng']), 2)
            
            # Chercher dans waves ou générer aléatoire
            key = (lat, lng, obs.get('month', '').lower())
            
            if key in waves:
                wave_height = waves[key]
            else:
                # Valeur factice basée sur la latitude
                wave_height = 0.5 + (abs(lat) / 90) * 2.5  # 0.5 à 3.0 m
            
            enriched_obs["avg_wave"] = wave_height
            enriched_obs["avg_wave_height"] = wave_height
            enriched_obs["VHM0"] = wave_height
        
        enriched.append(enriched_obs)
    
    print(f"Observations enrichies: {len(enriched)}")
    return jsonify(enriched)

def create_fake_wave_data(observations):
    """Crée des données factices de vagues pour tester"""
    waves = {}
    print("Création de données factices de vagues...")
    
    for obs in observations:
        try:
            lat = round(float(obs.get('lat', 0)), 2)
            lng = round(float(obs.get('lng', 0)), 2)
            month = obs.get('month', '').lower()
            
            # Générer une hauteur de vague réaliste
            # En Atlantique Nord : plus de vagues en hiver
            if month in ['december', 'january', 'february']:
                base_height = 2.0
            elif month in ['march', 'april', 'october', 'november']:
                base_height = 1.5
            else:  # été
                base_height = 0.8
            
            # Variation basée sur la longitude
            if lng < -10:  # Océan Atlantique
                base_height *= 1.3
            elif lng < 5:  # Golfe de Gascogne
                base_height *= 1.1
            else:  # Méditerranée
                base_height *= 0.7
            
            # Ajouter un peu d'aléatoire
            import random
            wave_height = round(base_height + random.uniform(-0.3, 0.3), 2)
            
            waves[(lat, lng, month)] = wave_height
            
        except:
            continue
    
    print(f"Données factices créées: {len(waves)} entrées")
    return waves

@app.route('/static/<path:filename>')
def serve_static(filename):
    """
    Route pour servir TOUS les fichiers statiques (JS, CSS, Images/Photos, etc.) 
    depuis le dossier 'static'. 
    
    C'est cette route qui rend vos photos accessibles publiquement.
    """
    # Flask utilise par défaut le dossier 'static', mais cette implémentation 
    # explicite assure la compatibilité.
    return send_from_directory('static', filename)

if __name__ == '__main__':
    print("Démarrage du serveur Flask pour BlueObserver...")
    # Assurez-vous d'avoir un dossier 'static' contenant vos photos.
    # Si les photos sont dans 'static/images', elles seront accessibles via '/static/images/nom_photo.jpg'
    app.run(debug=True)