import csv
import os

# Nom du fichier CSV généré précédemment
CSV_FILE = "cjk_characters.csv"

# --- TABLE DE RÉFÉRENCE : Nombre de traits des 214 Radicaux Kangxi ---
# L'index de la liste correspond au numéro du radical (0 est vide pour aligner R1 à l'index 1).
# R1-R6: 1 trait, R7-R29: 2 traits, etc.
RADICAL_STROKE_COUNTS = [0] + \
    [1]*6 +   [2]*23 +  [3]*31 +  [4]*34 +  [5]*23 + \
    [6]*29 +  [7]*20 +  [8]*9 +   [9]*11 +  [10]*8 + \
    [11]*6 +  [12]*4 +  [13]*4 +  [14]*2 +  [15]*1 + \
    [16]*2 +  [17]*1

def load_stroke_database(csv_path):
    """
    Charge le CSV en mémoire.
    Retourne un dictionnaire : { 'Caractère' : Nombre_Total_Traits }
    """
    db = {}
    print(f"Chargement de {csv_path}...")

    if not os.path.exists(csv_path):
        print(f"ERREUR : Le fichier {csv_path} est introuvable.")
        return {}

    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                char = row['char']
                try:
                    rad_idx = int(row['rad'])
                    extra_strokes = int(row['str'])

                    # Sécurité si le radical est hors limites (rare)
                    if 1 <= rad_idx <= 214:
                        base_strokes = RADICAL_STROKE_COUNTS[rad_idx]
                        total = base_strokes + extra_strokes
                        db[char] = total
                        count += 1
                except ValueError:
                    continue
        print(f"   -> {count} caractères chargés en mémoire.")
        return db
    except Exception as e:
        print(f"Erreur de lecture : {e}")
        return {}

def analyze_text(text, db):
    """Affiche le nombre de coups pour chaque caractère d'une chaîne."""
    print(f"\n--- Analyse de la chaîne : \"{text}\" ---")
    total_string_strokes = 0

    for char in text:
        # On ignore les espaces ou caractères non-CJK si absents de la base
        if char in db:
            strokes = db[char]
            total_string_strokes += strokes
            print(f"'{char}' : {strokes} coups")
        else:
            print(f"'{char}' : ? (Non trouvé dans le CSV)")

    print("-" * 30)
    print(f"TOTAL pour la phrase : {total_string_strokes} coups")

if __name__ == "__main__":
    # 1. Chargement de la base
    stroke_db = load_stroke_database(CSV_FILE)

    if stroke_db:
        # 2. Test avec votre exemple
        sample_text = "全漢字辞典"
        analyze_text(sample_text, stroke_db)

        # 3. Mode interactif (optionnel)
        while True:
            user_input = input("\nEntrez un autre mot (ou 'q' pour quitter) : ")
            if user_input.lower() == 'q':
                break
            analyze_text(user_input, stroke_db)
