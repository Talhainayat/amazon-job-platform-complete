import { FormEvent, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Application, Candidate, apiError, applicationsApi, candidatesApi } from '../services/api'

export default function AdminCandidateDetailPage() {
  const { candidateId } = useParams()
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [apps, setApps] = useState<Application[]>([])
  const [overview, setOverview] = useState<any>(null)
  const [status, setStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!candidateId) return
    const id = Number(candidateId)
    Promise.all([candidatesApi.get(id), applicationsApi.listForCandidate(id), candidatesApi.overview(id)])
      .then(([c, a, o]) => {
        setCandidate(c)
        setApps(a)
        setOverview(o)
      })
      .catch((err) => setError(apiError(err)))
  }, [candidateId])

  if (error) return <div className="page"><div className="alert error">{error}</div></div>
  if (!candidate) return <div className="page"><div className="skeleton" /></div>

  const saveCandidate = async (event: FormEvent) => {
    event.preventDefault()
    try {
      const saved = await candidatesApi.update(candidate.id, {
        name: candidate.name,
        phone: candidate.phone,
        postal_code: candidate.postal_code,
        preferred_shift: candidate.preferred_shift,
        work_eligibility: candidate.work_eligibility,
        amazon_portal_link: candidate.amazon_portal_link,
      })
      setCandidate(saved)
      setStatus('Candidate saved.')
    } catch (err) {
      setStatus(apiError(err, 'Could not save candidate'))
    }
  }

  return (
    <div className="page">
      <h1>{candidate.name}</h1>
      <p className="lede">{candidate.email} · {candidate.phone || 'No phone'} · {candidate.location || 'No location'}</p>
      {status && <div className="alert success">{status}</div>}
      <div className="grid grid-2">
        <div className="card">
          <h2>Edit candidate</h2>
          <form className="grid" onSubmit={saveCandidate}>
            <label className="field"><span>Full name</span><input value={candidate.name} onChange={(e) => setCandidate({ ...candidate, name: e.target.value })} required /></label>
            <label className="field"><span>Phone</span><input value={candidate.phone || ''} onChange={(e) => setCandidate({ ...candidate, phone: e.target.value })} /></label>
            <label className="field"><span>Target ZIP / postal code</span><input value={candidate.postal_code || ''} onChange={(e) => setCandidate({ ...candidate, postal_code: e.target.value })} /></label>
            <label className="field"><span>Preferred shift</span><input value={candidate.preferred_shift || ''} onChange={(e) => setCandidate({ ...candidate, preferred_shift: e.target.value })} /></label>
            <label className="field"><span>Work eligibility</span><input value={candidate.work_eligibility || ''} onChange={(e) => setCandidate({ ...candidate, work_eligibility: e.target.value })} /></label>
            <label className="field"><span>Amazon portal link</span><input type="url" value={candidate.amazon_portal_link || ''} onChange={(e) => setCandidate({ ...candidate, amazon_portal_link: e.target.value })} /></label>
            <button className="btn" type="submit">Save candidate</button>
          </form>
        </div>
        <div className="card">
          <h2>Action hub</h2>
          {candidate.amazon_portal_link ? <a className="btn" href={candidate.amazon_portal_link} target="_blank" rel="noreferrer">Open portal</a> : <p className="empty">No portal link saved.</p>}
          <div className="status-tags">
            <span className={`badge ${candidate.alert_sent ? 'success' : 'pending'}`}>Alert {candidate.alert_sent ? 'sent' : 'pending'}</span>
            <span className={`badge ${candidate.applied ? 'success' : 'pending'}`}>{candidate.applied ? 'Applied' : 'Not applied'}</span>
            <span className={`badge ${candidate.interview_scheduled ? 'success' : 'pending'}`}>{candidate.interview_scheduled ? 'Interview scheduled' : 'Interview pending'}</span>
          </div>
        </div>
        <div className="card">
          <h2>Profile</h2>
          <p>Status: <span className={`badge ${candidate.status}`}>{candidate.status}</span></p>
          <p>Skills: {(candidate.skills || []).join(', ') || '—'}</p>
          <p>Experience: {candidate.experience || '—'}</p>
          <p>Education: {candidate.education || '—'}</p>
          <p>Vehicle: {candidate.has_vehicle ? 'Yes' : 'No'}</p>
          <p>Resume: {candidate.resume_filename || 'Not uploaded'}</p>
        </div>
        <div className="card">
          <h2>Top matches</h2>
          {(overview?.top_matches || []).map((m: any) => (
            <div key={m.job_id}>{m.match_score}% · job #{m.job_id}</div>
          ))}
        </div>
      </div>
      <div className="card" style={{ marginTop: 16 }}>
        <h2>Application history</h2>
        {apps.map((app) => (
          <div key={app.id} style={{ padding: '0.5rem 0' }}>
            {app.job?.title || app.job_id} — <span className={`badge ${app.status}`}>{app.status}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
