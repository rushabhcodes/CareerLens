import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  GitCompareArrows,
  ArrowRight,
  CheckCircle2,
  CircleAlert,
  Compass,
  ExternalLink,
  ScanText,
} from 'lucide-react'
import { api, allRecords, errorMessage } from '../api'
import { useData, useCollection } from '../hooks'
import {
  Badge,
  Button,
  DataState,
  EmptyState,
  Field,
  PageHeading,
  ScoreRing,
  SectionTitle,
  SkillTags,
  formatDate,
  useToast,
  Loading,
  ErrorState,
} from '../components/ui'

export function Roadmap({ steps }) {
  if (!steps.length)
    return (
      <div className="success-note">
        <CheckCircle2 size={22} />
        <p>
          All requested catalog skills are explicitly present. Keep strengthening your evidence with
          demonstrable work.
        </p>
      </div>
    )
  return (
    <div className="roadmap">
      {steps.map((step, i) => (
        <article className="roadmap-step" key={step.skill_id}>
          <span className="roadmap-number">{i + 1}</span>
          <div className="roadmap-content">
            <div className="roadmap-title">
              <h3>{step.name}</h3>
              <Badge variant={step.importance === 'essential' ? 'amber' : 'blue'}>
                {step.partial
                  ? 'Related evidence'
                  : step.importance === 'essential'
                    ? 'Essential skill'
                    : 'Preferred skill'}
              </Badge>
              <Badge>{step.category}</Badge>
            </div>
            <p>{step.action}</p>
            <p className="milestone">
              <strong>Milestone:</strong> {step.milestone}
            </p>
            <div className="resource-links">
              {step.resources.map((resource) => (
                <a key={resource.url} href={resource.url} target="_blank" rel="noreferrer">
                  {resource.title}
                  <ExternalLink size={13} />
                </a>
              ))}
            </div>
          </div>
        </article>
      ))}
    </div>
  )
}

export function MatchReport({ match, compact = false }) {
  const result = match.result
  return (
    <>
      <section className="panel match-summary">
        <ScoreRing score={match.score} size={136} label="Documented job alignment" />
        <div>
          <Badge variant="green">Rule-based comparison</Badge>
          <h2>{match.job_title}</h2>
          <p>
            {match.company || 'Company unspecified'} <span>·</span> {match.resume_title}
          </p>
          <small>{formatDate(match.created_at)}</small>
        </div>
        <div className="match-totals">
          <div>
            <strong>{result.matched.length}</strong>
            <span>Matched</span>
          </div>
          <div>
            <strong>{result.partial.length}</strong>
            <span>Related</span>
          </div>
          <div>
            <strong>{result.missing.length}</strong>
            <span>Missing</span>
          </div>
        </div>
      </section>
      <p className="analysis-disclaimer">
        <CircleAlert size={16} />
        {result.disclaimer}
      </p>
      {!compact && (
        <>
          <div className="match-skill-columns">
            {[
              ['Matched skills', result.matched, 'green', 'Explicitly mentioned in your resume'],
              ['Partially matched', result.partial, 'amber', 'Related evidence earns half credit'],
              ['Missing skills', result.missing, 'red', 'No matching mention was found'],
            ].map(([title, skills, color, desc]) => (
              <section className="panel" key={title}>
                <SectionTitle title={title} subtitle={desc} />
                {skills.length ? (
                  <div className="match-skill-list">
                    {skills.map((skill) => (
                      <details key={skill.skill_id}>
                        <summary>
                          <span className={`status-dot ${color}`} />
                          {skill.name}
                          <Badge>{skill.importance}</Badge>
                        </summary>
                        <p>
                          {skill.evidence ||
                            skill.explanation ||
                            'Add truthful evidence after developing this skill.'}
                        </p>
                      </details>
                    ))}
                  </div>
                ) : (
                  <p className="muted">No skills in this category.</p>
                )}
              </section>
            ))}
          </div>
          <section className="panel">
            <SectionTitle
              title="The reasoning behind your score"
              subtitle="Active components and their documented evidence"
            />
            <div className="match-components">
              {result.components.map((c) => (
                <div key={c.name}>
                  <div>
                    <h3>
                      {c.name}
                      <Badge>{c.weight} weight units</Badge>
                    </h3>
                    <strong>{c.value}%</strong>
                  </div>
                  <div className="bar-track">
                    <span style={{ width: `${c.value}%` }} />
                  </div>
                  <p>{c.explanation}</p>
                </div>
              ))}
            </div>
            <div className="formula-note">{result.formula}</div>
            <div className="evidence-pair">
              <details>
                <summary>Experience evidence</summary>
                <p className="preserved-text">
                  {result.experience_evidence || 'No experience section detected.'}
                </p>
              </details>
              <details>
                <summary>Qualification evidence</summary>
                <p className="preserved-text">
                  {result.education_evidence || 'No education section detected.'}
                </p>
              </details>
              <details>
                <summary>Saved job description at analysis time</summary>
                <p className="preserved-text">{result.job_snapshot?.description}</p>
              </details>
            </div>
          </section>
          <section className="panel">
            <SectionTitle
              title="A practical way forward"
              subtitle="Build evidence for each skill gap"
            />
            <Roadmap steps={result.roadmap} />
          </section>
        </>
      )}
    </>
  )
}

