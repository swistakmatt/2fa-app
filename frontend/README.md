# Frontend - 2FA Application (Streamlit)

Modern, interactive frontend for the 2FA authentication application built with Streamlit.

## ✨ Features

- 🎨 **Custom Cyberpunk UI** - Animated background, glassmorphism effects
- 🔐 **Complete Auth Flow** - Register, Login, 2FA Verification, Profile
- 🔄 **Session-based Routing** - Smooth navigation between pages
- ⏱️ **Live Timer** - 90-second countdown for 2FA code expiration
- 🎯 **Auto-focus** - Automatic input field focus and navigation
- 📱 **Responsive Design** - Works on desktop and mobile
- 🚀 **Fast & Lightweight** - Streamlit with async HTTP client

## 🛠️ Technology Stack

- **Framework**: Streamlit 1.30.0
- **HTTP Client**: httpx (async)
- **Environment**: python-dotenv
- **Styling**: Custom CSS with animations
- **JavaScript**: Timer, auto-focus, input validation

## 📁 Project Structure

```
frontend/
├── UI/
│   ├── login_page.py           # Login page with email/password
│   ├── register_page.py         # User registration
│   ├── twofa_page.py            # 2FA code verification (6 digits)
│   ├── profile_page.py          # User profile (authenticated)
│   ├── success_register_page.py # Registration success message
│   └── password_reminder_page.py # Password reset (placeholder)
├── services/
│   └── api_handler.py           # Backend API communication
├── utils/
│   ├── styles.py                # Custom CSS styles
│   └── validators.py            # Input validation
├── app.py                       # Main Streamlit application
├── requirements.txt             # Python dependencies
├── .env                         # Environment configuration
├── .env.example                 # Example environment variables
├── Dockerfile                   # Container configuration
└── README.md                    # This file
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# From project root
docker-compose up -d frontend

# Access at http://localhost:8501
```

### Option 2: Local Development

```bash
cd frontend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set BACKEND_API_URL=http://localhost:8000/api

# Run Streamlit
streamlit run app.py
```

Frontend will be available at: http://localhost:8501

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Backend API URL
BACKEND_API_URL=http://localhost:8000/api  # Local development
# BACKEND_API_URL=http://backend:8000/api  # Docker
```

### Streamlit Configuration

Create `.streamlit/config.toml` for custom settings:

```toml
[server]
port = 8501
address = "0.0.0.0"

[theme]
primaryColor = "#00ff41"
backgroundColor = "#0a0e27"
secondaryBackgroundColor = "#1a1f3a"
textColor = "#ffffff"
```

## 📄 Pages Overview

### 1. Login Page (`login_page.py`)
- Email and password inputs
- Form validation
- Calls `/api/auth/login` endpoint
- Receives `tmp_token` on success
- Redirects to 2FA page

### 2. Register Page (`register_page.py`)
- Email and password registration
- Password confirmation
- Password strength validation (min 8 chars)
- Calls `/api/auth/register` endpoint
- Redirects to success page

### 3. 2FA Page (`twofa_page.py`)
- 6-digit PIN input (separate boxes)
- Live 90-second countdown timer
- Auto-focus and auto-jump between inputs
- Calls `/api/auth/verify-2fa` endpoint
- Receives JWT `access_token` on success
- Stores token in session state

### 4. Profile Page (`profile_page.py`)
- Displays user information (email, ID, dates)
- Logout functionality
- Protected route (requires JWT token)
- Calls `/api/user/profile` endpoint

### 5. Success Register Page (`success_register_page.py`)
- Registration confirmation message
- Link to login page

### 6. Password Reminder Page (`password_reminder_page.py`)
- Password reset flow (not yet integrated)

## 🔌 API Integration

### API Handler (`services/api_handler.py`)

The `APIHandler` class manages all backend communication:

```python
from services.api_handler import api_handler

# Register new user
result = await api_handler.register(email, password)

# Login (get tmp_token)
result = await api_handler.login(email, password)

