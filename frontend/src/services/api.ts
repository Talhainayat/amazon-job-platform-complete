import axios, { AxiosError } from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default api

export type Role = 'admin' | 'candidate'

export function apiError(err: unknown, fallback = 'Something went wrong'): string {
  const ax = err as AxiosError<{ detail?: string | string[] }>
  const detail = ax.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.join(' ')
  return fallback
}

export interface LoginResponse {
  access_token: string
  token_type: string
  role: Role
}

export interface MeResponse {
  id: number
  email: string
  role: Role
  candidate_id?: number | null
  name?: string | null
}

export interface Candidate {
  id: number
  name: string
  email: string
  phone?: string
  location?: string
  city?: string
  province?: string
  postal_code?: string
  preferred_city?: string
  preferred_shift?: string
  job_type?: string
  skills?: string[]
  years_experience?: number
  experience?: string
  education?: string
  availability?: string
  has_vehicle?: boolean
  amazon_portal_link?: string
  work_eligibility?: string
  alert_sent?: boolean
  applied?: boolean
  interview_scheduled?: boolean
  status: string
  resume_filename?: string
  has_resume?: boolean
  profile_completion?: number
  created_at: string
  updated_at: string
}

export interface CandidatePreferences {
  id: number
  candidate_id: number
  location?: string
  radius_km: number
  shift?: string
  job_type?: string
  minimum_pay?: number
  maximum_pay?: number
  availability?: string
  has_vehicle?: boolean
  years_experience?: number
}

export interface Job {
  id: number
  title: string
  company?: string
  description?: string
  requirements?: string
  location?: string
  city?: string
  province?: string
  postal_code?: string
  shift?: string
  job_type?: string
  skills?: string[]
  years_experience?: number
  openings?: number
  pay_min?: number
  pay_max?: number
  pay_period?: string
  application_deadline?: string
  source: string
  external_job_id?: string
  job_url?: string
  status: string
  posted_at?: string
  created_at: string
  updated_at: string
  match_score?: number | null
  match_explanation?: string[] | null
  distance_km?: number | null
  distance_known?: boolean | null
  already_applied?: boolean | null
  application_status?: string | null
  is_custom?: boolean
  application_url?: string
  badge_status?: string
  is_active?: boolean
  image_url?: string
}

export interface JobListResponse {
  items: Job[]
  total: number
  page: number
  page_size: number
}

export interface Match {
  id: number
  candidate_id: number
  job_id: number
  match_score: number
  matched_criteria: Record<string, unknown>
  unmatched_criteria: Record<string, unknown>
  explanation: string[]
  distance_km?: number | null
  distance_known?: boolean
  status: string
  matched_at: string
  job_title?: string
  company?: string
  location?: string
}

export interface Application {
  id: number
  candidate_id: number
  job_id: number
  status: string
  applied_at?: string
  notes?: string
  interview_status: string
  interview_date?: string
  created_at: string
  updated_at: string
  job?: { id: number; title: string; company?: string; location?: string; status: string }
  candidate?: { id: number; name: string; email: string; phone?: string; location?: string }
  match_score?: number | null
}

export interface NotificationItem {
  id: number
  title?: string
  message?: string
  notification_type?: string
  is_read: boolean
  created_at: string
  job_id?: number | null
}

export interface AdminSummary {
  total_candidates: number
  active_candidates: number
  total_jobs: number
  open_jobs: number
  closed_jobs: number
  total_matches: number
  total_applications: number
  pending_applications: number
  interviews: number
  hires: number
  average_match_score: number
  total_notifications: number
  recent_activity: { type: string; id: number; label: string; status: string; created_at: string }[]
  recent_jobs: { id: number; title: string; status: string; location?: string }[]
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>('/auth/login', { email, password })
  return data
}

export async function registerCandidate(payload: {
  email: string
  password: string
  name: string
  phone?: string
  location?: string
  postal_code?: string
  preferred_shift?: string
  work_eligibility?: string
  amazon_portal_link?: string
}): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>('/auth/register', payload)
  return data
}

export async function me(): Promise<MeResponse> {
  const { data } = await api.get<MeResponse>('/auth/me')
  return data
}

export async function logoutApi(): Promise<void> {
  try {
    await api.post('/auth/logout')
  } catch {
    /* token is cleared locally either way */
  }
}

