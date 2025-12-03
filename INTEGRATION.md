# 2FA Application - Frontend + Backend Integration Guide

## 📋 Overview

This document describes the complete integration between:

- **Streamlit Frontend** (UI, routing, user interactions)
- **FastAPI Backend** (API, database, authentication, 2FA)
- **Supporting Services** (PostgreSQL, Redis, MailHog)

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** (recommended)
- Python 3.11+ (for local development)
- Git

### Running the Full Stack with Docker

1. **Clone the repository:**

```bash
git clone https://github.com/swistakmatt/2fa-app.git
cd 2fa-app
```

2. **Configure environment:**

```bash
# Backend configuration already in .env
# Frontend - use Docker settings in frontend/.env
```

3. **Start all services:**

```bash
docker-compose up -d
```

This will start:

- **PostgreSQL** (port 5432)
- **Redis** (port 6379)
- **MailHog** (port 8025 for web UI, 1025 for SMTP)
- **Backend API** (port 8000)
- **Frontend Streamlit** (port 8501)

4. **Access the application:**

- Frontend: http://localhost:8501
- Backend API Docs: http://localhost:8000/docs
- MailHog (view emails): http://localhost:8025
- pgAdmin: http://localhost:5050

### Running Locally (Development)

#### Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

# Set environment variables in .env
# DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/2fa_app_db
# REDIS_URL=redis://localhost:6379/0
# SECRET_KEY=your-secret-key

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000

#### Frontend

```bash
cd frontend
pip install -r requirements.txt

# Set BACKEND_API_URL in .env
# BACKEND_API_URL=http://localhost:8000/api

# Start Streamlit
streamlit run app.py
```

Frontend will be available at: http://localhost:8501

## 📝 User Flow

1. **Register** - Create new account
2. **Login** - Enter email and password
3. **2FA Verification** - Enter 6-digit code sent to email (check MailHog)
4. **Profile** - View and manage user profile

## 🔧 Configuration

### Backend (.env)

```env
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/2fa_app_db
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379/0
MAIL_SERVER=2fa_mailhog
MAIL_PORT=1025
```

### Frontend (frontend/.env)

```env
# For local development
BACKEND_API_URL=http://localhost:8000/api

# For Docker
BACKEND_API_URL=http://backend:8000/api
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest -v
```

### Manual Testing Flow

1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `streamlit run app.py`
3. Register new user
4. Check MailHog (http://localhost:8025) for 2FA code
5. Complete 2FA verification
6. Access profile page

## 📚 API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (sends 2FA code)
- `POST /api/auth/verify-2fa` - Verify 2FA code (returns JWT)

### User

- `GET /api/user/profile` - Get user profile (requires JWT)
- `PUT /api/user/update` - Update profile (requires JWT)
- `DELETE /api/user/delete` - Delete account (requires JWT)

## 📧 Email System (MailHog vs Gmail)

### Why MailHog for Development?

The application uses **MailHog** as the default email service for development:

#### Advantages:

- ✅ **No configuration** - Works immediately after `docker-compose up`
- ✅ **Web UI** - View all emails at http://localhost:8025
- ✅ **Fast** - Instant email delivery (no SMTP delays)
- ✅ **Safe** - No risk of sending emails to real users during testing
- ✅ **Debugging** - See email content, headers, attachments
- ✅ **Offline** - Works without internet connection

#### How It Works:

1. **Backend sends email** → FastAPI-Mail connects to MailHog SMTP (port 1025)
2. **MailHog captures** → Stores email in memory (not sent to real address)
3. **View in browser** → Open http://localhost:8025 to see all emails
4. **Copy 2FA code** → Use the 6-digit code from email subject/body

### Switching to Gmail (Production)

For production deployment with real Gmail:

#### Step 1: Generate App Password

1. Go to: https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not already enabled)
3. Go to: https://myaccount.google.com/apppasswords
4. Generate password for "Mail" → "Other (Custom name)"
5. Copy the 16-character password

#### Step 2: Update Configuration

Edit `backend/.env`:

```env
# Gmail Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your.email@gmail.com
MAIL_PASSWORD=your_16_char_app_password
MAIL_FROM=your.email@gmail.com
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
```

#### Step 3: Restart Services

```bash
docker-compose restart backend
```

#### Important Notes:

- Gmail has **500 emails/day limit** for free accounts
- Use **App Password**, not your regular Gmail password
- Consider using **SendGrid** or **AWS SES** for higher volume

## 🔒 Security Features

