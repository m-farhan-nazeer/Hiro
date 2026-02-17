# Hiro – AI-Powered Recruitment Web Application

## 📌 Project Description
Hiro is an **AI-powered recruitment web application** designed to simplify the hiring process. Recruiters can post jobs, review applicants, and leverage AI-based scoring to identify the best candidates faster. The platform offers modern dashboards, applicant profiles with resume previews, and insightful analytics — all in a responsive, user-friendly interface.

---

## ✨ Features
- Public landing page with value proposition
- Authentication (Email/Password + Google)
- Recruiter dashboard with stats and AI scoring
- Applicant profile view with resume preview & notes
- Job posting and applicant tracking
- Contact applicants directly from profile view
- Settings for profile and notifications
- Fully responsive (desktop, tablet, mobile)

---

## 🛠️ Tech Stack
- **Frontend:** React + Vite, Tailwind CSS (served via Nginx)
- **Backend:** Django 5.x + Django REST Framework (Python 3.11)
- **Database:** PostgreSQL 15
- **Authentication:** Session-based + Google OAuth
- **AI/ML:** Resume parsing & candidate scoring (with Playwright for web scraping)
- **Containerization:** Docker + Docker Compose

---

## 🐳 Docker Architecture

### Container Overview

The application runs in **3 Docker containers**:

1. **`db` (PostgreSQL 15)**
   - Database container
   - Persistent volume: `postgres_data`
   - Accessible internally on port 5432

2. **`backend` (Django)**
   - Python 3.11 slim image
   - Includes Playwright (Chromium) for web scraping
   - Exposes port 8000
   - Auto-runs migrations on startup
   - Serves API endpoints at `/api`

3. **`frontend` (React + Nginx)**
   - Multi-stage build (Node.js → Nginx)
   - Production-optimized static files
   - Exposes port 80 (main entry point)
   - Proxies `/api` requests to backend
   - Serves React SPA

### Network

All containers communicate via a custom bridge network: `hiro_network`

### Build Process

**Frontend (Multi-stage):**
1. **Stage 1 (build-stage):** Node.js 20 compiles React → static files
2. **Stage 2 (production-stage):** Nginx serves static files + proxies API

**Backend:**
- Single-stage build with Python 3.11
- Installs system dependencies (PostgreSQL client, netcat)
- Installs Python packages + Playwright with Chromium
- Copies `server/` and `mlops/` directories
- Runs entrypoint script for migrations + server startup

---

## 🚀 Quick Start (Docker - Recommended)

### Prerequisites
- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop))
- Docker Compose (included with Docker Desktop)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd Hiro

# 2. Create environment file from template
cp .env.docker.example .env.docker

# 3. Edit .env.docker and add your API keys
# - OPENAI_API_KEY (required for resume extraction)
# - QDRANT_URL and QDRANT_API_KEY (optional)
# - GROQ_API_KEY (optional)

# 4. Start application
docker-compose up --build

# 5. Access application
# Frontend: http://localhost/
# Backend API: http://localhost:8000/api
```
- **Direct Backend:** http://localhost:8000 (if needed)

### 5. Create Admin User (Optional)
```bash
# While containers are running, open a new terminal
docker compose exec backend python manage.py createsuperuser
```

---

## 🔧 Docker Management Commands

### Starting & Stopping

```bash
# Start containers (without rebuilding)
docker compose up

# Start in background
docker compose up -d

# Stop containers (keeps containers)
docker compose stop

# Stop and remove containers
docker compose down

# Stop and remove containers + volumes (clears database!)
docker compose down -v
```

### When to Use `--build`

**Use `docker compose up --build` when:**
- First time setup
- You modified frontend code (React/TypeScript)
- You modified backend code (Python/Django)
- You changed dependencies (package.json or requirements.txt)
- You updated Dockerfiles

**Use `docker compose up` when:**
- Just restarting after `docker compose stop`
- No code changes were made
- Much faster!

### View Logs

```bash
# All containers
docker compose logs

# Follow logs in real-time
docker compose logs -f

# Specific service
docker compose logs backend
docker compose logs frontend
docker compose logs db

