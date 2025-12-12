import os
from pathlib import Path
import json
import pandas as pd

# --------- CONFIGURATION DES PATHS ---------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DATA_FOLDER = PROJECT_ROOT / "data"
ESPECES_FOLDER = PROJECT_ROOT / "static" / "photos"
DATASET_FOLDER = DATA_FOLDER / "obis_observation_especes"
POINTS_FILE = DATA_FOLDER / "points.json"
NOMS_FILE = DATA_FOLDER / "nomsespecefin.csv"
OUTPUT_FILE = DATA_FOLDER / "final_points.json"

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

IMAGE_EXTENSIONS = [".jpg", ".png", ".webp"]

# --------- FONCTIONS UTILITAIRES ---------
def print_progress(current, total, prefix="Progress"):
    percent = (current / total) * 100
    print(f"\r{prefix} : {current}/{total} ({percent:.2f}%)", end="")

def load_obis_points(tsv_path):
    """Charge les points OBIS d'un fichier TSV et retourne une liste de dictionnaires."""
    species_name = tsv_path.stem
    
    try:
        parquet_path = tsv_path.with_suffix('.parquet')
        df = pd.read_parquet(parquet_path, columns=['decimalLatitude','decimalLongitude'])
        df = df.dropna(subset=['decimalLatitude','decimalLongitude'])
        return species_name, df.to_dict(orient='records')
    except FileNotFoundError:
        return species_name, []

# --------- Charger les données ---------
# Points météo
with open(POINTS_FILE, "r", encoding="utf-8") as f:
    meteo_points = json.load(f)
total_points = len(meteo_points)

# Noms communs
df_noms = pd.read_csv(NOMS_FILE, sep=";", skiprows=1)
nom_map = dict(zip(df_noms['Nom scientifique'], df_noms['Nom vernaculaire (français)']))
print(f"{len(nom_map)} noms scientifiques chargés")

# Images
images = {}

for extension in IMAGE_EXTENSIONS:
    for p in ESPECES_FOLDER.glob(f"*{extension}"):
        images[p.stem] = p.name

# Points OBIS
obis_points = {}
for tsv_file in DATASET_FOLDER.glob("*.tsv"):
    species, points = load_obis_points(tsv_file)
    if points:
        obis_points[species] = points

# --------- Générateur de points ---------
def generate_points():
    print("Génération des points finaux avec enrichissement OBIS...")
    for i, p in enumerate(meteo_points, start=1):
        species = p.get('species')
        lat, lng = p.get('lat'), p.get('lng') or p.get('lon')
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
        for ob_point in obis_points.get(species, [base_point]):
            yield {**base_point, "lat": ob_point['decimalLatitude'], "lng": ob_point['decimalLongitude']} \
                  if 'decimalLatitude' in ob_point else ob_point

        # Progression
        if i % 1000 == 0 or i == total_points:
            print_progress(i, total_points, prefix="Traitement des points")


# --------- Écriture du JSON ---------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    print("\nÉcriture du fichier JSON final...")
    points_iter = generate_points()
    first_point = True
    f.write("[\n")
    for point in points_iter:
        if not first_point:
            f.write(",\n")
        json.dump(point, f, ensure_ascii=False)
        first_point = False
    f.write("\n]")

print(f"\n JSON final généré dans {OUTPUT_FILE}")
