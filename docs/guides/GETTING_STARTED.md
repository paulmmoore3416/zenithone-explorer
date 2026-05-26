# Getting Started with ZenithOne Explorer

Welcome to ZenithOne Explorer! This guide will help you get started with your first workload in just a few minutes.

## What is ZenithOne Explorer?

ZenithOne Explorer is an enterprise-grade platform that brings IBM LinuxONE capabilities to consumer hardware. It provides:

- **AI-Enhanced Workload Management**: Intelligent scheduling using Ollama AI
- **Container Orchestration**: Podman-based container management
- **z/OS Subsystem Simulation**: JES, CICS, DB2, and TSO simulators
- **Real-Time Monitoring**: Live metrics and performance tracking
- **Multiple Interfaces**: Web UI, CLI, and REST API

## Prerequisites

Before you begin, ensure you have:

- Ubuntu 20.04+ (or compatible Linux distribution)
- 8GB+ RAM (16GB recommended)
- 20GB+ free disk space
- Internet connection
- Basic command-line knowledge

## Quick Start (5 Minutes)

### Step 1: Install ZenithOne

```bash
# Clone the repository
git clone https://github.com/paulmmoore3416/zenithone-explorer.git
cd zenithone-explorer

# Run the installation script
chmod +x scripts/install.sh
./scripts/install.sh
```

The installer will:
1. Check system requirements
2. Install dependencies (Python, Podman, Ollama)
3. Set up the backend
4. Install the CLI
5. Configure the system

**Time:** ~3-5 minutes

### Step 2: Start the Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!**

### Step 3: Login

Open a new terminal:

```bash
# Login with default credentials
zenith auth login --username admin --password admin123
```

You should see:
```
✓ Login successful
✓ Token saved
```

### Step 4: Create Your First Workload

```bash
# Create a simple "Hello World" workload
zenith workload create \
  --name hello-world \
  --type batch \
  --image alpine:latest \
  --command "echo 'Hello from ZenithOne!'"
```

You should see:
```
✓ Workload created successfully
ID: wl_abc123
Name: hello-world
Status: pending
```

### Step 5: Schedule and Monitor

```bash
# Schedule the workload
zenith workload schedule wl_abc123

# Watch it run
zenith workload get wl_abc123 --watch

# View the logs
zenith workload logs wl_abc123
```

**Congratulations!** 🎉 You've just run your first workload on ZenithOne Explorer!

## Understanding the Basics

### Workload Types

ZenithOne supports four workload types:

1. **Batch**: One-time execution jobs
   - Example: Data processing, backups, reports
   - Runs to completion and stops

2. **Interactive**: User-interactive workloads
   - Example: Development environments, debugging
   - Requires user input/interaction

3. **Service**: Long-running services
   - Example: Web servers, APIs, databases
   - Runs continuously until stopped

4. **Scheduled**: Time-based execution
   - Example: Cron jobs, periodic tasks
   - Runs at specified times/intervals

### Workload Lifecycle

```
Created → Pending → Scheduled → Running → Completed
                                    ↓
                                 Failed
                                    ↓
                               Cancelled
```

### Priority Levels

- **Critical**: Highest priority, immediate execution
- **High**: Important workloads, scheduled soon
- **Normal**: Standard priority (default)
- **Low**: Background tasks, scheduled when resources available

## Common Tasks

### View All Workloads

```bash
zenith workload list
```

### Filter Workloads

```bash
# By status
zenith workload list --status running

# By type
zenith workload list --type batch

# By priority
zenith workload list --priority high
```

### Check System Status

```bash
# System metrics
zenith metrics system

# Container status
zenith container list

# Subsystem status
zenith subsystem list
```

### Using the Web UI

1. Open browser: `http://localhost:8000`
2. Login with: `admin` / `admin123`
3. Explore the dashboard
4. Create workloads via the UI
5. Monitor in real-time

## Example Workloads

### Python Script

```bash
zenith workload create \
  --name python-script \
  --type batch \
  --image python:3.14 \
  --command "python -c 'print(\"Hello from Python!\")'"
```

### Node.js Application

```bash
zenith workload create \
  --name node-app \
  --type service \
  --image node:22 \
  --command "node server.js" \
  --cpu 2.0 \
  --memory 1024
```

### Data Processing

```bash
zenith workload create \
  --name data-processor \
  --type batch \
  --image python:3.14 \
  --command "python process_data.py" \
  --priority high \
  --cpu 4.0 \
  --memory 2048
```

