# ZenithOne Explorer - Database Schema Design

## Overview

**Database Engine**: SQLite 3.x  
**ORM**: SQLAlchemy 2.x  
**Migration Tool**: Alembic  
**Location**: `/backend/data/database.db`

---

## Schema Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │   workloads     │       │   containers    │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │───┐   │ id (PK)         │       │ id (PK)         │
│ username        │   │   │ name            │       │ name            │
│ email           │   │   │ type            │       │ image           │
│ password_hash   │   │   │ status          │       │ status          │
│ role            │   │   │ priority        │       │ created_at      │
│ created_at      │   │   │ subsystem       │       │ started_at      │
│ last_login      │   │   │ command         │       │ ports           │
│ active          │   │   │ parameters      │       │ environment     │
└─────────────────┘   │   │ created_at      │       │ volumes         │
                      │   │ started_at      │       │ cpu_limit       │
                      │   │ completed_at    │       │ memory_limit    │
                      │   │ duration        │       └─────────────────┘
                      │   │ cpu_usage       │
                      │   │ memory_usage    │
                      └───│ owner_id (FK)   │
                          └─────────────────┘
                                  │
                                  │
                          ┌───────┴─────────┐
                          │                 │
                  ┌───────▼──────┐  ┌──────▼──────┐
                  │ workload_logs│  │ workload_   │
                  ├──────────────┤  │ metrics     │
                  │ id (PK)      │  ├─────────────┤
                  │ workload_id  │  │ id (PK)     │
                  │ timestamp    │  │ workload_id │
                  │ level        │  │ timestamp   │
                  │ message      │  │ cpu_usage   │
                  └──────────────┘  │ memory_usage│
                                    │ disk_io     │
                                    │ network_io  │
                                    └─────────────┘

┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   subsystems    │       │  system_metrics │       │   audit_logs    │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ name            │       │ timestamp       │       │ timestamp       │
│ status          │       │ cpu_usage       │       │ user_id (FK)    │
│ uptime          │       │ memory_total    │       │ action          │
│ version         │       │ memory_used     │       │ resource_type   │
│ configuration   │       │ disk_total      │       │ resource_id     │
│ statistics      │       │ disk_used       │       │ ip_address      │
│ last_started    │       │ network_rx      │       │ status          │
└─────────────────┘       │ network_tx      │       │ details         │
                          └─────────────────┘       └─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│  api_tokens     │       │  configurations │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ user_id (FK)    │       │ key             │
│ token_hash      │       │ value           │
│ expires_at      │       │ category        │
│ created_at      │       │ description     │
│ last_used       │       │ updated_at      │
│ revoked         │       │ updated_by      │
└─────────────────┘       └─────────────────┘
```

---

## Table Definitions

### users

Stores user account information and authentication data.

```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,                    -- UUID
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,            -- bcrypt hash
    role TEXT NOT NULL,                     -- admin, user, viewer
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    metadata TEXT                           -- JSON: additional user data
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

**Columns**:
- `id`: Unique identifier (UUID v4)
- `username`: Unique username (3-32 chars)
- `email`: Valid email address
- `password_hash`: bcrypt hashed password
- `role`: User role (admin|user|viewer)
- `created_at`: Account creation timestamp
- `last_login`: Last successful login
- `active`: Account status
- `metadata`: JSON field for extensibility

**Constraints**:
- Username: alphanumeric + underscore, 3-32 chars
- Email: valid email format
- Password: min 8 chars (enforced at application level)

---

### workloads

Stores job/workload information and execution state.

```sql
CREATE TABLE workloads (
    id TEXT PRIMARY KEY,                    -- UUID
    name TEXT NOT NULL,
    type TEXT NOT NULL,                     -- batch, transaction, interactive
    status TEXT NOT NULL,                   -- pending, running, completed, failed, cancelled
    priority TEXT NOT NULL,                 -- low, medium, high, critical
    subsystem TEXT NOT NULL,                -- JES, CICS, TSO, DB2
    command TEXT NOT NULL,
    parameters TEXT,                        -- JSON: command parameters
    resources TEXT,                         -- JSON: resource limits
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration INTEGER,                       -- seconds
    cpu_usage REAL,                         -- percentage
    memory_usage INTEGER,                   -- MB
    owner_id TEXT NOT NULL,
    exit_code INTEGER,
    error_message TEXT,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_workloads_status ON workloads(status);
CREATE INDEX idx_workloads_owner ON workloads(owner_id);
CREATE INDEX idx_workloads_created ON workloads(created_at DESC);
CREATE INDEX idx_workloads_priority ON workloads(priority);
CREATE INDEX idx_workloads_subsystem ON workloads(subsystem);
```

