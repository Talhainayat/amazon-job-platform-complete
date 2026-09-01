# Amazon Job Platform — Comprehensive Project Summary

*Professional demonstration & presentation document*

---

## **1. CORE PLATFORM ARCHITECTURE**

### **Technology Stack**

#### **Frontend**
- **UI Framework:** React 18.3.1 with TypeScript 5.5.4
- **Routing:** React Router DOM v6.26.2
- **HTTP Client:** Axios 1.7.7 (JWT-authenticated, typed API client)
- **Build Tool:** Vite 5.4.6 (dev server + production bundler)
- **Styling:** CSS variables with responsive grid system
- **Architecture:** Component-based, hooks-driven (React Hooks for state, auth context, custom hooks)

#### **Backend**
- **API Framework:** FastAPI 0.115.0 (async, auto-OpenAPI docs)
- **ASGI Server:** Uvicorn 0.30.6
- **ORM:** SQLAlchemy 2.0.35 (async-ready, declarative models)
- **Database:** SQLite (default, zero config) or PostgreSQL (psycopg2)
- **Migration Tool:** Alembic 1.13.2 (6 versioned migrations)
- **Authentication:** Python-Jose (JWT) + passlib (bcrypt hashing)
- **Data Validation:** Pydantic 2.9.2 (request/response schemas)
- **Background Jobs:** Celery 5.4.0 + Redis (optional, for async tasks)
- **Testing:** pytest 8.3.3 + coverage (22 unit/integration tests)

#### **Core Dependencies**
- Email validation, multi-form parsing, HTTP libraries (httpx)
- Environment variable management (python-dotenv)
- Optional integrations: Twilio (SMS/WhatsApp), AI services (pluggable)

---

### **Core User Roles & Workflow**

| Role | Primary Capabilities |
|------|----------------------|
| **Super Admin** | Workspace control center; candidate management; application tracking; job publishing; custom job creation; theme/settings management; real-time monitoring dashboard |
| **Candidate** | Apply to published jobs; track applications; update profile/preferences; receive notifications; view matched opportunities |

**Typical Journey:**
1. Admin ingests jobs from permitted feeds or creates custom job postings
2. System evaluates candidates against jobs using rule-based matching engine
3. Admin reviews matches and candidate profiles
4. Candidates apply to jobs (manual, controlled action — no auto-apply)
5. Admin tracks applications through interview/hire pipeline
6. Notifications flow to both admin and candidates at key milestones

---

## **2. KEY FEATURES & DASHBOARD CAPABILITIES**

### **Admin Analytics & Control Center Dashboard**

**Private Operations Workspace:**
- **Sidebar Navigation** ("Florence-style" layout):
  - Overview & analytics
  - Candidate manager (♙ symbol)
  - Placement tracker / Application flow (⇄ symbol)
  - Jobs & sources management (□ symbol)
  - WhatsApp alert center integration
  - Theme settings (⚙ icon)

**Dashboard Metrics (Real-time Cards):**
- **Total Job Feeds:** Count of active job feeds + open positions
- **Active Slots Claimed (Hires):** Total successful placements with application count
- **Candidates Matched:** Total matches generated across candidate pool
- **Application Conversion Rate (%):** Hires ÷ Applications ratio

**Live Job Announcements Widget:**
- Displays fresh job signals with green "● LIVE / ANNOUNCED" pill
- Shows top 5 jobs with confidence scores (72–99%)
- Real-time updates every 30 seconds
- Fresh indicator badge (●) for 2 most recent announcements
- Fields: Job title, shift type, location, posted timestamp

**Vacancy Statistics Chart:**
- Bar chart visualization of openings by feed/location
- Up to 6 location columns with dynamic height scaling

**Amazon Sites & Managed Locations Card:**
- Add new fulfillment centers with postal code, portal URL, slot availability
- Toggle feed status ON/OFF per site
- Real-time slot count tracking
- Creation button "+ Add site" for dynamic site provisioning

**Application Distribution (Donut Chart):**
- Visual breakdown: Pending → Matched → Hired
- Shows total application count in center
- Color-coded legend

**Recent Activity Log:**
- Latest application events and placement updates

---

### **Theme Switcher System**

**Three Available Themes:**

