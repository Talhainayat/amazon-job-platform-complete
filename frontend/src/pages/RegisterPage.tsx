import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import confetti from 'canvas-confetti'
import { motion } from 'framer-motion'
import { apiError, registerCandidate } from '../services/api'
import { useAuth } from '../hooks/useAuth'

export default function RegisterPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [phone, setPhone] = useState('')
  const [location, setLocation] = useState('')
  const [postalCode, setPostalCode] = useState('')
  const [shift, setShift] = useState('')
  const [eligibility, setEligibility] = useState('')
  const [portalLink, setPortalLink] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    if (password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }
    setLoading(true)
    try {
      const res = await registerCandidate({ name, email, password, phone, location, postal_code: postalCode, preferred_shift: shift, work_eligibility: eligibility, amazon_portal_link: portalLink })
      await login(res.access_token, res.role)
      confetti({
        particleCount: 120,
        spread: 80,
        origin: { y: 0.65 },
        colors: ['#ffb000', '#146ef5', '#16a34a'],
        disableForReducedMotion: true,
      })
      navigate('/profile')
    } catch (err) {
      setError(apiError(err, 'Could not create your account'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrap">
      <motion.div
        className="card auth-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45, ease: 'easeOut' }}
      >
        <h1>Create your profile</h1>
        <p className="lede">Candidates can search jobs, see match scores, and apply in minutes.</p>
        <form onSubmit={handleSubmit} className="grid" style={{ marginTop: '1.2rem' }}>
          <label className="field">
            <span>Full name</span>
            <input value={name} onChange={(e) => setName(e.target.value)} required minLength={2} />
          </label>
          <label className="field">
            <span>Email</span>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label className="field">
            <span>Password</span>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
          </label>
          <label className="field">
            <span>Phone</span>
            <input value={phone} onChange={(e) => setPhone(e.target.value)} />
          </label>
          <label className="field">
            <span>City / location</span>
            <input value={location} onChange={(e) => setLocation(e.target.value)} />
          </label>
          <label className="field"><span>Target ZIP / postal code</span><input value={postalCode} onChange={(e) => setPostalCode(e.target.value)} /></label>
          <label className="field"><span>Preferred shift</span><input value={shift} onChange={(e) => setShift(e.target.value)} placeholder="Day, night, or rotating" /></label>
          <label className="field"><span>Work eligibility</span><input value={eligibility} onChange={(e) => setEligibility(e.target.value)} /></label>
          <label className="field"><span>Amazon portal link</span><input type="url" value={portalLink} onChange={(e) => setPortalLink(e.target.value)} /></label>
          {error && <div className="alert error">{error}</div>}
          <button className="btn block" type="submit" disabled={loading}>
            {loading ? (
              <span style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                <motion.span
                  aria-hidden="true"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
                  style={{ width: 14, height: 14, border: '2px solid rgba(255,255,255,0.45)', borderTopColor: '#fff', borderRadius: '50%' }}
                />
                Creating account…
              </span>
            ) : 'Create account'}
          </button>
        </form>
        <p className="notice" style={{ marginTop: '1rem' }}>
          Already registered? <Link to="/login">Log in</Link>
        </p>
      </motion.div>
    </div>
  )
}
