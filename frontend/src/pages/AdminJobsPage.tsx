import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Job, apiError, jobsApi } from '../services/api'

export default function AdminJobsPage() {
  const [items, setItems] = useState<Job[]>([])
  const [q, setQ] = useState('')
  const [status, setStatus] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [importing, setImporting] = useState(false)
  const [importStatus, setImportStatus] = useState<string | null>(null)

  const load = () => {
    jobsApi
      .list({ q: q || undefined, status_filter: status || undefined, page_size: 50, sort: 'newest' })
      .then((res) => setItems(res.items))
      .catch((err) => setError(apiError(err)))
  }

  useEffect(() => {
    load()
  }, [])

  const act = async (job: Job, action: 'publish' | 'close' | 'reopen' | 'archive') => {
    const fn = { publish: jobsApi.publish, close: jobsApi.close, reopen: jobsApi.reopen, archive: jobsApi.archive }[action]
    await fn(job.id)
    load()
  }

  const fetchLiveJobs = async () => {
    setImporting(true)
    setImportStatus(null)
    try {
      const result = await jobsApi.importLive()
      setImportStatus(`${result.imported} live jobs imported; ${result.skipped_duplicates} duplicates skipped.`)
      load()
    } catch (err) {
      setError(apiError(err, 'Could not fetch live jobs'))
    } finally {
      setImporting(false)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Job management</h1>
          <p className="lede">Create, publish, close, and archive roles.</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}><button className="btn secondary" type="button" onClick={fetchLiveJobs} disabled={importing}>{importing ? 'Fetching…' : 'Fetch Live Web Jobs'}</button><Link className="btn" to="/admin/jobs/new">New job</Link></div>
      </div>
      {error && <div className="alert error">{error}</div>}
      {importStatus && <div className="alert success">{importStatus}</div>}
      <div className="card" style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
        <input placeholder="Search" value={q} onChange={(e) => setQ(e.target.value)} />
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All statuses</option>
          <option value="draft">Draft</option>
          <option value="open">Open</option>
          <option value="closed">Closed</option>
          <option value="archived">Archived</option>
        </select>
        <button className="btn" type="button" onClick={load}>Filter</button>
      </div>
      <div className="card table-wrap">
        <table>
          <thead>
            <tr><th>Title</th><th>Location</th><th>Status</th><th></th></tr>
          </thead>
          <tbody>
            {items.map((job) => (
              <tr key={job.id}>
                <td><Link to={`/jobs/${job.id}`}>{job.title}</Link></td>
                <td>{job.city || job.location}</td>
                <td><span className={`badge ${job.status}`}>{job.status}</span></td>
                <td style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  <Link className="btn ghost" to={`/admin/jobs/${job.id}/edit`}>Edit</Link>
                  {job.status === 'draft' && <button className="btn" type="button" onClick={() => act(job, 'publish')}>Publish</button>}
                  {job.status === 'open' && <button className="btn secondary" type="button" onClick={() => act(job, 'close')}>Close</button>}
                  {job.status === 'closed' && <button className="btn" type="button" onClick={() => act(job, 'reopen')}>Reopen</button>}
                  {job.status !== 'archived' && <button className="btn ghost" type="button" onClick={() => act(job, 'archive')}>Archive</button>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {items.length === 0 && <p className="empty">No jobs yet.</p>}
      </div>
    </div>
  )
}
