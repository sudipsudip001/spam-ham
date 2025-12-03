from fastapi import FastAPI
import joblib
from pydantic import BaseModel
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from bs4 import BeautifulSoup
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')
eng_stopwords = stopwords.words('english')

class Message(BaseModel):
    message: str

class text_preprocessing():
    def __init__(self):        
        self.stemmer = PorterStemmer()        
        self.eng_stopwords = stopwords.words('english')
        self.corpus = []

    def clean_text(self, string):
        string = re.sub("http\S+", " ", string)
        string = BeautifulSoup(string, 'lxml')
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
        return string
    
    def tokenize(self, string):
        strings = word_tokenize(string)
        return strings

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
model = joblib.load("multinomial.joblib")
vectorize_model = joblib.load("vectorizer.joblib")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Allow cookies and authentication headers
    allow_methods=["*"],     # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],     # Allow all headers in the request
)

@app.post("/predict")
def read_root(input_data: Message):
    print("The message that you sent is: ", input_data.message)
    message = input_data.message
    
    processor =  text_preprocessing()
    preprocessed = processor.preprocess(message)
    tokenized = processor.tokenize(preprocessed)
    tokens = processor.normalize_text(tokenized)
    tokens = [token for token in tokens if token not in eng_stopwords]
    processed_text = " ".join(tokens)

    vectorized = vectorize_model.transform([processed_text])
    predicted_value = model.predict(vectorized)[0]

    if predicted_value == 1:
        return "Spam"
    else:
        return "Ham"