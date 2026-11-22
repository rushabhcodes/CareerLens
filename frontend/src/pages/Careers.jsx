import { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { Compass, Sparkles, ArrowRight } from 'lucide-react'
import { api, allRecords, errorMessage } from '../api'
import { useData } from '../hooks'
import { Roadmap } from './Matching'
import {
  Badge,
  Button,
  DataState,
  EmptyState,
  Field,
  PageHeading,
  SkillTags,
  SectionTitle,
  useToast,
  Loading,
} from '../components/ui'

export default function Careers() {
  const [params, setParams] = useSearchParams()
  const [resumes, setResumes] = useState(null)
  const [resume, setResume] = useState(params.get('resume') || '')
  const [useAi, setUseAi] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [expanded, setExpanded] = useState(null)
  const state = useData(`careers/?${resume ? `resume=${resume}` : ''}`)
  const notify = useToast()
  useEffect(() => {
    allRecords('resumes/')
      .then((rows) => {
        setResumes(rows)
        setResume((v) => v || String(rows[0]?.id || ''))
      })
      .catch((err) => setError(errorMessage(err)))
  }, [])
  async function generate(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await api.post(`resumes/${resume}/recommend/`, { use_ai: useAi })
      setExpanded(null)
      state.reload()
      notify('Career pathways saved. Explore the evidence and learning steps.')
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }
  const rows = state.data?.results.slice(0, 4).sort((a, b) => b.score - a.score) || []
  return (
    <>
      <PageHeading
        eyebrow="A WORLD OF POSSIBILITIES"
        title="There’s a path in your potential."
        description="Explore roles that connect with your skills, with a reason behind every recommendation."
      />
      {resumes === null && !error ? (
        <Loading />
      ) : resumes?.length ? (
        <section className="panel">
          <form className="career-form" onSubmit={generate}>
            <Field label="Start with a resume">
              <select
                value={resume}
                required
                onChange={(e) => {
                  setResume(e.target.value)
                  setParams({ resume: e.target.value })
                  setExpanded(null)
                }}
              >
                {resumes.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.title}
                  </option>
                ))}
              </select>
            </Field>
            <Button busy={busy} type="submit">
              <Compass size={18} />
              Explore pathways
            </Button>
          </form>
          <label className="ai-checkbox">
            <input type="checkbox" checked={useAi} onChange={(e) => setUseAi(e.target.checked)} />
            <span>
              Include optional AI learning advice
              <small>
                Sends only matched and missing skill names and role title to your configured
                provider. Scores and extracted facts stay rule-based. Without a provider, local
                analysis still works.
              </small>
            </span>
          </label>
        </section>
      ) : (
        <div className="panel">
          <EmptyState
            icon={Compass}
            title="Let your experience point the way"
            description="Upload a resume to see career paths aligned with your documented skills."
            to="/resumes?upload=1"
            label="Upload a resume"
          />
        </div>
      )}
      {error && (
        <p className="inline-error" role="alert">
          {error}
        </p>
      )}
      <DataState state={state}>
        {rows.length ? (
          <>
            <div className="career-grid">
              {rows.map((c) => (
                <article
                  key={c.id}
                  className={`panel career-card ${expanded === c.id ? 'career-selected' : ''}`}
                >
                  <div className="career-card-top">
                    <span className="pathway-icon">
                      <Compass size={24} />
                    </span>
                    <Badge variant={c.engine.startsWith('llm') ? 'blue' : 'green'}>
                      {c.engine.startsWith('llm') ? 'AI-enriched advice' : 'Rule-based analysis'}
                    </Badge>
                  </div>
                  <h2>{c.role_title}</h2>
                  <p>{c.result.reason}</p>
                  <div className="career-coverage">
                    <span>Catalog skill coverage</span>
                    <strong>{c.score}%</strong>
                  </div>
                  <div className="bar-track">
                    <span style={{ width: `${c.score}%` }} />
                  </div>
                  <h3>Skills you bring</h3>
                  <SkillTags skills={c.result.matched_skills} />
                  <h3>Skills to explore</h3>
                  {c.result.missing_skills.length ? (
                    <SkillTags variant="amber" skills={c.result.missing_skills} />
                  ) : (
                    <p className="muted">All catalog skills mentioned. Keep building evidence.</p>
                  )}
                  <Button
                    variant={expanded === c.id ? 'primary' : 'secondary'}
                    onClick={() => setExpanded(expanded === c.id ? null : c.id)}
                  >
                    {expanded === c.id ? 'Close learning plan' : 'View learning plan'}
                    <ArrowRight size={15} />
                  </Button>
                  {expanded === c.id && (
                    <div className="career-plan">
                      <SectionTitle title="Your learning plan" />
                      <Roadmap steps={c.result.roadmap} />
                      {c.result.advice.length > 0 && (
                        <div className="ai-advice">
                          <h3>
                            <Sparkles size={17} />
                            AI-generated learning advice
                          </h3>
                          <ul>
                            {c.result.advice.map((a) => (
                              <li key={a}>{a}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      <p className="formula-note">{c.result.provider_status}</p>
                    </div>
                  )}
                </article>
              ))}
            </div>
            <div className="formula-note">
              {rows[0].result.formula}
              <br />
              {rows[0].result.experience_note} Showing the latest four recommendations for this
              resume.
            </div>
          </>
        ) : resumes?.length ? (
          <section className="panel">
            <EmptyState
              icon={Compass}
              title="Find a few directions worth exploring"
              description="Choose a resume and select Explore pathways to compare your skills with the career catalog. Roles appear only when at least one skill matches."
            />
          </section>
        ) : null}
      </DataState>
    </>
  )
}
