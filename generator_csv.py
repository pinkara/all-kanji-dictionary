import urllib.request
import zipfile
import io
import re
import csv
import sys

# --- CONFIGURATION ---
UNIHAN_URL = "https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip"
OUTPUT_FILE = "cjk_characters.csv"

def download_and_extract():
    """Télécharge le fichier ZIP Unihan depuis unicode.org."""
    print(f"1. Téléchargement de {UNIHAN_URL}...")
    try:
        req = urllib.request.Request(
            UNIHAN_URL, 
            data=None, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        response = urllib.request.urlopen(req)
        zip_data = response.read()
        print(f"   Téléchargement terminé ({len(zip_data)/1024/1024:.2f} MB).")
        return zip_data
    except Exception as e:
        print(f"   ERREUR CRITIQUE: Impossible de télécharger Unihan. {e}")
        return None

def parse_unihan(zip_bytes):
    """Analyse tous les fichiers du ZIP pour extraire les données kRSUnicode."""
    print("2. Analyse des fichiers ZIP...")
    cjk_map = []
    
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        # On liste tous les fichiers pertinents (ignorer les dossiers et fichiers cachés Mac)
        file_list = [n for n in z.namelist() if not n.endswith('/') and not n.startswith('__MACOSX') and not '/.' in n]
        
        for filename in file_list:
            # On ignore les fichiers de documentation
            if "ReadMe" in filename or "History" in filename:
                continue

            print(f"   -> Inspection : {filename}")
            
            with z.open(filename) as f:
                entries_found = 0
                for line in f:
                    try:
                        line_str = line.decode('utf-8').strip()
                    except:
                        continue
                    
                    if not line_str or line_str.startswith('#'):
                        continue
                    
                    # On cherche la propriété qui définit le Radical et les Traits
                    if 'kRSUnicode' in line_str:
                        parts = line_str.split('\t')
                        
                        # Format attendu: U+XXXX \t kRSUnicode \t Radical.Strokes
                        if len(parts) >= 3 and parts[1] == 'kRSUnicode':
                            try:
                                # 1. Code Point (cp)
                                code_str = parts[0].replace('U+', '')
                                code_point = int(code_str, 16)
                                char = chr(code_point)
                                
                                # 2. Radical et Traits (rad, str)
                                # Le format est souvent "Radical.Traits" (ex: 1.4) ou "Radical'.Traits"
                                rs_data = parts[2].split(' ')[0] # On prend le premier radical si plusieurs
                                
                                match = re.match(r"(\d+)'?\.(-?\d+)", rs_data)
                                if match:
                                    radical = int(match.group(1))
                                    strokes = int(match.group(2))
                                    
                                    cjk_map.append({
                                        'rad': radical,
                                        'str': strokes,
                                        'cp': code_point,
                                        'char': char
                                    })
                                    entries_found += 1
                            except ValueError:
                                continue
                
                if entries_found > 0:
                    print(f"      {entries_found} entrées trouvées dans {filename}.")

    print(f"   TOTAL: {len(cjk_map)} caractères extraits.")
    return cjk_map

def generate_csv(data):
    """Génère le fichier CSV final."""
    if not data:
        print("   ERREUR: Aucune donnée à générer.")
        return

    print("3. Tri des données (Radical > Traits > CodePoint)...")
    # Tri identique à la version précédente
    data.sort(key=lambda x: (x['rad'], x['str'], x['cp']))
    
    print(f"4. Écriture du fichier CSV : {OUTPUT_FILE}...")
    
    try:
        with open(OUTPUT_FILE, mode='w', encoding='utf-8', newline='') as csv_file:
            # Définition des colonnes demandées
            fieldnames = ['rad', 'str', 'cp', 'char']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Écriture de l'en-tête
            writer.writeheader()

            # Écriture des lignes
            writer.writerows(data)
            
        print(f"Succès ! Le fichier '{OUTPUT_FILE}' a été créé.")
        
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier CSV : {e}")

if __name__ == "__main__":
    zip_data = download_and_extract()
    if zip_data:
        data = parse_unihan(zip_data)
        if data:
            generate_csv(data)