export default function Matching() {
  const [params] = useSearchParams()
  const [choices, setChoices] = useState(null)
  const [error, setError] = useState('')
  const [resume, setResume] = useState(params.get('resume') || '')
  const [job, setJob] = useState(params.get('job') || '')
  const [busy, setBusy] = useState(false)
  const [match, setMatch] = useState(null)
  const history = useCollection('matches/')
  const notify = useToast()
  useEffect(() => {
    let active = true
    Promise.all([allRecords('resumes/'), allRecords('jobs/')])
      .then(([resumes, jobs]) => {
        if (!active) return
        setChoices({ resumes, jobs })
        setResume((v) => v || String(resumes[0]?.id || ''))
        setJob((v) => v || String(jobs[0]?.id || ''))
      })
      .catch((err) => {
        if (active) setError(errorMessage(err))
      })
    return () => {
      active = false
    }
  }, [])
  useEffect(() => {
    if (params.get('match'))
      api
        .get(`matches/${params.get('match')}/`)
        .then(({ data }) => setMatch(data))
        .catch((err) => setError(errorMessage(err)))
  }, [params])
  async function compare(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const { data } = await api.post('matches/', {
        resume: Number(resume),
        job: Number(job),
      })
      setMatch(data)
      history.reload()
      notify('Comparison saved. Your score and skill gaps are ready.')
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }
  return (
    <>
      <PageHeading
        eyebrow="FIND YOUR ALIGNMENT"
        title="A role. A resume. A clearer picture."
        description="Compare your documented experience with the requirements of a role."
      />
      {!choices && !error && <Loading />}
      {choices && (
        <section className="panel comparison-form">
          <form onSubmit={compare}>
            <Field label="Your resume">
              <select value={resume} onChange={(e) => setResume(e.target.value)} required>
                <option value="">Choose a resume</option>
                {choices.resumes.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.title}
                  </option>
                ))}
              </select>
            </Field>
            <span className="compare-connector">
              <GitCompareArrows size={24} />
            </span>
            <Field label="The opportunity">
              <select value={job} onChange={(e) => setJob(e.target.value)} required>
                <option value="">Choose a job description</option>
                {choices.jobs.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.title}
                    {j.company ? ` · ${j.company}` : ''}
                  </option>
                ))}
              </select>
            </Field>
            <Button busy={busy} disabled={!resume || !job} type="submit">
              Analyze match <ArrowRight size={16} />
            </Button>
          </form>
          {(!choices.resumes.length || !choices.jobs.length) && (
            <p className="form-help">
              You’ll need a <Link to="/resumes?upload=1">resume</Link> and a{' '}
              <Link to="/jobs">saved job description</Link> to run a comparison.
            </p>
          )}
        </section>
      )}
      {error && <ErrorState message={error} />}{' '}
      {match ? (
        <MatchReport match={match} />
      ) : (
        !history.loading &&
        !history.data?.results.length && (
          <div className="panel">
            <EmptyState
              icon={GitCompareArrows}
              title="See how your experience connects"
              description="Choose a resume and job above. Every score comes with matched evidence and a plan for what’s missing."
            />
          </div>
        )
      )}
      <section className="panel">
        <SectionTitle
          title="Saved comparisons"
          subtitle="Select a report to review its original scoring evidence"
        />
        <DataState state={history}>
          {history.data?.results.length ? (
            <div className="comparison-history">
              {history.data.results.map((m) => (
                <button
                  key={m.id}
                  className={`comparison-history-row ${match?.id === m.id ? 'selected' : ''}`}
                  onClick={() => setMatch(m)}
                >
                  <span className="job-icon">
                    <GitCompareArrows size={18} />
                  </span>
                  <div>
                    <strong>{m.job_title}</strong>
                    <small>
                      {m.resume_title} · {formatDate(m.created_at)}
                    </small>
                  </div>
                  <span className="score-pill">{m.score}%</span>
                  <ArrowRight size={16} />
                </button>
              ))}
            </div>
          ) : (
            <p className="muted">No saved comparisons yet.</p>
          )}
        </DataState>
      </section>
    </>
  )
}

