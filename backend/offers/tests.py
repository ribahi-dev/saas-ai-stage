from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APITestCase

from offers.scraper import _is_moroccan_offer, _normalize_text
from offers.scraper_ai import _parse_batch_json
from offers.models import Application, InternshipOffer
from users.models import CompanyProfile, StudentProfile, User


class ScraperMoroccoFilterTests(SimpleTestCase):
    def test_is_moroccan_offer_positive(self):
        self.assertTrue(
            _is_moroccan_offer(
                {
                    "title": "Stage developpeur",
                    "description": "Poste base a Rabat",
                    "location": "Rabat",
                }
            )
        )

    def test_is_moroccan_offer_negative(self):
        self.assertFalse(
            _is_moroccan_offer(
                {
                    "title": "Software engineer",
                    "description": "Berlin startup",
                    "location": "Berlin",
                }
            )
        )

    def test_normalize_text(self):
        self.assertEqual(_normalize_text("  Python  Django  "), "python django")


class ScraperAIParseTests(SimpleTestCase):
    def test_parse_batch_json_array(self):
        raw = '[{"index": 0, "skills": ["Python"], "offer_type": "stage"}]'
        rows = _parse_batch_json(raw)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].get("index"), 0)


class OfferWorkflowTests(APITestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            username="student_flow",
            email="student.flow@example.com",
            password="StrongPass123!",
            role=User.Role.STUDENT,
        )
        self.student = StudentProfile.objects.create(user=self.student_user)
        self.company_user = User.objects.create_user(
            username="company_flow",
            email="company.flow@example.com",
            password="StrongPass123!",
            role=User.Role.COMPANY,
        )
        self.company = CompanyProfile.objects.create(
            user=self.company_user,
            company_name="StageConnect Flow",
        )

    def offer_payload(self):
        return {
            "title": "Stage Full Stack",
            "offer_type": InternshipOffer.OfferType.STAGE,
            "description": "Construire une plateforme de stages.",
            "required_skills": "Python Django React TypeScript",
            "location": "Casablanca",
            "duration_months": 4,
            "is_paid": False,
            "status": InternshipOffer.Status.ACTIVE,
        }

    def test_company_can_create_offer_and_student_cannot(self):
        self.client.force_authenticate(user=self.student_user)
        student_response = self.client.post(
            "/api/offers/",
            self.offer_payload(),
            format="json",
        )
        self.assertEqual(student_response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.company_user)
        company_response = self.client.post(
            "/api/offers/",
            self.offer_payload(),
            format="json",
        )

        self.assertEqual(company_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InternshipOffer.objects.count(), 1)
        self.assertEqual(InternshipOffer.objects.get().company, self.company)

    def test_student_application_and_company_status_workflow(self):
        offer = InternshipOffer.objects.create(company=self.company, **self.offer_payload())
        self.client.force_authenticate(user=self.student_user)

        apply_response = self.client.post(
            f"/api/offers/{offer.id}/apply/",
            {"cover_letter": "Je suis motive."},
            format="json",
        )
        duplicate_response = self.client.post(
            f"/api/offers/{offer.id}/apply/",
            {"cover_letter": "Deuxieme tentative."},
            format="json",
        )

        self.assertEqual(apply_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)
        application = Application.objects.get()

        self.client.force_authenticate(user=self.company_user)
        received_response = self.client.get("/api/offers/received-applications/")
        status_response = self.client.patch(
            f"/api/offers/applications/{application.id}/status/",
            {"status": Application.Status.ACCEPTED},
            format="json",
        )

        self.assertEqual(received_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(received_response.data["results"]), 1)
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        application.refresh_from_db()
        self.assertEqual(application.status, Application.Status.ACCEPTED)
