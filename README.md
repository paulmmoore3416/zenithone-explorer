# ZenithOne Explorer

**Enterprise-Grade LinuxONE Showcase Platform with AI-Enhanced Workload Management**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 22+](https://img.shields.io/badge/node-22+-green.svg)](https://nodejs.org/)
[![Podman](https://img.shields.io/badge/podman-4.5+-purple.svg)](https://podman.io/)

> **Democratizing Enterprise Computing**: Bringing IBM LinuxONE capabilities to consumer hardware through AI-powered workload management, container orchestration, and z/OS subsystem simulation.

---
https://zenith-one.lovable.app

## 🌟 Overview

ZenithOne Explorer is an innovative platform that bridges traditional mainframe computing and modern cloud-native architectures. Built to showcase IBM LinuxONE principles on standard Linux systems, it provides developers, students, and enterprises with an accessible environment for learning, prototyping, and experimenting with enterprise-grade workload management.

### Key Highlights

- 🤖 **AI-Enhanced Scheduling**: Ollama-powered intelligent workload optimization
- 🐳 **Container Orchestration**: Podman-based workload execution
- 🖥️ **z/OS Simulation**: JES, CICS, DB2, and TSO subsystem emulators
- 📊 **Real-Time Monitoring**: Live metrics and performance tracking
- 🎯 **Multiple Interfaces**: Web UI, CLI, and REST API

---

## 🚀 Quick Start

### Prerequisites

- Ubuntu 20.04+ (or compatible Linux)
- 8GB+ RAM (16GB recommended)
- 20GB+ free disk space
- Internet connection

### Installation (5 Minutes)

```bash
# Clone the repository
git clone https://github.com/paulmmoore3416/zenithone-explorer.git
cd zenithone-explorer

# Run installation script
chmod +x scripts/install.sh
./scripts/install.sh

# Start the backend
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### First Workload

```bash
# Login
zenith auth login --username admin --password admin123

# Create and run your first workload
zenith workload create \
  --name hello-world \
  --type batch \
  --image alpine:latest \
  --command "echo 'Hello from ZenithOne!'"

zenith workload schedule <workload-id>
zenith workload logs <workload-id>
```

### Access the UI

Open your browser: **http://localhost:8000**

Default credentials: `admin` / `admin123`

---

## ✨ Features

### 🎯 Core Capabilities

#### AI-Powered Workload Management
- **Intelligent Scheduling**: AI analyzes system load and predicts optimal execution times
- **Resource Optimization**: Machine learning optimizes CPU, memory, and I/O allocation
- **Anomaly Detection**: Automatic identification of performance issues
- **Adaptive Learning**: Continuous improvement through historical data analysis

#### Container Orchestration
- **Multi-Type Workloads**: Batch, interactive, service, and scheduled execution
- **Resource Management**: CPU, memory, and I/O limits with enforcement
- **Lifecycle Control**: Complete container management (create, start, stop, pause, delete)
- **Volume Management**: Persistent storage and data sharing

#### z/OS Subsystem Simulation
- **JES (Job Entry Subsystem)**: Job submission, queuing, and management
- **CICS (Transaction Processing)**: Transaction control and monitoring
- **DB2 (Database Management)**: Database operations and connection pooling
- **TSO (Time Sharing Option)**: Interactive session management

#### Real-Time Monitoring
- **System Metrics**: CPU, memory, disk, and network monitoring
- **Workload Analytics**: Execution time, resource usage, success rates
- **Visual Dashboards**: Interactive charts and graphs
- **Alert System**: Threshold-based notifications

### 🖥️ User Interfaces

#### Web Dashboard
- Modern, responsive design
- Real-time updates via WebSocket
- Interactive charts (Chart.js)
- Comprehensive workload management
- System monitoring and metrics

#### Command-Line Interface
- 50+ commands for automation
- Multiple output formats (table, JSON, YAML)
- Shell completion (bash, zsh, fish)
- Scriptable and CI/CD-ready

#### REST API
- 30+ RESTful endpoints
- OpenAPI/Swagger documentation
- JWT authentication
- Rate limiting and security

---

## 📚 Documentation

### Getting Started
- **[Installation Guide](docs/INSTALLATION.md)** - Complete setup instructions
- **[Getting Started](docs/guides/GETTING_STARTED.md)** - Quick start tutorial
- **[First Workload](docs/guides/FIRST_WORKLOAD.md)** - Step-by-step walkthrough
- **[FAQ](docs/guides/FAQ.md)** - Frequently asked questions

### User Guides
- **[CLI Guide](docs/CLI_GUIDE.md)** - Command-line reference
- **[UI Guide](docs/UI_GUIDE.md)** - Web interface documentation
- **[API Reference](docs/API_REFERENCE.md)** - REST API documentation

### Technical Documentation
- **[Configuration](docs/CONFIGURATION.md)** - Configuration reference
- **[Architecture](docs/architecture/ARCHITECTURE.md)** - System architecture
- **[Database Schema](docs/architecture/DATABASE_SCHEMA.md)** - Data model
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Development
- **[Contributing](docs/CONTRIBUTING.md)** - Contribution guidelines
- **[Changelog](CHANGELOG.md)** - Version history

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ZenithOne Explorer                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐  │
│  │  Web UI  │  │   CLI    │  │    REST API Clients      │  │
│  └────┬─────┘  └────┬─────┘  └───────────┬──────────────┘  │
│       │             │                     │                  │
│       └─────────────┴─────────────────────┘                  │
│                     │                                         │
│       ┌─────────────▼─────────────────────────┐             │
│       │      FastAPI Backend (Python)         │             │
│       │  • Authentication & Security          │             │
│       │  • Workload Manager                   │             │
│       │  • Container Orchestrator             │             │
│       │  • Monitoring Service                 │             │
│       │  • Subsystem Simulators               │             │
│       └───────────┬───────────────────────────┘             │
│                   │                                           │
│       ┌───────────▼───────────┐  ┌──────────────────────┐   │
│       │  Database (SQLite)    │  │   Ollama AI Engine   │   │
│       └───────────────────────┘  └──────────────────────┘   │
│                                                               │
│       ┌──────────────────────────────────────────────────┐   │
│       │           Podman Container Runtime               │   │
│       └──────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | Python 3.14, FastAPI | REST API and business logic |
| **Database** | SQLite/PostgreSQL | Data persistence |
| **AI Engine** | Ollama (Qwen2.5) | Workload optimization |
| **Containers** | Podman 4.5+ | Workload execution |
| **CLI** | Node.js 22, Commander.js | Command-line interface |
| **UI** | HTML5, CSS3, JavaScript | Web dashboard |
| **Charts** | Chart.js | Data visualization |
| **Testing** | pytest, Jest | Quality assurance |

---

## 📊 Use Cases

### 🎓 Education & Training
- Learn mainframe concepts without expensive infrastructure
- Hands-on experience with enterprise workload management
- Practice container orchestration and AI optimization
- Understand z/OS subsystems and their interactions

### 💼 Enterprise Prototyping
- Test LinuxONE workloads before production deployment
- Validate resource requirements and performance
- Train operations teams on enterprise concepts
- Prototype migration strategies

### 🔬 Research & Development
- Experiment with AI-powered scheduling algorithms
- Study workload optimization techniques
- Collect performance data and metrics
- Test new orchestration strategies

### 👨‍💻 Software Development
- Develop and test containerized applications
- CI/CD pipeline integration
- Performance testing and benchmarking
- API integration development

---

## 🎯 Project Status

### Current Version: 1.0.0

**Completed Features:**
- ✅ Complete backend with 30+ API endpoints
- ✅ CLI with 50+ commands
- ✅ Web UI with real-time monitoring
- ✅ AI-powered workload scheduling
- ✅ Container orchestration
- ✅ z/OS subsystem simulators
- ✅ Comprehensive testing suite
- ✅ Complete documentation

**Roadmap:**
- 🔄 Multi-node cluster support (v1.5)
- 🔄 Enhanced AI capabilities (v1.5)
- 🔄 IBM Cloud integration (v2.0)
- 🔄 Mobile app (v2.0)

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Ways to Contribute
- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit pull requests
- ⭐ Star the repository

---

## 📈 Performance

### Benchmarks (Alienware Area 51 R5)
- **API Response Time**: <50ms average
- **Container Startup**: <2 seconds
- **Concurrent Workloads**: 10+ simultaneous
- **AI Scheduling**: <500ms decision time
- **Memory Footprint**: ~500MB base system

### Scalability
- Supports 50+ active containers
- Handles 1000+ API requests/second
- Manages 100+ WebSocket connections
- Processes 100+ concurrent operations

---

## 🔒 Security

- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Rate limiting
- SSL/TLS support

See [Security Documentation](docs/architecture/ARCHITECTURE.md#security) for details.

---

## 📦 System Requirements

### Minimum
- 4-core CPU (x86_64)
- 8GB RAM
- 20GB storage
- Ubuntu 20.04+

### Recommended
- 8+ core CPU
- 16GB+ RAM
- 50GB+ SSD storage
- Ubuntu 22.04 LTS

### Tested Hardware
- **Alienware Area 51 R5**
- Intel i7-7820X (8C/16T)
- 22GB RAM
- 1.5TB Storage

---

## 🌐 Community & Support

### Get Help
- 📖 [Documentation](docs/)
- 💬 [GitHub Discussions](https://github.com/paulmmoore3416/zenithone-explorer/discussions)
- 🐛 [Issue Tracker](https://github.com/paulmmoore3416/zenithone-explorer/issues)
- 📧 Email: paulmmoore3416@gmail.com

### Stay Updated
- ⭐ Star the repository
- 👀 Watch for updates
- 🔔 Enable notifications

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

### Development Team
- **Paul Moore** - Project Lead & Full Stack Development
- **IBM Bob AI** - AI-assisted development and documentation
- **Gemini CLI AI** - Collaborative development support

### Inspiration
- IBM LinuxONE team for enterprise computing excellence
- Open source community for tools and libraries
- Beta testers and early adopters

### Technology Partners
- FastAPI for the excellent web framework
- Ollama for local AI capabilities
- Podman for container orchestration
- Chart.js for data visualization

---

## 🎉 Quick Links

- **Repository**: https://github.com/paulmmoore3416/zenithone-explorer
- **Documentation**: [docs/](docs/)
- **Issues**: https://github.com/paulmmoore3416/zenithone-explorer/issues
- **Discussions**: https://github.com/paulmmoore3416/zenithone-explorer/discussions

---

## 📞 Contact

**Paul Moore**  
📧 paulmmoore3416@gmail.com  
🐙 [@paulmmoore3416](https://github.com/paulmmoore3416)

---

<div align="center">

**ZenithOne Explorer: Making Enterprise Computing Accessible to Everyone**

Made with ❤️ by Paul Moore | Powered by AI | Inspired by IBM LinuxONE

[Get Started](docs/guides/GETTING_STARTED.md) • [Documentation](docs/) • [Contribute](docs/CONTRIBUTING.md)

</div>
