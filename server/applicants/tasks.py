"""
Background task utilities for asynchronous processing
"""
import threading
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)


class BackgroundTask:
    """Simple background task runner using threading"""
    
    @staticmethod
    def run(func: Callable, *args, **kwargs) -> threading.Thread:
        """
        Run a function in a background thread
        
        Args:
            func: Function to run
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            threading.Thread: The background thread
        """
        def wrapper():
            try:
                logger.info(f"Starting background task: {func.__name__}")
                result = func(*args, **kwargs)
                logger.info(f"Background task completed: {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Background task failed: {func.__name__} - {str(e)}", exc_info=True)
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
        return thread


def process_application_all_in_one(applicant_id: int, application_id: int) -> None:
    """
    Consolidated background task to:
    1. Score resume against job
    2. Extract profile insights
    """
    import os
    import tempfile
    from applicants.models import Applicant, ApplicantProfile
    from applications.models import Application
    from rag.resume_extractor import extract_resume_insights
    from rag.utils import store_job_description, rank_resume_against_job
    from posts.models import Job

    try:
        logger.info(f"Starting consolidated processing for application {application_id}")
        
        # 1. Get objects
        application = Application.objects.get(id=application_id)
        applicant = application.applicant
        job = application.job

        if not application.resume:
            logger.warning(f"No resume found for application {application_id}")
            return

        # 2. Scoring (moved from serializer)
        # Build job description text for vector store
        job_text_parts = [
            job.title or "",
            job.description or "",
            f"Skills: {job.required_skills}" if getattr(job, "required_skills", None) else "",
            f"Domain: {job.domain}" if getattr(job, "domain", None) else "",
        ]
        job_text = "\n\n".join([p for p in job_text_parts if p])

        if job_text:
            try:
                store_job_description(job_text)
            except Exception as e:
                logger.error(f"Failed to store job description: {e}")

        # Rank resume
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(application.resume)
                tmp_path = tmp_file.name

            # Extract custom weights from job
            weights = {
                "experience": job.weight_experience,
                "skills": job.weight_skills,
                "projects": job.weight_projects,
                "education": job.weight_education,
                "institute": job.weight_institute,
            }

            generated_score = rank_resume_against_job(tmp_path, custom_weights=weights)
            application.score = generated_score
            application.save(update_fields=["score"])
            logger.info(f"Updated application {application_id} with score: {generated_score}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

        # 3. Profile Extraction
        # Extract insights from resume
        insights = extract_resume_insights(
            resume_bytes=application.resume,
            filename=f"resume_{applicant_id}.pdf"
        )
        
        # Create or update profile
        ApplicantProfile.objects.update_or_create(
            applicant=applicant,
            defaults={
                'summary': insights.get('summary', ''),
                'skills': insights.get('skills', []),
                'experience': insights.get('experience', []),
                'education': insights.get('education', []),
                'certifications': insights.get('certifications', []),
                'total_experience_years': insights.get('total_experience_years'),
                'github_url': insights.get('github_url'),
                'linkedin_url': insights.get('linkedin_url'),
                'raw_extraction': insights,
                'extraction_source': f"Application #{application_id}"
            }
        )
        
        logger.info(f"Consolidated processing completed for application {application_id}")
        
    except Application.DoesNotExist:
        logger.error(f"Application {application_id} not found")
    except Exception as e:
        logger.error(f"Consolidated processing failed for application {application_id}: {str(e)}", exc_info=True)


def scrape_linkedin_async(applicant_id: int, linkedin_url: str) -> None:
    """
    LinkedIn scraping in background
    """
    from applicants.models import Applicant, ApplicantProfile, LinkedInScrapingActivity
    from applicants.scrapers import LinkedInScraper

    try:
        logger.info(f"Starting LinkedIn scrape for applicant {applicant_id} at {linkedin_url}")
        
        scraper = LinkedInScraper()
        insights = scraper.scrape_profile(linkedin_url)
        
        # Log activity
        success = bool(insights.get("headline") or insights.get("about"))
        LinkedInScrapingActivity.log_scrape(
            linkedin_url,
            success=success,
            error=insights.get("error")
        )
        
        # Save to DB
        profile = ApplicantProfile.objects.get(applicant_id=applicant_id)
        profile.social_insights = insights
        profile.linkedin_scrape_status = 'completed'
        profile.save()
        
        logger.info(f"LinkedIn scrape completed for applicant {applicant_id}")
        
    except Exception as e:
        logger.error(f"LinkedIn scrape failed for applicant {applicant_id}: {str(e)}", exc_info=True)
        LinkedInScrapingActivity.log_scrape(linkedin_url, success=False, error=str(e))
        # Update status to failed
        try:
            profile = ApplicantProfile.objects.get(applicant_id=applicant_id)
            profile.linkedin_scrape_status = 'failed'
            profile.save(update_fields=['linkedin_scrape_status'])
        except:
            pass
