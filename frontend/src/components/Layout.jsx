import { useState } from 'react'
import { NavLink, Outlet, Link } from 'react-router-dom'
import {
  LayoutDashboard,
  Files,
  ScanText,
  BriefcaseBusiness,
  GitCompareArrows,
  ChartNoAxesCombined,
  Compass,
  History,
  Settings2,
  ShieldCheck,
  LogOut,
  Menu,
  X,
  ArrowUpRight,
  CircleHelp,
  ChevronDown,
} from 'lucide-react'
import { useAuth } from '../auth'
import { Brand, useToast } from './ui'
import { PUBLIC_DEMO } from '../config'

const primary = [
  ['/', 'Overview', LayoutDashboard],
  ['/resumes', 'My resumes', Files],
  ['/analysis', 'Resume analysis', ScanText],
  ['/jobs', 'Job descriptions', BriefcaseBusiness],
  ['/matches', 'Job match', GitCompareArrows],
  ['/gaps', 'Skill gap analysis', ChartNoAxesCombined],
  ['/careers', 'Career pathways', Compass],
  ['/history', 'Analysis history', History],
]

export default function Layout() {
  const { user, logout } = useAuth()
  const notify = useToast()
  const [open, setOpen] = useState(false)
  const sample = user.headline?.includes('Sample workspace')
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      {open && (
        <button
          aria-label="Close navigation overlay"
          className="sidebar-overlay"
          onClick={() => setOpen(false)}
        />
      )}
      <aside className={`sidebar ${open ? 'sidebar-open' : ''}`}>
        <div className="sidebar-brand">
          <Brand />
          <button
            className="mobile-only icon-btn"
            aria-label="Close navigation"
            onClick={() => setOpen(false)}
          >
            <X size={20} />
          </button>
        </div>
        <div className="workspace-tag">
          <span className="workspace-mark">P</span>
          <div>
            Personal workspace
            <small>{sample ? 'Sample account' : 'Career explorer'}</small>
          </div>
          <ChevronDown size={14} />
        </div>
        <div className="nav-label">YOUR WORKSPACE</div>
        <nav aria-label="Main navigation">
          {primary.map(([to, label, Icon]) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setOpen(false)}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={19} strokeWidth={1.7} />
              <span>{label}</span>
              {to === '/careers' && <span className="tiny-dot" />}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-tip">
            <span className="tip-icon">
              <Compass size={21} />
            </span>
            <h3>Small steps. Real progress.</h3>
            <p>Your next opportunity starts with understanding your strengths.</p>
            <Link to="/methodology">
              How scoring works <ArrowUpRight size={14} />
            </Link>
          </div>
          <NavLink to="/profile" className="nav-item" onClick={() => setOpen(false)}>
            <Settings2 size={18} />
            My profile
          </NavLink>
          {user.is_staff && (
            <NavLink to="/admin" className="nav-item">
              <ShieldCheck size={18} />
              Administration
            </NavLink>
          )}
          <div className="sidebar-user">
            <Link to="/profile" className="user-details">
              <span className="avatar">
                {user.first_name?.[0] || 'U'}
                {user.last_name?.[0] || ''}
              </span>
              <div>
                <strong>
                  {user.first_name} {user.last_name}
                </strong>
                <small>{sample ? 'Sample workspace' : 'Personal account'}</small>
              </div>
            </Link>
            <button
              className="icon-btn"
              aria-label="Sign out"
              title="Sign out"
              onClick={() => logout().catch(() => notify('Your local session has ended.', 'error'))}
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </aside>
      <div className="workspace-main">
        <header className="topbar">
          <div>
            <button
              className="icon-btn mobile-only"
              aria-label="Open navigation"
              onClick={() => setOpen(true)}
            >
              <Menu size={22} />
            </button>
            <span className="breadcrumb">
              Workspace<span>/</span>
              <strong>Career explorer</strong>
            </span>
          </div>
          <div className="topbar-actions">
            <span className="engine-indicator">
              <span />
              Evidence-based analysis
            </span>
            <Link to="/methodology" className="icon-btn" aria-label="About analysis scores">
              <CircleHelp size={19} />
            </Link>
            <Link to="/profile" className="avatar avatar-small" aria-label="Open profile">
              {user.first_name?.[0] || 'U'}
            </Link>
          </div>
        </header>
        {sample && (
          <div className="sample-banner">
            <span>Sample workspace</span> All resumes, jobs and candidate details here are synthetic
            demonstration data.{' '}
            {PUBLIC_DEMO
              ? 'Please use synthetic resumes in this public demo.'
              : 'Stored in your local database.'}
          </div>
        )}
        <main id="main-content" className="main-content">
          <Outlet />
        </main>
        <footer className="app-footer">
          <span>
            CareerLens <span className="footer-dot">·</span> A little clarity for your next chapter.
          </span>
          <Link to="/methodology">
            Transparent by design <ArrowUpRight size={12} />
          </Link>
        </footer>
      </div>
    </div>
  )
}
