#!/usr/bin/env python
"""Quick test script for resume extraction - Phase 1"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from applications.models import Application
from applicants.models import ApplicantProfile
from rag.resume_extractor import extract_resume_insights
import json


def test_extraction():
    """Test resume extraction with first available resume"""
    
    print("\n" + "="*70)
    print("RESUME EXTRACTION TEST - PHASE 1")
    print("="*70 + "\n")
    
    # Get first application with resume
    app = Application.objects.filter(resume__isnull=False).first()
    
    if not app:
        print("❌ No applications with resumes found")
        print("   Please submit an application with a resume first")
        return
    
    print(f"✅ Found application #{app.id}")
    print(f"   Applicant: {app.applicant.name}")
    print(f"   Email: {app.applicant.email}")
    print(f"   Job: {app.job.title}")
    print(f"\n📄 Extracting resume insights using GPT-4o-mini...")
    print("   (This may take 10-30 seconds)\n")
    
    try:
        # Extract
        insights = extract_resume_insights(app.resume, f"resume_{app.id}.pdf")
        
        # Print results
        print("="*70)
        print("EXTRACTION RESULTS")
        print("="*70)
        print(json.dumps(insights, indent=2))
        print("="*70 + "\n")
        
        # Summary stats
        print("📊 SUMMARY:")
        print(f"   • Summary: {insights.get('summary', 'N/A')[:100]}...")
        print(f"   • Skills: {len(insights.get('skills', []))} found")
        print(f"   • Experience: {len(insights.get('experience', []))} positions")
        print(f"   • Education: {len(insights.get('education', []))} entries")
        print(f"   • Certifications: {len(insights.get('certifications', []))} found")
        print(f"   • Total Experience: {insights.get('total_experience_years', 'N/A')} years\n")
        
        # Create or update profile
        profile, created = ApplicantProfile.objects.update_or_create(
            applicant=app.applicant,
            defaults={
                'extraction_source': f"Application #{app.id}",
                'skills': insights.get('skills', []),
                'experience': insights.get('experience', []),
                'education': insights.get('education', []),
                'certifications': insights.get('certifications', []),
                'summary': insights.get('summary', ''),
                'total_experience_years': insights.get('total_experience_years'),
                'raw_extraction': insights
            }
        )
        
        if created:
            print(f"✅ Profile CREATED for {app.applicant.name}")
        else:
            print(f"✅ Profile UPDATED for {app.applicant.name}")
        
        print(f"   Profile ID: {profile.id}")
        print(f"   Extracted at: {profile.extracted_at}")
        print(f"\n🎉 Phase 1 Test PASSED!\n")
        print("Next steps:")
        print("  1. Check Django admin: http://localhost:8000/admin/applicants/applicantprofile/")
        print("  2. Verify profile data looks correct")
        print("  3. Ready to move to Phase 2 (API endpoints)\n")
        
    except Exception as e:
        print(f"\n❌ Extraction FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("  • Check OPENAI_API_KEY is set in environment")
        print("  • Verify resume file is valid PDF/DOCX")
        print("  • Check server logs for details\n")


if __name__ == '__main__':
    test_extraction()
