from flask import Flask, render_template, send_from_directory
import os
import json # <-- Ajout de l'importation de la librairie json

app = Flask(__name__)

# --- CHEMIN ABSOLU VERS VOTRE FICHIER JSON ---
# IMPORTANT: Utilisez ce chemin ABSOLU uniquement pour le fichier de données
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # dossier contenant app.py
DATA_FILE_PATH = os.path.join(BASE_DIR, "finalpoints", "final_points.json")

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
    Route dédiée pour servir le fichier JSON de données.
    """
    # Récupère le chemin du dossier (dirname) et le nom du fichier (basename)
    directory = os.path.dirname(DATA_FILE_PATH)
    filename = os.path.basename(DATA_FILE_PATH)
    
    # Utilise send_from_directory pour servir le fichier
    return send_from_directory(directory, filename, mimetype='application/json')

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