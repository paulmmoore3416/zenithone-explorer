# ZenithOne Explorer - CLI Guide

Complete command-line interface reference for ZenithOne Explorer.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Authentication](#authentication)
- [Workload Commands](#workload-commands)
- [Container Commands](#container-commands)
- [Subsystem Commands](#subsystem-commands)
- [Metrics Commands](#metrics-commands)
- [Admin Commands](#admin-commands)
- [Global Options](#global-options)
- [Examples](#examples)

## Installation

```bash
# Install from source
cd cli
npm install
npm link

# Verify installation
zenith --version
```

## Configuration

### Initial Setup

```bash
# Configure API endpoint
zenith config set api_url http://localhost:8000/api/v1

# View configuration
zenith config show

# Reset to defaults
zenith config reset
```

### Configuration File

Location: `~/.zenithone/config.json`

```json
{
  "api_url": "http://localhost:8000/api/v1",
  "timeout": 30000,
  "output_format": "table"
}
```

## Authentication

### Login

```bash
# Interactive login
zenith auth login

# With credentials
zenith auth login --username admin --password admin123

# Save credentials
zenith auth login --username admin --password admin123 --save
```

### Register

```bash
# Interactive registration
zenith auth register

# With details
zenith auth register \
  --username newuser \
  --email user@example.com \
  --password SecurePass123!
```

### Logout

```bash
zenith auth logout
```

### Check Status

```bash
# View authentication status
zenith auth status

# View current user
zenith auth whoami
```

## Workload Commands

### Create Workload

```bash
# Basic workload
zenith workload create \
  --name my-workload \
  --type batch \
  --image python:3.14 \
  --command "python script.py"

# With resource limits
zenith workload create \
  --name data-processing \
  --type batch \
  --image python:3.14 \
  --command "python process.py" \
  --cpu 2.0 \
  --memory 1024 \
  --priority high

# With environment variables
zenith workload create \
  --name web-service \
  --type service \
  --image nginx:latest \
  --env PORT=8080 \
  --env ENV=production

# From file
zenith workload create --file workload.json
```

**workload.json:**
```json
{
  "name": "batch-job",
  "type": "batch",
  "image": "python:3.14",
  "command": "python script.py",
  "priority": "normal",
  "cpu_limit": 2.0,
  "memory_limit": 1024
}
```

### List Workloads

```bash
# List all workloads
zenith workload list

# Filter by status
zenith workload list --status running
zenith workload list --status pending

# Filter by type
zenith workload list --type batch

# Filter by priority
zenith workload list --priority high

# JSON output
zenith workload list --output json

# With pagination
zenith workload list --limit 50 --offset 0
```

### Get Workload Details

```bash
# View workload details
zenith workload get <workload-id>

# JSON output
zenith workload get <workload-id> --output json

# Watch status (auto-refresh)
zenith workload get <workload-id> --watch
```

### Update Workload

```bash
# Update priority
zenith workload update <workload-id> --priority critical

# Update resource limits
zenith workload update <workload-id> --cpu 4.0 --memory 2048
```

### Schedule Workload

```bash
# Schedule immediately
zenith workload schedule <workload-id>

# Schedule with AI optimization
zenith workload schedule <workload-id> --use-ai

# Schedule for specific time
zenith workload schedule <workload-id> --at "2024-01-01 14:00:00"
```

### Cancel Workload

```bash
# Cancel workload
zenith workload cancel <workload-id>

# Force cancel
zenith workload cancel <workload-id> --force
```

### Delete Workload

```bash
# Delete workload
zenith workload delete <workload-id>

# Delete without confirmation
zenith workload delete <workload-id> --yes
```

### View Workload Logs

```bash
# View logs
zenith workload logs <workload-id>

# Tail logs (last 100 lines)
zenith workload logs <workload-id> --tail 100

# Follow logs (stream)
zenith workload logs <workload-id> --follow

# Save logs to file
zenith workload logs <workload-id> > workload.log
```

## Container Commands

### List Containers

```bash
# List all containers
zenith container list

# List running containers only
zenith container list --status running

# Include stopped containers
zenith container list --all

# JSON output
zenith container list --output json
```

### Get Container Details

```bash
# View container details
zenith container get <container-id>

# Inspect container (full details)
zenith container inspect <container-id>
```

### Start Container

```bash
zenith container start <container-id>
```

### Stop Container

```bash
# Stop container (graceful)
zenith container stop <container-id>

# Stop with timeout
zenith container stop <container-id> --timeout 30

# Force stop
zenith container stop <container-id> --force
```

### Restart Container

```bash
zenith container restart <container-id>
```

### Pause Container

```bash
zenith container pause <container-id>
```

### Unpause Container

```bash
zenith container unpause <container-id>
```

### Delete Container

```bash
# Delete stopped container
zenith container delete <container-id>

# Force delete running container
zenith container delete <container-id> --force
```

### View Container Logs

```bash
# View logs
zenith container logs <container-id>

# Tail logs
zenith container logs <container-id> --tail 100

# Follow logs
zenith container logs <container-id> --follow

# With timestamps
zenith container logs <container-id> --timestamps
```

### View Container Stats

```bash
# View resource usage
zenith container stats <container-id>

# Continuous monitoring
zenith container stats <container-id> --watch

# All containers
zenith container stats --all
```

### Execute Command in Container

```bash
# Execute command
zenith container exec <container-id> -- echo "Hello"

# Interactive shell
zenith container exec <container-id> --interactive --tty -- /bin/bash

# As specific user
zenith container exec <container-id> --user root -- ls -la
```

## Subsystem Commands

### List Subsystems

```bash
# List all subsystems
zenith subsystem list

# JSON output
zenith subsystem list --output json
```

### Get Subsystem Status

```bash
# View subsystem status
zenith subsystem status --name jes
zenith subsystem status --name cics
zenith subsystem status --name db2
zenith subsystem status --name tso

# Watch status (auto-refresh)
zenith subsystem status --name jes --watch
```

### Start Subsystem

```bash
zenith subsystem start --name jes
```

### Stop Subsystem

```bash
zenith subsystem stop --name jes
```

### Restart Subsystem

```bash
zenith subsystem restart --name jes
```

### View Subsystem Logs

```bash
# View logs
zenith subsystem logs --name jes

# Tail logs
zenith subsystem logs --name jes --tail 100

# Follow logs
zenith subsystem logs --name jes --follow
```

## Metrics Commands

### System Metrics

```bash
# View system metrics
zenith metrics system

# Specific time range
zenith metrics system --range 1h
zenith metrics system --range 24h
zenith metrics system --range 7d

# JSON output
zenith metrics system --output json

# Watch metrics (auto-refresh)
zenith metrics system --watch
```

### Workload Metrics

```bash
# View workload metrics
zenith metrics workload <workload-id>

# Historical metrics
zenith metrics workload <workload-id> --range 24h
```

### Container Metrics

```bash
# View container metrics
zenith metrics container <container-id>

# Real-time monitoring
zenith metrics container <container-id> --watch
```

### Export Metrics

```bash
# Export to CSV
zenith metrics export --format csv --output metrics.csv

# Export to JSON
zenith metrics export --format json --output metrics.json

# Specific time range
zenith metrics export --range 7d --output weekly-metrics.csv
```

## Admin Commands

### User Management

```bash
# List users
zenith admin user list

# Create user
zenith admin user create \
  --username newuser \
  --email user@example.com \
  --password SecurePass123! \
  --role user

# Update user
zenith admin user update <user-id> --role admin
zenith admin user update <user-id> --active false

# Delete user
zenith admin user delete <user-id>

# Reset password
zenith admin user reset-password <user-id>
```

### System Information

```bash
# View system info
zenith admin system info

# View version
zenith admin system version

# Health check
zenith admin system health
```

### Configuration Management

```bash
# View configuration
zenith admin config show

# Update configuration
zenith admin config set max_workloads 20

# Validate configuration
zenith admin config validate

# Reload configuration
zenith admin config reload
```

### Database Management

```bash
# Database status
zenith admin db status

# Backup database
zenith admin db backup --output backup.db

# Restore database
zenith admin db restore --file backup.db

# Migrate database
zenith admin db migrate
```

### Logs Management

```bash
# View application logs
zenith admin logs view

# Tail logs
zenith admin logs tail --lines 100

# Clear logs
zenith admin logs clear

# Export logs
zenith admin logs export --output app-logs.txt
```

## Global Options

Available for all commands:

```bash
# Output format
--output, -o <format>    # table, json, yaml (default: table)

# Verbosity
--verbose, -v            # Verbose output
--quiet, -q              # Quiet mode (errors only)

# Help
--help, -h               # Show help

# Version
--version, -V            # Show version

# Configuration
--config <file>          # Use custom config file

# API endpoint
--api-url <url>          # Override API URL

# Timeout
--timeout <seconds>      # Request timeout (default: 30)

# No color
--no-color               # Disable colored output
```

## Examples

### Complete Workflow

```bash
# 1. Login
zenith auth login --username admin --password admin123

# 2. Create workload
zenith workload create \
  --name data-analysis \
  --type batch \
  --image python:3.14 \
  --command "python analyze.py" \
  --cpu 4.0 \
  --memory 2048 \
  --priority high

# 3. Schedule workload
zenith workload schedule <workload-id> --use-ai

# 4. Monitor progress
zenith workload get <workload-id> --watch

# 5. View logs
zenith workload logs <workload-id> --follow

# 6. Check system metrics
zenith metrics system --watch
```

### Batch Operations

```bash
# Create multiple workloads from files
for file in workloads/*.json; do
  zenith workload create --file "$file"
done

# Stop all running containers
zenith container list --status running --output json | \
  jq -r '.[].id' | \
  xargs -I {} zenith container stop {}

# Export all workload logs
zenith workload list --output json | \
  jq -r '.[].id' | \
  xargs -I {} sh -c 'zenith workload logs {} > logs/{}.log'
```

### Monitoring Script

```bash
#!/bin/bash
# monitor.sh - Monitor system and workloads

while true; do
  clear
  echo "=== System Metrics ==="
  zenith metrics system
  
  echo ""
  echo "=== Active Workloads ==="
  zenith workload list --status running
  
  echo ""
  echo "=== Container Stats ==="
  zenith container stats --all
  
  sleep 10
done
```

### Automated Deployment

```bash
#!/bin/bash
# deploy.sh - Deploy workload with monitoring

# Create workload
WORKLOAD_ID=$(zenith workload create \
  --name production-job \
  --type batch \
  --image myapp:latest \
  --command "npm start" \
  --output json | jq -r '.id')

echo "Created workload: $WORKLOAD_ID"

# Schedule workload
zenith workload schedule $WORKLOAD_ID --use-ai

# Wait for completion
while true; do
  STATUS=$(zenith workload get $WORKLOAD_ID --output json | jq -r '.status')
  echo "Status: $STATUS"
  
  if [ "$STATUS" = "completed" ]; then
    echo "Workload completed successfully"
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "Workload failed"
    zenith workload logs $WORKLOAD_ID
    exit 1
  fi
  
  sleep 5
done
```

## Shell Completion

### Bash

```bash
# Add to ~/.bashrc
eval "$(zenith completion bash)"
```

### Zsh

```bash
# Add to ~/.zshrc
eval "$(zenith completion zsh)"
```

### Fish

```bash
# Add to ~/.config/fish/config.fish
zenith completion fish | source
```

## Troubleshooting

### Connection Issues

```bash
# Test connection
zenith admin system health

# Check configuration
zenith config show

# Update API URL
zenith config set api_url http://localhost:8000/api/v1
```

### Authentication Issues

```bash
# Check auth status
zenith auth status

# Re-login
zenith auth logout
zenith auth login
```

### Command Not Found

```bash
# Reinstall CLI
cd cli
npm link

# Check PATH
echo $PATH

# Add to PATH
export PATH="$PATH:~/.npm-global/bin"
```

## Next Steps

- Review [API_REFERENCE.md](API_REFERENCE.md) for API details
- Check [UI_GUIDE.md](UI_GUIDE.md) for web interface
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
