# 🌊 BlueObserver - Marine Species Observation Platform

**A web-based visualization tool for marine species distribution with environmental data integration**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/InesBahraoui22/BlueObserver?style=social)](https://github.com/InesBahraoui22/BlueObserver)

## 📋 Overview

BlueObserver is an interactive web application that visualizes marine species observations combined with oceanographic data (temperature, waves, wind, rain). The platform allows researchers and marine enthusiasts to explore species distribution patterns across different regions and seasons.

**Key Features:**
- 🗺️ **Interactive map** with D3.js visualization
- 🐋 **Species filtering** by region, month, and species type
- 📊 **Environmental data** integration (Copernicus Marine Service)
- 🔍 **Detailed observation cards** with wave height classification
- 📱 **Responsive design** for all devices

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- Git
- (Optional) Conda for virtual environment management

### Installation


### 1. Cloner et se déplacer
```bash
git clone https://github.com/InesBahraoui22/BlueObserver.git
cd BlueObserver
```

### 2. Installer les dépendances
```bash
# Créer l'environnement
python -m venv venv

# Activer (Mac/Linux)
source venv/bin/activate

# Activer (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Installer tout
pip install -r requirements.txt
```

### 3. Lancer l'application
```bash
python app.py
```
📍 **Ouvrir** : [http://localhost:5000](http://localhost:5000)

### 4. Tester (optionnel)
```bash
# Vérifier que tout marche
python tests/test_jointure.py --quick

# Lancer tous les tests
python -m pytest tests/ -v
```

## 🔧 Développement

### Générer les données
```bash
# Exécuter le script de fusion
python finalpoints/jointure.py

# Vérifier le fichier généré
ls -lh finalpoints/final_points.json
```

### Redémarrer l'application
```bash
# Toujours avec l'environnement activé
python app.py
# Appuyer sur Ctrl+C pour arrêter
```
Ines BAHRAOUI — 21901184
