#!/usr/bin/env python
"""Test script for proactive background extraction"""

import os
import sys
import django
import time

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from applicants.models import Applicant, ApplicantProfile
from applications.models import Application
from jobs.models import Job


def test_proactive_extraction():
    """Test that profiles are extracted in background on application creation"""
    
    print("\n" + "="*70)
    print("PROACTIVE EXTRACTION TEST")
    print("="*70 + "\n")
    
    # Find an applicant without a profile
    applicant = Applicant.objects.filter(
        applications__resume__isnull=False
    ).exclude(
        id__in=ApplicantProfile.objects.values_list('applicant_id', flat=True)
    ).first()
    
    if not applicant:
        print("❌ No applicants found without profiles")
        print("Creating a test scenario...")
        
        # Delete a profile to test
        profile = ApplicantProfile.objects.first()
        if profile:
            applicant = profile.applicant
            profile.delete()
            print(f"✅ Deleted profile for {applicant.name} to test extraction\n")
        else:
            print("❌ No profiles to delete. Please create an application first.")
            return
    
    print(f"Testing with applicant: {applicant.name} (ID: {applicant.id})")
    print(f"Email: {applicant.email}\n")
    
    # Check current state
    profile_exists_before = ApplicantProfile.objects.filter(applicant=applicant).exists()
    print(f"Profile exists before: {profile_exists_before}")
    
    if profile_exists_before:
        print("⚠️  Profile already exists. Deleting for test...")
        ApplicantProfile.objects.filter(applicant=applicant).delete()
    
    # Get an application with resume
    application = Application.objects.filter(
        applicant=applicant,
        resume__isnull=False
    ).first()
    
    if not application:
        print("❌ No application with resume found for this applicant")
        return
    
    print(f"\nApplication ID: {application.id}")
    print(f"Has resume: {bool(application.resume)}")
    print(f"Resume size: {len(application.resume) if application.resume else 0} bytes\n")
    
    # Trigger extraction manually (simulating what happens on application creation)
    print("="*70)
    print("TRIGGERING BACKGROUND EXTRACTION")
    print("="*70 + "\n")
    
    from applicants.tasks import BackgroundTask, extract_profile_async
    
    print("Starting background task...")
    thread = BackgroundTask.run(
        extract_profile_async,
        applicant_id=applicant.id,
        application_id=application.id
    )
    
    print("✅ Background task started (non-blocking)")
    print("⏳ Waiting for extraction to complete...\n")
    
    # Poll for completion
    max_wait = 60  # seconds
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        profile_exists = ApplicantProfile.objects.filter(applicant=applicant).exists()
        
        if profile_exists:
            elapsed = time.time() - start_time
            print(f"\n✅ Profile created in {elapsed:.2f} seconds!")
            
            # Show profile details
            profile = ApplicantProfile.objects.get(applicant=applicant)
            print("\n" + "="*70)
            print("EXTRACTED PROFILE")
            print("="*70)
            print(f"Profile ID: {profile.id}")
            print(f"Skills: {len(profile.skills)} found")
            print(f"Experience: {len(profile.experience)} positions")
            print(f"Education: {len(profile.education)} entries")
            print(f"Certifications: {len(profile.certifications)} found")
            print(f"Summary: {profile.summary[:100]}...")
            print(f"Extracted at: {profile.extracted_at}")
            print(f"Source: {profile.extraction_source}")
            
            print("\n" + "="*70)
            print("🎉 PROACTIVE EXTRACTION WORKING!")
            print("="*70)
            print("\nNext steps:")
            print("1. Submit a new application via the frontend")
            print("2. Wait 10-30 seconds for background extraction")
            print("3. Click on the applicant name")
            print("4. Modal should open INSTANTLY with profile data!\n")
            
            return
        
        time.sleep(2)
        print(".", end="", flush=True)
    
    print(f"\n\n❌ Profile not created after {max_wait} seconds")
    print("Check server logs for errors")


if __name__ == '__main__':
    test_proactive_extraction()
