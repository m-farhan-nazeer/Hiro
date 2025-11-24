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
- **Frontend:** React, Tailwind CSS  
- **Backend:** Django / Django REST Framework  
- **Database:** PostgreSQL  
- **Authentication:** Email/Password + Google OAuth  
- **AI:** Resume parsing & candidate scoring  

---

## ⚙️ Setup Instructions

### Client (Frontend)
```bash
cd client
npm install
npm run start
```

### Server (Backend)
```bash
cd server

# Create Virtual Environment

# (Windows)
python -m venv venv 
.\venv\Scripts\activate

# (UNIX/MacOS)
python3 -m venv venv
source venv/bin/activate

# Run Server
python manage.py runserver

```
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