# Quick Start Guide - 2FA Application

🚀 **Fastest way to run:** Use Docker! ⚡

This guide will help you quickly run the full-stack 2FA application (Backend + Frontend) on your Windows system.

## Prerequisites

Before starting, make sure you have installed:

- ✅ **Docker Desktop** (recommended - easiest option!)
- ✅ Git
- ✅ Python 3.11+ (only if running without Docker)

## Step 1: Clone Repository

```powershell
git clone https://github.com/swistakmatt/2fa-app.git
cd 2fa-app
```

## Step 2: Run Full Application with Docker 🐳 (RECOMMENDED)

### Complete Stack in One Command!

```powershell
# Start ALL services: postgres, redis, mailhog, backend, frontend
docker-compose up -d
```

This starts:

- ✅ **PostgreSQL** - Database (port 5432)
- ✅ **Redis** - 2FA code storage (port 6379)
- ✅ **MailHog** - Email viewer (port 8025)
- ✅ **Backend API** - FastAPI (port 8000)
- ✅ **Frontend** - Streamlit (port 8501)
- ✅ **pgAdmin** - Database admin (port 5050)

### Access the Application

```powershell
# Wait ~30 seconds for migrations to complete, then:
```

- **Frontend App**: http://localhost:8501
- **Backend API Docs**: http://localhost:8000/docs
- **MailHog (View 2FA Emails)**: http://localhost:8025 ⭐
- **pgAdmin**: http://localhost:5050

### Testing the Application

1. **Open Frontend**: http://localhost:8501
2. **Register**: Click "Zarejestruj się" and create account
3. **Login**: Enter your email and password
4. **Check Email**: Open http://localhost:8025 to see 2FA code
5. **Verify**: Enter the 6-digit code
6. **Profile**: You're logged in! 🎉

### Stop Application

```powershell
# Stop all services
docker-compose down

# Stop and remove all data (fresh start)
docker-compose down -v
```

---

## Alternative: Local Development (Without Docker)

### Option A: Run Individual Services with Docker

```powershell
# Run only infrastructure (postgres, redis, mailhog)
docker-compose up -d postgres redis mailhog
```

Database connection string:

```
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/2fa_app_db
REDIS_URL=redis://localhost:6379/0
```

### Option B: Local PostgreSQL

If you have PostgreSQL installed locally:

```sql
CREATE DATABASE 2fa_app_db;
```

You can also use pgAdmin or another PostgreSQL management tool.

## Step 3: Backend Configuration

### 3.1. Navigate to backend directory

```powershell
cd backend
```

### 3.2. Create virtual environment

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3.3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3.4. Environment variables configuration

Copy `.env.example` file to `.env`:

```powershell
copy .env.example .env
```

Edit `.env` file (you can use Notepad or VS Code):

**If using Docker (Option A):**

```env
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/2fa_app_db
SECRET_KEY=generate_random_key_here
```

**If using local PostgreSQL (Option B):**

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/2fa_app_db
SECRET_KEY=generate_random_key_here
```

**Generate SECRET_KEY:**

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the generated key and paste it into `.env`.

### 3.5. Run database migrations

````powershell
# Generate first migration
```powershell
# Generate first migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
````

### 3.6. Run server

```powershell
uvicorn app.main:app --reload
```

🎉 **Backend is running!** Open browser: http://localhost:8000/docs

## Step 4: Understanding the 2FA Flow

### Why MailHog? 📧

**MailHog** is a development email testing tool that catches all outgoing emails. Instead of sending real emails to Gmail/Outlook, MailHog:

✅ **Captures emails locally** - View at http://localhost:8025
✅ **No configuration needed** - Works out of the box
✅ **Fast testing** - Instant email delivery
✅ **Safe** - Won't spam real email addresses
✅ **Perfect for development** - See all sent emails in one place

### 2FA Email Flow

1. **Register** → User creates account (no email sent)
2. **Login** → Backend generates 6-digit code → Sends to MailHog
3. **Check MailHog** → Open http://localhost:8025 → Copy code
4. **Verify** → Enter code → Receive JWT token
5. **Authenticated** → Access profile

### When to Use Real Gmail?

**MailHog is for DEVELOPMENT.** For production:

