# app/generate_templates.py

import pandas as pd
import itertools
from pathlib import Path

# Load your cleaned lexicon
LEXICON_PATH = Path("data/cleaned_pairs.csv")
OUTPUT_PATH = Path("data/expanded_pairs.csv")

df = pd.read_csv(LEXICON_PATH)
df["english"] = df["english"].str.lower()
df["ron"] = df["ron"].str.lower()

# Quick lookup dictionaries
en2ron = dict(zip(df["english"], df["ron"]))

def map_ron(english: str) -> str:
    """Map English to Ron if in lexicon, else placeholder."""
    return en2ron.get(english.lower().strip(), f"<ron:{english}>")

# --- Domains and templates ---
templates = {
    "greetings": [
        ("hello!", "shikam!"),
        ("good morning", "shikam kúro"),
        ("good evening", "shikam mána"),
        ("how are you?", "atan rúmày?"),
        ("how do you do?", "atan rúmày?"),
        ("it’s nice to meet you", "a ji shikam"),
        ("welcome, friend", "shikam, maɗafal"),
        ("are you fine?", "àtàn rúmày dá?"),
        ("we are fine", "naf á rúmày"),
    ],
    "market": [
        ("i want to buy yam", "á mí nàn fùs nàny"),
        ("i want to buy goat", "á mí nàn fùs átsiŋ"),
        ("i want to buy cloth", "á mí nàn fùs àtàmpul"),
        ("how much is this?", "híŋ dà?"),
        ("give me two yams", "à bèr nàny pí"),
        ("reduce the price", "kúrá shí"),
        ("do you have goat?", "à ká átsiŋ dá?"),
        ("yes, i have", "éh, mí ká"),
    ],
    "health": [
        ("i am sick", "á mí ròsh"),
        ("my head hurts", "shísh mí á jìŋ"),
        ("my stomach pains", "kúf mí á jìŋ"),
        ("do you have medicine?", "à ká àshè dá?"),
        ("i need water", "á mí nàn nùm"),
        ("the child is coughing", "nufuy á kòr"),
        ("i am feeling better", "á mí rúmày"),
        ("where is the clinic?", "à shí nàshpítì?"),
    ],
    "travel": [
        ("where is the road?", "à shí kúndù?"),
        ("where is the market?", "à shí shíngà?"),
        ("i want to go to jos", "á mí nàn rúmà jos"),
        ("how far is the school?", "nà shí kúndù dá?"),
        ("is this the right road?", "à kúndù shí dá?"),
        ("stop here", "bèr nàn"),
        ("go straight", "rúmà dàn"),
        ("turn left", "kúrá shí"),
        ("turn right", "kúrá dá"),
    ],
    "school": [
        ("the teacher is here", "málám á nàn"),
        ("the student is writing", "nufuy á kúrá"),
        ("we are learning ron", "naf á shí ron"),
        ("i am reading a book", "á mí shí nàlì"),
        ("where is the classroom?", "à shí kúrá?"),
        ("the children are singing", "nufuy á rúmà"),
        ("open your book", "kúrà nàlì mí"),
        ("close the door", "kúrà kùtù"),
        ("teacher, explain again", "málám, bèr rúmà"),
    ],
}

# --- Slot-filling expansions ---
market_items = ["yam", "goat", "cloth", "dress", "fish", "book"]
market_ron = {
    "yam": "nàny",
    "goat": "átsiŋ",
    "cloth": "àtàmpul",
    "dress": "fúm",
    "fish": "ànshì",
    "book": "nàlì",
}

slot_templates = [
    "i want to buy {item}",
    "how much is this {item}?",
    "do you have {item}?",
    "give me two {item}s",
]

slot_pairs = []
for item, ron_word in market_ron.items():
    for tmpl in slot_templates:
        en = tmpl.format(item=item)
        ron = en2ron.get(en, None)
        if not ron:
            # Build Ron template roughly (can be refined)
            if "buy" in en:
                ron = f"á mí nàn fùs {ron_word}"
            elif "how much" in en:
                ron = f"híŋ {ron_word} dá?"
            elif "do you have" in en:
                ron = f"à ká {ron_word} dá?"
            elif "give me two" in en:
                ron = f"à bèr {ron_word} pí"
        slot_pairs.append((en, ron))

# --- Combine all ---
expanded = []
for domain, pairs in templates.items():
    for en, ron in pairs:
        expanded.append({"english": en, "ron": ron, "domain": domain, "pos": "general"})

for en, ron in slot_pairs:
    expanded.append({"english": en, "ron": ron, "domain": "market", "pos": "general"})

expanded_df = pd.DataFrame(expanded)
expanded_df.to_csv(OUTPUT_PATH, index=False)
print(f"Expanded dataset saved to {OUTPUT_PATH}, size={len(expanded_df)}")