**Columns**:
- `id`: Unique identifier (UUID v4)
- `name`: Workload name/description
- `type`: Workload type
- `status`: Current execution status
- `priority`: Execution priority
- `subsystem`: Target z/OS subsystem
- `command`: Command to execute
- `parameters`: JSON parameters
- `resources`: JSON resource limits
- `created_at`: Submission timestamp
- `started_at`: Execution start time
- `completed_at`: Completion time
- `duration`: Total execution time
- `cpu_usage`: Average CPU usage
- `memory_usage`: Peak memory usage
- `owner_id`: User who submitted
- `exit_code`: Process exit code
- `error_message`: Error details if failed

---

### workload_logs

Stores execution logs for workloads.

```sql
CREATE TABLE workload_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workload_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    level TEXT NOT NULL,                    -- DEBUG, INFO, WARNING, ERROR, CRITICAL
    message TEXT NOT NULL,
    source TEXT,                            -- log source/component
    FOREIGN KEY (workload_id) REFERENCES workloads(id) ON DELETE CASCADE
);

CREATE INDEX idx_workload_logs_workload ON workload_logs(workload_id);
CREATE INDEX idx_workload_logs_timestamp ON workload_logs(timestamp DESC);
CREATE INDEX idx_workload_logs_level ON workload_logs(level);
```

**Columns**:
- `id`: Auto-increment ID
- `workload_id`: Associated workload
- `timestamp`: Log entry time
- `level`: Log severity level
- `message`: Log message
- `source`: Component that generated log

---

### workload_metrics

Stores time-series metrics for workloads.

```sql
CREATE TABLE workload_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workload_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cpu_usage REAL,                         -- percentage
    memory_usage INTEGER,                   -- MB
    disk_read INTEGER,                      -- bytes
    disk_write INTEGER,                     -- bytes
    network_rx INTEGER,                     -- bytes
    network_tx INTEGER,                     -- bytes
    FOREIGN KEY (workload_id) REFERENCES workloads(id) ON DELETE CASCADE
);

CREATE INDEX idx_workload_metrics_workload ON workload_metrics(workload_id);
CREATE INDEX idx_workload_metrics_timestamp ON workload_metrics(timestamp DESC);
```

**Columns**:
- `id`: Auto-increment ID
- `workload_id`: Associated workload
- `timestamp`: Metric collection time
- `cpu_usage`: CPU usage percentage
- `memory_usage`: Memory usage in MB
- `disk_read`: Bytes read from disk
- `disk_write`: Bytes written to disk
- `network_rx`: Bytes received
- `network_tx`: Bytes transmitted

---

### containers

Stores container information and state.

```sql
CREATE TABLE containers (
    id TEXT PRIMARY KEY,                    -- Container ID from Podman
    name TEXT UNIQUE NOT NULL,
    image TEXT NOT NULL,
    status TEXT NOT NULL,                   -- running, stopped, paused, error
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    ports TEXT,                             -- JSON: port mappings
    environment TEXT,                       -- JSON: environment variables
    volumes TEXT,                           -- JSON: volume mounts
    cpu_limit REAL,                         -- CPU cores
    memory_limit INTEGER,                   -- MB
    command TEXT,
    owner_id TEXT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_containers_status ON containers(status);
CREATE INDEX idx_containers_owner ON containers(owner_id);
CREATE INDEX idx_containers_name ON containers(name);
```

**Columns**:
- `id`: Container ID from Podman
- `name`: Container name
- `image`: Container image
- `status`: Current status
- `created_at`: Creation timestamp
- `started_at`: Start timestamp
- `ports`: JSON port mappings
- `environment`: JSON environment vars
- `volumes`: JSON volume mounts
- `cpu_limit`: CPU limit in cores
- `memory_limit`: Memory limit in MB
- `command`: Container command
- `owner_id`: User who created

---

### subsystems

Stores z/OS subsystem status and configuration.

```sql
CREATE TABLE subsystems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,              -- JES, CICS, DB2, TSO
    status TEXT NOT NULL,                   -- active, inactive, error
    uptime INTEGER DEFAULT 0,               -- seconds
    version TEXT,
    configuration TEXT,                     -- JSON: subsystem config
    statistics TEXT,                        -- JSON: runtime statistics
    last_started TIMESTAMP,
    last_stopped TIMESTAMP
);

CREATE INDEX idx_subsystems_name ON subsystems(name);
CREATE INDEX idx_subsystems_status ON subsystems(status);
```

