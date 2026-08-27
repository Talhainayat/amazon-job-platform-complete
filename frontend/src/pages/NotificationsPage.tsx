import { useEffect, useState } from 'react'
import { NotificationItem, apiError, notificationsApi } from '../services/api'

export default function NotificationsPage() {
  const [items, setItems] = useState<NotificationItem[]>([])
  const [unread, setUnread] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const load = () => {
    notificationsApi
      .me()
      .then((res) => {
        setItems(res.items)
        setUnread(res.unread_count)
      })
      .catch((err) => setError(apiError(err)))
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Notifications</h1>
          <p className="lede">{unread} unread</p>
        </div>
        <button className="btn secondary" type="button" onClick={async () => { await notificationsApi.markAll(); load() }}>
          Mark all read
        </button>
      </div>
      {error && <div className="alert error">{error}</div>}
      {items.length === 0 && <div className="card empty">You are all caught up.</div>}
      <div className="grid">
        {items.map((item) => (
          <button
            key={item.id}
            className="card"
            style={{ textAlign: 'left', opacity: item.is_read ? 0.7 : 1 }}
            onClick={async () => {
              await notificationsApi.markRead(item.id)
              load()
            }}
            type="button"
          >
            <strong>{item.title || 'Update'}</strong>
            <p>{item.message}</p>
            <small className="notice">{new Date(item.created_at).toLocaleString()}</small>
          </button>
        ))}
      </div>
    </div>
  )
}
