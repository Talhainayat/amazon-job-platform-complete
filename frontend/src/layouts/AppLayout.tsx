import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { notificationsApi } from '../services/api'
import { AdminTheme, useAdminTheme } from '../hooks/useAdminTheme'

export default function AppLayout() {
  const { role, logout, name, email } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const [unread, setUnread] = useState(0)
  const { theme, setTheme } = useAdminTheme()

  useEffect(() => {
    notificationsApi.unread().then((r) => setUnread(r.unread_count)).catch(() => {})
  }, [])

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const links =
    role === 'admin'
      ? [
          ['/dashboard', 'Dashboard'],
          ['/jobs', 'Jobs'],
          ['/admin/jobs', 'Manage jobs'],
          ['/admin/manage-jobs', 'Custom Jobs'],
          ['/admin/candidates', 'Candidates'],
          ['/admin/applications', 'Applications'],
        ]
      : [
          ['/dashboard', 'Dashboard'],
          ['/applications', 'Applications'],
          ['/profile', 'Profile'],
          ['/notifications', 'Notifications'],
        ]

  return (
    <div className="app-shell">
      <header className="topbar">
        <Link className="brand" to="/">
          <span className="brand-mark">JP</span>
          TalentPath
        </Link>
        <button className="btn ghost menu-toggle" onClick={() => setOpen((v) => !v)} type="button">
          Menu
        </button>
        <nav className={`nav-links ${open ? 'open' : ''}`} onClick={() => setOpen(false)}>
          {links.map(([to, label]) => (
            <NavLink key={to} to={to} end={to === '/'}>
              {label}
              {label === 'Notifications' && unread > 0 ? ` (${unread})` : ''}
            </NavLink>
          ))}
        </nav>
        <div className="topbar-spacer">
          {role === 'admin' && <select className="theme-select" value={theme} onChange={(event) => setTheme(event.target.value as AdminTheme)} aria-label="Dashboard theme"><option value="light">Light</option><option value="dark">Dark</option><option value="blue">Midnight blue</option></select>}
          <span className="notice" style={{ color: '#cbd5e1' }}>
            {name || email}
          </span>
          <button className="btn secondary" type="button" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>
      <Outlet />
    </div>
  )
}
