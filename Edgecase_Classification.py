import getpass
import pandas as pd
import os
os.environ["GROQ_API_KEY"] = " "
from langchain_groq import ChatGroq
llm = ChatGroq(model="llama3-8b-8192")
import sqlite3
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords')
def preprocess(text):
    # Lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove extra whitespaces
    text = ' '.join(text.split())
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in word_tokenize(text) if word not in stop_words]
    # Join tokens back into a single string
    return ''.join(tokens)

def get_text_embedding(cleaned_text):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model.encode([cleaned_text])[0]

def predict_edgecase(text, embedding_layout):
    cleaned_text = preprocess(text)
    # Connect to the SQLite database
    conn = sqlite3.connect('./uploaded_pdf_database_new.db')
    cursor = conn.cursor()

    # Get the embedding for the input text
    embedding_text = get_text_embedding(cleaned_text)
    embedding_layout_resized = embedding_layout[:embedding_text.shape[0]]
    #new_embedding = 0.35*embedding_text + 0.65*embedding_layout_resized
    new_embedding = np.concatenate((embedding_text, embedding_layout_resized), axis=0)
    # Fetch all embeddings and associated labels from the flagged_pdf_metadata table
    cursor.execute("SELECT embedding, classification_label FROM flagged_pdf_metadata")
    flagged_data = cursor.fetchall()

    # Initialize a variable to store the result
    matched_label = None
    max_similarity = -1

    if not flagged_data:
        # Skip to the final else block by leaving matched_label as None
        pass
    else:

        # Loop through the fetched embeddings and compare with the new embedding
        for i, (embedding, label) in enumerate(flagged_data):
            # Convert the fetched embedding into a numpy array
            embedding = np.frombuffer(embedding, dtype=np.float32)
            # Compute cosine similarity between the new embedding and the flagged embedding
            similarity = cosine_similarity([new_embedding], [embedding])[0][0]
            if similarity > max_similarity:
                max_similarity = similarity
                matched_label = label
        if max_similarity < 0.70:
            matched_label = None


        # Close the database connection
    conn.close()

    # Return the matched label or None if no match is found
    if matched_label:
        return matched_label, new_embedding
    else:
        from langchain_core.messages import HumanMessage, SystemMessage

        messages = [
            SystemMessage(
                "the given text is extracted from a scanned PDF document using OCR. Based on the text, return what type of document label it is in maximum of 3 words only .Refrain from using any adjectives, be as straight forward and to the point as possible. For example: cards, credit cards, application form, etc. If nothing can be deduced directly, return Nan."),
            HumanMessage(text),
        ]

        return llm.invoke(messages).content, new_embedding
