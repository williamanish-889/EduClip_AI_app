# EduClip AI - Complete Setup and Deployment Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Detailed Installation](#detailed-installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Testing](#testing)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Minimum Requirements
- Python 3.8+
- 4GB RAM
- 10GB free disk space
- Internet connection (for AI APIs)

### One-Command Setup (Linux/Mac)
```bash
# Clone and setup
git clone https://github.com/yourusername/educlip-ai.git
cd educlip-ai
chmod +x setup.sh
./setup.sh
```

### Windows Setup
```cmd
# Run PowerShell as Administrator
git clone https://github.com/yourusername/educlip-ai.git
cd educlip-ai
powershell -ExecutionPolicy Bypass -File setup.ps1
```

## 📥 Detailed Installation

### Step 1: System Prerequisites

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3.8 python3-pip python3-venv
sudo apt install -y ffmpeg
sudo apt install -y postgresql postgresql-contrib
```

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.8
brew install ffmpeg
brew install postgresql
```

#### Windows
1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
3. Download PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)

### Step 2: Project Setup

```bash
# Create project directory
mkdir educlip-ai
cd educlip-ai

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Python Dependencies

```bash
# Install all required packages
pip install -r code/requirements.txt

# Download NLTK data (required for NLP)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Step 4: Database Setup

#### PostgreSQL Setup

**Create Database:**
```bash
# Start PostgreSQL service
sudo service postgresql start  # Linux
brew services start postgresql  # Mac

# Create user and database
sudo -u postgres psql
```

**In psql prompt:**
```sql
CREATE USER educlip_user WITH PASSWORD 'secure_password';
CREATE DATABASE educlip_db OWNER educlip_user;
GRANT ALL PRIVILEGES ON DATABASE educlip_db TO educlip_user;
\q
```

**Load Schema:**
```bash
psql -U educlip_user -d educlip_db -f code/database/schema.sql
```

#### MySQL Setup (Alternative)

```bash
# Create database
mysql -u root -p
```

**In MySQL prompt:**
```sql
CREATE DATABASE educlip_db;
CREATE USER 'educlip_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON educlip_db.* TO 'educlip_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Load Schema:**
```bash
mysql -u educlip_user -p educlip_db < code/database/schema.sql
```

### Step 5: Environment Configuration

Create `.env` file in project root:

```bash
# .env file
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=postgresql://educlip_user:secure_password@localhost:5432/educlip_db
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-key-optional

# Optional configurations
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# Storage paths
UPLOAD_DIR=./storage/uploads
CLIPS_DIR=./storage/clips
THUMBNAILS_DIR=./storage/thumbnails

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# JWT Configuration
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# File Upload Limits
MAX_UPLOAD_SIZE=2147483648  # 2GB in bytes
```

### Step 6: Create Storage Directories

```bash
mkdir -p storage/uploads
mkdir -p storage/clips
mkdir -p storage/thumbnails
mkdir -p logs
```

## ⚙️ Configuration

### Getting API Keys

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key to your `.env` file

#### OpenAI API Key (Optional)
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key to your `.env` file

### Database Configuration Options

**For Production:**
```python
# Use connection pooling
DATABASE_URL=postgresql://user:pass@host:5432/db?pool_size=20&max_overflow=0
```

**For SQLite (Development Only):**
```python
DATABASE_URL=sqlite:///./educlip.db
```

## 🏃 Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd code/backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd code/frontend
python -m http.server 8080
```

Access the application:
- Frontend: http://localhost:8080
- API Documentation: http://localhost:8000/docs
- API Health Check: http://localhost:8000/health

### Production Mode

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn code.backend.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
```

### Using Docker (Recommended for Production)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY code/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create storage directories
RUN mkdir -p storage/uploads storage/clips storage/thumbnails logs

EXPOSE 8000

CMD ["gunicorn", "code.backend.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: educlip_db
      POSTGRES_USER: educlip_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./code/database/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "5432:5432"

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://educlip_user:secure_password@postgres:5432/educlip_db
      - SECRET_KEY=your-secret-key
      - GEMINI_API_KEY=your-api-key
    volumes:
      - ./storage:/app/storage
      - ./logs:/app/logs
    depends_on:
      - postgres

  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./code/frontend:/usr/share/nginx/html:ro

volumes:
  postgres_data:
```

