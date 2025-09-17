# import necessary libraries
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger("uvicorn.error")

class RonTranslator:
    def __init__(self, dict_path="data/cleaned_pairs.csv", embedding_model="all-MiniLM-L6-v2"):
        self.df = pd.read_csv(dict_path)
        # Pre-normalize: ensure column type to be strings and in lower case
        self.df["english"] = self.df["english"].astype(str).str.lower()
        self.df["ron"] = self.df["ron"].astype(str).str.lower()

        # Dictionaries
        self.en2ron = dict(zip(self.df["english"], self.df["ron"]))
        self.ron2en = dict(zip(self.df["ron"], self.df["english"]))

        # Load embedding model
        logger.info("Loading embedding model: %s", embedding_model)
        self.model = SentenceTransformer(embedding_model)

        # English embeddings
        self.english_texts = self.df["english"].tolist()
        self.english_embeddings = self.model.encode(self.english_texts, convert_to_tensor=True)

        # Ron embeddings
        self.ron_texts = self.df["ron"].tolist()
        self.ron_embeddings = self.model.encode(self.ron_texts, convert_to_tensor=True)

        logger.info("Embeddings computed: %d en, %d ron", len(self.english_embeddings), len(self.ron_embeddings))

    def exact_lookup(self, text: str, direction: str) -> Optional[str]:
        key = text.strip().lower()
        if direction == "en-ron":
            return self.en2ron.get(key)
        elif direction == "ron-en":
            return self.ron2en.get(key)
        return None

    def phrase_match(self, text: str, direction: str) -> Optional[str]:
        dictionary = self.en2ron if direction == "en-ron" else self.ron2en
        words = text.strip().lower().split()
        for size in range(len(words), 0, -1):  # longest first
            for i in range(len(words) - size + 1):
                phrase = " ".join(words[i:i+size])
                if phrase in dictionary:
                    return dictionary[phrase]
        return None

    def retrieval_fallback(self, text: str, direction: str, top_k: int = 3) -> List[Tuple[str, str, float]]:
        query_emb = self.model.encode(text, convert_to_tensor=True)
        results = []

        if direction == "en-ron":
            hits = util.semantic_search(query_emb, self.english_embeddings, top_k=top_k)[0]
            for hit in hits:
                cid = hit["corpus_id"]
                results.append((self.english_texts[cid], self.ron_texts[cid], float(hit["score"])))

        elif direction == "ron-en":
            hits = util.semantic_search(query_emb, self.ron_embeddings, top_k=top_k)[0]
            for hit in hits:
                cid = hit["corpus_id"]
                results.append((self.ron_texts[cid], self.english_texts[cid], float(hit["score"])))

        return results

    def translate(self, text: str, direction: str = "en-ron"):
        """
        Translate text in given direction.
        direction = "en-ron" (default) or "ron-en"
        """
        text = text.strip().lower()

        # 1. Exact match
        exact = self.exact_lookup(text, direction)
        if exact:
            return {"method": "exact", "translation": exact}

        # 2. Phrase match
        phrase = self.phrase_match(text, direction)
        if phrase:
            return {"method": "phrase", "translation": phrase}

        # 3. Retrieval fallback
        retrievals = self.retrieval_fallback(text, direction)
        if retrievals:
            return {
                "method": "retrieval",
                "translation": retrievals[0][1],  # top-1 suggestion
                "alternatives": retrievals
            }

        return {"method": "none", "translation": None, "alternatives": []}
