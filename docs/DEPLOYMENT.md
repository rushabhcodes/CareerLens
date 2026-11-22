# Hosting CareerLens on Vercel

Live application: **https://careerlens.rushabh.dev/**. Recorded walkthrough: **https://careerlens.rushabh.dev/demo/**.

The deployment uses the existing React and Django application, with PostgreSQL selected by `DATABASE_URL`. MySQL remains the default when that variable is empty. No local computer or temporary tunnel is needed to keep the hosted application running.

## Hosting layout

- `vercel.json` declares a Vite frontend service and a Django backend service in one project. API, Django admin and static admin assets route to the backend; other paths reach the frontend, with an SPA fallback for client routes.
- The Vercel project and the database use Singapore (`sin1`) to keep database calls close to the Python function.
- Neon provides PostgreSQL persistence. `PRIVATE_FILE_STORAGE=database` stores the small uploaded originals in the `PrivateDocument` table, avoiding an ephemeral function filesystem. The existing owner-checked download endpoint serves them. Deletion also removes the stored original.
- Vercel serves the frontend, video player and MP4 as static assets. Django's collected static assets serve its staff interface.
- The existing deployment uses Vercel Hobby and Neon Free. Paid upgrades were not enabled. Each service remains subject to its provider's usage allowances.

Vercel's [Django guide](https://vercel.com/docs/frameworks/full-stack/django), [Services routing reference](https://vercel.com/docs/services/routing) and [Neon integration](https://vercel.com/marketplace/neon) document the hosting facilities used here. Services is currently a Vercel beta feature.

## Deploy another copy

1. Clone the repository and install its dependencies using the main README. Sign in to the [Vercel CLI](https://vercel.com/docs/cli) with your own account. Use a current CLI version that supports Services.
2. Create/link a Vercel project with the repository root as its root directory. `vercel.json` supplies each service's build configuration. Connect your GitHub repository if you want deployments on pushes.
3. Provision a separate Neon database through Vercel Marketplace. Select its **Free** plan and the Singapore region. This injects `DATABASE_URL` and the direct connection URL into your project's environment. Never reuse someone else's database credentials.
4. Add the environment variables below to Vercel **Production**, replacing the example hostname and generating a new Django secret. Database credentials and provider keys belong only in Vercel's encrypted server environment.
5. Download the production environment to the ignored `.env.production` file and initialize the database using the commands below.
6. Deploy with `vercel deploy --prod`. Add your own domain in the Vercel project's Domains settings and apply any DNS records Vercel requests. Verify the custom domain without being signed into Vercel.

| Variable                | Hosted value / purpose                                                                                                                    |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `DATABASE_URL`          | Neon pooled PostgreSQL connection URL, supplied by its integration; TLS is required by default                                            |
| `DATABASE_URL_UNPOOLED` | Direct URL used by the management helper for migrations and isolated test databases                                                       |
| `DJANGO_SECRET_KEY`     | New random secret, for example generated with `python -c "import secrets; print(secrets.token_urlsafe(48))"`; keep it private             |
| `DJANGO_DEBUG`          | `false`                                                                                                                                   |
| `DJANGO_ALLOWED_HOSTS`  | Your custom hostname and any production alias you intend to use, comma-separated; Vercel's deployment hostname is also read automatically |
| `CORS_ALLOWED_ORIGINS`  | Your full HTTPS origin, e.g. `https://careerlens.example.com`; also used for trusted Django admin origins                                 |
| `DEMO_ENABLED`          | `true` to explicitly enable one-click sample workspaces with debug disabled                                                               |
| `PRIVATE_FILE_STORAGE`  | `database`                                                                                                                                |
| `MAX_UPLOAD_MIB`        | `4`, leaving room under Vercel's default 4.5 MB request-body ceiling                                                                      |
| `DJANGO_ADMIN_PATH`     | `django-admin/`, keeping the backend staff interface distinct from the React `/admin` route                                               |
| `VITE_ADMIN_URL`        | `/django-admin/`                                                                                                                          |
| `VITE_PUBLIC_DEMO`      | `true`, showing the public-demo notice                                                                                                    |
| `VITE_MAX_UPLOAD_MIB`   | `4`, matching the API upload limit                                                                                                        |

`VITE_*` values are public build-time configuration. Never put a database password, Django secret or API key in a `VITE_*` variable. Configure an isolated database and secret for Preview if you enable preview deployments; production data should not be reused for previews.

With the local Python environment activated, run from the repository root:

```sh
vercel env pull .env.production --environment production
python scripts/manage_hosted.py migrate --noinput
python scripts/manage_hosted.py seed_catalog
python scripts/manage_hosted.py check
vercel deploy --prod
```

The management helper reads production settings without replacing the local `.env`. Its credentials file is ignored by Git and restricted to the owner on Unix. Run migrations before deploying a schema change. To create your private staff account interactively:

```sh
python scripts/manage_hosted.py createsuperuser
```

Use its email to sign into the React app. Staff can open the Django interface at `/django-admin/` and sign in there with their username. No administrator password is included in the repository or recording. The administrator created for this deployment has its credentials stored privately on the owner's machine at `.runtime/production-admin-credentials.txt`.

## Record and publish a new walkthrough

The repository includes an actual captioned MP4, its WebVTT captions, a poster and chapter metadata under `docs/demo/`. The recording uses real browser interactions and fictional candidate data, without mocked API responses. Install Chromium for Playwright and FFmpeg, then run from the root:

```sh
node scripts/record_demo.mjs
python scripts/encode_demo.py
```

`DEMO_BASE_URL` optionally selects another deployment. Raw recordings and downloaded originals/reports remain in ignored `.runtime/demo-recording/`. An optional `DEMO_STAFF_SESSION` points to a private JSON file containing `token` and `sessionid` for an already authenticated administrator; it lets the recorder include staff screens without filming a login or credentials. Without it, the staff segment is skipped. Never commit that session file.

The frontend's hosting build copies the finished `docs/demo/` artifacts into its static output with `scripts/copy_demo_assets.mjs`. Commit the finished MP4 and documentation, then redeploy to refresh `/demo/`.

## Verification and limits

Backend tests run on a separate `test_careerlens` database, including when using the hosted management helper. They do not run against the application database itself. See [TEST_RESULTS.md](TEST_RESULTS.md) for executed checks.

The shared demo has a 4 MiB upload limit, supports selectable-text PDFs and DOCX, and has no OCR. No live AI provider is configured; optional advice falls back to the labeled local engine. Each sample click creates a separate persisted workspace; these accounts are not automatically expired or deleted. The owner can remove obsolete sample users through Django admin, which cascades through their private data. Public deployment has not been load-tested, and the default per-process throttle cache is not a distributed abuse-control system. Use synthetic resumes for demonstrations.
