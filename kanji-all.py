import urllib.request
import zipfile
import io
import re
import os
import json

# --- CONFIGURATION ---
UNIHAN_URL = "https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip"
OUTPUT_FILE = "ALL_KANJI.html"
IRG_DATA_FILE = "irg2024_attributes.json" # Fichier contenant les radicaux/traits IRG

# 1. CONFIGURATION DES DICTIONNAIRES GLYPHWIKI
GLYPHWIKI_DICTS = {
    "kokuji": "K",         # 国字の字典
    "wasei-kanji": "W",             # 和製漢字の辞典
    "kadokawa-daijigen": "KD",      # 角川大字源国字一覧
    "nihonjin-no-tsukutta": "N",    # 日本人の作った漢字
    "shincho-nihongo": "S",         # 新潮日本語漢字辞典
    "hokke": "H",                   # 法華三大部難字記
    "chukajikai": "Z",              # 中華字海 (Z pour Zhōnghuá)
    "kozouji-jiten": "G",           # 古壮字字典
    "shinsen-jikyo": "SJ",          # 新撰字鏡-抄録本
    "toshoryo-ruiju": "T",         # 図書寮本類聚名義抄
    "kozanji-tenrei": "KT",         # 高山寺本篆隷万象名義
    "chunom-jiten": "V",            # 字喃字典 (V pour Vietnam)
    "daijiten-chunom": "VD",        # 大字典字喃
    "jiten-chunom-tekiin": "J",     # 字典字喃摘引
    "joshin-bun-jiten": "JU",       # 女真文辞典 (Jurchen)
    "buyi-fangkuai": "B",           # 布依方块古文字 (Bouyei)
    "china-jingyu": "C",            # 中国京语词典
    "dkw": "DKW",                   # 大漢和辞典
    "ids": "IDS",
    "irg2024": "IRG"                # AJOUT : Working Set 2024
}

# 2. LISTE DES CARACTÈRES MANUELS (Exemples)
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

# === AJOUT AUTOMATIQUE IRG 2024 ===
print("--- Chargement des données IRG 2024 ---")
irg_attributes = {}

# On essaie de charger les vrais attributs (Radical/Traits) depuis le JSON
if os.path.exists(IRG_DATA_FILE):
    print(f"   Fichier '{IRG_DATA_FILE}' trouvé ! Chargement des détails...")
    try:
        with open(IRG_DATA_FILE, 'r', encoding='utf-8') as f:
            irg_attributes = json.load(f)
    except Exception as e:
        print(f"   Erreur de lecture du JSON ({e}). Utilisation des valeurs par défaut.")
else:
    print(f"   ⚠️ '{IRG_DATA_FILE}' introuvable.")
    print("   Les caractères IRG seront classés à la fin (Radical 215).")
    print("   (Utilisez le script 'scrape_irg2024.py' pour récupérer les vraies données)")

# Boucle pour ajouter les 4674 caractères IRG
for i in range(1, 4675):
    str_id = f"{i:05d}" # Format 00001, 00002...
    
    # Valeurs par défaut (si pas dans le JSON)
    rad = 216
    strokes = 0
    
    # Si on a les infos du scraper
    if str_id in irg_attributes:
        rad = irg_attributes[str_id]['rad']
        strokes = irg_attributes[str_id]['str']
    
    RAW_GLYPHWIKI_DATA.append({
        'source': 'irg2024',
        'id': str_id,
        'rad': rad,
        'str': strokes,
        'has_unicode_sim': False
    })

# 3. POLICES
FONT_STACK = '"BabelStone Han Extra", "BabelStone Han", "Hanazono Mincho B", "HanaMinB", "HanaMin A", "Hanazono Mincho A", "HanaMinA", "TH-Tshyn-P1", "TH-Tshyn-P2", "SimSun-ExtB", "MingLiU-ExtB", "Nom Na Tong", "Noto Serif JP", "Source Han Serif", serif'

def download_and_extract():
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
        print(f"   ERREUR: Impossible de télécharger Unihan. {e}")
        return None

