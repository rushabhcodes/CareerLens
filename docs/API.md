# CareerLens API

Base development URL: `http://127.0.0.1:8000/api/`. JSON requests use `Content-Type: application/json`. Every endpoint except registration, login and optional sample creation requires `Authorization: Token <token>`. Tokens expire 24 hours after issue; a new login revokes the previous token. Logout revokes the current token.

## Endpoints

| Method | Path | Purpose | Success |
|---|---|---|---|
| POST | `/auth/register/` | first_name, last_name (optional), email, password | 201, token and user |
| POST | `/auth/login/` | email, password | 200, token and user |
| POST | `/auth/logout/` | Revoke current token | 200 |
| GET / PATCH | `/auth/me/` | Read/update own name, headline, location, career_goal | 200 |
| POST | `/auth/demo/` | Create isolated synthetic sample workspace in development | 201 |
| GET / POST | `/resumes/` | List records / upload multipart file and optional title | 200 / 201 |
| GET / DELETE | `/resumes/{id}/` | Read report / remove file and dependent records | 200 / 204 |
| GET | `/resumes/{id}/download/` | Authorized original file download | 200, binary attachment |
| GET | `/resumes/{id}/report/` | Download extracted information and quality report | 200, JSON attachment |
| POST | `/resumes/{id}/recommend/` | Generate and store careers; `{ "use_ai": false }` by default | 201, array |
| GET / POST | `/jobs/` | List / create saved jobs | 200 / 201 |
| GET / PATCH / PUT / DELETE | `/jobs/{id}/` | Read / update / replace / delete a job | 200 / 204 |
| GET / POST | `/matches/` | List / compare `{ "resume": 1, "job": 1 }` | 200 / 201 |
| GET | `/matches/{id}/` | Saved match, gaps and roadmap | 200 |
| GET | `/careers/` | Stored career recommendations; optional `?resume=id` | 200 |
| GET | `/careers/{id}/` | One owned recommendation | 200 |
| GET | `/history/` | Own analysis activity | 200 |
| GET | `/history/{id}/` | One owned activity | 200 |
| GET | `/dashboard/` | Database aggregates, chart data, recent results | 200 |
| GET | `/skills/` | Selectable skill catalog | 200, array |
| GET | `/system/` | System counts and activity, staff only | 200 |
| GET | `/schema/` and `/docs/` | OpenAPI and interactive API reference, authenticated | 200 |

The administration website lives at `/admin/` outside the API and uses a separate Django session login.

## Job payload

```json
{
  "title": "Python backend developer",
  "company": "Your target company",
  "description": "Build reliable Python services with Django, Docker and automated testing.",
  "experience_years": 2,
  "qualification": "MCA",
  "requirements": [
    {"skill": 1, "importance": "essential"},
    {"skill": 18, "importance": "preferred"}
  ]
}
```

Read `/skills/` to obtain actual IDs; IDs above are illustrative. Omit `requirements` to detect catalog skills from the description. Detected requirements default to essential and should be reviewed before matching. A job needs at least one catalog requirement. Omit experience or use null when unspecified. Zero means no experience required. Qualification uses exact phrase matching inside the recognized education section. A PATCH omitting description and requirements retains existing requirements; changing description without supplying requirements redetects them.

## Lists and filtering

Paginated lists return `{ "count": 23, "next": "...page=2", "previous": null, "results": [...] }` with 20 records per page. Use `?page=2`. Search resumes, jobs, matches and history using `?search=term`. Resume ordering supports `created_at`, `quality_score`, `title`; jobs support `created_at`, `title`; matches support `created_at`, `score`. Prefix an ordering field with `-` for descending order. Matches and careers also accept `?resume=id`.

## Errors and authorization

Errors return `{ "error": { "message": "...", "fields": { "field": ["reason"] } } }`. Validation uses 400. Missing, invalid or expired authentication uses 401. Staff-only access uses 403. Access to another user's record returns 404. Rate limits use 429. A temporary database failure returns 503 without internal details. Deleted objects return 204 without a body. Unexpected programming errors are logged by Django rather than presented as validation failures.

PDF and DOCX uploads are limited to 5 MiB, PDF files to 30 pages, expanded DOCX content to 20 MiB, archive entries to 2,000 and extracted text to 150,000 characters. Extensions alone are insufficient; content must parse. Encrypted PDFs and unreadable scans return actionable validation errors.

## Score evidence

A match returns `result.matched`, `result.partial`, `result.missing`, weighted `components`, `job_snapshot`, `gaps` and `roadmap`. Original job text is copied into the result so editing a job does not rewrite old reports. The related `SkillGapAnalysis` record is created in the same transaction. Deleting a job removes dependent matches and their activity records. Deleting a resume also removes its private original and dependent reports.

Career advice uses `engine: rule-based-v1` or `llm-enriched-v1` and an explicit provider status. AI advice cannot replace the deterministic score or extracted data. Mock provider tests cover rate limits, timeouts and invalid schemas; a real provider requires user credentials.