**Columns**:
- `id`: Auto-increment ID
- `name`: Subsystem name
- `status`: Current status
- `uptime`: Uptime in seconds
- `version`: Subsystem version
- `configuration`: JSON configuration
- `statistics`: JSON runtime stats
- `last_started`: Last start time
- `last_stopped`: Last stop time

---

### system_metrics

Stores system-wide metrics over time.

```sql
CREATE TABLE system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cpu_usage REAL,                         -- percentage
    cpu_load_1 REAL,                        -- 1-min load average
    cpu_load_5 REAL,                        -- 5-min load average
    cpu_load_15 REAL,                       -- 15-min load average
    memory_total INTEGER,                   -- bytes
    memory_used INTEGER,                    -- bytes
    memory_available INTEGER,               -- bytes
    disk_total INTEGER,                     -- bytes
    disk_used INTEGER,                      -- bytes
    network_rx INTEGER,                     -- bytes
    network_tx INTEGER,                     -- bytes
    active_workloads INTEGER,
    active_containers INTEGER
);

CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp DESC);
```

**Columns**:
- `id`: Auto-increment ID
- `timestamp`: Metric collection time
- `cpu_usage`: Overall CPU usage
- `cpu_load_*`: Load averages
- `memory_*`: Memory statistics
- `disk_*`: Disk statistics
- `network_*`: Network statistics
- `active_workloads`: Running workloads
- `active_containers`: Running containers

---

### audit_logs

Stores audit trail for security and compliance.

```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT,
    action TEXT NOT NULL,                   -- workload:create, container:start, etc.
    resource_type TEXT,                     -- workload, container, user, etc.
    resource_id TEXT,
    ip_address TEXT,
    status TEXT NOT NULL,                   -- success, failure
    details TEXT,                           -- JSON: additional details
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
```

**Columns**:
- `id`: Auto-increment ID
- `timestamp`: Action timestamp
- `user_id`: User who performed action
- `action`: Action performed
- `resource_type`: Type of resource
- `resource_id`: Resource identifier
- `ip_address`: Client IP address
- `status`: Action result
- `details`: JSON additional info

---

### api_tokens

Stores API authentication tokens.

```sql
CREATE TABLE api_tokens (
    id TEXT PRIMARY KEY,                    -- UUID
    user_id TEXT NOT NULL,
    token_hash TEXT UNIQUE NOT NULL,        -- SHA-256 hash
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_api_tokens_user ON api_tokens(user_id);
CREATE INDEX idx_api_tokens_expires ON api_tokens(expires_at);
CREATE INDEX idx_api_tokens_hash ON api_tokens(token_hash);
```

**Columns**:
- `id`: Token ID (UUID v4)
- `user_id`: Token owner
- `token_hash`: SHA-256 hash of token
- `expires_at`: Expiration timestamp
- `created_at`: Creation timestamp
- `last_used`: Last usage timestamp
- `revoked`: Revocation status
- `description`: Token description

---

### configurations

Stores system configuration key-value pairs.

```sql
CREATE TABLE configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    category TEXT,                          -- security, resources, ui, etc.
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT,
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_configurations_key ON configurations(key);
CREATE INDEX idx_configurations_category ON configurations(category);
```

**Columns**:
- `id`: Auto-increment ID
- `key`: Configuration key
- `value`: Configuration value (JSON)
- `category`: Configuration category
- `description`: Human-readable description
- `updated_at`: Last update timestamp
- `updated_by`: User who updated

---

## Data Relationships

### One-to-Many Relationships

1. **users → workloads**
   - One user can submit many workloads
   - Cascade delete: Remove workloads when user deleted

2. **users → containers**
   - One user can create many containers
   - Cascade delete: Remove containers when user deleted

3. **workloads → workload_logs**
   - One workload has many log entries
   - Cascade delete: Remove logs when workload deleted

4. **workloads → workload_metrics**
   - One workload has many metric snapshots
   - Cascade delete: Remove metrics when workload deleted

5. **users → audit_logs**
   - One user generates many audit entries
   - Set null on delete: Preserve audit trail

6. **users → api_tokens**
   - One user can have many API tokens
   - Cascade delete: Remove tokens when user deleted

---

## Initial Data

### Default Users

```sql
INSERT INTO users (id, username, email, password_hash, role, active) VALUES
('00000000-0000-0000-0000-000000000001', 'admin', 'admin@zenitone.local', '$2b$12$...', 'admin', TRUE),
('00000000-0000-0000-0000-000000000002', 'demo', 'demo@zenitone.local', '$2b$12$...', 'user', TRUE),
('00000000-0000-0000-0000-000000000003', 'viewer', 'viewer@zenitone.local', '$2b$12$...', 'viewer', TRUE);
```

