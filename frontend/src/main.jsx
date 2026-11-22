import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import '@fontsource/manrope/400.css'
import '@fontsource/manrope/500.css'
import '@fontsource/manrope/600.css'
import '@fontsource/manrope/700.css'
import '@fontsource/manrope/800.css'
import '@fontsource/dm-sans/400.css'
import '@fontsource/dm-sans/500.css'
import '@fontsource/dm-sans/600.css'
import './styles.css'
import { AuthProvider, Protected } from './auth'
import { ToastProvider, EmptyState } from './components/ui'
import Layout from './components/Layout'
import Auth from './pages/Auth'
import Dashboard from './pages/Dashboard'
import Resumes from './pages/Resumes'
import Analysis from './pages/Analysis'
import Jobs from './pages/Jobs'
import Matching, { Gaps } from './pages/Matching'
import Careers from './pages/Careers'
import { History, Profile, Admin, Methodology } from './pages/Account'

class ErrorBoundary extends React.Component {
  state = { failed: false }
  static getDerivedStateFromError() {
    return { failed: true }
  }
  render() {
    return this.state.failed ? (
      <div className="fatal-error">
        <h1>Let’s reopen your workspace.</h1>
        <p>
          Something unexpected interrupted the page. Your saved records are still in your account.
        </p>
        <button className="btn btn-primary" onClick={() => window.location.assign('/')}>
          Reopen CareerLens
        </button>
      </div>
    ) : (
      this.props.children
    )
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <ToastProvider>
            <Routes>
              <Route path="/login" element={<Auth />} />
              <Route
                element={
                  <Protected>
                    <Layout />
                  </Protected>
                }
              >
                <Route index element={<Dashboard />} />
                <Route path="resumes" element={<Resumes />} />
                <Route path="analysis" element={<Analysis />} />
                <Route path="jobs" element={<Jobs />} />
                <Route path="matches" element={<Matching />} />
                <Route path="gaps" element={<Gaps />} />
                <Route path="careers" element={<Careers />} />
                <Route path="history" element={<History />} />
                <Route path="profile" element={<Profile />} />
                <Route path="admin" element={<Admin />} />
                <Route path="methodology" element={<Methodology />} />
                <Route
                  path="*"
                  element={
                    <EmptyState
                      title="This page is out of focus"
                      description="Return to your workspace to keep exploring."
                      to="/"
                      label="Back to overview"
                    />
                  }
                />
              </Route>
            </Routes>
          </ToastProvider>
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>,
)
