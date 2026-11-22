"""Build the academic DOCX from implemented behavior and captured evidence.
Run with the bundled artifact Python runtime, then render with render_docx.py.
"""

from pathlib import Path
import re
from PIL import Image
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION_START, WD_ORIENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
QA = OUT / "qa"
QA.mkdir(exist_ok=True)
doc = Document()
sec = doc.sections[0]
sec.page_width = Inches(8.27)
sec.page_height = Inches(11.69)
sec.top_margin = sec.bottom_margin = Inches(0.72)
sec.left_margin = sec.right_margin = Inches(0.8)
for name in [
    "Normal",
    "Body Text",
    "Title",
    "Subtitle",
    "Heading 1",
    "Heading 2",
    "Heading 3",
    "Header",
    "Footer",
    "Caption",
]:
    s = doc.styles[name]
    s.font.name = "Arial"
    s.font.color.rgb = RGBColor(0, 0, 0)
    s.font.size = Pt(11)
    s.paragraph_format.space_after = Pt(7)
    s.paragraph_format.line_spacing = 1.12
for name, size in [
    ("Title", 32),
    ("Subtitle", 16),
    ("Heading 1", 19),
    ("Heading 2", 14),
    ("Heading 3", 12),
]:
    doc.styles[name].font.size = Pt(size)
    doc.styles[name].font.bold = name != "Subtitle"
    doc.styles[name].paragraph_format.space_before = Pt(15)
    doc.styles[name].paragraph_format.keep_with_next = True
# No theme colors, borders or decorative title rules.
for name in ["Title", "Subtitle", "Heading 1", "Heading 2", "Heading 3"]:
    ppr = doc.styles[name].element.find(qn("w:pPr"))
    if ppr is not None:
        for e in list(ppr):
            if e.tag == qn("w:pBdr"):
                ppr.remove(e)
header = sec.header.paragraphs[0]
header.text = "CareerLens  /  MCA Semester 3 project report"
header.style = "Header"
header.runs[0].font.size = Pt(9)
footer = sec.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = footer.add_run("CareerLens  |  ")
r.font.size = Pt(9)
fld = OxmlElement("w:fldSimple")
fld.set(qn("w:instr"), "PAGE")
footer._p.append(fld)


def p(text, style=None):
    return doc.add_paragraph(text, style)


def h(title, level=1):
    return doc.add_heading(title, level)


def page(title):
    doc.add_page_break()
    h(title)


def table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    if widths:
        for i, width in enumerate(widths):
            t.columns[i].width = Inches(width)
    for i, value in enumerate(headers):
        t.rows[0].cells[i].text = str(value)
    for row in rows:
        cells = t.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = str(value)
    for ri, row in enumerate(t.rows):
        trpr = row._tr.get_or_add_trPr()
        if ri == 0:
            repeat = OxmlElement("w:tblHeader")
            trpr.append(repeat)
        for ci, cell in enumerate(row.cells):
            if widths:
                cell.width = Inches(widths[ci])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr = cell._tc.get_or_add_tcPr()
            borders = OxmlElement("w:tcBorders")
            for side in ["top", "left", "bottom", "right"]:
                e = OxmlElement("w:" + side)
                e.set(qn("w:val"), "single")
                e.set(qn("w:sz"), "4")
                e.set(qn("w:color"), "D9D9D9")
                borders.append(e)
            tcpr.append(borders)
            shade = OxmlElement("w:shd")
            shade.set(
                qn("w:fill"),
                "213B30" if ri == 0 else ("F1F5F2" if ri % 2 == 0 else "FFFFFF"),
            )
            tcpr.append(shade)
            margins = OxmlElement("w:tcMar")
            for side in ["top", "bottom", "left", "right"]:
                e = OxmlElement("w:" + side)
                e.set(qn("w:w"), "100")
                e.set(qn("w:type"), "dxa")
                margins.append(e)
            tcpr.append(margins)
            for para in cell.paragraphs:
                para.paragraph_format.space_after = Pt(3)
                para.paragraph_format.space_before = Pt(3)
                for run in para.runs:
                    run.font.size = Pt(9)
                    run.font.bold = ri == 0
                    run.font.color.rgb = (
                        RGBColor(255, 255, 255) if ri == 0 else RGBColor(0, 0, 0)
                    )
    p("")
    return t


