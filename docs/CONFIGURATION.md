# ZenithOne Explorer - Configuration Reference

Complete configuration reference for ZenithOne Explorer.

## Table of Contents

- [Environment Variables](#environment-variables)
- [Backend Configuration](#backend-configuration)
- [CLI Configuration](#cli-configuration)
- [UI Configuration](#ui-configuration)
- [Database Configuration](#database-configuration)
- [Security Configuration](#security-configuration)
- [Performance Tuning](#performance-tuning)
- [Logging Configuration](#logging-configuration)

## Environment Variables

### Backend (.env)

Located at: `backend/.env`

```bash
# ============================================
# DATABASE CONFIGURATION
# ============================================
DATABASE_URL=sqlite:///./data/zenithone.db
# For PostgreSQL: postgresql://user:password@localhost/zenithone
# For MySQL: mysql://user:password@localhost/zenithone

# ============================================
# SECURITY
# ============================================
SECRET_KEY=your-secret-key-min-32-chars-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Policy
MIN_PASSWORD_LENGTH=8
REQUIRE_UPPERCASE=true
REQUIRE_LOWERCASE=true
REQUIRE_NUMBERS=true
REQUIRE_SPECIAL_CHARS=true

# ============================================
# API CONFIGURATION
# ============================================
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=false
API_DEBUG=false

# CORS Settings
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET","POST","PUT","DELETE","PATCH"]
CORS_ALLOW_HEADERS=["*"]

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# ============================================
# OLLAMA (AI ENGINE)
# ============================================
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:latest
OLLAMA_TIMEOUT=120
OLLAMA_TEMPERATURE=0.7
OLLAMA_MAX_TOKENS=2048

# AI Features
AI_WORKLOAD_OPTIMIZATION=true
AI_RESOURCE_PREDICTION=true
AI_ANOMALY_DETECTION=true

# ============================================
# PODMAN (CONTAINER RUNTIME)
# ============================================
PODMAN_SOCKET=unix:///run/user/1000/podman/podman.sock
PODMAN_TIMEOUT=300
PODMAN_MAX_CONTAINERS=50

# Container Defaults
DEFAULT_CPU_LIMIT=2.0
DEFAULT_MEMORY_LIMIT=1024
DEFAULT_NETWORK_MODE=bridge

# ============================================
# WORKLOAD MANAGEMENT
# ============================================
MAX_CONCURRENT_WORKLOADS=10
WORKLOAD_TIMEOUT=3600
WORKLOAD_RETRY_ATTEMPTS=3
WORKLOAD_CLEANUP_INTERVAL=300

# Priority Levels
PRIORITY_CRITICAL_WEIGHT=10
PRIORITY_HIGH_WEIGHT=5
PRIORITY_NORMAL_WEIGHT=1
PRIORITY_LOW_WEIGHT=0.5

# ============================================
# MONITORING & METRICS
# ============================================
METRICS_ENABLED=true
METRICS_INTERVAL=60
METRICS_RETENTION_DAYS=30
METRICS_EXPORT_PROMETHEUS=false

# System Monitoring
MONITOR_CPU=true
MONITOR_MEMORY=true
MONITOR_DISK=true
MONITOR_NETWORK=true

# Alert Thresholds
CPU_ALERT_THRESHOLD=80
MEMORY_ALERT_THRESHOLD=85
DISK_ALERT_THRESHOLD=90

# ============================================
# LOGGING
# ============================================
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=./data/logs/app.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5
LOG_ROTATION=daily

# Log Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

# ============================================
# SUBSYSTEMS (z/OS SIMULATION)
# ============================================
SUBSYSTEM_JES_ENABLED=true
SUBSYSTEM_CICS_ENABLED=true
SUBSYSTEM_DB2_ENABLED=true
SUBSYSTEM_TSO_ENABLED=true

# JES Configuration
JES_MAX_JOBS=100
JES_SPOOL_SIZE=1024

# CICS Configuration
CICS_MAX_TRANSACTIONS=1000
CICS_TIMEOUT=30

# DB2 Configuration
DB2_MAX_CONNECTIONS=50
DB2_QUERY_TIMEOUT=60

# TSO Configuration
TSO_MAX_SESSIONS=20
TSO_SESSION_TIMEOUT=300

# ============================================
# BACKUP & RECOVERY
# ============================================
BACKUP_ENABLED=true
BACKUP_INTERVAL=daily
BACKUP_RETENTION_DAYS=30
BACKUP_LOCATION=./data/backups

# ============================================
# DEVELOPMENT
# ============================================
DEBUG=false
TESTING=false
PROFILING=false
```

## Backend Configuration

### config.py

Located at: `backend/config.py`

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./data/zenithone.db"
    
    # Security
    secret_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:latest"
    
    # Podman
    podman_socket: str = "unix:///run/user/1000/podman/podman.sock"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

## CLI Configuration

### ~/.zenithone/config.json

```json
{
  "api_url": "http://localhost:8000/api/v1",
  "timeout": 30000,
  "output_format": "table",
  "color_output": true,
  "auto_update": true,
  "log_level": "info",
  "log_file": "~/.zenithone/cli.log",
  "cache_enabled": true,
  "cache_ttl": 300,
  "default_workload_type": "batch",
  "default_priority": "normal",
  "confirm_destructive": true,
  "pagination_size": 20
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| api_url | string | http://localhost:8000/api/v1 | Backend API URL |
| timeout | number | 30000 | Request timeout (ms) |
| output_format | string | table | Output format (table, json, yaml) |
| color_output | boolean | true | Enable colored output |
| auto_update | boolean | true | Auto-update CLI |
| log_level | string | info | Log level (debug, info, warn, error) |
| cache_enabled | boolean | true | Enable response caching |
| cache_ttl | number | 300 | Cache TTL (seconds) |
| confirm_destructive | boolean | true | Confirm destructive operations |
| pagination_size | number | 20 | Items per page |

### CLI Commands

```bash
# View current configuration
zenith config show

# Set configuration value
zenith config set api_url http://production:8000/api/v1

# Reset to defaults
zenith config reset

# Export configuration
zenith config export > config-backup.json

# Import configuration
zenith config import config-backup.json
```

## UI Configuration

### ui/assets/js/config.js

```javascript
const CONFIG = {
    // API Configuration
    API_BASE_URL: 'http://localhost:8000/api/v1',
    API_TIMEOUT: 30000,
    
    // WebSocket Configuration
    WS_URL: 'ws://localhost:8000/ws',
    WS_RECONNECT_INTERVAL: 5000,
    WS_MAX_RECONNECT_ATTEMPTS: 10,
    
    // UI Settings
    THEME: 'dark',
    LANGUAGE: 'en',
    TIMEZONE: 'America/Chicago',
    DATE_FORMAT: 'YYYY-MM-DD HH:mm:ss',
    
    // Refresh Intervals (ms)
    DASHBOARD_REFRESH: 10000,
    WORKLOADS_REFRESH: 10000,
    CONTAINERS_REFRESH: 10000,
    METRICS_REFRESH: 30000,
    
    // Pagination
    DEFAULT_PAGE_SIZE: 20,
    PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
    
    // Charts
    CHART_ANIMATION: true,
    CHART_POINTS_LIMIT: 50,
    
    // Notifications
    NOTIFICATION_DURATION: 5000,
    NOTIFICATION_POSITION: 'top-right',
    
    // Session
    SESSION_TIMEOUT: 3600000, // 1 hour
    AUTO_LOGOUT: true
};
```

## Database Configuration

### SQLite (Default)

```bash
DATABASE_URL=sqlite:///./data/zenithone.db
```

**Advantages:**
- No setup required
- Portable
- Good for development

**Limitations:**
- Single connection
- Limited concurrency
- Not recommended for production

### PostgreSQL (Recommended for Production)

```bash
DATABASE_URL=postgresql://zenithone:password@localhost:5432/zenithone
```

**Setup:**

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE zenithone;
CREATE USER zenithone WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE zenithone TO zenithone;
\q

# Update backend/.env
DATABASE_URL=postgresql://zenithone:secure_password@localhost:5432/zenithone

# Install Python driver
pip install psycopg2-binary
```

### MySQL

```bash
DATABASE_URL=mysql://zenithone:password@localhost:3306/zenithone
```

**Setup:**

```bash
# Install MySQL
sudo apt install mysql-server

# Create database
sudo mysql
CREATE DATABASE zenithone;
CREATE USER 'zenithone'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON zenithone.* TO 'zenithone'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Install Python driver
pip install pymysql
```

## Security Configuration

### SSL/TLS Configuration

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Update backend configuration
uvicorn main:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

### Firewall Configuration

```bash
# Allow API port
sudo ufw allow 8000/tcp

# Allow UI port (if separate)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### Authentication Configuration

```bash
# JWT Configuration
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Policy
MIN_PASSWORD_LENGTH=12
REQUIRE_UPPERCASE=true
REQUIRE_LOWERCASE=true
REQUIRE_NUMBERS=true
REQUIRE_SPECIAL_CHARS=true

# Account Lockout
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
```

## Performance Tuning

### Backend Performance

```bash
# Worker Processes
API_WORKERS=4  # Set to number of CPU cores

# Connection Pooling
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# Caching
CACHE_ENABLED=true
CACHE_BACKEND=redis
CACHE_TTL=300
REDIS_URL=redis://localhost:6379/0
```

### Container Performance

```bash
# Resource Limits
DEFAULT_CPU_LIMIT=2.0
DEFAULT_MEMORY_LIMIT=2048
DEFAULT_DISK_LIMIT=10240

# Concurrency
MAX_CONCURRENT_WORKLOADS=20
MAX_CONCURRENT_CONTAINERS=50
```

### Database Performance

```bash
# PostgreSQL Tuning
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

## Logging Configuration

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

### Log Formats

**JSON Format:**
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "message": "Workload created",
  "workload_id": "abc123",
  "user": "admin"
}
```

**Text Format:**
```
2024-01-01 12:00:00 INFO Workload created workload_id=abc123 user=admin
```

### Log Rotation

```bash
LOG_ROTATION=daily
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5
```

## Advanced Configuration

### Custom Subsystem Configuration

Create `backend/config/subsystems.yaml`:

```yaml
jes:
  enabled: true
  max_jobs: 100
  spool_size: 1024
  priority_levels: [low, normal, high, critical]

cics:
  enabled: true
  max_transactions: 1000
  timeout: 30
  regions: [PROD, TEST, DEV]

db2:
  enabled: true
  max_connections: 50
  query_timeout: 60
  buffer_pool_size: 512

tso:
  enabled: true
  max_sessions: 20
  session_timeout: 300
  command_history: 100
```

### Monitoring Configuration

Create `backend/config/monitoring.yaml`:

```yaml
metrics:
  enabled: true
  interval: 60
  retention_days: 30
  
alerts:
  enabled: true
  channels: [email, slack]
  
  rules:
    - name: high_cpu
      condition: cpu > 80
      duration: 300
      severity: warning
      
    - name: critical_memory
      condition: memory > 90
      duration: 60
      severity: critical
```

## Environment-Specific Configurations

### Development

```bash
DEBUG=true
LOG_LEVEL=DEBUG
API_RELOAD=true
CORS_ORIGINS=["*"]
```

### Staging

```bash
DEBUG=false
LOG_LEVEL=INFO
API_RELOAD=false
CORS_ORIGINS=["https://staging.example.com"]
```

### Production

```bash
DEBUG=false
LOG_LEVEL=WARNING
API_RELOAD=false
API_WORKERS=8
CORS_ORIGINS=["https://example.com"]
RATE_LIMIT_ENABLED=true
BACKUP_ENABLED=true
```

## Configuration Validation

```bash
# Validate configuration
zenith admin config validate

# Test configuration
zenith admin config test

# Show effective configuration
zenith admin config show --effective
```

## Next Steps

- Review [INSTALLATION.md](INSTALLATION.md) for setup
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for issues
- See [API_REFERENCE.md](API_REFERENCE.md) for API details
