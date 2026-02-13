# config.py
import os
from dotenv import load_dotenv, find_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

#test-commit
from qdrant_client import QdrantClient

load_dotenv(find_dotenv())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------------
# COLLECTIONS
# -----------------------------
JOB_COLLECTION = os.getenv("JOB_COLLECTION","job_descriptions")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# -----------------------------
# EMBEDDINGS + QDRANT CLIENT
# -----------------------------
# def get_embedding_model():
#     return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_embedding_model():
    return OpenAIEmbeddings(model="text-embedding-3-large")


def get_qdrant_client():
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )
    return client

# -----------------------------
# CATEGORY WEIGHTS
# -----------------------------
CATEGORY_WEIGHTS = {
    "experience": 0.05,
    "skills": 0.25,
    "projects": 0.50,
    "education": 0.10,
    "institute": 0.10,
}
