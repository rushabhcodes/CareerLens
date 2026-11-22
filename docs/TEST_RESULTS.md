# Executed verification

Executed locally on 22 November 2026 (Asia/Kolkata) against **MySQL Community Server 8.4.6**, Python 3.12, Django 5.2, React 19 and Vite 7. No SQLite substitute was used for backend validation.

| Check                                   | Executed result                                                                                                                    |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Django suite                            | **36 passed** on a separate `test_careerlens` MySQL database                                                                       |
| React / Vitest suite                    | **8 passed**                                                                                                                       |
| Playwright browser suite                | **4 passed**, including the optional local staff flow                                                                              |
| Postman collection via Newman           | **20 requests, 20 assertions, 0 failures**                                                                                         |
| Production frontend build               | Passed; chart and vendor code split into separate bundles                                                                          |
| OpenAPI schema                          | Passed `--validate --fail-on-warn` with no warnings                                                                                |
| Django model migration check            | No ungenerated changes                                                                                                             |
| npm dependency audit                    | 0 vulnerabilities reported in the installed dependency set                                                                         |
| Bootstrap rerun                         | Passed with existing secrets and database records preserved                                                                        |
| Private MySQL stop/start                | Passed; database records remained available                                                                                        |
| Application dev helper start/stop/start | Passed; backend and frontend responded after restart                                                                               |
| Academic DOCX                           | Rendered and visually reviewed                                                                                                     |
| Academic PowerPoint                     | 18 slides rendered and reviewed; package, geometry, fonts and first-party reimport checks passed; actual screenshot media verified |

## Backend coverage

Tests cover registration and hashed passwords, weak/duplicate registrations, correct and incorrect login, token revocation and expiry, profile updates, staff escalation prevention, authentication, ownership of lists and individual records, owner-only downloads, PDF/DOCX extraction including Word tables, invalid extensions, spoofed/damaged content, oversize uploads, unreadable/encrypted PDFs, unknown candidate facts, token-boundary skill detection, quality component arithmetic, job CRUD, automatic requirement detection, invalid and duplicate requirements, weighted matching, partial skill credit, explicit/unknown experience, qualification credit, immutable snapshots, gap persistence, cascade deletion, original-file cleanup, career persistence, dashboard isolation, pagination, search, invalid filter IDs, database uniqueness, repeatable catalog seeding and provider validation/fallback.

## Browser coverage

1. Real-account workflow: create account, verify empty dashboard, upload a PDF, inspect extraction, download the report, create/edit a job, match it, inspect gaps, generate careers, view history, save a profile goal, refresh, sign out/in and delete the test resume.
2. Sample workspace: navigate every main module, verify loaded results, check for browser exceptions and horizontal overflow, capture desktop screenshots at 1440 × 1000.
3. Mobile: navigate the dashboard and roadmap at 390 × 844, verify the menu and absence of horizontal overflow, capture mobile screens.
4. Local staff account: read application statistics, sign into Django admin and open the managed skills catalog. This test runs when `.runtime/admin-credentials.txt` exists and otherwise explicitly skips. It was executed and passed on this workstation.

## Postman execution

The supplied collection creates a unique test account, captures its token, exercises profile, skill catalog, multipart upload, job CRUD, matching, career generation, dashboard and history, verifies staff rejection, deletes its test records, logs out and verifies that the revoked token returns 401. Newman executed the collection directly against the running Django API.

```bash
cd frontend
npm exec --yes --package newman -- newman run ../docs/CareerLens.postman_collection.json --working-dir ../docs
```

The browser tests use the real API and database. Test-only sample accounts remain in the local demonstration database; they are labeled synthetic or test accounts. Complete logs and runner JSON are in ignored `.runtime/` files because API runner output can contain ephemeral tokens. Screenshots under `docs/screenshots/` contain synthetic candidate data.

## Fixes found during verification

- Saved career cards now display the strongest coverage first.
- Match history follows its match foreign key, so deleting a job does not leave a broken history link.
- Invalid resume filter IDs return validation errors rather than server errors.
- The catalog seed explicitly looks up related-skill pairs, avoiding duplicate `INSERT IGNORE` warnings on repeat MySQL bootstrap runs. A regression test runs the seed twice.
- Mobile off-canvas navigation is hidden from focus and accessibility navigation while closed.
- Screenshot capture waits for loaded records, and the PowerPoint includes verified non-empty screenshot bytes.

## Verification limits

No live LLM-provider call was executed because credentials were not supplied. Provider success, bad schemas, timeouts and rate limits were tested with mocks. OCR is intentionally not configured. Scoring heuristics have not been validated against hiring outcomes. The initial local checks did not cover public deployment; functional hosted checks are recorded below. Production load, multi-browser coverage beyond Chromium and native Microsoft PowerPoint execution were not tested. The Docker alternative is supplied but was not executed on this workstation, where Docker is not installed.

## Hosted demo verification — 23 November 2026

The application was deployed to **https://careerlens.rushabh.dev/** using Vercel frontend/backend Services and Neon PostgreSQL. These checks used the real hosted API and database, with fictional candidate information:

| Check                                 | Executed result                                                                                                                                                                                                                         |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Updated backend suite on MySQL        | **39 passed**, including persistent serverless originals, owner-only downloads, deletion, hosted upload limits and sample workspaces with debug disabled                                                                                |
| Same backend suite on Neon PostgreSQL | **39 passed** on the separate `test_careerlens` database; the application database was not used as the test database                                                                                                                    |
| React suite                           | **8 passed**                                                                                                                                                                                                                            |
| Frontend production build             | Passed; malformed mobile CSS was corrected and the build's CSS warnings were eliminated                                                                                                                                                 |
| Hosted configuration / migrations     | Django checks passed and no pending model migration changes                                                                                                                                                                             |
| Anonymous custom-domain access        | HTTPS frontend, one-click sample workspace, Django login page and admin static CSS responded without Vercel sign-in                                                                                                                     |
| Hosted workspace API                  | Dashboard, resumes, jobs, matches, careers and history returned authenticated JSON successfully                                                                                                                                         |
| New-account workflow                  | Registration started empty; a PDF uploaded, extracted and persisted; a later request downloaded its original                                                                                                                            |
| Ownership and staff access            | Another account could not download the original; regular users received 403 from staff statistics                                                                                                                                       |
| Deletion and logout                   | Deletion removed the resume; its original became unavailable; logout revoked the token and subsequent account access returned 401                                                                                                       |
| Recorded browser walkthrough          | Completed PDF and DOCX upload, private original/report downloads, evidence expansion, job creation/editing, matching, gaps, optional-advice fallback, career plans, history/search, persisted profile updates, methodology and deletion |
| Staff walkthrough                     | Private authenticated staff session opened statistics, Django administration and the skill catalog without filming credentials                                                                                                          |
| Mobile walkthrough                    | Dashboard, navigation and skill roadmap completed at 390 × 844, with no horizontal overflow                                                                                                                                             |

The walkthrough uses genuine browser interaction, with no mocked network responses. No browser exceptions or HTTP 5xx responses were observed by the recorder. The MP4 and captions are included under `docs/demo/`.

The hosted demo uses a 4 MiB upload limit and private PostgreSQL-backed originals; local MySQL installations retain the 5 MiB default and private filesystem originals. Optional provider credentials remain unset, so the recording demonstrates the labeled local fallback. Hosted functional checks do not establish production capacity or hiring-score validity.
