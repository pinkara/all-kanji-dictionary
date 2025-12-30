import os
import urllib.request
import zipfile
import time

# --- CONFIGURATION ---
BASE_URL = "https://glyphwiki.org/glyph/"
OUTPUT_DIR = "downloaded_fonts"
ZIP_NAME = "fonts_glyphwiki.zip"

#  PLAGE EXTENSION J (U+323B0 .. U+3347F)
EXT_J_START = 0x323B0
EXT_J_END = 0x3347F

def download_file(filename):
    url = f"{BASE_URL}{filename}.ttf"
    filepath = os.path.join(OUTPUT_DIR, f"{filename}.ttf")

    # Si le fichier existe déjà, on passe (pour pouvoir relancer le script sans tout retélécharger)
    if os.path.exists(filepath):
        print(f"   [Existe déjà] {filename}")
        return True

    try:
        # User-Agent pour ne pas être bloqué
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            with open(filepath, 'wb') as out_file:
                out_file.write(response.read())
        print(f"   [OK] Téléchargé: {filename}")
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"   [404] Introuvable sur GlyphWiki: {filename}")
        else:
            print(f"   [ERREUR {e.code}] {filename}")
        return False
    except Exception as e:
        print(f"   [ERREUR] {filename}: {e}")
        return False

def main():
    # Création du dossier
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"=== DÉBUT DU TÉLÉCHARGEMENT ===")
    print(f"Dossier cible : {OUTPUT_DIR}")

    files_to_download = []

    # A. Ajout des Custom
    print("--- Préparation de la liste Custom ---")
    files_to_download.extend(CUSTOM_LIST)

    # B. Ajout de l'Extension J
    print(f"--- Préparation de la liste Extension J (U+{hex(EXT_J_START)} à U+{hex(EXT_J_END)}) ---")
    for cp in range(EXT_J_START, EXT_J_END + 1):
        # Format GlyphWiki pour unicode : "u" + hex minuscule (ex: u323b0)
        hex_code = f"u{cp:x}"
        files_to_download.append(hex_code)

    total = len(files_to_download)
    print(f"Total de fichiers à traiter : {total}")

    # C. Téléchargement
    success_count = 0
    for i, filename in enumerate(files_to_download):
        # Petit délai pour ne pas DDOS GlyphWiki (important !)
        # time.sleep(0.05)

        if download_file(filename):
            success_count += 1

        # Affichage progression tous les 100 fichiers
        if i % 100 == 0:
            print(f"   ... Progression : {i}/{total}")

    # D. Création du ZIP
    print(f"\n=== CRÉATION DU ZIP ({ZIP_NAME}) ===")
    with zipfile.ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for file in files:
                if file.endswith('.ttf'):
                    filepath = os.path.join(root, file)
                    zipf.write(filepath, arcname=file) # On met les fichiers à la racine du zip

    print(f"Terminé ! {success_count} fichiers téléchargés.")
    print(f"Votre fichier ZIP est prêt : {ZIP_NAME}")

if __name__ == "__main__":
    main()
