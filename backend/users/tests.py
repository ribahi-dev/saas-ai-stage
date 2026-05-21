from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import CompanyProfile, StudentProfile
from offers.models import InternshipOffer


User = get_user_model()


class RegistrationTests(APITestCase):
    def test_student_registration_returns_tokens_and_profile(self):
        response = self.client.post(
            "/api/users/register/",
            {
                "username": "student_v1",
                "email": "student.v1@example.com",
                "first_name": "Student",
                "last_name": "V1",
                "role": "student",
                "password": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        user = User.objects.get(username="student_v1")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertTrue(StudentProfile.objects.filter(user=user).exists())

    def test_company_registration_returns_tokens_and_profile(self):
        response = self.client.post(
            "/api/users/register/",
            {
                "username": "company_v1",
                "email": "company.v1@example.com",
                "first_name": "Company",
                "last_name": "V1",
                "role": "company",
                "password": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        user = User.objects.get(username="company_v1")
        self.assertEqual(user.role, User.Role.COMPANY)
        self.assertTrue(CompanyProfile.objects.filter(user=user).exists())

    def test_student_profile_endpoint_recreates_missing_profile(self):
        user = User.objects.create_user(
            username="legacy_student",
            email="legacy.student@example.com",
            password="StrongPass123!",
            role=User.Role.STUDENT,
        )
        StudentProfile.objects.filter(user=user).delete()
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/users/me/student/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(StudentProfile.objects.filter(user=user).exists())


class AdminApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_v1",
            email="admin.v1@example.com",
            password="StrongPass123!",
            role=User.Role.ADMIN,
            is_staff=True,
        )
        self.student = User.objects.create_user(
            username="student_stats",
            email="student.stats@example.com",
            password="StrongPass123!",
            role=User.Role.STUDENT,
        )
        StudentProfile.objects.create(user=self.student)
        self.company_user = User.objects.create_user(
            username="company_stats",
            email="company.stats@example.com",
            password="StrongPass123!",
            role=User.Role.COMPANY,
        )
        self.company = CompanyProfile.objects.create(
            user=self.company_user,
            company_name="StageConnect Labs",
        )

    def test_admin_stats_counts_active_offers(self):
        InternshipOffer.objects.create(
            company=self.company,
            title="Stage Django",
            description="Develop APIs for internships.",
            required_skills="Python Django REST",
            status=InternshipOffer.Status.ACTIVE,
        )
        InternshipOffer.objects.create(
            company=self.company,
            title="Stage React archive",
            description="Build React interfaces.",
            required_skills="React TypeScript",
            status=InternshipOffer.Status.ARCHIVED,
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.get("/api/users/admin/stats/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_students"], 1)
        self.assertEqual(response.data["total_companies"], 1)
        self.assertEqual(response.data["total_offers"], 2)
        self.assertEqual(response.data["active_offers"], 1)

    def test_non_admin_cannot_access_admin_stats(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.get("/api/users/admin/stats/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
