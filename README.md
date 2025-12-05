### 🌊 BlueObserver — Carte interactive des espèces marines
## 📘 Projet de développement logiciel
BlueObserver est une application web interactive permettant d'explorer la biodiversité marine à partir de données ouvertes (OBIS, Copernicus, Open-Meteo).
# 🔗 Lien du site
(ajouter ici)
# 🧩 Structure du projet
# 📁 Organisation générale

BlueObserver/
├─ app.py
├─ finalpoints/
│   └─ final_points.json
├─ templates/
│   └─ index.html
├─ static/
│   ├─ styles.css
│   └─ images/
└─ README.md


# 📦 data_processing/
Scripts dédiés au traitement des données :
collect/ — récupération OBIS, Copernicus, Open-Meteo
cleaning/ — nettoyage, filtrage
integration/ — fusion et enrichissement
generate_final_points.py — génère final_points.json utilisé par la carte
# 🌐 webapp/
Application Flask :
app.py — serveur
templates/ — pages HTML
static/ — CSS, images, fichiers divers
finalpoints/final_points.json — observations affichées sur la carte

## Objectif principal
Créer une carte interactive touristique et scientifique affichant :
observations d’espèces marines (OBIS)
conditions environnementales (Copernicus)
données météo locales (Open-Meteo)
Chaque point sur la carte présente :
le nom complet de l’espèce (scientifique + commun)
la période d’observation
la température / salinité de l’eau
une photo
des informations touristiques ou contextuelles
# Filtres disponibles
L'utilisateur peut sélectionner :
une espèce
une région (ex. Méditerranée)
une saison (été, hiver…)
# Exemple de narration
Un utilisateur choisit dauphin et été →
La carte affiche les zones où l’eau est entre 20°C et 27°C, montrant que la Méditerranée orientale est optimale.
Il visualise directement où partir pour maximiser ses chances d’observation.
# Description du projet
BlueObserver combine des données scientifiques et touristiques afin de fournir :
une exploration intuitive de la biodiversité marine
une aide à la planification de voyages responsables
une valorisation de la donnée ouverte océanographique
## ⚙️ Installation
1. Cloner le dépôt
git clone https://github.com/InesBahraoui22/BlueObserver
cd BlueObserver
2. Créer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
3. Installer les dépendances
pip install -r requirements.txt
4. Lancer l’application
python app.py
# 🔗 Accéder ensuite à :
http://127.0.0.1:5000/

# Auteurs
Ines BAHRAOUI — 21901184
