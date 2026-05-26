# ZenithOne Explorer - API Design Specification

## API Overview

**Base URL**: `http://localhost:8080/api/v1`  
**Protocol**: HTTP/HTTPS  
**Authentication**: JWT Bearer Token  
**Content-Type**: `application/json`  
**API Version**: 1.0.0

---

## Authentication

### POST /auth/login
Authenticate user and receive JWT token.

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "username": "string",
    "role": "admin|user|viewer"
  }
}
```

**Errors**:
- 401: Invalid credentials
- 429: Too many login attempts

---

### POST /auth/refresh
Refresh expired JWT token.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "access_token": "string",
  "expires_in": 3600
}
```

---

### POST /auth/logout
Invalidate current token.

**Headers**: `Authorization: Bearer <token>`

**Response** (204 No Content)

---

## Workload Management

### GET /workloads
List all workloads with filtering and pagination.

**Query Parameters**:
- `status` (optional): `pending|running|completed|failed`
- `priority` (optional): `low|medium|high|critical`
- `limit` (optional, default: 50): Number of results
- `offset` (optional, default: 0): Pagination offset
- `sort` (optional, default: `created_at`): Sort field
- `order` (optional, default: `desc`): `asc|desc`

**Response** (200 OK):
```json
{
  "total": 150,
  "limit": 50,
  "offset": 0,
  "workloads": [
    {
      "id": "uuid",
      "name": "string",
      "type": "batch|transaction|interactive",
      "status": "pending|running|completed|failed",
      "priority": "low|medium|high|critical",
      "created_at": "2026-05-26T21:00:00Z",
      "started_at": "2026-05-26T21:01:00Z",
      "completed_at": "2026-05-26T21:05:00Z",
      "duration": 240,
      "cpu_usage": 45.2,
      "memory_usage": 512,
      "owner": "username",
      "subsystem": "JES|CICS|TSO"
    }
  ]
}
```

---

### POST /workloads
Submit a new workload.

**Request Body**:
```json
{
  "name": "string",
  "type": "batch|transaction|interactive",
  "priority": "low|medium|high|critical",
  "subsystem": "JES|CICS|TSO",
  "command": "string",
  "parameters": {
    "key": "value"
  },
  "resources": {
    "cpu_limit": 2,
    "memory_limit": 1024,
    "timeout": 3600
  },
  "schedule": {
    "type": "immediate|scheduled",
    "run_at": "2026-05-26T22:00:00Z"
  }
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "name": "string",
  "status": "pending",
  "created_at": "2026-05-26T21:00:00Z",
  "message": "Workload submitted successfully"
}
```

**Errors**:
- 400: Invalid request body
- 403: Insufficient permissions
- 429: Rate limit exceeded

---

### GET /workloads/{id}
Get detailed information about a specific workload.

**Path Parameters**:
- `id`: Workload UUID

**Response** (200 OK):
```json
{
  "id": "uuid",
  "name": "string",
  "type": "batch",
  "status": "running",
  "priority": "high",
  "created_at": "2026-05-26T21:00:00Z",
  "started_at": "2026-05-26T21:01:00Z",
  "completed_at": null,
  "duration": 120,
  "cpu_usage": 45.2,
  "memory_usage": 512,
  "owner": "username",
  "subsystem": "JES",
  "command": "python script.py",
  "parameters": {},
  "resources": {
    "cpu_limit": 2,
    "memory_limit": 1024,
    "timeout": 3600
  },
  "logs": [
    {
      "timestamp": "2026-05-26T21:01:30Z",
      "level": "INFO",
      "message": "Processing started"
    }
  ],
  "metrics": {
    "cpu_history": [30.5, 35.2, 45.2],
    "memory_history": [256, 384, 512]
  }
}
```

**Errors**:
- 404: Workload not found

---

### PATCH /workloads/{id}
Update workload properties (priority, status).

**Path Parameters**:
- `id`: Workload UUID

**Request Body**:
```json
{
  "priority": "critical",
  "status": "paused"
}
```

**Response** (200 OK):
```json
{
  "id": "uuid",
  "message": "Workload updated successfully"
}
```

---

### DELETE /workloads/{id}
Cancel/delete a workload.

**Path Parameters**:
- `id`: Workload UUID

