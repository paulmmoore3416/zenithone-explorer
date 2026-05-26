# ZenithOne Explorer - Project Structure

## Directory Layout

```
linuxonetproj/
├── README.md                          # Project overview and quick start
├── MASTER_PLAN.md                     # Complete project plan (this document)
├── PROJECT_STRUCTURE.md               # Directory structure reference
├── PROGRESS.md                        # Daily progress tracking
├── ISSUES.md                          # Issue tracking and resolution
├── CHANGELOG.md                       # Version history
├── LICENSE                            # MIT License
├── .gitignore                         # Git ignore patterns
├── .env.example                       # Environment configuration template
│
├── assets/                            # Branding and visual assets
│   ├── logo/                          # Project logo variations
│   │   ├── zenitone-logo.svg
│   │   ├── zenitone-logo.png
│   │   └── zenitone-icon.png
│   ├── screenshots/                   # UI screenshots for documentation
│   └── diagrams/                      # Architecture diagrams
│
├── backend/                           # Python backend application
│   ├── __init__.py
│   ├── main.py                        # FastAPI application entry point
│   ├── config.py                      # Configuration management
│   ├── requirements.txt               # Python dependencies
│   ├── setup.py                       # Package setup
│   ├── .env                           # Environment variables (gitignored)
│   │
│   ├── api/                           # REST API layer
│   │   ├── __init__.py
│   │   ├── routes/                    # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── workloads.py
│   │   │   ├── containers.py
│   │   │   ├── metrics.py
│   │   │   ├── subsystems.py
│   │   │   └── admin.py
│   │   ├── middleware/                # API middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── rate_limit.py
│   │   │   └── cors.py
│   │   └── schemas/                   # Pydantic models
│   │       ├── __init__.py
│   │       ├── workload.py
│   │       ├── container.py
│   │       └── user.py
│   │
│   ├── core/                          # Core business logic
│   │   ├── __init__.py
│   │   ├── workload_manager.py        # Job scheduling and management
│   │   ├── container_orchestrator.py  # Podman integration
│   │   ├── monitoring_service.py      # System metrics collection
│   │   └── security.py                # Security utilities
│   │
│   ├── subsystems/                    # z/OS subsystem simulators
│   │   ├── __init__.py
│   │   ├── jes.py                     # Job Entry Subsystem
│   │   ├── cics.py                    # Transaction processing
│   │   ├── db2.py                     # Database simulator
│   │   └── tso.py                     # Time Sharing Option
│   │
│   ├── database/                      # Database layer
│   │   ├── __init__.py
│   │   ├── models.py                  # SQLAlchemy models
│   │   ├── connection.py              # Database connection
│   │   └── migrations/                # Database migrations
│   │
│   ├── utils/                         # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py                  # Logging configuration
│   │   ├── validators.py              # Input validation
│   │   └── helpers.py                 # Helper functions
│   │
│   ├── tests/                         # Backend tests
│   │   ├── __init__.py
│   │   ├── unit/                      # Unit tests
│   │   ├── integration/               # Integration tests
│   │   └── fixtures/                  # Test fixtures
│   │
│   └── data/                          # Runtime data (gitignored)
│       ├── database.db                # SQLite database
│       ├── logs/                      # Application logs
│       └── workloads/                 # Workload data
│
├── cli/                               # Node.js CLI application
│   ├── package.json                   # NPM package configuration
│   ├── package-lock.json
│   ├── .npmrc                         # NPM configuration
│   ├── index.js                       # CLI entry point
│   ├── zenitone.js                    # Main CLI script
│   │
│   ├── commands/                      # CLI command handlers
│   │   ├── init.js                    # Initialize environment
│   │   ├── workload.js                # Workload commands
│   │   ├── container.js               # Container commands
│   │   ├── metrics.js                 # Metrics commands
│   │   ├── subsystem.js               # Subsystem commands
│   │   └── admin.js                   # Admin commands
│   │
│   ├── lib/                           # CLI libraries
│   │   ├── api-client.js              # API communication
│   │   ├── config.js                  # Configuration management
│   │   ├── formatter.js               # Output formatting
│   │   └── validator.js               # Input validation
│   │
│   ├── templates/                     # CLI templates
│   │   └── config.template.json
│   │
│   └── tests/                         # CLI tests
│       ├── unit/
│       └── integration/
│
├── ui/                                # Admin web UI
│   ├── index.html                     # Main HTML file
│   ├── login.html                     # Login page
│   ├── 404.html                       # Error page
│   │
│   ├── assets/                        # UI assets
│   │   ├── css/                       # Stylesheets
│   │   │   ├── tailwind.config.js
│   │   │   ├── main.css
│   │   │   └── themes.css
│   │   ├── js/                        # JavaScript modules
│   │   │   ├── main.js
│   │   │   ├── api.js
│   │   │   ├── auth.js
│   │   │   ├── dashboard.js
│   │   │   ├── workloads.js
│   │   │   ├── containers.js
│   │   │   ├── subsystems.js
│   │   │   ├── admin.js
│   │   │   └── charts.js
│   │   ├── images/                    # UI images
│   │   └── fonts/                     # Custom fonts
│   │
│   ├── components/                    # Reusable UI components
│   │   ├── navbar.html
│   │   ├── sidebar.html
│   │   ├── card.html
│   │   └── modal.html
│   │
│   └── pages/                         # UI pages
│       ├── dashboard.html
│       ├── workloads.html
│       ├── containers.html
│       ├── subsystems.html
│       └── admin.html
│
├── docs/                              # Documentation
│   ├── README.md                      # Documentation index
│   │
│   ├── architecture/                  # Architecture documentation
│   │   ├── ARCHITECTURE.md            # System architecture
│   │   ├── DATABASE_SCHEMA.md         # Database design
│   │   ├── API_DESIGN.md              # API architecture
│   │   └── SECURITY_DESIGN.md         # Security architecture
│   │
│   ├── api/                           # API documentation
│   │   ├── API_REFERENCE.md           # Complete API reference
│   │   ├── openapi.yaml               # OpenAPI specification
│   │   └── AUTHENTICATION.md          # Auth documentation
│   │
│   ├── cli/                           # CLI documentation
│   │   ├── CLI_GUIDE.md               # CLI user guide
│   │   ├── COMMANDS.md                # Command reference
│   │   └── EXAMPLES.md                # Usage examples
│   │
│   ├── ui/                            # UI documentation
│   │   ├── UI_GUIDE.md                # UI user manual
│   │   ├── DESIGN_SYSTEM.md           # Design guidelines
│   │   └── COMPONENTS.md              # Component library
│   │
│   ├── guides/                        # User guides
│   │   ├── GETTING_STARTED.md         # Beginner tutorial
│   │   ├── INSTALLATION.md            # Installation guide
│   │   ├── CONFIGURATION.md           # Configuration reference
│   │   ├── FIRST_WORKLOAD.md          # First job tutorial
│   │   ├── UNDERSTANDING_LINUXONE.md  # LinuxOne concepts
│   │   ├── TROUBLESHOOTING.md         # Common issues
│   │   └── FAQ.md                     # Frequently asked questions
│   │
│   ├── ibm-submission/                # IBM submission package
│   │   ├── IBM_PRODUCT_BRIEF.md
│   │   ├── IBM_TECHNICAL_SPECIFICATION.md
│   │   ├── IBM_DEPLOYMENT_GUIDE.md
│   │   ├── IBM_SECURITY_ASSESSMENT.md
│   │   ├── IBM_COMPLIANCE_CHECKLIST.md
│   │   ├── IBM_SUPPORT_PLAN.md
│   │   ├── IBM_LICENSING.md
│   │   └── IBM_ROADMAP.md
│   │
│   └── diagrams/                      # Architecture diagrams
│       ├── system-architecture.mmd
│       ├── data-flow.mmd
│       ├── deployment.mmd
│       └── security.mmd
│
├── scripts/                           # Utility scripts
│   ├── install.sh                     # Quick installation script
│   ├── setup.py                       # Python setup script
│   ├── start.sh                       # Start all services
│   ├── stop.sh                        # Stop all services
│   ├── test.sh                        # Run all tests
│   ├── build.sh                       # Build containers
│   └── deploy.sh                      # Deployment script
│
├── tests/                             # Integration tests
│   ├── integration/                   # End-to-end tests
│   ├── performance/                   # Load tests
│   └── security/                      # Security tests
│
├── containers/                        # Container configurations
│   ├── Dockerfile.backend             # Backend container
│   ├── Dockerfile.ui                  # UI container
│   ├── docker-compose.yml             # Docker Compose config
│   └── podman-compose.yml             # Podman Compose config
│
├── systemd/                           # Systemd service files
│   ├── zenitone-backend.service
│   ├── zenitone-ui.service
│   └── zenitone.target
│
├── config/                            # Configuration files
│   ├── backend.yaml                   # Backend configuration
│   ├── cli.json                       # CLI configuration
│   ├── nginx.conf                     # Nginx configuration
│   └── logging.yaml                   # Logging configuration
│
└── marketing/                         # Marketing materials
    ├── LINKEDIN_PROJECT_DOCUMENT.md   # LinkedIn project doc
    ├── LINKEDIN_POST.md               # LinkedIn post
    ├── WHITEPAPER.md                  # White paper source
    ├── WHITEPAPER.pdf                 # White paper PDF
    └── PRESENTATION.pdf               # Project presentation
```