export const jobsApi = {
  list: (params?: Record<string, string | number | undefined>) =>
    api.get<JobListResponse>('/jobs', { params }).then((r) => r.data),
  get: (id: number) => api.get<Job>(`/jobs/${id}`).then((r) => r.data),
  create: (payload: Partial<Job>) => api.post<Job>('/jobs', payload).then((r) => r.data),
  update: (id: number, payload: Partial<Job>) => api.patch<Job>(`/jobs/${id}`, payload).then((r) => r.data),
  publish: (id: number) => api.post<Job>(`/jobs/${id}/publish`).then((r) => r.data),
  close: (id: number) => api.post<Job>(`/jobs/${id}/close`).then((r) => r.data),
  reopen: (id: number) => api.post<Job>(`/jobs/${id}/reopen`).then((r) => r.data),
  archive: (id: number) => api.post<Job>(`/jobs/${id}/archive`).then((r) => r.data),
  // Custom jobs management
  listCustom: (params?: Record<string, string | number | undefined>) =>
    api.get<JobListResponse>('/jobs/custom/list/all', { params }).then((r) => r.data),
  createCustom: (payload: Partial<Job>) => api.post<Job>('/jobs/custom/create', payload).then((r) => r.data),
  updateCustom: (id: number, payload: Partial<Job>) => api.patch<Job>(`/jobs/custom/${id}`, payload).then((r) => r.data),
  deleteCustom: (id: number) => api.delete(`/jobs/custom/${id}`).then(() => undefined),
  toggleCustomActive: (id: number) => api.post<Job>(`/jobs/custom/${id}/toggle`).then((r) => r.data),
}

export const candidatesApi = {
  list: (params?: Record<string, string | number | undefined>) =>
    api.get<Candidate[]>('/candidates', { params }).then((r) => r.data),
  get: (id: number) => api.get<Candidate>(`/candidates/${id}`).then((r) => r.data),
  me: () => api.get<Candidate>('/candidates/me').then((r) => r.data),
  update: (id: number, payload: Partial<Candidate>) =>
    api.patch<Candidate>(`/candidates/${id}`, payload).then((r) => r.data),
  getPreferences: (id: number) =>
    api.get<CandidatePreferences>(`/candidates/${id}/preferences`).then((r) => r.data),
  savePreferences: (id: number, payload: Partial<CandidatePreferences>) =>
    api.put<CandidatePreferences>(`/candidates/${id}/preferences`, payload).then((r) => r.data),
  uploadResume: (id: number, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post<Candidate>(`/candidates/${id}/resume`, form).then((r) => r.data)
  },
  overview: (id: number) => api.get(`/candidates/${id}/overview`).then((r) => r.data),
  createAdmin: (payload: {
    name: string
    email?: string
    phone?: string
    postal_code?: string
    preferred_shift?: string
    work_eligibility?: string
    amazon_portal_link?: string
    preferred_city?: string
  }) => api.post<Candidate>('/candidates/admin-create', payload).then((r) => r.data),
}

export const contactApi = {
  create: (payload: { name: string; email: string; phone?: string; message: string }) =>
    api.post('/contact/inquiries', payload).then((r) => r.data),
}

export const applicationsApi = {
  list: (params?: Record<string, string | number | undefined>) =>
    api.get<{ items: Application[]; total: number; page: number; page_size: number }>('/applications', { params }).then((r) => r.data),
  listForCandidate: (candidateId: number) =>
    api.get<Application[]>(`/applications/candidates/${candidateId}`).then((r) => r.data),
  create: (jobId: number, candidateId?: number, notes?: string) =>
    api.post<Application>('/applications', { job_id: jobId, candidate_id: candidateId, notes }).then((r) => r.data),
  update: (id: number, payload: Partial<Application>) =>
    api.patch<Application>(`/applications/${id}`, payload).then((r) => r.data),
}

export const matchesApi = {
  listForCandidate: (candidateId: number) =>
    api.get<Match[]>(`/matches/candidates/${candidateId}`).then((r) => r.data),
  recalculate: (candidateId: number) =>
    api.post<Match[]>(`/matches/candidates/${candidateId}/recalculate`).then((r) => r.data),
}

export const notificationsApi = {
  me: () => api.get<{ items: NotificationItem[]; unread_count: number; total: number }>('/notifications/me').then((r) => r.data),
  unread: () => api.get<{ unread_count: number }>('/notifications/unread-count').then((r) => r.data),
  markRead: (id: number) => api.post(`/notifications/${id}/read`).then((r) => r.data),
  markAll: () => api.post('/notifications/read-all'),
}

export const adminApi = {
  summary: () => api.get<AdminSummary>('/admin/summary').then((r) => r.data),
  sites: () => api.get<ManagedSite[]>('/admin/sites').then((r) => r.data),
  createSite: (payload: Omit<ManagedSite, 'id'>) => api.post<ManagedSite>('/admin/sites', payload).then((r) => r.data),
  updateSite: (id: number, payload: Omit<ManagedSite, 'id'>) => api.patch<ManagedSite>(`/admin/sites/${id}`, payload).then((r) => r.data),
}

export interface ManagedSite {
  id: number
  name: string
  postal_code?: string
  portal_url?: string
  feed_enabled: boolean
  available_slots: number
}

export function payLabel(job: Job): string {
  if (job.pay_min && job.pay_max) return `$${job.pay_min}–$${job.pay_max}${job.pay_period ? `/${job.pay_period}` : ''}`
  if (job.pay_min) return `From $${job.pay_min}`
  return 'Pay not listed'
}
