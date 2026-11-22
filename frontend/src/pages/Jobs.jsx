import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Plus,
  Search,
  BriefcaseBusiness,
  Pencil,
  Trash2,
  ArrowUpRight,
  Building2,
} from 'lucide-react'
import { api, errorMessage } from '../api'
import { useData } from '../hooks'
import {
  Badge,
  Button,
  DataState,
  EmptyState,
  Field,
  Modal,
  PageHeading,
  Pagination,
  SkillTags,
  formatDate,
  useToast,
} from '../components/ui'

function JobForm({ job, onClose, onSaved }) {
  const [form, setForm] = useState(
    job || {
      title: '',
      company: '',
      description: '',
      experience_years: '',
      qualification: '',
      requirements: [],
    },
  )
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const skills = useData('skills/')
  const [skillSearch, setSkillSearch] = useState('')
  const update = (e) => setForm({ ...form, [e.target.name]: e.target.value })
  function toggle(skill) {
    setForm({
      ...form,
      requirements: form.requirements.some((r) => r.skill === skill.id)
        ? form.requirements.filter((r) => r.skill !== skill.id)
        : [...form.requirements, { skill: skill.id, name: skill.name, importance: 'essential' }],
    })
  }
  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    const payload = {
      ...form,
      experience_years:
        form.experience_years === '' || form.experience_years == null
          ? null
          : Number(form.experience_years),
    }
    if (!payload.requirements.length) delete payload.requirements
    try {
      if (job) await api.patch(`jobs/${job.id}/`, payload)
      else await api.post('jobs/', payload)
      onSaved()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }
  return (
    <Modal title={job ? 'Edit job description' : 'Add an opportunity'} onClose={onClose} wide>
      <p className="modal-description">
        Save the role you’re working toward. Make its requirements explicit for a meaningful
        comparison.
      </p>
      <form onSubmit={submit}>
        <div className="form-grid">
          <Field label="Job title">
            <input
              name="title"
              required
              maxLength={160}
              placeholder="e.g. Python backend developer"
              value={form.title}
              onChange={update}
            />
          </Field>
          <Field label="Company">
            <input
              name="company"
              maxLength={160}
              placeholder="Company or organization"
              value={form.company}
              onChange={update}
            />
          </Field>
        </div>
        <Field label="Job description">
          <textarea
            name="description"
            required
            minLength={30}
            maxLength={30000}
            rows={5}
            placeholder="Paste the responsibilities and requirements…"
            value={form.description}
            onChange={update}
          />
        </Field>
        <div className="form-grid">
          <Field
            label="Required experience (years)"
            hint="Leave blank when unspecified. Zero means no experience required."
          >
            <input
              type="number"
              name="experience_years"
              min={0}
              max={60}
              step={0.5}
              value={form.experience_years ?? ''}
              onChange={update}
            />
          </Field>
          <Field
            label="Qualification phrase"
            hint="Use a phrase expected in the resume, such as MCA. Leave blank if unspecified."
          >
            <input
              name="qualification"
              maxLength={240}
              value={form.qualification}
              onChange={update}
            />
          </Field>
        </div>
        <div className="field">
          <span>Skill requirements</span>
          <small>
            Select catalog skills, or leave empty to detect skills from the description. Review
            automatically detected requirements after saving.
          </small>
          <input
            aria-label="Find a skill"
            value={skillSearch}
            onChange={(e) => setSkillSearch(e.target.value)}
            placeholder="Find a skill…"
          />
          <DataState state={skills}>
            <div className="skill-picker">
              {skills.data
                ?.filter((s) => s.name.toLowerCase().includes(skillSearch.toLowerCase()))
                .map((s) => (
                  <button
                    className={form.requirements.some((r) => r.skill === s.id) ? 'chosen' : ''}
                    key={s.id}
                    type="button"
                    aria-pressed={form.requirements.some((r) => r.skill === s.id)}
                    onClick={() => toggle(s)}
                  >
                    {s.name}
                  </button>
                ))}
            </div>
          </DataState>
        </div>
        {form.requirements.length > 0 && (
          <div className="requirement-weights">
            {form.requirements.map((r) => (
              <div key={r.skill}>
                <span>{r.name}</span>
                <select
                  aria-label={`${r.name} importance`}
                  value={r.importance}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      requirements: form.requirements.map((item) =>
                        item.skill === r.skill ? { ...item, importance: e.target.value } : item,
                      ),
                    })
                  }
                >
                  <option value="essential">Essential (2 points)</option>
                  <option value="preferred">Preferred (1 point)</option>
                </select>
              </div>
            ))}
          </div>
        )}
        {error && (
          <p className="inline-error" role="alert">
            {error}
          </p>
        )}
        <div className="modal-actions">
          <Button variant="secondary" type="button" onClick={onClose} disabled={busy}>
            Cancel
          </Button>
          <Button type="submit" busy={busy}>
            {job ? 'Save changes' : 'Save job description'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}

