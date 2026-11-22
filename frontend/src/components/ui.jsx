import { createContext, useContext, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowUpRight, Check, X, AlertCircle, FileSearch, ChevronRight } from 'lucide-react'

const ToastContext = createContext(null)
export const useToast = () => useContext(ToastContext)
export function ToastProvider({ children }) {
  const [toast, setToast] = useState(null)
  const timer = useRef()
  function notify(message, type = 'success') {
    clearTimeout(timer.current)
    setToast({ message, type })
    timer.current = setTimeout(() => setToast(null), 6000)
  }
  useEffect(() => () => clearTimeout(timer.current), [])
  return (
    <ToastContext.Provider value={notify}>
      {children}
      {toast && (
        <div className={`toast ${toast.type}`} role={toast.type === 'error' ? 'alert' : 'status'}>
          {toast.type === 'error' ? <AlertCircle size={19} /> : <Check size={19} />}
          <span>{toast.message}</span>
          <button aria-label="Dismiss notification" onClick={() => setToast(null)}>
            <X size={16} />
          </button>
        </div>
      )}
    </ToastContext.Provider>
  )
}

export function Brand({ light = false }) {
  return (
    <Link to="/" className={`brand ${light ? 'light' : ''}`} aria-label="CareerLens home">
      <span className="brand-icon">
        <span />
        <span />
      </span>
      <span>
        Career<span className="brand-light">Lens</span>
        <i />
      </span>
    </Link>
  )
}
export function Button({ children, variant = 'primary', busy, className = '', ...props }) {
  return (
    <button
      className={`btn btn-${variant} ${className}`}
      disabled={busy || props.disabled}
      {...props}
    >
      {busy && <span className="spinner" />}
      {children}
    </button>
  )
}
export function PageHeading({ eyebrow, title, description, action }) {
  return (
    <div className="page-heading">
      <div>
        {eyebrow && <div className="eyebrow">{eyebrow}</div>}
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {action}
    </div>
  )
}
export function SectionTitle({ title, subtitle, to, label = 'View all' }) {
  return (
    <div className="section-title">
      <div>
        <h2>{title}</h2>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {to && (
        <Link className="text-link" to={to}>
          {label}
          <ArrowUpRight size={15} />
        </Link>
      )}
    </div>
  )
}
export function Badge({ children, variant = 'neutral' }) {
  return <span className={`badge badge-${variant}`}>{children}</span>
}
export function SkillTags({ skills, variant = 'green' }) {
  return (
    <div className="skill-tags">
      {skills.map((s, i) => (
        <span className={`tag tag-${variant}`} key={typeof s === 'string' ? s : s.skill_id || i}>
          {typeof s === 'string' ? s : s.name}
        </span>
      ))}
    </div>
  )
}
export function EmptyState({ icon: Icon = FileSearch, title, description, to, label, action }) {
  return (
    <div className="empty-state">
      <span className="empty-icon">
        <Icon size={28} strokeWidth={1.5} />
      </span>
      <h3>{title}</h3>
      <p>{description}</p>
      {to ? (
        <Link to={to} className="btn btn-primary">
          {label}
          <ChevronRight size={16} />
        </Link>
      ) : (
        action
      )}
    </div>
  )
}
export function ErrorState({ message, onRetry }) {
  return (
    <div className="error-state" role="alert">
      <AlertCircle size={20} />
      <p>{message}</p>
      {onRetry && (
        <Button variant="secondary" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  )
}
export function Loading() {
  return (
    <div className="loading-state" role="status">
      <span className="spinner" />
      Loading your records…
    </div>
  )
}
export function DataState({ state, children }) {
  if (state.loading) return <Loading />
  if (state.error) return <ErrorState message={state.error} onRetry={state.reload} />
  return children
}
export function Modal({ title, children, onClose, wide = false }) {
  const ref = useRef()
  useEffect(() => {
    ref.current.showModal()
    const dialog = ref.current
    const onCancel = (event) => {
      event.preventDefault()
      onClose()
    }
    dialog.addEventListener('cancel', onCancel)
    return () => {
      dialog.removeEventListener('cancel', onCancel)
      dialog.close()
    }
  }, [onClose])
  return (
    <dialog ref={ref} className={`modal ${wide ? 'modal-wide' : ''}`} aria-labelledby="modal-title">
      <div className="modal-heading">
        <h2 id="modal-title">{title}</h2>
        <button className="icon-btn" onClick={onClose} aria-label="Close dialog">
          <X size={20} />
        </button>
      </div>
      {children}
    </dialog>
  )
}
export function Field({ label, children, hint }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
      {hint && <small>{hint}</small>}
    </label>
  )
}
export function ScoreRing({ score, label = 'Resume quality', size = 100 }) {
  const clamped = Math.max(0, Math.min(100, Number(score) || 0))
  return (
    <div
      className="score-ring"
      style={{ width: size, height: size }}
      role="img"
      aria-label={`${label}: ${clamped} out of 100`}
    >
      <svg viewBox="0 0 100 100" aria-hidden="true">
        <circle
          cx="50"
          cy="50"
          r="43"
          fill="none"
          stroke="currentColor"
          className="ring-track"
          strokeWidth="7"
        />
        <circle
          cx="50"
          cy="50"
          r="43"
          fill="none"
          stroke="currentColor"
          strokeWidth="7"
          strokeLinecap="round"
          strokeDasharray={`${clamped * 2.702} 270.2`}
          transform="rotate(-90 50 50)"
        />
      </svg>
      <span>
        {clamped}
        <small>/ 100</small>
      </span>
    </div>
  )
}
export function Pagination({ page, count, onPage }) {
  const total = Math.ceil(count / 20)
  if (total < 2) return null
  return (
    <div className="pagination">
      <span>
        {count} records · Page {page} of {total}
      </span>
      <Button variant="secondary" disabled={page === 1} onClick={() => onPage(page - 1)}>
        Previous
      </Button>
      <Button variant="secondary" disabled={page === total} onClick={() => onPage(page + 1)}>
        Next
      </Button>
    </div>
  )
}
export const formatDate = (value) =>
  new Intl.DateTimeFormat('en-IN', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(value))