### Web Server

```bash
zenith workload create \
  --name web-server \
  --type service \
  --image nginx:latest \
  --env PORT=8080
```

## Using AI Scheduling

ZenithOne includes AI-powered workload scheduling:

```bash
# Create workload
zenith workload create \
  --name ai-optimized \
  --type batch \
  --image python:3.14 \
  --command "python analyze.py"

# Schedule with AI optimization
zenith workload schedule wl_abc123 --use-ai
```

The AI will:
- Analyze current system load
- Predict resource availability
- Determine optimal execution time
- Provide reasoning for the decision

## Exploring Subsystems

ZenithOne simulates z/OS subsystems:

### JES (Job Entry Subsystem)

```bash
# Check JES status
zenith subsystem status --name jes

# View JES logs
zenith subsystem logs --name jes
```

### CICS (Transaction Processing)

```bash
# Check CICS status
zenith subsystem status --name cics

# Start CICS
zenith subsystem start --name cics
```

### DB2 (Database)

```bash
# Check DB2 status
zenith subsystem status --name db2
```

### TSO (Time Sharing)

```bash
# Check TSO status
zenith subsystem status --name tso
```

## Tips for Beginners

### 1. Start Small
Begin with simple workloads (like `alpine:latest` with basic commands) before moving to complex applications.

### 2. Monitor Resources
Keep an eye on system resources:
```bash
zenith metrics system --watch
```

### 3. Use the UI
The web interface is great for learning and visualization:
- Real-time monitoring
- Visual feedback
- Easy navigation

### 4. Check Logs
When something goes wrong, check the logs:
```bash
zenith workload logs <workload-id>
zenith container logs <container-id>
```

### 5. Use Help
Every command has built-in help:
```bash
zenith --help
zenith workload --help
zenith workload create --help
```

### 6. Save Configurations
Save workload configurations for reuse:
```bash
# Export workload
zenith workload get wl_abc123 --output json > my-workload.json

# Create from file
zenith workload create --file my-workload.json
```

## Troubleshooting

### Backend Won't Start

```bash
# Check if port is in use
sudo lsof -i :8000

# Try different port
uvicorn main:app --port 8001
```

### CLI Not Found

```bash
# Reinstall CLI
cd cli
npm link

# Verify installation
which zenith
```

### Container Won't Start

```bash
# Check Podman
podman ps

# Check logs
zenith container logs <container-id>
```

### Authentication Failed

```bash
# Re-login
zenith auth logout
zenith auth login
```

## Next Steps

Now that you're familiar with the basics:

1. **Read the Full Documentation**
   - [CLI Guide](../CLI_GUIDE.md) - Complete CLI reference
   - [UI Guide](../UI_GUIDE.md) - Web interface guide
   - [API Reference](../API_REFERENCE.md) - REST API documentation

2. **Try Advanced Features**
   - [First Workload Tutorial](FIRST_WORKLOAD.md) - Detailed walkthrough
   - [Configuration Guide](../CONFIGURATION.md) - Advanced settings

3. **Explore Examples**
   - Check the `examples/` directory
   - Try different workload types
   - Experiment with AI scheduling

4. **Join the Community**
   - GitHub Discussions
   - Report issues
   - Contribute improvements

## Getting Help

If you need help:

1. **Check Documentation**: Most questions are answered in the docs
2. **Search Issues**: Someone may have had the same problem
3. **Ask Questions**: Create a GitHub Discussion
4. **Report Bugs**: Open a GitHub Issue
5. **Contact Support**: paulmmoore3416@gmail.com

## Useful Commands Reference

```bash
# Authentication
zenith auth login
zenith auth logout
zenith auth status

# Workloads
zenith workload create --name <name> --type <type> --image <image>
zenith workload list
zenith workload get <id>
zenith workload schedule <id>
zenith workload cancel <id>
zenith workload logs <id>

# Containers
zenith container list
zenith container start <id>
zenith container stop <id>
zenith container logs <id>

# Metrics
zenith metrics system
zenith metrics workload <id>

# Subsystems
zenith subsystem list
zenith subsystem status --name <name>

# Admin
zenith admin system info
zenith admin user list
```

## What's Next?

Continue your journey with:
- [First Workload Tutorial](FIRST_WORKLOAD.md) - Step-by-step workload creation
- [FAQ](FAQ.md) - Frequently asked questions
- [Configuration Guide](../CONFIGURATION.md) - Customize your setup

Welcome to ZenithOne Explorer! 🚀
