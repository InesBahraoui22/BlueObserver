import os
import requests
from PIL import Image

# Dossier courant : celui où se trouve le script
FOLDER = os.path.dirname(os.path.abspath(__file__))

def download_image_from_url(url, target_path):
    """Télécharge une image à partir d'une URL."""
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()

        with open(target_path, "wb") as f:
            f.write(r.content)

        print(f"✔ Image téléchargée → {target_path}")
        return target_path

    except Exception as e:
        print(f"❌ Erreur téléchargement {url}: {e}")
        return None


def convert_to_jpg(path):
    """Convertit un fichier JPEG ou autre format image en JPG."""
    try:
        img = Image.open(path).convert("RGB")

        new_path = os.path.splitext(path)[0] + ".jpg"
        img.save(new_path, "JPEG")

        print(f"✔ Converti en JPG : {path} → {new_path}")

        # supprimer l'ancien fichier si différent
        if new_path != path:
            os.remove(path)

        return new_path

    except Exception as e:
        print(f"❌ Erreur conversion {path}: {e}")
        return None


def process_all_images():
    """Traite tous les fichiers du dossier."""
    for file in os.listdir(FOLDER):
        file_path = os.path.join(FOLDER, file)
        ext = file.lower().split(".")[-1]

        # ------- 1️⃣ CAS : le fichier est un .html ou contient une URL -------
        if ext in ["html", "txt"]:  
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()

                if content.startswith("http://") or content.startswith("https://"):
                    print(f"⚠ {file} contient une URL → {content}")

                    # nom jpg basé sur nom du fichier original
                    jpg_name = os.path.splitext(file)[0] + ".jpg"
                    save_path = os.path.join(FOLDER, jpg_name)

                    download_image_from_url(content, save_path)
                    continue

            except Exception as e:
                print(f"Erreur lecture {file}: {e}")
                continue

        # ------- 2️⃣ CAS : un fichier image jpeg → jpg -------
        if ext in ["jpeg"]:
            convert_to_jpg(file_path)
            continue

        # ------- 3️⃣ CAS : un fichier JPG mais qui contient une URL -------
        if ext in ["jpg"]:
            try:
                with open(file_path, "rb") as f:
                    data = f.read()

                if data[:4] == b"http":  # contenu = URL
                    url = data.decode("utf-8").strip()
                    print(f"⚠ {file} contient une URL → {url}")

                    download_image_from_url(url, file_path)
                    continue

            except Exception as e:
                print(f"Erreur dans {file}: {e}")
                continue

        # Autres formats ignorés
        # (png, gif, etc — si tu veux les convertir aussi, dis-le)
        

if __name__ == "__main__":
    process_all_images()
    print("✅ Traitement terminé.")
