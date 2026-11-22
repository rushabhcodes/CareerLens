# CareerLens

An explainable resume analysis and career planning application for an MCA Semester 3 major project. Built with **React + Vite (JavaScript), Tailwind CSS, Django REST Framework, MySQL, PyMuPDF, python-docx, spaCy and Recharts**.

CareerLens runs locally without an AI API key. The default engine is explicitly labeled **rule-based**. Optional OpenAI-compatible provider enrichment produces learning advice only; extracted candidate facts and numerical scores remain deterministic.

## Run on your own device

The setup below provides commands for Linux, macOS and Windows PowerShell. MySQL runs in Docker; Python and Node.js run on your device. An existing MySQL installation can be used instead. Local execution was verified on Arch Linux; native Windows, macOS and the Docker alternative have not been executed here.

### 1. Install the prerequisites

| Tool | Requirement |
| --- | --- |
| [Git](https://git-scm.com/downloads) | To clone this repository |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | Installs Python 3.12 and the backend dependencies |
| [Node.js and npm](https://nodejs.org/en/download) | Node.js 22.12+ in the 22.x line, or Node.js 24.x |
| [Docker with Compose](https://docs.docker.com/compose/install/) | Docker Desktop on Windows/macOS, or Docker Engine with the Compose plugin on Linux; start Docker before continuing |

You need internet access for the initial dependency and database-image downloads. No AI subscription, API key or spaCy model download is required.

### 2. Clone and configure the project

Run these commands in a terminal (PowerShell on Windows):

```sh
git clone https://github.com/rushabhcodes/CareerLens.git
cd CareerLens
uv python install 3.12
uv venv --python 3.12 .venv
uv pip install --python .venv -r backend/requirements.lock
```

Activate the Python environment on **Linux/macOS**:

```sh
source .venv/bin/activate
```

Or on **Windows PowerShell**:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` in place of `python` in every command below. Activation is optional when you use that full executable path.

From the repository root, create your local configuration:

```sh
python scripts/create_env.py
```

This creates `.env` with random Django and MySQL passwords. An existing `.env` is preserved. Keep it private; Git ignores `.env`, database files, administrator credentials and uploaded resumes. Each person creates their own accounts and database locally.

### 3. Start MySQL

From the repository root:

```sh
docker compose up -d db
docker compose ps
```

Wait for the database status to show **healthy** before continuing. The first launch downloads MySQL 8.4 and creates the `careerlens` database and application user using your `.env`. Docker only runs the database, so you still need to start Django and React in step 5. Data persists in the `careerlens_mysql` Docker volume.

The default connection is `127.0.0.1:3307`. If that port is occupied, change `MYSQL_PORT` in `.env` to an unused port before starting Compose. Both Compose and Django read this setting.

**Using MySQL without Docker:** install MySQL 8.0.11 or newer (8.4 recommended), set the `MYSQL_*` values in `.env` to match it, then adapt and execute [database-init.sql](docs/database-init.sql) using a database administrator account. Replace its example password with `MYSQL_PASSWORD` from `.env`. Skip the Docker commands; the remaining steps are the same. Use Django migrations below to create the tables.

### 4. Initialize the application

In the terminal with the Python environment activated, from the repository root:

```sh
python backend/manage.py migrate --noinput
python backend/manage.py seed_catalog
npm --prefix frontend ci
```

Migrations create the application tables; the seed command adds the shared skill and career catalogs. Both commands can be run again on an existing installation.

### 5. Start Django and React

Keep **two terminals** open, both in the repository root.

**Terminal 1 — backend:** activate `.venv` as shown in step 2, then run:

```sh
python backend/manage.py runserver 127.0.0.1:8000
```

**Terminal 2 — frontend:**

```sh
npm --prefix frontend run dev
```

Open **[http://127.0.0.1:5173/](http://127.0.0.1:5173/)**. Select **Explore sample workspace** for clearly labeled synthetic resumes and jobs, or create an account for your own empty workspace. Try the included [sample PDF](docs/sample-resume.pdf) or [sample DOCX](docs/sample-resume.docx) when uploading a resume. The backend API is at [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/).

### Stop and restart

Press **Ctrl+C** in each server terminal. To stop the Docker database while keeping its data:

```sh
docker compose stop db
```

Next time, run `docker compose up -d db`, activate `.venv` in the backend terminal, and run the two commands in step 5. Dependency installation, secret generation and catalog initialization are only needed during setup or when the project changes.

### Optional Arch Linux helpers

On Arch Linux x86_64, you can use a private MySQL installation instead of Docker:

```sh
bash scripts/bootstrap.sh --local-mysql
.venv/bin/python scripts/dev.py start
```

The installer downloads the official Linux x86_64 MySQL binary into `.runtime/mysql`, extracts libaio locally if needed, initializes a private data directory and binds to `127.0.0.1`. It requires `uv`, Node.js/npm, `curl`, `tar`, `rg`, `pacman` and `bsdtar`. The pinned local binary is for reproducible demonstration; use a maintained MySQL release for deployment.

For later starts and stops:

```sh
.venv/bin/python scripts/local_mysql.py start
.venv/bin/python scripts/dev.py start
.venv/bin/python scripts/dev.py stop
.venv/bin/python scripts/local_mysql.py stop
```

These helpers are for Linux; use the manual server commands above on Windows/macOS. Logs are `.runtime/backend.log`, `.runtime/frontend.log` and `.runtime/mysql.log`. The dev helper starts only missing servers and stops only processes it recorded in this checkout.

### Troubleshooting

| Problem | What to check |
| --- | --- |
| `uv`, `node`, `npm` or `docker` is not found | Install the prerequisite and reopen your terminal so its PATH is refreshed. |
| Docker cannot connect to its daemon | Start Docker Desktop or the Docker Engine service. |
| MySQL connection refused during migrations | Wait for `docker compose ps` to show healthy; check `MYSQL_HOST` and `MYSQL_PORT` in `.env`. Inspect startup errors with `docker compose logs db`. |
| MySQL access denied | Verify the database user/password in `.env`. An existing Docker volume keeps its original credentials; editing `.env` does not reset database passwords. |
| `ModuleNotFoundError` | Activate this checkout's `.venv`, or use its Python executable directly; repeat the dependency-install command in step 2. |
| Frontend opens but API calls fail | Keep Django running on `127.0.0.1:8000`. Vite proxies API requests to that address. |
| Port 8000 or 5173 is already in use | Stop the previous server using that port. If Vite selects a different port, free 5173 and restart to match the supplied origin configuration. |
| A scanned PDF cannot be read | Use a PDF containing selectable text or a DOCX file; OCR is not configured. |

## Administration

With `.venv` activated, run:

```sh
python backend/manage.py createsuperuser
```

Use an email address along with the username. Sign in to the React app with the **email** and password. The staff navigation shows application statistics. Open **Django admin** from that page, or visit http://127.0.0.1:8000/admin/ and sign in with the **username** and password. Catalog management uses Django's staff/model permissions. Regular users cannot access operational statistics or catalog management.

Alternatively, run `python scripts/create_local_admin.py` to generate a local demonstration administrator. Read the credentials privately from `.runtime/admin-credentials.txt`. The helper generates a random password once and does not change an existing administrator's credentials. This file is ignored by Git.

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

Django's test runner creates and drops a separate `test_careerlens` database. With the default Docker setup, grant the application account access to that database first:

```sh
docker compose exec db mysql -u root -p
```

Enter `MYSQL_ROOT_PASSWORD` from `.env` at the password prompt, then run this SQL and `exit`:

```sql
GRANT ALL PRIVILEGES ON test_careerlens.* TO 'careerlens'@'%';
```

This SQL uses the default `MYSQL_USER=careerlens`; adapt it if you changed the username. The existing-MySQL initialization script and the private Linux database helper already include scoped test-database permissions.

Then activate `.venv` and run from the repository root:

```sh
python backend/manage.py test core --verbosity 2 --noinput
npm --prefix frontend test
npm --prefix frontend run build
```

For browser tests, keep Django and Vite running as in step 5, then use a third terminal:

```sh
cd frontend
npx playwright install chromium --only-shell
npm run test:e2e
```

On Linux, Playwright may also require its browser system dependencies; install them with `npx playwright install-deps chromium`. E2E tests create test-only accounts, exercise real APIs/MySQL and refresh screenshots under `docs/screenshots/`. Run `python scripts/create_local_admin.py` from the root first to include the optional staff test; otherwise that test skips. If you already have a compatible Chromium executable, set the `PLAYWRIGHT_EXECUTABLE` environment variable to its absolute path. Executed results and limits are in [TEST_RESULTS.md](docs/TEST_RESULTS.md).

## Academic materials

- [Architecture, ER, use cases and data flow](docs/ARCHITECTURE.md)
- [API documentation](docs/API.md) and [Postman collection](docs/CareerLens.postman_collection.json)
- [Schema SQL without user records](docs/database-schema.sql)
- [50 viva questions and answers](docs/VIVA.md)
- [Step-by-step demonstration](docs/DEMONSTRATION.md)
- [Development progress](DEVELOPMENT_PROGRESS.md)
- `docs/screenshots/`: captured desktop and mobile module screens using synthetic data.
- [Editable academic report](outputs/CareerLens-Project-Report.docx) and [18-slide presentation](outputs/CareerLens-Academic-Presentation.pptx).

## Code map for beginners

`backend/core/models.py` defines tables and relationships. `serializers.py` validates requests and shapes JSON. `views.py` authenticates the caller and selects only their records. Services do the actual extraction and scoring. `frontend/src/api.js` adds the token to API requests; `auth.jsx` stores the current account; `pages/` contains the screens. The API is the only layer that talks to MySQL. A React route guard improves navigation, while backend permissions enforce security.

## Deployment boundary

This repository is a working local academic application, not a verified public deployment. Before public use, set `DJANGO_DEBUG=false`, disable sample workspaces, configure hostnames and HTTPS, enable secure redirects behind a correctly configured reverse proxy, use a production WSGI server, back up MySQL and private files, configure persistent throttling, and review data retention. Build the frontend with `npm --prefix frontend run build` and serve `frontend/dist` with SPA fallback. Proxy `/api`, `/admin` and `/static` to the proper backend/static services. Configure `VITE_API_BASE` and `VITE_ADMIN_URL` at build time only when paths differ. Never serve `backend/private_media` as public static files.