# Last 50 lines
docker compose logs --tail=50 -f
```

### Execute Commands in Containers

```bash
# Django shell
docker compose exec backend python manage.py shell

# Run migrations
docker compose exec backend python manage.py migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser

# Access PostgreSQL
docker compose exec db psql -U postgres -d hiro_db

# Access backend container bash
docker compose exec backend /bin/sh
```

### Rebuild Specific Service

```bash
# Rebuild only backend
docker compose build backend

# Rebuild only frontend
docker compose build frontend

# Then restart
docker compose up
```

---

## 🖥️ Docker Desktop GUI Management

You can manage containers visually through **Docker Desktop**:

1. Open Docker Desktop application
2. Navigate to **Containers** tab
3. Find `hiro` project
4. Available actions:
   - ▶️ Start/Stop containers
   - 🔄 Restart containers
   - 📊 View logs and stats
   - 🗑️ Delete containers
   - 🔍 Inspect container details

---

## 🔍 Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is ready
docker compose exec backend nc -z db 5432

# View database logs
docker compose logs db
```

### Port Already in Use
```bash
# If port 80 or 8000 is occupied:
# Option 1: Stop the conflicting service
# Option 2: Change ports in docker-compose.yml
ports:
  - "8080:80"  # Changed from 80:80
```

### Reset Everything (Clean Slate)
```bash
# Stop and remove containers, networks, volumes
docker compose down -v

# Remove images (optional)
docker rmi hiro-frontend hiro-backend

# Rebuild from scratch
docker compose up --build
```

### Container Exits Immediately
```bash
# Check container logs
docker compose logs backend

# Common issues:
# - Database not ready → entrypoint.sh handles this
# - Missing .env.docker → create it
# - Port conflict → change ports in docker-compose.yml
```

---

## 📦 Alternative: Local Development (Without Docker)

### Frontend
```bash
cd client
npm install
npm run dev
# Runs on http://localhost:5173
```

### Backend
```bash
cd server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright
playwright install chromium

# Set up PostgreSQL (must be installed separately)
# Update server/.env with your local database credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
# Runs on http://localhost:8000
```

> **Note:** When running locally, you'll need to:
> - Install PostgreSQL 15 separately
> - Update API proxy in frontend (Vite config)
> - Manage Python virtual environment
> - Install system dependencies for Playwright

---

## 🌐 Deployment Options

### Docker Hub Distribution

**Push to Docker Hub:**
```bash
# Login
docker login

# Tag images
docker tag hiro-backend-1 yourusername/hiro-backend:v1.0.0
docker tag hiro-frontend-1 yourusername/hiro-frontend:v1.0.0

# Push
docker push yourusername/hiro-backend:v1.0.0
docker push yourusername/hiro-frontend:v1.0.0
```

**Others can pull:**
```bash
docker pull yourusername/hiro-backend:v1.0.0
docker pull yourusername/hiro-frontend:v1.0.0
```

### Production Deployment

For production, update `docker-compose.yml`:
- Use specific version tags instead of `latest`
- Set `DEBUG=0` in environment
- Configure proper `SECRET_KEY`
- Set up SSL/HTTPS (add reverse proxy like Traefik/Nginx)
- Use managed database (AWS RDS, DigitalOcean Database)
- Configure `ALLOWED_HOSTS` properly

---
# Applicants API (Django + DRF + PostgreSQL)

Backend module to manage job applicants with full CRUD and resume storage as a **BLOB (bytea)** in PostgreSQL.

---

## Tech Stack

- Python 3.11
- Django 5.x
- Django REST Framework
- PostgreSQL

---

## Model: `Applicant`

Database table: `applicants_applicant`

| Field             | Type            | Notes                                                |
|-------------------|-----------------|------------------------------------------------------|
| `id`              | BigAutoField    | Primary key (auto-generated)                        |
| `name`            | CharField       | Applicant name                                      |
| `status`          | CharField       | Choices: `pending`, `shortlisted`, `rejected`, `hired` |
| `email`           | EmailField      | Applicant email                                     |
| `telephone`       | CharField       | Phone number                                        |
| `job_applied_for` | CharField       | Position applied for                                |
| `applied_date`    | DateField       | Auto-set on create (`auto_now_add=True`)            |
| `score`           | DecimalField    | Nullable (acts as N/A)                              |
| `resume`          | BinaryField     | BLOB (`bytea`) storing raw resume file bytes        |
| `prior_experience`| TextField       | Experience in past companies                        |
| `source`          | CharField       | Where candidate came from (LinkedIn, referral, etc.)|
| `skill_set`       | TextField       | Comma-separated or free-text skill list             |

