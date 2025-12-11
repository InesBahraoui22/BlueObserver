# Importation des packages

import os
import csv
import time
import datetime as dt
from pathlib import Path
import requests

# Définition des paramètres de filtration

LON_MIN, LON_MAX = -25.0, 45.0  # Ouest, Est
LAT_MIN, LAT_MAX = 27.0, 69.0  # Sud, Nord

START_DATE = "2000-01-01"  # Date définie comme début pour tous les fichiers

END_DATE = dt.date.today().isoformat()  # "aujourd'hui" au format AAAA-MM-JJ ou en eng YYYY-MM-DD

SPECIES = [
    "Balaenoptera acutorostrata",
    "Balaenoptera edeni",
    "Balaenoptera musculus",
    "Balaenoptera physalus",
    "Balaenoptera borealis",
    "Eschrichtius robustus",
    "Eubalaena glacialis",
    "Feresa attenuata",
    "Globicephala macrorhynchus",
    "Globicephala melas",
    "Grampus griseus",
    "Hyperoodon ampullatus",
    "Kogia sima",
    "Lagenorhynchus acutus",
    "Lagenorhynchus albirostratus",
    "Mesoplodon bidens",
    "Mesoplodon densirostris",
    "Mesoplodon europaeus",
    "Mesoplodon mirus",
    "Monachus monachus",
    "Odobenus rosmarus",
    "Orcinus orca",
    "Peponocephala electra",
    "Pseudorca crassidens",
    "Stenella attenuata",
    "Stenella frontalis",
    "Steno bredanensis",
    "Ziphius cavirostris"
    ]


FILE_PATH = "../data/obis_observation_espèces/"

SIZE = 10000  # Nombre d'enregistrements à demander par sous-requête

SLEEP = 0.2  # Pause entre chaque requête pour ne pas surcharger l'API

FIELDS = ["scientificName", "decimalLongitude", "decimalLatitude", "eventDate"]
BASE_URL = "https://api.obis.org/v3/occurrence"
OFFSET_FILE = "offset.state"

# POLYGÔNE zone de délimitation
POLYGON = f"""POLYGON((
    {LON_MIN} {LAT_MIN},
    {LON_MAX} {LAT_MIN},
    {LON_MAX} {LAT_MAX},
    {LON_MIN} {LAT_MAX},
    {LON_MIN} {LAT_MIN}
    ))"""

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / FILE_PATH
DATA_DIR.mkdir(parents=True, exist_ok=True)
OFFSET_PATH = SCRIPT_DIR / OFFSET_FILE


def fetch_page(session, base_url, scientific_name, polygon, start_date, end_date, size, offset, fields):
    params = {
        "scientificname": scientific_name,
        "geometry": polygon,
        "startdate": start_date,
        "enddate": end_date,
        "size": size,
        "offset": offset,
        "fields": ",".join(fields),
        "hasCoordinate": "true"
    }
    response = session.get(
        base_url,
        params=params,
        timeout=180,
        headers={"Accept-Encoding": "gzip"}
        )
    return response.json()


def ensure_writer(file, writer, rows, fields):
    if writer is not None:
        return writer
    headers = list({k for row in rows for k in row.keys()})
    ordered = [c for c in fields if c in headers] + [c for c in headers if c not in fields]
    writer = csv.DictWriter(file, fieldnames=ordered, delimiter="\t")
    writer.writeheader()
    return writer


def load_offset(file_path):
    if os.path.exists(file_path):
        with open(file_path, encoding="utf-8") as f:
            return int(f.read().strip() or 0)
    return 0


def save_offset(file_path, offset):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(offset))


def get_species_data(session, species):
    tsv_output_path = DATA_DIR / f"{species.replace(' ', '_')}.tsv"

    # Récupération du nombre total d'occurrences disponibles
    total_occurences_request = fetch_page(
        session=session,
        base_url=BASE_URL,
        scientific_name=species,
        polygon=POLYGON,
        start_date=START_DATE,
        end_date=END_DATE,
        size=0,
        offset=0,
        fields=["total"]
    )
    total_occurences = total_occurences_request.get("total", 0)

    print(f"Nombre d'occurences pour l'espèce {species} : {total_occurences}")
    if total_occurences == 0:
        print(f"Aucune donnée trouvée pour l'espèce {species}. Fin.")
        return

    # Fichier temporaire : pour reprendre là où on s'était arrêté si crash
    offset = load_offset(OFFSET_PATH)

    # Fabrication du TSV
    writer = None
    written = offset

    with tsv_output_path.open("w", newline="", encoding="utf-8") as f:
        while offset < total_occurences:
            remaining = total_occurences - offset
            page_size = min(SIZE, remaining)

            # Requête pour une page de données
            rows = fetch_page(
                session=session,
                base_url=BASE_URL,
                scientific_name=species,
                polygon=POLYGON,
                start_date=START_DATE,
                end_date=END_DATE,
                size=page_size,
                offset=offset,
                fields=FIELDS
            ).get("results", [])

            if not rows:
                print("Page vide renvoyée. Arrêt.")
                break

            writer = ensure_writer(f, writer, rows, FIELDS)

            for row in rows:
                writer.writerow(row)

            n = len(rows)
            written += n
            print(f"Téléchargées : {written}/{total_occurences}")

            offset += n
            save_offset(OFFSET_PATH, offset)
            time.sleep(SLEEP)

    print(f"✅ Terminé (ou stoppé proprement). Lignes écrites : {written}/{total_occurences}")

    if OFFSET_PATH.exists() and written >= total_occurences:
        OFFSET_PATH.unlink()


def main():
    session = requests.Session()
    session.headers.update({"Accept-Encoding": "gzip"})

    for species in SPECIES:
        get_species_data(session, species)

    session.close()


if __name__ == "__main__":
    main()
