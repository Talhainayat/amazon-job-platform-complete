import { FormEvent, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Job, apiError, jobsApi } from '../services/api'

const blank: Partial<Job> = {
  title: '',
  company: '',
  description: '',
  requirements: '',
  location: '',
  city: '',
  province: '',
  postal_code: '',
  shift: 'day',
  job_type: 'warehouse',
  skills: [],
  openings: 1,
  status: 'draft',
  source: 'manual_upload',
}

export default function AdminJobFormPage() {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const [job, setJob] = useState<Partial<Job>>(blank)
  const [skills, setSkills] = useState('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!jobId) return
    jobsApi.get(Number(jobId)).then((data) => {
      setJob(data)
      setSkills((data.skills || []).join(', '))
    })
  }, [jobId])

  const save = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    const payload = { ...job, skills: skills.split(',').map((s) => s.trim()).filter(Boolean) }
    try {
      if (jobId) await jobsApi.update(Number(jobId), payload)
      else await jobsApi.create(payload)
      navigate('/admin/jobs')
    } catch (err) {
      setError(apiError(err, 'Could not save job'))
    }
  }

  return (
    <div className="page">
      <h1>{jobId ? 'Edit job' : 'Create job'}</h1>
      {error && <div className="alert error">{error}</div>}
      <form className="card grid grid-2" onSubmit={save}>
        <label className="field"><span>Title</span><input value={job.title || ''} onChange={(e) => setJob({ ...job, title: e.target.value })} required /></label>
        <label className="field"><span>Company</span><input value={job.company || ''} onChange={(e) => setJob({ ...job, company: e.target.value })} /></label>
        <label className="field" style={{ gridColumn: '1 / -1' }}><span>Description</span><textarea value={job.description || ''} onChange={(e) => setJob({ ...job, description: e.target.value })} /></label>
        <label className="field" style={{ gridColumn: '1 / -1' }}><span>Requirements</span><textarea value={job.requirements || ''} onChange={(e) => setJob({ ...job, requirements: e.target.value })} /></label>
        <label className="field"><span>Location</span><input value={job.location || ''} onChange={(e) => setJob({ ...job, location: e.target.value })} /></label>
        <label className="field"><span>City</span><input value={job.city || ''} onChange={(e) => setJob({ ...job, city: e.target.value })} /></label>
        <label className="field"><span>Province</span><input value={job.province || ''} onChange={(e) => setJob({ ...job, province: e.target.value })} /></label>
        <label className="field"><span>Postal code</span><input value={job.postal_code || ''} onChange={(e) => setJob({ ...job, postal_code: e.target.value })} /></label>
        <label className="field"><span>Job type</span><input value={job.job_type || ''} onChange={(e) => setJob({ ...job, job_type: e.target.value })} /></label>
        <label className="field"><span>Shift</span><input value={job.shift || ''} onChange={(e) => setJob({ ...job, shift: e.target.value })} /></label>
        <label className="field"><span>Skills</span><input value={skills} onChange={(e) => setSkills(e.target.value)} /></label>
        <label className="field"><span>Experience (years)</span><input type="number" value={job.years_experience ?? ''} onChange={(e) => setJob({ ...job, years_experience: Number(e.target.value) })} /></label>
        <label className="field"><span>Openings</span><input type="number" value={job.openings ?? 1} onChange={(e) => setJob({ ...job, openings: Number(e.target.value) })} /></label>
        <label className="field"><span>Pay min</span><input type="number" value={job.pay_min ?? ''} onChange={(e) => setJob({ ...job, pay_min: Number(e.target.value) })} /></label>
        <label className="field"><span>Pay max</span><input type="number" value={job.pay_max ?? ''} onChange={(e) => setJob({ ...job, pay_max: Number(e.target.value) })} /></label>
        <label className="field"><span>Pay period</span><input value={job.pay_period || 'hourly'} onChange={(e) => setJob({ ...job, pay_period: e.target.value })} /></label>
        <label className="field"><span>Status</span>
          <select value={job.status || 'draft'} onChange={(e) => setJob({ ...job, status: e.target.value })}>
            <option value="draft">Draft</option>
            <option value="open">Open</option>
            <option value="closed">Closed</option>
            <option value="archived">Archived</option>
          </select>
        </label>
        <button className="btn" type="submit">Save job</button>
      </form>
    </div>
  )
}
