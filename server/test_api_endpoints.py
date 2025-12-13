#!/usr/bin/env python
"""Test script for Phase 2 - API Endpoints"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import RequestFactory
from applicants.views import get_applicant_profile, refresh_applicant_profile
from applicants.models import Applicant, ApplicantProfile
import json


def test_api_endpoints():
    """Test the profile API endpoints"""
    
    print("\n" + "="*70)
    print("PHASE 2 API ENDPOINT TEST")
    print("="*70 + "\n")
    
    # Get an applicant with a resume
    applicant = Applicant.objects.filter(applications__resume__isnull=False).first()
    
    if not applicant:
        print("❌ No applicants with resumes found")
        return
    
    print(f"✅ Testing with applicant: {applicant.name} (ID: {applicant.id})\n")
    
    # Create request factory
    factory = RequestFactory()
    
    # Test 1: GET profile (should create if doesn't exist)
    print("="*70)
    print("TEST 1: GET /api/applicants/<id>/profile/")
    print("="*70)
    
    # Delete existing profile first to test auto-creation
    ApplicantProfile.objects.filter(applicant=applicant).delete()
    print("Deleted existing profile to test auto-creation\n")
    
    request = factory.get(f'/api/applicants/{applicant.id}/profile/')
    response = get_applicant_profile(request, applicant.id)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        print("✅ Profile auto-created successfully!")
        data = response.data
        print(f"\nProfile Data:")
        print(f"  - ID: {data['id']}")
        print(f"  - Applicant: {data['applicant_name']}")
        print(f"  - Skills: {len(data['skills'])} found")
        print(f"  - Experience: {len(data['experience'])} positions")
        print(f"  - Education: {len(data['education'])} entries")
        print(f"  - Summary: {data['summary'][:100]}...")
    else:
        print(f"❌ Failed: {response.data}")
    
    # Test 2: GET profile again (should return existing)
    print("\n" + "="*70)
    print("TEST 2: GET /api/applicants/<id>/profile/ (existing)")
    print("="*70)
    
    request = factory.get(f'/api/applicants/{applicant.id}/profile/')
    response = get_applicant_profile(request, applicant.id)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Returned existing profile successfully!")
        print(f"  - Profile ID: {response.data['id']}")
    else:
        print(f"❌ Failed: {response.data}")
    
    # Test 3: Refresh profile
    print("\n" + "="*70)
    print("TEST 3: POST /api/applicants/<id>/profile/refresh/")
    print("="*70)
    
    request = factory.post(f'/api/applicants/{applicant.id}/profile/refresh/')
    response = refresh_applicant_profile(request, applicant.id)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        print("✅ Profile refreshed successfully!")
        print(f"  - New Profile ID: {response.data['id']}")
        print(f"  - Extracted at: {response.data['extracted_at']}")
    else:
        print(f"❌ Failed: {response.data}")
    
    # Test 4: Non-existent applicant
    print("\n" + "="*70)
    print("TEST 4: GET /api/applicants/99999/profile/ (non-existent)")
    print("="*70)
    
    request = factory.get('/api/applicants/99999/profile/')
    response = get_applicant_profile(request, 99999)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 404:
        print("✅ Correctly returned 404 for non-existent applicant")
        print(f"  - Error: {response.data['error']}")
    else:
        print(f"❌ Unexpected response: {response.data}")
    
    print("\n" + "="*70)
    print("🎉 PHASE 2 API TESTS COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Test endpoints via browser/Postman:")
    print(f"     GET  http://localhost:8000/api/applicants/{applicant.id}/profile/")
    print(f"     POST http://localhost:8000/api/applicants/{applicant.id}/profile/refresh/")
    print("  2. Ready to move to Phase 3 (Frontend implementation)\n")


if __name__ == '__main__':
    test_api_endpoints()