**Response** (204 No Content)

**Errors**:
- 404: Workload not found
- 409: Cannot delete running workload

---

### GET /workloads/{id}/logs
Stream workload logs in real-time.

**Path Parameters**:
- `id`: Workload UUID

**Query Parameters**:
- `follow` (optional, default: false): Stream logs
- `tail` (optional, default: 100): Number of lines

**Response** (200 OK):
```json
{
  "logs": [
    {
      "timestamp": "2026-05-26T21:01:30Z",
      "level": "INFO",
      "message": "Processing started"
    }
  ]
}
```

---

## Container Management

### GET /containers
List all containers.

**Query Parameters**:
- `status` (optional): `running|stopped|paused`
- `limit` (optional, default: 50)
- `offset` (optional, default: 0)

**Response** (200 OK):
```json
{
  "total": 25,
  "containers": [
    {
      "id": "string",
      "name": "string",
      "image": "string",
      "status": "running|stopped|paused",
      "created_at": "2026-05-26T20:00:00Z",
      "started_at": "2026-05-26T20:01:00Z",
      "ports": ["8080:80", "8443:443"],
      "cpu_usage": 15.5,
      "memory_usage": 256,
      "network_rx": 1024000,
      "network_tx": 512000
    }
  ]
}
```

---

### POST /containers
Create and start a new container.

**Request Body**:
```json
{
  "name": "string",
  "image": "string",
  "command": "string",
  "environment": {
    "KEY": "value"
  },
  "ports": ["8080:80"],
  "volumes": ["/host/path:/container/path"],
  "resources": {
    "cpu_limit": 1,
    "memory_limit": 512
  }
}
```

**Response** (201 Created):
```json
{
  "id": "string",
  "name": "string",
  "status": "running",
  "message": "Container created successfully"
}
```

---

### GET /containers/{id}
Get container details.

**Path Parameters**:
- `id`: Container ID

**Response** (200 OK):
```json
{
  "id": "string",
  "name": "string",
  "image": "string",
  "status": "running",
  "created_at": "2026-05-26T20:00:00Z",
  "started_at": "2026-05-26T20:01:00Z",
  "ports": ["8080:80"],
  "environment": {},
  "volumes": [],
  "resources": {
    "cpu_limit": 1,
    "memory_limit": 512
  },
  "stats": {
    "cpu_usage": 15.5,
    "memory_usage": 256,
    "network_rx": 1024000,
    "network_tx": 512000,
    "block_read": 2048000,
    "block_write": 1024000
  }
}
```

---

### POST /containers/{id}/start
Start a stopped container.

**Response** (200 OK):
```json
{
  "id": "string",
  "status": "running",
  "message": "Container started"
}
```

---

### POST /containers/{id}/stop
Stop a running container.

**Response** (200 OK):
```json
{
  "id": "string",
  "status": "stopped",
  "message": "Container stopped"
}
```

---

### POST /containers/{id}/restart
Restart a container.

**Response** (200 OK):
```json
{
  "id": "string",
  "status": "running",
  "message": "Container restarted"
}
```

---

### DELETE /containers/{id}
Remove a container.

**Query Parameters**:
- `force` (optional, default: false): Force removal

**Response** (204 No Content)

---

### GET /containers/{id}/logs
Get container logs.

**Query Parameters**:
- `follow` (optional): Stream logs
- `tail` (optional, default: 100)
- `since` (optional): Timestamp

**Response** (200 OK):
```json
{
  "logs": "string"
}
```

---

## System Metrics

### GET /metrics
Get current system metrics.

**Response** (200 OK):
```json
{
  "timestamp": "2026-05-26T21:00:00Z",
  "system": {
    "cpu": {
      "usage": 35.5,
      "cores": 16,
      "load_average": [2.5, 2.3, 2.1]
    },
    "memory": {
      "total": 23622320128,
      "used": 3006477312,
      "free": 11811160064,
      "available": 21474836480,
      "usage_percent": 12.7
    },
    "disk": {
      "total": 1978419200000,
      "used": 237304217600,
      "free": 1610612736000,
      "usage_percent": 13
    },
    "network": {
      "bytes_sent": 1024000000,
      "bytes_recv": 2048000000,
      "packets_sent": 1000000,
      "packets_recv": 2000000
    }
  },
  "workloads": {
    "total": 150,
    "running": 5,
    "pending": 10,
    "completed": 130,
    "failed": 5
  },
  "containers": {
    "total": 25,
    "running": 15,
    "stopped": 10
  }
}
```

