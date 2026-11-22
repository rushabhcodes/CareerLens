import { useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  UploadCloud,
  Plus,
  FileText,
  ArrowUpRight,
  Trash2,
  Download,
  Search,
  CheckCircle2,
} from 'lucide-react'
import { api, downloadFile, errorMessage } from '../api'
import { useData } from '../hooks'
import { MAX_UPLOAD_MIB } from '../config'
import {
  Badge,
  Button,
  DataState,
  EmptyState,
  Field,
  Modal,
  PageHeading,
  Pagination,
  ScoreRing,
  SkillTags,
  formatDate,
  useToast,
} from '../components/ui'

export function UploadModal({ onClose, onUploaded }) {
  const [file, setFile] = useState(null)
  const [title, setTitle] = useState('')
  const [dragging, setDragging] = useState(false)
  const [progress, setProgress] = useState(0)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const input = useRef()
  function choose(selected) {
    setError('')
    if (!selected) return
    if (!/\.(pdf|docx)$/i.test(selected.name)) return setError('Choose a PDF or DOCX file.')
    if (selected.size > MAX_UPLOAD_MIB * 1024 * 1024)
      return setError(`Your resume must be ${MAX_UPLOAD_MIB} MiB or smaller.`)
    setFile(selected)
    if (!title) setTitle(selected.name.replace(/\.(pdf|docx)$/i, '').slice(0, 160))
  }
  async function submit(event) {
    event.preventDefault()
    if (!file) return setError('Choose a resume to upload.')
    const data = new FormData()
    data.append('file', file)
    data.append('title', title)
    setBusy(true)
    setError('')
    try {
      const result = await api.post('resumes/', data, {
        onUploadProgress: (event) =>
          setProgress(Math.round((100 * event.loaded) / (event.total || file.size))),
      })
      onUploaded(result.data)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }
  return (
    <Modal title="Bring your experience into focus" onClose={onClose}>
      <p className="modal-description">
        Upload a text-based resume. We’ll extract what’s there and explain what could be stronger.
      </p>
      <form onSubmit={submit}>
        <input
          ref={input}
          className="visually-hidden"
          type="file"
          accept=".pdf,.docx"
          aria-label="Choose resume file"
          onChange={(e) => choose(e.target.files[0])}
        />
        <button
          type="button"
          className={`upload-dropzone ${dragging ? 'dragging' : ''}`}
          onClick={() => input.current.click()}
          onDragOver={(e) => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault()
            setDragging(false)
            choose(e.dataTransfer.files[0])
          }}
        >
          <span className="upload-icon">
            {file ? <CheckCircle2 size={30} /> : <UploadCloud size={32} />}
          </span>
          <strong>{file ? file.name : 'Drop your resume here, or browse'}</strong>
          <span>
            {file
              ? `${(file.size / 1024).toFixed(1)} KB · Click to choose another file`
              : `PDF or DOCX · Up to ${MAX_UPLOAD_MIB} MiB · Maximum 30 PDF pages`}
          </span>
        </button>
        <Field label="Resume title">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={160}
            placeholder="e.g. Full-stack developer resume"
          />
        </Field>
        {busy && (
          <div className="upload-progress" role="status">
            <div className="bar-track">
              <span style={{ width: `${progress}%` }} />
            </div>
            <span>
              {progress < 100
                ? `Uploading ${progress}%`
                : 'Upload complete. Reading and analyzing your resume…'}
            </span>
          </div>
        )}
        {error && (
          <p className="inline-error" role="alert">
            {error}
          </p>
        )}
        <p className="privacy-note">
          Your original file is private. Scanned PDFs need OCR, which is not configured.
        </p>
        <div className="modal-actions">
          <Button type="button" variant="secondary" onClick={onClose} disabled={busy}>
            Cancel
          </Button>
          <Button type="submit" busy={busy}>
            Upload & analyze <ArrowUpRight size={16} />
          </Button>
        </div>
      </form>
    </Modal>
  )
}