export default function Jobs() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [editing, setEditing] = useState(null)
  const [remove, setRemove] = useState(null)
  const [busy, setBusy] = useState(false)
  const state = useData(`jobs/?page=${page}&search=${encodeURIComponent(search)}`)
  const notify = useToast()
  async function destroy() {
    setBusy(true)
    try {
      await api.delete(`jobs/${remove.id}/`)
      setRemove(null)
      setPage(1)
      state.reload()
      notify('Job and its related match analyses deleted.')
    } catch (err) {
      notify(errorMessage(err), 'error')
    } finally {
      setBusy(false)
    }
  }
  return (
    <>
      <PageHeading
        eyebrow="OPPORTUNITIES AHEAD"
        title="Job descriptions"
        description="Collect the roles that interest you. Understand what each one asks for."
        action={
          <Button onClick={() => setEditing({})}>
            <Plus size={18} />
            Add job description
          </Button>
        }
      />
      <div className="list-toolbar">
        <div className="search-input">
          <Search size={17} />
          <input
            aria-label="Search job descriptions"
            placeholder="Search roles or companies…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
          />
        </div>
        <span className="muted">{state.data?.count ?? 0} saved opportunities</span>
      </div>
      <DataState state={state}>
        {state.data?.results.length ? (
          <>
            <div className="job-grid">
              {state.data.results.map((job) => (
                <article className="panel job-card" key={job.id}>
                  <div className="job-card-top">
                    <span className="job-icon">
                      <BriefcaseBusiness size={22} />
                    </span>
                    <div className="job-card-buttons">
                      <button
                        aria-label={`Edit ${job.title}`}
                        className="icon-btn"
                        onClick={() => setEditing(job)}
                      >
                        <Pencil size={16} />
                      </button>
                      <button
                        aria-label={`Delete ${job.title}`}
                        className="icon-btn danger"
                        onClick={() => setRemove(job)}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                  <h2>{job.title}</h2>
                  <p className="company-line">
                    <Building2 size={14} />
                    {job.company || 'Company unspecified'}
                  </p>
                  <p className="job-description">{job.description}</p>
                  <div className="job-meta">
                    <Badge>
                      {job.experience_years == null
                        ? 'Experience unspecified'
                        : `${job.experience_years}+ years`}
                    </Badge>
                    {job.qualification && <Badge>{job.qualification}</Badge>}
                  </div>
                  <SkillTags
                    skills={job.requirements.map(
                      (r) => `${r.name}${r.importance === 'preferred' ? ' (preferred)' : ''}`,
                    )}
                  />
                  <div className="job-card-footer">
                    <small>Added {formatDate(job.created_at)}</small>
                    <Link className="text-link" to={`/matches?job=${job.id}`}>
                      Check my match <ArrowUpRight size={16} />
                    </Link>
                  </div>
                </article>
              ))}
            </div>
            <Pagination page={page} count={state.data.count} onPage={setPage} />
          </>
        ) : (
          <div className="panel">
            <EmptyState
              icon={BriefcaseBusiness}
              title={search ? 'No opportunities found' : 'What does your next role look like?'}
              description={
                search
                  ? 'Try another title, company or keyword.'
                  : 'Paste a job description to understand its requirements and compare your resume.'
              }
              action={
                !search && (
                  <Button onClick={() => setEditing({})}>
                    <Plus size={17} />
                    Add your first job
                  </Button>
                )
              }
            />
          </div>
        )}
      </DataState>
      {editing && (
        <JobForm
          job={editing.id ? editing : null}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null)
            state.reload()
            notify('Job description saved. Review the requirements before matching.')
          }}
        />
      )}{' '}
      {remove && (
        <Modal title="Delete this job?" onClose={() => setRemove(null)}>
          <p>
            “{remove.title}” and all its saved match and skill gap analyses will be permanently
            deleted.
          </p>
          <div className="modal-actions">
            <Button variant="secondary" disabled={busy} onClick={() => setRemove(null)}>
              Keep job
            </Button>
            <Button variant="danger" busy={busy} onClick={destroy}>
              Delete job
            </Button>
          </div>
        </Modal>
      )}
    </>
  )
}
