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
        # enhanced PDF loading with hyperlink extraction
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            docs = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                
                # Extract hyperlinks
                links = []
                if "/Annots" in page:
                    for annot in page["/Annots"]:
                        obj = annot.get_object()
                        if "/A" in obj and "/URI" in obj["/A"]:
                            uri = obj["/A"]["/URI"]
                            links.append(uri)
                
                # Append links to text if found
                if links:
                    text += "\n\nExtracted Links:\n" + "\n".join(links)
                
                docs.append(Document(page_content=text, metadata={"source": file_path, "page": i}))
            return docs
            
        except ImportError:
            # Fallback to langchain loader if pypdf is not directly available
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


def build_scoring_text_from_insights(insights: dict) -> str:
    parts = []

    if insights.get("summary"):
        parts.append(f"Summary: {insights['summary']}")

    skills = insights.get("skills") or []
    if skills:
        skill_names = [skill.get("name", "") if isinstance(skill, dict) else str(skill) for skill in skills]
        parts.append("Skills: " + ", ".join([s for s in skill_names if s]))

    experience = insights.get("experience") or []
    if experience:
        exp_lines = []
        for item in experience:
            if isinstance(item, dict):
                exp_lines.append(
                    " | ".join(
                        [
                            item.get("title", ""),
                            item.get("company", ""),
                            item.get("duration", ""),
                            item.get("description", ""),
                        ]
                    )
                )
        parts.append("Experience:\n" + "\n".join([line for line in exp_lines if line.strip(" |")]))

    education = insights.get("education") or []
    if education:
        edu_lines = []
        for item in education:
            if isinstance(item, dict):
                edu_lines.append(
                    " | ".join(
                        [
                            item.get("degree", ""),
                            item.get("field", ""),
                            item.get("institution", ""),
                            item.get("year", ""),
                        ]
                    )
                )
        parts.append("Education:\n" + "\n".join([line for line in edu_lines if line.strip(" |")]))

    certifications = insights.get("certifications") or []
    if certifications:
        cert_lines = []
        for item in certifications:
            if isinstance(item, dict):
                cert_lines.append(
                    " | ".join(
                        [
                            item.get("name", ""),
                            item.get("issuer", ""),
                            str(item.get("year", "") or ""),
                        ]
                    )
                )
        parts.append("Certifications:\n" + "\n".join([line for line in cert_lines if line.strip(" |")]))

    return "\n\n".join(parts)


# -----------------------------
# STORE JOB DESCRIPTION
# -----------------------------
def store_job_description(job_text: str, job_id: int = None):

    print(f"\n📌 Storing Job Description {f'#{job_id}' if job_id else ''} in Qdrant...")

    embedding_model = get_embedding_model()
    client = get_qdrant_client()

    doc = Document(
        page_content=job_text, 
        metadata={
            "type": "job_description",
            "job_id": job_id
        }
    )

    # Use QdrantVectorStore but with a specific ID to prevent duplicates
    # Qdrant IDs can be integers or UUIDs. We use job_id as integer.
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=JOB_COLLECTION,
        embedding=embedding_model,
    )
    
    # Use add_documents with ids to ensure UPSERT behavior (no duplicates)
    if job_id:
        vector_store.add_documents(documents=[doc], ids=[job_id])
    else:
        # Fallback to standard flow if no ID
        vector_store.add_documents(documents=[doc])

    print(f"✅ Job Description {f'#{job_id}' if job_id else ''} stored/updated successfully.")


# -----------------------------
# MAIN RANKING FUNCTION
# -----------------------------
def rank_resume_against_job(file_path, job_text=None, job_id: int = None, custom_weights=None, resume_text_override: str | None = None):

    print("\n📄 Processing Resume...\n")

    # Use custom weights if provided, else defaults from config
    weights = custom_weights if custom_weights else CATEGORY_WEIGHTS
    
    # Ensure weights are in 0-1 range for calculation
    # (they might come as 0-100 from frontend)
    normalized_weights = {}
    for cat, w in weights.items():
        if w > 1:
            normalized_weights[cat] = w / 100.0
        else:
            normalized_weights[cat] = w

    # Load + chunk resume
    if resume_text_override is not None:
        print("\n🧾 Scoring from extracted insights text...\n")
        text_chunks = create_chunks([Document(page_content=resume_text_override, metadata={"source": file_path, "type": "extracted_insights"})])
    else:
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

    # Load latest job description from Qdrant IF not provided directly
    if not job_text:
        job_qdrant = QdrantVectorStore(
            client=client,
            collection_name=JOB_COLLECTION,
            embedding=embedding_model,
        )
        
        # If we have a job_id, try to fetch exactly that point
        if job_id:
            try:
                # Retrieve by ID from Qdrant
                points = client.retrieve(
                    collection_name=JOB_COLLECTION,
                    ids=[job_id],
                    with_payload=True
                )
                if points:
                    job_text = points[0].payload.get("page_content")
            except Exception as e:
                print(f"⚠️ Failed to retrieve job by ID {job_id}: {e}")

        # Fallback to similarity search if ID fetch failed or wasn't provided
        if not job_text:
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
        final_score += avg_sim * normalized_weights.get(cat, 0)

    final_score = round(final_score * 100, 2)

    print("\n🏆 RESUME SCORE:", final_score)
    return final_score
