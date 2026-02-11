from fastapi import FastAPI, HTTPException
import joblib
from pydantic import BaseModel
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv
import os
from mangum import Mangum

load_dotenv()
MODEL_NAME = os.getenv("MODEL")
VECTORIZER_NAME = os.getenv("VECTORIZER")
ORIGIN = os.getenv("ORIGIN_NAME")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DOWNLOAD LOCALLY DURING BUILD PROCESS IN DOCKERFILE OR SETUP SCRIPT
try:
    ENG_STOPWORDS = set(stopwords.words('english'))
except Exception as e:
    logger.error(f"NLTK stopwords load failed. Ensure NLTK_DATA is set: {e}")

class Message(BaseModel):
    message: str

class text_preprocessing():
    def __init__(self):        
        self.stemmer = PorterStemmer()        
        self.eng_stopwords = ENG_STOPWORDS

    def clean_text(self, string):
        try:
            string = re.sub("http\S+", " ", string)
            string = BeautifulSoup(string, 'html.parser')
            string = string.get_text()
            string = re.sub('[^A-Za-z]+', ' ', string)
            string = re.sub(r"n\'t", " not", string)
            string = re.sub(r"\'re", " are", string)
            string = re.sub(r"\'s", " is", string)
            string = re.sub(r"\'d", " would", string)
            string = re.sub(r"\'ll", " will", string)
            string = re.sub(r"\'t", " not", string)
            string = re.sub(r"\'ve", " have", string)
            string = re.sub(r"\'m", " am", string)
            return string.lower()
        except Exception as e:
            logger.error(f"Cleaning error: {e}")
            raise ValueError("Failed to clean text input.")

    def normalize_text(self, tokens):
        tokens = [token.lower() for token in tokens]
        tokens = [self.stemmer.stem(token) for token in tokens]
        return tokens

    def preprocess(self, message):
        cleaned_text = self.clean_text(message)
        tokens = word_tokenize(cleaned_text)
        tokens = self.normalize_text(tokens)
        tokens = [token for token in tokens if token not in self.eng_stopwords]
        string = " ".join(tokens)
        return string

app = FastAPI()

try:
    model = joblib.load(MODEL_NAME)
    vectorize_model = joblib.load(VECTORIZER_NAME)
except Exception as e:
    logger.critical("Model files not found! Prediction will fail.")
    model, vectorize_model = None, None

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origins=["https://staging.d3ok0uz900bq7g.amplifyapp.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)
processor = text_preprocessing()

@app.post("/predict")
async def read_root(input_data: Message):
    if not model or not vectorize_model:
        raise HTTPException(status_code=503, detail="Model service unavailable")

    try:
        preprocessed = processor.preprocess(input_data.message)
        vectorized = vectorize_model.transform([preprocessed])
        predicted_value = model.predict(vectorized)[0]
        if predicted_value == 1:
            return "Spam"
        else:
            return "Ham"
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="An internal error occured during prediction.")

@app.get("/")
def detail():
    return {"detail": "Healthy"}

handler = Mangum(app)