# 2FA Application

Web application implementing two-factor authentication (2FA) with TOTP codes sent via email.

### Main features:

- ✅ User registration and login
- ✅ Password hashing (bcrypt)
- ✅ JWT authorization
- 🔄 2FA via email with TOTP codes (in progress)
- 🔄 Streamlit frontend (planned)

## 🛠️ Technology Stack

### Backend

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Hashing**: passlib + bcrypt
- **JWT**: python-jose
- **2FA**: pyotp (TOTP)
- **Email**: FastAPI Mail
- **Migrations**: Alembic

### Frontend (planned)

- **Framework**: Streamlit

## 📁 Project Structure

```
2fa-app/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── api/
│   │   │   └── endpoints/   # API endpoints
│   │   ├── core/            # Configuration and security
│   │   ├── services/        # Business logic
│   │   └── utils/           # Helper utilities
│   ├── tests/               # Tests
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

## 🚀 Installation and Setup

### Requirements

- Python 3.10+
- PostgreSQL 14+
- pip or poetry

### Step 1: Clone the repository

```bash
git clone https://github.com/swistakmatt/2fa-app.git
cd 2fa-app
```

### Step 2: Configure backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Database configuration

```bash
# Copy .env.example file
cp .env.example .env

# Edit .env and set DATABASE_URL and SECRET_KEY
```

### Step 4: Run migrations

```bash
alembic upgrade head
```

### Step 5: Run the application

```bash
uvicorn app.main:app --reload
```

API will be available at: `http://localhost:8000`

API Documentation (Swagger): `http://localhost:8000/docs`

## 📚 API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - Logout (planned)

### User

- `GET /api/user/profile` - Get user profile (requires JWT)
- `PUT /api/user/update` - Update profile (planned)

### 2FA (in progress)

- `POST /api/auth/verify-2fa` - Verify 2FA code
- `POST /api/auth/resend-code` - Resend code

## 🔒 Security

- Passwords hashed with bcrypt algorithm
- JWT tokens with expiration date
- Data validation (Pydantic)
- Rate limiting (planned)
- CORS configuration
- SQL injection protection (SQLAlchemy ORM)

## 🧪 Testing

```bash
pytest
```
