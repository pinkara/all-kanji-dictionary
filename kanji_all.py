import urllib.request
import zipfile
import io
import re
import os
import json

# --- CONFIGURATION ---
UNIHAN_URL = "https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip"
OUTPUT_FILE = "ALL_KANJI.html"

# FICHIERS DE DONNÉES LOCAUX (Indispensables)
# 1. Le fichier généré par scrape_irg2024.py (contient les radicaux)
IRG_ATTR_FILE = "irg2024_attributes.json" 
# 2. Votre fichier de liste (celui que vous avez uploadé)
IRG_VALID_FILE = "irg2024_qui_marche.json"

# CONFIGURATION DES DICTIONNAIRES GLYPHWIKI
GLYPHWIKI_DICTS = {
    "kokuji": "K", "wasei-kanji": "W", "kadokawa-daijigen": "KD",
    "nihonjin-no-tsukutta": "N", "shincho-nihongo": "S", "hokke": "H",
    "chukajikai": "Z", "kozouji-jiten": "G", "shinsen-jikyo": "SJ",
    "toshoryo-ruiju": "T", "kozanji-tenrei": "KT", "chunom-jiten": "V",
    "daijiten-chunom": "VD", "jiten-chunom-tekiin": "J", "joshin-bun-jiten": "JU",
    "buyi-fangkuai": "B", "china-jingyu": "C", 
    "irg2024": "I24"
}

