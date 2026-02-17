# 🚀 Hiro - AI-Powered Recruitment Platform

Modern recruitment platform with AI-powered resume screening and applicant tracking.

---

## 📋 About

**Hiro** streamlines hiring by combining traditional ATS features with AI-powered resume analysis. Recruiters can post jobs, review applicants, and leverage semantic scoring to identify top candidates faster.

**Key Features:**
- 🤖 AI resume parsing & scoring (GPT-4o)
- 📊 Real-time applicant dashboards
- 🔍 LinkedIn profile scraping
- 📄 Resume preview & insights
- 🎯 Semantic job-candidate matching
- 👥 Multi-user RBAC system

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** React 18 + Vite
- **UI:** Tailwind CSS, custom components
- **State:** Redux Toolkit
- **Server:** Nginx (production)

### Backend
- **Framework:** Django 5.2 + Django REST Framework
- **Language:** Python 3.11
- **Database:** PostgreSQL 15
- **AI/ML:** LangChain, OpenAI GPT-4o, Qdrant (vector DB)
- **Scraping:** Playwright (Chromium)

### Infrastructure
- **Containers:** Docker + Docker Compose
- **Network:** Custom bridge network
- **Storage:** Persistent volumes (PostgreSQL data)

---

## 🗄️ Database Schema

### Core Models

**Users & Auth:**
- `auth_user` - Django built-in users
- `users_userprofile` - Extended profiles (roles: super_admin, admin, recruiter, employee)
- `users_loginhistory` - Login/logout tracking

**Jobs:**
- `posts_job` - Job postings with scoring weights
  - Relationship: `created_by` → `auth_user`

**Applicants:**
- `applicants_applicant` - Candidate basic info
- `applicants_applicantprofile` - AI-extracted data (JSON fields: skills, experience, education)
  - JSON Fields: `skills`, `experience`, `education`, `social_insights`
- `linkedin_scraping_activity` - Scraping logs (rate limiting)

**Applications:**
- `applications_application` - Links applicants to jobs
  - Fields: `resume` (binary), `score`, `status`, `scoring_status`
  - Constraint: `UNIQUE(applicant_id, job_id)`

### Key Relationships
```
User ←→ UserProfile (OneToOne)
User → Job (OneToMany)
Job ← Application → Applicant (ManyToMany through Application)
Applicant ←→ ApplicantProfile (OneToOne)
```

---

## 🎨 Frontend Features

### Pages & Routes

**Public:**
- `/` - Landing page
- `/apply?id={jobId}` - Public application form

**Authenticated:**
- `/dashboard` - Overview statistics
- `/jobs` - Job listings (RBAC filtered)
- `/jobs/new` - Create job posting
- `/job?id={jobId}` - View applicants for job
- `/applicants` - All applicants (global view)
- `/settings` - User profile & preferences

### Key Components

**Applicant Management:**
- `CustomersTable` - Sortable, filterable applicant list
- `ApplicantProfileModal` - Full profile view with:
  - Resume preview (PDF viewer)
  - AI-extracted insights (skills, experience, education)
  - LinkedIn scraping integration
  - Hiring status dropdown
  - Notes & actions

**Job Management:**
- `ProjectList` - Job dashboard
- `JobForm` - Create/edit jobs with scoring weights
- `JobPage` - Per-job applicant view

**Authentication:**
- Email/password + Google OAuth
- Session-based auth
- Protected routes

---

## 🐳 Docker Setup (Recommended)

### Quick Start

```bash
# 1. Clone repository
git clone <your-repo-url>
cd Hiro

# 2. Create environment file
cat > .env.docker << EOF
# Database
DATABASE=postgres
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=hiro_db
SQL_USER=postgres
SQL_PASSWORD=postgres
SQL_HOST=db
SQL_PORT=5432

# Django
SECRET_KEY=your-random-secret-key-here
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1,backend

# OpenAI API
OPENAI_API_KEY=your-openai-api-key

# Qdrant Vector DB (optional - for semantic search)
QDRANT_URL=https://your-qdrant-url
QDRANT_API_KEY=your-qdrant-key
EOF

# 3. Start application
docker-compose up --build

# 4. Access application
# Frontend: http://localhost/
# Backend API: http://localhost:8000/api
```

### Container Architecture

```
┌─────────────────────────────────────────┐
│         Docker Network (hiro_network)   │
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────┐ │
│  │ Frontend │  │ Backend  │  │  DB  │ │
│  │  Nginx   │  │  Django  │  │ PG15 │ │
│  │  :80     │→→│  :8000   │→→│ :5432││
│  └──────────┘  └──────────┘  └──────┘ │
└─────────────────────────────────────────┘
         ↑
    localhost:80
```

**Request Flow:**
1. User → `localhost/` → Nginx serves React app
2. User → `localhost/api/*` → Nginx proxies to Django
3. Django → PostgreSQL (db:5432)

### Management Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart containers
docker-compose restart

# Stop containers
docker-compose down

# Rebuild after code changes
docker-compose up --build

# Access backend shell
docker-compose exec backend python manage.py shell

# Run migrations manually
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

---

## 🧠 AI/ML Features

### Resume Processing Pipeline

1. **Upload** - User uploads PDF/DOCX resume
2. **Parse** - LangChain extracts text + hyperlinks
3. **Extract** - GPT-4o structures data:
   - Summary, skills, experience, education, certifications
   - GitHub/LinkedIn URLs
   - Total years of experience
4. **Score** - Semantic similarity against job description:
   - Embeddings: OpenAI `text-embedding-3-large` (3072 dim)
   - Vector store: Qdrant (cloud)
   - Weighted scoring: Skills (25%), Projects (50%), Education (25%)
5. **Store** - Save to `ApplicantProfile` (JSON fields)

### LinkedIn Scraping

- **Engine:** Playwright (Chromium headless)
- **Session:** Persistent cookies (~30 days)
- **Setup:** Run `python server/linkedin_login.py` once
- **Rate Limit:** 50 profiles/day
- **Data Extracted:** Headline, about, connections, experience, education

---

## 🔧 Local Development (Without Docker)

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15

### Backend Setup
```bash
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# Configure database in .env
cp .env.example .env

python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd client
npm install
npm run dev
```

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login/` - Email/password login
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/session/` - Check session

### Jobs
- `GET /api/jobs/` - List jobs (RBAC filtered)
- `POST /api/jobs/` - Create job
- `GET /api/jobs/{id}/` - Job details
- `PUT /api/jobs/{id}/` - Update job
- `DELETE /api/jobs/{id}/` - Delete job

### Applicants
- `GET /api/applicants/` - List applicants
- `GET /api/applicants/{id}/` - Applicant details
- `POST /api/applicants/{id}/profile/refresh/` - Re-extract resume
- `POST /api/applicants/{id}/scrape-linkedin/` - Scrape LinkedIn

### Applications
- `GET /api/applications/` - List applications
- `POST /api/applications/` - Submit application (public)
- `PATCH /api/applications/{id}/` - Update status/score

---

## 🔐 Environment Variables

**Required:**
- `OPENAI_API_KEY` - For resume extraction (GPT-4o)

**Optional:**
- `QDRANT_URL` - Vector DB for semantic search
- `QDRANT_API_KEY` - Qdrant authentication
- `GOOGLE_CLIENT_ID` - Google OAuth
- `GOOGLE_CLIENT_SECRET` - Google OAuth

---

## 📝 License

All rights reserved © 2026 Hiro

---

## 🤝 Support

For issues or questions, please open a GitHub issue.