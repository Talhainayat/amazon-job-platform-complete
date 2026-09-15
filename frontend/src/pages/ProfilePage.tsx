import { FormEvent, useEffect, useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import {
  Candidate,
  CandidatePreferences,
  apiError,
  candidatesApi,
  matchesApi,
} from '../services/api'

export default function ProfilePage() {
  const { candidateId } = useAuth()
  const [candidate, setCandidate] = useState<Partial<Candidate>>({})
  const [prefs, setPrefs] = useState<Partial<CandidatePreferences>>({ radius_km: 25 })
  const [status, setStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [detecting, setDetecting] = useState(false)

  useEffect(() => {
    if (!candidateId) return
    candidatesApi.get(candidateId).then(setCandidate).catch((err) => setError(apiError(err)))
    candidatesApi.getPreferences(candidateId).then(setPrefs).catch(() => {})
  }, [candidateId])

  if (!candidateId) return <div className="page">Loading your profile…</div>

  const saveProfile = async (e: FormEvent) => {
    e.preventDefault()
    setStatus(null)
    try {
      const saved = await candidatesApi.update(candidateId, {
        name: candidate.name,
        phone: candidate.phone,
        location: candidate.location,
        city: candidate.city,
        province: candidate.province,
        postal_code: candidate.postal_code,
        preferred_shift: candidate.preferred_shift,
        job_type: candidate.job_type,
        skills: typeof candidate.skills === 'string' ? (candidate.skills as unknown as string).split(',') : candidate.skills,
        years_experience: candidate.years_experience,
        experience: candidate.experience,
        education: candidate.education,
        availability: candidate.availability,
        has_vehicle: candidate.has_vehicle,
        amazon_portal_link: candidate.amazon_portal_link,
        work_eligibility: candidate.work_eligibility,
      })
      setCandidate(saved)
      setStatus('Profile saved.')
    } catch (err) {
      setStatus(apiError(err, 'Could not save profile'))
    }
  }

  const savePrefs = async () => {
    try {
      const saved = await candidatesApi.savePreferences(candidateId, prefs)
      setPrefs(saved)
      await matchesApi.recalculate(candidateId)
      setStatus('Preferences saved and matches updated.')
    } catch (err) {
      setStatus(apiError(err, 'Could not save preferences'))
    }
  }

  const detectLocation = async () => {
    setDetecting(true)
    try {
      const detected = await candidatesApi.detectLocation()
      setCandidate(detected)
      setStatus('Location detected. Review it and save your profile if needed.')
    } catch (err) {
      setStatus(apiError(err, 'Could not detect your location'))
    } finally {
      setDetecting(false)
    }
  }

  const onResume = async (file?: File) => {
    if (!file) return
    try {
      const saved = await candidatesApi.uploadResume(candidateId, file)
      setCandidate(saved)
      setStatus('Resume uploaded.')
    } catch (err) {
      setStatus(apiError(err, 'Resume upload failed'))
    }
  }

  const completion = candidate.profile_completion ?? 0

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Your profile</h1>
          <p className="lede">Complete this so matching, distance, and applications stay accurate.</p>
        </div>
        <div className="card" style={{ minWidth: 220 }}>
          <div className="progress"><div style={{ width: `${completion}%` }} /></div>
          <small>{completion}% complete</small>
        </div>
      </div>
      {error && <div className="alert error">{error}</div>}
      {status && <div className="alert success">{status}</div>}
      <form className="card grid grid-2" onSubmit={saveProfile}>
        <label className="field"><span>Full name</span><input value={candidate.name || ''} onChange={(e) => setCandidate({ ...candidate, name: e.target.value })} required /></label>
        <label className="field"><span>Email</span><input value={candidate.email || ''} disabled /></label>
        <label className="field"><span>Phone</span><input value={candidate.phone || ''} onChange={(e) => setCandidate({ ...candidate, phone: e.target.value })} /></label>
        <label className="field"><span>Target ZIP / postal code</span><input value={candidate.postal_code || ''} onChange={(e) => setCandidate({ ...candidate, postal_code: e.target.value })} /></label>
        <label className="field"><span>Location</span><input value={candidate.location || ''} onChange={(e) => setCandidate({ ...candidate, location: e.target.value })} /></label>
        <label className="field"><span>City</span><input value={candidate.city || ''} onChange={(e) => setCandidate({ ...candidate, city: e.target.value })} /><button className="btn secondary" type="button" onClick={detectLocation} disabled={detecting}>{detecting ? 'Detecting…' : 'Auto-detect My Location'}</button></label>
        <label className="field"><span>Province / state</span><input value={candidate.province || ''} onChange={(e) => setCandidate({ ...candidate, province: e.target.value })} /></label>
        <label className="field"><span>Postal code</span><input value={candidate.postal_code || ''} onChange={(e) => setCandidate({ ...candidate, postal_code: e.target.value })} /></label>
        <label className="field"><span>Preferred job type</span><input value={candidate.job_type || ''} onChange={(e) => setCandidate({ ...candidate, job_type: e.target.value })} /></label>
        <label className="field"><span>Preferred shift</span><input value={candidate.preferred_shift || ''} onChange={(e) => setCandidate({ ...candidate, preferred_shift: e.target.value })} /></label>
        <label className="field"><span>Work eligibility</span><input value={candidate.work_eligibility || ''} onChange={(e) => setCandidate({ ...candidate, work_eligibility: e.target.value })} placeholder="Eligible to work" /></label>
        <label className="field" style={{ gridColumn: '1 / -1' }}><span>Amazon portal link</span><input type="url" value={candidate.amazon_portal_link || ''} onChange={(e) => setCandidate({ ...candidate, amazon_portal_link: e.target.value })} placeholder="https://..." /></label>
        <label className="field"><span>Years of experience</span><input type="number" value={candidate.years_experience ?? ''} onChange={(e) => setCandidate({ ...candidate, years_experience: Number(e.target.value) })} /></label>
        <label className="field"><span>Skills (comma separated)</span><input value={(candidate.skills || []).join(', ')} onChange={(e) => setCandidate({ ...candidate, skills: e.target.value.split(',').map((s) => s.trim()).filter(Boolean) })} /></label>
        <label className="field"><span>Availability</span><input value={candidate.availability || ''} onChange={(e) => setCandidate({ ...candidate, availability: e.target.value })} /></label>
        <label className="field" style={{ gridColumn: '1 / -1' }}><span>Experience</span><textarea value={candidate.experience || ''} onChange={(e) => setCandidate({ ...candidate, experience: e.target.value })} /></label>
        <label className="field" style={{ gridColumn: '1 / -1' }}><span>Education</span><textarea value={candidate.education || ''} onChange={(e) => setCandidate({ ...candidate, education: e.target.value })} /></label>
        <label className="field"><span>Vehicle available</span>
          <select value={candidate.has_vehicle ? 'yes' : 'no'} onChange={(e) => setCandidate({ ...candidate, has_vehicle: e.target.value === 'yes' })}>
            <option value="no">No</option>
            <option value="yes">Yes</option>
          </select>
        </label>
        <label className="field"><span>Resume (PDF, DOC, DOCX)</span>
          <input type="file" accept=".pdf,.doc,.docx" onChange={(e) => onResume(e.target.files?.[0])} />
          {candidate.resume_filename && <small>Current: {candidate.resume_filename}</small>}
        </label>
        <button className="btn" type="submit">Save profile</button>
      </form>

      <div className="card" style={{ marginTop: '1rem' }}>
        <h2>Job preferences</h2>
        <div className="grid grid-2">
          <label className="field"><span>Preferred location</span><input value={prefs.location || ''} onChange={(e) => setPrefs({ ...prefs, location: e.target.value })} /></label>
          <label className="field"><span>Work radius (km)</span><input type="number" value={prefs.radius_km ?? 25} onChange={(e) => setPrefs({ ...prefs, radius_km: Number(e.target.value) })} /></label>
          <label className="field"><span>Shift</span><input value={prefs.shift || ''} onChange={(e) => setPrefs({ ...prefs, shift: e.target.value })} /></label>
          <label className="field"><span>Job type</span><input value={prefs.job_type || ''} onChange={(e) => setPrefs({ ...prefs, job_type: e.target.value })} /></label>
          <label className="field"><span>Minimum pay</span><input type="number" value={prefs.minimum_pay ?? ''} onChange={(e) => setPrefs({ ...prefs, minimum_pay: Number(e.target.value) })} /></label>
          <label className="field"><span>Maximum pay</span><input type="number" value={prefs.maximum_pay ?? ''} onChange={(e) => setPrefs({ ...prefs, maximum_pay: Number(e.target.value) })} /></label>
        </div>
        <button className="btn" type="button" onClick={savePrefs} style={{ marginTop: 12 }}>Save preferences</button>
      </div>
    </div>
  )
}