# LISTE MANUELLE (Vos autres dictionnaires hors IRG)
RAW_GLYPHWIKI_DATA = [
    # DKW
    {'source': 'dkw', 'id': '00005', 'rad': 1, 'str': 1, 'has_unicode_sim': False},
    {'source': 'dkw', 'id': '00092', 'rad': 3, 'str': 1, 'has_unicode_sim': False},
    {'source': 'dkw', 'id': '00095', 'rad': 3, 'str': 2, 'has_unicode_sim': False},
    {'source': 'dkw', 'id': '00098', 'rad': 1, 'str': 2, 'has_unicode_sim': False},

    # IDS
    {'source': 'ids', 'id': '0001', 'rad': 100, 'str': 7, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0002', 'rad': 130, 'str': 7, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0003', 'rad': 85, 'str': 6, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0004', 'rad': 9, 'str': 7, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0005', 'rad': 5, 'str': 20, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0006', 'rad': 9, 'str': 20, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0007', 'rad': 130, 'str': 17, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0008', 'rad': 75, 'str': 14, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0009', 'rad': 85, 'str': 18, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0010', 'rad': 102, 'str': 2, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0011', 'rad': 132, 'str': 21, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0012', 'rad': 137, 'str': 7, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0013', 'rad': 57, 'str': 10, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0014', 'rad': 102, 'str': 11, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0015', 'rad': 170, 'str': 3, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0016', 'rad': 170, 'str': 9, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0017', 'rad': 170, 'str': 4, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0018', 'rad': 143, 'str': 15, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0019', 'rad': 30, 'str': 13, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0020', 'rad': 86, 'str': 27, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0021', 'rad': 75, 'str': 10, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0022', 'rad': 115, 'str': 9, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0023', 'rad': 108, 'str': 10, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0024', 'rad': 31, 'str': 24, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0025', 'rad': 31, 'str': 8, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0026', 'rad': 31, 'str': 8, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0027', 'rad': 104, 'str': 17, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0028', 'rad': 54, 'str': 8, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0029', 'rad': 173, 'str': 11, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0030', 'rad': 194, 'str': 16, 'has_unicode_sim': False},
    {'source': 'ids', 'id': '0031', 'rad': 194, 'str': 13, 'has_unicode_sim': False},



    # Exemple : H+37524
    {'source': 'hokke', 'id': '00712', 'rad': 72, 'str': 14, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '00713', 'rad': 72, 'str': 21, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '00714', 'rad': 72, 'str': 15, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '00716', 'rad': 72, 'str': 9, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '00724', 'rad': 72, 'str': 9, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '00735', 'rad': 72, 'str': 7, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '00736', 'rad': 72, 'str': 12, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '00741', 'rad': 72, 'str': 12, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '00742', 'rad': 72, 'str': 13, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '00743', 'rad': 72, 'str': 10, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '00744', 'rad': 72, 'str': 6, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '00745', 'rad': 72, 'str': 16, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '00756', 'rad': 72, 'str': 8, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '00761', 'rad': 72, 'str': 11, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '00764', 'rad': 72, 'str': 10, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '00765', 'rad': 72, 'str': 6, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '01243', 'rad': 143, 'str': 3, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '01245', 'rad': 102, 'str': 2, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '01246', 'rad': 120, 'str': 10, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '01252', 'rad': 172, 'str': 6, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '01253', 'rad': 100, 'str': 7, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '01254', 'rad': 148, 'str': 14, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '01255', 'rad': 115, 'str': 7, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '01333', 'rad': 188, 'str': 0, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '02032', 'rad': 188, 'str': 16, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '02033', 'rad': 188, 'str': 8, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '02325', 'rad': 86, 'str': 8, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '02943', 'rad': 139, 'str': 0, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '02944', 'rad': 139, 'str': -1, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '02945', 'rad': 139, 'str': 10, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '02952', 'rad': 80, 'str': -1, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '02953', 'rad': 80, 'str': 2, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '02955', 'rad': 80, 'str': 7, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '09666', 'rad': 8, 'str': 3, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '09756', 'rad': 8, 'str': 5, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '09764', 'rad': 8, 'str': 21, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '11033', 'rad': 33, 'str': 13, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '11034', 'rad': 33, 'str': 20, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '11036', 'rad': 33, 'str': 21, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '11041', 'rad': 33, 'str': 12, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '11043', 'rad': 33, 'str': 20, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '11044', 'rad': 33, 'str': 19, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '11045', 'rad': 33, 'str': 22, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '14132', 'rad': 173, 'str': 0, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '14216', 'rad': 173, 'str': 3, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '14231', 'rad': 173, 'str': 8, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '14236', 'rad': 173, 'str': 15, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '14322', 'rad': 173, 'str': 18, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '14335', 'rad': 173, 'str': 24, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '17356', 'rad': 46, 'str': 6, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '17525', 'rad': 46, 'str': 8, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '17632', 'rad': 46, 'str': 6, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '21154', 'rad': 61, 'str': 13, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '21155', 'rad': 61, 'str': 5, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '24526', 'rad': 30, 'str': 15, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '24634', 'rad': 30, 'str': 23, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '25016', 'rad': 30, 'str': 19, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '25165', 'rad': 30, 'str': 18, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '25742', 'rad': 195, 'str': 0, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '25914', 'rad': 195, 'str': 36, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '26154', 'rad': 147, 'str': 7, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '26155', 'rad': 147, 'str': 21, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '32764', 'rad': 57, 'str': 3, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '35253', 'rad': 162, 'str': 14, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '35453', 'rad': 162, 'str': 16, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '35564', 'rad': 162, 'str': 4, 'has_unicode_sim': False},

    {'source': 'hokke', 'id': '37464', 'rad': 215, 'str': 7, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37513', 'rad': 215, 'str': 14, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37522', 'rad': 215, 'str': 3, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37523', 'rad': 215, 'str': 3, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37524', 'rad': 215, 'str': 4, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37525', 'rad': 215, 'str': 22, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37526', 'rad': 215, 'str': 16, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37533', 'rad': 215, 'str': 12, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37534', 'rad': 215, 'str': 6, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37546', 'rad': 215, 'str': 10, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37551', 'rad': 215, 'str': 6, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37554', 'rad': 215, 'str': 9, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37555', 'rad': 215, 'str': 8, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37556', 'rad': 215, 'str': 16, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37564', 'rad': 215, 'str': 13, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37565', 'rad': 215, 'str': 16, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37613', 'rad': 215, 'str': 13, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37614', 'rad': 215, 'str': 12, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37651', 'rad': 215, 'str': 5, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '38433', 'rad': 215, 'str': 21 , 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '38432', 'rad': 215, 'str': 12 , 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '38426', 'rad': 215, 'str': 15 , 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '38425', 'rad': 215, 'str': 21 , 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '38424', 'rad': 215, 'str': 22, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '38423', 'rad': 215, 'str': 14, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '38422', 'rad': 215, 'str': 12, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '38416', 'rad': 215, 'str': 12, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '38415', 'rad': 215, 'str': 12, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '38414', 'rad': 215, 'str': 5, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '38413', 'rad': 215, 'str': 14, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '38412', 'rad': 215, 'str': 15, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '38234', 'rad': 215, 'str': 4, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '38232', 'rad': 215, 'str': 6, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37763', 'rad': 215, 'str': 14, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37761', 'rad': 215, 'str': 7, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37755', 'rad': 215, 'str': 19, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37754', 'rad': 215, 'str': 19, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37753', 'rad': 215, 'str': 14, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37632', 'rad': 215, 'str': 11, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37633', 'rad': 215, 'str': 10, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37634', 'rad': 215, 'str': 9, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37635', 'rad': 215, 'str': 10, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37643', 'rad': 215, 'str': 16, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37655', 'rad': 215, 'str': 10, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37752', 'rad': 215, 'str': 18, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37751', 'rad': 215, 'str': 6, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37746', 'rad': 215, 'str': 9, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37745', 'rad': 215, 'str': 12, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37744', 'rad': 215, 'str': 18, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37742', 'rad': 215, 'str': 14, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37741', 'rad': 215, 'str': 19, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37735', 'rad': 215, 'str': 16, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37732', 'rad': 215, 'str': 13, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37726', 'rad': 215, 'str': 10, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37725', 'rad': 215, 'str': 11, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37724', 'rad': 215, 'str': 14, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37723', 'rad': 215, 'str': 13, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37722', 'rad': 215, 'str': 8, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37721', 'rad': 215, 'str': 8, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37716', 'rad': 215, 'str': 13, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37715', 'rad': 215, 'str': 8, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37713', 'rad': 215, 'str': 8, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37712', 'rad': 215, 'str': 17, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37666', 'rad': 215, 'str': 7, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37664', 'rad': 215, 'str': 13, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37663', 'rad': 215, 'str': 13, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37662', 'rad': 215, 'str': 8, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37661', 'rad': 215, 'str': 18, 'has_unicode_sim': False},
    {'source': 'hokke', 'id': '37656', 'rad': 215, 'str': 10, 'has_unicode_sim': False},


    # Exemple : (Kokuji)
    {'source': 'kokuji', 'id': '0001', 'rad': 2, 'str': 11, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0002', 'rad': 4, 'str': 8, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0003', 'rad': 15, 'str': 3, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0004', 'rad': 30, 'str': 76, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0005', 'rad': 31, 'str': 8, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0006', 'rad': 41, 'str': 6, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0007', 'rad': 46, 'str': 9, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0008', 'rad': 51, 'str': 7, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0009', 'rad': 53, 'str': 2, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0010', 'rad': 64, 'str': 1, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0011', 'rad': 72, 'str': 12, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0012', 'rad': 75, 'str': 3, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0013', 'rad': 77, 'str': 3, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0014', 'rad': 98, 'str': 4, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0015', 'rad': 111, 'str': 6, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0016', 'rad': 41, 'str': 8, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0017', 'rad': 117, 'str': 3, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0018', 'rad': 118, 'str': 13, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0019', 'rad': 140, 'str': 2, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0020', 'rad': 140, 'str': 5, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0021', 'rad': 162, 'str': 35, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0022', 'rad': 187, 'str': 0, 'has_unicode_sim': False},
    {'source': 'kokuji', 'id': '0023', 'rad': 140, 'str': 11, 'has_unicode_sim': False},
]

# === LOGIQUE D'IMPORTATION IRG 2024 ===
print("--- Importation IRG 2024 ---")

# 1. Chargement des attributs de tri (Le "Cerveau")
irg_sorting_data = {}
if os.path.exists(IRG_ATTR_FILE):
    try:
        with open(IRG_ATTR_FILE, 'r', encoding='utf-8') as f:
            irg_sorting_data = json.load(f)
        print(f"   [TRI] {len(irg_sorting_data)} définitions chargées (Radicaux/Traits).")
    except Exception as e:
        print(f"   [ERREUR LECTURE] {IRG_ATTR_FILE}: {e}")
else:
    print(f"   [ATTENTION] '{IRG_ATTR_FILE}' introuvable ! Lancez scrape_irg2024.py d'abord.")

# 2. Chargement de la liste validée (Le "Filtre")
if os.path.exists(IRG_VALID_FILE):
    try:
        with open(IRG_VALID_FILE, 'r', encoding='utf-8') as f:
            content = json.load(f)
            # Gestion souple du format JSON
            if isinstance(content, dict) and "successfully_downloaded_files" in content:
                valid_list = content["successfully_downloaded_files"]
            elif isinstance(content, list):
                valid_list = content
            else:
                valid_list = []
                
        print(f"   [FILTRE] {len(valid_list)} fichiers valides trouvés dans {IRG_VALID_FILE}.")
        
        # 3. Fusion et Ajout
        count_added = 0
        for filename in valid_list:
            # Nettoyage du nom de fichier (enlève .ttf si présent)
            filename = filename.replace('.ttf', '')
            
            # Format attendu: "irg2024-XXXXX"
            if not filename.startswith("irg2024-"):
                continue
                
            parts = filename.split('-')
            if len(parts) < 2: continue
            
            char_id = parts[1] # ex: "03502"
            
            # Récupération du tri
            rad = 215 # Par défaut (Inconnu/Fin)
            strokes = 0
            
            if char_id in irg_sorting_data:
                rad = irg_sorting_data[char_id]['rad']
                strokes = irg_sorting_data[char_id]['str']
            
            RAW_GLYPHWIKI_DATA.append({
                'source': 'irg2024',
                'id': char_id,
                'rad': rad,
                'str': strokes,
                'has_unicode_sim': False
            })
            count_added += 1
            
        print(f"   -> {count_added} caractères IRG ajoutés à la grille.")
        
    except Exception as e:
        print(f"   [ERREUR LECTURE] {IRG_VALID_FILE}: {e}")
else:
    print(f"   [ERREUR CRITIQUE] '{IRG_VALID_FILE}' est introuvable ! Aucun IRG ne sera généré.")


# --- SUITE DU SCRIPT STANDARD ---
FONT_STACK = '"BabelStone Han Extra", "BabelStone Han", "Hanazono Mincho B", "HanaMinB", "HanaMin A", "Hanazono Mincho A", "HanaMinA", "Plangothic P2", "TH-Tshyn-P1", "TH-Tshyn-P2", "SimSun-ExtB", "MingLiU-ExtB", "Nom Na Tong", "Noto Serif JP", "Source Han Serif", serif'

def download_and_extract():
    print(f"1. Téléchargement Unicode ({UNIHAN_URL})...")
    try:
        req = urllib.request.Request(UNIHAN_URL, data=None, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        return response.read()
    except Exception as e:
        print(f"   ERREUR DOWNLOAD: {e}")
        return None

def parse_unihan(zip_bytes):
    print("2. Analyse Unicode...")
    cjk_map = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        # Optimisation : on ne cherche que le fichier RadicalStroke
        candidates = [n for n in z.namelist() if 'RadicalStrokeCounts.txt' in n]
        if not candidates: candidates = [n for n in z.namelist() if not n.endswith('/')]
        
        for filename in candidates:
            if "ReadMe" in filename: continue
            with z.open(filename) as f:
                for line in f:
                    try: l = line.decode('utf-8').strip()
                    except: continue
                    if not l or l.startswith('#'): continue
                    
                    if 'kRSUnicode' in l:
                        p = l.split()
                        try:
                            cp = int(p[0].replace('U+',''), 16)
                            m = re.match(r"(\d+)'?\.(-?\d+)", p[2])
                            if m:
                                cjk_map.append({
                                    'rad': int(m.group(1)),
                                    'str': int(m.group(2)),
                                    'cp': cp,
                                    'char': chr(cp),
                                    'type': 'U',
                                    'font_file': None,
                                    'font_family': None
                                })
                        except: continue

    print("   -> Intégration GlyphWiki...")
    for item in RAW_GLYPHWIKI_DATA:
        s_key = item['source']
        r_id = item['id']
        prefix = GLYPHWIKI_DICTS.get(s_key, "GW")
        
        # Tri tertiaire via CP fictif (pour stabilité)
        dummy_cp = 90000000 + (hash(s_key + r_id) % 10000000)
        
        fname = f"{s_key}-{r_id}.ttf"
        fam = f"GW_{s_key}_{r_id}".replace('-', '_')
        
        cjk_map.append({
            'rad': item['rad'],
            'str': item['str'],
            'cp': dummy_cp,
            'char': '〓', # Placeholder
            'type': 'GW',
            'display_code': f"{prefix}+{r_id}",
            'font_file': fname,
            'font_family': fam
        })

    return cjk_map

def generate_grid_html(data):
    if not data: return
    print("3. Tri Global (Radical > Traits > Code)...")
    data.sort(key=lambda x: (x['rad'], x['str'], x['cp']))
    
    print(f"4. Génération {OUTPUT_FILE}...")
    
    css_fonts = ""
    seen_fonts = set()
    js_data = []
    
    for item in data:
        if item['type'] == 'U':
            hex_c = "U+" + hex(item['cp']).upper().replace('0X','')
            js_data.append([item['char'], hex_c, item['rad'], False, None])
        else:
            fam = item['font_family']
            if fam not in seen_fonts:
                css_fonts += f"@font-face {{ font-family: '{fam}'; src: url('{item['font_file']}'); }}\n"
                seen_fonts.add(fam)
            js_data.append([item['char'], item['display_code'], item['rad'], False, fam])
            
    json_str = json.dumps(js_data, ensure_ascii=False)
    
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>CJK Grid - Seamless Layout</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');
        {css_fonts}
        :root {{
            --page-w: 210mm; --page-h: 297mm;
            --cols: 10; --rows: 7;
            --unit-w: calc(210mm / 11); --unit-h: calc(297mm / 8);
            --cell-width: var(--unit-w); --cell-height: var(--unit-h);
            --margin-left: var(--unit-w); --margin-top: var(--unit-h);
            --font-size-char: 52px; --font-size-code: 9px;
        }}
        @page {{ size: A4; margin: 0; }}
        body {{ background-color: #e5e5e5; margin: 0; padding: 20px; font-family: {FONT_STACK}; display: flex; flex-direction: column; align-items: center; }}
        .sheet {{ width: var(--page-w); height: var(--page-h); background: white; position: relative; box-sizing: border-box; padding-top: var(--margin-top); padding-left: var(--margin-left); margin-bottom: 30px; overflow: hidden; break-after: page; page-break-after: always; }}
        .grid-container {{ display: flex; flex-wrap: wrap; align-content: flex-start; width: calc(var(--cell-width) * var(--cols)); height: calc(var(--cell-height) * var(--rows)); }}
        .cell {{ width: var(--cell-width); height: var(--cell-height); box-sizing: border-box; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; }}
        .char {{ font-size: var(--font-size-char); line-height: 1; margin-bottom: 4px; z-index: 2; }}
        .code {{ font-family: "Courier New", monospace; font-size: var(--font-size-code); color: #aaa; text-transform: uppercase; }}
        .radical-start {{ border: 2px solid #000 !important; box-sizing: border-box; }}
        .radical-label {{ position: absolute; top: 0; left: 0; font-size: 8px; font-weight: bold; color: white; background: black; padding: 1px 3px; font-family: sans-serif; z-index: 5; }}
        .controls {{ position: fixed; bottom: 20px; right: 20px; background: white; padding: 10px; border-radius: 30px; display: flex; gap: 10px; z-index: 9999; border: 1px solid #ccc; }}
        .btn {{ padding: 8px 16px; cursor: pointer; background: #16a34a; color: white; border: none; border-radius: 20px; font-weight: bold; }}
        @media print {{ body {{ background: none; padding: 0; margin: 0; display: block; }} .controls {{ display: none; }} .sheet {{ margin: 0; box-shadow: none; }} }}
    </style>
</head>
<body>
    <div id="sheets-container"></div>
    <div class="controls"><button class="btn" onclick="window.print()">🖨️ Imprimer</button></div>
    <script>
        const DATA = {json_str};
        const ITEMS_PER_PAGE = 70;
        const container = document.getElementById('sheets-container');

        function renderAll() {{
            let currentRadical = -1;
            let groupedByRad = [];
            let currentGroup = [];

            DATA.forEach((item) => {{
                const rad = item[2];
                if (rad !== currentRadical) {{
                    if (currentGroup.length > 0) groupedByRad.push(currentGroup);
                    currentGroup = [];
                    currentRadical = rad;
                    item.push(true);
                }} else item.push(false);
                currentGroup.push(item);
            }});
            if (currentGroup.length > 0) groupedByRad.push(currentGroup);

            groupedByRad.forEach(group => {{
                for (let i = 0; i < group.length; i += ITEMS_PER_PAGE) {{
                    const pageItems = group.slice(i, i + ITEMS_PER_PAGE);
                    const sheet = document.createElement('div');
                    sheet.className = 'sheet';
                    const grid = document.createElement('div');
                    grid.className = 'grid-container';
                    
                    pageItems.forEach(it => {{
                        const [char, code, rad, isNew, font] = it;
                        const cell = document.createElement('div');
                        cell.className = 'cell';
                        if (isNew) {{
                            cell.classList.add('radical-start');
                            cell.innerHTML += `<div class="radical-label">R${{rad}}</div>`;
                        }}
                        const style = font ? `style="font-family: '${{font}}'"` : "";
                        cell.innerHTML += `<div class="char" ${{style}}>${{char}}</div><div class="code">${{code}}</div>`;
                        grid.appendChild(cell);
                    }});
                    sheet.appendChild(grid);
                    container.appendChild(sheet);
                }}
            }});
        }}
        setTimeout(renderAll, 100);
    </script>
</body>
</html>
"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Terminé ! Ouvrez '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    zip_data = download_and_extract()
    if zip_data:
        data = parse_unihan(zip_data)
        if data:
            generate_grid_html(data)