def image(source, caption, max_w=6.5, max_h=6.8, crop=False):
    source = Path(source)
    if not source.exists():
        raise FileNotFoundError(source)
    im = Image.open(source)
    if crop:
        im = im.crop((0, 0, im.width, min(im.height, 1050)))
        source = QA / (source.stem + "-report.png")
        im.save(source)
    w, hgt = im.size
    width = min(max_w, max_h * w / hgt)
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.add_run().add_picture(str(source), width=Inches(width))
    para.paragraph_format.keep_with_next = True
    shape = doc.inline_shapes[-1]
    shape._inline.docPr.set("descr", caption)
    c = p(caption, "Caption")
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in c.runs:
        run.font.size = Pt(9)


p("MCA SEMESTER 3  /  MAJOR ACADEMIC PROJECT")
p("CareerLens project report", "Title")
p("AI Powered Resume Analysis and Career Recommendation System", "Subtitle")
p("A full stack application with explainable scoring and optional AI learning advice")
p("Prepared as an academic software project\n22 November 2026")
p(
    "This report documents the implemented local application, its architecture, algorithms, security boundaries and executed validation. It accompanies the source code, database scripts, API collection, screenshots, presentation, viva guide and demonstration script."
)
p(
    "The application works without provider credentials through a deterministic local engine. Optional LLM advice is labeled separately. Scores measure documented alignment and never represent a hiring probability."
)
p(
    "Student and institution details can be added to this editable report before submission. No institutional approval, supervisor endorsement or examination outcome is claimed."
)

page("Abstract and report guide")
p(
    "CareerLens supports job seekers who need a clear view of the information in a resume and its relationship to a target role. A user uploads a PDF or DOCX, reviews extracted contact and section evidence, saves job requirements, and receives an explainable comparison with a skill development roadmap. A managed career catalog offers additional roles based on explicit skill overlap."
)
p(
    "The implementation uses React and Vite in JavaScript, Tailwind CSS, Django REST Framework and MySQL. PyMuPDF and python-docx extract text. spaCy provides tokenization and vocabulary phrase matching. The local analysis engine stores evidence and component formulas rather than generating unsupported candidate facts. An optional HTTPS LLM integration can enrich learning advice after explicit opt-in and schema validation."
)
p(
    "Authentication, owner-scoped queries, private file downloads, upload limits and database constraints protect the records. The application has been exercised through backend tests on MySQL, React tests, browser workflows and a Postman collection executed with Newman. Live AI-provider access, OCR and public deployment are outside the verified local scope."
)
h("Report contents", 2)
for title in [
    "Problem and requirements",
    "Technology and feasibility",
    "Architecture and workflows",
    "Database design",
    "Resume processing and scoring",
    "Job matching and skill development",
    "Optional AI integration",
    "Security and administration",
    "Implementation and request cycle",
    "Testing and verification",
    "User interface evidence",
    "Deployment and maintenance",
    "Limitations and future work",
    "References and supporting deliverables",
]:
    p(title, "List Bullet")

page("Problem and requirements")
h("Problem statement", 2)
p(
    "Students often revise resumes without a clear connection to the requirements of a specific role. A generic score alone does not tell them which information the application found, why it counted, or what they should improve. CareerLens places extracted evidence beside explicit job requirements so a user can assess the result and make a learning decision."
)
h("Objectives", 2)
for text in [
    "Preserve uploaded originals securely and extract only supported information.",
    "Calculate transparent structural quality and job alignment scores.",
    "Identify full, partial and missing skill evidence with priorities.",
    "Recommend career roles and learning resources from a managed catalog.",
    "Persist each account’s records and expose useful dashboard analytics.",
    "Keep optional generative advice separate from deterministic facts and scores.",
]:
    p(text, "List Bullet")
