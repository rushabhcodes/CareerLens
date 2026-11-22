import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import {
  Search,
  ScanText,
  GitCompareArrows,
  Compass,
  ArrowUpRight,
  ShieldCheck,
} from 'lucide-react'
import { useData } from '../hooks'
import { useAuth } from '../auth'
import { api, errorMessage } from '../api'
import {
  PageHeading,
  Badge,
  Button,
  Field,
  DataState,
  EmptyState,
  Pagination,
  formatDate,
  useToast,
  SectionTitle,
} from '../components/ui'

export function History() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const state = useData(`history/?page=${page}&search=${encodeURIComponent(search)}`)
  return (
    <>
      <PageHeading
        eyebrow="YOUR JOURNEY SO FAR"
        title="Every step, in perspective."
        description="Revisit the reviews and comparisons that shape your next move."
      />
      <div className="list-toolbar">
        <div className="search-input">
          <Search size={17} />
          <input
            aria-label="Search analysis history"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            placeholder="Search your analysis history…"
          />
        </div>
        <span className="muted">{state.data?.count ?? 0} activities</span>
      </div>
      <DataState state={state}>
        {state.data?.results.length ? (
          <section className="panel history-panel">
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Analysis</th>
                    <th>Type</th>
                    <th>Score</th>
                    <th>Date</th>
                    <th>
                      <span className="visually-hidden">Open report</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {state.data.results.map((row) => {
                    const Icon =
                      row.kind === 'resume'
                        ? ScanText
                        : row.kind === 'career'
                          ? Compass
                          : GitCompareArrows
                    const to =
                      row.kind === 'resume'
                        ? `/analysis?resume=${row.resume}`
                        : row.kind === 'career'
                          ? `/careers?resume=${row.resume}`
                          : `/matches?match=${row.detail.match_id}`
                    return (
                      <tr key={row.id}>
                        <td>
                          <div className="history-title">
                            <span className="history-icon">
                              <Icon size={18} />
                            </span>
                            <strong>{row.title}</strong>
                          </div>
                        </td>
                        <td>
                          <Badge>{row.kind.replace('_', ' ')}</Badge>
                        </td>
                        <td>
                          {row.score == null ? (
                            '—'
                          ) : (
                            <span className="score-pill">{row.score}%</span>
                          )}
                        </td>
                        <td>{formatDate(row.created_at)}</td>
                        <td>
                          <Link className="icon-btn" to={to} aria-label={`Open ${row.title}`}>
                            <ArrowUpRight size={17} />
                          </Link>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
            <Pagination page={page} count={state.data.count} onPage={setPage} />
          </section>
        ) : (
          <section className="panel">
            <EmptyState
              title="Your story is just getting started"
              description="Upload a resume or run a job match. Your analyses will appear here."
              to="/resumes?upload=1"
              label="Start with a resume"
            />
          </section>
        )}
      </DataState>
    </>
  )
}

export function Profile() {
  const { user, setUser } = useAuth()
  const [form, setForm] = useState({ ...user })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const notify = useToast()
  const change = (e) => setForm({ ...form, [e.target.name]: e.target.value })
  async function save(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const { data } = await api.patch('auth/me/', {
        first_name: form.first_name,
        last_name: form.last_name,
        headline: form.headline,
        location: form.location,
        career_goal: form.career_goal,
      })
      setUser(data)
      notify('Your profile has been updated.')
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }
  return (
    <>
      <PageHeading
        eyebrow="YOUR PERSONAL WORKSPACE"
        title="A little about you."
        description="Keep your profile up to date and your next goal in sight."
      />
      <div className="profile-layout">
        <section className="panel profile-card">
          <span className="avatar avatar-large">
            {user.first_name?.[0]}
            {user.last_name?.[0]}
          </span>
          <h2>
            {user.first_name} {user.last_name}
          </h2>
          <p>{user.email}</p>
          <Badge variant="green">{user.is_staff ? 'Administrator' : 'Career explorer'}</Badge>
          <p className="profile-privacy">
            <ShieldCheck size={21} />
            Your resumes and reports belong to your account. Every API request checks ownership.
          </p>
        </section>
        <section className="panel">
          <SectionTitle title="Personal details" />
          <form onSubmit={save}>
            <div className="form-grid">
              <Field label="First name">
                <input
                  required
                  name="first_name"
                  maxLength={150}
                  value={form.first_name}
                  onChange={change}
                />
              </Field>
              <Field label="Last name">
                <input name="last_name" maxLength={150} value={form.last_name} onChange={change} />
              </Field>
            </div>
            <Field label="Email address" hint="Your sign-in email is fixed for this account.">
              <input type="email" value={user.email} readOnly />
            </Field>
            <Field label="Professional headline">
              <input
                name="headline"
                maxLength={160}
                value={form.headline || ''}
                onChange={change}
                placeholder="e.g. MCA student exploring backend development"
              />
            </Field>
            <Field label="Location">
              <input
                name="location"
                maxLength={120}
                value={form.location || ''}
                onChange={change}
              />
            </Field>
            <Field label="Your next career goal">
              <textarea
                name="career_goal"
                maxLength={240}
                rows={3}
                value={form.career_goal || ''}
                onChange={change}
                placeholder="What would you like to work toward?"
              />
            </Field>
            {error && (
              <p className="inline-error" role="alert">
                {error}
              </p>
            )}
            <Button busy={busy} type="submit">
              Save profile
            </Button>
          </form>
        </section>
      </div>
    </>
  )
}

export function Admin() {
  const { user } = useAuth()
  const state = useData('system/')
  if (!user.is_staff) return <Navigate to="/" replace />
  return (
    <>
      <PageHeading
        eyebrow="STAFF WORKSPACE"
        title="Application administration"
        description="Operational statistics and the managed career catalog."
        action={
          <a
            className="btn btn-primary"
            href={import.meta.env.VITE_ADMIN_URL || '/admin/'}
            target="_blank"
            rel="noreferrer"
          >
            Open Django admin
            <ArrowUpRight size={16} />
          </a>
        }
      />
      <DataState state={state}>
        {state.data && (
          <>
            <div className="metric-grid">
              {Object.entries(state.data)
                .filter(([key]) => key !== 'activity')
                .map(([key, value]) => (
                  <article className="metric-card" key={key}>
                    <span className="capitalize">{key}</span>
                    <strong>{value}</strong>
                  </article>
                ))}
            </div>
            <section className="panel">
              <SectionTitle title="System activity" />
              {state.data.activity.map((row) => (
                <div className="admin-activity" key={row.kind}>
                  <span>{row.kind.replace('_', ' ')}</span>
                  <strong>{row.count}</strong>
                </div>
              ))}
            </section>
            <section className="panel prose">
              <h2>Manage the catalog</h2>
              <p>
                Django admin provides staff access to registered users, skills and aliases, related
                skills, job categories, career roles and learning resources. Sign in with a staff
                account and the model permissions assigned to it. Superusers have full access.
              </p>
            </section>
          </>
        )}
      </DataState>
    </>
  )
}

export function Methodology() {
  return (
    <>
      <PageHeading
        eyebrow="TRANSPARENT BY DESIGN"
        title="A score you can understand."
        description="The evidence, formulas and limitations behind CareerLens."
      />
      <div className="panel prose">
        <h2>What the local engine does</h2>
        <p>
          PyMuPDF and python-docx extract selectable text. spaCy tokenizes it and matches phrases
          against an administrator-managed vocabulary. Section headings and regular expressions
          identify contact information and explicit experience statements. Results are labeled
          rule-based. A skill mention does not verify proficiency.
        </p>
        <h2>Resume quality</h2>
        <p>
          Quality = contact details (20) + section completeness (30) + catalog skill breadth (25) +
          contribution evidence (15) + text length (10). Three contact fields share 20 points.
          Education, experience, projects, skills and certifications each contribute 6 points when a
          recognized heading has content. Each detected skill contributes 2.5 points up to 10
          skills. An action verb or percentage contributes 15 points. A length of 150–1200 words
          contributes 10 points, 60–149 contributes 5, and other lengths contribute 0. The report
          displays every component.
        </p>
        <h2>Job alignment</h2>
        <p>
          Essential skills carry 2 points and preferred skills carry 1. Explicit matches earn full
          credit. Administrator-defined related skills earn half credit and are shown as partial.
          Missing skills earn zero. Skill credit is earned points divided by total points.
        </p>
        <p>
          Experience credit is the smaller of documented years divided by required years and 1. A
          requirement of zero years earns full credit. Missing explicit experience earns zero when
          experience is requested. Qualification credit requires the exact saved phrase, ignoring
          capitalization and whitespace, in the detected education section. Equivalent
          qualifications need manual review.
        </p>
        <p>
          The final score combines skills with weight 70, experience with weight 20 and
          qualification with weight 10. Unrequested components are excluded, and remaining weights
          are renormalized. It measures documented alignment. It does not estimate your probability
          of getting hired.
        </p>
        <h2>Career pathways</h2>
        <p>
          Career roles rank by the fraction of their catalog skills explicitly mentioned in the
          resume. Roles with zero overlap are omitted. Ranking does not estimate seniority or job
          readiness. Missing catalog skills form a learning roadmap with resources maintained by an
          administrator.
        </p>
        <h2>Optional AI advice</h2>
        <p>
          You can opt in when generating career pathways. The server reads provider credentials from
          environment variables and sends only the role title and matched and missing skill names.
          Responses must match a strict JSON schema. Failure, rate limiting or invalid output keeps
          the local result and shows a fallback label. AI advice never changes candidate facts or
          numerical scores.
        </p>
        <h2>Parsing limits and privacy</h2>
        <p>
          Names use a first-line heuristic. Years of experience require an explicit statement such
          as “2 years of experience.” Dates are not converted into estimated employment duration.
          Unrecognized section headings can lower completeness scores. Scanned resumes need OCR,
          which is not configured. Read the original file to validate extraction. Files have random
          storage names, are not served through a public media URL, and downloads require an owner
          token. Deleting a resume also removes its dependent analysis records and original file.
        </p>
      </div>
    </>
  )
}