## File Count Summary

- **Total Directories**: ~50
- **Total Files**: ~150+
- **Code Files**: ~80
- **Documentation Files**: ~40
- **Configuration Files**: ~15
- **Test Files**: ~20

## Key Files Description

### Root Level
- `README.md` - First point of contact, quick start guide
- `MASTER_PLAN.md` - Complete project blueprint
- `LICENSE` - MIT License for open source
- `.gitignore` - Excludes data/, logs/, .env, node_modules/, etc.

### Backend (`/backend/`)
- `main.py` - FastAPI app initialization, CORS, middleware
- `config.py` - Environment variables, settings management
- `requirements.txt` - Python dependencies (FastAPI, SQLAlchemy, etc.)

### CLI (`/cli/`)
- `zenitone.js` - Main CLI entry with Commander.js
- `package.json` - NPM dependencies (commander, chalk, inquirer, axios)

### UI (`/ui/`)
- `index.html` - Main dashboard page
- `assets/css/main.css` - TailwindCSS with IBM theme
- `assets/js/main.js` - Core JavaScript logic

### Documentation (`/docs/`)
- Comprehensive guides for all user levels
- IBM submission package with 8 required documents
- API reference with OpenAPI spec

### Scripts (`/scripts/`)
- `install.sh` - One-command installation
- `start.sh` - Start all services
- `test.sh` - Run complete test suite

