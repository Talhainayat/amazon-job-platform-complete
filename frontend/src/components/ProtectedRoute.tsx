import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Role } from '../services/api'

export default function ProtectedRoute({
  children,
  roles,
}: {
  children: JSX.Element
  roles?: Role[]
}) {
  const { token, role, ready } = useAuth()
  if (!ready) return <div className="page">Loading…</div>
  if (!token) return <Navigate to={roles?.includes('admin') ? '/login?role=admin' : '/login'} replace />
  if (roles && role && !roles.includes(role)) return <Navigate to={role === 'admin' ? '/admin' : '/dashboard'} replace />
  return children
}
