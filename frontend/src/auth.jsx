import { createContext, useContext, useState, useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { api } from './api'

const AuthContext = createContext(null)
export const useAuth = () => useContext(AuthContext)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  function clearSession() {
    sessionStorage.removeItem('careerlens-token')
    setUser(null)
  }
  useEffect(() => {
    if (sessionStorage.getItem('careerlens-token')) {
      api
        .get('auth/me/')
        .then(({ data }) => setUser(data))
        .catch(clearSession)
        .finally(() => setLoading(false))
    } else setLoading(false)
    window.addEventListener('careerlens-session-expired', clearSession)
    return () => window.removeEventListener('careerlens-session-expired', clearSession)
  }, [])
  async function authenticate(path, values) {
    const { data } = await api.post(`auth/${path}/`, values)
    sessionStorage.setItem('careerlens-token', data.token)
    setUser(data.user)
    return data.user
  }
  async function logout() {
    try {
      await api.post('auth/logout/')
    } finally {
      clearSession()
    }
  }
  return (
    <AuthContext.Provider value={{ user, setUser, loading, authenticate, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function Protected({ children }) {
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading)
    return (
      <div className="screen-loader">
        <span className="spinner" />
        Opening your workspace…
      </div>
    )
  return user ? children : <Navigate to="/login" state={{ from: location.pathname }} replace />
}