h("Functional scope", 2)
p(
    "The project includes registration, login, logout and profile editing; private resume management; extracted candidate details; saved job CRUD; job matching; skill gap roadmaps; career recommendations; database-driven charts and activity history; and staff statistics with Django admin catalog management. Every major user action calls a real API and persists the resulting record where appropriate."
)
h("Nonfunctional requirements", 2)
p(
    "The implementation aims for understandable calculations, secure account separation, responsive desktop and mobile navigation, actionable validation errors, modular services, reproducible setup and automated verification. These are engineering requirements for the local project, not claims of externally certified security or measured production throughput."
)

page("Technology and feasibility")
table(
    ["Layer", "Technology", "Purpose"],
    [
        [
            "Frontend",
            "React, JavaScript, Vite",
            "Routed views and reactive interaction",
        ],
        ["Styling", "Tailwind CSS and project CSS", "Responsive visual system"],
        ["Visualization", "Recharts", "Real database chart series"],
        ["API", "Django REST Framework", "Validation, routing and permissions"],
        [
            "Persistence",
            "MySQL 8.4, Connector/Python",
            "Transactions and relational storage",
        ],
        [
            "Extraction",
            "PyMuPDF and python-docx",
            "PDF text and Word paragraphs/tables",
        ],
        ["NLP", "spaCy PhraseMatcher", "Explicit skills and alias detection"],
        [
            "Optional AI",
            "HTTPS chat-completions provider, Pydantic",
            "Validated learning advice",
        ],
        [
            "Verification",
            "Django tests, Vitest, Playwright, Newman",
            "Service, API and browser checks",
        ],
    ],
    [1.0, 2.15, 3.2],
)
h("Technical feasibility", 2)
p(
    "The default analysis requires no paid provider, external credential or downloadable language model. All core records persist locally in MySQL. A private database installation under the project allows a demonstration without modifying system services. An existing MySQL instance or Docker Compose is an alternative setup path."
)
h("Operational feasibility", 2)
p(
    "A student can demonstrate the entire request cycle with a supplied synthetic PDF or DOCX. The sample workspace is explicitly labeled and creates isolated stored records, while a newly registered account starts empty. The README and demonstration guide give the required commands and explain the observable outcome of each step."
)

page("System architecture")
image(
    ROOT / "docs/diagrams/architecture.png",
    "Figure 1  System architecture and trust boundaries",
    max_h=5.7,
)
p(
    "React communicates with Django over authenticated HTTP. Django checks record ownership before service operations or downloads. The service layer extracts text, identifies skills and calculates scores. The API alone accesses MySQL and private file storage. Optional LLM communication originates from the server and includes only the opted-in role and skill context."
)
p(
    "The frontend contains reusable components, a central API client, authentication context and routed pages. The backend separates models, serializers, viewsets and services so that calculations remain testable and do not depend on visual components."
)

page("Use cases and data flow")
image(
    ROOT / "docs/diagrams/use-cases.png",
    "Figure 2  User and administrator use cases",
    max_h=4.1,
)
image(
    ROOT / "docs/diagrams/dfd-context.png",
    "Figure 3  Context level data flow",
    max_h=3.8,
)

page("Detailed analysis data flow")
image(
    ROOT / "docs/diagrams/dfd-level-1.png", "Figure 4  Level one data flow", max_h=6.4
)
p(
    "The upload path validates before extraction and persistence. A match reads stored evidence and requirements, then creates a match record, its skill gap and a history entry atomically. Career generation reads the managed role catalog and stores its evidence and roadmap. Dashboard views aggregate the same account-owned database records."
)