## Technology Stack by Component

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: SQLAlchemy + SQLite
- **Container**: Podman Python SDK
- **AI**: Ollama Python client (Qwen2.5:latest)
- **Auth**: python-jose (JWT)
- **Validation**: Pydantic v2
- **Testing**: pytest, pytest-asyncio

### CLI
- **Framework**: Commander.js 11+
- **UI**: Chalk 5+, Inquirer 9+
- **HTTP**: Axios 1.6+
- **Config**: Cosmiconfig 8+
- **Testing**: Jest 29+

### UI
- **CSS**: TailwindCSS 3.4+
- **Charts**: Chart.js 4+
- **Icons**: Heroicons
- **HTTP**: Fetch API
- **WebSocket**: Native WebSocket API

### DevOps
- **Containers**: Podman/Docker
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana (optional)
- **Logging**: Python logging + Winston (Node.js)

## Development Workflow

1. **Backend Development** (IBM Bob + Qwen2.5)
   - Work in `/backend/` directory
   - Use virtual environment: `python -m venv venv`
   - Install deps: `pip install -r requirements.txt`
   - Run: `uvicorn backend.main:app --reload`

2. **CLI Development** (Gemini CLI)
   - Work in `/cli/` directory
   - Install deps: `npm install`
   - Link locally: `npm link`
   - Test: `zenitone --help`

3. **UI Development** (IBM Bob + Qwen2.5)
   - Work in `/ui/` directory
   - Use live server for development
   - Build TailwindCSS: `npx tailwindcss -i input.css -o output.css --watch`

4. **Documentation** (IBM Bob)
   - Work in `/docs/` directory
   - Use Markdown for all docs
   - Generate diagrams with Mermaid

## Git Workflow

```bash
# Main branches
main          # Production-ready code
develop       # Development branch
feature/*     # Feature branches
hotfix/*      # Hotfix branches

# Commit convention
feat: Add new feature
fix: Bug fix
docs: Documentation update
style: Code style changes
refactor: Code refactoring
test: Test updates
chore: Build/config changes
```

## Build and Deployment

```bash
# Development
./scripts/start.sh

# Testing
./scripts/test.sh

# Production build
./scripts/build.sh

# Deployment
./scripts/deploy.sh
```

## Resource Requirements

### Development
- Disk: ~500MB (code + dependencies)
- RAM: ~1GB (all services running)
- CPU: Minimal (background services)

### Production
- Disk: ~1GB (includes data)
- RAM: ~2GB (under load)
- CPU: ~20-30% (typical usage)

## Next Steps

1. Create directory structure: `mkdir -p backend cli ui docs scripts tests`
2. Initialize Git: `git init && git add . && git commit -m "Initial commit"`
3. Set up Python venv: `cd backend && python -m venv venv`
4. Initialize Node project: `cd cli && npm init -y`
5. Begin Phase 2 development

---

**Last Updated**: 2026-05-26  
**Version**: 1.0.0
