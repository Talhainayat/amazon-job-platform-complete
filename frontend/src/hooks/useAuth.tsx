import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { Role, logoutApi, me as fetchMe } from '../services/api'

interface AuthState {
  token: string | null
  role: Role | null
  candidateId: number | null
  email: string | null
  name: string | null
  ready: boolean
  login: (token: string, role: Role) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthState | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'))
  const [role, setRole] = useState<Role | null>(localStorage.getItem('role') as Role | null)
  const [candidateId, setCandidateId] = useState<number | null>(
    localStorage.getItem('candidate_id') ? Number(localStorage.getItem('candidate_id')) : null
  )
  const [email, setEmail] = useState<string | null>(localStorage.getItem('email'))
  const [name, setName] = useState<string | null>(localStorage.getItem('name'))
  const [ready, setReady] = useState(false)

  const hydrate = async (existingToken: string) => {
    try {
      const profile = await fetchMe()
      setRole(profile.role)
      setEmail(profile.email)
      setName(profile.name || null)
      localStorage.setItem('role', profile.role)
      localStorage.setItem('email', profile.email)
      if (profile.candidate_id) {
        localStorage.setItem('candidate_id', String(profile.candidate_id))
        setCandidateId(profile.candidate_id)
      }
      if (profile.name) localStorage.setItem('name', profile.name)
    } catch {
      localStorage.removeItem('access_token')
      setToken(null)
      setRole(null)
    } finally {
      setReady(true)
    }
  }

  useEffect(() => {
    if (token) hydrate(token)
    else setReady(true)
  }, [])

  const login = async (newToken: string, newRole: Role) => {
    localStorage.setItem('access_token', newToken)
    localStorage.setItem('role', newRole)
    setToken(newToken)
    setRole(newRole)
    await hydrate(newToken)
  }

  const logout = async () => {
    await logoutApi()
    localStorage.removeItem('access_token')
    localStorage.removeItem('role')
    localStorage.removeItem('candidate_id')
    localStorage.removeItem('email')
    localStorage.removeItem('name')
    setToken(null)
    setRole(null)
    setCandidateId(null)
    setEmail(null)
    setName(null)
  }

  return (
    <AuthContext.Provider value={{ token, role, candidateId, email, name, ready, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