page("Database design")
p(
    "The data model normalizes reusable facts such as skills, roles and learning resources. Join tables record resume evidence and job requirement importance. A user owns resumes and saved jobs, and dependent analysis records follow these ownership chains. Immutable JSON fields store the exact component values and job snapshot used by an analysis, while the underlying reusable vocabulary remains relational."
)
table(
    ["Entity", "Key relationship", "Stored information"],
    [
        [
            "User and Profile",
            "One profile per user",
            "Unique email, hashed password, headline and goal",
        ],
        [
            "Resume",
            "Many per user",
            "Private file, size, quality components and creation time",
        ],
        [
            "ExtractedInformation",
            "One per resume",
            "Text, contact fields, sections and explicit years",
        ],
        [
            "Skill",
            "Shared catalog",
            "Unique name, category, aliases and related skills",
        ],
        ["ResumeSkill", "Unique resume and skill", "Source evidence line"],
        [
            "JobDescription",
            "Many per user",
            "Title, company, description, years and qualification",
        ],
        ["JobRequirement", "Unique job and skill", "Essential or preferred importance"],
        [
            "JobMatchAnalysis",
            "User, resume and job",
            "Score, version, evidence and immutable job snapshot",
        ],
        ["SkillGapAnalysis", "One per match", "Prioritized gaps and roadmap"],
        [
            "CareerRole and JobCategory",
            "Category groups roles",
            "Catalog role description and required skills",
        ],
        [
            "CareerRecommendation",
            "Resume and role",
            "Coverage, explanation, roadmap and provenance",
        ],
        ["LearningResource", "Many per skill", "Title, level and URL"],
        [
            "AnalysisHistory",
            "User, resume and optional match",
            "Activity type, title, score and timestamp",
        ],
    ],
    [1.7, 1.7, 2.95],
)


# A dedicated landscape page keeps the full relationship diagram usable.
land = doc.add_section(WD_SECTION_START.NEW_PAGE)
land.orientation = WD_ORIENT.LANDSCAPE
land.page_width = Inches(11.69)
land.page_height = Inches(8.27)
land.left_margin = land.right_margin = Inches(0.55)
land.top_margin = land.bottom_margin = Inches(0.6)
h("Database entity relationship diagram")
image(
    ROOT / "docs/diagrams/er-diagram.png",
    "Figure 5  Domain entities and relationship cardinality",
    max_w=10.5,
    max_h=4.9,
)
p(
    "The complete scalable SVG and editable Graphviz source are supplied in docs/diagrams. Authentication and Django administration support tables are present in the schema but omitted from this domain view."
)
p(
    "Foreign keys and unique pairs enforce valid references and prevent duplicate evidence or requirements. Creation-time indexes support recent records. Source deletion removes dependent analyses and their history. Resume deletion also removes the original file, verified by an executed test."
)
portrait = doc.add_section(WD_SECTION_START.NEW_PAGE)
portrait.orientation = WD_ORIENT.PORTRAIT
portrait.page_width = Inches(8.27)
portrait.page_height = Inches(11.69)
portrait.left_margin = portrait.right_margin = Inches(0.8)
portrait.top_margin = portrait.bottom_margin = Inches(0.72)
h("Resume processing and information extraction")
p(
    "An uploaded file passes extension and size checks, then content validation. PDFs must begin with the PDF signature and parse successfully. Encrypted files, files above 30 pages, unreadable scans and excessive text return useful validation errors. DOCX archives must contain Word document XML, remain within expansion and entry limits, and parse with python-docx. The parser includes table text because many resumes use tables for layout."
)
p(
    "The extraction service preserves the original text. Contact expressions find email and plausible phone evidence, while a conservative first-line heuristic suggests a candidate name. Recognized headings identify education, experience, projects, certifications, summary and skills. Experience years require an explicit statement such as “2 years of experience.” The service does not infer duration from dates or manufacture missing fields."
)
h("Vocabulary based NLP", 2)
p(
    "spaCy tokenizes the extracted text. PhraseMatcher compares catalog skill names and administrator-defined aliases without substring guessing. This prevents JavaScript from counting as Java and avoids matching React inside an unrelated word. Every detected skill stores a nearby source line. The interface states that an explicit mention does not prove proficiency."
)
h("Quality formula", 2)
table(
    ["Component", "Points", "Rule"],
    [
        ["Contact details", "20", "Name, email and phone share 20 points"],
        ["Section completeness", "30", "Five recognized non-empty sections, 6 each"],
        ["Skill breadth", "25", "2.5 points per catalog skill, capped at 10 skills"],
        ["Contribution evidence", "15", "An action verb or percentage appears"],
        ["Text length", "10", "150–1200 words = 10; 60–149 = 5; otherwise 0"],
    ],
    [1.55, 0.65, 4.15],
)
p(
    "Each displayed component explains its evidence and cap. This is a structural heuristic rather than a validated labor-market outcome model. A certification heading can improve completeness without establishing certification authenticity. Users should review the original document and use the suggestions in context."
)

