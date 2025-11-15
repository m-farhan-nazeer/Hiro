import os
from dotenv import load_dotenv, find_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from groq import Groq

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv(find_dotenv())

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "resume_embeddings")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client_llm = Groq(api_key=GROQ_API_KEY)


# ----------------------------
# Helper Functions
# ----------------------------
def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def get_qdrant_client():
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def fetch_all_resumes():
    """Fetch all stored resume chunks and group by filename"""
    embedding_model = get_embedding_model()
    client = get_qdrant_client()
    qdrant = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embedding_model,
    )

    results = qdrant.similarity_search("resume", k=100)

    resumes = {}
    for r in results:
        filename = r.metadata.get("filename", "Unknown")
        resumes.setdefault(filename, "")
        resumes[filename] += r.page_content + "\n"

    return resumes


# ----------------------------
# Ranking Logic
# ----------------------------
def rank_resumes(job_description, weightage):
    """
    job_description: string (JD text)
    weightage: dict, e.g. {"skills": 0.25, "experience": 0.4, "education": 0.2, "projects": 0.1, "cgpa": 0.05}
    """
    resumes = fetch_all_resumes()

    ranking_prompt = f"""
You are an expert technical recruiter. 
For the given job description, assign each resume a score out of 100.

Job Description:
{job_description}

Weightage criteria (total = 1.0):
{weightage}

Rules:
- Output a simple list of resume names with their scores out of 100.
- No JSON, no explanations, no extra text.
- Example format:
Resume1.pdf — 85%
Resume2.pdf — 74%
Resume3.pdf — 60%

Resumes:
"""

    for name, content in resumes.items():
        ranking_prompt += f"\n\n### Resume: {name}\n{content[:2500]}"

    # Send prompt to LLM via Groq
    response = client_llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": ranking_prompt}],
    )

    # Print clean output
    print("\n✅ Resume Ranking Results:\n")
    print(response.choices[0].message.content.strip())


# ----------------------------
# Run Example
# ----------------------------
if __name__ == "__main__":
    job_description = """
We are hiring a LangChain Developer skilled in Python, FastAPI, and NLP-based RAG systems.
Experience with Hugging Face, Qdrant, and model fine-tuning preferred.
Minimum CGPA 3.0, from reputed institutes.
"""

    weightage = {
        "skills": 0.25,
        "experience": 0.4,
        "education": 0.2,
        "institute": 0.05,
        "projects": 0.1
    }

    rank_resumes(job_description, weightage)