**Run with Docker:**
```bash
docker-compose up -d
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest --cov=code --cov-report=html tests/
# View coverage report at htmlcov/index.html
```

### Test Specific Module
```bash
pytest tests/test_api.py -v
```

### Manual API Testing

Use the interactive API docs:
1. Open http://localhost:8000/docs
2. Try out endpoints
3. View request/response schemas

Or use curl:
```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test123","role":"educator"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'
```

## 🌐 Deployment

### Cloud Deployment Options

#### AWS Deployment

**1. EC2 Instance:**
```bash
# SSH into EC2 instance
ssh -i key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install -y python3-pip ffmpeg postgresql

# Clone and setup project
git clone https://github.com/yourusername/educlip-ai.git
cd educlip-ai
pip3 install -r code/requirements.txt

# Setup systemd service
sudo nano /etc/systemd/system/educlip.service
```

**Service file content:**
```ini
[Unit]
Description=EduClip AI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/educlip-ai
Environment="PATH=/home/ubuntu/educlip-ai/venv/bin"
ExecStart=/home/ubuntu/educlip-ai/venv/bin/gunicorn code.backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl enable educlip
sudo systemctl start educlip
```

**2. Setup Nginx:**
```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/educlip
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /home/ubuntu/educlip-ai/code/frontend;
        index index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/educlip /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Heroku Deployment

Create `Procfile`:
```
web: gunicorn code.backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

Create `runtime.txt`:
```
python-3.9.16
```

Deploy:
```bash
heroku login
heroku create educlip-ai
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set SECRET_KEY=your-key
heroku config:set GEMINI_API_KEY=your-key
git push heroku main
```

#### Google Cloud Platform

```bash
# Install Google Cloud SDK
gcloud init

# Create App Engine configuration
echo "runtime: python39" > app.yaml

# Deploy
gcloud app deploy
```

### SSL Certificate (Production)

```bash
# Using Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 🔧 Troubleshooting

### Common Issues

**1. FFmpeg not found**
```bash
# Check installation
ffmpeg -version

# If not found, reinstall
sudo apt install ffmpeg  # Linux
brew install ffmpeg      # Mac
```

**2. Database connection error**
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Test connection
psql -U educlip_user -d educlip_db -c "SELECT 1;"
```

**3. Import errors**
```bash
# Reinstall dependencies
pip install --force-reinstall -r code/requirements.txt
```

**4. Permission errors**
```bash
# Fix storage directory permissions
chmod -R 755 storage/
chown -R $USER:$USER storage/
```

**5. Port already in use**
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

### Debug Mode

Enable detailed logging:
```python
# In .env
DEBUG=True
LOG_LEVEL=DEBUG
```

View logs:
```bash
tail -f logs/app.log
```

### Performance Issues

**Check system resources:**
```bash
# CPU and memory
htop

# Disk space
df -h

# Database connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

## 📊 Monitoring

### Setup Monitoring (Optional)

**Install Prometheus:**
```bash
# Add metrics endpoint to main.py
from prometheus_client import make_asgi_app

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

**Setup Grafana:**
```bash
docker run -d -p 3000:3000 grafana/grafana
```

## 🔄 Updates and Maintenance

### Update Application
```bash
git pull origin main
pip install -r code/requirements.txt
sudo systemctl restart educlip
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

### Backup Database
```bash
# PostgreSQL backup
pg_dump -U educlip_user educlip_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U educlip_user educlip_db < backup_20260128.sql
```

## 📞 Support

For deployment issues:
- Check logs in `logs/` directory
- Review API docs at `/docs`
- Open GitHub issue
- Email: support@educlip.ai

## ✅ Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] FFmpeg installed
- [ ] Database created and schema loaded
- [ ] Environment variables configured
- [ ] Storage directories created
- [ ] Dependencies installed
- [ ] Tests passing
- [ ] API accessible
- [ ] Frontend accessible
- [ ] SSL certificate (production)
- [ ] Firewall configured
- [ ] Backups scheduled
- [ ] Monitoring enabled

---

**Deployment successful! 🎉**
