import os
import urllib.request
import zipfile
import time

# --- CONFIGURATION ---
BASE_URL = "https://glyphwiki.org/glyph/"
OUTPUT_DIR = "irg2024_fonts"
ZIP_NAME = "fonts_irg2024.zip"

# Plage IRG 2024 : 00001 à 04674
START_ID = 1
END_ID = 4674

def download_file(filename):
    url = f"{BASE_URL}{filename}.ttf"
    filepath = os.path.join(OUTPUT_DIR, f"{filename}.ttf")
    
    # Si le fichier existe déjà, on passe
    if os.path.exists(filepath):
        return True

    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            with open(filepath, 'wb') as out_file:
                out_file.write(response.read())
        return True
    except Exception as e:
        print(f"   [ERREUR] Impossible de télécharger {filename}: {e}")
        return False

def main():
    # Création du dossier de stockage
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    print(f"=== TÉLÉCHARGEMENT IRG 2024 ({START_ID} à {END_ID}) ===")
    
    files_to_download = []
    
    # Génération de la liste
    for i in range(START_ID, END_ID + 1):
        filename = f"irg2024-{i:05d}" # ex: irg2024-01201
        files_to_download.append(filename)
    
    total = len(files_to_download)
    print(f"Total de fichiers : {total}")
    print("Démarrage... (Cela peut prendre 10-15 minutes)")
    
    success_count = 0
    start_time = time.time()
    
    # Boucle de téléchargement
    for i, filename in enumerate(files_to_download):
        if download_file(filename):
            success_count += 1
            
        # Affichage progression tous les 100 fichiers
        if i % 100 == 0 and i > 0:
            elapsed = time.time() - start_time
            percent = (i / total) * 100
            print(f"   Progression : {i}/{total} ({percent:.1f}%) - {elapsed:.0f}s écoulées")

    # Création du ZIP
    print(f"\n=== CRÉATION DU ZIP ({ZIP_NAME}) ===")
    with zipfile.ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for file in files:
                if file.endswith('.ttf'):
                    filepath = os.path.join(root, file)
                    zipf.write(filepath, arcname=file)
    
    print(f"Terminé ! {success_count} fichiers sont dans '{ZIP_NAME}'.")
    print("Vous pouvez maintenant utiliser 'install_fonts.py' avec ce fichier zip.")

if __name__ == "__main__":
    main()
