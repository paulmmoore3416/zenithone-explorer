# ZenithOne Explorer CLI

Enterprise-grade command-line interface for managing LinuxONE workloads, containers, and z/OS subsystems.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start

### Installation

```bash
# Install from source
cd cli
pip install -e .

# Or install directly
pip install zenithone-cli
```

### First Steps

```bash
# Login to ZenithOne Explorer
zenith login

# View help
zenith --help

# Check system status
zenith metrics system
```

## 📚 Commands Overview

### Authentication

```bash
# Login
zenith login [username]

# Logout
zenith logout

# Show current user
zenith whoami
```

### Workload Management

```bash
# List workloads
zenith workload list [--status STATUS] [--limit N]

# Get workload details
zenith workload get <workload_id>

# Create workload
zenith workload create --name NAME --type TYPE --image IMAGE [OPTIONS]

# Schedule workload
zenith workload schedule <workload_id>

# View workload logs
zenith workload logs <workload_id> [--tail N]

# Delete workload
zenith workload delete <workload_id> [--force]
```

### Container Operations

```bash
# List containers
zenith container list [--status STATUS]

# Get container details
zenith container get <container_id>

# Start/Stop/Restart container
zenith container start <container_id>
zenith container stop <container_id>
zenith container restart <container_id>

# View container logs
zenith container logs <container_id> [--tail N]

# Container statistics
zenith container stats [container_id]

# Delete container
zenith container delete <container_id> [--force]
```

### z/OS Subsystems

#### JES (Job Entry Subsystem)

```bash
# Submit JCL job
zenith subsystem jes submit <jcl_file> [--priority PRIORITY]

# Get job status
zenith subsystem jes job <job_id>

# List jobs
zenith subsystem jes list [--status STATUS]

# JES status
zenith subsystem jes status
```

#### CICS (Customer Information Control System)

```bash
# Process transaction
zenith subsystem cics transaction <program> [--data JSON] [--file FILE]

# List transactions
zenith subsystem cics list

# CICS status
zenith subsystem cics status
```

#### DB2 Database

```bash
# Execute SQL query
zenith subsystem db2 query "SELECT * FROM table"
zenith subsystem db2 query --file query.sql

# List tables
zenith subsystem db2 tables

# DB2 status
zenith subsystem db2 status
```

#### TSO (Time Sharing Option)

```bash
# Execute TSO command
zenith subsystem tso exec "LISTCAT LEVEL(SYS1)"

# TSO status
zenith subsystem tso status
```

### Performance Metrics

```bash
# System metrics
zenith metrics system

# Workload metrics
zenith metrics workload [workload_id]

# Container metrics
zenith metrics container [container_id]

# Performance summary
zenith metrics summary
```

### Administration (Admin Only)

```bash
# User management
zenith admin users list
zenith admin users get <user_id>
zenith admin users create --username USER --email EMAIL --password PASS
zenith admin users update <user_id> [OPTIONS]
zenith admin users delete <user_id> [--force]

# Role management
zenith admin roles list

# System management
zenith admin system info
zenith admin system health
zenith admin system config
```

## 🎨 Output Formats

The CLI supports multiple output formats:

```bash
# Table format (default)
zenith workload list

# JSON format
zenith workload list --format json

# YAML format
zenith workload list --format yaml

# Disable colors
zenith workload list --no-color
```

## ⚙️ Configuration

### Configuration File

The CLI stores configuration in `~/.zenithone/config.json`:

```json
{
  "api_url": "http://localhost:8000",
  "api_version": "v1",
  "timeout": 30,
  "verify_ssl": true,
  "output_format": "table",
  "color_output": true
}
```

### Custom Configuration

```bash
# Use custom config file
zenith --config /path/to/config.json workload list

# Set API URL
zenith --config custom.json login
```

## 📖 Examples

### Create and Schedule a Workload

```bash
# Create workload from command line
zenith workload create \
  --name "data-processing" \
  --type batch \
  --image "python:3.14" \
  --command "python" \
  --args "process.py" \
  --env "ENV=production" \
  --cpu 2 \
  --memory 1024 \
  --priority high

# Schedule for execution
zenith workload schedule <workload_id>

# Monitor logs
zenith workload logs <workload_id> --tail 100
```

### Create Workload from File

```bash
# workload.json
{
  "name": "web-service",
  "type": "service",
  "image": "nginx:latest",
  "priority": "normal",
  "cpu_limit": 1,
  "memory_limit": 512,
  "environment": {
    "PORT": "8080"
  }
}

# Create from file
zenith workload create --file workload.json
```

### Submit JCL Job

```bash
# job.jcl
//MYJOB    JOB (ACCT),'SAMPLE JOB',CLASS=A,MSGCLASS=X
//STEP1    EXEC PGM=IEFBR14
//

# Submit job
zenith subsystem jes submit job.jcl --priority HIGH

# Check status
zenith subsystem jes job JOB00123
```

### Execute DB2 Query

```bash
# Simple query
zenith subsystem db2 query "SELECT * FROM CUSTOMERS WHERE REGION='US'"

# Query from file
zenith subsystem db2 query --file complex_query.sql
```

### Monitor System Performance

```bash
# View system metrics
zenith metrics system

# View all workload metrics
zenith metrics workload

# View specific workload metrics
zenith metrics workload wl-12345

# Performance summary
zenith metrics summary
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/paulmmoore3416/zenithone-explorer.git
cd zenithone-explorer/cli

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black .

# Linting
flake8
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cli --cov-report=html

# Run specific test file
pytest tests/unit/test_auth.py
```

## 🐛 Troubleshooting

### Connection Issues

```bash
# Check API connectivity
curl http://localhost:8000/api/v1/health

# Verify configuration
cat ~/.zenithone/config.json

# Enable debug mode
zenith --debug workload list
```

### Authentication Issues

```bash
# Clear stored token
rm ~/.zenithone/config.json

# Login again
zenith login

# Verify authentication
zenith whoami
```

### Common Errors

**Error: "Not authenticated"**
```bash
# Solution: Login first
zenith login
```

**Error: "Connection refused"**
```bash
# Solution: Ensure backend is running
# Check backend status or start it
cd ../backend
python -m backend.main
```

**Error: "Invalid token"**
```bash
# Solution: Refresh authentication
zenith logout
zenith login
```

## 📝 Environment Variables

```bash
# Override API URL
export ZENITH_API_URL=http://custom-host:8000

# Override config file location
export ZENITH_CONFIG_FILE=/path/to/config.json

# Disable SSL verification (development only)
export ZENITH_VERIFY_SSL=false
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](../CONTRIBUTING.md).

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- IBM for LinuxONE technology
- FastAPI for the excellent backend framework
- The open-source community

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/paulmmoore3416/zenithone-explorer/issues)
- **Email**: paulmmoore3416@gmail.com
- **Documentation**: [Full Documentation](https://github.com/paulmmoore3416/zenithone-explorer/tree/main/docs)

---

**Built with ❤️ by AI for the future of enterprise computing**
