import os
import requests
from urllib.parse import urlparse

FOLDER = "espece"   # ton dossier d'espèces

def is_url(string):
    return string.startswith("http://") or string.startswith("https://")

def clean_espece_folder():
    files = os.listdir(FOLDER)

    for filename in files:
        full_path = os.path.join(FOLDER, filename)

        # Si ce n’est pas un .jpg → on ignore
        if not filename.lower().endswith(".jpg"):
            continue

        # Lire le contenu du fichier
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
        except:
            # Ce fichier est déjà une image binaire → OK
            print(f"✔ Image OK : {filename}")
            continue

        # Si le contenu n'est pas une URL → on garde
        if not is_url(content):
            print(f"✔ Fichier déjà bon : {filename}")
            continue

        # Si c'est une URL → télécharger
        print(f"⬇ Téléchargement : {filename} depuis {content}")

        try:
            response = requests.get(content, timeout=10)
            response.raise_for_status()

            # Écrire l'image réelle
            with open(full_path, "wb") as out:
                out.write(response.content)

            print(f"✔ Converti en vraie image : {filename}")

        except Exception as e:
            print(f"❌ Impossible de télécharger {content} → {e}")

if __name__ == "__main__":
    clean_espece_folder()
