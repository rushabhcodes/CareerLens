import io
import json
import tempfile
import zipfile
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch, Mock
import pymupdf as fitz
import requests
from docx import Document
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from core.models import (
    Resume,
    JobDescription,
    Skill,
    JobRequirement,
    JobMatchAnalysis,
    SkillGapAnalysis,
    AnalysisHistory,
    CareerRecommendation,
    Profile,
)
from core.services.catalog import seed_catalog
from core.services.demo import SAMPLE_TEXT, sample_pdf
from core.services.parsing import extract_file, parse_information, identify_skills
from core.services.provider import enrich_advice

PASSWORD = "Strong!CareerLens42"


class CareerLensTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_catalog()
        cls.owner = get_user_model().objects.create_user(
            username="owner", email="owner@example.com", password=PASSWORD
        )
        cls.other = get_user_model().objects.create_user(
            username="other", email="other@example.com", password=PASSWORD
        )

    def setUp(self):
        cache.clear()
        self.media = tempfile.TemporaryDirectory()
        self.settings = override_settings(MEDIA_ROOT=self.media.name)
        self.settings.enable()
        self.addCleanup(self.settings.disable)
        self.addCleanup(self.media.cleanup)
        self.client = APIClient()
        self.client.force_authenticate(self.owner)

    def upload(self, text=SAMPLE_TEXT, name="resume.pdf"):
        upload = SimpleUploadedFile(
            name, sample_pdf(text), content_type="application/pdf"
        )
        return self.client.post(
            "/api/resumes/", {"file": upload, "title": "My resume"}, format="multipart"
        )

    def job(self, names=("Python", "Docker"), **values):
        payload = {
            "title": "Backend developer",
            "description": "Build reliable Python backend services and deploy them with Docker.",
            "requirements": [
                {"skill": Skill.objects.get(name=n).pk, "importance": "essential"}
                for n in names
            ],
            **values,
        }
        response = self.client.post("/api/jobs/", payload, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def comparison(self, **job_values):
        resume = self.upload()
        self.assertEqual(resume.status_code, 201, resume.data)
        job = self.job(**job_values)
        response = self.client.post(
            "/api/matches/",
            {"resume": resume.data["id"], "job": job["id"]},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def test_registration_hashes_password_and_starts_empty(self):
        self.client.force_authenticate(None)
        response = self.client.post(
            "/api/auth/register/",
            {"first_name": "Taylor", "email": "NEW@example.com", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        user = get_user_model().objects.get(email="new@example.com")
        self.assertTrue(user.check_password(PASSWORD))
        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertFalse(user.resumes.exists())

    def test_weak_password_and_duplicate_registration_rejected(self):
        self.client.force_authenticate(None)
        for values in [
            {"first_name": "New", "email": "new@example.com", "password": "password"},
            {"first_name": "New", "email": self.owner.email, "password": PASSWORD},
        ]:
            self.assertEqual(
                self.client.post(
                    "/api/auth/register/", values, format="json"
                ).status_code,
                400,
            )

    def test_login_logout_revokes_token(self):
        self.client.force_authenticate(None)
        login = self.client.post(
            "/api/auth/login/",
            {"email": self.owner.email.upper(), "password": PASSWORD},
            format="json",
        )
        self.assertEqual(login.status_code, 200, login.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 200)
        self.assertEqual(self.client.post("/api/auth/logout/").status_code, 200)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)

    def test_invalid_login_does_not_expose_account_existence(self):
        self.client.force_authenticate(None)
        responses = [
            self.client.post(
                "/api/auth/login/",
                {"email": email, "password": "incorrect"},
                format="json",
            )
            for email in [self.owner.email, "missing@example.com"]
        ]
        self.assertEqual(responses[0].status_code, 401)
        self.assertEqual(responses[0].data, responses[1].data)

    def test_expired_token_rejected(self):
        token = Token.objects.create(user=self.owner)
        Token.objects.filter(pk=token.pk).update(
            created=timezone.now() - timedelta(days=2)
        )
        self.client.force_authenticate(None)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.assertEqual(self.client.get("/api/dashboard/").status_code, 401)

    def test_profile_update_cannot_escalate_staff(self):
        response = self.client.patch(
            "/api/auth/me/",
            {"first_name": "Updated", "headline": "MCA student", "is_staff": True},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.first_name, "Updated")
        self.assertFalse(self.owner.is_staff)

    def test_unauthenticated_user_cannot_read_records(self):
        self.client.force_authenticate(None)
        for path in [
            "resumes",
            "jobs",
            "matches",
            "dashboard",
            "careers",
            "history",
            "skills",
        ]:
            self.assertEqual(self.client.get(f"/api/{path}/").status_code, 401)

    def test_pdf_upload_extracts_and_persists_real_evidence(self):
        response = self.upload()
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["extracted"]["email"], "alex.morgan@example.com")
        self.assertEqual(response.data["extracted"]["candidate_name"], "Alex Morgan")
        self.assertEqual(response.data["extracted"]["experience_years"], 2)
        names = [row["skill"]["name"] for row in response.data["skill_evidence"]]
        self.assertIn("Python", names)
        self.assertNotIn("Docker", names)
        resume = Resume.objects.get(pk=response.data["id"])
        self.assertTrue(Path(resume.file.path).exists())
        self.assertTrue(
            AnalysisHistory.objects.filter(resume=resume, kind="resume").exists()
        )

    def test_docx_text_and_table_extraction(self):
        doc = Document()
        for line in SAMPLE_TEXT.splitlines():
            doc.add_paragraph(line)
        table = doc.add_table(rows=1, cols=1)
        table.cell(0, 0).text = "Docker"
        stream = io.BytesIO()
        doc.save(stream)
        upload = SimpleUploadedFile("resume.docx", stream.getvalue())
        response = self.client.post(
            "/api/resumes/", {"file": upload}, format="multipart"
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertIn("Docker", response.data["extracted"]["text"])

    def test_invalid_extension_and_spoofed_pdf_rejected(self):
        for name, raw in [
            ("resume.exe", b"bad"),
            ("resume.pdf", b"not a pdf"),
            ("resume.docx", b"invalid zip"),
        ]:
            response = self.client.post(
                "/api/resumes/",
                {"file": SimpleUploadedFile(name, raw)},
                format="multipart",
            )
            self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(Resume.objects.count(), 0)

    def test_oversized_upload_rejected(self):
        response = self.client.post(
            "/api/resumes/",
            {
                "file": SimpleUploadedFile(
                    "big.pdf", b"%PDF-" + b"x" * (5 * 1024 * 1024)
                )
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, 400)

    def test_scan_and_password_protection_have_actionable_errors(self):
        doc = fitz.open()
        doc.new_page()
        for raw in [
            doc.tobytes(),
            doc.tobytes(
                encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw="owner", user_pw="secret"
            ),
        ]:
            response = self.client.post(
                "/api/resumes/",
                {"file": SimpleUploadedFile("scan.pdf", raw)},
                format="multipart",
            )
            self.assertEqual(response.status_code, 400)
        self.assertIn("password", str(response.data).lower())
        doc.close()

    def test_unknown_candidate_information_stays_unknown(self):
        info = parse_information(
            "RESUME\nSkills\nPython, SQL\nProjects\nBuilt an application without contact details."
        )
        self.assertEqual(info["candidate_name"], "")
        self.assertEqual(info["email"], "")
        self.assertIsNone(info["experience_years"])

    def test_quality_components_add_up(self):
        response = self.upload()
        report = response.data["quality_report"]
        self.assertEqual(
            response.data["quality_score"],
            round(sum(c["score"] for c in report["components"])),
        )
        self.assertEqual(sum(c["maximum"] for c in report["components"]), 100)

    def test_skill_matching_respects_token_boundaries(self):
        names = [
            s.name
            for s, _ in identify_skills(
                "JavaScript and MySQL, not unrelated names like Reactivate."
            )
        ]
        self.assertIn("JavaScript", names)
        self.assertIn("MySQL", names)
        self.assertNotIn("Java", names)
        self.assertNotIn("React", names)

    def test_original_download_is_private_and_delete_removes_file(self):
        response = self.upload()
        pk = response.data["id"]
        path = Resume.objects.get(pk=pk).file.path
        self.assertEqual(
            self.client.get(f"/api/resumes/{pk}/download/").status_code, 200
        )
        self.client.force_authenticate(self.other)
        for suffix in ["", "download/", "report/"]:
            self.assertEqual(
                self.client.get(f"/api/resumes/{pk}/{suffix}").status_code, 404
            )
        self.assertEqual(self.client.delete(f"/api/resumes/{pk}/").status_code, 404)
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.delete(f"/api/resumes/{pk}/").status_code, 204)
        self.assertFalse(Path(path).exists())

    def test_job_crud_and_auto_detected_requirements(self):
        response = self.client.post(
            "/api/jobs/",
            {
                "title": "Python developer",
                "description": "Develop Python applications with Django and automated testing.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        pk = response.data["id"]
        self.assertTrue(response.data["requirements"])
        edited = self.client.patch(
            f"/api/jobs/{pk}/", {"company": "My company"}, format="json"
        )
        self.assertEqual(edited.data["company"], "My company")
        self.assertEqual(self.client.delete(f"/api/jobs/{pk}/").status_code, 204)

    def test_invalid_job_duplicate_requirements_and_negative_years(self):
        skill = Skill.objects.get(name="Python").pk
        for values in [
            {"description": "tiny"},
            {"experience_years": -1},
            {"requirements": [{"skill": skill}, {"skill": skill}]},
        ]:
            response = self.client.post(
                "/api/jobs/",
                {
                    "title": "Role",
                    "description": "Develop reliable Python and Django applications.",
                    **values,
                },
                format="json",
            )
            self.assertEqual(response.status_code, 400, response.data)

    def test_job_and_match_ownership(self):
        resume_id = self.upload().data["id"]
        job = self.job()
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(f"/api/jobs/{job['id']}/").status_code, 404)
        self.assertEqual(
            self.client.patch(
                f"/api/jobs/{job['id']}/", {"title": "Stolen"}, format="json"
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(
                "/api/matches/", {"resume": resume_id, "job": job["id"]}, format="json"
            ).status_code,
            404,
        )
        self.assertEqual(self.client.get("/api/resumes/").data["count"], 0)

    def test_weighted_skills_missing_gaps_and_transaction(self):
        result = self.comparison()
        self.assertEqual(result["score"], 50)
        self.assertEqual([s["name"] for s in result["result"]["matched"]], ["Python"])
        self.assertEqual([s["name"] for s in result["result"]["missing"]], ["Docker"])
        self.assertEqual(SkillGapAnalysis.objects.count(), 1)
        gap = SkillGapAnalysis.objects.first()
        self.assertEqual(gap.roadmap[0]["name"], "Docker")
        self.assertTrue(gap.roadmap[0]["resources"])

    def test_partially_related_skill_receives_half_credit(self):
        result = self.comparison(names=("TypeScript",))
        self.assertEqual(result["score"], 50)
        self.assertEqual(result["result"]["partial"][0]["related_skill"], "JavaScript")

    def test_experience_and_qualification_components(self):
        result = self.comparison(
            names=("Python",), experience_years=4, qualification="MCA"
        )
        # Skills 100*70 + experience 50*20 + qualification 100*10 = 9000 / 100.
        self.assertEqual(result["score"], 90)
        self.assertEqual(result["result"]["active_weight"], 100)

    def test_unknown_experience_earns_zero_not_invented_credit(self):
        resume = self.upload(SAMPLE_TEXT.replace("2 years of experience", "experience"))
        job = self.job(names=("Python",), experience_years=2)
        result = self.client.post(
            "/api/matches/",
            {"resume": resume.data["id"], "job": job["id"]},
            format="json",
        )
        self.assertEqual(result.data["score"], 77.8)
        self.assertIn("Unknown", result.data["result"]["experience"])

    def test_saved_match_keeps_job_snapshot_after_edit(self):
        result = self.comparison()
        self.client.patch(
            f"/api/jobs/{result['job']}/", {"title": "Changed title"}, format="json"
        )
        saved = self.client.get(f"/api/matches/{result['id']}/").data
        self.assertEqual(saved["job_title"], "Backend developer")

    def test_deleting_job_removes_dependent_match_history(self):
        result = self.comparison()
        self.client.delete(f"/api/jobs/{result['job']}/")
        self.assertEqual(JobMatchAnalysis.objects.count(), 0)
        self.assertEqual(SkillGapAnalysis.objects.count(), 0)
        self.assertFalse(AnalysisHistory.objects.filter(kind="job_match").exists())

    def test_career_recommendation_is_persisted_and_owned(self):
        pk = self.upload().data["id"]
        response = self.client.post(
            f"/api/resumes/{pk}/recommend/", {"use_ai": False}, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]["engine"], "rule-based-v1")
        self.assertEqual(CareerRecommendation.objects.count(), len(response.data))
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get("/api/careers/").data["count"], 0)
        self.assertEqual(
            self.client.post(
                f"/api/resumes/{pk}/recommend/", {}, format="json"
            ).status_code,
            404,
        )

    def test_dashboard_uses_database_and_excludes_other_accounts(self):
        self.comparison()
        dashboard = self.client.get("/api/dashboard/").data
        self.assertEqual(dashboard["total_resumes"], 1)
        self.assertEqual(dashboard["total_matches"], 1)
        self.assertEqual(dashboard["average_match"], 50)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get("/api/dashboard/").data["total_resumes"], 0)
        self.assertEqual(self.client.get("/api/history/").data["count"], 0)

    def test_pagination_and_search(self):
        JobDescription.objects.bulk_create(
            [
                JobDescription(
                    user=self.owner, title=f"Role {n}", description="Python services"
                )
                for n in range(23)
            ]
        )
        response = self.client.get("/api/jobs/")
        self.assertEqual(len(response.data["results"]), 20)
        self.assertTrue(response.data["next"])
        self.assertEqual(
            self.client.get("/api/jobs/?search=Role%2022").data["count"], 1
        )

    def test_invalid_resume_filter_returns_validation_error(self):
        for endpoint in ["matches", "careers"]:
            for value in ["abc", "-1", ""]:
                response = self.client.get(f"/api/{endpoint}/?resume={value}")
                self.assertEqual(response.status_code, 400)

    def test_staff_statistics_require_staff_permissions(self):
        self.assertEqual(self.client.get("/api/system/").status_code, 403)
        self.owner.is_staff = True
        self.owner.save()
        self.assertEqual(self.client.get("/api/system/").status_code, 200)

    def test_database_enforces_unique_job_requirement(self):
        job = JobDescription.objects.create(
            user=self.owner, title="Role", description="Python"
        )
        skill = Skill.objects.get(name="Python")
        JobRequirement.objects.create(job=job, skill=skill)
        with self.assertRaises(IntegrityError), transaction.atomic():
            JobRequirement.objects.create(job=job, skill=skill)

    def test_catalog_seed_is_safe_to_repeat(self):
        skill_count = Skill.objects.count()
        relation_count = Skill.related_skills.through.objects.count()
        seed_catalog()
        seed_catalog()
        self.assertEqual(Skill.objects.count(), skill_count)
        self.assertEqual(Skill.related_skills.through.objects.count(), relation_count)

    @override_settings(LLM_API_KEY="", LLM_BASE_URL="", LLM_MODEL="")
    def test_llm_without_credentials_falls_back(self):
        self.assertEqual(enrich_advice({})["advice"], [])

    @override_settings(
        LLM_API_KEY="test-only",
        LLM_BASE_URL="https://provider.example/v1",
        LLM_MODEL="test-model",
    )
    @patch("core.services.provider.requests.post")
    def test_llm_schema_validation_success_and_invalid_results(self, post):
        response = Mock()
        response.content = b"{}"
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"recommendations":["Build a small Docker deployment."]}'
                    }
                }
            ]
        }
        post.return_value = response
        self.assertEqual(len(enrich_advice({})["advice"]), 1)
        response.json.return_value = {
            "choices": [{"message": {"content": '{"recommendations":[4],"score":100}'}}]
        }
        self.assertEqual(enrich_advice({})["advice"], [])

    @override_settings(
        LLM_API_KEY="test-only",
        LLM_BASE_URL="https://provider.example/v1",
        LLM_MODEL="test-model",
    )
    @patch("core.services.provider.requests.post")
    def test_llm_timeout_and_rate_limit_fall_back(self, post):
        post.side_effect = requests.Timeout()
        self.assertEqual(enrich_advice({})["advice"], [])
        post.side_effect = requests.HTTPError("429 Too Many Requests")
        self.assertEqual(enrich_advice({})["advice"], [])

    @override_settings(DEMO_ENABLED=False)
    def test_demo_can_be_disabled(self):
        self.client.force_authenticate(None)
        self.assertEqual(
            self.client.post("/api/auth/demo/", {}, format="json").status_code, 404
        )
