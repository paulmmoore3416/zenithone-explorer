# ZenithOne Explorer - API Reference

Complete REST API documentation for ZenithOne Explorer.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All API endpoints (except `/auth/login` and `/auth/register`) require authentication using JWT Bearer tokens.

### Headers

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

## API Endpoints

### Authentication

#### POST /auth/login

Authenticate user and receive access token.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user123",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

**Errors:**
- `401 Unauthorized`: Invalid credentials
- `429 Too Many Requests`: Rate limit exceeded

#### POST /auth/register

Register new user account.

**Request:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "role": "user"
}
```

**Response (201):**
```json
{
  "id": "user456",
  "username": "newuser",
  "email": "user@example.com",
  "role": "user",
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Errors:**
- `400 Bad Request`: Invalid input or username exists
- `422 Unprocessable Entity`: Validation error

#### POST /auth/logout

Logout and invalidate token.

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

#### GET /auth/me

Get current user information.

**Response (200):**
```json
{
  "id": "user123",
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin",
  "created_at": "2024-01-01T12:00:00Z",
  "last_login": "2024-01-01T12:00:00Z"
}
```

---

### Workloads

#### POST /workloads

Create new workload.

**Request:**
```json
{
  "name": "data-processing",
  "type": "batch",
  "image": "python:3.14",
  "command": "python process.py",
  "priority": "normal",
  "cpu_limit": 2.0,
  "memory_limit": 1024,
  "environment": {
    "ENV_VAR": "value"
  },
  "volumes": {
    "/host/path": "/container/path"
  }
}
```

**Response (201):**
```json
{
  "id": "wl_abc123",
  "name": "data-processing",
  "type": "batch",
  "status": "pending",
  "priority": "normal",
  "image": "python:3.14",
  "command": "python process.py",
  "cpu_limit": 2.0,
  "memory_limit": 1024,
  "created_at": "2024-01-01T12:00:00Z",
  "created_by": "admin"
}
```

**Errors:**
- `400 Bad Request`: Invalid workload configuration
- `401 Unauthorized`: Not authenticated
- `422 Unprocessable Entity`: Validation error

#### GET /workloads

List all workloads with optional filtering.

**Query Parameters:**
- `status` (optional): Filter by status (pending, running, completed, failed, cancelled)
- `type` (optional): Filter by type (batch, interactive, service, scheduled)
- `priority` (optional): Filter by priority (low, normal, high, critical)
- `limit` (optional): Number of results (default: 20)
- `offset` (optional): Pagination offset (default: 0)

**Response (200):**
```json
[
  {
    "id": "wl_abc123",
    "name": "data-processing",
    "type": "batch",
    "status": "running",
    "priority": "normal",
    "created_at": "2024-01-01T12:00:00Z",
    "started_at": "2024-01-01T12:01:00Z"
  }
]
```

#### GET /workloads/{workload_id}

Get workload details.

**Response (200):**
```json
{
  "id": "wl_abc123",
  "name": "data-processing",
  "type": "batch",
  "status": "running",
  "priority": "normal",
  "image": "python:3.14",
  "command": "python process.py",
  "cpu_limit": 2.0,
  "memory_limit": 1024,
  "created_at": "2024-01-01T12:00:00Z",
  "started_at": "2024-01-01T12:01:00Z",
  "container_id": "cont_xyz789",
  "exit_code": null,
  "metrics": {
    "cpu_usage": 45.5,
    "memory_usage": 512
  }
}
```

**Errors:**
- `404 Not Found`: Workload not found

#### PUT /workloads/{workload_id}

Update workload configuration.

**Request:**
```json
{
  "priority": "high",
  "cpu_limit": 4.0
}
```

**Response (200):**
```json
{
  "id": "wl_abc123",
  "name": "data-processing",
  "priority": "high",
  "cpu_limit": 4.0,
  "updated_at": "2024-01-01T12:05:00Z"
}
```

#### DELETE /workloads/{workload_id}

Delete workload.

**Response (204):** No content

**Errors:**
- `404 Not Found`: Workload not found
- `409 Conflict`: Cannot delete running workload

#### POST /workloads/{workload_id}/schedule

Schedule workload for execution.

**Request (optional):**
```json
{
  "use_ai": true,
  "scheduled_time": "2024-01-01T14:00:00Z"
}
```

**Response (200):**
```json
{
  "id": "wl_abc123",
  "status": "scheduled",
  "scheduled_at": "2024-01-01T14:00:00Z",
  "ai_recommendation": {
    "optimal_time": "2024-01-01T14:00:00Z",
    "reason": "Low system load predicted"
  }
}
```

#### POST /workloads/{workload_id}/cancel

Cancel running or scheduled workload.

**Response (200):**
```json
{
  "id": "wl_abc123",
  "status": "cancelled",
  "cancelled_at": "2024-01-01T12:10:00Z"
}
```

#### GET /workloads/{workload_id}/logs

Get workload execution logs.

**Query Parameters:**
- `tail` (optional): Number of lines from end (default: 100)
- `follow` (optional): Stream logs (boolean)

**Response (200):**
```json
{
  "workload_id": "wl_abc123",
  "logs": "Starting process...\nProcessing data...\nComplete.",
  "lines": 3,
  "truncated": false
}
```

---

### Containers

#### GET /containers

List all containers.

**Query Parameters:**
- `status` (optional): Filter by status (running, stopped, paused, exited)
- `all` (optional): Include stopped containers (boolean)

**Response (200):**
```json
[
  {
    "id": "cont_xyz789",
    "name": "workload-container",
    "image": "python:3.14",
    "status": "running",
    "created_at": "2024-01-01T12:00:00Z",
    "ports": {"8080": "8080"},
    "workload_id": "wl_abc123"
  }
]
```

#### GET /containers/{container_id}

Get container details.

**Response (200):**
```json
{
  "id": "cont_xyz789",
  "name": "workload-container",
  "image": "python:3.14",
  "status": "running",
  "created_at": "2024-01-01T12:00:00Z",
  "started_at": "2024-01-01T12:01:00Z",
  "state": {
    "status": "running",
    "running": true,
    "paused": false,
    "pid": 12345
  },
  "config": {
    "cpu_limit": 2.0,
    "memory_limit": 1024,
    "environment": {"ENV": "value"}
  }
}
```

#### POST /containers/{container_id}/start

Start stopped container.

**Response (200):**
```json
{
  "id": "cont_xyz789",
  "status": "running",
  "started_at": "2024-01-01T12:15:00Z"
}
```

#### POST /containers/{container_id}/stop

Stop running container.

**Request (optional):**
```json
{
  "timeout": 10
}
```

**Response (200):**
```json
{
  "id": "cont_xyz789",
  "status": "stopped",
  "stopped_at": "2024-01-01T12:20:00Z"
}
```

#### POST /containers/{container_id}/restart

Restart container.

**Response (200):**
```json
{
  "id": "cont_xyz789",
  "status": "running",
  "restarted_at": "2024-01-01T12:25:00Z"
}
```

#### POST /containers/{container_id}/pause

Pause running container.

**Response (200):**
```json
{
  "id": "cont_xyz789",
  "status": "paused",
  "paused_at": "2024-01-01T12:30:00Z"
}
```

#### POST /containers/{container_id}/unpause

Unpause paused container.

**Response (200):**
```json
{
  "id": "cont_xyz789",
  "status": "running",
  "unpaused_at": "2024-01-01T12:35:00Z"
}
```

#### DELETE /containers/{container_id}

Delete container.

**Query Parameters:**
- `force` (optional): Force delete running container (boolean)

**Response (204):** No content

#### GET /containers/{container_id}/logs

Get container logs.

**Query Parameters:**
- `tail` (optional): Number of lines (default: 100)
- `follow` (optional): Stream logs (boolean)
- `timestamps` (optional): Include timestamps (boolean)

**Response (200):**
```json
{
  "container_id": "cont_xyz789",
  "logs": "2024-01-01 12:00:00 Starting...\n2024-01-01 12:00:01 Running...",
  "lines": 2
}
```

#### GET /containers/{container_id}/stats

Get container resource statistics.

**Response (200):**
```json
{
  "container_id": "cont_xyz789",
  "cpu_percent": 45.5,
  "memory_usage": 512000000,
  "memory_limit": 1024000000,
  "memory_percent": 50.0,
  "network_rx": 1024000,
  "network_tx": 512000,
  "block_read": 2048000,
  "block_write": 1024000,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### Subsystems

#### GET /subsystems

List all z/OS subsystems.

**Response (200):**
```json
[
  {
    "name": "jes",
    "display_name": "JES (Job Entry Subsystem)",
    "status": "active",
    "uptime": 3600
  },
  {
    "name": "cics",
    "display_name": "CICS",
    "status": "active",
    "uptime": 3600
  }
]
```

#### GET /subsystems/{subsystem_name}

Get subsystem status.

**Subsystem Names:** `jes`, `cics`, `db2`, `tso`

**Response (200) - JES:**
```json
{
  "subsystem": "jes",
  "status": "active",
  "uptime": 3600,
  "active_jobs": 5,
  "total_jobs": 100,
  "spool_usage": 45.5,
  "jobs": [
    {
      "job_id": "JOB00001",
      "name": "BATCH001",
      "status": "running",
      "priority": "normal"
    }
  ]
}
```

**Response (200) - CICS:**
```json
{
  "subsystem": "cics",
  "status": "active",
  "uptime": 3600,
  "active_transactions": 10,
  "total_transactions": 1000,
  "response_time_avg": 0.05
}
```

#### POST /subsystems/{subsystem_name}/start

Start subsystem.

**Response (200):**
```json
{
  "subsystem": "jes",
  "status": "active",
  "started_at": "2024-01-01T12:00:00Z"
}
```

#### POST /subsystems/{subsystem_name}/stop

Stop subsystem.

**Response (200):**
```json
{
  "subsystem": "jes",
  "status": "stopped",
  "stopped_at": "2024-01-01T12:00:00Z"
}
```

#### GET /subsystems/{subsystem_name}/logs

Get subsystem logs.

**Response (200):**
```json
{
  "subsystem": "jes",
  "logs": "JES started\nJob submitted\nJob completed",
  "lines": 3
}
```

---

### Metrics

#### GET /metrics

Get system metrics.

**Query Parameters:**
- `range` (optional): Time range (1h, 6h, 24h, 7d, 30d)

**Response (200):**
```json
{
  "cpu": {
    "current": 45.5,
    "average": 42.0,
    "history": [40.0, 42.0, 45.5]
  },
  "memory": {
    "current": 60.0,
    "average": 58.5,
    "total": 16384,
    "used": 9830,
    "history": [55.0, 58.0, 60.0]
  },
  "disk": {
    "usage": 70.0,
    "total": 1000000,
    "used": 700000,
    "free": 300000
  },
  "network": {
    "throughput": 125.5,
    "inbound": 100.0,
    "outbound": 25.5,
    "inbound_history": [90.0, 95.0, 100.0],
    "outbound_history": [20.0, 22.0, 25.5]
  },
  "workloads": {
    "running": 5,
    "pending": 2,
    "completed": 100,
    "failed": 3
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### Administration

#### GET /admin/users

List all users (admin only).

**Response (200):**
```json
[
  {
    "id": "user123",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

#### POST /admin/users

Create new user (admin only).

**Request:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "role": "user"
}
```

**Response (201):**
```json
{
  "id": "user456",
  "username": "newuser",
  "email": "user@example.com",
  "role": "user",
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### PUT /admin/users/{user_id}

Update user (admin only).

**Request:**
```json
{
  "role": "admin",
  "is_active": true
}
```

**Response (200):**
```json
{
  "id": "user456",
  "username": "newuser",
  "role": "admin",
  "is_active": true,
  "updated_at": "2024-01-01T12:00:00Z"
}
```

#### DELETE /admin/users/{user_id}

Delete user (admin only).

**Response (204):** No content

#### GET /admin/system

Get system information (admin only).

**Response (200):**
```json
{
  "version": "1.0.0",
  "os": "Linux",
  "architecture": "x86_64",
  "kernel": "5.15.0",
  "cpu_cores": 8,
  "total_memory": 16384,
  "disk_space": 1000000,
  "uptime": 86400,
  "python_version": "3.14.0",
  "podman_version": "4.5.0",
  "ollama_version": "0.1.0"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success with no response body
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

API requests are rate limited:
- **Per Minute**: 60 requests
- **Per Hour**: 1000 requests

Rate limit headers:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `limit`: Items per page (default: 20, max: 100)
- `offset`: Number of items to skip (default: 0)

**Response Headers:**
```http
X-Total-Count: 150
X-Page-Size: 20
X-Page-Offset: 0
```

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws?token=<access_token>');
```

### Events

**Workload Status Update:**
```json
{
  "event": "workload.status",
  "data": {
    "workload_id": "wl_abc123",
    "status": "running",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

**Metrics Update:**
```json
{
  "event": "metrics.update",
  "data": {
    "cpu": 45.5,
    "memory": 60.0,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## SDK Examples

### Python

```python
import requests

# Login
response = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    json={'username': 'admin', 'password': 'admin123'}
)
token = response.json()['access_token']

# Create workload
headers = {'Authorization': f'Bearer {token}'}
response = requests.post(
    'http://localhost:8000/api/v1/workloads',
    json={
        'name': 'test-workload',
        'type': 'batch',
        'image': 'python:3.14',
        'command': 'python script.py'
    },
    headers=headers
)
workload = response.json()
```

### JavaScript

```javascript
// Login
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'admin', password: 'admin123'})
});
const {access_token} = await response.json();

// Create workload
const workloadResponse = await fetch('http://localhost:8000/api/v1/workloads', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'test-workload',
    type: 'batch',
    image: 'python:3.14',
    command: 'python script.py'
  })
});
const workload = await workloadResponse.json();
```

## Next Steps

- See [CLI_GUIDE.md](CLI_GUIDE.md) for CLI usage
- Check [UI_GUIDE.md](UI_GUIDE.md) for UI documentation
- Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for issues