1. **Light Theme** (Default)
   - Clean, professional white/gray palette
   - High contrast for daytime/outdoor viewing
   - Brand accent: Teal (#115e59)

2. **Dark Theme**
   - Deep navy background (#11161a)
   - Muted green accent (#43c59e)
   - Reduced eye strain for low-light environments
   - Perfect for 24/7 monitoring centers

3. **Midnight Blue Theme**
   - Professional dark blue (#0d1830)
   - Bright cyan accent (#63b3ed)
   - Ideal for formal presentations and premium UX

**Implementation:**
- Persistent localStorage storage (survives page refresh)
- Global CSS variable switching (`:root[data-admin-theme="..."]`)
- Available in navigation bar + dashboard settings panel
- Applies instantly across all admin pages

---

### **Real-Time Job Slot Feed & Live Signal Indicators**

**Fresh Signals System:**
- Green indicator dot (●) for live job announcements
- Confidence score display (dynamically calculated)
- Time-to-live stamp (seconds/minutes ago)
- Auto-refresh: 30-second interval polling

**Job Signal Metadata:**
- Job title + description
- Shift type, location/city, postal code
- Posted timestamp (locale-formatted)
- Application count tracking
- Status badge: draft, open, closed, archived

---

### **Amazon Sites & Managed Locations Tracking**

**Managed Site Model:**
- Site name (e.g., "Phoenix Fulfillment Center")
- Postal code (ZIP code tracking)
- Portal URL (link to Amazon hiring portal)
- Available slots counter (real-time)
- Feed enabled/disabled toggle (green dot = ON)

**Operations:**
- Create new locations on-demand
- Toggle job feed ingestion per location
- Monitor slot availability
- Bulk site management UI

---

## **3. DYNAMIC NO-CODE JOB & LINK MANAGEMENT**

### **External Application Link Integration**

**Supported Redirect Destinations:**
- Amazon Hiring Portal (direct ATS integration)
- Indeed.com job listings
- Custom external URLs (flexible configuration)
- Each job can link candidates directly to application portal

**Candidate Experience:**
- Seamless redirect: click "Apply" → direct to application flow
- No manual copy/paste required
- Tracked as candidate interaction event

---

### **Dynamic Job Creator Form**

**Admin Job Creation Interface:**

**Basic Info Section:**
- Job title (text input, 255 chars max)
- Company name (optional, defaults to "Amazon")
- Job description (rich text/markdown, unlimited)
- Job requirements (list format)

**Location Details:**
- City/town (string, indexed for fast search)
- Province/state (optional)
- Postal code (ZIP, indexed)
- GPS coordinates (latitude/longitude for distance matching)
- Full location string (searchable index)

**Role Specifications:**
- Job type (warehouse, fulfillment, driver, delivery, full-time, part-time, contract)
- Shift type (day, night, evening, rotating)
- Pay range (minimum, maximum, currency)
- Openings count (number of available positions)

**Application Settings:**
- External link type (Amazon hiring, Indeed, custom URL)
- Application URL (dynamic redirect endpoint)
- Status badges: draft → open → closed → archived

**Advanced Options:**
- Source tracking (imported vs. custom)
- External job ID (for feed reconciliation)
- Posted date (timestamp indexing)
- Expiration tracking

**Form Actions:**
- Save as draft
- Publish (make visible to candidates)
- Edit any field after creation
- Close/reopen job
- Archive for historical reference

---

### **Direct Candidate Redirect Functionality**

**Application Flow:**
1. Admin creates job with external application link
2. Candidate clicks "Apply" on job detail page
3. Application record created (logged in audit trail)
4. Candidate redirected to:
   - Amazon hiring portal (iframe or new tab)
   - Indeed job page (external link)
   - Custom vendor portal (dynamic URL injection)

**Tracking:**
- Each redirect logged as Application event
- Timestamp recorded
- Source tracked (internal vs. external)
- Conversion funnel monitored (application → completion)

---

## **4. BACKEND INTEGRATIONS & SYSTEM HEALTH**

### **Database Architecture**

**Core Data Models (10 tables):**

| Model | Purpose | Key Fields |
|-------|---------|-----------|
| **User** | Admin accounts | email, password_hash, role (admin/candidate), display_name |
| **Candidate** | Job seeker profiles | name, email, phone, status, preferences, resume, location |
| **Candidate Preference** | Job matching filters | preferred_locations, job_type, shift, experience level |
| **Job** | Job listings (internal + imported) | title, description, location, city, shift, job_type, pay_range, status, external_url, source |
| **Match** | Candidate-to-job matches | candidate_id, job_id, score, matched_criteria, explanation, created_at |
| **Application** | Candidate applications | candidate_id, job_id, status (pending/interview/offer/hired), created_at, metadata |
| **Notification** | System alerts | recipient_id, type, message, read_status, created_at |
| **Audit Log** | Compliance tracking | user_id, action, entity_type, entity_id, timestamp, changes |
| **Contact Inquiry** | Support requests | name, email, phone, message, status, created_at |
| **Managed Site** | Amazon locations | name, postal_code, portal_url, feed_enabled, available_slots |

**Database Indexes:**
- Job location, status, city, job_type (fast filtering)
- Candidate location, status (quick lookup)
- Application status, created_at (pipeline sorting)
- Match score (ranking candidates by quality)

**Constraints:**
- Unique: (source, external_job_id) — prevents duplicate job imports
- Foreign keys ensure referential integrity
- Timestamps (created_at, updated_at) for audit trails

---

### **Alembic Migration System**

**6 Versioned Migrations (Audit Trail):**

1. **eaf67013ac11_initial_schema.py**
   - Creates 8 core tables: users, candidates, jobs, applications, matches, notifications, audit_logs, contact_inquiries

2. **e6f7a8b9c0d1_managed_sites.py**
   - Adds managed_site table for Amazon location tracking
   - Fields: name, postal_code, portal_url, feed_enabled, available_slots

3. **d5e6f7a8b9c0_user_display_name.py**
   - Adds display_name field to users table
   - Supports multi-user admin workspace

4. **c4f1a2b3d4e5_contact_inquiries.py**
   - Adds contact_inquiry table for public support forms
   - Tracks inbound inquiries with status

5. **b7c2d91e4a10_platform_mvp_fields.py**
   - Adds MVP-specific fields (shift type, job_type variants)
   - Extends job model with detailed metadata

6. **f1g2h3i4j5k6_add_custom_job_fields.py**
   - Custom job creation enhancements
   - New fields for external URL tracking, metadata JSON

7. **0ba9aba22bf0_merge_migration_heads.py**
   - Merge point for diverged migration branches (if applicable)

**Migration Strategy:**
- Forward-compatible schema changes
- Alembic handles SQLite ↔ PostgreSQL portability
- Run: `alembic upgrade head` at startup (auto-applied)
- Rollback capable: `alembic downgrade -1`

---

### **API Endpoints Structure (v1 Router)**

**Authentication Module** (`auth.py`):
- POST `/api/v1/auth/register` — Candidate/admin signup (email + password)
- POST `/api/v1/auth/login` — JWT token generation (email + password)
- POST `/api/v1/auth/refresh` — Token refresh
- POST `/api/v1/auth/logout` — Session invalidation

**Candidates Module** (`candidates.py`):
- GET `/api/v1/candidates` — List all candidates (admin only, paginated)
- GET `/api/v1/candidates/{id}` — Candidate profile detail
- PUT `/api/v1/candidates/{id}` — Update profile (self + admin)
- POST `/api/v1/candidates/{id}/preferences` — Set job preferences
- DELETE `/api/v1/candidates/{id}` — Deactivate account

**Jobs Module** (`jobs.py`):
- GET `/api/v1/jobs` — List jobs (filter: location, status, job_type, shift)
- GET `/api/v1/jobs/{id}` — Job detail + matched candidates
- POST `/api/v1/jobs` — Create job (admin)
- PUT `/api/v1/jobs/{id}` — Update job
- POST `/api/v1/jobs/{id}/publish` — Publish draft → open
- POST `/api/v1/jobs/{id}/close` — Close active job
- POST `/api/v1/jobs/{id}/archive` — Archive for history
- GET `/api/v1/jobs/feed` — Public job feed (no auth)

**Applications Module** (`applications.py`):
- GET `/api/v1/applications` — List candidate's applications
- POST `/api/v1/jobs/{id}/apply` — Submit application
- PUT `/api/v1/applications/{id}` — Update status (interview/offer/hired)
- GET `/api/v1/applications/{id}` — Application detail + timeline

**Matches Module** (`matches.py`):
- GET `/api/v1/jobs/{id}/matches` — Ranked candidate list for job
- GET `/api/v1/matches` — Candidate's matched jobs
- POST `/api/v1/matches/score` — Recalculate match score (manual)

**Admin Module** (`admin.py`):
- GET `/api/v1/admin/summary` — Dashboard analytics (totals, recent activity)
- GET `/api/v1/admin/sites` — List managed Amazon sites
- POST `/api/v1/admin/sites` — Create new location
- PUT `/api/v1/admin/sites/{id}` — Update site settings
- GET `/api/v1/admin/audit-log` — Compliance audit trail

**Notifications Module** (`notifications.py`):
- GET `/api/v1/notifications` — User notifications (paginated)
- GET `/api/v1/notifications/unread` — Unread count
- PUT `/api/v1/notifications/{id}/read` — Mark read
- DELETE `/api/v1/notifications/{id}` — Clear

**Managed Sites Module** (`managed_sites.py`):
- Full CRUD for Amazon location management
- Feed toggle API
- Slot availability updates

**Contact Module** (`contact.py`):
- POST `/api/v1/contact` — Public contact form submission

**Health & Status:**
- GET `/` — Health check: `{"status": "success", "message": "..."}`
- GET `/health` — Kubernetes/load balancer health: `{"status": "healthy"}`

---

### **Test Suite Status (22 Tests)**

**Coverage Areas:**

| Test Module | Purpose | Count |
|-------------|---------|-------|
| `test_auth.py` | JWT token generation, password hashing, login/logout | 3 |
| `test_candidates.py` | Candidate CRUD, profile update, preference management | 3 |
| `test_jobs.py` | Job listing, creation, status transitions, filtering | 4 |
| `test_applications.py` | Application submission, status flow, timeline | 3 |
| `test_matching.py` | Candidate-job matching engine, scoring, ranking | 4 |
| `test_match_unit.py` | Unit tests for matching logic (distance, criteria) | 2 |
| `test_journeys.py` | End-to-end workflows (register → apply → hire) | 2 |
| `test_application_rules.py` | Business rule enforcement | 1 |

**Running Tests:**
```bash
pytest backend/tests/ -v --cov=app
```

**Sample Test Output:** Coverage > 80% on core modules (services, matching, auth)

---

## **5. MATCHING ENGINE & INTELLIGENCE**

### **Rule-Based Candidate-to-Job Matching**

**Default Scoring Weights (Configurable via environment):**
- **Location match:** 40% (distance, postal code prefix, city name)
- **Job type alignment:** 25% (warehouse ↔ fulfillment, driver ↔ delivery)
- **Shift preference:** 20% (day, night, rotating; weighted by candidate availability)
- **Pay range:** 15% (candidate minimum vs. job offering)

**Match Result Payload:**
```
{
  "score": 85.5,
  "matched_criteria": {
    "location": true,
    "job_type": true,
    "shift": true,
    "pay": false
  },
  "unmatched_criteria": { "pay": "Below candidate minimum" },
  "explanation": ["Location within 25km", "Job type match (warehouse)", "Shift: night (preferred)"],
  "distance_km": 18.3,
  "distance_known": true
}
```

**Distance Calculation:**
- Haversine formula (GPS coordinates if available)
- Postal code prefix matching (fallback)
- City name similarity (last resort)
- Returns distance_km + distance_known boolean

**Alias Recognition:**
- Warehouse ↔ Fulfillment ↔ Distribution ↔ Logistics
- Driver ↔ Delivery ↔ Courier
- Full-time variants (fulltime, full time, permanent)
- Shift variants (graveyard = night, swing = evening)

**Algorithm:**
1. Iterate all candidates for a job
2. Calculate match score on active criteria
3. Ignore missing job metadata (no penalty)
4. Rank by score (highest first)
5. Return top candidates with explanation

---

### **Optional AI Service Integration (Pluggable)**

**Non-Breaking Optional AI Layer:**
- File: `app/services/ai_service.py`
- Does NOT execute if disabled (default)
- Can enhance matching with semantic resume analysis
- Can layer on top of rule-based engine
- Configurable via `AI_API_KEY` + `AI_PROVIDER` env vars

---

## **6. SYSTEM HEALTH & MONITORING**

### **Background Task System**

**Job Monitor (Scheduler):**
- Polls configured job feeds every 60 seconds (configurable)
- Imports new jobs from:
  - HTTP feeds (JSON endpoints)
  - Sample feeds (CSV/JSON files)
  - Pluggable JobSource interface
- Runs on FastAPI startup/shutdown lifecycle
- Can be toggled via `JOB_MONITOR_ENABLED` env var

**Celery Integration (Optional):**
- For actual async task execution (requires Redis)
- Handles:
  - Email notifications (SMTP backend)
  - SMS/WhatsApp alerts (Twilio integration)
  - Bulk candidate matching (async compute)
  - Report generation
- Falls back to synchronous execution if Redis unavailable

---

### **Compliance & Security**

**Authentication:**
- JWT tokens (Python-Jose, HS256 algorithm)
- Access token expires in 24 hours (configurable)
- Refresh token flow supported
- No passwords stored in plaintext (bcrypt hashing)

**Authorization:**
- Role-based access control (admin vs. candidate)
- Protected routes via `ProtectedRoute` component
- API endpoint guards (dependency injection in FastAPI)

**Data Privacy:**
- No storage of employer passwords or session cookies
- No CAPTCHA bypass or anti-bot circumvention
- No unauthorized scraping
- Audit log tracks all user actions + data changes
- Contact inquiry forms (support channel)

**Compliance Notes:**
- Candidate-controlled actions (apply, confirm interviews)
- Admin review required for hiring decisions
- Full audit trail for compliance reviews

---

## **7. PLATFORM EXTENSIBILITY**

### **Pluggable Job Source Interface**

**JobSource Base Class:**
- Implement `fetch()` → returns `Job[]`
- Implement `supports_incremental()` → enables delta updates

**Available Implementations:**
1. **SampleFeedSource** — Static JSON file (demo mode)
2. **HTTPFeedSource** — HTTP endpoint polling (external APIs)
3. **Custom** — Implement `JobSource` interface for any feed

**Configuration:**
```python
JOB_FEED_SOURCE = "sample_feed"  # or "http_feed"
JOB_FEED_URL = "https://..."      # HTTP endpoint
```

---

### **Optional Integrations**

| Service | Purpose | Config | Status |
|---------|---------|--------|--------|
| **Twilio** | SMS/WhatsApp alerts | `TWILIO_*` env vars | Optional |
| **SMTP** | Email notifications | `EMAIL_ENABLED`, `SMTP_*` | Optional |
| **AI API** | Semantic matching | `AI_API_KEY`, `AI_PROVIDER` | Optional |
| **Redis** | Celery broker (async) | `REDIS_URL`, `CELERY_*` | Optional |
| **PostgreSQL** | Production database | `DATABASE_URL` | Optional |

---

## **8. DEPLOYMENT & OPERATIONS**

### **Quick Start (Windows PowerShell)**

```powershell
# One-command full setup (venv, deps, migrations, seed data)
.\setup.ps1

# Start backend (FastAPI + Uvicorn on :8000)
.\start_backend.ps1

# Start frontend (Vite dev server on :5173)
.\start_frontend.ps1
```

### **Environment Configuration**

Create `.env` file (template: `.env.example`):
```
DATABASE_URL=sqlite:///./job_platform.db
SECRET_KEY=your-random-jwt-secret-key
JOB_FEED_SOURCE=sample_feed
DEBUG=true
CORS_ORIGINS=["http://localhost:5173"]
```

### **Production Checklist**

- [ ] Change `SECRET_KEY` to random 32+ char string
- [ ] Set `DEBUG=false`
- [ ] Configure PostgreSQL `DATABASE_URL`
- [ ] Set `ALGORITHM=HS256` (or configure RS256 with keys)
- [ ] Configure email/SMS (Twilio, SMTP) if needed
- [ ] Set up Redis for Celery (optional but recommended)
- [ ] Configure HTTPS/TLS on API server
- [ ] Set proper CORS origins for frontend domain
- [ ] Run database migrations (`alembic upgrade head`)
- [ ] Seed initial admin account
- [ ] Enable monitoring/logging (Sentry, CloudWatch, etc.)

---

## **Summary**

**Amazon Job Platform** is a **rule-based, compliance-focused candidate-job matching system** featuring:

✅ **Frontend:** React 18 + TypeScript, responsive admin dashboard with Florence-style UI  
✅ **Backend:** FastAPI + SQLAlchemy, 10-table data model, 6 migrations  
✅ **Matching Engine:** Configurable rule-based scoring (location, job type, shift, pay)  
✅ **Admin Tools:** Real-time analytics, theme switcher (light/dark/blue), job management  
✅ **Extensibility:** Pluggable job sources, optional AI, Twilio/email integrations  
✅ **Security:** JWT auth, role-based access, audit logs, no employer credential storage  
✅ **Testing:** 22 pytest tests covering core workflows  
✅ **Compliance:** Candidate-controlled actions, full audit trail, zero unauthorized automation  

**Perfect for:** Enterprise recruiting, fulfillment center hiring, compliance-heavy hiring pipelines, 100+ candidate management at scale.

---

*Document prepared for demonstration, presentation, and stakeholder review.*
