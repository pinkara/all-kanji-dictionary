import urllib.request
import zipfile
import io
import re
import os
import sys

# --- CONFIGURATION ---
UNIHAN_URL = "https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip"
OUTPUT_FILE = "cjk_full_busyu_ja_en.html"

# Liste des 214 Radicaux Kangxi (Kangxi Radicals)
KANGXI_RADICALS = [
    "一", "丨", "丶", "丿", "乙", "亅", "二", "亠", "人", "儿", "入", "八", "冂", "冖", "冫", "几", "凵", "刀", "力", "勹", "匕", "匚", "匸", "十", "卜", "卩", "厂", "厶", "又",
    "口", "囗", "土", "士", "夂", "夊", "夕", "大", "女", "子", "宀", "寸", "小", "尢", "尸", "屮", "山", "巛", "工", "己", "巾", "干", "幺", "广", "廴", "廾", "弋", "弓", "彐", "彡", "彳",
    "心", "戈", "戶", "手", "支", "攴", "文", "斗", "斤", "方", "无", "日", "曰", "月", "木", "欠", "止", "歹", "殳", "毋", "比", "毛", "氏", "气", "水", "火", "爪", "父", "爻", "爿", "片", "牙", "牛", "犬",
    "玄", "玉", "瓜", "瓦", "甘", "生", "用", "田", "疋", "疒", "癶", "白", "皮", "皿", "目", "矛", "矢", "石", "示", "禸", "禾", "穴", "立", "竹", "米", "糸", "缶", "网", "羊", "羽", "老", "而", "耒", "耳", "聿", "肉", "臣", "自", "至", "臼", "舌", "舛", "舟", "艮", "色", "艸", "虍", "虫", "血", "行", "衣", "襾",
    "見", "角", "言", "谷", "豆", "豕", "豸", "貝", "赤", "走", "足", "身", "車", "辛", "辰", "辵", "邑", "酉", "釆", "里",
    "金", "長", "門", "阜", "隶", "隹", "雨", "青", "非",
    "面", "革", "韋", "韭", "音", "頁", "風", "飛", "食", "首", "香",
    "馬", "骨", "高", "髟", "鬥", "鬯", "鬲", "鬼",
    "魚", "鳥", "鹵", "鹿", "麥", "麻",
    "黃", "黍", "黑", "黹",
    "黽", "鼎", "鼓", "鼠",
    "鼻", "齊",
    "齒",
    "龍", "龜",
    "龠"
]