page("Job matching and skill development")
h("Explicit requirements", 2)
p(
    "A saved job contains title, company, description, optional experience and qualification, and related JobRequirement records. Users select catalog skills and mark each as essential or preferred. If requirements are omitted, the backend identifies vocabulary skills in the description and defaults them to essential. The interface asks the user to review those requirements before matching."
)
h("Weighted alignment", 2)
p(
    "Each essential requirement carries two skill points and each preferred requirement carries one. A direct skill mention earns the full weight. An explicitly configured related skill earns half, appears in a separate partial category and does not prove equivalence. A missing skill earns zero. Skill alignment equals earned points divided by possible points, multiplied by 100."
)
p(
    "The experience component uses the smaller of documented years divided by requested years and one. A request of zero years earns full experience credit. Missing explicit years earn zero only when experience is actually requested. Qualification uses an exact phrase, ignoring case and repeated whitespace, inside the detected education section. Equivalent qualifications require manual review."
)
p(
    "The final percentage is the weighted mean of active components: skills 70, experience 20 and qualification 10. Criteria that the job does not request are omitted and the remaining weights are renormalized. Match reports retain the job text and component evidence used at that time, so a later job edit does not silently rewrite an earlier result."
)
h("Worked example", 2)
p(
    "If Python and Docker are equally essential and only Python is documented, the skill component earns 2 out of 4 points, or 50%. With no experience or qualification requirement, skills are the only active component and the final result is 50%. A backend test verifies this exact case and the persisted Docker gap."
)
h("Roadmaps and career roles", 2)
p(
    "Missing and partial requirements become a roadmap ordered by importance. Each step supplies an action, a portfolio milestone and resources from the skill catalog. Career roles rank by explicit catalog overlap and omit zero-overlap roles. The system does not infer seniority, promise learning durations or describe coverage as readiness."
)

page("Optional AI integration")
p(
    "Core analysis is deterministic and always labeled rule-based. The optional provider path runs only after the user selects AI learning advice. It reads base URL, model and credentials from server environment variables. The server enforces HTTPS and sends only role title, matched skills and missing skills. It does not send contact details or the full resume in this implementation."
)
p(
    "The request asks for structured JSON containing one to eight short recommendation strings. Pydantic rejects unknown fields, incorrect types and missing content. The service additionally limits response and string sizes, uses connection/read timeouts and refuses redirects. Provider output is stored only as separate learning advice and cannot replace extracted facts, quality components or numerical match scores."
)
p(
    "If credentials are absent, a request times out, an HTTP error occurs, rate limiting applies or validation fails, the system retains the deterministic result and shows a fallback status. Executed tests mock successful advice, invalid schemas, timeout and HTTP failure. No live external provider call has been verified without user credentials."
)
h("Why this distinction matters", 2)
p(
    "A generated paragraph can sound confident without being supported by a resume. Separating advice from evidence allows the user to review suggestions while keeping reproducible calculations. It also makes the academic demonstration honest: the application can explain which techniques are rules, which are NLP vocabulary matching and which optional content came from a generative provider."
)

