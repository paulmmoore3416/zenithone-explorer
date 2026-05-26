# ZenithOne Explorer - Troubleshooting Guide

Common issues and solutions for ZenithOne Explorer.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Backend Issues](#backend-issues)
- [CLI Issues](#cli-issues)
- [UI Issues](#ui-issues)
- [Container Issues](#container-issues)
- [Database Issues](#database-issues)
- [Performance Issues](#performance-issues)
- [Security Issues](#security-issues)

## Installation Issues

### Python Version Not Found

**Problem:** `python3.14: command not found`

**Solution:**
```bash
# Install Python 3.14
sudo apt install python3.14 python3.14-venv python3.14-dev

# Verify installation
python3.14 --version
```

### Podman Installation Fails

**Problem:** Cannot install Podman

**Solution:**
```bash
# Update package list
sudo apt update

# Install Podman
sudo apt install podman -y

# If still fails, add repository
. /etc/os-release
echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/ /" | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
curl -L "https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/Release.key" | sudo apt-key add -
sudo apt update
sudo apt install podman
```

### Ollama Model Download Fails

**Problem:** `ollama pull qwen2.5:latest` fails

**Solution:**
```bash
# Check Ollama service
systemctl status ollama

# Restart Ollama
sudo systemctl restart ollama

# Try pulling again
ollama pull qwen2.5:latest

# If still fails, check disk space
df -h

# Check network connectivity
curl -I https://ollama.com
```

## Backend Issues

### Backend Won't Start

**Problem:** `uvicorn main:app` fails

**Solution:**
```bash
# Check Python version
python3 --version

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Check for errors
python -c "import main"

# Check port availability
sudo lsof -i :8000

# Use different port
uvicorn main:app --port 8001
```

### Database Connection Error

**Problem:** `sqlite3.OperationalError: unable to open database file`

**Solution:**
```bash
# Create data directory
mkdir -p backend/data

# Check permissions
chmod 755 backend/data

# Initialize database
python -c "from database.connection import init_db; init_db()"

# Verify database file
ls -la backend/data/zenithone.db
```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

### Ollama Connection Failed

**Problem:** `Cannot connect to Ollama at http://localhost:11434`

**Solution:**
```bash
# Check Ollama service
systemctl status ollama

# Start Ollama
sudo systemctl start ollama

# Test connection
curl http://localhost:11434/api/tags

# Check firewall
sudo ufw status
sudo ufw allow 11434/tcp

# Update .env file
OLLAMA_HOST=http://localhost:11434
```

## CLI Issues

### Command Not Found

**Problem:** `zenith: command not found`

**Solution:**
```bash
# Reinstall CLI
cd cli
npm install
npm link

# Check PATH
echo $PATH

# Add to PATH if needed
echo 'export PATH="$PATH:~/.npm-global/bin"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
which zenith
zenith --version
```

### Connection Refused

**Problem:** `Error: connect ECONNREFUSED 127.0.0.1:8000`

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Start backend
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

# Update CLI configuration
zenith config set api_url http://localhost:8000/api/v1
```

### Authentication Failed

**Problem:** `Error: 401 Unauthorized`

**Solution:**
```bash
# Check auth status
zenith auth status

# Re-login
zenith auth logout
zenith auth login --username admin --password admin123

# Verify token
cat ~/.zenithone/token

# Clear cache
rm -rf ~/.zenithone/cache
```

## UI Issues

### Blank Page

**Problem:** UI shows blank page

**Solution:**
```bash
# Check browser console for errors (F12)

# Verify backend is running
curl http://localhost:8000/health

# Check API configuration in ui/assets/js/config.js
# Ensure API_BASE_URL is correct

# Clear browser cache
# Ctrl+Shift+Delete (Chrome/Firefox)

# Try incognito/private mode
```

### Login Failed

**Problem:** Cannot login to UI

**Solution:**
```bash
# Verify credentials
zenith auth login --username admin --password admin123

# Check backend logs
tail -f backend/data/logs/app.log

# Reset admin password
cd backend
python -c "
from core.security import update_user_password
update_user_password('admin', 'newpassword123')
"

# Clear browser cookies
```

### Charts Not Loading

**Problem:** Dashboard charts don't display

**Solution:**
```bash
# Check browser console for errors

# Verify Chart.js is loaded
# Open browser console and type: Chart

# Check network tab for failed requests

# Verify metrics endpoint
curl http://localhost:8000/api/v1/metrics \
  -H "Authorization: Bearer <token>"

# Clear browser cache
```

## Container Issues

### Podman Socket Not Found

**Problem:** `Error: cannot find podman socket`

**Solution:**
```bash
# Enable Podman socket
systemctl --user enable podman.socket
systemctl --user start podman.socket

# Verify socket
ls -la /run/user/$(id -u)/podman/podman.sock

# Update .env
PODMAN_SOCKET=unix:///run/user/$(id -u)/podman/podman.sock

# Test Podman
podman ps
```

### Container Won't Start

**Problem:** Container fails to start

**Solution:**
```bash
# Check container logs
podman logs <container-id>

# Inspect container
podman inspect <container-id>

# Check image exists
podman images

# Pull image if missing
podman pull python:3.14

# Check resource limits
podman stats

# Try with more resources
zenith workload create \
  --name test \
  --image alpine:latest \
  --cpu 4.0 \
  --memory 2048
```

### Permission Denied

**Problem:** `Error: permission denied`

**Solution:**
```bash
# Enable rootless mode
podman system migrate

# Add user to podman group
sudo usermod -aG podman $USER

# Logout and login again
# Or run: newgrp podman

# Verify permissions
podman info

# Check SELinux (if enabled)
sudo setenforce 0
```

## Database Issues

### Database Locked

**Problem:** `sqlite3.OperationalError: database is locked`

**Solution:**
```bash
# Stop all backend processes
pkill -f uvicorn

# Check for locks
lsof backend/data/zenithone.db

# Remove lock file
rm -f backend/data/zenithone.db-journal

# Restart backend
cd backend
source venv/bin/activate
uvicorn main:app
```

### Corrupted Database

**Problem:** Database file is corrupted

**Solution:**
```bash
# Backup current database
cp backend/data/zenithone.db backend/data/zenithone.db.backup

# Try to recover
sqlite3 backend/data/zenithone.db ".recover" | sqlite3 backend/data/zenithone_recovered.db

# If recovery fails, restore from backup
cp ~/zenithone-backups/latest.db backend/data/zenithone.db

# Or reinitialize (WARNING: data loss)
rm backend/data/zenithone.db
python -c "from database.connection import init_db; init_db()"
```

### Migration Failed

**Problem:** Database migration fails

**Solution:**
```bash
# Check current schema version
sqlite3 backend/data/zenithone.db "SELECT version FROM schema_version;"

# Backup database
cp backend/data/zenithone.db backend/data/zenithone.db.pre-migration

# Run migration manually
cd backend
python -c "from database.migrations import run_migrations; run_migrations()"

# If fails, restore backup
cp backend/data/zenithone.db.pre-migration backend/data/zenithone.db
```

## Performance Issues

### High CPU Usage

**Problem:** Backend consuming too much CPU

**Solution:**
```bash
# Check running processes
top -u $USER

# Reduce worker count
# In .env: API_WORKERS=2

# Check for infinite loops in logs
tail -f backend/data/logs/app.log

# Restart backend
sudo systemctl restart zenithone-backend

# Limit container resources
zenith admin config set default_cpu_limit 1.0
```

### High Memory Usage

**Problem:** System running out of memory

**Solution:**
```bash
# Check memory usage
free -h

# Check container memory
podman stats

# Reduce memory limits
# In .env: DEFAULT_MEMORY_LIMIT=512

# Stop unused containers
podman stop $(podman ps -q)

# Clear cache
sync; echo 3 > /proc/sys/vm/drop_caches

# Restart services
sudo systemctl restart zenithone-backend
```

### Slow Response Times

**Problem:** API responses are slow

**Solution:**
```bash
# Check system load
uptime

# Check database size
du -h backend/data/zenithone.db

# Optimize database
sqlite3 backend/data/zenithone.db "VACUUM;"

# Enable caching
# In .env: CACHE_ENABLED=true

# Increase workers
# In .env: API_WORKERS=4

# Check network latency
ping localhost
```

## Security Issues

### Unauthorized Access

**Problem:** Unauthorized users accessing system

**Solution:**
```bash
# Change admin password
zenith admin user reset-password admin

# Update secret keys
# In .env: Generate new SECRET_KEY and JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Enable rate limiting
# In .env: RATE_LIMIT_ENABLED=true

# Check access logs
tail -f backend/data/logs/access.log

# Revoke all tokens
zenith admin auth revoke-all
```

### SSL Certificate Issues

**Problem:** SSL certificate errors

**Solution:**
```bash
# Generate new certificate
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem -out cert.pem \
  -days 365 -nodes

# Update backend configuration
uvicorn main:app \
  --ssl-keyfile=key.pem \
  --ssl-certfile=cert.pem

# Trust certificate (development only)
# Chrome: chrome://settings/certificates
# Firefox: about:preferences#privacy
```

## Getting Help

### Enable Debug Mode

```bash
# Backend debug mode
# In .env: DEBUG=true, LOG_LEVEL=DEBUG

# CLI verbose mode
zenith --verbose <command>

# Check logs
tail -f backend/data/logs/app.log
tail -f ~/.zenithone/cli.log
```

### Collect Diagnostic Information

```bash
# System information
zenith admin system info > system-info.txt

# Backend logs
tail -n 1000 backend/data/logs/app.log > backend-logs.txt

# Container status
podman ps -a > containers.txt

# Configuration
zenith config show > config.txt

# Create support bundle
tar -czf zenithone-diagnostics.tar.gz \
  system-info.txt \
  backend-logs.txt \
  containers.txt \
  config.txt
```

### Report Issues

1. Check existing issues: https://github.com/paulmmoore3416/zenithone-explorer/issues
2. Create new issue with:
   - Problem description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Relevant logs
   - Screenshots (if applicable)

### Community Support

- GitHub Discussions: https://github.com/paulmmoore3416/zenithone-explorer/discussions
- Email: paulmmoore3416@gmail.com

## Next Steps

- Review [INSTALLATION.md](INSTALLATION.md) for setup
- Check [CONFIGURATION.md](CONFIGURATION.md) for settings
- See [API_REFERENCE.md](API_REFERENCE.md) for API details
