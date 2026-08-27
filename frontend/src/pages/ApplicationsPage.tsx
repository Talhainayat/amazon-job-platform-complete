import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Application, apiError, applicationsApi } from '../services/api'

export default function ApplicationsPage() {
  const { candidateId } = useAuth()
  const [items, setItems] = useState<Application[]>([])
  const [error, setError] = useState<string | null>(null)

  const load = () => {
    if (!candidateId) return
    applicationsApi.listForCandidate(candidateId).then(setItems).catch((err) => setError(apiError(err)))
  }

  useEffect(() => {
    load()
  }, [candidateId])

  const withdraw = async (app: Application) => {
    if (!window.confirm('Withdraw this application?')) return
    await applicationsApi.update(app.id, { status: 'withdrawn' })
    load()
  }

  return (
    <div className="page">
      <h1>Your applications</h1>
      <p className="lede">Track status, interviews, and outcomes.</p>
      {error && <div className="alert error">{error}</div>}
      {items.length === 0 && <div className="card empty">No applications yet. Browse jobs and apply when you are ready.</div>}
      <div className="grid" style={{ marginTop: '1rem' }}>
        {items.map((app) => (
          <div className="card" key={app.id}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
              <div>
                <Link to={`/jobs/${app.job_id}`}><strong>{app.job?.title || `Job #${app.job_id}`}</strong></Link>
                <div className="notice">{app.job?.company} · {app.job?.location}</div>
                <div className="notice">Applied {app.applied_at ? new Date(app.applied_at).toLocaleDateString() : '—'}</div>
              </div>
              <span className={`badge ${app.status}`}>{app.status.replace('_', ' ')}</span>
            </div>
            {app.interview_date && <p>Interview: {new Date(app.interview_date).toLocaleString()}</p>}
            {app.status !== 'withdrawn' && app.status !== 'hired' && app.status !== 'rejected' && (
              <button className="btn ghost" type="button" onClick={() => withdraw(app)}>Withdraw</button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