export default function Resumes() {
  const [params, setParams] = useSearchParams()
  const [upload, setUpload] = useState(params.has('upload'))
  const [remove, setRemove] = useState(null)
  const [busy, setBusy] = useState(false)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const notify = useToast()
  const state = useData(`resumes/?page=${page}&search=${encodeURIComponent(search)}`)
  function closeUpload() {
    setUpload(false)
    setParams({})
  }
  async function destroy() {
    setBusy(true)
    try {
      await api.delete(`resumes/${remove.id}/`)
      notify('Resume and its related analyses deleted.')
      setRemove(null)
      if (page > 1) setPage(1)
      else state.reload()
    } catch (err) {
      notify(errorMessage(err), 'error')
    } finally {
      setBusy(false)
    }
  }
  return (
    <>
      <PageHeading
        eyebrow="YOUR PROFESSIONAL STORY"
        title="My resumes"
        description="Keep every version organized. Make each one a little stronger."
        action={
          <Button onClick={() => setUpload(true)}>
            <Plus size={18} />
            Upload resume
          </Button>
        }
      />
      <div className="list-toolbar">
        <div className="search-input">
          <Search size={17} />
          <input
            aria-label="Search resumes"
            placeholder="Search your resumes…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
          />
        </div>
        <span className="muted">
          {state.data?.count ?? 0} resume{state.data?.count === 1 ? '' : 's'}
        </span>
      </div>
      <DataState state={state}>
        {state.data?.results.length ? (
          <>
            <div className="resume-grid">
              {state.data.results.map((r) => (
                <article className="panel resume-card" key={r.id}>
                  <div className="resume-card-top">
                    <span className="document-icon">
                      <FileText size={26} />
                      <small>{r.original_filename.split('.').pop().toUpperCase()}</small>
                    </span>
                    <Badge variant="green">Analyzed</Badge>
                  </div>
                  <h2>{r.title}</h2>
                  <p className="file-name">{r.original_filename}</p>
                  <div className="resume-card-score">
                    <ScoreRing score={r.quality_score} size={80} />
                    <div>
                      <strong>Resume quality</strong>
                      <p>
                        {r.skill_evidence.length} skills detected
                        <br />
                        {r.quality_report.missing_sections.length} missing sections
                      </p>
                    </div>
                  </div>
                  <SkillTags skills={r.skill_evidence.slice(0, 4).map((s) => s.skill.name)} />
                  <div className="resume-card-meta">
                    <span>{formatDate(r.created_at)}</span>
                    <span>{(r.file_size / 1024).toFixed(0)} KB</span>
                  </div>
                  <div className="resume-card-actions">
                    <Link to={`/analysis?resume=${r.id}`} className="text-link">
                      View analysis <ArrowUpRight size={16} />
                    </Link>
                    <div>
                      <button
                        className="icon-btn"
                        aria-label={`Download ${r.title}`}
                        onClick={() =>
                          downloadFile(`resumes/${r.id}/download/`, r.original_filename).catch(
                            (err) => notify(errorMessage(err), 'error'),
                          )
                        }
                      >
                        <Download size={17} />
                      </button>
                      <button
                        className="icon-btn danger"
                        aria-label={`Delete ${r.title}`}
                        onClick={() => setRemove(r)}
                      >
                        <Trash2 size={17} />
                      </button>
                    </div>
                  </div>
                </article>
              ))}
            </div>
            <Pagination page={page} count={state.data.count} onPage={setPage} />
          </>
        ) : (
          <div className="panel">
            <EmptyState
              title={
                search
                  ? 'No resumes match your search'
                  : 'A fresh perspective starts with your resume'
              }
              description={
                search
                  ? 'Try another title or filename.'
                  : 'Upload a PDF or DOCX to discover your skills and get an explainable quality report.'
              }
              action={
                !search && (
                  <Button onClick={() => setUpload(true)}>
                    <UploadCloud size={18} />
                    Upload your first resume
                  </Button>
                )
              }
            />
          </div>
        )}
      </DataState>
      {upload && (
        <UploadModal
          onClose={closeUpload}
          onUploaded={() => {
            closeUpload()
            state.reload()
            notify('Resume uploaded and analyzed. Your report is ready.')
          }}
        />
      )}{' '}
      {remove && (
        <Modal title="Delete this resume?" onClose={() => setRemove(null)}>
          <p>
            “{remove.title}” and its match results, career recommendations and analysis history will
            be permanently deleted.
          </p>
          <div className="modal-actions">
            <Button variant="secondary" disabled={busy} onClick={() => setRemove(null)}>
              Keep resume
            </Button>
            <Button variant="danger" busy={busy} onClick={destroy}>
              Delete resume
            </Button>
          </div>
        </Modal>
      )}
    </>
  )
}
