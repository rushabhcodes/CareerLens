import io
import re
import zipfile
from functools import lru_cache
from pathlib import Path
import pymupdf as fitz
import spacy
from spacy.matcher import PhraseMatcher
from docx import Document
from rest_framework.exceptions import ValidationError
from core.models import Skill

MAX_SIZE = 5 * 1024 * 1024
SECTION_ALIASES = {
    "education": [
        "education",
        "academic qualifications",
        "academics",
        "qualifications",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "internships",
    ],
    "projects": [
        "projects",
        "personal projects",
        "academic projects",
        "selected projects",
    ],
    "certifications": ["certifications", "certificates", "courses"],
    "skills": [
        "skills",
        "technical skills",
        "technologies",
        "skills and tools",
        "core competencies",
        "soft skills",
    ],
    "summary": ["summary", "profile", "professional summary", "objective"],
}


def extract_file(upload):
    ext = Path(upload.name).suffix.lower()
    if ext not in {".pdf", ".docx"}:
        raise ValidationError({"file": "Upload a PDF or DOCX resume."})
    if upload.size > MAX_SIZE:
        raise ValidationError({"file": "The maximum file size is 5 MiB."})
    raw = upload.read(MAX_SIZE + 1)
    upload.seek(0)
    if len(raw) > MAX_SIZE:
        raise ValidationError({"file": "The maximum file size is 5 MiB."})
    try:
        if ext == ".pdf":
            if not raw.startswith(b"%PDF-"):
                raise ValueError("File content is not a PDF.")
            with fitz.open(stream=raw, filetype="pdf") as doc:
                if doc.is_encrypted:
                    raise ValueError("Remove the PDF password before uploading.")
                if len(doc) > 30:
                    raise ValueError("Resumes may contain at most 30 pages.")
                text = "\n".join(page.get_text() for page in doc)
        else:
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                if "word/document.xml" not in archive.namelist():
                    raise ValueError("File content is not a Word document.")
                if (
                    sum(i.file_size for i in archive.infolist()) > 20 * 1024 * 1024
                    or len(archive.infolist()) > 2000
                ):
                    raise ValueError("The DOCX archive exceeds safe extraction limits.")
            doc = Document(io.BytesIO(raw))
            text = "\n".join(
                [p.text for p in doc.paragraphs]
                + [c.text for t in doc.tables for row in t.rows for c in row.cells]
            )
    except ValidationError:
        raise
    except Exception as exc:
        message = (
            str(exc)
            if isinstance(exc, ValueError)
            else "The document is damaged or cannot be read."
        )
        raise ValidationError({"file": message}) from exc
    text = text.replace("\x00", "").strip()
    if len(text) < 40:
        raise ValidationError(
            {
                "file": "No readable resume text was found. Scanned PDFs need OCR, which is not configured. Upload a text-based PDF or DOCX."
            }
        )
    if len(text) > 150000:
        raise ValidationError(
            {"file": "The document contains too much text for a resume."}
        )
    return text


@lru_cache(maxsize=1)
def nlp_pipeline():
    # No downloadable model is needed: this uses spaCy tokenization and PhraseMatcher.
    return spacy.blank("en")


def identify_skills(text):
    nlp = nlp_pipeline()
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    skills = list(Skill.objects.all())
    for skill in skills:
        matcher.add(
            str(skill.pk), [nlp.make_doc(name) for name in [skill.name, *skill.aliases]]
        )
    doc = nlp.make_doc(text)
    found = {}
    for key, start, end in matcher(doc):
        pk = int(nlp.vocab.strings[key])
        span = doc[start:end]
        before = text.rfind("\n", 0, span.start_char) + 1
        after = text.find("\n", span.end_char)
        found[pk] = text[before : after if after != -1 else len(text)][:500].strip()
    return [(skill, found[skill.pk]) for skill in skills if skill.pk in found]


