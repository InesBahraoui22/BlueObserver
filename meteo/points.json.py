import os
import pandas as pd
import json
from glob import glob
import openmeteo_requests
import requests_cache
from retry_requests import retry
import time

# -----------------------------
# Chemins relatifs
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # dossier du script (meteo/)
OBIS_DIR = "/Users/ines/Desktop/M1/OceanAware/obis_tsv"  # dossier TSV
OUTPUT_JSON = "/Users/ines/Desktop/M1/OceanAware/meteo/_site/data/points.json"  # sortie JSON

os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

# -----------------------------
# Open-Meteo config
# -----------------------------
cache_session = requests_cache.CachedSession(".cache", expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

month_ranges = {
    "january": ("2024-01-01", "2024-01-31"),
    "february": ("2024-02-01", "2024-02-29"),
    "march": ("2024-03-01", "2024-03-31"),
    "april": ("2024-04-01", "2024-04-30"),
    "may": ("2024-05-01", "2024-05-31"),
    "june": ("2024-06-01", "2024-06-30"),
    "july": ("2024-07-01", "2024-07-31"),
    "august": ("2024-08-01", "2024-08-31"),
    "september": ("2024-09-01", "2024-09-30"),
    "october": ("2024-10-01", "2024-10-31"),
    "november": ("2024-11-01", "2024-11-30"),
    "december": ("2024-12-01", "2024-12-31")
}

def get_weather(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min,rain_sum,windspeed_10m_max",
        "timezone": "Europe/London"
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    daily = response.Daily()
    dates = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )
    df = pd.DataFrame({
        "date": dates,
        "temp_max": daily.Variables(0).ValuesAsNumpy(),
        "temp_min": daily.Variables(1).ValuesAsNumpy(),
        "rain_sum": daily.Variables(2).ValuesAsNumpy(),
        "wind_max": daily.Variables(3).ValuesAsNumpy()
    })
    avg_temp = round(((df["temp_max"] + df["temp_min"]) / 2).mean(), 2)
    avg_rain = round(df["rain_sum"].mean(), 2)
    avg_wind = round(df["wind_max"].mean(), 2)
    return {
        "avg_temp": f"{avg_temp:.2f}",
        "avg_rain": f"{avg_rain:.2f}",
        "avg_wind": f"{avg_wind:.2f}"
    }

# -----------------------------
# Charger points déjà traités
# -----------------------------
if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        updated_points = json.load(f)
else:
    updated_points = []

processed_coords = {(p["lat"], p["lng"], p["month"]) for p in updated_points}

# -----------------------------
# Création / enrichissement du points.json
# -----------------------------
all_points = []

for tsv_file in glob(f"{OBIS_DIR}/*.tsv"):
    species_name = os.path.splitext(os.path.basename(tsv_file))[0]
    df = pd.read_csv(tsv_file, sep='\t')

    # Vérifie les colonnes correctes
    if "decimalLongitude" not in df.columns or "decimalLatitude" not in df.columns:
        print(f"⚠️ Colonnes manquantes dans {tsv_file}: {df.columns}")
        continue

    # Filtre Europe occidentale
    df["decimalLatitude"] = pd.to_numeric(df["decimalLatitude"], errors="coerce")
    df["decimalLongitude"] = pd.to_numeric(df["decimalLongitude"], errors="coerce")
    df = df[
        (df["decimalLongitude"] >= -25) & (df["decimalLongitude"] <= 45) &
        (df["decimalLatitude"] >= 27) & (df["decimalLatitude"] <= 69)
    ]

    df["species"] = species_name

    if "eventDate" in df.columns:
        df["eventDate_parsed"] = pd.to_datetime(df["eventDate"], errors="coerce", utc=True)
        df["month"] = df["eventDate_parsed"].dt.month_name().str.lower().fillna("january")
    else:
        df["month"] = "january"

    df = df[["decimalLatitude", "decimalLongitude", "species", "month"]]
    df = df.rename(columns={"decimalLatitude": "lat", "decimalLongitude": "lng"})

    all_points.extend(df.to_dict(orient="records"))

# -----------------------------
# Enrichissement météo avec reprise et rate limit
# -----------------------------
for i, point in enumerate(all_points):
    if (point["lat"], point["lng"], point["month"]) in processed_coords:
        continue  # déjà traité

    month = point.get("month", "january").lower()
    start_date, end_date = month_ranges.get(month, ("2024-01-01", "2024-12-31"))

    try:
        weather = get_weather(point["lat"], point["lng"], start_date, end_date)
        point["avg_temp"] = weather["avg_temp"]
        point["avg_rain"] = weather["avg_rain"]
        point["avg_wind"] = weather["avg_wind"]
    except Exception as e:
        print(f"⚠️ Erreur météo pour {point['species']} ({point['lat']},{point['lng']}): {e}")
        point["avg_temp"] = None
        point["avg_rain"] = None
        point["avg_wind"] = None

    updated_points.append(point)
    processed_coords.add((point["lat"], point["lng"], point["month"]))

    # Rate limit : pause 1 sec
    time.sleep(1)

    # Sauvegarde intermédiaire toutes les 100 requêtes
    if (i + 1) % 100 == 0:
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(updated_points, f, indent=4, ensure_ascii=False)
        print(f"✔ Sauvegarde intermédiaire après {i+1} points")

# -----------------------------
# Sauvegarde finale
# -----------------------------
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(updated_points, f, indent=4, ensure_ascii=False)

print(f"🎉 points.json créé avec {len(updated_points)} points enrichis avec météo")
