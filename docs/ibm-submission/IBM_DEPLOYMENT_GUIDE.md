# ZenithOne Explorer - Enterprise Deployment Guide

**Comprehensive Deployment Documentation for IBM LinuxONE Showcase**

---

## Document Information

- **Document Type**: Enterprise Deployment Guide
- **Version**: 1.0.0
- **Date**: January 15, 2024
- **Status**: Final
- **Classification**: Public
- **Author**: Paul Moore (paulmmoore3416@gmail.com)

---

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Infrastructure Requirements](#infrastructure-requirements)
3. [Deployment Architectures](#deployment-architectures)
4. [Installation Procedures](#installation-procedures)
5. [Configuration Management](#configuration-management)
6. [Security Hardening](#security-hardening)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Scaling Strategies](#scaling-strategies)

---

## 1. Deployment Overview

### 1.1 Deployment Models

ZenithOne Explorer supports multiple deployment models to meet different organizational needs:

#### Development Environment
- **Purpose**: Individual developer workstations
- **Scale**: Single node, minimal resources
- **Features**: Full functionality, development tools
- **Maintenance**: Self-managed

#### Testing/Staging Environment
- **Purpose**: Quality assurance and pre-production testing
- **Scale**: Single or multi-node
- **Features**: Production-like configuration
- **Maintenance**: Team-managed

#### Production Environment
- **Purpose**: Enterprise workload management
- **Scale**: Multi-node, high availability
- **Features**: Full security, monitoring, backup
- **Maintenance**: Operations team managed

#### Educational Environment
- **Purpose**: Training and learning
- **Scale**: Multiple single-node instances
- **Features**: Simplified configuration
- **Maintenance**: Instructor-managed

### 1.2 Deployment Phases

```
Phase 1: Infrastructure Preparation
    ↓
Phase 2: Base System Installation
    ↓
Phase 3: ZenithOne Installation
    ↓
Phase 4: Configuration & Security
    ↓
Phase 5: Testing & Validation
    ↓
Phase 6: Go-Live & Monitoring
```

---

## 2. Infrastructure Requirements

### 2.1 Hardware Specifications

#### Minimum Configuration (Development)
```
CPU: 4 cores (x86_64)
RAM: 8 GB
Storage: 50 GB SSD
Network: 1 Gbps
```

#### Recommended Configuration (Production)
```
CPU: 16+ cores (x86_64)
RAM: 32+ GB
Storage: 200+ GB NVMe SSD
Network: 10 Gbps
Redundancy: RAID 1/10 for storage
```

#### High Availability Configuration
```
Nodes: 3+ servers
Load Balancer: Hardware or software
Shared Storage: NFS/GlusterFS/Ceph
Database: PostgreSQL cluster
Backup: Automated daily backups
```

### 2.2 Operating System Requirements

#### Supported Distributions
- **Ubuntu 20.04 LTS** (Recommended)
- **Ubuntu 22.04 LTS** (Preferred for new deployments)
- **Red Hat Enterprise Linux 8+**
- **CentOS Stream 8+**
- **Debian 11+**
- **SUSE Linux Enterprise 15+**

#### System Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    curl \
    wget \
    git \
    build-essential \
    python3.14 \
    python3.14-venv \
    python3.14-dev \
    nodejs \
    npm \
    podman \
    postgresql-client

# Configure firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # ZenithOne API
sudo ufw enable
```

### 2.3 Network Architecture

#### Single Node Deployment
```
Internet → Firewall → Load Balancer → ZenithOne Server
                                           ↓
                                      Local Database
```

#### Multi-Node Deployment
```
Internet → Firewall → Load Balancer → [ZenithOne Nodes]
                                           ↓
                                   Shared Database Cluster
                                           ↓
                                     Shared Storage
```

#### Network Requirements
- **Bandwidth**: Minimum 100 Mbps, Recommended 1 Gbps+
- **Latency**: <10ms between nodes
- **Ports**: 22 (SSH), 80/443 (HTTP/HTTPS), 8000 (API), 5432 (PostgreSQL)
- **DNS**: Proper hostname resolution
- **NTP**: Time synchronization

---

## 3. Deployment Architectures

### 3.1 Single Node Architecture

**Use Cases**: Development, small teams, proof of concept

```
┌─────────────────────────────────────────┐
│            ZenithOne Server             │
├─────────────────────────────────────────┤
│  Web UI │ CLI │ REST API │ WebSocket    │
├─────────────────────────────────────────┤
│         FastAPI Backend                 │
├─────────────────────────────────────────┤
│  SQLite │ Ollama │ Podman │ Monitoring  │
└─────────────────────────────────────────┘
```

**Advantages**:
- Simple setup and maintenance
- Low resource requirements
- Quick deployment
- Ideal for learning and development

**Limitations**:
- Single point of failure
- Limited scalability
- No high availability

### 3.2 High Availability Architecture

**Use Cases**: Production environments, critical workloads

```
┌─────────────────────────────────────────────────────────┐
│                Load Balancer                            │
└─────────────────┬───────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐    ┌───▼───┐    ┌───▼───┐
│Node 1 │    │Node 2 │    │Node 3 │
│       │    │       │    │       │
│ZenOne │    │ZenOne │    │ZenOne │
└───┬───┘    └───┬───┘    └───┬───┘
    │             │             │
    └─────────────┼─────────────┘
                  │
        ┌─────────▼─────────┐
        │  PostgreSQL       │
        │  Cluster          │
        │  (Primary +       │
        │   Replicas)       │
        └───────────────────┘
```

**Components**:
- **Load Balancer**: HAProxy, NGINX, or cloud LB
- **Application Nodes**: 3+ ZenithOne instances
- **Database Cluster**: PostgreSQL with replication
- **Shared Storage**: For logs and data
- **Monitoring**: Centralized monitoring stack

### 3.3 Microservices Architecture (Future)

**Use Cases**: Large-scale deployments, cloud-native environments

```
┌─────────────────────────────────────────────────────────┐
│                 API Gateway                             │
└─────────────────┬───────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐    ┌───▼───┐    ┌───▼───┐
│Auth   │    │Workload│   │Monitor│
│Service│    │Service │   │Service│
└───────┘    └────────┘   └───────┘
    │             │             │
    └─────────────┼─────────────┘
                  │
        ┌─────────▼─────────┐
        │  Message Queue    │
        │  (Redis/RabbitMQ) │
        └───────────────────┘
```

---

## 4. Installation Procedures

### 4.1 Automated Installation

#### Production Installation Script
```bash
#!/bin/bash
# production-install.sh - Enterprise installation script

set -euo pipefail

# Configuration
ZENITHONE_USER="zenithone"
ZENITHONE_HOME="/opt/zenithone"
DATABASE_HOST="localhost"
DATABASE_NAME="zenithone_prod"

# Create system user
sudo useradd -r -s /bin/bash -d $ZENITHONE_HOME $ZENITHONE_USER

# Create directories
sudo mkdir -p $ZENITHONE_HOME/{app,data,logs,backups}
sudo chown -R $ZENITHONE_USER:$ZENITHONE_USER $ZENITHONE_HOME

# Install ZenithOne
cd $ZENITHONE_HOME
sudo -u $ZENITHONE_USER git clone https://github.com/paulmmoore3416/zenithone-explorer.git app

# Setup backend
cd $ZENITHONE_HOME/app/backend
sudo -u $ZENITHONE_USER python3.14 -m venv venv
sudo -u $ZENITHONE_USER ./venv/bin/pip install -r requirements.txt

# Setup CLI
cd $ZENITHONE_HOME/app/cli
sudo npm install -g .

# Configure database
sudo -u postgres createdb $DATABASE_NAME
sudo -u postgres createuser $ZENITHONE_USER
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE_NAME TO $ZENITHONE_USER;"

# Create configuration
cat > $ZENITHONE_HOME/app/backend/.env << EOF
DATABASE_URL=postgresql://$ZENITHONE_USER:password@$DATABASE_HOST/$DATABASE_NAME
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
LOG_LEVEL=INFO
EOF

# Set permissions
sudo chown $ZENITHONE_USER:$ZENITHONE_USER $ZENITHONE_HOME/app/backend/.env
sudo chmod 600 $ZENITHONE_HOME/app/backend/.env

# Install systemd service
sudo cp $ZENITHONE_HOME/app/systemd/zenithone.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable zenithone
sudo systemctl start zenithone

echo "ZenithOne installation completed successfully!"
```

### 4.2 Container-Based Deployment

#### Docker Compose Configuration
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  zenithone-backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://zenithone:password@db:5432/zenithone
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=zenithone
      - POSTGRES_USER=zenithone
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - zenithone-backend
    restart: unless-stopped

volumes:
  postgres_data:
```

### 4.3 Kubernetes Deployment

#### Kubernetes Manifests
```yaml
# zenithone-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zenithone-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: zenithone-backend
  template:
    metadata:
      labels:
        app: zenithone-backend
    spec:
      containers:
      - name: zenithone
        image: zenithone/backend:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: zenithone-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: zenithone-service
spec:
  selector:
    app: zenithone-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## 5. Configuration Management

### 5.1 Environment-Specific Configuration

#### Development Configuration
```bash
# development.env
DEBUG=true
LOG_LEVEL=DEBUG
API_RELOAD=true
DATABASE_URL=sqlite:///./data/zenithone_dev.db
CORS_ORIGINS=["*"]
RATE_LIMIT_ENABLED=false
```

#### Production Configuration
```bash
# production.env
DEBUG=false
LOG_LEVEL=WARNING
API_RELOAD=false
API_WORKERS=8
DATABASE_URL=postgresql://zenithone:password@db-cluster:5432/zenithone
CORS_ORIGINS=["https://zenithone.company.com"]
RATE_LIMIT_ENABLED=true
BACKUP_ENABLED=true
SSL_CERT_PATH=/etc/ssl/certs/zenithone.crt
SSL_KEY_PATH=/etc/ssl/private/zenithone.key
```

### 5.2 Configuration Templates

#### Ansible Playbook
```yaml
# zenithone-deploy.yml
---
- hosts: zenithone_servers
  become: yes
  vars:
    zenithone_version: "1.0.0"
    database_host: "{{ groups['database'][0] }}"
    
  tasks:
    - name: Create ZenithOne user
      user:
        name: zenithone
        system: yes
        shell: /bin/bash
        home: /opt/zenithone
        
    - name: Install dependencies
      apt:
        name:
          - python3.14
          - python3.14-venv
          - nodejs
          - npm
          - podman
        state: present
        
    - name: Deploy ZenithOne application
      git:
        repo: https://github.com/paulmmoore3416/zenithone-explorer.git
        dest: /opt/zenithone/app
        version: "{{ zenithone_version }}"
      become_user: zenithone
      
    - name: Configure environment
      template:
        src: production.env.j2
        dest: /opt/zenithone/app/backend/.env
        owner: zenithone
        group: zenithone
        mode: '0600'
```

---

## 6. Security Hardening

### 6.1 System Security

#### Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 10.0.0.0/8 to any port 22    # SSH from internal
sudo ufw allow 80/tcp                              # HTTP
sudo ufw allow 443/tcp                             # HTTPS
sudo ufw limit ssh                                 # Rate limit SSH
sudo ufw enable
```

#### SSL/TLS Configuration
```bash
# Generate SSL certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
  -keyout /etc/ssl/private/zenithone.key \
  -out /etc/ssl/certs/zenithone.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=zenithone.company.com"

# Set permissions
sudo chmod 600 /etc/ssl/private/zenithone.key
sudo chmod 644 /etc/ssl/certs/zenithone.crt
```

### 6.2 Application Security

#### Security Configuration
```bash
# Generate secure secrets
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Configure strong password policy
MIN_PASSWORD_LENGTH=12
REQUIRE_UPPERCASE=true
REQUIRE_LOWERCASE=true
REQUIRE_NUMBERS=true
REQUIRE_SPECIAL_CHARS=true

# Enable security features
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
SESSION_TIMEOUT=3600
```

### 6.3 Database Security

#### PostgreSQL Hardening
```sql
-- Create dedicated user
CREATE USER zenithone WITH PASSWORD 'secure_random_password';
CREATE DATABASE zenithone OWNER zenithone;

-- Grant minimal permissions
GRANT CONNECT ON DATABASE zenithone TO zenithone;
GRANT USAGE ON SCHEMA public TO zenithone;
GRANT CREATE ON SCHEMA public TO zenithone;

-- Configure connection limits
ALTER USER zenithone CONNECTION LIMIT 50;
```

---

## 7. Monitoring & Maintenance

### 7.1 Health Monitoring

#### Health Check Script
```bash
#!/bin/bash
# health-check.sh - System health monitoring

# Check API health
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$API_STATUS" != "200" ]; then
    echo "CRITICAL: API health check failed (HTTP $API_STATUS)"
    exit 2
fi

# Check database connectivity
DB_STATUS=$(zenith admin db status --quiet)
if [ $? -ne 0 ]; then
    echo "CRITICAL: Database connectivity failed"
    exit 2
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "WARNING: Disk usage is ${DISK_USAGE}%"
    exit 1
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ "$MEM_USAGE" -gt 90 ]; then
    echo "WARNING: Memory usage is ${MEM_USAGE}%"
    exit 1
fi

echo "OK: All health checks passed"
exit 0
```

### 7.2 Log Management

#### Logrotate Configuration
```bash
# /etc/logrotate.d/zenithone
/opt/zenithone/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 zenithone zenithone
    postrotate
        systemctl reload zenithone
    endscript
}
```

### 7.3 Backup Strategy

#### Automated Backup Script
```bash
#!/bin/bash
# backup.sh - Automated backup script

BACKUP_DIR="/opt/zenithone/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="zenithone_backup_$DATE.tar.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump zenithone > $BACKUP_DIR/database_$DATE.sql

# Backup application data
tar -czf $BACKUP_DIR/$BACKUP_FILE \
    /opt/zenithone/app/backend/data \
    /opt/zenithone/logs \
    $BACKUP_DIR/database_$DATE.sql

# Clean up old backups (keep 30 days)
find $BACKUP_DIR -name "zenithone_backup_*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "database_*.sql" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/$BACKUP_FILE"
```

---

## 8. Scaling Strategies

### 8.1 Vertical Scaling

#### Resource Optimization
```bash
# Increase worker processes
API_WORKERS=8

# Optimize database connections
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Increase memory limits
DEFAULT_MEMORY_LIMIT=2048
MAX_CONCURRENT_WORKLOADS=20
```

### 8.2 Horizontal Scaling

#### Load Balancer Configuration (HAProxy)
```
# /etc/haproxy/haproxy.cfg
global
    daemon
    maxconn 4096

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend zenithone_frontend
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/zenithone.pem
    redirect scheme https if !{ ssl_fc }
    default_backend zenithone_backend

backend zenithone_backend
    balance roundrobin
    option httpchk GET /health
    server node1 10.0.1.10:8000 check
    server node2 10.0.1.11:8000 check
    server node3 10.0.1.12:8000 check
```

### 8.3 Database Scaling

#### PostgreSQL Cluster Setup
```bash
# Primary node configuration
# postgresql.conf
wal_level = replica
max_wal_senders = 3
wal_keep_segments = 64
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/archive/%f'

# Replica node setup
pg_basebackup -h primary-server -D /var/lib/postgresql/data -U replication -v -P -W
```

---

## Appendix A: Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check service status
sudo systemctl status zenithone

# Check logs
sudo journalctl -u zenithone -f

# Check configuration
zenith admin config validate
```

#### Database Connection Issues
```bash
# Test database connectivity
psql -h localhost -U zenithone -d zenithone -c "SELECT 1;"

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

#### Performance Issues
```bash
# Check system resources
htop
iotop
nethogs

# Check application metrics
zenith metrics system
```

---

## Appendix B: Migration Guide

### Upgrading from Previous Versions

#### Version 0.9 to 1.0
```bash
# Backup current installation
./backup.sh

# Stop services
sudo systemctl stop zenithone

# Update code
cd /opt/zenithone/app
git pull origin main

# Update dependencies
cd backend
./venv/bin/pip install -r requirements.txt --upgrade

# Run migrations
./venv/bin/python -c "from database.migrations import run_migrations; run_migrations()"

# Start services
sudo systemctl start zenithone
```

---

*Document Version: 1.0*  
*Last Updated: January 15, 2024*  
*Classification: Public*
