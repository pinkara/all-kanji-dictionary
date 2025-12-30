import urllib.request
import re
import json
import time

# --- CONFIGURATION ---
TARGET_URL = "https://hc.jsecs.org/irg/ws2024/app/list.php?show_all=1"
OUTPUT_JSON = "irg2024_attributes.json"

# Plage exacte des caractères IRG 2024
START_ID = 1
END_ID = 4674

def scrape_and_generate_json():
    print(f"1. Téléchargement de la liste officielle depuis :")
    print(f"   {TARGET_URL}")
    print("   (Patientez quelques secondes...)")
    
    scraped_data = {}
    
    try:
        # User-Agent pour passer pour un navigateur standard
        req = urllib.request.Request(
            TARGET_URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        # Timeout généreux car la page est grosse
        with urllib.request.urlopen(req, timeout=60) as response:
            html_content = response.read().decode('utf-8')
            
        print(f"   Page téléchargée avec succès ({len(html_content)} octets).")
        print("2. Analyse des données (Radical & Traits)...")

        # Analyse du HTML ligne par ligne pour trouver les motifs
        # On découpe par ligne de tableau pour isoler chaque caractère
        lines = html_content.split('</tr>')
        
        for line in lines:
            # 1. On cherche l'ID du caractère (5 chiffres)
            # ex: >01201<
            id_match = re.search(r'>(\d{5})<', line)
            if not id_match:
                continue
            
            char_id = id_match.group(1)
            
            # 2. On cherche le pattern Radical.Traits
            # AMÉLIORATION : On utilise findall pour voir tous les candidats potentiels
            # et on cherche spécifiquement après un chevron '>' pour éviter les attributs
            matches = re.findall(r'>\s*(\d{1,3})\.(\d{1,2})', line)
            
            found_rad = None
            found_str = None
            
            # On parcourt les candidats pour trouver le premier radical valide (1-214)
            for m in matches:
                r_val = int(m[0])
                s_val = int(m[1])
                
                # Vérification de cohérence (Radical Kangxi standard)
                if 1 <= r_val <= 214:
                    found_rad = r_val
                    found_str = s_val
                    break # On prend le premier valide trouvé
            
            if found_rad is not None:
                scraped_data[char_id] = {
                    'rad': found_rad,
                    'str': found_str
                }

        print(f"   -> {len(scraped_data)} caractères identifiés avec succès.")

    except Exception as e:
        print(f"   [ERREUR] Impossible de lire le site : {e}")
        print("   Le fichier JSON sera généré avec des valeurs par défaut pour tout le monde.")

    print(f"3. Consolidation de la liste ({START_ID:05d} à {END_ID:05d})...")
    
    final_data = {}
    missing_count = 0
    
    # On boucle de 1 à 4674 pour être sûr de ne rien oublier
    for i in range(START_ID, END_ID + 1):
        str_id = f"{i:05d}" # Format 00001
        
        if str_id in scraped_data:
            # On a les infos officielles
            final_data[str_id] = scraped_data[str_id]
        else:
            # Pas d'info trouvée : on met des valeurs par défaut
            # Radical 215 = "Nouveau/Inconnu" (trié à la fin)
            final_data[str_id] = {
                'rad': 215,
                'str': 0
            }
            missing_count += 1
            
    print(f"   Total entrées : {len(final_data)}")
    if missing_count > 0:
        print(f"   (Note : {missing_count} caractères n'étaient pas listés sur la page web, ajoutés par défaut).")

    # Écriture du fichier
    print(f"4. Sauvegarde du fichier '{OUTPUT_JSON}'...")
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2)
        
    print("Terminé ! Vous pouvez maintenant lancer 'kanji_all.py'.")

if __name__ == "__main__":
    scrape_and_generate_json()
