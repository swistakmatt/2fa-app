# Docker - PostgreSQL for 2FA App

Docker configuration for local development environment with PostgreSQL.

## 🐳 Quick Start

### 1. Run PostgreSQL

```powershell
# From project root directory
docker-compose up -d postgres
```

### 2. Check status

```powershell
docker-compose ps
```

You should see:

```
NAME            STATUS          PORTS
2fa_postgres    Up (healthy)    0.0.0.0:5432->5432/tcp
```

### 3. Connect to database

Access credentials:

- **Host**: localhost
- **Port**: 5432
- **Database**: 2fa_app_db
- **User**: postgres
- **Password**: postgres123

**Connection String for .env:**

```env
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/2fa_app_db
```

## 🔧 Useful Commands

### Start containers

```powershell
# PostgreSQL only
docker-compose up -d postgres

# PostgreSQL + pgAdmin
docker-compose up -d
```

### Stop containers

```powershell
docker-compose down
```

### Remove data (cleanup)

```powershell
# WARNING: This removes all data!
docker-compose down -v
```

### Logs

```powershell
# PostgreSQL logs
docker-compose logs postgres

# Live logs
docker-compose logs -f postgres
```

### Restart container

```powershell
docker-compose restart postgres
```

## 🌐 pgAdmin (Web Interface)

If you run full docker-compose, you'll have access to pgAdmin:

1. Open: http://localhost:5050
2. Login:

   - Email: `admin@admin.com`
   - Password: `admin123`

3. Add PostgreSQL server:
   - "General" tab:
     - Name: `2FA App DB`
   - "Connection" tab:
     - Host: `postgres` (container name)
     - Port: `5432`
     - Database: `2fa_app_db`
     - Username: `postgres`
     - Password: `postgres123`

## 🔍 Connection Testing

## 🔍 Connection Testing

### Via psql in container

```powershell
docker exec -it 2fa_postgres psql -U postgres -d 2fa_app_db
```

Command will display:

```
psql (15.x)
Type "help" for help.

2fa_app_db=#
```

You can now execute SQL queries:

```sql
-- Check tables
\dt

-- View users
SELECT * FROM users;

-- Exit
\q
```

### Via Python

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="2fa_app_db",
    user="postgres",
    password="postgres123"
)
print("Connected to database!")
conn.close()
```

## 📊 Volume Structure

Docker creates persistent volumes for data:

```
postgres_data    -> PostgreSQL data (tables, indexes)
pgadmin_data     -> pgAdmin configuration
```

Data persists even after `docker-compose down`.

## 🛠️ Troubleshooting

### Problem: Port 5432 already in use

**Solution 1** - Change port in docker-compose.yml:

```yaml
ports:
  - '5433:5432' # External port 5433
```

Then connection string:

```
DATABASE_URL=postgresql://postgres:postgres123@localhost:5433/2fa_app_db
```

**Solution 2** - Stop local PostgreSQL:

```powershell
# Check if PostgreSQL is running locally
Get-Service -Name postgresql*

# Stop service
Stop-Service -Name postgresql-x64-14  # Adjust name
```

### Problem: Container won't start

```powershell
# View detailed logs
docker-compose logs postgres

# Remove everything and start fresh
docker-compose down -v
docker-compose up -d postgres
```

### Problem: Cannot connect to pgAdmin

- Check if container is running: `docker-compose ps`
- Check logs: `docker-compose logs pgadmin`
- Wait ~30 seconds for full startup

## 🔒 Security

⚠️ **WARNING:** This configuration is for local development only!

For production:

- Change passwords to strong ones
- Use secrets instead of plain text
- Configure SSL/TLS
- Restrict network access

## 📝 Changing Password

Edit `docker-compose.yml`:

```yaml
environment:
  POSTGRES_PASSWORD: your_new_password
```

Then:

```powershell
docker-compose down -v  # Remove old data
docker-compose up -d postgres
```

## 🚀 Application Integration

After running PostgreSQL via Docker:

1. Update `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/2fa_app_db
```

2. Run migrations:

```powershell
cd backend
.\venv\Scripts\activate
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

3. Run application:

```powershell
uvicorn app.main:app --reload
```

Done! 🎉
