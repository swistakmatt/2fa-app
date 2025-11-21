FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (needed for psycopg2)
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev gcc \
    && apt-get clean

# Copy requirements first (better Docker caching)
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code into the image
COPY backend /app

# Expose application port
EXPOSE 8000

# Run migrations automatically on container start
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
