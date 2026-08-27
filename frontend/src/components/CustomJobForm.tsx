import { FormEvent, useEffect, useState } from 'react'
import { Job, apiError, jobsApi } from '../services/api'

interface CustomJobFormProps {
  job?: Partial<Job>
  onSubmit: (job: Partial<Job>) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

const blank: Partial<Job> = {
  title: '',
  company: '',
  description: '',
  requirements: '',
  location: '',
  city: '',
  postal_code: '',
  shift: 'day',
  job_type: 'warehouse',
  skills: [],
  openings: 1,
  status: 'open',
  is_custom: true,
  application_url: '',
  badge_status: 'live',
  pay_min: undefined,
  pay_max: undefined,
  pay_period: 'hourly',
}

export default function CustomJobForm({ job, onSubmit, onCancel, isLoading }: CustomJobFormProps) {
  const [formData, setFormData] = useState<Partial<Job>>(job || blank)
  const [skills, setSkills] = useState('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (job) {
      setFormData(job)
      setSkills((job.skills || []).join(', '))
    }
  }, [job])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!formData.title || !formData.company) {
      setError('Title and Company are required')
      return
    }

    if (formData.is_custom && !formData.application_url) {
      setError('Application URL is required for custom jobs')
      return
    }

    const payload = {
      ...formData,
      skills: skills.split(',').map((s) => s.trim()).filter(Boolean),
    }

    try {
      await onSubmit(payload)
    } catch (err) {
      setError(apiError(err, 'Could not save job'))
    }
  }

  return (
    <form className="card grid grid-2" onSubmit={handleSubmit}>
      {error && <div className="alert error" style={{ gridColumn: '1 / -1' }}>{error}</div>}

      <label className="field">
        <span>Job Title *</span>
        <input
          value={formData.title || ''}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          placeholder="e.g., Amazon Fulfillment Associate"
          required
        />
      </label>

      <label className="field">
        <span>Company Name *</span>
        <input
          value={formData.company || ''}
          onChange={(e) => setFormData({ ...formData, company: e.target.value })}
          placeholder="e.g., Amazon, Custom Portal"
          required
        />
      </label>

      <label className="field" style={{ gridColumn: '1 / -1' }}>
        <span>Description</span>
        <textarea
          value={formData.description || ''}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Job description..."
          rows={3}
        />
      </label>

      <label className="field" style={{ gridColumn: '1 / -1' }}>
        <span>Requirements</span>
        <textarea
          value={formData.requirements || ''}
          onChange={(e) => setFormData({ ...formData, requirements: e.target.value })}
          placeholder="Job requirements..."
          rows={3}
        />
      </label>

      <label className="field">
        <span>Location / City</span>
        <input
          value={formData.city || ''}
          onChange={(e) => setFormData({ ...formData, city: e.target.value })}
          placeholder="e.g., Toronto"
        />
      </label>

      <label className="field">
        <span>Postal Code / ZIP</span>
        <input
          value={formData.postal_code || ''}
          onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
          placeholder="e.g., M5H 2N2"
        />
      </label>

      <label className="field">
        <span>Shift Type</span>
        <select value={formData.shift || 'day'} onChange={(e) => setFormData({ ...formData, shift: e.target.value })}>
          <option value="day">Day</option>
          <option value="night">Night</option>
          <option value="flexible">Flexible</option>
          <option value="rotation">Rotation</option>
        </select>
      </label>

      <label className="field">
        <span>Job Type</span>
        <input
          value={formData.job_type || ''}
          onChange={(e) => setFormData({ ...formData, job_type: e.target.value })}
          placeholder="e.g., Warehouse, Delivery"
        />
      </label>

      <label className="field">
        <span>Hourly Rate (Min)</span>
        <input
          type="number"
          step="0.50"
          value={formData.pay_min ?? ''}
          onChange={(e) => setFormData({ ...formData, pay_min: Number(e.target.value) || undefined })}
          placeholder="e.g., 15.50"
        />
      </label>

      <label className="field">
        <span>Hourly Rate (Max)</span>
        <input
          type="number"
          step="0.50"
          value={formData.pay_max ?? ''}
          onChange={(e) => setFormData({ ...formData, pay_max: Number(e.target.value) || undefined })}
          placeholder="e.g., 18.00"
        />
      </label>

      <label className="field">
        <span>Pay Period</span>
        <select value={formData.pay_period || 'hourly'} onChange={(e) => setFormData({ ...formData, pay_period: e.target.value })}>
          <option value="hourly">Hourly</option>
          <option value="salary">Salary</option>
        </select>
      </label>

      <label className="field">
        <span>Opening Slots</span>
        <input
          type="number"
          value={formData.openings ?? 1}
          onChange={(e) => setFormData({ ...formData, openings: Number(e.target.value) })}
          min="1"
        />
      </label>

      <label className="field">
        <span>Skills (comma-separated)</span>
        <input
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
          placeholder="e.g., Forklift, Inventory Management"
        />
      </label>

      <label className="field" style={{ gridColumn: '1 / -1' }}>
        <span>External Application URL *</span>
        <input
          type="url"
          value={formData.application_url || ''}
          onChange={(e) => setFormData({ ...formData, application_url: e.target.value })}
          placeholder="https://amazon.com/jobs or https://custom-portal.com/apply"
          required
        />
      </label>

      <label className="field">
        <span>Badge Status</span>
        <select
          value={formData.badge_status || 'live'}
          onChange={(e) => setFormData({ ...formData, badge_status: e.target.value })}
        >
          <option value="live">● GREEN LIVE SIGNAL</option>
          <option value="urgent">🔴 URGENT</option>
        </select>
      </label>

      <label className="field">
        <span>Job Status</span>
        <select
          value={formData.status || 'open'}
          onChange={(e) => setFormData({ ...formData, status: e.target.value })}
        >
          <option value="draft">Draft</option>
          <option value="open">Open</option>
          <option value="closed">Closed</option>
        </select>
      </label>

      <div style={{ gridColumn: '1 / -1', display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
        <button type="button" className="btn" onClick={onCancel} disabled={isLoading}>
          Cancel
        </button>
        <button type="submit" className="btn" disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Custom Job'}
        </button>
      </div>
    </form>
  )
}
