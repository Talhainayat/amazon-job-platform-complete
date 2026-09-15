import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Application, Job, apiError, applicationsApi, jobsApi, payLabel } from '../services/api'
import LazyImage from '../components/LazyImage'

export default function JobDetailPage() {
  const { jobId } = useParams()
  const { role, candidateId } = useAuth()
  const [job, setJob] = useState<Job | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [status, setStatus] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const load = () => {
    if (!jobId) return
    jobsApi.get(Number(jobId)).then(setJob).catch((err) => setError(apiError(err, 'Job not found')))
  }

  useEffect(() => {
    load()
  }, [jobId])

  const apply = async () => {
    if (!job) return
    
    const externalUrl = job.external_url || (job.is_custom ? job.application_url : undefined)
    if (externalUrl) {
      setBusy(true)
      setStatus(null)
      try {
        await jobsApi.applyExternal(job.id)
      } catch {
        // The destination can still be opened when a tracking request is unavailable.
      }
      window.open(externalUrl, '_blank', 'noopener,noreferrer')
      setStatus('Application started on the official site.')
      setBusy(false)
      return
    }
    
    // For standard jobs, create an application record
    setBusy(true)
    setStatus(null)
    try {
      await applicationsApi.create(job.id, candidateId || undefined)
      setStatus('Application submitted.')
      load()
    } catch (err) {
      setStatus(apiError(err, 'Could not apply'))
    } finally {
      setBusy(false)
    }
  }

  const withdraw = async () => {
    if (!job || !candidateId) return
    if (!window.confirm('Withdraw this application?')) return
    setBusy(true)
    try {
      const apps = await applicationsApi.listForCandidate(candidateId)
      const mine = apps.find((a: Application) => a.job_id === job.id && a.status !== 'withdrawn')
      if (!mine) return
      await applicationsApi.update(mine.id, { status: 'withdrawn' })
      load()
    } catch (err) {
      setStatus(apiError(err, 'Could not withdraw'))
    } finally {
      setBusy(false)
    }
  }

  if (error) return <div className="page"><div className="alert error">{error}</div></div>
  if (!job) return <div className="page"><div className="skeleton" /></div>

  const applied = Boolean(job.already_applied)

  return (
    <div className="page">
      <Link to="/jobs">← All jobs</Link>
      <div className="page-header" style={{ marginTop: '0.8rem' }}>
        <div>
          <h1>{job.title}</h1>
          <div className="job-meta">
            <span>{job.company || 'Hiring company'}</span>
            <span>{[job.city || job.location, job.province, job.postal_code].filter(Boolean).join(', ')}</span>
            <span>{payLabel(job)}</span>
            <span className={`badge ${job.status}`}>{job.status}</span>
            {job.is_custom && job.badge_status && (
              <span
                className="badge"
                style={{
                  backgroundColor: job.badge_status === 'urgent' ? '#dc2626' : '#16a34a',
                  color: 'white'
                }}
              >
                {job.badge_status === 'urgent' ? '🔴 URGENT' : '● LIVE'}
              </span>
            )}
          </div>
        </div>
        {typeof job.match_score === 'number' && (
          <div className="match" style={{ ['--p' as string]: job.match_score }}>
            <span>{Math.round(job.match_score)}%</span>
          </div>
        )}
      </div>
      {job.image_url && (
        <div className="job-image-banner">
          <LazyImage
            src={job.image_url}
            alt={job.title}
            fallback="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 800 300%22%3E%3Crect fill=%22%23e2e8f0%22 width=%22800%22 height=%22300%22/%3E%3C/svg%3E"
          />
        </div>
      )}
      <div className="grid grid-2">
        <div className="card">
          <h2>About this role</h2>
          <p>{job.description || 'No description provided yet.'}</p>
          <h2>Requirements</h2>
          <p>{job.requirements || 'See skills and experience below.'}</p>
          <div className="job-meta">
            <span>Type: {job.job_type || '—'}</span>
            <span>Shift: {job.shift || '—'}</span>
            <span>Experience: {job.years_experience ?? 0}+ years</span>
            <span>Openings: {job.openings ?? 1}</span>
            <span>Deadline: {job.application_deadline ? new Date(job.application_deadline).toLocaleDateString() : 'Open'}</span>
          </div>
          <p><strong>Skills:</strong> {(job.skills || []).join(', ') || 'Not specified'}</p>
        </div>
        <div className="card">
          <h2>Why this match</h2>
          {job.match_explanation && job.match_explanation.length > 0 ? (
            <ul className="why">
              {job.match_explanation.map((item) => <li key={item}>{item}</li>)}
            </ul>
          ) : (
            <p className="notice">Sign in as a candidate with a complete profile to see a personalized match score.</p>
          )}
          {job.distance_known && job.distance_km != null && (
            <p className="notice">Estimated distance: {job.distance_km} km</p>
          )}
          {role === 'candidate' && job.status === 'open' && (
            applied && !job.is_custom ? (
              <div>
                <button className="btn secondary block" type="button" disabled>Already applied</button>
                <p className="notice">Status: {job.application_status}</p>
                <button className="btn ghost block" type="button" onClick={withdraw} disabled={busy}>Withdraw</button>
              </div>
            ) : (
              <button className="btn block" type="button" onClick={apply} disabled={busy}>
                {job.external_url || job.is_custom ? 'Apply on Official Site ↗' : 'Quick Apply'}
              </button>
            )
          )}
          {role === 'admin' && <Link className="btn secondary block" to={`/admin/jobs/${job.id}/edit`}>Edit job</Link>}
          {status && <div className="alert info">{status}</div>}
        </div>
      </div>
    </div>
  )
}