def parse_unihan(zip_bytes):
    print("2. Analyse des données...")
    cjk_map = []

    # A. Données Unicode Officielles
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        file_list = [n for n in z.namelist() if not n.endswith('/') and not n.startswith('__MACOSX') and not '/.' in n]

        for filename in file_list:
            # Only process relevant Unihan files that contain kRSUnicode data
            if not filename.startswith('Unihan_'):
                continue
            if "ReadMe" in filename or "History" in filename:
                continue

            with z.open(filename) as f:
                for line in f:
                    try:
                        line_str = line.decode('utf-8').strip()
                    except:
                        continue
                    if not line_str or line_str.startswith('#'):
                        continue

                    # Use tab split for Unihan files for more robustness
                    parts = line_str.split('\t')

                    # Check if it's a kRSUnicode line and has enough parts
                    if len(parts) >= 3 and parts[1] == 'kRSUnicode':
                        try:
                            code_str = parts[0].replace('U+', '')
                            code_point = int(code_str, 16)
                            char = chr(code_point)
                            rs_data = parts[2] # Radical-Stroke data is the third part

                            match = re.match(r"(\d+)'?\.(\-?\d+)", rs_data)
                            if not match:
                                continue # Skip if radical-stroke data doesn't match expected pattern

                            # Check if the character falls into the custom font range
                            if 0x323B0 <= code_point <= 0x3347F:
                                hex_code_lower = hex(code_point)[2:].lower() # Convert to lowercase hex
                                cjk_map.append({
                                    'rad': int(match.group(1)),
                                    'str': int(match.group(2)),
                                    'cp': code_point,
                                    'char': '〓',   # Placeholder for custom font
                                    'type': 'U_CUSTOM_FONT', # Custom Unicode font
                                    'display_code': f"U+{hex(code_point).upper()[2:]}",
                                    'font_file': f"u{hex_code_lower}.ttf",
                                    'font_family': f"U_CUSTOM_FONT_{hex(code_point).upper()[2:]}"
                                })
                            else:
                                cjk_map.append({
                                    'rad': int(match.group(1)),
                                    'str': int(match.group(2)),
                                    'cp': code_point,
                                    'char': char,
                                    'type': 'U', # Unicode
                                    'font_file': None
                                })
                        except Exception as e:
                            # For debugging, you could print(f"   ERROR parsing line: {line_str} - {e}")
                            continue


    # B. Ajout des données GlyphWiki
    print("   -> Intégration des données GlyphWiki...")
    count_k = 0
    
    for item in RAW_GLYPHWIKI_DATA:
        if item.get('has_unicode_sim') is True: continue
            
        source_key = item['source']
        raw_id = item['id']
        prefix = GLYPHWIKI_DICTS.get(source_key, "GW")
        
        # CP fictif pour le tri
        dummy_cp = 90000000 + (hash(source_key + raw_id) % 10000000)
        
        # Le fichier .ttf DOIT s'appeler ainsi : "source-id.ttf"
        font_filename = f"{source_key}-{raw_id}.ttf"
        safe_family = f"GW_{source_key}_{raw_id}".replace('-', '_')
        
        cjk_map.append({
            'rad': item['rad'],
            'str': item['str'],
            'cp': dummy_cp,
            'char': '〓',
            'type': 'GW',
            'display_code': f"{prefix}+{raw_id}",
            'font_file': font_filename,
            'font_family': safe_family
        })
        count_k += 1

    print(f"   TOTAL : {len(cjk_map)} caractères prêts (dont {count_k} GlyphWiki).")
    return cjk_map