page("Security and administration")
h("Account boundaries", 2)
p(
    "Django hashes passwords and validates password strength at registration. Login returns an opaque token that expires after 24 hours. A new login replaces the old token and logout revokes it. React keeps the current token in sessionStorage. Authentication and authorization happen again on the server regardless of the route guard in the browser."
)
p(
    "Every user-owned query filters by request.user. Requests for another account’s resume, job, analysis or download return 404. Regular users cannot set staff status through their profile and cannot read system statistics. Django administration uses a separate session login and assigned model permissions."
)
h("Files and data handling", 2)
p(
    "Random storage filenames and a private media directory avoid a public file listing. Download endpoints stream only the authorized owner’s file and set no-store. Upload limits reduce oversized-document and archive-expansion risks. Secrets and runtime files are excluded from Git. The application user has scoped development database permissions rather than unrestricted root access."
)
h("Staff features", 2)
p(
    "The staff page displays current system counts and activity types. Django admin manages users, job categories, skills, aliases, related skills, career roles and learning resources. Catalog edits affect subsequent analyses; saved numerical reports retain their earlier snapshot. Administrators should maintain related-skill definitions carefully because partial credit expresses a deliberate domain rule."
)
h("Production boundary", 2)
p(
    "The tested environment is local and loopback-bound. Public deployment requires HTTPS, production WSGI/static hosting, explicit hosts and origins, private file backups, persistent throttling and an appropriate retention policy. Development settings and sample workspace access should not be exposed publicly."
)

page("Implementation and request cycle")
table(
    ["Source area", "Responsibility"],
    [
        [
            "backend/core/models.py",
            "Tables, relationships, uniqueness and private-file lifecycle",
        ],
        [
            "backend/core/serializers.py",
            "Field validation, request shape and JSON serialization",
        ],
        [
            "backend/core/views.py",
            "Authentication, ownership filtering and HTTP actions",
        ],
        [
            "backend/core/services/parsing.py",
            "File extraction, headings, contacts, vocabulary skills and quality",
        ],
        [
            "backend/core/services/analysis.py",
            "Weighted comparison, gaps, role ranking and history",
        ],
        [
            "backend/core/services/provider.py",
            "HTTPS provider calls, schema checks and fallback",
        ],
        [
            "frontend/src/api.js and auth.jsx",
            "Authenticated HTTP, session restoration and error handling",
        ],
        ["frontend/src/pages", "Interactive module screens and report rendering"],
        [
            "frontend/src/components",
            "Reusable layout, fields, dialogs, rings and notifications",
        ],
    ],
    [2.9, 3.45],
)
h("Beginner explanation", 2)
p(
    "When Analyze match is selected, React sends two record IDs and the token. Django identifies the user and retrieves only that user’s resume and job. The analysis service compares saved evidence with requirements, then saves the match, skill gap and history in one transaction. The serializer converts the result into JSON. React uses that JSON to display the percentage, source evidence and roadmap. MySQL persists the report so a reload or later login can retrieve it."
)
p(
    "Migrations are the canonical schema history. The SQL export is an inspection and academic deliverable, not a replacement for applying migrations to a fresh environment. The catalog seed installs reference vocabulary and resources without creating hidden user activity."
)

