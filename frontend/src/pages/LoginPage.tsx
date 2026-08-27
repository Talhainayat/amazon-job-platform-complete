import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiError, login as loginApi } from '../services/api'
import { useAuth } from '../hooks/useAuth'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const res = await loginApi(email, password)
      await login(res.access_token, res.role)
      navigate(res.role === 'admin' ? '/admin' : '/dashboard')
    } catch (err) {
      setError(apiError(err, 'Invalid email or password'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrap">
      <div className="card auth-card">
        <h1>Welcome back</h1>
        <p className="lede">Sign in to manage jobs, matches, and applications.</p>
        <form onSubmit={handleSubmit} className="grid" style={{ marginTop: '1.2rem' }}>
          <label className="field">
            <span>Email</span>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label className="field">
            <span>Password</span>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>
          {error && <div className="alert error">{error}</div>}
          <button className="btn block" type="submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Log in'}
          </button>
        </form>
        <p className="notice" style={{ marginTop: '1rem' }}>
          New candidate? <Link to="/register">Create an account</Link>
        </p>
      </div>
    </div>
  )
}
