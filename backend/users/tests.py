from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import CompanyProfile, StudentProfile


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