1. Generate App Password: https://myaccount.google.com/apppasswords
2. Update `backend/.env`:
   ```env
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=your.email@gmail.com
   MAIL_PASSWORD=your_16_char_app_password
   MAIL_STARTTLS=True
   ```
3. Restart: `docker-compose restart backend`

### API Testing (Optional)

If using backend directly (Swagger UI at http://localhost:8000/docs):

```powershell
# Register user
curl -X POST "http://localhost:8000/api/auth/register" `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@example.com\",\"password\":\"Admin123!abc\"}'

# Login (sends 2FA code)
curl -X POST "http://localhost:8000/api/auth/login" `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@example.com\",\"password\":\"Admin123!abc\"}'

# Check MailHog for code, then verify
curl -X POST "http://localhost:8000/api/auth/verify-2fa" `
  -H "Content-Type: application/json" `
  -d '{\"tmp_token\":\"TOKEN_FROM_LOGIN\",\"code\":\"123456\"}'
```

## Step 5: Run Tests

```powershell
pytest
```

Or with code coverage:

```powershell
pytest --cov=app --cov-report=html
```

## 🔍 Installation Check

### Check versions

```powershell
python --version    # Should be 3.10+
pip --version
psql --version      # PostgreSQL
```

### Check if database is working

```powershell
psql -U postgres -c "SELECT version();"
```

### Check if virtual environment is active

You should see `(venv)` before the PowerShell prompt.

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError"

**Solution:**

```powershell
# Make sure environment is active
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: "Could not connect to database"

**Solution:**

- Check if PostgreSQL is running (service `postgresql-x64-14`)
- Check `DATABASE_URL` in `.env` file
- Check if database `2fa_app_db` exists

### Problem: "Port 8000 already in use"

**Solution:**

```powershell
# Use different port
uvicorn app.main:app --reload --port 8001
```

### Problem: Alembic not working

**Solution:**

```powershell
# Make sure you are in backend/ directory
cd backend

# Check if alembic.ini exists
ls alembic.ini

# Reinitialize alembic if needed
alembic init alembic
```

## 📚 Next Steps

1. ✅ Backend is running locally
2. 🔄 Next step: 2FA implementation (TOTP + Email)
3. 🔄 Next step: Frontend (Streamlit)
4. 🔄 Production deployment

## 📝 Useful Links

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 💡 Tips

- Use **Swagger UI** to test API - very convenient!
- Always activate virtual environment before work
- Commit frequently and use meaningful commit names
- Don't commit `.env` file (it's in .gitignore)

## 🎯 Project Status

- [x] Project structure
- [x] Database models (User)
- [x] Authentication endpoints (register, login, verify-2fa)
- [x] Password hashing (bcrypt)
- [x] JWT authorization
- [x] 2FA via email (6-digit codes)
- [x] Redis integration (code storage)
- [x] Rate limiting and blocking
- [x] Frontend (Streamlit with custom UI)
- [x] Frontend-Backend integration
- [x] Docker Compose deployment
- [x] MailHog email testing
- [x] Unit tests
- [ ] Integration tests (automated)
- [ ] Production deployment guide
- [ ] Password reset functionality

## 🏗️ Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Frontend   │─────▶│   Backend   │─────▶│  PostgreSQL │
│ (Streamlit) │      │  (FastAPI)  │      │  Database   │
│  Port 8501  │◀─────│  Port 8000  │      │  Port 5432  │
└─────────────┘      └─────────────┘      └─────────────┘
                            │
                            │
                     ┌──────┴──────┐
                     ▼              ▼
              ┌──────────┐   ┌──────────┐
              │  Redis   │   │ MailHog  │
              │ (Codes)  │   │ (Emails) │
              │Port 6379 │   │Port 8025 │
              └──────────┘   └──────────┘
```

## 👥 Development Team

This application was built collaboratively:

- **Backend Development**: FastAPI, PostgreSQL, Redis, 2FA service
- **Frontend Development**: Streamlit UI, custom styling, routing
- **Integration**: API handler, Docker configuration
- **Documentation**: Setup guides, troubleshooting

## 📚 Learn More

- **INTEGRATION.md** - Detailed integration documentation
- **README.md** - Project overview and API reference
- **Backend API**: http://localhost:8000/docs (Swagger UI)
