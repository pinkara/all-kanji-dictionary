import urllib.request
import re
import json
import time

# --- CONFIGURATION ---
# Utilisation de list.php qui est plus léger et structuré
TARGET_URL = "https://hc.jsecs.org/irg/ws2024/app/list.php?show_all=1"
OUTPUT_JSON = "irg2024_attributes.json"

# Plage exacte des caractères IRG 2024
START_ID = 1
END_ID = 4674

def scrape_and_generate_json():
    print(f"1. Téléchargement de la liste officielle depuis :")
    print(f"   {TARGET_URL}")
    print("   (Patientez, téléchargement en cours...)")
    
    scraped_data = {}
    
    try:
        req = urllib.request.Request(
            TARGET_URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            html_content = response.read().decode('utf-8')
            
        print(f"   Page téléchargée ({len(html_content)} octets). Analyse intelligente...")

        # Découpage par ligne de tableau
        rows = html_content.split('</tr>')
        
        for row in rows:
            # 1. Extraction de l'ID (5 chiffres)
            id_match = re.search(r'>(\d{5})<', row)
            if not id_match:
                continue
            
            char_id = id_match.group(1)
            
            # 2. Extraction Radical.Traits (Smart Regex)
            # On cherche un motif nombre.nombre (ex: 85.9)
            # MAIS qui n'est PAS précédé par une lettre ou un tiret (pour éviter G-12.3)
            # (?<![-\w]) : Lookbehind négatif (pas de lettre/chiffre/tiret avant)
            # (\d{1,3})  : Radical (1 à 3 chiffres)
            # \'?        : Apostrophe optionnelle (pour les radicaux primés comme 187')
            # \.         : Point
            # (\d{1,2})  : Traits (1 à 2 chiffres)
            
            pattern = r'(?<![-\w])(\d{1,3})\'?\.(\d{1,2})(?:\.\d+)?(?![-\w])'
            matches = re.findall(pattern, row)
            
            found_rad = None
            found_str = None
            
            # On parcourt les candidats trouvés dans la ligne
            for m in matches:
                r_val = int(m[0])
                s_val = int(m[1])
                
                # Validation : Radical Kangxi doit être entre 1 et 214
                if 1 <= r_val <= 214:
                    found_rad = r_val
                    found_str = s_val
                    # On prend le premier radical valide trouvé qui n'est pas un code source
                    break 
            
            if found_rad is not None:
                scraped_data[char_id] = {
                    'rad': found_rad,
                    'str': found_str
                }

        print(f"   -> {len(scraped_data)} caractères correctement identifiés.")

    except Exception as e:
        print(f"   [ERREUR] Impossible de lire le site : {e}")
        print("   Le JSON sera incomplet (valeurs par défaut).")

    print(f"3. Consolidation et Remplissage ({START_ID:05d} à {END_ID:05d})...")
    
    final_data = {}
    missing_count = 0
    
    for i in range(START_ID, END_ID + 1):
        str_id = f"{i:05d}"
        
        if str_id in scraped_data:
            final_data[str_id] = scraped_data[str_id]
        else:
            # Valeur par défaut UNIQUEMENT si vraiment introuvable
            final_data[str_id] = {
                'rad': 215, # Radical "Inconnu"
                'str': 0
            }
            missing_count += 1
            
    print(f"   Total entrées finales : {len(final_data)}")
    if missing_count > 0:
        print(f"   (Info : {missing_count} caractères non trouvés, mis en Radical 215)")
    else:
        print("   (Succès : Tous les caractères ont été associés à un radical !)")

    print(f"4. Sauvegarde dans '{OUTPUT_JSON}'...")
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2)
        
    print("Terminé ! Lancez maintenant 'kanji_all.py' pour générer la grille corrigée.")

if __name__ == "__main__":
    scrape_and_generate_json()