def download_and_extract():
    print(f"1. Downloading {UNIHAN_URL}...")
    try:
        req = urllib.request.Request(
            UNIHAN_URL, 
            data=None, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        response = urllib.request.urlopen(req)
        zip_data = response.read()
        print(f"   Download complete ({len(zip_data)/1024/1024:.2f} MB).")
        return zip_data
    except Exception as e:
        print(f"   CRITICAL ERROR: Cannot download Unihan. {e}")
        return None

def parse_unihan(zip_bytes):
    print("2. Scanning ALL files in ZIP...")
    cjk_map = []
    
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        # On liste tous les fichiers qui pourraient contenir du texte
        file_list = [n for n in z.namelist() if not n.endswith('/') and not n.startswith('__MACOSX') and not '/.' in n]
        
        print(f"   {len(file_list)} files found in archive.")
        
        for filename in file_list:
            if "ReadMe" in filename or "History" in filename:
                continue

            print(f"   -> Inspecting: {filename}")
            
            with z.open(filename) as f:
                krs_in_this_file = 0
                debug_lines = []
                
                for line in f:
                    try:
                        line_str = line.decode('utf-8').strip()
                    except:
                        continue
                    
                    if not line_str or line_str.startswith('#'):
                        continue
                    
                    if len(debug_lines) < 3:
                        debug_lines.append(line_str)

                    # Recherche de la propriété kRSUnicode
                    if 'kRSUnicode' in line_str:
                        krs_in_this_file += 1
                        
                        parts = line_str.split()
                        try:
                            idx = parts.index('kRSUnicode')
                            
                            code_str = parts[0].replace('U+', '')
                            code_point = int(code_str, 16)
                            char = chr(code_point)
                            
                            if len(parts) > idx + 1:
                                rs_data = parts[idx + 1]
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
                        except:
                            continue
                
                if krs_in_this_file > 0:
                    print(f"      SUCCESS! {krs_in_this_file} entries found in {filename}.")

    print(f"   TOTAL: {len(cjk_map)} characters extracted.")
    return cjk_map

def generate_html(data):
    if not data:
        print("   ERROR: No data to generate.")
        return

    print("3. Sorting data...")
    data.sort(key=lambda x: (x['rad'], x['str'], x['cp']))
    
    print(f"4. Generating {OUTPUT_FILE}...")
    
    # HTML en Japonais / Anglais
    html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CJK Unified Ideographs Dictionary (Busyu Order) / 全訳CJK統合漢字辞典 (部首順)</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Noto+Serif+JP:wght@400;700&display=swap');
        
        :root { 
            --bg: #0f172a; 
            --text: #e2e8f0; 
            --accent: #3b82f6; 
            --border: #1e293b; 
            --rad-bg: #1e293b; 
            --sidebar-bg: #020617;
        }
        
        body { 
            font-family: "HanaMinA", "HanaMinB", "SimSun-ExtB", "Noto Serif JP", "Noto Sans CJK JP", serif; 
            background: var(--bg); 
            color: var(--text); 
            margin: 0; 
            padding: 0; 
        }
        
        /* Sidebar */
        .sidebar { 
            position: fixed; top: 0; left: 0; width: 220px; height: 100vh; 
            overflow-y: auto; background: var(--sidebar-bg); 
            border-right: 1px solid var(--border); 
            padding: 10px; font-size: 13px; font-family: "Noto Sans JP", sans-serif;
        }
        .sidebar::-webkit-scrollbar { width: 6px; background: var(--sidebar-bg); }
        .sidebar::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
        
        .sidebar-header {
            padding: 10px 5px; color: #fff; font-weight: bold; font-size: 14px;
            border-bottom: 1px solid #334155; margin-bottom: 10px;
        }
        
        .sidebar a { 
            display: block; color: #94a3b8; text-decoration: none; 
            padding: 4px 8px; border-radius: 4px; margin-bottom: 1px; 
            transition: background 0.2s;
        }
        .sidebar a:hover { background: var(--accent); color: #fff; }
        
        /* Main Content */
        .main { margin-left: 220px; padding: 40px; }
        
        h1 { 
            font-weight: 300; color: #fff; 
            border-bottom: 1px solid var(--border); padding-bottom: 20px; 
            font-family: "Noto Sans JP", sans-serif;
        }
        
        .desc { color: #94a3b8; margin-bottom: 40px; font-family: "Noto Sans JP", sans-serif; font-size: 0.9em; }
        
        /* Radical Section */
        .radical-section { margin-bottom: 60px; scroll-margin-top: 20px; }
        
        .rad-header { 
            background: var(--rad-bg); padding: 15px 25px; border-radius: 8px; 
            font-size: 2.2em; margin-bottom: 20px; 
            display: flex; align-items: center; gap: 20px; 
            border-left: 5px solid var(--accent); 
        }
        
        .rad-info { 
            display: flex; flex-direction: column;
        }
        .rad-info-main { font-size: 0.4em; color: #fff; font-weight: bold; }
        .rad-info-sub { font-size: 0.3em; color: #94a3b8; font-family: "Noto Sans JP", sans-serif; }
        
        /* Strokes */
        .stroke-group { margin-bottom: 25px; }
        .stroke-label { 
            color: #64748b; font-size: 0.9em; margin-bottom: 10px; 
            font-weight: bold; border-bottom: 1px solid #1e293b; padding-bottom: 4px; 
            font-family: "Noto Sans JP", sans-serif;
        }
        
        /* Grid */
        .grid { 
            display: grid; grid-template-columns: repeat(auto-fill, minmax(52px, 1fr)); gap: 8px; 
        }
        .char-box { 
            aspect-ratio: 1; display: flex; align-items: center; justify-content: center; 
            font-size: 32px; background: #1e293b; border-radius: 6px; 
            transition: transform 0.1s, background 0.1s; cursor: pointer; color: #cbd5e1;
        }
        .char-box:hover { 
            background: var(--accent); color: white; transform: scale(1.15); 
            z-index: 10; box-shadow: 0 4px 12px rgba(0,0,0,0.5); 
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">部首索引 / RADICAL INDEX</div>
    """
    
    # Sidebar
    for i, rad_char in enumerate(KANGXI_RADICALS):
        rad_num = i + 1
        html += f'<a href="#rad-{rad_num}">R{rad_num} {rad_char}</a>'
    
    html += """
    </div>
    <div class="main">
        <h1>
            CJK統合漢字 (基本 + 拡張A-J)<br>
            <span style="font-size:0.6em; color:#64748b;">CJK Unified Ideographs (Base + Ext A-J)</span>
        </h1>
        <p class="desc">
            Unicode公式データベース生成 (Generated from Official Unicode Database).<br>
            ソート順 (Sort): 康熙部首 (Kangxi Radical) → 画数 (Strokes) → コードポイント (Code Point).
        </p>
    """
    
    current_rad = -1
    current_stroke = -999
    
    for item in data:
        rad = item['rad']
        strokes = item['str']
        char = item['char']
        hex_code = hex(item['cp']).upper().replace('0X', '')
        
        # Nouveau Radical
        if rad != current_rad:
            if current_rad != -1:
                html += '</div></div></div>'
            current_rad = rad
            current_stroke = -999
            rad_char = KANGXI_RADICALS[rad-1] if 0 < rad <= 214 else f"R{rad}"
            
            html += f"""
            <div id="rad-{rad}" class="radical-section">
                <div class="rad-header">
                    <span>{rad_char}</span>
                    <div class="rad-info">
                        <span class="rad-info-main">Radical {rad}</span>
                        <span class="rad-info-sub">部首 {rad}</span>
                    </div>
                </div>
            """
        
        # Nouveaux Traits
        if strokes != current_stroke:
            if current_stroke != -999:
                html += '</div></div>'
            current_stroke = strokes
            
            # Label bilingue
            if strokes == 0:
                label = "部首のみ / Radical only (0)"
            else:
                label = f"+{strokes} 画 / +{strokes} Strokes"
                
            html += f"""
            <div class="stroke-group">
                <div class="stroke-label">{label}</div>
                <div class="grid">
            """
        
        html += f'<div class="char-box" title="U+{hex_code}">{char}</div>'

    html += "</div></div></div></div></body></html>"
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Finished! Open '{OUTPUT_FILE}' to see the result.")

if __name__ == "__main__":
    zip_data = download_and_extract()
    if zip_data:
        data = parse_unihan(zip_data)
        if data:
            generate_html(data)
