# Backend - 2FA Application

Backend of two-factor authentication application built with FastAPI.

## 🚀 Quick Start

### 1. Create virtual environment

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Environment variables configuration

Copy `.env.example` file to `.env` and fill in the values:

```powershell
cp .env.example .env
```

**Important:** Set in `.env` file:

- `DATABASE_URL` - URL to your PostgreSQL database
- `SECRET_KEY` - random key (you can generate it with the command below)

Generate SECRET_KEY:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Create database

Make sure PostgreSQL is running and create the database:

```sql
CREATE DATABASE 2fa_app_db;
```

### 5. Run migrations

```powershell
alembic upgrade head
```

If this is the first migration, generate it first:

```powershell
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 6. Run the application

```powershell
uvicorn app.main:app --reload
```

Application will be available at: `http://localhost:8000`

## 📚 API Documentation

After running the application, documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

Run tests:

```powershell
pytest
```

With code coverage:

```powershell
pytest --cov=app --cov-report=html
```

## 📋 API Endpoints

### Authentication (`/api/auth`)

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - Logout

### User (`/api/user`)

- `GET /api/user/profile` - Get profile (requires JWT)
- `PUT /api/user/update` - Update profile (requires JWT)
- `DELETE /api/user/delete` - Delete account (requires JWT)

## 🗂️ Project Structure

```
backend/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas (validation)
│   ├── api/
│   │   ├── endpoints/   # API endpoints
│   │   └── deps.py      # Dependency injection
│   ├── core/
│   │   ├── config.py    # Application configuration
│   │   ├── database.py  # Database connection
│   │   └── security.py  # JWT, password hashing
│   ├── services/        # Business logic
│   └── main.py          # Main application file
├── alembic/             # Database migrations
├── tests/               # Tests
└── requirements.txt     # Dependencies
```

## 🔒 Security

- Passwords hashed with **bcrypt** algorithm
- **JWT** tokens with expiration date (default 30 min)
- Input data validation with **Pydantic**
- **CORS** configured for allowed origins
- **SQL injection** protection (SQLAlchemy ORM)

## 🛠️ Development Tools

### Create new migration

```powershell
alembic revision --autogenerate -m "Migration description"
```

### Rollback migration

```powershell
alembic downgrade -1
```

### Check migration history

```powershell
alembic history
```

### Code formatting (Black)

```powershell
black app/
```

### Linting (Flake8)

```powershell
flake8 app/
```

## 📝 Environment Variables

Full list of variables in `.env.example` file.

| Variable                      | Description             | Example                                    |
| ----------------------------- | ----------------------- | ------------------------------------------ |
| `DATABASE_URL`                | PostgreSQL database URL | `postgresql://user:pass@localhost:5432/db` |
| `SECRET_KEY`                  | Key for JWT signing     | `supersecretkey123`                        |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token validity time     | `30`                                       |
| `DEBUG`                       | Debug mode              | `True`                                     |

## 🐛 Troubleshooting

### Database connection error

- Check if PostgreSQL is running
- Verify `DATABASE_URL` in `.env` file
- Make sure the database has been created

### Import errors

```powershell
# Refresh virtual environment
deactivate
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Port already in use

Change port in run command:

```powershell
uvicorn app.main:app --reload --port 8001
```
