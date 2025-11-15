import json
from llm.client import call_groq
from llm.prompts import resume_extraction_prompt

from extractors.basic_info_extractor import extract_basic_info
from extractors.education_extractor import extract_education
from extractors.skills_extractor import extract_skills
from extractors.experience_extractor import extract_experience
from extractors.projects_extractor import extract_projects
from extractors.certifications_extractors import extract_certifications

from text.extract import extract_text


def parse_resume(resume_text: str, extracted_urls: list = None):
    """
    Parse resume using LLM first, then fallback to regex extractors.
    """
    prompt = resume_extraction_prompt(resume_text)

    try:
        llm_response = call_groq(prompt)
        
        # Try to extract JSON from response (sometimes wrapped in markdown)
        if "```json" in llm_response:
            json_str = llm_response.split("```json")[1].split("```")[0].strip()
        elif "```" in llm_response:
            json_str = llm_response.split("```")[1].split("```")[0].strip()
        else:
            json_str = llm_response.strip()
        
        resume_data = json.loads(json_str)
        print("✅ Extracted via GROQ LLM.")
        
    except Exception as e:
        print(f"⚠️ LLM failed: {e}")
        print("   Switching to fallback extractors...")
        resume_data = {}

    # Import company extractor
    from extractors.experience_extractor import extract_companies
    from extractors.projects_extractor import format_projects_for_output
    
    # Extract basic info with URLs
    basic_info = extract_basic_info(resume_text, extra_urls=extracted_urls or [])
    
    # Merge data: use LLM data if available, otherwise fallback
    if not resume_data.get("name"):
        resume_data["name"] = basic_info.get("name", "")
    
    if not resume_data.get("email"):
        emails = basic_info.get("emails", [])
        resume_data["email"] = emails[0] if emails else ""
    
    if not resume_data.get("phone"):
        phones = basic_info.get("phones", [])
        resume_data["phone"] = phones[0] if phones else ""
    
    # Add social links
    if not resume_data.get("linkedin"):
        resume_data["linkedin"] = basic_info.get("linkedin", "")
    if not resume_data.get("github"):
        resume_data["github"] = basic_info.get("github", "")
    
    if not resume_data.get("education") or len(resume_data.get("education", [])) == 0:
        resume_data["education"] = extract_education(resume_text)
    
    if not resume_data.get("skills") or len(resume_data.get("skills", [])) == 0:
        resume_data["skills"] = extract_skills(resume_text)
    
    if not resume_data.get("experience_years"):
        resume_data["experience_years"] = extract_experience(resume_text)
    
    if not resume_data.get("companies") or len(resume_data.get("companies", [])) == 0:
        resume_data["companies"] = extract_companies(resume_text)
    
    if not resume_data.get("projects") or len(resume_data.get("projects", [])) == 0:
        projects_dicts = extract_projects(resume_text)
        resume_data["projects"] = format_projects_for_output(projects_dicts)
    
    if not resume_data.get("certifications") or len(resume_data.get("certifications", [])) == 0:
        resume_data["certifications"] = extract_certifications(resume_text)
    
    if not resume_data.get("summary"):
        resume_data["summary"] = ""

    # Ensure consistent output schema
    schema = {
        "name": "",
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": "",
        "education": [],
        "skills": [],
        "experience_years": "",
        "companies": [],
        "projects": [],
        "certifications": [],
        "summary": ""
    }
    
    for key in schema:
        resume_data.setdefault(key, schema[key])

    return resume_data


if __name__ == "__main__":
    try:
        file_path = "MusaArfah-Resume.pdf"
        resume_text, extracted_urls = extract_text(file_path)
        
        print("📄 Resume Text Preview:")
        print("-" * 80)
        print(resume_text[:500] + "...\n")
        print(f"🔗 Found {len(extracted_urls)} URLs\n")
        print("📘 Text extracted successfully. Beginning parsing...\n")

        parsed = parse_resume(resume_text, extracted_urls)

        print("\n🎯 Final Extracted Resume Data:")
        print(json.dumps(parsed, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()