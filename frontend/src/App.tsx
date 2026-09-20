import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './hooks/useAuth'
import ProtectedRoute from './components/ProtectedRoute'
import AppLayout from './layouts/AppLayout'
import PublicLayout from './layouts/PublicLayout'
import HomePage from './pages/HomePage'
import AboutPage from './pages/AboutPage'
import ServicesPage from './pages/ServicesPage'
import ContactPage from './pages/ContactPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import JobsPage from './pages/JobsPage'
import JobDetailPage from './pages/JobDetailPage'
import ProfilePage from './pages/ProfilePage'
import ApplicationsPage from './pages/ApplicationsPage'
import NotificationsPage from './pages/NotificationsPage'
import AdminJobsPage from './pages/AdminJobsPage'
import AdminJobFormPage from './pages/AdminJobFormPage'
import AdminCustomJobsPage from './pages/AdminCustomJobsPage'
import AdminCandidatesPage from './pages/AdminCandidatesPage'
import AdminCandidateDetailPage from './pages/AdminCandidateDetailPage'
import AdminApplicationsPage from './pages/AdminApplicationsPage'
import ErrorBoundary from './components/ErrorBoundary'

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
          <Route element={<PublicLayout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/services" element={<ServicesPage />} />
            <Route path="/contact" element={<ContactPage />} />
          </Route>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/jobs" element={<JobsPage />} />
            <Route path="/jobs/:jobId" element={<JobDetailPage />} />
            <Route
              path="/profile"
              element={
                <ProtectedRoute roles={['candidate']}>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/applications"
              element={
                <ProtectedRoute roles={['candidate']}>
                  <ApplicationsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/notifications"
              element={
                <ProtectedRoute roles={['candidate']}>
                  <NotificationsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <ProtectedRoute roles={['admin']}>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/jobs"
              element={
                <ProtectedRoute roles={['admin']}>
                  <AdminJobsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/jobs/new"
              element={
                <ProtectedRoute roles={['admin']}>
                  <AdminJobFormPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/jobs/:jobId/edit"
              element={
                <ProtectedRoute roles={['admin']}>
                  <AdminJobFormPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/manage-jobs"
              element={
                <ProtectedRoute roles={['admin']}>
                  <AdminCustomJobsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/candidates"
              element={
                <ProtectedRoute roles={['admin']}>
                  <AdminCandidatesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/candidates/:candidateId"
              element={
                <ProtectedRoute roles={['admin']}>
                  <AdminCandidateDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/applications"
              element={
                <ProtectedRoute roles={['admin']}>
                  <AdminApplicationsPage />
                </ProtectedRoute>
              }
            />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  )
}
