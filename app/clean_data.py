# import necessary libraries
from more_itertools import only
import pandas as pd
import unicodedata
import re
import spacy


# Load English spaCy model for POS (Part-of-Speech) tagging 
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    print(f"Error loading spaCy model: {e}")
    nlp = None

# function to clean and preprocess data
def normalize_text(text: str) -> str:
    """Lowercase, strip, normalize Unicode, remove extra spaces/punct spacing."""
    text = text.strip().lower()
    text = unicodedata.normalize("NFC", text)  # canonical form
    text = re.sub(r"\s+", " ", text)  # collapse spaces
    return text

# function to add POS and Domain columns given a dataframe
def add_pos_domain(df: pd.DataFrame) -> pd.DataFrame:
    """Add POS (for English side) and placeholder Domain column."""
    if nlp:
        pos_tags = []
        for sentence in df["english"]:
            doc = nlp(sentence)
            # Simple heuristic: take POS of root token (main word)
            root_pos = [token.pos_ for token in doc if token.head == token][0]
            pos_tags.append(root_pos)
        df["pos"] = pos_tags
    else:
        df["pos"] = "unknown"

    # Placeholder: mark all as 'general' for now, you can refine manually later
    df["domain"] = "general"
    return df


# Preprocess data function
def preprocess_dataset(input_path="data/english_ron_pair.tsv", output_path="data/cleaned_pairs.csv") -> pd.DataFrame:
    # Read raw data
    df = pd.read_csv(input_path, sep="\t")

    # Convert columns to string and normalize text
    df["english"] = df["en"].astype(str).apply(normalize_text)
    df["ron"] = df["ron"].astype(str).apply(normalize_text)

    # Add POS and Domain columns and save to new cleaned_pairs.csv as output
    df = add_pos_domain(df)
    df.to_csv(output_path, index=False)
    return df




# Run this script if only this file is executed directly
if __name__ == "__main__":
    df = preprocess_dataset()
    print("Your cleaned & normalized dataset is saved to data/cleaned_pairs.csv")