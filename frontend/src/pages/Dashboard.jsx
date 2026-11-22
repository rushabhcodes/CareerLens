import { Link } from 'react-router-dom'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import {
  ArrowRight,
  ArrowUpRight,
  Plus,
  Files,
  ScanText,
  GitCompareArrows,
  BriefcaseBusiness,
  Compass,
  FileText,
  Check,
  Sparkles,
  ChevronRight,
} from 'lucide-react'
import { useAuth } from '../auth'
import { useData } from '../hooks'
import {
  PageHeading,
  DataState,
  SectionTitle,
  ScoreRing,
  Badge,
  EmptyState,
  formatDate,
  SkillTags,
} from '../components/ui'

export default function Dashboard() {
  const { user } = useAuth()
  const state = useData('dashboard/')
  const d = state.data
  return (
    <>
      <PageHeading
        eyebrow="YOUR NEXT CHAPTER"
        title={`A little clarity, ${user.first_name || 'explorer'}.`}
        description="Your experience has a story. Let’s see where it can take you."
        action={
          <Link to="/resumes?upload=1" className="btn btn-primary">
            <Plus size={18} />
            Upload resume
          </Link>
        }
      />
      <DataState state={state}>
        {d && (
          <>
            <section className="overview-hero">
              <div className="hero-copy">
                <span className="hero-eyebrow">
                  <span />
                  YOUR CAREER, IN FOCUS
                </span>
                <h2>
                  {d.careers[0] ? (
                    <>
                      You have the foundation.
                      <br />
                      Build your next opportunity.
                    </>
                  ) : (
                    <>
                      Your next move starts
                      <br />
                      with what you already know.
                    </>
                  )}
                </h2>
                <p>
                  {d.careers[0] ? (
                    <>
                      Your skills align with{' '}
                      <strong>{d.careers[0].role_title.toLowerCase()}</strong>.
                      <br />
                      Explore the evidence and make a plan for the gaps.
                    </>
                  ) : (
                    'Bring your resume. Discover your strengths, explore career paths, and find the skills worth learning next.'
                  )}
                </p>
                <Link
                  className="btn btn-dark"
                  to={d.total_resumes ? '/careers' : '/resumes?upload=1'}
                >
                  {d.total_resumes ? 'Explore my career paths' : 'Analyze my first resume'}
                  <ArrowRight size={16} />
                </Link>
                <div className="hero-footnote">
                  <Check size={13} />
                  Clear evidence. Practical next steps.
                </div>
              </div>
              <div className="hero-visual" aria-hidden="true">
                <div className="hero-orbit orbit-one" />
                <div className="hero-orbit orbit-two" />
                <div className="hero-orbit orbit-three" />
                <span className="orbit-node node-one" />
                <span className="orbit-node node-two" />
                <div className="hero-focus">
                  <Compass size={35} strokeWidth={1.2} />
                  <strong>{d.total_resumes ? d.average_quality : 'Your'}</strong>
                  <span>{d.total_resumes ? 'average resume quality' : 'potential, in focus'}</span>
                </div>
                <span className="hero-chip chip-one">
                  <Check size={13} />
                  {d.top_skills[0]?.name || 'Your strengths'}
                </span>
                <span className="hero-chip chip-two">
                  <Sparkles size={13} />
                  {d.top_skills[1]?.name || 'Your possibilities'}
                </span>
                <span className="lens-caption">A CLEARER PICTURE OF YOU</span>
              </div>
            </section>
            <div className="metric-grid">
              {[
                [Files, 'Resumes uploaded', d.total_resumes, 'Your professional story', 'mint'],
                [
                  ScanText,
                  'Average resume quality',
                  d.total_resumes ? `${d.average_quality}%` : '—',
                  'Based on detected evidence',
                  'blue',
                ],
                [
                  GitCompareArrows,
                  'Average job match',
                  d.total_matches ? `${d.average_match}%` : '—',
                  `${d.total_matches} saved comparison${d.total_matches === 1 ? '' : 's'}`,
                  'amber',
                ],
                [
                  BriefcaseBusiness,
                  'Jobs analyzed',
                  d.analyzed_jobs,
                  `${d.total_jobs} saved job description${d.total_jobs === 1 ? '' : 's'}`,
                  'lavender',
                ],
              ].map(([Icon, title, value, desc, color]) => (
                <article className="metric-card" key={title}>
                  <div className="metric-top">
                    <span>{title}</span>
                    <span className={`metric-icon ${color}`}>
                      <Icon size={18} />
                    </span>
                  </div>
                  <strong>{value}</strong>
                  <small>{desc}</small>
                </article>
              ))}
            </div>
            <div className="dashboard-columns">
              <section className="panel chart-panel">
                <SectionTitle
                  title="How you match up"
                  subtitle="Your most recent job comparisons"
                  to="/matches"
                  label="Compare a job"
                />
                {d.trend.length ? (
                  <>
                    <div className="chart-legend">
                      <span />
                      Job alignment
                      <span className="legend-range">0–100% documented alignment</span>
                    </div>
                    <div className="dashboard-chart">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart
                          data={d.trend}
                          margin={{ top: 15, right: 15, left: -27, bottom: 0 }}
                        >
                          <defs>
                            <linearGradient id="scoreFill" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="0%" stopColor="#119a86" stopOpacity={0.18} />
                              <stop offset="100%" stopColor="#119a86" stopOpacity={0} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid vertical={false} stroke="#edf0f0" strokeDasharray="4 4" />
                          <XAxis
                            dataKey="job"
                            tick={{ fontSize: 10, fill: '#71817e' }}
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(v) => (v.length > 17 ? `${v.slice(0, 15)}…` : v)}
                          />
                          <YAxis
                            domain={[0, 100]}
                            tick={{ fontSize: 11, fill: '#71817e' }}
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(v) => `${v}%`}
                          />
                          <Tooltip
                            contentStyle={{
                              borderRadius: 12,
                              border: '1px solid #e1e9e6',
                              fontSize: 12,
                            }}
                            formatter={(value) => [`${value}%`, 'Alignment']}
                          />
                          <Area
                            isAnimationActive={false}
                            type="monotone"
                            dataKey="score"
                            stroke="#168c7c"
                            strokeWidth={2.5}
                            fill="url(#scoreFill)"
                            dot={{
                              r: 4,
                              fill: '#168c7c',
                              stroke: 'white',
                              strokeWidth: 3,
                            }}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                    <p className="chart-note">
                      {d.trend.map((t) => `${t.job}: ${t.score}%`).join(' · ')}
                    </p>
                  </>
                ) : (
                  <EmptyState
                    title="Your progress starts here"
                    description="Compare a resume with a saved job to see your alignment."
                    to="/matches"
                    label="Create a comparison"
                  />
                )}
              </section>
              <section className="panel skills-panel">
                <SectionTitle
                  title="Your skill fingerprint"
                  subtitle="Skills found across your resumes"
                  to="/analysis"
                  label="Details"
                />
                {d.top_skills.length ? (
                  <>
                    <div className="fingerprint-bars">
                      {d.top_skills.slice(0, 6).map((skill, i) => (
                        <div className="fingerprint-row" key={skill.name}>
                          <div>
                            <span>{skill.name}</span>
                            <small>
                              {skill.count} resume{skill.count === 1 ? '' : 's'}
                            </small>
                          </div>
                          <div className="bar-track">
                            <span
                              style={{
                                width: `${(100 * skill.count) / d.total_resumes}%`,
                                opacity: 1 - i * 0.09,
                              }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="subtle-note">
                      <span className="tiny-dot" />
                      Explicit mentions, not verified proficiency
                    </div>
                  </>
                ) : (
                  <EmptyState
                    title="Make your skills visible"
                    description="Upload a resume to discover your skill fingerprint."
                    to="/resumes"
                    label="Add a resume"
                  />
                )}
              </section>
            </div>
            <div className="dashboard-columns">
              <section className="panel">
                <SectionTitle
                  title="Your resume collection"
                  subtitle="A fresh look at your professional story"
                  to="/resumes"
                />
                {d.recent_resumes.length ? (
                  <div className="resume-mini-list">
                    {d.recent_resumes.map((r) => (
                      <Link to={`/analysis?resume=${r.id}`} className="resume-mini" key={r.id}>
                        <span className="document-icon">
                          <FileText size={23} />
                          <small>{r.original_filename.split('.').pop().toUpperCase()}</small>
                        </span>
                        <div>
                          <strong>{r.title}</strong>
                          <small>
                            {formatDate(r.created_at)} <span>·</span>{' '}
                            {(r.file_size / 1024).toFixed(0)} KB
                          </small>
                        </div>
                        <div className="mini-score">
                          <strong>
                            {r.quality_score}
                            <span>/100</span>
                          </strong>
                          <small>Resume quality</small>
                        </div>
                        <ChevronRight size={17} />
                      </Link>
                    ))}
                  </div>
                ) : (
                  <EmptyState
                    title="Your story belongs here"
                    description="Add a PDF or DOCX resume to begin your review."
                    to="/resumes?upload=1"
                    label="Upload resume"
                  />
                )}
              </section>
              <section className="panel focus-panel">
                <SectionTitle
                  title="A few skills worth exploring"
                  subtitle="Gaps from your latest 20 comparisons"
                  to="/gaps"
                  label="See roadmap"
                />
                {d.missing_skills.length ? (
                  <>
                    <div className="focus-skills">
                      {d.missing_skills.slice(0, 4).map((skill, i) => (
                        <Link to="/gaps" className="focus-skill" key={skill.name}>
                          <span className={`focus-dot focus-dot-${i}`} />
                          <div>
                            <strong>{skill.name}</strong>
                            <small>
                              Gap in {skill.count} comparison
                              {skill.count === 1 ? '' : 's'}
                            </small>
                          </div>
                          <ArrowUpRight size={17} />
                        </Link>
                      ))}
                    </div>
                    <p className="focus-note">One new skill can open a different conversation.</p>
                  </>
                ) : (
                  <EmptyState
                    title="Find your next learning goal"
                    description="A job comparison reveals the skills to work on next."
                    to="/matches"
                    label="Compare a job"
                  />
                )}
              </section>
            </div>
            <section className="panel pathway-panel">
              <SectionTitle
                title="Where your skills could take you"
                subtitle="Career paths with evidence behind every recommendation"
                to="/careers"
                label="Explore pathways"
              />
              {d.careers.length ? (
                <div className="pathway-grid">
                  {d.careers.slice(0, 3).map((c, i) => (
                    <Link to={`/careers?resume=${c.resume}`} className="pathway-card" key={c.id}>
                      <div className="pathway-top">
                        <span className={`pathway-icon path-${i}`}>
                          <Compass size={21} />
                        </span>
                        <ArrowUpRight size={18} />
                      </div>
                      <h3>{c.role_title}</h3>
                      <p>{c.result.matched_skills.slice(0, 3).join(' · ')}</p>
                      <div className="pathway-bottom">
                        <span>Skill coverage</span>
                        <strong>{c.score}%</strong>
                      </div>
                      <div className="bar-track">
                        <span style={{ width: `${c.score}%` }} />
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <EmptyState
                  icon={Compass}
                  title="There’s more than one path forward"
                  description="Analyze a resume, then generate career recommendations based on its skills."
                  to="/careers"
                  label="Explore career pathways"
                />
              )}
            </section>
          </>
        )}
      </DataState>
    </>
  )
}
