import pandas as pd
import json
import os
from glob import glob

# --- PATHS ---
DATASET_DIR = "dataset"
EXCEL_FILE = os.path.join(DATASET_DIR, "nomsespece.xlsx")
METEO_FILE = "meteo/points.json"
OUTPUT_JSON = "_site/data/points.json"

# --- Charger Excel (species → commonName) ---
species_info = pd.read_excel(EXCEL_FILE)

if "species" not in species_info.columns:
    raise ValueError("❌ La colonne 'species' manque dans le fichier Excel.")

# --- Charger météo ---
if os.path.exists(METEO_FILE):
    with open(METEO_FILE, "r", encoding="utf-8") as f:
        meteo_data = json.load(f)
    meteo_df = pd.DataFrame(meteo_data)
else:
    raise FileNotFoundError("❌ Le fichier meteo/points.json est introuvable.")

required_meteo_cols = {"lat", "lng", "species", "month"}
if not required_meteo_cols.issubset(meteo_df.columns):
    raise ValueError("❌ Le JSON météo n'a pas les colonnes nécessaires.")

# --- Charger ancienne sauvegarde (reprise automatique) ---
if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        existing_points = json.load(f)
else:
    existing_points = []

already_done = {
    (p["lat"], p["lng"], p["species"], p["month"])
    for p in existing_points
}

all_points = existing_points.copy()
processed = 0

# --- Lister fichiers OBIS ---
tsv_files = glob(os.path.join(DATASET_DIR, "*.tsv"))

for tsv_file in tsv_files:
    print(f"📄 Lecture de {tsv_file}")
    df = pd.read_csv(tsv_file, sep="\t", low_memory=False)

    # Colonnes essentielles
    df = df[['decimalLatitude', 'decimalLongitude', 'species', 'eventDate']].dropna()
    df['decimalLatitude'] = pd.to_numeric(df['decimalLatitude'], errors="coerce")
    df['decimalLongitude'] = pd.to_numeric(df['decimalLongitude'], errors="coerce")
    df = df.dropna(subset=['decimalLatitude', 'decimalLongitude'])

    # Ajouter mois
    df["eventDate_parsed"] = pd.to_datetime(df["eventDate"], errors="coerce", utc=True)
    df["month"] = df["eventDate_parsed"].dt.month_name().str.lower().fillna("january")

    # Fusion Excel (common name)
    df = df.merge(species_info, on="species", how="left")

    # Ajouter photo depuis le dossier ~/especes/
    df["photo"] = df["species"].apply(
        lambda s: f"especes/{s}.jpg"
    )

    # Renommer colonnes
    df = df.rename(columns={
        "decimalLatitude": "lat",
        "decimalLongitude": "lng"
    })

    # Fusion météo
    merged = df.merge(
        meteo_df,
        on=["lat", "lng", "species", "month"],
        how="left"
    )

    # Colonnes finales
    merged = merged[[
        "lat", "lng", "species", "commonName", "photo",
        "month", "avg_temp", "avg_rain", "avg_wind"
    ]]

    # Ajouter au JSON final
    for row in merged.to_dict(orient="records"):

        key = (row["lat"], row["lng"], row["species"], row["month"])
        if key in already_done:
            continue

        all_points.append(row)
        already_done.add(key)
        processed += 1

        # Sauvegarde automatique
        if processed % 500 == 0:
            with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                json.dump(all_points, f, indent=4, ensure_ascii=False)
            print(f"💾 Sauvegarde intermédiaire après {processed} nouveaux points")

# Sauvegarde finale
os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(all_points, f, indent=4, ensure_ascii=False)

print("🎉 Fusion complète terminée !")
print(f"📌 Total de points dans points.json : {len(all_points)}")
print(f"➕ Nouveaux points ajoutés pendant ce run : {processed}")
