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


def extract_profile_async(applicant_id: int, application_id: int) -> None:
    """
    Extract applicant profile in background
    
    Args:
        applicant_id: ID of the applicant
        application_id: ID of the application with resume
    """
    from applicants.models import Applicant, ApplicantProfile
    from applications.models import Application
    from rag.resume_extractor import extract_resume_insights
    
    try:
        logger.info(f"Starting profile extraction for applicant {applicant_id}")
        
        # Get the application with resume
        application = Application.objects.get(id=application_id)
        
        if not application.resume:
            logger.warning(f"No resume found for application {application_id}")
            return
        
        # Check if profile already exists
        if ApplicantProfile.objects.filter(applicant_id=applicant_id).exists():
            logger.info(f"Profile already exists for applicant {applicant_id}, skipping extraction")
            return
        
        # Extract insights from resume
        insights = extract_resume_insights(
            resume_bytes=application.resume,
            filename=f"resume_{applicant_id}.pdf"
        )
        
        # Create profile
        ApplicantProfile.objects.create(
            applicant_id=applicant_id,
            summary=insights.get('summary', ''),
            skills=insights.get('skills', []),
            experience=insights.get('experience', []),
            education=insights.get('education', []),
            certifications=insights.get('certifications', []),
            total_experience_years=insights.get('total_experience_years'),
            raw_extraction=insights,
            extraction_source=f"Application #{application_id}"
        )
        
        logger.info(f"Profile created successfully for applicant {applicant_id}")
        
    except Application.DoesNotExist:
        logger.error(f"Application {application_id} not found")
    except Exception as e:
        logger.error(f"Profile extraction failed for applicant {applicant_id}: {str(e)}", exc_info=True)
