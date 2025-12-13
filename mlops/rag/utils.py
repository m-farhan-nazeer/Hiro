# utils.py
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .config import (
    BASE_DIR,
    JOB_COLLECTION,
    get_embedding_model,
    get_qdrant_client,
    CATEGORY_WEIGHTS
)

# -----------------------------
# LOAD SINGLE FILE
# -----------------------------
def load_single_file(file_path):
    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext in [".docx", ".doc"]:
        loader = UnstructuredWordDocumentLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)
    else:
        raise ValueError(f"❌ Unsupported file format: {ext}")

    docs = loader.load()
    for doc in docs:
        doc.metadata["filename"] = os.path.basename(file_path)
    return docs


# -----------------------------
# CHUNKING
# -----------------------------
def create_chunks(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(documents)


# -----------------------------
# CATEGORY DETECTOR
# -----------------------------
def detect_category(text: str) -> str:
    text = text.lower()

    if any(w in text for w in ["experience", "worked", "developer", "engineer"]):
        return "experience"
    if any(w in text for w in ["skill", "technologies", "tools", "languages"]):
        return "skills"
    if any(w in text for w in ["project", "built", "created"]):
        return "projects"
    if any(w in text for w in ["bachelor", "degree", "education"]):
        return "education"
    return "institute"


# -----------------------------
# STORE JOB DESCRIPTION
# -----------------------------
def store_job_description(job_text: str):

    print("\n📌 Storing Job Description in Qdrant...")

    embedding_model = get_embedding_model()

    doc = Document(page_content=job_text, metadata={"type": "job_description"})

    QdrantVectorStore.from_documents(
        documents=[doc],
        embedding=embedding_model,
        collection_name=JOB_COLLECTION,
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
        # If collection already exists with a different vector size,
        # drop and recreate it so embeddings stay compatible.
        force_recreate=True,
    )

    print("✅ Job Description stored successfully.")


# -----------------------------
# MAIN RANKING FUNCTION
# -----------------------------
def rank_resume_against_job(file_path):

    print("\n📄 Processing Resume...\n")

    # Load + chunk resume
    documents = load_single_file(file_path)
    text_chunks = create_chunks(documents)

    embedding_model = get_embedding_model()
    client = get_qdrant_client()

    # Embed resume chunks
    resume_vectors = [
        {
            "text": chunk.page_content,
            "metadata": chunk.metadata,
            "vector": embedding_model.embed_query(chunk.page_content)
        }
        for chunk in text_chunks
    ]

    # Load latest job description from Qdrant
    job_qdrant = QdrantVectorStore(
        client=client,
        collection_name=JOB_COLLECTION,
        embedding=embedding_model,
    )

    job_docs = job_qdrant.similarity_search("job description", k=1)
    job_text = job_docs[0].page_content
    job_vector = embedding_model.embed_query(job_text)

    # print("🧠 Loaded Job Description from Qdrant.")

    # Score by category
    category_scores = {cat: [] for cat in CATEGORY_WEIGHTS}

    for item in resume_vectors:
        text = item["text"]
        vec = item["vector"]

        category = detect_category(text)

        sim = cosine_similarity([job_vector], [vec])[0][0]
        sim = (sim + 1) / 2  # normalize 0–1

        category_scores[category].append(sim)

    # Weighted score
    final_score = 0
    for cat, sims in category_scores.items():
        avg_sim = sum(sims) / len(sims) if sims else 0
        final_score += avg_sim * CATEGORY_WEIGHTS[cat]

    final_score = round(final_score * 100, 2)

    print("\n🏆 RESUME SCORE:", final_score)
    return final_score
