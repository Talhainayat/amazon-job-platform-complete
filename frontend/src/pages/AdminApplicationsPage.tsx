import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Application, apiError, applicationsApi } from '../services/api'

const STATUSES = ['applied', 'reviewing', 'shortlisted', 'interview', 'offer', 'hired', 'rejected']
const LANES = [{ label: 'New', status: 'saved' }, { label: 'Matched', status: 'shortlisted' }, { label: 'Alert Sent', status: 'reviewing' }, { label: 'Applied', status: 'applied' }, { label: 'Hired', status: 'hired' }]

export default function AdminApplicationsPage() {
  const [items, setItems] = useState<Application[]>([])
  const [q, setQ] = useState('')
  const [status, setStatus] = useState('')
  const [error, setError] = useState<string | null>(null)

  const load = () => {
    applicationsApi
      .list({ q: q || undefined, status_filter: status || undefined, page_size: 50 })
      .then((res) => setItems(res.items))
      .catch((err) => setError(apiError(err)))
  }

  useEffect(() => {
    load()
  }, [])

  const update = async (app: Application, next: string) => {
    await applicationsApi.update(app.id, { status: next })
    load()
  }

  const drop = async (event: React.DragEvent<HTMLElement>, next: string) => {
    event.preventDefault()
    const app = items.find((item) => item.id === Number(event.dataTransfer.getData('application/id')))
    if (app && app.status !== next) await update(app, next)
  }

  return (
    <div className="page placement-page">
      <div className="page-header"><div><p className="eyebrow">PLACEMENT PIPELINE</p><h1>Applications tracker</h1><p className="lede">Move candidates forward as the placement desk works each opportunity.</p></div></div>
      {error && <div className="alert error">{error}</div>}
      <div className="card" style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
        <input placeholder="Search candidate or job" value={q} onChange={(e) => setQ(e.target.value)} />
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All</option>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <button className="btn" type="button" onClick={load}>Filter</button>
      </div>
      <div className="kanban-board">{LANES.map((lane) => <section className="kanban-lane" key={lane.status} onDragOver={(event) => event.preventDefault()} onDrop={(event) => drop(event, lane.status)}><div className="kanban-lane-header"><strong>{lane.label}</strong><span>{items.filter((app) => app.status === lane.status).length}</span></div>{items.filter((app) => app.status === lane.status).map((app) => <article className="kanban-card" draggable onDragStart={(event) => event.dataTransfer.setData('application/id', String(app.id))} key={app.id}><div className="kanban-card-top"><span className={`badge ${app.status}`}>{app.status}</span><span>#{app.id}</span></div><Link to={app.candidate ? `/admin/candidates/${app.candidate.id}` : '/admin/candidates'}><strong>{app.candidate?.name || `Candidate ${app.candidate_id}`}</strong></Link><p>{app.job?.title || `Job #${app.job_id}`}</p><select value={app.status} onChange={(event) => update(app, event.target.value)} aria-label={`Update ${app.candidate?.name || 'application'} status`}>{STATUSES.map((statusOption) => <option key={statusOption} value={statusOption}>{statusOption}</option>)}</select></article>)}</section>)}</div>
    </div>
  )
}