def parse_information(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sections = {}
    current = None
    lookup = {
        alias: name for name, aliases in SECTION_ALIASES.items() for alias in aliases
    }
    for line in lines:
        label = line.lower().rstrip(":").strip()
        if label in lookup:
            current = lookup[label]
            sections.setdefault(current, [])
        elif current:
            sections[current].append(line)
    sections = {key: "\n".join(value) for key, value in sections.items() if value}
    email = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I)
    phone = re.search(
        r"(?<!\d)(?:\+\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,4}\d{3,4}(?!\d)", text
    )
    phone_value = (
        phone.group(0).strip()
        if phone and 10 <= len(re.sub(r"\D", "", phone.group(0))) <= 15
        else ""
    )
    first = lines[0] if lines else ""
    name = (
        first
        if 2 <= len(first.split()) <= 5
        and len(first) <= 80
        and re.fullmatch(r"[A-Za-z .'-]+", first)
        and first.lower() not in lookup
        and "resume" not in first.lower()
        else ""
    )
    explicit_years = re.search(
        r"(\d+(?:\.\d+)?)\+?\s*years?\s+(?:of\s+)?(?:professional\s+|work\s+)?experience",
        text,
        re.I,
    )
    years = float(explicit_years.group(1)) if explicit_years else None
    if years is not None and years > 60:
        years = None
    warnings = [
        "Candidate name is a first-line heuristic. Review the original document.",
        "Skills are explicit vocabulary matches, not verified proficiency.",
    ]
    if years is None:
        warnings.append(
            "Experience years were not explicitly stated. Employment dates are not converted into an estimate."
        )
    return {
        "candidate_name": name,
        "email": email.group(0) if email else "",
        "phone": phone_value,
        "sections": sections,
        "experience_years": years,
        "warnings": warnings,
    }


def quality_report(text, info, skill_count):
    sections = info["sections"]
    contacts = sum(bool(info[k]) for k in ["candidate_name", "email", "phone"])
    section_names = ["education", "experience", "projects", "skills", "certifications"]
    present = sum(bool(sections.get(k)) for k in section_names)
    word_count = len(text.split())
    measurable = bool(
        re.search(
            r"\d+(?:\.\d+)?\s*%|\b(?:increased|reduced|built|developed|delivered|improved|implemented)\b",
            text,
            re.I,
        )
    )
    components = [
        {
            "name": "Contact details",
            "score": round(20 * contacts / 3, 1),
            "maximum": 20,
            "explanation": f"{contacts}/3 detected: name, email and phone. Each contributes 20/3 points.",
        },
        {
            "name": "Section completeness",
            "score": 6 * present,
            "maximum": 30,
            "explanation": f"{present}/5 non-empty sections: education, experience, projects, skills and certifications. Each contributes 6 points.",
        },
        {
            "name": "Skill coverage",
            "score": min(skill_count, 10) * 2.5,
            "maximum": 25,
            "explanation": f"{skill_count} catalog skills detected. 2.5 points per skill, capped at 10 skills. This measures breadth, not proficiency.",
        },
        {
            "name": "Evidence of contribution",
            "score": 15 if measurable else 0,
            "maximum": 15,
            "explanation": "15 points for an action verb or percentage in the text. This heuristic does not assess achievement quality.",
        },
        {
            "name": "Text length",
            "score": 10
            if 150 <= word_count <= 1200
            else 5
            if 60 <= word_count < 150
            else 0,
            "maximum": 10,
            "explanation": f"{word_count} words. 150–1200 words earns 10 points; 60–149 earns 5; other lengths earn 0.",
        },
    ]
    missing = [name for name in section_names if not sections.get(name)]
    suggestions = [
        f"Add a clearly labeled {name} section with truthful evidence."
        for name in missing
    ]
    if contacts < 3:
        suggestions.append(
            "Put your name, email and phone in selectable text at the top."
        )
    if not measurable:
        suggestions.append(
            "Describe a specific contribution and a measurable result where available."
        )
    if word_count < 150:
        suggestions.append(
            "Expand your project and experience descriptions with responsibilities and outcomes."
        )
    return {
        "score": round(sum(c["score"] for c in components)),
        "components": components,
        "missing_sections": missing,
        "suggestions": suggestions,
        "engine": "rule-based-v1",
        "formula": "Quality = contact (20) + sections (30) + skill breadth (25) + contribution evidence (15) + text length (10).",
        "experience_relevance": "Job-specific relevance is evaluated in Job Match, not inferred from this quality score.",
        "word_count": word_count,
    }
