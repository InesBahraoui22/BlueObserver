import os
import json
import pandas as pd

# --------- 1️⃣ CONFIGURATION DES PATHS ---------
ESPECES_FOLDER = "/Users/ines/Desktop/M1/OceanAware/especes"
DATASET_FOLDER = "/Users/ines/Desktop/M1/OceanAware/dataset"
POINTS_FILE = "/Users/ines/Desktop/M1/OceanAware/meteo/_site/data/points.json"
NOMS_FILE = "/Users/ines/Desktop/M1/OceanAware/especes/nomsespecefin.csv"
OUTPUT_FILE = "/Users/ines/Desktop/M1/OceanAware/finalpoints/final_points.json"

# --------- FONCTIONS UTILITAIRES ---------
def print_progress(current, total, prefix="Progress"):
    percent = (current / total) * 100
    print(f"\r{prefix} : {current}/{total} ({percent:.2f}%)", end="")

def load_obis_points(tsv_path):
    """Charge les points OBIS d'un fichier TSV et retourne une liste de dictionnaires."""
    species_name = os.path.splitext(os.path.basename(tsv_path))[0]
    try:
        df = pd.read_parquet(tsv_path.replace(".tsv", ".parquet"), columns=['decimalLatitude','decimalLongitude'])
        df = df.dropna(subset=['decimalLatitude','decimalLongitude'])
        return species_name, df.to_dict(orient='records')
    except Exception as e:
        print(f"⚠ Impossible de charger {tsv_path}: {e}")
        return species_name, []

# --------- 2️⃣ Charger les données ---------
# Points météo
with open(POINTS_FILE, "r", encoding="utf-8") as f:
    meteo_points = json.load(f)
total_points = len(meteo_points)

# Noms communs
df_noms = pd.read_csv(NOMS_FILE, sep=";", skiprows=1)
nom_map = dict(zip(df_noms['Nom scientifique'], df_noms['Nom vernaculaire (français)']))
print(f"✅ {len(nom_map)} noms scientifiques chargés")

# Images
images = {os.path.splitext(f)[0]: os.path.join(ESPECES_FOLDER, f)
          for f in os.listdir(ESPECES_FOLDER) if f.lower().endswith(".jpg")}

# Points OBIS
obis_points = {}
for f in os.listdir(DATASET_FOLDER):
    if f.lower().endswith(".tsv"):
        tsv_path = os.path.join(DATASET_FOLDER, f)
        species, points = load_obis_points(tsv_path)
        if points:
            obis_points[species] = points

# --------- 3️⃣ Générateur de points ---------
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

# --------- 4️⃣ Écriture du JSON ---------
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

print(f"\n✅ JSON final généré dans {OUTPUT_FILE}")
