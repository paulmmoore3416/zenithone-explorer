# ZenithOne Explorer - Installation Guide

Complete step-by-step installation guide for ZenithOne Explorer.

## Table of Contents

- [System Requirements](#system-requirements)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Backend Installation](#backend-installation)
- [CLI Installation](#cli-installation)
- [UI Setup](#ui-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+ (or compatible Linux distribution)
- **CPU**: 4 cores (Intel/AMD x86_64)
- **RAM**: 8 GB
- **Storage**: 20 GB free space
- **Network**: Internet connection for initial setup

### Recommended Requirements
- **OS**: Ubuntu 22.04 LTS
- **CPU**: 8+ cores (Intel i7 or equivalent)
- **RAM**: 16 GB+
- **Storage**: 50 GB+ SSD
- **Network**: High-speed internet connection

### Tested Hardware
- **Alienware Area 51 R5**: Intel i7-7820X (8C/16T), 22GB RAM, 1.5TB Storage

## Prerequisites

### 1. System Updates

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Python 3.14+

```bash
# Check Python version
python3 --version

# If Python 3.14 not installed
sudo apt install python3.14 python3.14-venv python3.14-dev -y
```

### 3. Podman (Container Runtime)

```bash
# Install Podman
sudo apt install podman -y

# Verify installation
podman --version

# Configure rootless mode
podman system migrate
```

### 4. Ollama (AI Engine)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Pull Qwen2.5 model
ollama pull qwen2.5:latest
```

### 5. Git

```bash
sudo apt install git -y
git --version
```

### 6. Node.js 22+ (for CLI)

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install nodejs -y

# Verify installation
node --version
npm --version
```

## Installation Methods

### Method 1: Quick Install (Recommended)

```bash
# Clone repository
git clone https://github.com/paulmmoore3416/zenithone-explorer.git
cd zenithone-explorer

# Run installation script
chmod +x scripts/install.sh
./scripts/install.sh
```

### Method 2: Manual Installation

Follow the detailed steps below for manual installation.

## Backend Installation

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python3.14 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp ../.env.example .env

# Edit configuration
nano .env
```

**Required Environment Variables:**

```bash
# Database
DATABASE_URL=sqlite:///./data/zenithone.db

# Security
SECRET_KEY=your-secret-key-here-change-this
JWT_SECRET_KEY=your-jwt-secret-key-here-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:latest

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Podman
PODMAN_SOCKET=unix:///run/user/1000/podman/podman.sock
```

### 5. Initialize Database

```bash
python -c "from database.connection import init_db; init_db()"
```

### 6. Create Admin User

```bash
python -c "
from core.security import create_user
create_user('admin', 'admin@example.com', 'admin123', 'admin')
print('Admin user created successfully')
"
```

### 7. Start Backend Server

```bash
# Development mode
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 8. Verify Backend

```bash
# In another terminal
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

## CLI Installation

### 1. Navigate to CLI Directory

```bash
cd cli
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Link CLI Globally

```bash
npm link
```

### 4. Configure CLI

```bash
# Create config directory
mkdir -p ~/.zenithone

# Create config file
cat > ~/.zenithone/config.json << EOF
{
  "api_url": "http://localhost:8000/api/v1",
  "timeout": 30000,
  "output_format": "table"
}
EOF
```

### 5. Verify CLI

```bash
zenith --version
zenith --help
```

### 6. Login

```bash
zenith auth login --username admin --password admin123
```

## UI Setup

### Method 1: Serve from Backend

The UI is automatically served by the backend at `http://localhost:8000`

### Method 2: Standalone Web Server

```bash
# Install web server
sudo apt install nginx -y

# Copy UI files
sudo cp -r ui/* /var/www/html/

# Configure nginx
sudo nano /etc/nginx/sites-available/zenithone

# Add configuration:
server {
    listen 80;
    server_name localhost;
    root /var/www/html;
    index index.html;
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/zenithone /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Method 3: Python HTTP Server

```bash
cd ui
python3 -m http.server 8080
```

Access UI at: `http://localhost:8080`

## Systemd Service Setup (Optional)

### Backend Service

```bash
sudo nano /etc/systemd/system/zenithone-backend.service
```

```ini
[Unit]
Description=ZenithOne Explorer Backend
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/zenithone-explorer/backend
Environment="PATH=/path/to/zenithone-explorer/backend/venv/bin"
ExecStart=/path/to/zenithone-explorer/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable zenithone-backend
sudo systemctl start zenithone-backend
sudo systemctl status zenithone-backend
```

## Verification

### 1. Check All Services

```bash
# Backend
curl http://localhost:8000/health

# Ollama
ollama list

# Podman
podman ps

# CLI
zenith auth status
```

### 2. Run Test Workload

```bash
zenith workload create \
  --name "test-workload" \
  --type batch \
  --image alpine:latest \
  --command "echo 'Hello ZenithOne'"

zenith workload list
```

### 3. Access UI

Open browser: `http://localhost:8000`

Login with:
- Username: `admin`
- Password: `admin123`

## Post-Installation

### 1. Security Hardening

```bash
# Change default passwords
zenith admin user update --username admin --password NEW_SECURE_PASSWORD

# Update environment variables
nano backend/.env
# Change SECRET_KEY and JWT_SECRET_KEY
```

### 2. Configure Firewall

```bash
sudo ufw allow 8000/tcp
sudo ufw enable
```

### 3. Set Up Backups

```bash
# Create backup script
cat > ~/backup-zenithone.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/zenithone-backups
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf $BACKUP_DIR/zenithone-$DATE.tar.gz \
  ~/zenithone-explorer/backend/data \
  ~/zenithone-explorer/backend/.env
echo "Backup created: $BACKUP_DIR/zenithone-$DATE.tar.gz"
EOF

chmod +x ~/backup-zenithone.sh

# Add to crontab (daily backup at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/backup-zenithone.sh") | crontab -
```

## Troubleshooting

### Backend Won't Start

```bash
# Check Python version
python3 --version

# Check dependencies
pip list

# Check logs
tail -f backend/data/logs/app.log

# Verify database
ls -la backend/data/
```

### Ollama Connection Issues

```bash
# Check Ollama service
systemctl status ollama

# Restart Ollama
systemctl restart ollama

# Test connection
curl http://localhost:11434/api/tags
```

### Podman Permission Issues

```bash
# Enable rootless mode
podman system migrate

# Check socket
ls -la /run/user/$(id -u)/podman/podman.sock

# Test Podman
podman run --rm alpine echo "test"
```

### CLI Not Found

```bash
# Reinstall CLI
cd cli
npm link

# Check PATH
echo $PATH

# Add to PATH if needed
echo 'export PATH="$PATH:~/.npm-global/bin"' >> ~/.bashrc
source ~/.bashrc
```

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or use different port
uvicorn main:app --port 8001
```

## Uninstallation

```bash
# Stop services
sudo systemctl stop zenithone-backend
sudo systemctl disable zenithone-backend

# Remove systemd service
sudo rm /etc/systemd/system/zenithone-backend.service
sudo systemctl daemon-reload

# Unlink CLI
cd cli
npm unlink

# Remove files
cd ~
rm -rf zenithone-explorer

# Remove data (optional)
rm -rf ~/.zenithone
```

## Next Steps

- Read [CONFIGURATION.md](CONFIGURATION.md) for advanced configuration
- Check [CLI_GUIDE.md](CLI_GUIDE.md) for CLI usage
- See [UI_GUIDE.md](UI_GUIDE.md) for UI documentation
- Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

## Support

- GitHub Issues: https://github.com/paulmmoore3416/zenithone-explorer/issues
- Documentation: https://github.com/paulmmoore3416/zenithone-explorer/docs
- Email: paulmmoore3416@gmail.com