# Verify 2FA code (get access_token)
result = await api_handler.verify_2fa(tmp_token, code)

# Get user profile (requires JWT)
result = await api_handler.get_profile(access_token)
```

### Authentication Flow

```
1. Register → /api/auth/register
   ↓
2. Login → /api/auth/login → tmp_token
   ↓
3. Check Email (MailHog) → Copy 6-digit code
   ↓
4. Verify 2FA → /api/auth/verify-2fa → access_token
   ↓
5. Access Profile → /api/user/profile (with JWT)
```

## 🎨 Styling

### Custom CSS (`utils/styles.py`)

The frontend uses custom CSS for:
- **Animated background**: Moving grid effect
- **Glassmorphism**: Semi-transparent containers
- **Neon effects**: Glowing borders and text
- **Responsive design**: Mobile-friendly layouts

### Color Palette

- **Primary**: `#00ff41` (Matrix green)
- **Secondary**: `#00d4ff` (Cyan blue)
- **Background**: `#0a0e27` (Dark navy)
- **Container**: `rgba(26, 31, 58, 0.8)` (Semi-transparent)

## 🔒 Session Management

### Session State Variables

```python
st.session_state.page          # Current page name
st.session_state.tmp_token     # Temporary token from login
st.session_state.access_token  # JWT token after 2FA
st.session_state.user_email    # Logged-in user email
```

### Navigation

```python
# Navigate to different page
st.session_state.page = "twofa"
st.rerun()

# Or use query params
st.query_params.update(page="profile")
```

## 🧪 Testing

### Manual Testing

1. **Start backend**: `docker-compose up -d backend`
2. **Start frontend**: `streamlit run app.py`
3. **Test flow**:
   - Register new user
   - Login with credentials
   - Check MailHog for 2FA code (http://localhost:8025)
   - Enter code and verify
   - Access profile page

### Common Test Scenarios

```python
# Valid registration
Email: test@example.com
Password: Admin123!abc

# Invalid password (too short)
Password: 12345

# Invalid 2FA code
Code: 000000

# Expired token
Wait > 5 minutes after login
```

## 🐛 Troubleshooting

### Problem: "Cannot connect to backend"

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify BACKEND_API_URL in .env
echo $env:BACKEND_API_URL  # Windows
echo $BACKEND_API_URL      # Linux/Mac
```

### Problem: "Page not loading / blank screen"

**Solution:**
```bash
# Clear Streamlit cache
streamlit cache clear

# Restart Streamlit
Ctrl+C, then: streamlit run app.py
```

### Problem: "2FA code not working"

**Solution:**
- Check if code is still valid (3-minute TTL)
- Verify you copied the correct code from MailHog
- Ensure backend and Redis are running

### Problem: "Styles not applying"

**Solution:**
```bash
# Force reload browser (Ctrl+Shift+R)
# Check browser console for CSS errors
# Verify styles.py is imported in app.py
```

## 📦 Dependencies

```txt
streamlit==1.30.0      # Web framework
httpx==0.25.2          # Async HTTP client
python-dotenv==1.0.0   # Environment variables
```

Install all:
```bash
pip install -r requirements.txt
```

## 🚢 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t 2fa-frontend .
docker run -p 8501:8501 2fa-frontend
```

### Environment Variables for Production

```env
BACKEND_API_URL=https://api.yourdomain.com/api
```

## 🔗 Links

- **Frontend App**: http://localhost:8501
- **Backend API**: http://localhost:8000/docs
- **MailHog**: http://localhost:8025
- **GitHub**: https://github.com/swistakmatt/2fa-app

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [httpx Documentation](https://www.python-httpx.org/)
- [Project Main README](../README.md)
- [Integration Guide](../INTEGRATION.md)

## 🤝 Contributing

The frontend was developed collaboratively with focus on:
- Clean, maintainable code
- User-friendly interface
- Responsive design
- Security best practices

## 📝 License

MIT License - see [LICENSE](../LICENSE) file for details