def generate_grid_html(data):
    if not data: 
        print("   ERREUR: Aucune donnée à générer.")
        return

    print("3. Tri par Busyu...")
    data.sort(key=lambda x: (x['rad'], x['str'], x['cp']))
    
    print(f"4. Génération de la grille A4 (70 chars) : {OUTPUT_FILE}...")
    
    custom_fonts_css = ""
    processed_fonts = set()
    js_data = []
    
    for item in data:
        if item['type'] == 'U':
            hex_code = "U+" + hex(item['cp']).upper().replace('0X', '')
            js_data.append([item['char'], hex_code, item['rad'], False, None])
        else:
            font_fam = item['font_family']
            if font_fam not in processed_fonts:
                custom_fonts_css += f"@font-face {{ font-family: '{font_fam}'; src: url('{item['font_file']}'); }}\n"
                processed_fonts.add(font_fam)
            
            js_data.append([item['char'], item['display_code'], item['rad'], False, font_fam])
    
    json_data = json.dumps(js_data, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>CJK Grid - 70 Chars Seamless</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');

        /* === POLICES GLYPHWIKI ET CUSTOM UNICODE DYNAMIQUES === */
        {custom_fonts_css}

        :root {{
            --a4-width: 210mm;
            --a4-height: 297mm;

            /* CONFIG 7x9 = 63 */
            --cols: 7;
            --rows: 9;

            /* MARGES ASYMÉTRIQUES SEAMLESS */
            --cell-width: 30mm;  /* 210 / 11 */
            --cell-height: 29.7mm; /* 297 / 8 */
            --margin-left: 5mm;
            --margin-top: 5mm;

            --font-size-char: 58px;
            --font-size-code: 15px;
        }}

        @page {{
            size: A4;
            margin: 0;
        }}

        body {{
            background-color: #e5e5e5;
            margin: 0;
            padding: 20px;
            font-family: {FONT_STACK};
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        /* UI */
        .controls {{
            position: fixed; bottom: 20px; right: 20px;
            background: white; padding: 10px 20px;
            border-radius: 30px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            display: flex; gap: 10px; align-items: center; z-index: 9999;
            font-family: sans-serif; border: 1px solid #ccc;
        }}
        .btn {{
            padding: 8px 16px; cursor: pointer; background: #2563eb; color: white;
            border: none; border-radius: 20px; font-weight: bold;
        }}
        .btn-print {{ background: #16a34a; }}

        .font-warning {{
            background: #fff; border-left: 5px solid #2563eb; color: #333;
            padding: 15px; margin-bottom: 20px; border-radius: 4px;
            max-width: 210mm; font-family: sans-serif; font-size: 13px;
        }}

        /* FEUILLE */
        .sheet {{
            width: var(--a4-width);
            height: var(--a4-height);
            background: white;
            position: relative;
            box-sizing: border-box;

            padding-top: var(--margin-top);
            padding-left: var(--margin-left);
            padding-right: 0;
            padding-bottom: 0;

            margin-bottom: 30px;
            overflow: hidden;

            break-after: page;
            page-break-after: always;
        }}

        .grid-container {{
            display: flex;
            flex-wrap: wrap;
            align-content: flex-start;
            width: calc(var(--cell-width) * var(--cols));
            height: calc(var(--cell-height) * var(--rows));
        }}

        .cell {{
            width: var(--cell-width);
            height: var(--cell-height);
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
        }}

        .char {{
            font-size: var(--font-size-char);
            line-height: 1;
            margin-bottom: 4px;
            z-index: 2;
        }}

        .code {{
            font-family: "Courier New", monospace;
            font-size: var(--font-size-code);
            color: #aaa;
            text-transform: uppercase;
        }}

        .radical-start {{
            border: 2px solid #000 !important;
            border-radius: 0;
            box-sizing: border-box;
        }}

        .radical-label {{
            position: absolute; top: 0; left: 0;
            font-size: 8px; font-weight: bold; color: white; background: black;
            padding: 1px 3px; font-family: sans-serif; z-index: 5;
        }}

        @media print {{
            body {{ background: none; padding: 0; margin: 0; display: block; }}
            .controls, .font-warning {{ display: none !important; }}
            .sheet {{
                margin: 0; box-shadow: none;
                page-break-after: always;
            }}
        }}
    </style>
</head>
<body>

    <div class="font-warning">
        <strong>Mode Dictionnaires Multiples</strong><br>
        Pour que les caractères <b>K+, H+, Z+...</b> et les caractères Unicode personnalisés s'affichent, les fichiers <code>.ttf</code> correspondants<br>
        (ex: <code>kokuji-no-jiten-1034.ttf</code> ou <code>u323c7.ttf</code>) doivent être placés dans le même dossier que ce fichier HTML.
    </div>

    <div id="sheets-container"></div>

    <div class="controls">
        <div id="status">Génération...</div>
        <button class="btn btn-print" onclick="window.print()">🖨️ Imprimer</button>
    </div>

    <script>
        const DATA = {json_data};

        const COLS = 10;
        const ROWS = 7;
        const ITEMS_PER_PAGE = COLS * ROWS;

        const container = document.getElementById('sheets-container');
        const statusEl = document.getElementById('status');

        function renderAll() {{
            container.innerHTML = '';

            let currentRadical = -1;
            let sheetCount = 0;

            function createSheet(items) {{
                sheetCount++;
                const sheet = document.createElement('div');
                sheet.className = 'sheet';

                const grid = document.createElement('div');
                grid.className = 'grid-container';

                items.forEach(item => {{
                    const char = item[0];
                    const displayCode = item[1];
                    const rad = item[2];
                    const isNewRad = item[3];
                    const fontFam = item[4];

                    const cell = document.createElement('div');
                    cell.className = 'cell';

                    if (isNewRad) {{
                        cell.classList.add('radical-start');
                        cell.innerHTML += `<div class="radical-label">R${{rad}}</div>`;
                    }}

                    let styleStr = "";
                    if (fontFam) {{
                        styleStr = `style="font-family: '${{fontFam}}';"`;
                    }}

                    cell.innerHTML += `
                        <div class="char" ${{styleStr}}>${{char}}</div>
                        <div class="code">${{displayCode}}</div>
                    `;
                    grid.appendChild(cell);
                }});

                sheet.appendChild(grid);
                container.appendChild(sheet);
            }}

            let groupedByRad = [];
            let currentGroup = [];

            DATA.forEach((item) => {{
                const rad = item[2];
                if (rad !== currentRadical) {{
                    if (currentGroup.length > 0) groupedByRad.push(currentGroup);
                    currentGroup = [];
                    currentRadical = rad;
                    item.push(true);
                }} else {{
                    item.push(false);
                }}
                currentGroup.push(item);
            }});
            if (currentGroup.length > 0) groupedByRad.push(currentGroup);

            groupedByRad.forEach(group => {{
                for (let i = 0; i < group.length; i += ITEMS_PER_PAGE) {{
                    const pageItems = group.slice(i, i + ITEMS_PER_PAGE);
                    createSheet(pageItems);
                }}
            }});

            statusEl.textContent = `${{sheetCount}} Pages`;
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
