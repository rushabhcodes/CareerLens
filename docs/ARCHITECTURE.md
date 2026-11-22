# CareerLens requirements and architecture

CareerLens helps a student or job seeker understand the evidence in a resume, compare it with a saved job, and choose a learning plan. A match score measures documented alignment; it does not estimate a hiring probability. The local engine is deterministic. An optional LLM may enrich advice after explicit user action, without replacing extracted facts or scores.

## Requirements and acceptance

1. Register, log in, revoke a token on logout, edit a profile and isolate all user-owned records.
2. Upload PDF or DOCX up to 5 MiB. Validate content as well as extension, extract text, reject scans with an actionable OCR message, retain originals in private storage and authorize downloads.
3. Extract contact details, section evidence and vocabulary-based skills with spaCy phrase matching. Display unknown fields honestly. Explain every quality component and show the extracted text.
4. Create, edit, search and delete jobs with weighted essential/preferred requirements, experience and qualification text.
5. Persist a versioned match with full, related and missing skills, scored components, qualification evidence and caveats. Persist its skill gaps and learning roadmap in the same transaction.
6. Recommend roles from an administrator-managed catalog. Persist role recommendations and learning resources.
7. Validate optional provider output against a strict schema, allow only configured HTTPS endpoints, enforce a timeout and fall back on invalid responses, rate limits or network errors. Credentials stay on the server.
8. Derive dashboard metrics, trends, top skills and history from the logged-in user's MySQL records. Empty accounts show empty states.
9. Expose staff-only operational statistics and Django admin catalog management.
10. Provide reproducible tests, API/Postman documentation, diagrams, a report, slides and a demonstration guide.

## System architecture

```mermaid
flowchart LR
  U[Job seeker] --> R[React and Vite browser app]
  R -->|Authenticated JSON and multipart| A[Django REST API]
  A --> S[Service layer]
  S --> P[PyMuPDF and python docx]
  S --> N[spaCy vocabulary matcher and scoring]
  S --> L[Optional HTTPS LLM provider]
  A --> D[(MySQL)]
  A --> F[Private resume filesystem]
  Admin[Staff administrator] --> DA[Django admin]
  DA --> D
```

## Database ER diagram

```mermaid
erDiagram
  USER ||--|| PROFILE : has
  USER ||--o{ RESUME : owns
  RESUME ||--|| EXTRACTED_INFORMATION : contains
  RESUME ||--o{ RESUME_SKILL : evidences
  SKILL ||--o{ RESUME_SKILL : classifies
  USER ||--o{ JOB_DESCRIPTION : owns
  JOB_DESCRIPTION ||--o{ JOB_REQUIREMENT : requires
  SKILL ||--o{ JOB_REQUIREMENT : references
  RESUME ||--o{ JOB_MATCH_ANALYSIS : compared
  JOB_DESCRIPTION ||--o{ JOB_MATCH_ANALYSIS : targets
  JOB_MATCH_ANALYSIS ||--|| SKILL_GAP_ANALYSIS : produces
  USER ||--o{ ANALYSIS_HISTORY : records
  RESUME ||--o{ CAREER_RECOMMENDATION : receives
  CAREER_ROLE ||--o{ CAREER_RECOMMENDATION : suggests
  CAREER_ROLE }o--o{ SKILL : requires
  SKILL ||--o{ LEARNING_RESOURCE : teaches
  JOB_CATEGORY ||--o{ CAREER_ROLE : groups
```

Foreign keys enforce ownership chains and cascades. ResumeSkill and JobRequirement have unique pairs. Scores have 0–100 validators. JSON fields retain immutable scoring evidence and provider provenance; reusable skills, requirements and resources use relational tables. User/time indexes support recent-history queries. Deleting a source deletes its dependent analyses; original files are also removed.

## UML use cases

```mermaid
flowchart LR
  User((Job seeker)) --> Auth([Register and authenticate])
  User --> Upload([Upload or delete resume])
  User --> Review([Review extraction and quality])
  User --> Jobs([Manage job descriptions])
  User --> Match([Compare resume and job])
  Match --> Gaps([Inspect skill gaps and roadmap])
  User --> Career([Request career recommendations])
  User --> History([View dashboard and history])
  Staff((Administrator)) --> Stats([View system statistics])
  Staff --> Catalog([Manage skills roles and resources])
  Staff --> Auth
```

## Data flow

```mermaid
flowchart TD
  File[Resume file] --> V[Validate extension signature archive and size]
  V --> E[Extract text and section evidence]
  E --> C[Identify catalog skills]
  C --> Q[Calculate quality components]
  Q --> DB[(User records in MySQL)]
  JD[Job description and requirements] --> DB
  DB --> M[Weighted skill experience and qualification comparison]
  M --> G[Persist match and skill gaps]
  G --> DB
  DB --> Rec[Rank career roles and create roadmap]
  Rec --> Optional[Optional validated LLM advice]
  Optional --> DB
  DB --> UI[Reports charts and history]
```

## Implementation milestones

Build storage and service contracts first, then wire all pages to those contracts. Verify parsing and access control on MySQL before browser demonstrations. Use synthetic fixtures only in tests and an explicitly labeled optional demo seed, never as hidden dashboard data. Finish documentation from actual test output and captured application screens.

## Project structure

`backend/config` contains settings and routing. `backend/core` contains models, serializers, permissions, API views and tests. `backend/core/services` owns parsing, matching, career ranking and provider validation. `frontend/src` contains the API client, authentication provider, reusable UI and routed pages. `scripts` contains setup, database and demonstration helpers. `docs` and `outputs` hold academic deliverables.