page("Testing and verification")
p(
    "Validation uses an actual MySQL database. Django creates and removes a separate test database rather than replacing the storage engine with SQLite. Frontend and browser tests target observable behavior, and the Postman collection provides an independent HTTP demonstration. Exact commands and executed results are retained in docs/TEST_RESULTS.md."
)
table(
    ["Verification", "Executed scope", "Result"],
    [
        [
            "Django tests",
            "36 checks of auth, parsing, permissions, storage, formulas, constraints and provider fallback",
            "Passed on MySQL",
        ],
        [
            "React tests",
            "8 checks of file validation, score accessibility, roadmap resources and API error display",
            "Passed",
        ],
        [
            "Playwright",
            "4 browser workflows covering real account lifecycle, every main module and 390px mobile fit",
            "Passed",
        ],
        [
            "OpenAPI validation",
            "Schema generation with --validate and --fail-on-warn",
            "Passed",
        ],
        [
            "Newman / Postman",
            "20 ordered API requests with status assertions and token lifecycle",
            "Passed",
        ],
        [
            "Production frontend build",
            "Vite asset generation and split chart/vendor bundles",
            "Passed",
        ],
    ],
    [1.25, 4.15, 0.95],
)
h("Representative cases", 2)
for text in [
    "A different user cannot read or delete an uploaded resume or download its original.",
    "An invalid extension, spoofed PDF, oversized file, unreadable scan and encrypted PDF receive validation errors.",
    "Quality component points add up to the stored quality score.",
    "A missing Docker skill produces the expected 50% alignment and a saved gap roadmap.",
    "A job edit preserves the original match snapshot. Source deletion removes dependent records.",
    "A new account has no hidden resume or match data. Browser refresh and sign-in recover persisted records.",
]:
    p(text, "List Bullet")
p(
    "The local tests do not measure production load, prove absence of every vulnerability or evaluate the quality of a live LLM response. These limits are reported rather than treated as completed verification."
)

page("User interface evidence")
p(
    "The following screens were captured from the running React application against real Django APIs and MySQL records. Candidate details, resumes and companies in the sample workspace are explicitly synthetic. Full-resolution originals are supplied in docs/screenshots. Some figures show the upper viewport for readable document placement."
)
for filename, title, explain in [
    (
        "01-sign-in.png",
        "Authentication",
        "Registration and sign-in use the Django API. The separate sample action creates a labeled account.",
    ),
    (
        "02-dashboard.png",
        "Dashboard overview",
        "Counts, scores and chart series originate from the authenticated account’s database records.",
    ),
    (
        "03-resumes.png",
        "Resume management",
        "Stored originals have download, analysis and delete actions.",
    ),
    (
        "04-resume-analysis.png",
        "Evidence and quality analysis",
        "The report exposes detected contact details and each component of the score.",
    ),
    (
        "05-job-descriptions.png",
        "Job description management",
        "Saved requirements support editing and a comparison action.",
    ),
    (
        "06-job-match.png",
        "Job match report",
        "The score, matched evidence, partial matches and missing requirements remain inspectable.",
    ),
    (
        "07-skill-gaps.png",
        "Skill development roadmap",
        "Priority and category accompany each gap and portfolio milestone.",
    ),
    (
        "08-career-pathways.png",
        "Career pathways",
        "Catalog overlap ranks roles and explains the skills behind each suggestion.",
    ),
    (
        "09-history.png",
        "Stored analysis history",
        "A user can reopen reports through their recorded activity.",
    ),
    (
        "10-profile.png",
        "Profile management",
        "Profile updates persist through the authenticated API.",
    ),
    (
        "13-administration.png",
        "Staff administration",
        "A separately authenticated administrator can inspect system statistics and open Django admin.",
    ),
]:
    page(title)
    p(explain)
    image(
        ROOT / "docs/screenshots" / filename,
        "Application screen  " + title,
        max_h=6.5,
        crop=True,
    )
page("Responsive mobile interface")
p(
    "Browser checks used a 390 by 844 pixel viewport. Navigation opens as an overlay and closes after selecting a module. Both the dashboard and roadmap passed horizontal overflow checks. Full-length mobile screenshots are supplied separately."
)
source = ROOT / "docs/screenshots/11-mobile-dashboard.png"
im = Image.open(source)
im.crop((0, 0, im.width, min(1000, im.height))).save(QA / "mobile-top.png")
image(
    QA / "mobile-top.png", "Application screen  Mobile dashboard", max_w=2.8, max_h=6.3
)

