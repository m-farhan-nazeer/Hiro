import os
from dotenv import load_dotenv, find_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient


load_dotenv(find_dotenv())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "resume_embeddings")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")




url = os.getenv("QDRANT_URL")
api_key = os.getenv("QDRANT_API_KEY")



# client = QdrantClient(url=url, api_key=api_key)

# try:
#     collections = client.get_collections()
#     print("✅ Connection successful:", collections)
# except Exception as e:
#     print("❌ Connection failed:", e)



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

    documents = loader.load()
    for doc in documents:
        doc.metadata["filename"] = os.path.basename(file_path)
    return documents



def create_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    text_chunks = text_splitter.split_documents(documents)
    return text_chunks



def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")



def get_qdrant_client():
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )
    return client



def process_resume(file_path):
    print(f"📂 Processing file: {file_path}")

    documents = load_single_file(file_path)
    print(f"✅ Loaded {len(documents)} pages from {os.path.basename(file_path)}")

    text_chunks = create_chunks(documents)
    print(f"✂️ Split into {len(text_chunks)} text chunks")

    embedding_model = get_embedding_model()
    client = get_qdrant_client()

    qdrant = QdrantVectorStore.from_documents(
        documents=text_chunks,
        embedding=embedding_model,
        collection_name=COLLECTION_NAME,
        url=QDRANT_URL,           # ✅ use your cloud URL
        api_key=QDRANT_API_KEY,  # use client instead of local path
    )

    print("✅ Resume embedded and stored successfully in Qdrant Cloud.")
    return qdrant


def search_similar_resumes(query_text, top_k=1):
    print(f"\n🔍 Searching for: '{query_text}'\n")

    # Load same embedding model
    embedding_model = get_embedding_model()

    # ✅ Create a Qdrant client (instead of passing URL directly)
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )

    # ✅ Use existing collection
    qdrant = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embedding_model,
    )

    # Perform semantic search
    results = qdrant.similarity_search(query_text, k=top_k)

    print("🧠 Top matching resume sections:\n")
    for i, r in enumerate(results, 1):
        filename = r.metadata.get("filename", "Unknown")
        snippet = r.page_content.replace("\n", " ")[:200]
        print(f"{i}. 📄 {filename}")
        print(f"   🧩 {snippet}...")
        print("-" * 80)

# ----------------------------
# Step 8: Run
# ----------------------------
if __name__ == "__main__":
    # FILE_PATH = os.path.join(BASE_DIR, "Resume-Suleman.pdf")
    # process_resume(FILE_PATH)

    query = "LangChain Developer"
    search_similar_resumes(query)