---

### GET /metrics/history
Get historical metrics data.

**Query Parameters**:
- `metric` (required): `cpu|memory|disk|network`
- `from` (required): Start timestamp
- `to` (required): End timestamp
- `interval` (optional, default: 60): Seconds between data points

**Response** (200 OK):
```json
{
  "metric": "cpu",
  "interval": 60,
  "data": [
    {
      "timestamp": "2026-05-26T20:00:00Z",
      "value": 35.5
    },
    {
      "timestamp": "2026-05-26T20:01:00Z",
      "value": 38.2
    }
  ]
}
```

---

## Subsystem Management

### GET /subsystems
Get status of all z/OS subsystems.

**Response** (200 OK):
```json
{
  "subsystems": [
    {
      "name": "JES",
      "status": "active|inactive|error",
      "uptime": 86400,
      "jobs_processed": 1500,
      "jobs_queued": 10,
      "spool_usage": 45.2
    },
    {
      "name": "CICS",
      "status": "active",
      "uptime": 86400,
      "transactions_processed": 50000,
      "active_transactions": 25,
      "response_time_avg": 150
    },
    {
      "name": "DB2",
      "status": "active",
      "uptime": 86400,
      "queries_executed": 100000,
      "active_connections": 50,
      "cache_hit_ratio": 95.5
    },
    {
      "name": "TSO",
      "status": "active",
      "uptime": 86400,
      "active_sessions": 15,
      "commands_executed": 5000
    }
  ]
}
```

---

### GET /subsystems/{name}
Get detailed subsystem information.

**Path Parameters**:
- `name`: Subsystem name (JES|CICS|DB2|TSO)

**Response** (200 OK):
```json
{
  "name": "JES",
  "status": "active",
  "uptime": 86400,
  "version": "1.0.0",
  "configuration": {
    "max_jobs": 1000,
    "spool_size": 10737418240
  },
  "statistics": {
    "jobs_processed": 1500,
    "jobs_queued": 10,
    "jobs_failed": 5,
    "spool_usage": 45.2,
    "avg_job_duration": 180
  },
  "recent_jobs": [
    {
      "id": "uuid",
      "name": "string",
      "status": "completed",
      "submitted_at": "2026-05-26T20:00:00Z"
    }
  ]
}
```

---

### POST /subsystems/{name}/start
Start a subsystem.

**Response** (200 OK):
```json
{
  "name": "JES",
  "status": "active",
  "message": "Subsystem started successfully"
}
```

---

### POST /subsystems/{name}/stop
Stop a subsystem.

**Response** (200 OK):
```json
{
  "name": "JES",
  "status": "inactive",
  "message": "Subsystem stopped successfully"
}
```

---

### POST /subsystems/{name}/restart
Restart a subsystem.

**Response** (200 OK):
```json
{
  "name": "JES",
  "status": "active",
  "message": "Subsystem restarted successfully"
}
```

---

## Administration

### GET /admin/users
List all users.

**Query Parameters**:
- `role` (optional): Filter by role
- `limit` (optional, default: 50)
- `offset` (optional, default: 0)

**Response** (200 OK):
```json
{
  "total": 25,
  "users": [
    {
      "id": "uuid",
      "username": "string",
      "email": "string",
      "role": "admin|user|viewer",
      "created_at": "2026-05-26T20:00:00Z",
      "last_login": "2026-05-26T21:00:00Z",
      "active": true
    }
  ]
}
```

---

### POST /admin/users
Create a new user.

**Request Body**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "admin|user|viewer"
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "username": "string",
  "message": "User created successfully"
}
```

---

### GET /admin/users/{id}
Get user details.

**Response** (200 OK):
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "role": "admin",
  "created_at": "2026-05-26T20:00:00Z",
  "last_login": "2026-05-26T21:00:00Z",
  "active": true,
  "permissions": ["workload:create", "container:manage"]
}
```

---

### PATCH /admin/users/{id}
Update user properties.

