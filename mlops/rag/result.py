# main.py

from .config import BASE_DIR
from .utils import store_job_description, rank_resume_against_job
import os

if __name__ == "__main__":

    # 1️⃣ Store job description (ONLY ONCE)
    job_text = """
    We are hiring a passionate Data Science enthusiast proficient in Python, SQL, FastAPI,
    Power BI, and Machine Learning. Involves creating dashboards, optimizing scripts,
    developing RAG chatbots and predictive models.
    """
    # store_job_description(job_text)

    # 2️⃣ Compare resume at runtime
    FILE_PATH = os.path.join(BASE_DIR, "Shahroz_Naveed_Resume (6).pdf")
    rank_resume_against_job(FILE_PATH)
