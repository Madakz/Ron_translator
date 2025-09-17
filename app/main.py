# app/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import logging
import os
from pathlib import Path
import pandas as pd

# clean data module
from app.clean_data import preprocess_dataset
# local translator
from app.translator import RonTranslator

logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="Ron Translator API",
    description="Translate English <-> Ron with dictionary, phrase match, and retrieval fallback.",
    version="0.2.0"
)

# Singleton translator instance
TRANSLATOR: Optional[RonTranslator] = None

# Feedback CSV
FEEDBACK_CSV = Path("data/feedback_queue.csv")
FEEDBACK_CSV.parent.mkdir(parents=True, exist_ok=True)
if not FEEDBACK_CSV.exists():
    pd.DataFrame(columns=["english", "ron", "direction", "user_id", "notes", "timestamp"]).to_csv(FEEDBACK_CSV, index=False)

# --- Request/Response Models ---
class TranslateRequest(BaseModel):
    text: str
    direction: str = "en-ron"  # or "ron-en"
    top_k: Optional[int] = 3

class TranslateResponse(BaseModel):
    method: str
    translation: str
    alternatives: Optional[List[Dict[str, Any]]] = None

class SuggestRequest(BaseModel):
    text: str
    direction: str = "en-ron"
    top_k: Optional[int] = 5

class SuggestResponseItem(BaseModel):
    source: str
    target: str
    score: float

class FeedbackRequest(BaseModel):
    english: str
    ron: str
    direction: str = "en-ron"
    user_id: Optional[str] = None
    notes: Optional[str] = None

# --- Startup ---
@app.on_event("startup")
def startup_event():
    clean_path = Path("data/cleaned_pairs.csv")

    # Clean data automatically if cleaned file doesn't exist
    if not clean_path.exists():
        logging.info("Cleaning raw data...")
        preprocess_dataset()

    global TRANSLATOR
    TRANSLATOR = RonTranslator(dict_path=str(clean_path))
    # global TRANSLATOR
    logger.info("Loading translator...")
    TRANSLATOR = RonTranslator(dict_path="data/cleaned_pairs.csv", embedding_model="all-MiniLM-L6-v2")
    logger.info("Translator loaded: %d entries", len(TRANSLATOR.english_texts))

@app.get("/health")
def health():
    ok = TRANSLATOR is not None
    return {"status": "ok" if ok else "loading"}

# --- Translate Endpoint ---
@app.post("/translate", response_model=TranslateResponse)
def translate(req: TranslateRequest):
    if TRANSLATOR is None:
        raise HTTPException(status_code=503, detail="Translator not ready")

    result = TRANSLATOR.translate(req.text, direction=req.direction)

    # Format alternatives nicely if present
    alternatives = None
    if "alternatives" in result and result["alternatives"]:
        if req.direction == "en-ron":
            alternatives = [{"source": r[0], "target": r[1], "score": r[2]} for r in result["alternatives"]]
        else:
            alternatives = [{"source": r[0], "target": r[1], "score": r[2]} for r in result["alternatives"]]

    return TranslateResponse(
        method=result["method"],
        translation=result["translation"],
        alternatives=alternatives
    )

# --- Suggest Endpoint ---
@app.post("/suggest", response_model=List[SuggestResponseItem])
def suggest(req: SuggestRequest):
    if TRANSLATOR is None:
        raise HTTPException(status_code=503, detail="Translator not ready")

    hits = TRANSLATOR.retrieval_fallback(req.text, direction=req.direction, top_k=req.top_k)
    return [SuggestResponseItem(source=h[0], target=h[1], score=h[2]) for h in hits]

# --- Feedback Endpoint ---
def append_feedback_row(row: dict):
    df = pd.read_csv(FEEDBACK_CSV)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(FEEDBACK_CSV, index=False)

@app.post("/feedback")
def feedback(req: FeedbackRequest, background_tasks: BackgroundTasks):
    row = {
        "english": req.english.strip(),
        "ron": req.ron.strip(),
        "direction": req.direction,
        "user_id": req.user_id or "",
        "notes": req.notes or "",
        "timestamp": pd.Timestamp.now().isoformat()
    }
    background_tasks.add_task(append_feedback_row, row)
    return {"status": "queued"}

# --- Run locally ---
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
