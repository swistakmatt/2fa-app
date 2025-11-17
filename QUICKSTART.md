# Quick Start Guide - 2FA Application

This guide will help you quickly run the application on your Windows system.

## Prerequisites

Before starting, make sure you have installed:

- ✅ Python 3.10 or newer
- ✅ **Docker Desktop** (recommended) OR PostgreSQL 14+
- ✅ Git

## Step 1: Clone Repository

```powershell
git clone https://github.com/swistakmatt/2fa-app.git
cd 2fa-app
```

## Step 2: Run PostgreSQL

### Option A: Docker (Recommended - easiest!) 🐳

```powershell
# Run PostgreSQL in Docker container
docker-compose up -d postgres
```

Database is ready! Connection string:

```
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/2fa_app_db
```

📚 More information: see `DOCKER.md` file

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

## Step 4: API Testing

### User registration

In Swagger UI (http://localhost:8000/docs) or via cURL:

```powershell
curl -X POST "http://localhost:8000/api/auth/register" `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@example.com\",\"password\":\"testpass123\"}'
```

### Login

```powershell
curl -X POST "http://localhost:8000/api/auth/login" `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@example.com\",\"password\":\"testpass123\"}'
```

You will receive a JWT token that you can use for authorization.

### Get profile

```powershell
curl -X GET "http://localhost:8000/api/user/profile" `
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
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
- [x] Database models
- [x] Authentication endpoints
- [x] Password hashing (bcrypt)
- [x] JWT authorization
- [x] Unit tests
- [ ] 2FA via email
- [ ] Frontend (Streamlit)
- [ ] Deployment

---

**Need help?** Check `backend/README.md` for more detailed instructions.