**Request Body**:
```json
{
  "email": "string",
  "role": "admin",
  "active": true
}
```

**Response** (200 OK):
```json
{
  "id": "uuid",
  "message": "User updated successfully"
}
```

---

### DELETE /admin/users/{id}
Delete a user.

**Response** (204 No Content)

---

### GET /admin/config
Get system configuration.

**Response** (200 OK):
```json
{
  "system": {
    "name": "ZenithOne Explorer",
    "version": "1.0.0",
    "environment": "production"
  },
  "security": {
    "jwt_expiration": 3600,
    "rate_limit": 100,
    "password_policy": {
      "min_length": 8,
      "require_uppercase": true,
      "require_numbers": true
    }
  },
  "resources": {
    "max_workloads": 1000,
    "max_containers": 100,
    "default_cpu_limit": 2,
    "default_memory_limit": 1024
  }
}
```

---

### PATCH /admin/config
Update system configuration.

**Request Body**:
```json
{
  "security": {
    "rate_limit": 200
  }
}
```

**Response** (200 OK):
```json
{
  "message": "Configuration updated successfully"
}
```

---

### GET /admin/audit
Get audit logs.

**Query Parameters**:
- `user` (optional): Filter by user
- `action` (optional): Filter by action
- `from` (optional): Start timestamp
- `to` (optional): End timestamp
- `limit` (optional, default: 100)

**Response** (200 OK):
```json
{
  "total": 500,
  "logs": [
    {
      "id": "uuid",
      "timestamp": "2026-05-26T21:00:00Z",
      "user": "username",
      "action": "workload:create",
      "resource": "workload:uuid",
      "ip_address": "192.168.1.100",
      "status": "success|failure",
      "details": {}
    }
  ]
}
```

---

## WebSocket API

### WS /ws/metrics
Real-time system metrics stream.

**Connection**: `ws://localhost:8080/ws/metrics?token=<jwt_token>`

**Message Format**:
```json
{
  "type": "metrics",
  "timestamp": "2026-05-26T21:00:00Z",
  "data": {
    "cpu": 35.5,
    "memory": 12.7,
    "disk": 13.0
  }
}
```

---

### WS /ws/workloads
Real-time workload updates.

**Connection**: `ws://localhost:8080/ws/workloads?token=<jwt_token>`

**Message Format**:
```json
{
  "type": "workload_update",
  "timestamp": "2026-05-26T21:00:00Z",
  "data": {
    "id": "uuid",
    "status": "running",
    "progress": 45.5
  }
}
```

---

### WS /ws/logs/{id}
Real-time log streaming.

**Connection**: `ws://localhost:8080/ws/logs/{id}?token=<jwt_token>`

**Message Format**:
```json
{
  "type": "log",
  "timestamp": "2026-05-26T21:00:00Z",
  "level": "INFO",
  "message": "Processing started"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {},
    "timestamp": "2026-05-26T21:00:00Z"
  }
}
```

### HTTP Status Codes

- **200 OK**: Successful request
- **201 Created**: Resource created
- **204 No Content**: Successful deletion
- **400 Bad Request**: Invalid request
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource conflict
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: Service temporarily unavailable

---

## Rate Limiting

- **Default**: 100 requests per minute per user
- **Admin**: 200 requests per minute
- **Headers**:
  - `X-RateLimit-Limit`: Total requests allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

---

## Versioning

API versioning is handled through the URL path:
- Current: `/api/v1/`
- Future: `/api/v2/`

Breaking changes will result in a new version.

---

## Security

### Authentication
- JWT tokens with 1-hour expiration
- Refresh tokens for extended sessions
- Secure password hashing (bcrypt)

### Authorization
- Role-based access control (RBAC)
- Permissions: `workload:*`, `container:*`, `admin:*`

### HTTPS
- TLS 1.3 required in production
- Certificate validation enforced

### CORS
- Configurable allowed origins
- Credentials support enabled

---

## Performance

### Caching
- Response caching for GET requests
- Cache-Control headers
- ETag support

### Pagination
- Default limit: 50 items
- Maximum limit: 1000 items
- Cursor-based pagination for large datasets

### Compression
- Gzip compression enabled
- Minimum size: 1KB

---

**Last Updated**: 2026-05-26  
**Version**: 1.0.0