export function Gaps() {
  const matches = useCollection('matches/')
  const [selected, setSelected] = useState('')
  const match =
    matches.data?.results.find((m) => String(m.id) === selected) || matches.data?.results[0]
  return (
    <>
      <PageHeading
        eyebrow="YOUR NEXT LEARNING GOALS"
        title="Turn your gaps into a plan."
        description="Focus on the skills your target role asks for, one practical step at a time."
        action={
          <Link to="/matches" className="btn btn-primary">
            Compare another job
            <ArrowRight size={16} />
          </Link>
        }
      />
      <DataState state={matches}>
        {match ? (
          <>
            <div className="selector-bar">
              <label htmlFor="gap-match">Saved comparison</label>
              <select id="gap-match" value={match.id} onChange={(e) => setSelected(e.target.value)}>
                {matches.data.results.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.job_title} · {m.resume_title} · {formatDate(m.created_at)}
                  </option>
                ))}
              </select>
            </div>
            <MatchReport match={match} compact />
            <div className="gap-summary-grid">
              {[
                [
                  'Essential gaps',
                  match.result.gaps.filter((g) => g.importance === 'essential').length,
                ],
                [
                  'Preferred gaps',
                  match.result.gaps.filter((g) => g.importance === 'preferred').length,
                ],
                [
                  'Technical & tool gaps',
                  match.result.gaps.filter((g) => g.category !== 'soft').length,
                ],
                ['Soft skill gaps', match.result.gaps.filter((g) => g.category === 'soft').length],
              ].map(([title, value]) => (
                <div className="panel gap-stat" key={title}>
                  <span>{title}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
            <section className="panel">
              <SectionTitle
                title="Your learning roadmap"
                subtitle="Essential skills come first. Related evidence still needs strengthening."
              />
              <Roadmap steps={match.result.roadmap} />
            </section>
            <section className="panel">
              <SectionTitle
                title="Build on what you know"
                subtitle="Explicitly documented strengths for this role"
              />
              <SkillTags skills={match.result.matched} />
              <div className="formula-note">
                Each roadmap step comes from an unfulfilled saved job requirement. Resource links
                come from the managed skill catalog. Learning time and mastery are not inferred.
              </div>
            </section>
          </>
        ) : (
          <div className="panel">
            <EmptyState
              icon={Compass}
              title="Your next skill is waiting to be discovered"
              description="Compare a resume with a job to build a personalized roadmap from its requirements."
              to="/matches"
              label="Find my skill gaps"
            />
          </div>
        )}
      </DataState>
    </>
  )
}
