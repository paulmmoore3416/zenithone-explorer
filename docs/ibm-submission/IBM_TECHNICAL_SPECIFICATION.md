# ZenithOne Explorer - Technical Specification

**Detailed Technical Documentation for IBM LinuxONE Showcase**

---

## Document Information

- **Document Type**: Technical Specification
- **Version**: 1.0.0
- **Date**: January 15, 2024
- **Status**: Final
- **Classification**: Public
- **Author**: Paul Moore (paulmmoore3416@gmail.com)

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Design](#architecture-design)
3. [Component Specifications](#component-specifications)
4. [API Specifications](#api-specifications)
5. [Database Schema](#database-schema)
6. [Security Architecture](#security-architecture)
7. [Performance Specifications](#performance-specifications)
8. [Integration Specifications](#integration-specifications)

---

## 1. System Overview

### 1.1 Product Description

ZenithOne Explorer is a comprehensive enterprise workload management platform that brings IBM LinuxONE capabilities to consumer hardware through:

- AI-enhanced workload scheduling and optimization
- Container-based workload execution using Podman
- z/OS subsystem simulation (JES, CICS, DB2, TSO)
- Real-time monitoring and metrics collection
- Multi-interface access (Web UI, CLI, REST API)

### 1.2 System Architecture

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
│       │  ┌─────────────────────────────────┐  │             │
│       │  │   Authentication & Security     │  │             │
│       │  └─────────────────────────────────┘  │             │
│       │  ┌─────────────────────────────────┐  │             │
│       │  │      Workload Manager           │  │             │
│       │  └─────────────────────────────────┘  │             │
│       │  ┌─────────────────────────────────┐  │             │
│       │  │   Container Orchestrator        │  │             │
│       │  └─────────────────────────────────┘  │             │
│       │  ┌─────────────────────────────────┐  │             │
│       │  │    Monitoring Service           │  │             │
│       │  └─────────────────────────────────┘  │             │
│       │  ┌─────────────────────────────────┐  │             │
│       │  │   Subsystem Simulators          │  │             │
│       │  └─────────────────────────────────┘  │             │
│       └───────────┬───────────────────────────┘             │
│                   │                                           │
│       ┌───────────▼───────────┐  ┌──────────────────────┐   │
│       │  SQLAlchemy ORM       │  │   Ollama AI Engine   │   │
│       └───────────┬───────────┘  └──────────────────────┘   │
│                   │                                           │
│       ┌───────────▼───────────┐  ┌──────────────────────┐   │
│       │  SQLite/PostgreSQL    │  │   Podman Runtime     │   │
│       └───────────────────────┘  └──────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Backend Framework | FastAPI | 0.104+ | REST API and WebSocket server |
| ORM | SQLAlchemy | 2.0+ | Database abstraction |
| Validation | Pydantic | 2.0+ | Data validation and serialization |
| Authentication | JWT | - | Token-based authentication |
| AI Engine | Ollama | 0.1+ | Local AI inference |
| AI Model | Qwen2.5 | Latest | Workload optimization |
| Container Runtime | Podman | 4.5+ | Container orchestration |
| Database | SQLite/PostgreSQL | - | Data persistence |
| CLI Framework | Commander.js | 11+ | Command-line interface |
| HTTP Client | Axios | 1.6+ | API communication |
| Charts | Chart.js | 4.4+ | Data visualization |
| Testing | pytest | 7.4+ | Unit and integration testing |

---

## 2. Architecture Design

### 2.1 Layered Architecture

#### Presentation Layer
- **Web UI**: HTML5, CSS3, JavaScript (ES6+)
- **CLI**: Node.js-based command-line interface
- **API**: RESTful endpoints with OpenAPI documentation

#### Application Layer
- **API Routes**: FastAPI route handlers
- **Business Logic**: Core service modules
- **Middleware**: Authentication, logging, error handling

#### Domain Layer
- **Workload Manager**: Workload lifecycle management
- **Container Orchestrator**: Container operations
- **Monitoring Service**: Metrics collection and analysis
- **Subsystem Simulators**: z/OS subsystem emulation

#### Data Layer
- **ORM Models**: SQLAlchemy entity definitions
- **Database**: SQLite (development) / PostgreSQL (production)
- **Caching**: In-memory caching for performance

### 2.2 Component Interaction

```
User Request → API Gateway → Authentication → Route Handler
                                                    ↓
                                            Business Logic
                                                    ↓
                                    ┌───────────────┴───────────────┐
                                    ↓                               ↓
                            Domain Services                  External Services
                            (Workload, Container)            (Podman, Ollama)
                                    ↓                               ↓
                            Data Access Layer                Response
                                    ↓
                                Database
```

### 2.3 Data Flow

#### Workload Creation Flow
1. User submits workload via UI/CLI/API
2. API validates request data
3. Authentication middleware verifies user
4. Workload Manager creates workload record
5. Database persists workload
6. Response returned to user

#### Workload Execution Flow
1. Scheduler selects pending workload
2. AI Engine (optional) optimizes scheduling
3. Container Orchestrator creates container
4. Podman starts container
5. Monitoring Service tracks execution
6. Logs collected and stored
7. Status updated in database
8. WebSocket notifies connected clients

---

## 3. Component Specifications

### 3.1 Backend Components

#### 3.1.1 FastAPI Application (main.py)

**Purpose**: Main application entry point and configuration

**Key Features**:
- CORS middleware configuration
- Route registration
- Exception handlers
- Startup/shutdown events
- Health check endpoint

**Configuration**:
```python
app = FastAPI(
    title="ZenithOne Explorer API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

#### 3.1.2 Workload Manager (core/workload_manager.py)

**Purpose**: Manage workload lifecycle

**Key Methods**:
- `create_workload()`: Create new workload
- `schedule_workload()`: Schedule for execution
- `execute_workload()`: Execute workload
- `cancel_workload()`: Cancel running workload
- `get_workload_status()`: Retrieve status
- `get_workload_logs()`: Retrieve logs

**Workload States**:
```
pending → scheduled → running → completed
                         ↓
                      failed
                         ↓
                    cancelled
```

#### 3.1.3 Container Orchestrator (core/container_orchestrator.py)

**Purpose**: Manage container lifecycle

**Key Methods**:
- `create_container()`: Create container from workload
- `start_container()`: Start container
- `stop_container()`: Stop container
- `pause_container()`: Pause container
- `unpause_container()`: Resume container
- `delete_container()`: Remove container
- `get_container_logs()`: Retrieve logs
- `get_container_stats()`: Get resource usage

**Podman Integration**:
```python
# Container creation
container = podman.containers.create(
    image=workload.image,
    command=workload.command,
    cpu_limit=workload.cpu_limit,
    memory_limit=workload.memory_limit,
    environment=workload.environment
)
```

#### 3.1.4 Monitoring Service (core/monitoring_service.py)

**Purpose**: Collect and analyze system metrics

**Metrics Collected**:
- CPU usage (overall and per-core)
- Memory usage (total, used, free, cached)
- Disk usage and I/O
- Network throughput
- Container resource usage
- Workload execution statistics

**Collection Interval**: 60 seconds (configurable)

**Retention**: 30 days (configurable)

#### 3.1.5 Security Module (core/security.py)

**Purpose**: Authentication and authorization

**Key Functions**:
- `create_access_token()`: Generate JWT token
- `verify_token()`: Validate JWT token
- `hash_password()`: Hash password with bcrypt
- `verify_password()`: Verify password
- `get_current_user()`: Extract user from token
- `require_role()`: Role-based access control

**JWT Configuration**:
```python
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

### 3.2 Subsystem Simulators

#### 3.2.1 JES Simulator (subsystems/jes.py)

**Purpose**: Simulate Job Entry Subsystem

**Features**:
- Job submission and tracking
- Job queue management
- Spool management
- Job status monitoring
- Priority-based scheduling

**Job States**: SUBMITTED → QUEUED → RUNNING → COMPLETED/FAILED

#### 3.2.2 CICS Simulator (subsystems/cics.py)

**Purpose**: Simulate transaction processing

**Features**:
- Transaction management
- Region control
- Response time tracking
- Transaction statistics
- Load balancing simulation

#### 3.2.3 DB2 Simulator (subsystems/db2.py)

**Purpose**: Simulate database operations

**Features**:
- Connection pool management
- Query execution simulation
- Performance metrics
- Buffer pool statistics
- Lock management simulation

#### 3.2.4 TSO Simulator (subsystems/tso.py)

**Purpose**: Simulate time-sharing operations

**Features**:
- Session management
- Command execution
- User interaction simulation
- Session timeout handling
- Command history

---

## 4. API Specifications

### 4.1 API Design Principles

- **RESTful**: Resource-based URLs
- **Stateless**: No server-side session state
- **JSON**: Request and response format
- **Versioned**: `/api/v1/` prefix
- **Documented**: OpenAPI/Swagger documentation

### 4.2 Authentication

**Method**: JWT Bearer Token

**Header**:
```
Authorization: Bearer <access_token>
```

**Token Structure**:
```json
{
  "sub": "user_id",
  "username": "admin",
  "role": "admin",
  "exp": 1640995200
}
```

### 4.3 API Endpoints Summary

| Category | Endpoints | Methods | Authentication |
|----------|-----------|---------|----------------|
| Authentication | /auth/* | POST | Public (login/register) |
| Workloads | /workloads/* | GET, POST, PUT, DELETE | Required |
| Containers | /containers/* | GET, POST, DELETE | Required |
| Subsystems | /subsystems/* | GET, POST | Required |
| Metrics | /metrics/* | GET | Required |
| Admin | /admin/* | GET, POST, PUT, DELETE | Admin only |

### 4.4 Request/Response Format

**Standard Success Response**:
```json
{
  "data": { ... },
  "message": "Success",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Standard Error Response**:
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 4.5 Rate Limiting

- **Per Minute**: 60 requests
- **Per Hour**: 1000 requests
- **Headers**: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset

---

## 5. Database Schema

### 5.1 Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│    Users    │       │  Workloads   │       │ Containers  │
├─────────────┤       ├──────────────┤       ├─────────────┤
│ id (PK)     │───┐   │ id (PK)      │───┐   │ id (PK)     │
│ username    │   └──→│ user_id (FK) │   └──→│ workload_id │
│ email       │       │ name         │       │ name        │
│ password    │       │ type         │       │ image       │
│ role        │       │ status       │       │ status      │
│ created_at  │       │ priority     │       │ created_at  │
└─────────────┘       │ image        │       └─────────────┘
                      │ command      │
                      │ cpu_limit    │
                      │ memory_limit │
                      │ created_at   │
                      │ started_at   │
                      │ completed_at │
                      └──────────────┘

┌─────────────┐       ┌──────────────┐
│   Metrics   │       │ Subsystems   │
├─────────────┤       ├──────────────┤
│ id (PK)     │       │ id (PK)      │
│ timestamp   │       │ name         │
│ cpu_usage   │       │ status       │
│ memory_usage│       │ uptime       │
│ disk_usage  │       │ config       │
│ network_io  │       │ created_at   │
└─────────────┘       └──────────────┘
```

### 5.2 Table Specifications

#### Users Table
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

#### Workloads Table
```sql
CREATE TABLE workloads (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    priority VARCHAR(20) NOT NULL DEFAULT 'normal',
    image VARCHAR(255) NOT NULL,
    command TEXT NOT NULL,
    cpu_limit FLOAT DEFAULT 1.0,
    memory_limit INTEGER DEFAULT 512,
    environment JSON,
    volumes JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    exit_code INTEGER
);
```

#### Containers Table
```sql
CREATE TABLE containers (
    id VARCHAR(36) PRIMARY KEY,
    workload_id VARCHAR(36) REFERENCES workloads(id),
    container_id VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    image VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    stopped_at TIMESTAMP
);
```

### 5.3 Indexes

```sql
CREATE INDEX idx_workloads_user_id ON workloads(user_id);
CREATE INDEX idx_workloads_status ON workloads(status);
CREATE INDEX idx_workloads_created_at ON workloads(created_at);
CREATE INDEX idx_containers_workload_id ON containers(workload_id);
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp);
```

---

## 6. Security Architecture

### 6.1 Authentication Flow

```
1. User → POST /auth/login {username, password}
2. Server validates credentials
3. Server generates JWT token
4. Server → User {access_token, refresh_token}
5. User stores token
6. User → API Request + Authorization: Bearer <token>
7. Server validates token
8. Server processes request
9. Server → Response
```

### 6.2 Authorization Levels

| Role | Permissions |
|------|-------------|
| Admin | Full access to all resources |
| User | Create/manage own workloads, view system metrics |
| Guest | Read-only access (if enabled) |

### 6.3 Security Measures

**Input Validation**:
- Pydantic models for request validation
- Type checking and constraints
- SQL injection prevention via ORM

**Password Security**:
- Bcrypt hashing (cost factor: 12)
- Minimum length: 8 characters
- Complexity requirements (configurable)

**Token Security**:
- Short-lived access tokens (60 minutes)
- Refresh tokens (7 days)
- Token revocation support

**Network Security**:
- CORS configuration
- Rate limiting
- SSL/TLS support

---

## 7. Performance Specifications

### 7.1 Response Time Targets

| Operation | Target | Maximum |
|-----------|--------|---------|
| API Request (simple) | <50ms | <100ms |
| API Request (complex) | <200ms | <500ms |
| Workload Creation | <100ms | <200ms |
| Container Startup | <2s | <5s |
| AI Scheduling | <500ms | <1s |
| WebSocket Update | <50ms | <100ms |

### 7.2 Throughput Targets

- **API Requests**: 1000+ requests/second
- **Concurrent Workloads**: 10+ simultaneous
- **Concurrent Containers**: 50+ active
- **WebSocket Connections**: 100+ simultaneous

### 7.3 Resource Usage

**Backend Process**:
- Memory: ~500MB base, +50MB per 10 workloads
- CPU: <10% idle, <50% under load
- Disk I/O: Minimal (database operations)

**Container Overhead**:
- Per container: ~10MB memory overhead
- Startup time: <2 seconds average

### 7.4 Scalability

**Vertical Scaling**:
- Increase worker processes
- Allocate more memory
- Add CPU cores

**Horizontal Scaling** (Future):
- Multi-node deployment
- Load balancing
- Distributed workload execution

---

## 8. Integration Specifications

### 8.1 Podman Integration

**Connection**: Unix socket (`/run/user/1000/podman/podman.sock`)

**Operations**:
- Container lifecycle management
- Image management
- Volume management
- Network configuration

**Error Handling**:
- Connection failures: Retry with exponential backoff
- Container failures: Log and update workload status
- Resource limits: Enforce and monitor

### 8.2 Ollama Integration

**Connection**: HTTP API (`http://localhost:11434`)

**Operations**:
- Model inference
- Workload optimization
- Resource prediction

**Timeout**: 120 seconds (configurable)

**Fallback**: Manual scheduling if AI unavailable

### 8.3 External Monitoring

**Prometheus Export** (Optional):
- Metrics endpoint: `/metrics`
- Format: Prometheus text format
- Update interval: 60 seconds

**Log Export**:
- Format: JSON structured logs
- Destination: File, syslog, or external service
- Rotation: Daily or size-based

---

## Appendix A: Configuration Reference

See [CONFIGURATION.md](../CONFIGURATION.md) for complete configuration options.

## Appendix B: API Reference

See [API_REFERENCE.md](../API_REFERENCE.md) for complete API documentation.

## Appendix C: Database Migrations

Database migrations managed via Alembic (future enhancement).

---

*Document Version: 1.0*  
*Last Updated: January 15, 2024*  
*Classification: Public*
