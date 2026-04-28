# mlops/rag/resume_extractor.py

import os
import json
import tempfile
import logging
import subprocess
import re
from typing import List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from .utils import load_single_file

logger = logging.getLogger(__name__)


def _is_weak_extracted_text(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) < 300:
        return True

    words = re.findall(r"[A-Za-z]{2,}", stripped)
    if len(words) < 50:
        return True

    alpha_chars = sum(1 for ch in stripped if ch.isalpha())
    return alpha_chars / max(len(stripped), 1) < 0.35


def _run_ocrmypdf(input_path: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        output_path = tmp.name

    try:
        subprocess.run(
            [
                "ocrmypdf",
                "--force-ocr",
                input_path,
                output_path,
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return output_path
    except subprocess.CalledProcessError as exc:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise RuntimeError(f"OCRmyPDF failed: {exc.stderr.strip() or exc.stdout.strip()}") from exc


# -----------------------------
# PYDANTIC SCHEMAS
# -----------------------------

class Skill(BaseModel):
    """Individual skill with category and proficiency"""
    name: str
    category: str = Field(description="e.g., Programming, Design, Management, Communication")
    proficiency: Optional[str] = Field(
        default=None, 
        description="Beginner/Intermediate/Advanced/Expert if mentioned"
    )


class Experience(BaseModel):
    """Work experience entry"""
    company: str
    title: str
    duration: str = Field(description="e.g., '2020-2023', 'Jan 2020 - Present', or '2 years'")
    description: str = Field(description="Brief description of key responsibilities and achievements")


class Education(BaseModel):
    """Education entry"""
    institution: str
    degree: str = Field(description="e.g., Bachelor's, Master's, PhD")
    field: str = Field(description="Field of study")
    year: str = Field(description="Graduation year or date range")


class Certification(BaseModel):
    """Professional certification"""
    name: str
    issuer: str
    year: Optional[str] = Field(default=None, description="Year obtained if mentioned")


class ResumeInsights(BaseModel):
    """Complete structured output schema for resume extraction"""
    summary: str = Field(
        description="2-3 sentence professional summary highlighting key strengths and experience"
    )
    github_url: Optional[str] = Field(
        default=None,
        description="GitHub profile URL if found (check for hyperlinks)"
    )
    linkedin_url: Optional[str] = Field(
        default=None,
        description="LinkedIn profile URL if found (check for hyperlinks)"
    )
    skills: List[Skill] = Field(
        default_factory=list,
        description="All technical and soft skills mentioned"
    )
    experience: List[Experience] = Field(
        default_factory=list,
        description="Work history in reverse chronological order"
    )
    education: List[Education] = Field(
        default_factory=list,
        description="Educational background"
    )
    certifications: List[Certification] = Field(
        default_factory=list,
        description="Professional certifications and licenses"
    )
    total_experience_years: Optional[float] = Field(
        default=None,
        description="Total years of professional experience calculated from work history"
    )


# -----------------------------
# EXTRACTION FUNCTION
# -----------------------------

def extract_resume_insights(resume_bytes: bytes, filename: str = "resume.pdf") -> dict:
    """
    Extract structured insights from resume using LLM.
    
    Args:
        resume_bytes: Binary content of resume file
        filename: Original filename (for format detection)
    
    Returns:
        dict: Structured resume insights with keys:
            - summary (str)
            - github_url (str or None)
            - linkedin_url (str or None)
            - skills (list)
            - experience (list)
            - education (list)
            - certifications (list)
            - total_experience_years (float or None)
    
    Raises:
        ValueError: If resume format is unsupported
        Exception: If extraction fails
    """
    
    logger.info(f"Starting resume extraction for file: {filename}")
    
    # Write resume to temp file
    file_ext = os.path.splitext(filename)[1] or '.pdf'
    with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
        tmp.write(resume_bytes)
        tmp_path = tmp.name
    ocr_tmp_path = None
    
    try:
        # Load resume content
        logger.info(f"Loading resume from temp file: {tmp_path}")
        documents = load_single_file(tmp_path)
        resume_text = "\n\n".join([doc.page_content for doc in documents])

        print(f"Initial extracted text length for {filename}: {len(resume_text.strip())} characters")
        print(f"Initial extracted text preview for {filename}:\n{resume_text[:500]}")

        if file_ext.lower() == ".pdf" and _is_weak_extracted_text(resume_text):
            print(f"Weak PDF text detected for {filename}. Triggering OCR fallback...")
            try:
                ocr_tmp_path = _run_ocrmypdf(tmp_path)
                ocr_documents = load_single_file(ocr_tmp_path)
                resume_text = "\n\n".join([doc.page_content for doc in ocr_documents])
                print(f"OCR extracted text length for {filename}: {len(resume_text.strip())} characters")
                print(f"OCR extracted text preview for {filename}:\n{resume_text[:500]}")
            except Exception as exc:
                print(f"OCR fallback failed for {filename}: {exc}")

        if not resume_text.strip():
            raise ValueError("Resume appears to be empty or unreadable")
        
        logger.info(f"Loaded resume text: {len(resume_text)} characters")
        
        # Set up LLM with structured output
        llm = ChatOpenAI(
            model="gpt-4o",  # Fast and cost-effective
            temperature=0,  # Deterministic extraction
        )
        
        parser = JsonOutputParser(pydantic_object=ResumeInsights)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume parser. Extract structured information from resumes accurately and comprehensively.

Instructions:
- Be thorough but concise
- Look specifically for social media links like GitHub and LinkedIn. If the text has "Extracted Links", check there first.
- For skills, categorize them appropriately (Programming, Design, Management, Communication, etc.)
- For experience, include company name, job title, duration, and key responsibilities
- Calculate total years of experience from the work history
- Extract education details including institution, degree, field, and year
- Include any certifications or professional licenses mentioned
- Write a professional 2-3 sentence summary highlighting the candidate's key strengths

{format_instructions}"""),
            ("human", "Extract information from this resume:\n\n{resume_text}")
        ])
        
        chain = prompt | llm | parser
        
        print("Invoking LLM for extraction...")
        result = chain.invoke({
            "resume_text": resume_text[:10000],  # Limit to first 10k chars to avoid token limits
            "format_instructions": parser.get_format_instructions()
        })
        
        print(f"Extracted resume insights for {filename}:\n{json.dumps(result, indent=2)}")
        logger.info("Extraction successful")
        return result
        
    except Exception as e:
        logger.error(f"Failed to extract resume insights: {str(e)}", exc_info=True)
        raise
        
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
                logger.debug(f"Cleaned up temp file: {tmp_path}")
            except OSError as e:
                logger.warning(f"Failed to remove temp file {tmp_path}: {e}")
        if ocr_tmp_path and os.path.exists(ocr_tmp_path):
            try:
                os.remove(ocr_tmp_path)
            except OSError as e:
                logger.warning(f"Failed to remove OCR temp file {ocr_tmp_path}: {e}")


# -----------------------------
# HELPER FUNCTION FOR TESTING
# -----------------------------

def extract_from_file_path(file_path: str) -> dict:
    """
    Helper function to extract insights from a file path (for testing).
    
    Args:
        file_path: Path to resume file
    
    Returns:
        dict: Structured resume insights
    """
    with open(file_path, 'rb') as f:
        resume_bytes = f.read()
    
    filename = os.path.basename(file_path)
    return extract_resume_insights(resume_bytes, filename)
