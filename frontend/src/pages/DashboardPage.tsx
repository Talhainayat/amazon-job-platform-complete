import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import {
  AdminSummary,
  Application,
  Candidate,
  Job,
  ManagedSite,
  Match,
  adminApi,
  applicationsApi,
  candidatesApi,
  jobsApi,
  matchesApi,
  apiError,
} from '../services/api'
import { AdminTheme, useAdminTheme } from '../hooks/useAdminTheme'

export default function DashboardPage() {
  const { role, candidateId } = useAuth()
  if (role === 'admin') return <AdminDashboard />
  return <CandidateDashboard candidateId={candidateId} />
}

function AdminDashboard() {
  const [summary, setSummary] = useState<AdminSummary | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [jobs, setJobs] = useState<Job[]>([])
  const [sites, setSites] = useState<ManagedSite[]>([])
  const [showSettings, setShowSettings] = useState(false)
  const { theme, setTheme } = useAdminTheme()

  useEffect(() => {
    const loadDashboard = () => Promise.all([adminApi.summary(), jobsApi.list({ page_size: 20 }), adminApi.sites()]).then(([nextSummary, feed, nextSites]) => { setSummary(nextSummary); setJobs(feed.items); setSites(nextSites) }).catch((err) => setError(apiError(err, 'Could not load dashboard')))
    loadDashboard()
    const timer = window.setInterval(() => jobsApi.list({ page_size: 20 }).then((feed) => setJobs(feed.items)).catch(() => {}), 30000)
    return () => window.clearInterval(timer)
  }, [])

  if (error) return <div className="page"><div className="alert error">{error}</div></div>
  if (!summary) return <div className="page"><div className="skeleton" /></div>

  return (
    <div className="page owner-dashboard">
      <aside className="owner-sidebar">
        <div className="owner-sidebar-title"><span className="owner-sidebar-mark">TP</span><div><strong>Control center</strong><small>Private workspace</small></div></div>
        <p className="sidebar-label">WORKSPACE</p>
        <Link className="sidebar-link active" to="/admin">▦ <span>Overview &amp; analytics</span></Link>
        <Link className="sidebar-link" to="/admin/candidates">♙ <span>Candidate manager</span></Link>
        <Link className="sidebar-link" to="/admin/applications">⇄ <span>Placement tracker</span></Link>
        <p className="sidebar-label">OPERATIONS</p>
        <a className="sidebar-link" href="https://wa.me/923332158308" target="_blank" rel="noreferrer">◌ <span>WhatsApp alert center</span></a>
        <Link className="sidebar-link" to="/admin/jobs">□ <span>Jobs &amp; sources</span></Link>
        <button className="sidebar-link sidebar-button" type="button" onClick={() => setShowSettings((value) => !value)}>⚙ <span>Theme settings</span></button>
        <div className="sidebar-footer"><small>Manager line</small><strong>+92 333 2158308</strong><span>● Monitoring active</span></div>
      </aside>
      <div className="owner-main">
      <div className="page-header">
        <div>
          <p className="eyebrow">PRIVATE OPERATIONS</p><h1>Overview &amp; analytics</h1>
          <p className="lede">A quiet command center for candidate movement and slot signals.</p>
        </div>
        <div className="owner-header-actions"><Link className="btn" to="/admin/candidates">Open candidate manager</Link><select className="theme-select dashboard-theme" value={theme} onChange={(event) => setTheme(event.target.value as AdminTheme)} aria-label="Dashboard theme"><option value="light">Light</option><option value="dark">Dark</option><option value="blue">Midnight blue</option></select></div>
      </div>
      <div className="grid grid-4">
        <Stat label="Total job feeds" value={jobs.length} hint={`${summary.open_jobs} open now`} />
        <Stat label="Active slots claimed" value={summary.hires} hint={`${summary.total_applications} applications`} />
        <Stat label="Candidates matched" value={summary.total_matches} hint={`${summary.total_candidates} candidates`} />
        <Stat label="Application conversions" value={`${summary.total_applications ? Math.round(summary.hires / summary.total_applications * 100) : 0}%`} hint="Applications to hires" />
      </div>
      {showSettings && <div className="card theme-panel"><strong>Dashboard appearance</strong><span>Choose the owner workspace tone.</span><div className="theme-options">{(['light', 'dark', 'blue'] as AdminTheme[]).map((option) => <button className={theme === option ? 'selected' : ''} key={option} onClick={() => setTheme(option)} type="button">{option === 'blue' ? 'Midnight blue' : option[0].toUpperCase() + option.slice(1)}</button>)}</div></div>}
      <div className="dashboard-grid"><div className="card live-feed"><div className="widget-heading"><div><p className="eyebrow">LIVE JOB ANNOUNCEMENTS</p><h2>Fresh signals</h2></div><span className="live-pill">● LIVE / ANNOUNCED</span></div>{jobs.slice(0, 5).map((job, index) => <div className={`feed-row ${index < 2 ? 'fresh' : ''}`} key={job.id}><span className="feed-dot">●</span><div><strong>{job.title}</strong><small>{job.shift || 'Shift open'} · {job.city || job.location || 'Location pending'} · {job.posted_at ? new Date(job.posted_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Recently'}</small></div><b>{Math.min(99, 72 + index * 5)}%<small>confidence</small></b></div>)}{jobs.length === 0 && <p className="empty">No live feed announcements yet.</p>}</div><div className="card chart-card"><div className="widget-heading"><div><p className="eyebrow">VACANCY STATISTICS</p><h2>Openings by feed</h2></div><span className="chart-key">■ Open</span></div><div className="bar-chart">{jobs.slice(0, 6).map((job) => <div className="bar-column" key={job.id}><span style={{ height: `${Math.min(100, (job.openings || 1) * 8 + 20)}%` }} /><small>{(job.city || job.location || 'Site').slice(0, 9)}</small></div>)}</div></div></div>
      <div className="dashboard-grid lower-grid"><div className="card site-card"><div className="widget-heading"><div><p className="eyebrow">AMAZON SITES &amp; AD FEEDS</p><h2>Managed locations</h2></div><button className="btn small" type="button" onClick={async () => { const created = await adminApi.createSite({ name: 'New fulfillment center', postal_code: '', portal_url: '', feed_enabled: true, available_slots: 0 }); setSites((current) => [created, ...current]) }}>+ Add site</button></div>{sites.map((site) => <div className="site-row" key={site.id}><span className={`site-status ${site.feed_enabled ? 'on' : ''}`}>●</span><div><strong>{site.name}</strong><small>ZIP {site.postal_code || '—'} · {site.available_slots} slots available</small></div><button className="feed-toggle" type="button" onClick={async () => { const updated = await adminApi.updateSite(site.id, { ...site, feed_enabled: !site.feed_enabled }); setSites((current) => current.map((item) => item.id === site.id ? updated : item)) }}>{site.feed_enabled ? 'ON' : 'OFF'}</button></div>)}{sites.length === 0 && <p className="empty">No managed sites configured.</p>}</div><div className="card donut-card"><div className="widget-heading"><div><p className="eyebrow">APPLICATION DISTRIBUTION</p><h2>Pipeline mix</h2></div></div><div className="donut"><strong>{summary.total_applications}</strong><small>applications</small></div><div className="donut-legend"><span><i className="legend-pending" />Pending {summary.pending_applications}</span><span><i className="legend-matched" />Matched {summary.total_matches}</span><span><i className="legend-hired" />Hired {summary.hires}</span></div></div></div>
      <div className="grid grid-2" style={{ marginTop: '1rem' }}>
        <div className="card">
          <h2>Recent activity</h2>
          {summary.recent_activity.length === 0 && <p className="empty">No applications yet.</p>}
          {summary.recent_activity.map((item) => (
            <div key={item.id} style={{ padding: '0.55rem 0', borderBottom: '1px solid var(--line)' }}>
              <div>{item.label}</div>
              <small className="notice">{item.status} · {new Date(item.created_at).toLocaleString()}</small>
            </div>
          ))}
        </div>
        <div className="card">
          <h2>Quick actions</h2>
          <div className="grid">
            <Link className="btn secondary" to="/admin/jobs">Manage jobs</Link>
            <Link className="btn secondary" to="/admin/candidates">Review candidates</Link>
            <Link className="btn secondary" to="/admin/applications">Update applications</Link>
          </div>
          <h2 style={{ marginTop: '1.2rem' }}>Latest jobs</h2>
          {summary.recent_jobs.map((job) => (
            <div key={job.id} style={{ padding: '0.4rem 0' }}>
              <Link to={`/jobs/${job.id}`}>{job.title}</Link>
              <span className={`badge ${job.status}`} style={{ marginLeft: 8 }}>{job.status}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="engine-strip"><span className="engine-pulse">●</span><div><strong>Real-time slot engine</strong><small>Watching permitted job sources and matching candidate profiles</small></div><b>ACTIVE</b></div>
      </div>
    </div>
  )
}

function CandidateDashboard({ candidateId }: { candidateId: number | null }) {
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [matches, setMatches] = useState<Match[]>([])
  const [apps, setApps] = useState<Application[]>([])
  const [matchAlert, setMatchAlert] = useState<Match | null>(null)
  const [customJobs, setCustomJobs] = useState<Job[]>([])
  const knownMatchIds = useRef<Set<number>>(new Set())
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!candidateId) return
    const playAlertBeep = () => {
      const AudioContextClass = window.AudioContext || (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
      if (!AudioContextClass) return
      const context = new AudioContextClass()
      const oscillator = context.createOscillator()
      const gain = context.createGain()
      oscillator.frequency.value = 880
      gain.gain.setValueAtTime(0.08, context.currentTime)
      gain.gain.exponentialRampToValueAtTime(0.001, context.currentTime + 0.35)
      oscillator.connect(gain).connect(context.destination)
      oscillator.start()
      oscillator.stop(context.currentTime + 0.35)
    }
    const loadMatches = () => matchesApi.listForCandidate(candidateId).then((m) => {
      const highMatch = m.find((item) => item.match_score >= 80 && !knownMatchIds.current.has(item.id))
      m.forEach((item) => knownMatchIds.current.add(item.id))
      if (highMatch) {
        setMatchAlert(highMatch)
        playAlertBeep()
      }
      setMatches(m.slice(0, 5))
    })
    const loadCustomJobs = () => jobsApi.list({ page_size: 20 }).then((res) => {
      const active = res.items.filter((j) => j.is_custom && j.is_active && j.status === 'open')
      setCustomJobs(active.slice(0, 3))
    }).catch(() => {})
    Promise.all([candidatesApi.get(candidateId), loadMatches(), applicationsApi.listForCandidate(candidateId).catch(() => []), loadCustomJobs()])
      .then(([c, , a]) => { setCandidate(c); setApps(a.slice(0, 5)) })
      .catch((err) => setError(apiError(err, 'Could not load your dashboard')))
    const timer = window.setInterval(() => { loadMatches().catch(() => {}); loadCustomJobs() }, 30000)
    return () => window.clearInterval(timer)
  }, [candidateId])

  if (!candidateId) return <div className="page">Loading your workspace…</div>
  if (error) return <div className="page"><div className="alert error">{error}</div></div>
  const completion = candidate?.profile_completion ?? 0

  return (
    <div className="page">
      {matchAlert && <div className="alert match-alert" role="alert">
        <strong>High-match role found: {Math.round(matchAlert.match_score)}%</strong>
        <Link to={`/jobs/${matchAlert.job_id}`}>Review this opportunity</Link>
        <button className="btn secondary" type="button" onClick={() => setMatchAlert(null)}>Dismiss</button>
      </div>}
      <div className="page-header">
        <div>
          <h1>Hello{candidate ? `, ${candidate.name.split(' ')[0]}` : ''}</h1>
          <p className="lede">Recommended roles, application status, and next steps in one place.</p>
        </div>
        <Link className="btn" to="/profile">Review profile</Link>
      </div>
      <div className="grid grid-3">
        <div className="card">
          <h2>Profile strength</h2>
          <div className="progress"><div style={{ width: `${completion}%` }} /></div>
          <p>{completion}% complete</p>
          <Link to="/profile">Complete your profile</Link>
        </div>
        <Stat label="Applications" value={apps.length} hint="Recent activity" />
        <Stat label="Top match" value={matches[0] ? `${Math.round(matches[0].match_score)}%` : '—'} hint={matches[0]?.job_title || 'Recalculate from your profile'} />
      </div>
      <div className="card journey-card">
        <div className="journey-heading"><div><p className="eyebrow">YOUR PLACEMENT JOURNEY</p><h2>One clear next step at a time.</h2></div><span>{candidate?.interview_scheduled ? 'Complete' : candidate?.applied ? 'In progress' : 'Getting started'}</span></div>
        <div className="journey-steps"><JourneyStep number="01" label="Profile setup" complete={completion >= 80} /><JourneyStep number="02" label="Slot matching" complete={matches.length > 0} /><JourneyStep number="03" label="Slot applied" complete={!!candidate?.applied} /><JourneyStep number="04" label="Interview scheduled" complete={!!candidate?.interview_scheduled} /></div>
      </div>
      <div className="grid grid-2" style={{ marginTop: '1rem' }}>
        <div className="card">
          <h2>Recommended jobs</h2>
          {matches.length === 0 && <p className="empty">No matches yet. Add skills and preferences, then browse jobs.</p>}
          {matches.map((m) => (
            <div key={m.id} style={{ display: 'flex', justifyContent: 'space-between', gap: 12, padding: '0.7rem 0', borderBottom: '1px solid var(--line)' }}>
              <div>
                <Link to={`/jobs/${m.job_id}`}><strong>{m.job_title || `Job #${m.job_id}`}</strong></Link>
                <div className="notice">{m.location || 'Location TBA'}</div>
              </div>
              <strong>{Math.round(m.match_score)}%</strong>
            </div>
          ))}
        </div>
        <div className="card">
          <h2>Recent applications</h2>
          {apps.length === 0 && <p className="empty">You have not applied yet.</p>}
          {apps.map((a) => (
            <div key={a.id} style={{ padding: '0.7rem 0', borderBottom: '1px solid var(--line)' }}>
              <Link to={`/jobs/${a.job_id}`}>{a.job?.title || `Job #${a.job_id}`}</Link>
              <div><span className={`badge ${a.status}`}>{a.status.replace('_', ' ')}</span></div>
            </div>
          ))}
        </div>
      </div>
      {customJobs.length > 0 && (
        <div className="card" style={{ marginTop: '1rem' }}>
          <h2 style={{ marginBottom: '0.8rem' }}>⭐ Featured opportunities</h2>
          <div className="grid grid-3" style={{ gap: '1rem' }}>
            {customJobs.map((job) => (
              <Link
                key={job.id}
                to={`/jobs/${job.id}`}
                style={{
                  padding: '1rem',
                  border: '1px solid var(--line)',
                  borderRadius: '0.5rem',
                  textDecoration: 'none',
                  color: 'inherit',
                  transition: 'all 0.2s',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'var(--primary)'
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--line)'
                  e.currentTarget.style.boxShadow = 'none'
                }}
              >
                <div style={{ marginBottom: '0.5rem' }}>
                  <span
                    className="badge"
                    style={{
                      backgroundColor: job.badge_status === 'urgent' ? '#dc2626' : '#16a34a',
                      color: 'white',
                      padding: '0.25rem 0.5rem',
                      fontSize: '0.75rem'
                    }}
                  >
                    {job.badge_status === 'urgent' ? '🔴 URGENT' : '● LIVE'}
                  </span>
                </div>
                <h3 style={{ marginBottom: '0.25rem', fontSize: '1rem' }}>{job.title}</h3>
                <div className="notice" style={{ marginBottom: '0.5rem' }}>
                  {job.company && <strong>{job.company}</strong>} {job.city && <span>· {job.city}</span>}
                </div>
                {job.pay_min && job.pay_max && (
                  <div style={{ color: '#16a34a', fontWeight: 'bold', fontSize: '0.9rem' }}>
                    ${job.pay_min} – ${job.pay_max}/{job.pay_period || 'hour'}
                  </div>
                )}
                <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#0ea5e9' }}>
                  Click to apply →
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function JourneyStep({ number, label, complete }: { number: string; label: string; complete: boolean }) {
  return <div className={`journey-step ${complete ? 'complete' : ''}`}><span>{complete ? '✓' : number}</span><strong>{label}</strong></div>
}

function Stat({ label, value, hint }: { label: string; value: number | string; hint?: string }) {
  return (
    <div className="card stat">
      <span>{label}</span>
      <b>{value}</b>
      {hint && <span>{hint}</span>}
    </div>
  )
}
