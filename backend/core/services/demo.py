import io
import uuid
import pymupdf as fitz
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Profile, JobDescription, JobRequirement, Skill
from core.serializers import ResumeUploadSerializer
from core.services.analysis import create_match, recommend_careers

SAMPLE_TEXT = """Alex Morgan
alex.morgan@example.com | +91 98765 43210
Summary
Software developer with 2 years of experience building practical web applications.
Education
Master of Computer Applications (MCA), Example Institute, 2026
Experience
Software developer, Sample Studio, 2024 to 2026
Built REST APIs with Python and Django. Reduced response time by 25%.
Developed React interfaces and SQL queries. Used Git for version control.
Collaborated with a small team and practiced communication and problem solving.
Projects
Career portfolio: Developed a React and Django application with MySQL persistence.
Task manager: Built JavaScript, HTML and CSS interfaces with automated testing.
Skills
Python, Django, JavaScript, React, HTML, CSS, SQL, MySQL, Git, REST APIs,
Testing, Communication, Teamwork, Problem solving
Certifications
Python fundamentals course, Sample Learning Institute
This is a synthetic resume created solely to demonstrate CareerLens.
The companies, institute, contact details and achievements are fictional.
"""


def sample_pdf(text):
    document = fitz.open()
    page = document.new_page()
    page.insert_textbox(fitz.Rect(45, 40, 550, 800), text, fontsize=11)
    raw = document.tobytes()
    document.close()
    return raw


def create_demo_workspace():
    token = uuid.uuid4().hex
    user = get_user_model().objects.create_user(
        username=f"sample-{token}",
        email=f"sample-{token}@example.invalid",
        password=uuid.uuid4().hex,
        first_name="Alex",
        last_name="Morgan",
    )
    Profile.objects.create(
        user=user,
        headline="Sample workspace · synthetic data",
        career_goal="Explore full-stack development",
    )

    class Request:
        pass

    request = Request()
    request.user = user
    resume = None
    for title, text in [
        (
            "Portfolio resume",
            SAMPLE_TEXT.replace("Testing, Communication", "Communication").replace(
                " with automated testing", ""
            ),
        ),
        ("Full-stack resume", SAMPLE_TEXT),
    ]:
        serializer = ResumeUploadSerializer(
            data={
                "title": title,
                "file": SimpleUploadedFile(
                    "sample-resume.pdf",
                    sample_pdf(text),
                    content_type="application/pdf",
                ),
            },
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        resume = serializer.save()
    for title, names in [
        (
            "Full-stack developer",
            [
                "Python",
                "Django",
                "React",
                "SQL",
                "Docker",
                "TypeScript",
                "Communication",
            ],
        ),
        (
            "Python backend developer",
            ["Python", "Django", "REST APIs", "Docker", "AWS", "Testing"],
        ),
        (
            "Frontend developer",
            ["JavaScript", "React", "HTML", "CSS", "TypeScript", "Accessibility"],
        ),
    ]:
        job = JobDescription.objects.create(
            user=user,
            title=title,
            company="Sample company",
            description=f"Synthetic demonstration job. Build reliable products as a {title.lower()} using {', '.join(names)}. Work with a collaborative team and document your decisions.",
            experience_years=2,
            qualification="MCA",
        )
        for index, name in enumerate(names):
            JobRequirement.objects.create(
                job=job,
                skill=Skill.objects.get(name=name),
                importance="essential" if index < 4 else "preferred",
            )
        create_match(user, resume, job)
    recommend_careers(resume)
    return user
