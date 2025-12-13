# mlops/rag/resume_extractor.py

import os
import json
import tempfile
import logging
from typing import List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from .utils import load_single_file

logger = logging.getLogger(__name__)


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
    
    try:
        # Load resume content
        logger.info(f"Loading resume from temp file: {tmp_path}")
        documents = load_single_file(tmp_path)
        resume_text = "\n\n".join([doc.page_content for doc in documents])
        
        if not resume_text.strip():
            raise ValueError("Resume appears to be empty or unreadable")
        
        logger.info(f"Loaded resume text: {len(resume_text)} characters")
        
        # Set up LLM with structured output
        llm = ChatOpenAI(
            model="gpt-4o-mini",  # Fast and cost-effective
            temperature=0,  # Deterministic extraction
        )
        
        parser = JsonOutputParser(pydantic_object=ResumeInsights)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume parser. Extract structured information from resumes accurately and comprehensively.

Instructions:
- Be thorough but concise
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
        
        logger.info("Invoking LLM for extraction...")
        result = chain.invoke({
            "resume_text": resume_text[:10000],  # Limit to first 10k chars to avoid token limits
            "format_instructions": parser.get_format_instructions()
        })
        
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