- ✅ JWT-based authentication
- ✅ 2FA via email (6-digit TOTP codes)
- ✅ Password hashing with bcrypt
- ✅ Redis-based code storage with TTL
- ✅ Rate limiting on 2FA attempts
- ✅ Progressive blocking for failed attempts
- ✅ CORS protection

## 🐛 Troubleshooting

### Backend won't start

- Check if PostgreSQL is running: `docker-compose ps`
- Verify DATABASE_URL in .env
- Run migrations: `alembic upgrade head`

### Frontend can't connect to backend

- Check BACKEND_API_URL in frontend/.env
- Verify backend is running on port 8000
- Check CORS settings allow port 8501

### 2FA code not received

- Check MailHog UI: http://localhost:8025
- Verify MAIL_SERVER and MAIL_PORT in backend/.env
- Ensure Redis is running for code storage

### Docker issues

```bash
# Restart all services
docker-compose down
docker-compose up -d

# View logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild images
docker-compose build --no-cache
```

## 📦 Tech Stack

**Backend:**

- FastAPI
- PostgreSQL (database)
- Redis (2FA code storage)
- SQLAlchemy (ORM)
- Alembic (migrations)
- FastAPI-Mail (email sending)
- MailHog (email testing)

**Frontend:**

- Streamlit
- httpx (async HTTP client)
- python-dotenv

## 🔗 Links

- **Frontend App**: http://localhost:8501
- **Backend API Documentation**: http://localhost:8000/docs
- **MailHog Email UI**: http://localhost:8025 ⭐ (Check 2FA codes here!)
- **pgAdmin**: http://localhost:5050
- **Redis**: localhost:6379

## 🤝 Integration Details

### Frontend → Backend Communication

**API Handler** (`frontend/services/api_handler.py`):

- Uses **httpx.AsyncClient** for async HTTP requests
- Loads `BACKEND_API_URL` from environment
- Implements: `register()`, `login()`, `verify_2fa()`, `get_profile()`
- Error handling with status-specific messages

**Session Management**:

- `tmp_token` stored in `st.session_state` after login
- `access_token` (JWT) stored after 2FA verification
- Tokens passed in request headers: `Authorization: Bearer {token}`

### Backend → Redis Communication

**2FA Code Storage** (`backend/app/services/twofa_service.py`):

- Generates 6-digit random code
- Stores in Redis with 180-second TTL
- Key format: `2fa_code:{user_id}`
- Automatic expiration prevents memory leaks

**Rate Limiting**:

- Tracks attempts: `2fa_attempts:{user_id}`
- Progressive blocking: 30min → 1h → 8h → 24h
- Block key: `2fa_blocked:{user_id}`

### Backend → MailHog Communication

**Email Sending** (FastAPI-Mail):

- SMTP connection to MailHog (port 1025)
- HTML email template with 6-digit code
- Subject: "Your 2FA Verification Code"
- From: "2FA Application <noreply@2fa-app.com>"

## 📝 Recent Implementation

### What Was Done by Collaborators:

1. **Backend Infrastructure** (FastAPI + PostgreSQL)

   - User model with SQLAlchemy
   - JWT authentication endpoints
   - Password hashing with bcrypt
   - Database migrations with Alembic

2. **2FA Service Implementation**

   - 6-digit code generation
   - Redis integration for code storage
   - Email sending via FastAPI-Mail
   - Rate limiting and progressive blocking

3. **Frontend UI** (Streamlit)

   - Login, Register, 2FA, Profile pages
   - Custom CSS styling (cyberpunk theme)
   - Session-based routing
   - JavaScript for 2FA timer and auto-focus

4. **Integration Work** (Current Session)
   - Created `api_handler.py` (complete APIHandler class)
   - Integrated all UI pages with backend API
   - Added frontend Docker service
   - Configured CORS for port 8501
   - Fixed database migrations in Docker
   - Updated environment configurations
   - Created comprehensive documentation

### Key Integration Fixes:

- ✅ Fixed empty `api_handler.py` → Full async implementation
- ✅ Added `httpx` and `python-dotenv` to frontend requirements
- ✅ Updated docker-compose to run migrations before uvicorn
- ✅ Fixed duplicate `model_config` in backend Settings
- ✅ Removed unused TOTP variables from .env
- ✅ Configured proper Docker networking (service names as hosts)

## 🎓 Learning Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Streamlit Docs**: https://docs.streamlit.io/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Redis**: https://redis.io/docs/
- **Docker Compose**: https://docs.docker.com/compose/
- **MailHog**: https://github.com/mailhog/MailHog
