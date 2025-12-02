from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# --- CHEMIN ABSOLU VERS VOTRE FICHIER JSON ---
# IMPORTANT: Utilisez ce chemin ABSOLU uniquement pour le fichier de données
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # dossier contenant app.py
DATA_FILE_PATH = os.path.join(BASE_DIR, "finalpoints", "final_points.json")

# Charger les données au démarrage
with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
    points = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data/observations.json')
def observations_data():
    """
    Route dédiée pour servir votre fichier JSON
    depuis son emplacement ABSOLU sur votre système.
    """
    # Récupère le chemin du dossier (dirname) et le nom du fichier (basename)
    directory = os.path.dirname(DATA_FILE_PATH)
    filename = os.path.basename(DATA_FILE_PATH)
    
    # Utilise send_from_directory pour servir le fichier
    return send_from_directory(directory, filename, mimetype='application/json')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Route pour servir les autres fichiers statiques (JS, images) depuis le dossier 'static'."""
    # Assurez-vous que cette route sert bien les images de la même manière si vous les utilisez
    return send_from_directory('static', filename)

if __name__ == '__main__':
    print("Démarrage du serveur Flask pour BlueObserver...")
    app.run(debug=True)