import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { ArrowRight, ArrowUpRight, ScanText, Compass, Check, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../auth'
import { errorMessage } from '../api'
import { Brand, Button, Field } from '../components/ui'
import { PUBLIC_DEMO } from '../config'

export default function Auth() {
  const { user, authenticate } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [register, setRegister] = useState(false)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  const [show, setShow] = useState(false)
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
  })
  if (user) return <Navigate to="/" replace />
  const change = (event) => setForm({ ...form, [event.target.name]: event.target.value })
  async function submit(event) {
    event.preventDefault()
    setBusy('form')
    setError('')
    try {
      await authenticate(register ? 'register' : 'login', form)
      navigate(location.state?.from || '/')
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy('')
    }
  }
  async function demo() {
    setBusy('demo')
    setError('')
    try {
      await authenticate('demo', {})
      navigate('/')
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy('')
    }
  }
  return (
    <div className="auth-page">
      <section className="auth-story">
        <Brand light />
        <div className="auth-story-body">
          <span className="auth-eyebrow">
            <span /> A CLEARER VIEW OF YOUR FUTURE
          </span>
          <h1>
            Your experience.
            <br />
            Your potential.
            <br />
            <span>In focus.</span>
          </h1>
          <p>
            Understand what your resume says.
            <br />
            See where your skills can take you.
          </p>
          <div className="auth-lens" aria-hidden="true">
            <div className="auth-orbit orbit-a" />
            <div className="auth-orbit orbit-b" />
            <div className="auth-orbit orbit-c" />
            <div className="lens-core">
              <Compass size={66} strokeWidth={1} />
            </div>
            <span className="floating-note note-a">
              <ScanText size={17} />
              Find your strengths
              <Check size={15} />
            </span>
            <span className="floating-note note-b">
              <Compass size={17} />
              Map your next move
              <ArrowUpRight size={15} />
            </span>
          </div>
        </div>
        <span className="auth-story-footer">Built for your next chapter.</span>
      </section>
      <section className="auth-form-side">
        <div className="auth-mobile-brand">
          <Brand />
        </div>
        <div className="auth-form-container">
          <span className="eyebrow">YOUR CAREER WORKSPACE</span>
          <h2>{register ? 'Make room for what’s next.' : 'Welcome to CareerLens.'}</h2>
          <p>
            {register
              ? 'Create an account and start with a clearer picture.'
              : 'A fresh perspective on your next opportunity.'}
          </p>
          <div className="auth-tabs">
            <button
              className={!register ? 'selected' : ''}
              onClick={() => {
                setRegister(false)
                setError('')
              }}
            >
              Sign in
            </button>
            <button
              className={register ? 'selected' : ''}
              onClick={() => {
                setRegister(true)
                setError('')
              }}
            >
              Create account
            </button>
          </div>
          <form onSubmit={submit}>
            {register && (
              <div className="form-grid">
                <Field label="First name">
                  <input
                    name="first_name"
                    autoComplete="given-name"
                    required
                    maxLength={150}
                    value={form.first_name}
                    onChange={change}
                  />
                </Field>
                <Field label="Last name">
                  <input
                    name="last_name"
                    autoComplete="family-name"
                    maxLength={150}
                    value={form.last_name}
                    onChange={change}
                  />
                </Field>
              </div>
            )}
            <Field label="Email address">
              <input
                type="email"
                name="email"
                placeholder="you@example.com"
                autoComplete="email"
                required
                maxLength={254}
                value={form.email}
                onChange={change}
              />
            </Field>
            <Field
              label="Password"
              hint={
                register
                  ? 'At least 10 characters. Avoid common passwords and your personal details.'
                  : undefined
              }
            >
              <span className="password-input">
                <input
                  type={show ? 'text' : 'password'}
                  name="password"
                  aria-label="Password"
                  placeholder={register ? 'Choose a secure password' : 'Enter your password'}
                  autoComplete={register ? 'new-password' : 'current-password'}
                  required
                  minLength={register ? 10 : 1}
                  maxLength={128}
                  value={form.password}
                  onChange={change}
                />
                <button
                  type="button"
                  aria-label={show ? 'Hide password' : 'Show password'}
                  onClick={() => setShow(!show)}
                >
                  {show ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </span>
            </Field>
            {error && (
              <p className="inline-error" role="alert">
                {error}
              </p>
            )}
            <Button className="full-width" type="submit" busy={busy === 'form'} disabled={!!busy}>
              {register ? 'Create my workspace' : 'Sign in to your workspace'}
              <ArrowRight size={17} />
            </Button>
          </form>
          <div className="auth-divider">
            <span>OR TAKE A LOOK AROUND</span>
          </div>
          <Button
            className="full-width demo-button"
            variant="secondary"
            busy={busy === 'demo'}
            disabled={!!busy}
            onClick={demo}
          >
            Explore sample workspace <ArrowUpRight size={17} />
          </Button>
          <p className="auth-fineprint">
            Explore with clearly labeled synthetic resumes and jobs.
            <br />
            {PUBLIC_DEMO
              ? 'Public demo: please use fictional candidate details.'
              : 'No account details or API key needed.'}
          </p>
          <div className="auth-trust">
            <Check size={14} />
            Private resume storage<span>·</span>
            <Check size={14} />
            Explainable scores
          </div>
        </div>
        <div className="auth-bottom">CareerLens · MCA academic project</div>
      </section>
    </div>
  )
}