**Default Passwords** (change in production):
- admin: `Admin@123`
- demo: `Demo@123`
- viewer: `Viewer@123`

### Default Subsystems

```sql
INSERT INTO subsystems (name, status, version, configuration, statistics) VALUES
('JES', 'inactive', '1.0.0', '{"max_jobs": 1000, "spool_size": 10737418240}', '{}'),
('CICS', 'inactive', '1.0.0', '{"max_transactions": 10000, "timeout": 30}', '{}'),
('DB2', 'inactive', '1.0.0', '{"max_connections": 100, "cache_size": 536870912}', '{}'),
('TSO', 'inactive', '1.0.0', '{"max_sessions": 50, "timeout": 1800}', '{}');
```

### Default Configurations

```sql
INSERT INTO configurations (key, value, category, description) VALUES
('security.jwt_expiration', '3600', 'security', 'JWT token expiration in seconds'),
('security.rate_limit', '100', 'security', 'API rate limit per minute'),
('security.password_min_length', '8', 'security', 'Minimum password length'),
('resources.max_workloads', '1000', 'resources', 'Maximum concurrent workloads'),
('resources.max_containers', '100', 'resources', 'Maximum concurrent containers'),
('resources.default_cpu_limit', '2', 'resources', 'Default CPU limit per workload'),
('resources.default_memory_limit', '1024', 'resources', 'Default memory limit in MB'),
('ui.theme', 'dark', 'ui', 'Default UI theme'),
('ui.refresh_interval', '5', 'ui', 'Metrics refresh interval in seconds');
```

---

## Database Migrations

### Migration Strategy

Using Alembic for schema versioning:

```bash
# Initialize Alembic
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Migration Files Location

`/backend/database/migrations/versions/`

---

## Performance Optimization

### Indexing Strategy

1. **Primary Keys**: All tables have indexed primary keys
2. **Foreign Keys**: All foreign keys are indexed
3. **Query Patterns**: Indexes on frequently queried columns
4. **Timestamp Columns**: Descending indexes for recent-first queries

### Query Optimization

1. **Pagination**: Use LIMIT/OFFSET for large result sets
2. **Filtering**: Use indexed columns in WHERE clauses
3. **Joins**: Minimize joins, use eager loading
4. **Aggregations**: Use database-level aggregations

### Data Retention

1. **Logs**: Retain 30 days, archive older
2. **Metrics**: Retain 90 days, aggregate older
3. **Audit Logs**: Retain 1 year minimum
4. **Completed Workloads**: Retain 90 days

---

## Backup Strategy

### Backup Schedule

- **Full Backup**: Daily at 2:00 AM
- **Incremental**: Every 6 hours
- **Retention**: 30 days

### Backup Commands

```bash
# Manual backup
sqlite3 database.db ".backup backup.db"

# Automated backup script
./scripts/backup-database.sh
```

### Restore Procedure

```bash
# Restore from backup
cp backup.db database.db

# Verify integrity
sqlite3 database.db "PRAGMA integrity_check;"
```

---

## Security Considerations

### Password Security

- bcrypt hashing with cost factor 12
- Minimum 8 characters
- Complexity requirements enforced

### Token Security

- JWT with HS256 algorithm
- 1-hour expiration
- Refresh token rotation

### SQL Injection Prevention

- Parameterized queries only
- SQLAlchemy ORM protection
- Input validation

### Data Encryption

- Sensitive fields encrypted at rest
- TLS for data in transit
- Secure key management

---

## Database Maintenance

### Regular Tasks

1. **VACUUM**: Weekly to reclaim space
2. **ANALYZE**: Daily to update statistics
3. **INTEGRITY_CHECK**: Weekly
4. **REINDEX**: Monthly

### Maintenance Commands

```sql
-- Vacuum database
VACUUM;

-- Analyze tables
ANALYZE;

-- Check integrity
PRAGMA integrity_check;

-- Reindex
REINDEX;
```

---

## Monitoring

### Key Metrics

- Database size
- Query performance
- Connection pool usage
- Lock contention
- Cache hit ratio

### Monitoring Queries

```sql
-- Database size
SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();

-- Table sizes
SELECT name, SUM(pgsize) as size FROM dbstat GROUP BY name ORDER BY size DESC;

-- Index usage
SELECT * FROM sqlite_stat1;
```

---

**Last Updated**: 2026-05-26  
**Version**: 1.0.0
