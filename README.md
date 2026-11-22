# CareerLens

An explainable resume analysis and career planning application for an MCA Semester 3 major project. Built with **React + Vite (JavaScript), Tailwind CSS, Django REST Framework, MySQL, PyMuPDF, python-docx, spaCy and Recharts**.

CareerLens runs locally without an AI API key. The default engine is explicitly labeled **rule-based**. Optional OpenAI-compatible provider enrichment produces learning advice only; extracted candidate facts and numerical scores remain deterministic.

## Open the application

During development the application runs at **http://127.0.0.1:5173/** and the API at **http://127.0.0.1:8000/api/**. Select **Explore sample workspace** to create a separate MySQL-backed workspace containing clearly labeled synthetic resumes and jobs, or create your own empty account.

## Requirements

- Python 3.12, `uv`, Node.js 22.12+ and npm.
- MySQL 8.0.11+ (8.4 recommended), accessible on loopback port 3307 by default.
- Internet access for the first dependency installation. No spaCy model download is required.
- This workstation also has a project-private MySQL 8.4.6 under `.runtime/`. It does not modify system services.

## Set up from scratch

### Option A: existing MySQL or Docker

```bash
cd /path/to/CareerLens
uv venv --python 3.12 .venv
uv pip sync --python .venv/bin/python backend/requirements.lock
.venv/bin/python scripts/create_env.py
```

`create_env.py` creates random local secrets without overwriting an existing `.env`. For an existing MySQL installation, edit `.env` to match its connection details, then adapt and execute [database-init.sql](docs/database-init.sql). Ensure the application account can create/drop only `test_careerlens` if you want to run Django tests.

If Docker Compose is installed:

```bash
docker compose up -d db
```

The Compose file provisions the main application database. To run Django's tests with Compose, grant the application user privileges on `test_careerlens.*` using a root connection. The private local database helper grants this scoped development permission automatically.

Then initialize the application:

```bash
.venv/bin/python backend/manage.py migrate --noinput
.venv/bin/python backend/manage.py seed_catalog
npm --prefix frontend ci
.venv/bin/python scripts/dev.py start
```

### Option B: private MySQL on this Arch Linux workstation

```bash
bash scripts/bootstrap.sh --local-mysql
.venv/bin/python scripts/dev.py start
```

The installer downloads the official Linux x86_64 generic MySQL binary into `.runtime/mysql`, extracts libaio locally if needed, initializes a private data directory and binds only to `127.0.0.1`. It requires `curl`, `tar`, `rg`, `pacman` and `bsdtar` on Arch. For other systems, use Option A rather than the Arch-specific libaio fallback. The pinned local binary is for reproducible demonstration; use a maintained MySQL release for deployment.

### Subsequent starts and stops

```bash
.venv/bin/python scripts/local_mysql.py start   # if using the private database
.venv/bin/python scripts/dev.py start
.venv/bin/python scripts/dev.py stop
.venv/bin/python scripts/local_mysql.py stop    # leaves database files intact
```

Server logs are `.runtime/backend.log`, `.runtime/frontend.log` and `.runtime/mysql.log`. The dev helper starts only missing servers. The stop helper stops only processes it recorded in this checkout. For manual terminals use `cd backend && ../.venv/bin/python manage.py runserver 127.0.0.1:8000` and `cd frontend && npm run dev`.

## Administration

```bash
.venv/bin/python backend/manage.py createsuperuser
```

Use an email address along with the username. Sign in to the React app with the **email** and password. The staff navigation shows application statistics. Open **Django admin** from that page, or visit http://127.0.0.1:8000/admin/ and sign in with the **username** and password. Catalog management uses Django's staff/model permissions. Regular users cannot access operational statistics or catalog management.

For the existing local demonstration administrator, read `.runtime/admin-credentials.txt` privately. To create one on a new checkout, run `.venv/bin/python scripts/create_local_admin.py`; it generates a random password once and stores it in that ignored, permission-restricted file. It does not change an existing administrator's credentials.

## Optional AI provider

Set all three values in `.env`, then restart Django:

```dotenv
LLM_BASE_URL=https://YOUR_PROVIDER_HOST/v1
LLM_MODEL=YOUR_MODEL_NAME
LLM_API_KEY=YOUR_PRIVATE_KEY
```

The provider must implement the OpenAI-compatible `/chat/completions` contract and JSON response mode. Do not put keys in frontend variables or source files. On Career pathways, explicitly select **Include optional AI learning advice** before generating recommendations. Only role and skill names are sent. Timeouts, HTTP errors including rate limits, redirects and invalid schemas produce a labeled local fallback. **Live provider calls were not verified without credentials.**

## How scoring works

- **Resume quality:** contact 20 + section completeness 30 + catalog skill breadth 25 + contribution evidence 15 + text length 10.
- **Job alignment:** essential skills = 2 points, preferred = 1; explicit mention = full credit, configured related skill = half, absent = zero. Components use skills weight 70, explicit experience weight 20, exact qualification phrase weight 10. Unrequested components are omitted and active weights are renormalized.
- **Role coverage:** matched explicit catalog skills / role catalog skills × 100.

The **How scoring works** page and each report explain the formulas. None of these scores represents a hiring probability. Experience years remain unknown unless the text explicitly states them. A name is a first-line heuristic, and a skill mention does not verify proficiency. Scanned PDFs need OCR, which is not configured.

## Verification

```bash
.venv/bin/python backend/manage.py test core --verbosity 2 --noinput
npm --prefix frontend test
npm --prefix frontend run build
cd frontend
npx playwright install chromium --only-shell
npm run test:e2e
```

Start Django and Vite before browser tests. The repository includes PDF and DOCX synthetic fixtures at `docs/sample-resume.*`. E2E tests create test-only accounts and exercise real APIs/MySQL. If you already have a compatible Chromium executable, set `PLAYWRIGHT_EXECUTABLE=/absolute/path/to/chrome-headless-shell`. Executed results and limits are in [TEST_RESULTS.md](docs/TEST_RESULTS.md).

## Academic materials

- [Architecture, ER, use cases and data flow](docs/ARCHITECTURE.md)
- [API documentation](docs/API.md) and [Postman collection](docs/CareerLens.postman_collection.json)
- [Schema SQL without user records](docs/database-schema.sql)
- [50 viva questions and answers](docs/VIVA.md)
- [Step-by-step demonstration](docs/DEMONSTRATION.md)
- [Development progress](DEVELOPMENT_PROGRESS.md)
- `docs/screenshots/`: captured desktop and mobile module screens using synthetic data.
- `outputs/`: final academic report and presentation reference.

## Code map for beginners

`backend/core/models.py` defines tables and relationships. `serializers.py` validates requests and shapes JSON. `views.py` authenticates the caller and selects only their records. Services do the actual extraction and scoring. `frontend/src/api.js` adds the token to API requests; `auth.jsx` stores the current account; `pages/` contains the screens. The API is the only layer that talks to MySQL. A React route guard improves navigation, while backend permissions enforce security.

## Deployment boundary

This repository is a working local academic application, not a verified public deployment. Before public use, set `DJANGO_DEBUG=false`, disable sample workspaces, configure hostnames and HTTPS, enable secure redirects behind a correctly configured reverse proxy, use a production WSGI server, back up MySQL and private files, configure persistent throttling, and review data retention. Build the frontend with `npm --prefix frontend run build` and serve `frontend/dist` with SPA fallback. Proxy `/api`, `/admin` and `/static` to the proper backend/static services. Configure `VITE_API_BASE` and `VITE_ADMIN_URL` at build time only when paths differ. Never serve `backend/private_media` as public static files.
