import { FormEvent, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { Candidate, apiError, candidatesApi } from '../services/api'

export default function AdminCandidatesPage() {
  const [items, setItems] = useState<Candidate[]>([])
  const [q, setQ] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [showAdd, setShowAdd] = useState(false)
  const [soundOn, setSoundOn] = useState(true)
  const audio = useRef<AudioContext | null>(null)

  const load = () => {
    candidatesApi.list({ q: q || undefined, limit: 100 }).then(setItems).catch((err) => setError(apiError(err)))
  }

  useEffect(() => {
    load()
  }, [])

  const toggleWorkflow = async (id: number, field: 'alert_sent' | 'applied' | 'interview_scheduled', value: boolean) => {
    try { const updated = await candidatesApi.update(id, { [field]: value }); setItems((current) => current.map((item) => item.id === id ? updated : item)); if (soundOn && field === 'alert_sent' && value) { audio.current ||= new AudioContext(); const oscillator = audio.current.createOscillator(); oscillator.connect(audio.current.destination); oscillator.frequency.value = 740; oscillator.start(); oscillator.stop(audio.current.currentTime + 0.16) } } catch (err) { setError(apiError(err)) }
  }

  const addCandidate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); const form = new FormData(event.currentTarget)
    try { const created = await candidatesApi.createAdmin({ name: String(form.get('name')), email: String(form.get('email') || ''), phone: String(form.get('phone') || ''), postal_code: String(form.get('postal_code') || ''), preferred_shift: String(form.get('preferred_shift') || ''), work_eligibility: String(form.get('work_eligibility') || ''), amazon_portal_link: String(form.get('amazon_portal_link') || ''), preferred_city: String(form.get('preferred_city') || '') }); setItems((current) => [created, ...current]); setShowAdd(false); event.currentTarget.reset() } catch (err) { setError(apiError(err)) }
  }

  return (
    <div className="page owner-page">
      <div className="page-header"><div><p className="eyebrow">OWNER CONTROL CENTER</p><h1>Candidate operations</h1><p className="lede">One view for every candidate, every signal, and every next step.</p></div><div className="owner-actions"><button className="btn secondary" type="button" onClick={() => setSoundOn((value) => !value)}>{soundOn ? '🔔 Alerts on' : '🔕 Alerts off'}</button><button className="btn" type="button" onClick={() => setShowAdd(true)}>+ Add candidate</button></div></div>
      {error && <div className="alert error">{error}</div>}
      <div className="card" style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <input placeholder="Search name, email, location" value={q} onChange={(e) => setQ(e.target.value)} />
        <button className="btn" type="button" onClick={load}>Search</button>
      </div>
      <div className="card table-wrap">
        <table>
          <thead>
            <tr><th>Candidate</th><th>Target</th><th>Eligibility</th><th>Workflow</th><th>Portal</th></tr>
          </thead>
          <tbody>
            {items.map((c) => (
              <tr key={c.id}>
                <td><Link to={`/admin/candidates/${c.id}`}>{c.name}</Link><small>{c.phone || c.email}</small></td>
                <td><strong>{c.postal_code || '—'}</strong><small>{c.preferred_shift || 'Shift open'}</small></td>
                <td><span className="badge active">{c.work_eligibility || 'Pending'}</span></td>
                <td><div className="workflow"><label><input type="checkbox" checked={!!c.alert_sent} onChange={(e) => toggleWorkflow(c.id, 'alert_sent', e.target.checked)} /> Alert</label><label><input type="checkbox" checked={!!c.applied} onChange={(e) => toggleWorkflow(c.id, 'applied', e.target.checked)} /> Applied</label><label><input type="checkbox" checked={!!c.interview_scheduled} onChange={(e) => toggleWorkflow(c.id, 'interview_scheduled', e.target.checked)} /> Interview</label></div></td>
                <td><div className="row-actions"><a className="btn small" href={c.amazon_portal_link || 'https://hiring.amazon.com'} target="_blank" rel="noreferrer">Open portal ↗</a><a className="whatsapp" href={`https://wa.me/923332158308?text=${encodeURIComponent(`TalentPath update for ${c.name}`)}`} target="_blank" rel="noreferrer">WhatsApp</a></div></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {showAdd && <div className="modal-backdrop"><form className="modal card" onSubmit={addCandidate}><div className="page-header"><div><p className="eyebrow">NEW RECORD</p><h2>Add candidate</h2></div><button className="icon-close" type="button" onClick={() => setShowAdd(false)}>×</button></div><div className="form-grid"><label className="field"><span>Full name</span><input name="name" required /></label><label className="field"><span>Email (optional)</span><input name="email" type="email" /></label><label className="field"><span>Phone</span><input name="phone" /></label><label className="field"><span>Target ZIP</span><input name="postal_code" /></label><label className="field"><span>Target city</span><input name="preferred_city" /></label><label className="field"><span>Shift</span><select name="preferred_shift"><option value="">Select shift</option><option>Day</option><option>Night</option><option>Weekend</option></select></label><label className="field"><span>Work eligibility</span><input name="work_eligibility" placeholder="Verified / Pending" /></label><label className="field"><span>Amazon portal link</span><input name="amazon_portal_link" type="url" /></label></div><button className="btn" type="submit">Create candidate</button></form></div>}
    </div>
  )
}
