from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from posts.models import Job
from users.models import UserProfile


class JobIsolationTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="u1", password="pass1234")
        self.user2 = User.objects.create_user(username="u2", password="pass1234")
        UserProfile.objects.create(user=self.user1)
        UserProfile.objects.create(user=self.user2)

        self.job1 = Job.objects.create(
            title="Job 1",
            description="Desc 1",
            status="active",
            jobtype="onsite",
            jobtime="full-time",
            shift="Day",
            required_skills="Python",
            domain="Engineering",
            created_by=self.user1,
        )
        self.job2 = Job.objects.create(
            title="Job 2",
            description="Desc 2",
            status="active",
            jobtype="remote",
            jobtime="part-time",
            shift="Night",
            required_skills="React",
            domain="Frontend",
            created_by=self.user2,
        )

    def test_user_only_sees_own_jobs(self):
        self.client.force_authenticate(user=self.user1)
        resp = self.client.get("/api/jobs/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["id"], self.job1.id)

    def test_user_cannot_access_other_job_detail(self):
        self.client.force_authenticate(user=self.user1)
        resp = self.client.get(f"/api/jobs/{self.job2.id}/")
        self.assertEqual(resp.status_code, 404)

    def test_superuser_can_view_all_jobs(self):
        admin = User.objects.create_superuser(
            username="admin", password="pass1234", email="admin@example.com"
        )
        self.client.force_authenticate(user=admin)
        resp = self.client.get("/api/jobs/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)
