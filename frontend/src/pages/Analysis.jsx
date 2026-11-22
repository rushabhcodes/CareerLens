import { useSearchParams, Link } from 'react-router-dom'
import { Download, ScanText, ArrowUpRight, CheckCircle2, Circle, FileText } from 'lucide-react'
import { useData, useCollection } from '../hooks'
import { downloadFile, errorMessage } from '../api'
import {
  Badge,
  Button,
  DataState,
  EmptyState,
  PageHeading,
  ScoreRing,
  SectionTitle,
  SkillTags,
  useToast,
} from '../components/ui'

export default function Analysis() {
  const [params, setParams] = useSearchParams()
  const list = useCollection('resumes/')
  const id = params.get('resume') || list.data?.results?.[0]?.id
  return (
    <>
      <PageHeading
        eyebrow="SEE THE EVIDENCE"
        title="Your resume, under the lens"
        description="Understand what’s working, what’s missing, and why it matters."
      />
      <DataState state={list}>
        {list.data?.results.length ? (
          <>
            <div className="selector-bar">
              <label htmlFor="resume-select">Review resume</label>
              <select
                id="resume-select"
                value={id || ''}
                onChange={(e) => setParams({ resume: e.target.value })}
              >
                {list.data.results.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.title}
                  </option>
                ))}
              </select>
              <Badge variant="green">Rule-based analysis</Badge>
            </div>
            {id && <ResumeReport key={id} id={id} />}
          </>
        ) : (
          <div className="panel">
            <EmptyState
              icon={ScanText}
              title="Let’s take a closer look"
              description="Upload a resume to review its evidence, skills and quality score."
              to="/resumes?upload=1"
              label="Upload a resume"
            />
          </div>
        )}
      </DataState>
    </>
  )
}

function ResumeReport({ id }) {
  const state = useData(`resumes/${id}/`)
  const r = state.data
  const notify = useToast()
  const info = r?.extracted
  return (
    <DataState state={state}>
      {r && (
        <>
          <div className="report-overview">
            <section className="panel quality-summary">
              <ScoreRing score={r.quality_score} size={142} />
              <div>
                <span className="eyebrow">RESUME QUALITY</span>
                <h2>{r.title}</h2>
                <p>
                  A structural review of documented information.
                  <br />
                  Review the original file for context.
                </p>
                <Button
                  variant="secondary"
                  onClick={() =>
                    downloadFile(`resumes/${id}/report/`, 'careerlens-resume-report.json').catch(
                      (err) => notify(errorMessage(err), 'error'),
                    )
                  }
                >
                  <Download size={15} />
                  Download report
                </Button>
              </div>
            </section>
            <section className="panel contact-summary">
              <SectionTitle title="Candidate details" subtitle="Extracted from selectable text" />
              <dl>
                {[
                  ['Name (heuristic)', info.candidate_name],
                  ['Email', info.email],
                  ['Phone', info.phone],
                  [
                    'Experience',
                    info.experience_years == null
                      ? ''
                      : `${info.experience_years} years explicitly stated`,
                  ],
                ].map(([label, value]) => (
                  <div key={label}>
                    <dt>{label}</dt>
                    <dd>{value || 'Not detected'}</dd>
                  </div>
                ))}
              </dl>
            </section>
          </div>
          <div className="analysis-grid">
            <section className="panel">
              <SectionTitle
                title="Every point, explained"
                subtitle="A transparent breakdown of your quality score"
              />
              <div className="score-components">
                {r.quality_report.components.map((c) => (
                  <div key={c.name}>
                    <div className="component-heading">
                      <h3>{c.name}</h3>
                      <strong>
                        {c.score}
                        <span> / {c.maximum}</span>
                      </strong>
                    </div>
                    <div className="bar-track">
                      <span style={{ width: `${(100 * c.score) / c.maximum}%` }} />
                    </div>
                    <p>{c.explanation}</p>
                  </div>
                ))}
              </div>
              <div className="formula-note">{r.quality_report.formula}</div>
            </section>
            <div className="stack">
              <section className="panel">
                <SectionTitle
                  title="Your next improvements"
                  subtitle="Practical changes to consider"
                />
                {r.quality_report.suggestions.length ? (
                  <ul className="recommendation-list">
                    {r.quality_report.suggestions.map((s, i) => (
                      <li key={s}>
                        <span>{i + 1}</span>
                        <p>{s}</p>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="success-note">
                    <CheckCircle2 size={23} />
                    <p>
                      All scored sections were detected. Review clarity and accuracy manually before
                      applying.
                    </p>
                  </div>
                )}
                <Link className="text-link" to={`/matches?resume=${id}`}>
                  Check alignment with a job <ArrowUpRight size={15} />
                </Link>
              </section>
              <section className="panel">
                <SectionTitle title="Section checklist" />
                {['education', 'experience', 'projects', 'skills', 'certifications'].map(
                  (section) => (
                    <div className="checklist-row" key={section}>
                      {info.sections[section] ? <CheckCircle2 size={17} /> : <Circle size={17} />}
                      <span>{section}</span>
                      <Badge variant={info.sections[section] ? 'green' : 'amber'}>
                        {info.sections[section] ? 'Detected' : 'Missing'}
                      </Badge>
                    </div>
                  ),
                )}
              </section>
            </div>
          </div>
          <section className="panel">
            <SectionTitle
              title="Your skills, with evidence"
              subtitle="Explicit catalog matches. A mention does not establish proficiency."
            />
            {['technical', 'tool', 'soft'].map((category) => {
              const rows = r.skill_evidence.filter((s) => s.skill.category === category)
              return (
                <div className="evidence-group" key={category}>
                  <h3>
                    {category === 'tool'
                      ? 'Tools & technologies'
                      : category === 'soft'
                        ? 'Soft skills'
                        : 'Technical skills'}
                  </h3>
                  {rows.length ? (
                    <div className="evidence-grid">
                      {rows.map((row) => (
                        <details key={row.skill.id}>
                          <summary>
                            {row.skill.name}
                            <span>View evidence</span>
                          </summary>
                          <p>{row.evidence}</p>
                        </details>
                      ))}
                    </div>
                  ) : (
                    <p className="muted">No skills from this category detected.</p>
                  )}
                </div>
              )
            })}
          </section>
          <section className="panel">
            <SectionTitle
              title="The information we found"
              subtitle="Original section text, preserved without rewriting"
            />
            <div className="extracted-sections">
              {Object.entries(info.sections).map(([name, text]) => (
                <details key={name}>
                  <summary>{name}</summary>
                  <p className="preserved-text">{text}</p>
                </details>
              ))}
              <details>
                <summary>
                  <FileText size={16} />
                  Full extracted text
                </summary>
                <pre>{info.text}</pre>
              </details>
            </div>
            <ul className="warning-list">
              {info.warnings.map((w) => (
                <li key={w}>{w}</li>
              ))}
            </ul>
          </section>
        </>
      )}
    </DataState>
  )
}
