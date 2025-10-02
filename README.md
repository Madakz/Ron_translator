## This is a translator application for a low resource language of Manguna district, Bokkos LGA of Plateau state, Nigeria

### Create virtual environment. This project didn't have a virtual environment when it was developed but it is recommended you have one
python -m venv venv
source venv/bin/activate  # activate virtual env. on Linux/Mac
venv\Scripts\activate     # activate virtual env. on Windows

### Install dependencies
pip install -r requirements.txt

### Install this from the terminal, for POS tagging
python -m spacy download en_core_web_sm

### Running the API
uvicorn app.main:app --reload

#### The API will be live at:
Root: http://127.0.0.1:8000

Interactive docs: http://127.0.0.1:8000/docs


### Translate: /translate
POST REQUEST:
{
  "text": "anzényet",
  "direction": "ron-en",
  "top_k": 3
}

or Bash
curl -X 'POST' \
  'http://127.0.0.1:8000/translate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "anzényet",
  "direction": "ron-en",
  "top_k": 3
}'

Result is: 
{
  "method": "exact",
  "translation": "ant (small, black)",
  "alternatives": null
}


### Feedback is stored in:
data/feedback_queue.csv

### Suggestion with percentage accuracy: /suggest
POST REQUEST:
{
  "text": "man",
  "direction": "en-ron",
  "top_k": 5
}


or Bash: 
curl -X 'POST' \
  'http://127.0.0.1:8000/suggest' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "man",
  "direction": "en-ron",
  "top_k": 5
}'

Result is:
[
  {
    "source": "he",
    "target": "sí",
    "score": 0.5989046692848206
  },
  {
    "source": "white man",
    "target": "masárá, malwya",
    "score": 0.49144643545150757
  },
  {
    "source": "friend",
    "target": "jèmàt",
    "score": 0.4565843343734741
  },
  {
    "source": "i",
    "target": "yín",
    "score": 0.45504483580589294
  },
  {
    "source": "baby",
    "target": "àkalijiw",
    "score": 0.44133260846138
  }
]