Serializer exposes:

- `has_resume` – `true/false` flag
- `resume_url` – link to view/download the resume
- virtual write-only field: `resume_file` (used for uploads)

---

## Running the Backend

From the project root (where `manage.py` lives):

```bash
# Apply migrations
python manage.py migrate

# Run dev server
python manage.py runserver
Base URL (local): http://127.0.0.1:8000/

Endpoints Overview
Base resource: /applicants/

Method	URL	Description
GET	/applicants/	List all applicants
POST	/applicants/	Create applicant (with resume_file)
GET	/applicants/<id>/	Retrieve single applicant
PUT	/applicants/<id>/	Full update
PATCH	/applicants/<id>/	Partial update
DELETE	/applicants/<id>/	Delete applicant
GET	/applicants/<id>/resume/	View/download resume from BLOB

1. List Applicants
Request

h
Copy code
GET /applicants/
Response 200 OK

json
Copy code
[
  {
    "id": 2,
    "name": "farhan",
    "status": "pending",
    "email": "farhan@gmail.com",
    "telephone": "03214565454",
    "job_applied_for": "Backend Engineer",
    "applied_date": "2025-11-24",
    "score": null,
    "prior_experience": "2",
    "source": "linkedin",
    "skill_set": "pthon",
    "has_resume": true,
    "resume_url": "http://127.0.0.1:8000/applicants/2/resume/"
  }
]
2. Create Applicant (with Resume)
Request

http
Copy code
POST /applicants/
Content-Type: multipart/form-data
Form-data fields:

name (text)

status (text) – pending / shortlisted / rejected / hired

email (text)

telephone (text)

job_applied_for (text)

score (text, optional)

prior_experience (text, optional)

source (text, optional)

skill_set (text, optional)

resume_file (file) – PDF/DOC/etc.

Response 201 Created

json
Copy code
{
  "id": 3,
  "name": "farhan",
  "status": "pending",
  "email": "farhan@gmail.com",
  "telephone": "03214565454",
  "job_applied_for": "Backend Engineer",
  "applied_date": "2025-11-24",
  "score": null,
  "prior_experience": "2",
  "source": "linkedin",
  "skill_set": "pthon",
  "has_resume": true,
  "resume_url": "http://127.0.0.1:8000/applicants/3/resume/"
}
3. Retrieve Applicant
Request

http
Copy code
GET /applicants/<id>/
Response 200 OK

json
Copy code
{
  "id": 2,
  "name": "farhan",
  "status": "pending",
  "email": "farhan@gmail.com",
  "telephone": "03214565454",
  "job_applied_for": "Backend Engineer",
  "applied_date": "2025-11-24",
  "score": null,
  "prior_experience": "2",
  "source": "linkedin",
  "skill_set": "pthon",
  "has_resume": true,
  "resume_url": "http://127.0.0.1:8000/applicants/2/resume/"
}
Errors

404 Not Found – if the id does not exist.

4. Full Update (PUT)
Request

http
Copy code
PUT /applicants/<id>/
Content-Type: multipart/form-data
Send all fields again (PUT replaces the resource):

text
Copy code
name=farhan updated
status=shortlisted
email=farhan@gmail.com
telephone=03214565454
job_applied_for=Senior Backend Engineer
score=90.0
prior_experience=3 years
source=linkedin
skill_set=python, django, drf
resume_file=<new PDF file>  (optional)
Response 200 OK

json
Copy code
{
  "id": 2,
  "name": "farhan updated",
  "status": "shortlisted",
  "email": "farhan@gmail.com",
  "telephone": "03214565454",
  "job_applied_for": "Senior Backend Engineer",
  "applied_date": "2025-11-24",
  "score": 90.0,
  "prior_experience": "3 years",
  "source": "linkedin",
  "skill_set": "python, django, drf",
  "has_resume": true,
  "resume_url": "http://127.0.0.1:8000/applicants/2/resume/"
}
5. Partial Update (PATCH)
Request (JSON)

http
Copy code
PATCH /applicants/<id>/
Content-Type: application/json
Example body:

json
Copy code
{
  "status": "hired",
  "score": 95.0
}
Response 200 OK

json
Copy code
{
  "id": 2,
  "name": "farhan updated",
  "status": "hired",
  "email": "farhan@gmail.com",
  "telephone": "03214565454",
  "job_applied_for": "Senior Backend Engineer",
  "applied_date": "2025-11-24",
  "score": 95.0,
  "prior_experience": "3 years",
  "source": "linkedin",
  "skill_set": "python, django, drf",
  "has_resume": true,
  "resume_url": "http://127.0.0.1:8000/applicants/2/resume/"
}
You can also PATCH with multipart/form-data if you want to update resume_file.

6. Delete Applicant
Request

http
Copy code
DELETE /applicants/<id>/
Response 204 No Content

No body.

Errors

404 Not Found – if id does not exist.

7. View/Download Resume
Request

http
Copy code
GET /applicants/<id>/resume/
Behavior

Reads resume BLOB (bytea) from DB.

Returns it as a PDF:

Content-Type: application/pdf

Content-Disposition: inline; filename="resume_<id>.pdf"

Browser will either open the PDF in a new tab or download it.

Errors

404 Not Found – applicant not found or no resume stored.



# Users API (Auth, Profiles, Sessions)

This module manages application users with:

- Registration
- Session-based login (cookies)
- Logout
- Current user info (`/users/me/`)
- Change password
- Login history
- User profiles (telephone, avatar, department, position, language, timezone)

Built on:

- Django 5.x
- Django REST Framework
- PostgreSQL
- Django's built-in `auth.User` model

---

## Database Design

### 1. Django `User` (built-in: `auth_user`)

Used for core identity:

- `id` (PK, integer, auto)
- `username` (unique, used for login)
- `email`
- `password` (hashed)
- `first_name`
- `last_name`
- plus Django’s default fields (`is_active`, etc.)

> **Primary key is `id`, not `username`.**

---

### 2. `UserProfile` (`users_userprofile`)

Extends `User` with profile + preferences.

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    telephone = models.CharField(max_length=20, blank=True)
    avatar = models.FileField(upload_to="avatars/", null=True, blank=True)
    department = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=255, blank=True)

    language = models.CharField(max_length=20, blank=True, default="en")
    timezone = models.CharField(max_length=64, blank=True, default="UTC")

    password_last_changed = models.DateTimeField(null=True, blank=True)
3. LoginHistory (users_loginhistory)
Tracks login / logout events per user.

python
Copy code
class LoginHistory(models.Model):
    LOGIN = "login"
    LOGOUT = "logout"

    EVENT_TYPE_CHOICES = [
        (LOGIN, "Login"),
        (LOGOUT, "Logout"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="login_history")
    type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES)

    device = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)

    time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
device typically stores User-Agent (browser info).

location can be derived from IP if needed.

logout_time is populated when logout is called.

Serializers (Summary)
Key serializers in users/serializers.py:

UserProfileSerializer – profile fields.

UserSerializer – basic user info + nested profile.

UserRegisterSerializer – registration (creates User + UserProfile).

LoginSerializer – username + password.

ChangePasswordSerializer – old/new password.

LoginHistorySerializer – login/logout events.

Views (Summary)
Located in users/views.py:

RegisterView – POST /users/register/

LoginView – POST /users/login/

LogoutView – POST /users/logout/

MeView – GET /users/me/

ChangePasswordView – POST /users/change-password/

LoginHistoryView – GET /users/login-history/

LoginView uses authenticate() + login() to create a session and set a sessionid cookie.
Other endpoints rely on IsAuthenticated + that session cookie.

URLs
Configured in backend/urls.py:

python
Copy code
path("users/register/", RegisterView.as_view(), name="user-register"),
path("users/login/", csrf_exempt(LoginView.as_view()), name="user-login"),
path("users/logout/", LogoutView.as_view(), name="user-logout"),
path("users/me/", MeView.as_view(), name="user-me"),
path("users/change-password/", ChangePasswordView.as_view(), name="user-change-password"),
path("users/login-history/", LoginHistoryView.as_view(), name="user-login-history"),
Base URL (dev): http://127.0.0.1:8000

Authentication & Sessions
Login sets a Django session via login(request, user).

Session ID is stored in a sessionid cookie.

Subsequent requests (e.g., /users/me/) use this cookie, so the user doesn’t have to send credentials again.

LoginHistory logs login and logout events.

Endpoints & Examples
1. Register
URL

http
Copy code
POST /users/register/
Content-Type: application/json
Request body

json
Copy code
{
  "username": "farhan1",
  "first_name": "Farhan",
  "last_name": "Dev",
  "email": "farhan@example.com",
  "password": "StrongPass123!",
  "password_confirm": "StrongPass123!",
  "telephone": "03214567890",
  "department": "Engineering",
  "position": "Backend Developer",
  "language": "en",
  "timezone": "Asia/Karachi"
}
Response 201

json
Copy code
{
  "id": 2,
  "username": "farhan1",
  "first_name": "Farhan",
  "last_name": "Dev",
  "email": "farhan@example.com",
  "profile": {
    "telephone": "03214567890",
    "avatar": null,
    "department": "Engineering",
    "position": "Backend Developer",
    "language": "en",
    "timezone": "Asia/Karachi",
    "password_last_changed": "2025-11-24T05:43:45.102880Z"
  }
}
2. Login (Session-based)
URL

http
Copy code
POST /users/login/
Content-Type: application/json
Request body

json
Copy code
{
  "username": "farhan1",
  "password": "StrongPass123!"
}
Response 200

json
Copy code
{
  "id": 2,
  "username": "farhan1",
  "first_name": "Farhan",
  "last_name": "Dev",
  "email": "farhan@example.com",
  "profile": {
    "telephone": "03214567890",
    "avatar": null,
    "department": "Engineering",
    "position": "Backend Developer",
    "language": "en",
    "timezone": "Asia/Karachi",
    "password_last_changed": "2025-11-24T05:43:45.102880Z"
  }
}
Django sets a session cookie (sessionid).

A LoginHistory row is created with type "login".

3. Current User
URL

http
Copy code
GET /users/me/
Auth

Requires a valid session cookie set by /users/login/.

Response 200

json
Copy code
{
  "id": 2,
  "username": "farhan1",
  "first_name": "Farhan",
  "last_name": "Dev",
  "email": "farhan@example.com",
  "profile": {
    "telephone": "03214567890",
    "avatar": null,
    "department": "Engineering",
    "position": "Backend Developer",
    "language": "en",
    "timezone": "Asia/Karachi",
    "password_last_changed": "2025-11-24T05:43:45.102880Z"
  }
}
4. Change Password
URL

http
Copy code
POST /users/change-password/
Content-Type: application/json
Auth

Requires logged-in user (session cookie).

Request body

json
Copy code
{
  "old_password": "StrongPass123!",
  "new_password": "NewStrongPass456!"
}
Response 200

json
Copy code
{
  "detail": "Password changed successfully."
}
Side effects:

Updates auth_user.password (secure hash).

Updates UserProfile.password_last_changed.

Keeps user logged in with new password.

5. Logout
URL

http
Copy code
POST /users/logout/
Auth

Requires logged-in user.

Response 200

json
Copy code
{
  "detail": "Logged out successfully."
}
Side effects:

Session is cleared.

Updates last login record’s logout_time (if present).

Creates a new LoginHistory row with type "logout".

6. Login History
URL

http
Copy code
GET /users/login-history/
Auth

Requires logged-in user.

Response 200

json
Copy code
[
  {
    "id": 5,
    "type": "login",
    "device": "PostmanRuntime/7.39.0",
    "location": "",
    "time": "2025-11-24T05:45:23.000000Z",
    "logout_time": null
  },
  {
    "id": 6,
    "type": "logout",
    "device": "PostmanRuntime/7.39.0",
    "location": "",
    "time": "2025-11-24T05:50:10.000000Z",
    "logout_time": null
  }
]