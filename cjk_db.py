import urllib.request
import zipfile
import io
import re
import json
import os

# --- CONFIGURATION ---
UNIHAN_URL = "https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip"
OUTPUT_DB = "cjk_db.json"

def download_unihan():
    print(f"1. Téléchargement de {UNIHAN_URL}...")
    try:
        req = urllib.request.Request(
            UNIHAN_URL, 
            data=None, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        response = urllib.request.urlopen(req)
        return response.read()
    except Exception as e:
        print(f"   ERREUR CRITIQUE: {e}")
        return None

def parse_unihan_data(zip_bytes):
    print("2. Analyse et fusion des données Unihan...")
    
    # Dictionnaire principal : { code_point (int) : { data... } }
    db = {}

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        # Liste des fichiers à analyser
        files_to_scan = {
            'Unihan_RadicalStrokeCounts.txt': 'structure',
            'Unihan_Readings.txt': 'definition',
            'Unihan_IRGSources.txt': 'source'
        }
        
        candidates = [n for n in z.namelist() if any(f in n for f in files_to_scan.keys())]
        
        for filename in candidates:
            short_name = filename.split('/')[-1]
            mode = files_to_scan.get(short_name, 'unknown')
            
            print(f"   -> Lecture de {short_name} ({mode})...")
            
            with z.open(filename) as f:
                for line in f:
                    try: line_str = line.decode('utf-8').strip()
                    except: continue
                    if not line_str or line_str.startswith('#'): continue

                    parts = line_str.split('\t')
                    if len(parts) < 3: continue

                    # Récupération du Code Point
                    try:
                        cp = int(parts[0].replace('U+', ''), 16)
                    except: continue

                    if cp not in db:
                        db[cp] = {
                            'cp': cp,
                            'char': chr(cp),
                            'rad': 0,
                            'str': 0,
                            'def': '', # Définition
                            'pinyin': '',
                            'is_ext_j': (0x323B0 <= cp <= 0x3347F) # Flag pour Ext J
                        }

                    tag = parts[1]
                    value = parts[2]

                    # --- ANALYSE SELON LE FICHIER ---
                    
                    # 1. STRUCTURE (Radical / Traits)
                    if tag == 'kRSUnicode':
                        # Format: "1.0" ou "1'.0"
                        # On prend le premier radical listé
                        primary = value.split(' ')[0]
                        m = re.match(r"(\d+)'?\.(-?\d+)", primary)
                        if m:
                            db[cp]['rad'] = int(m.group(1))
                            db[cp]['str'] = int(m.group(2))

                    # 2. DÉFINITIONS & LECTURES
                    elif tag == 'kDefinition':
                        db[cp]['def'] = value
                    elif tag == 'kMandarin':
                        db[cp]['pinyin'] = value

    # Conversion en liste pour le JSON final
    print("3. Conversion et tri...")
    final_list = list(db.values())
    
    # On nettoie les entrées sans radical (souvent des erreurs ou des contrôles)
    final_list = [x for x in final_list if x['rad'] > 0]
    
    # Tri : Radical > Traits > CodePoint
    final_list.sort(key=lambda x: (x['rad'], x['str'], x['cp']))
    
    print(f"4. Exportation de {len(final_list)} entrées vers {OUTPUT_DB}...")
    with open(OUTPUT_DB, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, separators=(',', ':')) # Minifié
    
    print("Terminé !")

if __name__ == "__main__":
    zip_data = download_unihan()
    if zip_data:
        parse_unihan_data(zip_data)
