# 2FA Application

Full-stack web application implementing two-factor authentication (2FA) with verification codes sent via email.

## ✨ Main Features

- ✅ User registration and login
- ✅ Password hashing (bcrypt)
- ✅ JWT authorization with access tokens
- ✅ 2FA via email with 6-digit codes
- ✅ Streamlit frontend (fully integrated)
- ✅ Redis-based code storage with TTL
- ✅ Rate limiting and progressive blocking
- ✅ Docker Compose for easy deployment
- ✅ MailHog for email testing in development

## 🛠️ Technology Stack

### Backend

- **Framework**: FastAPI 0.104.1 (Python 3.11)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy
- **Hashing**: passlib + bcrypt
- **JWT**: python-jose
- **2FA**: Custom 6-digit codes (not TOTP)
- **Cache/Storage**: Redis 7 (for 2FA codes)
- **Email**: FastAPI-Mail
- **Email Testing**: MailHog (development)
- **Migrations**: Alembic

### Frontend

- **Framework**: Streamlit
- **HTTP Client**: httpx (async)
- **Routing**: Session-based with query params
- **Styling**: Custom CSS with cyberpunk theme

## 📁 Project Structure

```
2fa-app/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models (User)
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── api/
│   │   │   └── endpoints/   # API endpoints (auth, user)
│   │   ├── core/            # Configuration and security
│   │   ├── services/        # Business logic (2FA service)
│   │   └── utils/           # Helper utilities
│   ├── alembic/             # Database migrations
│   ├── tests/               # Backend tests
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
├── frontend/
│   ├── UI/                  # Streamlit pages
│   │   ├── login_page.py
│   │   ├── register_page.py
│   │   ├── twofa_page.py
│   │   └── profile_page.py
│   ├── services/            # API handler
│   ├── utils/               # Helpers (styles, validation)
│   ├── app.py               # Main Streamlit app
│   ├── requirements.txt
│   ├── .env
│   ├── .env.example
│   └── Dockerfile
├── docker-compose.yml       # Multi-service orchestration
├── Dockerfile               # Backend Docker image
├── README.md
├── QUICKSTART.md
└── INTEGRATION.md
```

## 🚀 Quick Start

### Requirements

- **Docker Desktop** (recommended) OR:
  - Python 3.11+
  - PostgreSQL 15+
  - Redis 7+

### Option A: Docker (Recommended) 🐳

```bash
# Clone repository
git clone https://github.com/swistakmatt/2fa-app.git
cd 2fa-app

# Start all services (postgres, redis, mailhog, backend, frontend)
docker-compose up -d

# Wait ~30 seconds for migrations to complete
```

**Access the application:**

- Frontend: http://localhost:8501
- Backend API: http://localhost:8000/docs
- MailHog (email viewer): http://localhost:8025
- pgAdmin: http://localhost:5050

### Option B: Local Development

#### Backend Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

# Configure .env (copy from .env.example)
cp .env.example .env
# Edit DATABASE_URL, SECRET_KEY, REDIS_URL, MAIL_SERVER

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Set BACKEND_API_URL=http://localhost:8000/api

# Start frontend
streamlit run app.py
```

**Note:** You'll also need PostgreSQL, Redis, and MailHog running locally.

## 📚 API Endpoints

### Authentication Flow

1. **`POST /api/auth/register`** - Register new user

   - Input: `{"email": "user@example.com", "password": "Admin123!abc"}`
   - Output: `{"id": 1, "email": "user@example.com", "message": "User successfully registered"}`
   - Note: User is immediately active (no email activation required)

2. **`POST /api/auth/login`** - Login (Step 1 - sends 2FA code)

   - Input: `{"email": "user@example.com", "password": "Admin123!abc"}`
   - Output: `{"detail": "2fa_required", "tmp_token": "eyJ..."}`
   - Action: Sends 6-digit code to email (check MailHog at http://localhost:8025)

3. **`POST /api/auth/verify-2fa`** - Verify 2FA code (Step 2 - get JWT)
   - Input: `{"tmp_token": "eyJ...", "code": "123456"}`
   - Output: `{"access_token": "eyJ...", "token_type": "bearer"}`

### User Management

- **`GET /api/user/profile`** - Get user profile (requires JWT)

  - Header: `Authorization: Bearer {access_token}`
  - Output: `{"id": 1, "email": "user@example.com", "is_active": true, ...}`

- **`PUT /api/user/update`** - Update profile (requires JWT)
- **`DELETE /api/user/delete`** - Delete account (requires JWT)

## 📧 Why MailHog Instead of Gmail?

**MailHog** is a development email testing tool that:

✅ **Catches all emails** - No emails are sent to real addresses
✅ **Web UI** - View all emails at http://localhost:8025
✅ **No configuration** - Works out of the box
✅ **Fast** - No external SMTP delays
✅ **Safe** - Won't spam real inboxes during testing

**When to use Gmail:**

- Production environment
- Real user testing
- After configuring App Password in Google Account

**To switch to Gmail:**

1. Generate App Password: https://myaccount.google.com/apppasswords
2. Update `backend/.env`:
   ```env
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=your.email@gmail.com
   MAIL_PASSWORD=your_app_password
   MAIL_STARTTLS=True
   ```
3. Restart backend: `docker-compose restart backend`

## 🔐 2FA Flow Explained

1. **Registration** → User creates account (active immediately)
2. **Login** → User enters email + password → Backend sends 6-digit code via email
3. **Check Email** → User opens MailHog (http://localhost:8025) and copies code
4. **Verify Code** → User enters code → Backend returns JWT access token
5. **Access Profile** → User can view/edit profile using JWT token

**Important:**

- 2FA code is valid for **3 minutes** (180 seconds)
- Maximum **5 attempts** before account is blocked
- Progressive blocking: 30min → 1h → 8h → 24h
- Code is stored in Redis with automatic expiration

## 🔒 Security Features

- ✅ **Password Hashing**: bcrypt with salt (cost factor 12)
- ✅ **JWT Tokens**: Access tokens with 30-minute expiration
- ✅ **2FA Codes**: 6-digit random codes, 3-minute TTL
- ✅ **Rate Limiting**: Max 5 attempts, progressive blocking
- ✅ **Redis Storage**: Automatic code expiration
- ✅ **CORS Protection**: Configured for frontend port 8501
- ✅ **SQL Injection Protection**: SQLAlchemy ORM
- ✅ **Data Validation**: Pydantic schemas
- ✅ **Temporary Tokens**: 5-minute TTL for login flow

## 🧪 Testing

### Manual Testing

1. Start application: `docker-compose up -d`
2. Open frontend: http://localhost:8501
3. Register new user
4. Login with credentials
5. Check MailHog for 2FA code: http://localhost:8025
6. Enter code and verify
7. Access profile page

### Backend Unit Tests

```bash
cd backend
pytest -v
```

### Integration Tests

See `INTEGRATION.md` for detailed testing scenarios.

## 📖 Additional Documentation

- **`QUICKSTART.md`** - Step-by-step Windows installation guide
- **`INTEGRATION.md`** - Frontend-Backend integration details
- **`DOCKER.md`** - Docker deployment and troubleshooting

## 🤝 Contributors

This project was developed collaboratively:

- Backend API implementation (FastAPI, PostgreSQL, Redis)
- 2FA email service (6-digit codes, rate limiting)
- Frontend UI (Streamlit with custom styling)
- Docker integration and deployment
- Documentation and testing

## 📝 License

MIT License - see LICENSE file for details
