import { useEffect, useState } from 'react'
import CustomJobForm from '../components/CustomJobForm'
import { Job, apiError, jobsApi } from '../services/api'

export default function AdminCustomJobsPage() {
  const [items, setItems] = useState<Job[]>([])
  const [q, setQ] = useState('')
  const [status, setStatus] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [editingJob, setEditingJob] = useState<Job | undefined>(undefined)
  const [isSaving, setIsSaving] = useState(false)

  const loadCustomJobs = () => {
    jobsApi
      .listCustom({ q: q || undefined, status_filter: status || undefined, page_size: 50 })
      .then((res) => setItems(res.items))
      .catch((err) => setError(apiError(err)))
  }

  useEffect(() => {
    loadCustomJobs()
  }, [q, status])

  const handleCreateCustomJob = async (jobData: Partial<Job>) => {
    setIsSaving(true)
    try {
      await jobsApi.createCustom(jobData)
      setShowForm(false)
      setEditingJob(undefined)
      loadCustomJobs()
    } finally {
      setIsSaving(false)
    }
  }

  const handleUpdateCustomJob = async (jobData: Partial<Job>) => {
    if (!editingJob?.id) return
    setIsSaving(true)
    try {
      await jobsApi.updateCustom(editingJob.id, jobData)
      setShowForm(false)
      setEditingJob(undefined)
      loadCustomJobs()
    } finally {
      setIsSaving(false)
    }
  }

  const handleDeleteCustomJob = async (jobId: number) => {
    if (!confirm('Are you sure you want to delete this custom job?')) return
    try {
      await jobsApi.deleteCustom(jobId)
      loadCustomJobs()
    } catch (err) {
      setError(apiError(err, 'Could not delete job'))
    }
  }

  const handleToggleActive = async (job: Job) => {
    try {
      await jobsApi.toggleCustomActive(job.id)
      loadCustomJobs()
    } catch (err) {
      setError(apiError(err, 'Could not update job'))
    }
  }

  const openCreateForm = () => {
    setEditingJob(undefined)
    setShowForm(true)
  }

  const openEditForm = (job: Job) => {
    setEditingJob(job)
    setShowForm(true)
  }

  const closeForm = () => {
    setShowForm(false)
    setEditingJob(undefined)
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Custom Job Management</h1>
          <p className="lede">Create and manage external links and custom jobs.</p>
        </div>
        <button className="btn" onClick={openCreateForm}>+ Add Custom Job</button>
      </div>

      {error && <div className="alert error">{error}</div>}

      {showForm && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h2>{editingJob ? 'Edit Custom Job' : 'Create New Custom Job'}</h2>
            <button className="btn ghost" onClick={closeForm} disabled={isSaving}>✕</button>
          </div>
          <CustomJobForm
            job={editingJob}
            onSubmit={editingJob ? handleUpdateCustomJob : handleCreateCustomJob}
            onCancel={closeForm}
            isLoading={isSaving}
          />
        </div>
      )}

      <div className="card" style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
        <input
          placeholder="Search by title or company"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All statuses</option>
          <option value="draft">Draft</option>
          <option value="open">Open</option>
          <option value="closed">Closed</option>
        </select>
        <button className="btn" type="button" onClick={loadCustomJobs}>
          Refresh
        </button>
      </div>

      <div className="card table-wrap">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Company</th>
              <th>Location</th>
              <th>Badge</th>
              <th>Status</th>
              <th>Active</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map((job) => (
              <tr key={job.id}>
                <td><strong>{job.title}</strong></td>
                <td>{job.company}</td>
                <td>{job.city || job.location || '—'}</td>
                <td>
                  <span className="badge" style={{ 
                    backgroundColor: job.badge_status === 'urgent' ? '#dc2626' : '#16a34a' 
                  }}>
                    {job.badge_status === 'urgent' ? '🔴 URGENT' : '● LIVE'}
                  </span>
                </td>
                <td><span className={`badge ${job.status}`}>{job.status}</span></td>
                <td>
                  <button
                    className={`btn ${job.is_active ? 'secondary' : 'ghost'}`}
                    onClick={() => handleToggleActive(job)}
                    style={{ fontSize: '12px', padding: '4px 8px' }}
                  >
                    {job.is_active ? 'Active' : 'Inactive'}
                  </button>
                </td>
                <td style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  <button
                    className="btn ghost"
                    onClick={() => openEditForm(job)}
                    style={{ fontSize: '12px' }}
                  >
                    Edit
                  </button>
                  <button
                    className="btn ghost"
                    onClick={() => handleDeleteCustomJob(job.id)}
                    style={{ fontSize: '12px', color: '#dc2626' }}
                  >
                    Delete
                  </button>
                  {job.application_url && (
                    <a
                      href={job.application_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn ghost"
                      style={{ fontSize: '12px' }}
                    >
                      Link ↗
                    </a>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {items.length === 0 && (
          <p className="empty">
            No custom jobs yet.{' '}
            <button className="link" onClick={openCreateForm}>
              Create one
            </button>
            .
          </p>
        )}
      </div>
    </div>
  )
}
