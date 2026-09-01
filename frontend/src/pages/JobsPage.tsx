import { FormEvent, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Job, JobListResponse, apiError, jobsApi, payLabel } from '../services/api'
import { useAuth } from '../hooks/useAuth'
import LazyImage from '../components/LazyImage'

const emptyFilters = { q: '', location: '', job_type: '', shift: '', min_pay: '', skills: '', sort: 'newest' }

export default function JobsPage() {
  const { role } = useAuth()
  const [filters, setFilters] = useState(emptyFilters)
  const [data, setData] = useState<JobListResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)

  const load = (nextPage = page, nextFilters = filters) => {
    setLoading(true)
    setError(null)
    jobsApi
      .list({
        q: nextFilters.q || undefined,
        location: nextFilters.location || undefined,
        job_type: nextFilters.job_type || undefined,
        shift: nextFilters.shift || undefined,
        min_pay: nextFilters.min_pay ? Number(nextFilters.min_pay) : undefined,
        skills: nextFilters.skills || undefined,
        sort: nextFilters.sort,
        page: nextPage,
        page_size: 10,
        status_filter: role === 'admin' ? undefined : 'open',
      })
      .then(setData)
      .catch((err) => setError(apiError(err, 'Could not load jobs')))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load(1, filters)
  }, [])

  const onSearch = (e: FormEvent) => {
    e.preventDefault()
    setPage(1)
    load(1, filters)
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Find your next role</h1>
          <p className="lede">Search by keyword, city, shift, pay, and skills. Match scores update from your profile.</p>
        </div>
        {role === 'admin' && <Link className="btn" to="/admin/jobs/new">Create job</Link>}
      </div>
      <form className="card filters" onSubmit={onSearch}>
        <label className="field"><span>Keyword</span><input value={filters.q} onChange={(e) => setFilters({ ...filters, q: e.target.value })} /></label>
        <label className="field"><span>Location</span><input value={filters.location} onChange={(e) => setFilters({ ...filters, location: e.target.value })} /></label>
        <label className="field"><span>Job type</span><input value={filters.job_type} onChange={(e) => setFilters({ ...filters, job_type: e.target.value })} /></label>
        <label className="field"><span>Shift</span>
          <select value={filters.shift} onChange={(e) => setFilters({ ...filters, shift: e.target.value })}>
            <option value="">Any</option>
            <option value="day">Day</option>
            <option value="night">Night</option>
            <option value="evening">Evening</option>
            <option value="rotating">Rotating</option>
          </select>
        </label>
        <label className="field"><span>Min pay</span><input type="number" value={filters.min_pay} onChange={(e) => setFilters({ ...filters, min_pay: e.target.value })} /></label>
        <label className="field"><span>Skills</span><input value={filters.skills} onChange={(e) => setFilters({ ...filters, skills: e.target.value })} placeholder="warehouse, forklift" /></label>
        <label className="field"><span>Sort</span>
          <select value={filters.sort} onChange={(e) => setFilters({ ...filters, sort: e.target.value })}>
            <option value="newest">Newest</option>
            <option value="oldest">Oldest</option>
            <option value="pay">Pay</option>
            <option value="match">Best match</option>
          </select>
        </label>
        <button className="btn" type="submit">Search</button>
        <button className="btn secondary" type="button" onClick={() => { setFilters(emptyFilters); setPage(1); load(1, emptyFilters) }}>Clear</button>
      </form>
      {loading && <div className="skeleton" />}
      {error && <div className="alert error">{error}</div>}
      {!loading && data && data.items.length === 0 && <div className="card empty">No jobs match those filters. Try a wider location or clear filters.</div>}
      <div className="grid jobs-grid" style={{ marginTop: '1rem' }}>
        {data?.items.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
      </div>
      {data && data.total > data.page_size && (
        <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
          <button className="btn secondary" disabled={page <= 1} onClick={() => { const p = page - 1; setPage(p); load(p) }}>Previous</button>
          <button className="btn secondary" disabled={page * data.page_size >= data.total} onClick={() => { const p = page + 1; setPage(p); load(p) }}>Next</button>
        </div>
      )}
    </div>
  )
}

function JobCard({ job }: { job: Job }) {
  return (
    <Link to={`/jobs/${job.id}`} style={{ textDecoration: 'none' }}>
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem', cursor: 'pointer', height: '100%', transition: 'all 0.3s ease' }}>
        {job.image_url && (
          <div style={{ width: '100%', height: '160px', borderRadius: '8px', overflow: 'hidden', marginBottom: '0.4rem' }}>
            <LazyImage
              src={job.image_url}
              alt={job.title}
              width={400}
              height={160}
              fallback="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 400 160%22%3E%3Crect fill=%22%23e2e8f0%22 width=%22400%22 height=%22160%22/%3E%3C/svg%3E"
            />
          </div>
        )}
        <div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
            <strong>{job.title}</strong>
            <span className={`badge ${job.status}`}>{job.status}</span>
          </div>
          <div className="job-meta">
            <span>{job.company || 'Hiring company'}</span>
            <span>{[job.city || job.location, job.province].filter(Boolean).join(', ') || 'Location TBA'}</span>
            <span>{job.shift || 'Shift TBA'}</span>
            <span>{job.job_type || 'Type TBA'}</span>
            <span>{payLabel(job)}</span>
          </div>
          {job.match_explanation && job.match_explanation.length > 0 && (
            <p className="notice">{job.match_explanation.slice(0, 2).join(' · ')}</p>
          )}
        </div>
        {typeof job.match_score === 'number' && (
          <div className="match" style={{ ['--p' as string]: job.match_score, marginTop: 'auto' }}>
            <span>{Math.round(job.match_score)}%</span>
          </div>
        )}
      </div>
    </Link>
  )
}