page("Deployment and maintenance")
h("Local setup", 2)
p(
    "The README provides commands for Python 3.12, uv, npm and MySQL. scripts/create_env.py creates random local secrets once. Migrations create tables and seed_catalog installs skills, roles and learning resources. The optional private database helper binds MySQL to loopback. scripts/dev.py starts the backend and frontend with persistent local logs."
)
h("Administration", 2)
p(
    "Create a staff account with Django’s createsuperuser command, or use the supplied local demonstration administrator helper. Credentials from the helper remain in a permission-restricted ignored runtime file. React signs in using email while Django admin signs in using username. Regular users have no catalog write endpoint."
)
h("Maintenance", 2)
p(
    "Back up MySQL and the private media directory together. Keep the requirements lock and npm lockfile with the source. Apply schema changes through migrations. Review catalog aliases and related skills before changing scoring interpretation. Use the executed tests after changes to extraction, formulas or permissions. Old reports retain their evidence snapshots."
)
h("Deliverable map", 2)
p(
    "Source code is organized under backend and frontend. SQL scripts, API documentation, the Postman collection, diagrams, synthetic sample files, screenshots, the 50-question viva guide and demonstration script are under docs. This editable report and the academic presentation reference are under outputs. DEVELOPMENT_PROGRESS.md records verified milestones."
)

page("Limitations and future work")
p(
    "The extraction engine depends on selectable text and recognizable headings. It does not provide OCR, verify the truth of candidate claims, infer complete employment timelines or recognize every possible skill. The vocabulary and role catalog require maintenance. Exact qualification matching can miss equivalent degrees. Related skills receive deliberate partial credit but are not equivalent qualifications."
)
p(
    "Quality weights are transparent design choices, not a validated hiring model. Counting sections or vocabulary breadth can reward structure without proving substance. Career coverage does not establish seniority or market demand. Users should inspect the evidence and review equivalent qualifications and experience manually."
)
p(
    "Live provider behavior remains unverified until credentials are supplied. Network, latency and operational costs depend on the configured provider. Public deployment, sustained load tests, OCR and multilingual extraction are future work rather than hidden completed features."
)
h("Future development", 2)
p(
    "Potential improvements include opt-in OCR, user-corrected evidence with provenance, structured work-date parsing, multilingual skill catalogs, curated qualification equivalence, more varied career taxonomies and evaluated semantic matching. Each change should retain an explanation and add meaningful tests before affecting user scores."
)
h("Conclusion", 2)
p(
    "CareerLens implements the complete local path from authenticated resume upload to evidence review, saved job comparison and a skill development plan. MySQL-backed records, private file access and transparent formulas make the application demonstrable and understandable for an academic viva. The optional generative path is contained to advice so that the core system remains useful and reproducible without credentials."
)

page("References and supporting materials")
for name, url in [
    ("Django documentation", "https://docs.djangoproject.com/en/5.2/"),
    (
        "Django REST Framework authentication",
        "https://www.django-rest-framework.org/api-guide/authentication/",
    ),
    ("Vite documentation", "https://vite.dev/guide/"),
    (
        "MySQL generic binary installation",
        "https://dev.mysql.com/doc/refman/8.4/en/binary-installation.html",
    ),
    ("spaCy rule based matching", "https://spacy.io/usage/rule-based-matching"),
    ("PyMuPDF documentation", "https://pymupdf.readthedocs.io/"),
    ("python-docx documentation", "https://python-docx.readthedocs.io/"),
    ("React documentation", "https://react.dev/learn"),
    ("Recharts documentation", "https://recharts.org/"),
    ("Pydantic documentation", "https://docs.pydantic.dev/"),
]:
    p(name + "\n" + url)
p(
    "Implementation-specific evidence is the delivered source, migrations, tests, API schema and captured screenshots. Learning links are catalog resources and are not presented as individually quality-audited courses. The separate viva guide contains 50 project-specific questions with answers, and the demonstration script supplies a full examination walkthrough."
)

doc.core_properties.title = "CareerLens project report"
doc.core_properties.subject = "MCA Semester 3 major academic project"
doc.core_properties.author = "CareerLens project"
doc.save(OUT / "CareerLens-Project-Report.docx")
print("Created outputs/CareerLens-Project-Report.docx")
