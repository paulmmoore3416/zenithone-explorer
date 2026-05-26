# ZenithOne Explorer - UI User Guide

Complete user guide for the ZenithOne Explorer web interface.

## Table of Contents

- [Accessing the UI](#accessing-the-ui)
- [Login](#login)
- [Dashboard](#dashboard)
- [Workloads](#workloads)
- [Containers](#containers)
- [Subsystems](#subsystems)
- [Metrics](#metrics)
- [Admin Panel](#admin-panel)
- [User Settings](#user-settings)
- [Keyboard Shortcuts](#keyboard-shortcuts)

## Accessing the UI

### Default Access

Open your web browser and navigate to:
```
http://localhost:8000
```

### First Time Setup

1. Ensure the backend is running
2. Navigate to the login page
3. Use default credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
4. Change password after first login (recommended)

## Login

### Login Page

![Login Page](../assets/screenshots/login.png)

**Features:**
- Username/email input
- Password input (hidden)
- "Remember me" checkbox
- "Forgot password" link
- Registration link

**Steps:**
1. Enter your username or email
2. Enter your password
3. (Optional) Check "Remember me" to stay logged in
4. Click "Login" button

**Troubleshooting:**
- **Invalid credentials**: Verify username and password
- **Account locked**: Contact administrator
- **Connection error**: Check if backend is running

## Dashboard

### Overview

The dashboard provides a real-time overview of your ZenithOne system.

![Dashboard](../assets/screenshots/dashboard.png)

### Components

#### 1. System Status Cards

**CPU Usage**
- Current CPU utilization percentage
- Color-coded indicator (green/yellow/red)
- Historical trend sparkline

**Memory Usage**
- Current memory utilization
- Total/used/free memory display
- Visual progress bar

**Active Workloads**
- Count of running workloads
- Quick status breakdown
- Link to workloads page

**Containers**
- Total container count
- Running/stopped status
- Quick actions menu

#### 2. Real-Time Charts

**CPU History Chart**
- Line chart showing CPU usage over time
- Last 50 data points
- Auto-refresh every 10 seconds
- Hover for exact values

**Memory History Chart**
- Line chart showing memory usage
- Percentage and absolute values
- Color-coded thresholds

**Network Throughput**
- Dual-line chart (inbound/outbound)
- Real-time bandwidth monitoring
- Units: MB/s

#### 3. Recent Activity

**Activity Feed**
- Latest workload submissions
- Container state changes
- System events
- User actions

**Format:**
```
[Timestamp] [Event Type] [Description]
12:34:56    Workload     "data-processing" started
12:35:12    Container    "cont_abc123" stopped
```

#### 4. Quick Actions

- **Create Workload**: Opens workload creation dialog
- **View Metrics**: Navigate to metrics page
- **System Info**: Display system information
- **Refresh**: Manual refresh of dashboard data

### Auto-Refresh

Dashboard automatically refreshes every 10 seconds. You can:
- Pause auto-refresh (click pause icon)
- Manually refresh (click refresh icon)
- Adjust refresh interval in settings

## Workloads

### Workload List

![Workloads Page](../assets/screenshots/workloads.png)

**Table Columns:**
- **ID**: Unique workload identifier
- **Name**: Workload name
- **Type**: batch, interactive, service, scheduled
- **Status**: pending, running, completed, failed, cancelled
- **Priority**: low, normal, high, critical
- **Created**: Creation timestamp
- **Actions**: Quick action buttons

**Filters:**
- Status filter (dropdown)
- Type filter (dropdown)
- Priority filter (dropdown)
- Search by name (text input)

**Sorting:**
- Click column headers to sort
- Ascending/descending toggle

### Create Workload

**Steps:**
1. Click "Create Workload" button
2. Fill in the form:
   - **Name**: Unique workload name
   - **Type**: Select workload type
   - **Image**: Container image (e.g., `python:3.14`)
   - **Command**: Command to execute
   - **Priority**: Select priority level
   - **CPU Limit**: CPU cores (e.g., 2.0)
   - **Memory Limit**: Memory in MB (e.g., 1024)
3. (Optional) Add environment variables
4. (Optional) Add volume mounts
5. Click "Create" button

**Example:**
```
Name: data-processing
Type: batch
Image: python:3.14
Command: python process.py
Priority: high
CPU: 2.0
Memory: 1024
```

### Workload Details

Click on a workload to view details:

**Information Tabs:**

1. **Overview**
   - Status and progress
   - Resource usage
   - Execution time
   - Exit code (if completed)

2. **Configuration**
   - Image and command
   - Resource limits
   - Environment variables
   - Volume mounts

3. **Logs**
   - Real-time log streaming
   - Search and filter logs
   - Download logs
   - Auto-scroll toggle

4. **Metrics**
   - CPU usage chart
   - Memory usage chart
   - Network I/O
   - Disk I/O

**Actions:**
- **Schedule**: Schedule workload execution
- **Cancel**: Cancel running workload
- **Delete**: Delete workload
- **Clone**: Create copy of workload
- **Export**: Export workload configuration

### Schedule Workload

**Options:**

1. **Immediate Scheduling**
   - Click "Schedule Now"
   - Workload starts immediately

2. **AI-Optimized Scheduling**
   - Click "Schedule with AI"
   - AI determines optimal execution time
   - Shows recommendation and reasoning

3. **Custom Time**
   - Select date and time
   - Set timezone
   - Click "Schedule"

## Containers

### Container List

![Containers Page](../assets/screenshots/containers.png)

**Table Columns:**
- **ID**: Container identifier
- **Name**: Container name
- **Image**: Container image
- **Status**: running, stopped, paused, exited
- **Created**: Creation timestamp
- **Ports**: Port mappings
- **Actions**: Control buttons

**Status Indicators:**
- 🟢 Running
- 🔴 Stopped
- 🟡 Paused
- ⚫ Exited

### Container Actions

**Start Container**
1. Click "Start" button
2. Container starts immediately
3. Status updates to "running"

**Stop Container**
1. Click "Stop" button
2. Confirm action (if enabled)
3. Container stops gracefully
4. Status updates to "stopped"

**Restart Container**
1. Click "Restart" button
2. Container stops and starts
3. Brief downtime during restart

**Pause/Unpause**
1. Click "Pause" button
2. Container freezes (preserves state)
3. Click "Unpause" to resume

**Delete Container**
1. Click "Delete" button
2. Confirm deletion
3. Container removed permanently

### Container Details

**Information Tabs:**

1. **Overview**
   - Container state
   - Uptime
   - Resource usage
   - Network information

2. **Logs**
   - Real-time log viewer
   - Timestamp toggle
   - Search functionality
   - Download logs

3. **Stats**
   - Live resource monitoring
   - CPU usage graph
   - Memory usage graph
   - Network I/O graph
   - Disk I/O graph

4. **Inspect**
   - Full container configuration
   - JSON format
   - Copy to clipboard
   - Export to file

## Subsystems

### Subsystem Overview

![Subsystems Page](../assets/screenshots/subsystems.png)

ZenithOne simulates four z/OS subsystems:

#### 1. JES (Job Entry Subsystem)

**Status Card:**
- Active/Inactive indicator
- Uptime
- Active jobs count
- Spool usage

**Actions:**
- Start/Stop subsystem
- View logs
- View job queue

**Job Queue:**
- Job ID
- Job name
- Status
- Priority
- Submission time

#### 2. CICS (Customer Information Control System)

**Status Card:**
- Active/Inactive indicator
- Uptime
- Active transactions
- Response time average

**Actions:**
- Start/Stop subsystem
- View logs
- View transaction stats

#### 3. DB2 (Database Management System)

**Status Card:**
- Active/Inactive indicator
- Uptime
- Active connections
- Query performance

**Actions:**
- Start/Stop subsystem
- View logs
- View connection pool

#### 4. TSO (Time Sharing Option)

**Status Card:**
- Active/Inactive indicator
- Uptime
- Active sessions
- Session timeout

**Actions:**
- Start/Stop subsystem
- View logs
- View active sessions

### Subsystem Control

**Start Subsystem:**
1. Click "Start" button on subsystem card
2. Subsystem initializes
3. Status updates to "Active"

**Stop Subsystem:**
1. Click "Stop" button
2. Confirm action
3. Subsystem shuts down gracefully
4. Status updates to "Inactive"

**View Logs:**
1. Click "Logs" button
2. Log viewer opens
3. Real-time log streaming
4. Search and filter capabilities

## Metrics

### System Metrics

![Metrics Page](../assets/screenshots/metrics.png)

**Time Range Selector:**
- Last 1 hour
- Last 6 hours
- Last 24 hours
- Last 7 days
- Last 30 days
- Custom range

**Metric Categories:**

#### 1. CPU Metrics
- Overall CPU usage
- Per-core usage
- Load average
- Historical trends

#### 2. Memory Metrics
- Total memory
- Used memory
- Free memory
- Cached memory
- Swap usage

#### 3. Disk Metrics
- Disk usage by volume
- Read/write operations
- I/O wait time
- Disk throughput

#### 4. Network Metrics
- Inbound traffic
- Outbound traffic
- Packet statistics
- Connection count

#### 5. Workload Metrics
- Total workloads
- Running workloads
- Completed workloads
- Failed workloads
- Average execution time

### Export Metrics

**Export Options:**
1. Click "Export" button
2. Select format:
   - CSV
   - JSON
   - PDF Report
3. Select time range
4. Click "Download"

## Admin Panel

### User Management

![Admin Page](../assets/screenshots/admin.png)

**User List:**
- Username
- Email
- Role (admin/user)
- Status (active/inactive)
- Last login
- Actions

**Create User:**
1. Click "Create User" button
2. Fill in form:
   - Username
   - Email
   - Password
   - Role
3. Click "Create"

**Edit User:**
1. Click "Edit" button on user row
2. Modify fields
3. Click "Save"

**Delete User:**
1. Click "Delete" button
2. Confirm deletion
3. User removed

**Reset Password:**
1. Click "Reset Password" button
2. Enter new password
3. Click "Reset"

### System Configuration

**Configuration Editor:**
- View current configuration
- Edit configuration values
- Validate changes
- Apply configuration
- Restart services if needed

**Configuration Categories:**
- API settings
- Database settings
- Security settings
- Performance settings
- Logging settings

### System Information

**Display:**
- ZenithOne version
- Operating system
- Python version
- Podman version
- Ollama version
- System uptime
- Resource totals

## User Settings

### Profile Settings

**Edit Profile:**
1. Click user icon (top-right)
2. Select "Profile"
3. Edit fields:
   - Display name
   - Email
   - Avatar
4. Click "Save"

**Change Password:**
1. Go to Profile
2. Click "Change Password"
3. Enter current password
4. Enter new password
5. Confirm new password
6. Click "Update"

### Preferences

**UI Preferences:**
- Theme (light/dark)
- Language
- Timezone
- Date format
- Auto-refresh interval

**Notification Preferences:**
- Email notifications
- Browser notifications
- Notification types
- Notification frequency

## Keyboard Shortcuts

### Global Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + /` | Show shortcuts help |
| `Ctrl + K` | Quick search |
| `Ctrl + R` | Refresh current page |
| `Esc` | Close modal/dialog |

### Navigation Shortcuts

| Shortcut | Action |
|----------|--------|
| `G + D` | Go to Dashboard |
| `G + W` | Go to Workloads |
| `G + C` | Go to Containers |
| `G + S` | Go to Subsystems |
| `G + M` | Go to Metrics |
| `G + A` | Go to Admin (admin only) |

### Workload Shortcuts

| Shortcut | Action |
|----------|--------|
| `N` | New workload |
| `R` | Refresh list |
| `F` | Focus search |
| `/` | Quick filter |

### Container Shortcuts

| Shortcut | Action |
|----------|--------|
| `S` | Start selected |
| `T` | Stop selected |
| `P` | Pause selected |
| `D` | Delete selected |

## Tips and Tricks

### Performance Tips

1. **Reduce Auto-Refresh Frequency**: For slower systems, increase refresh interval
2. **Use Filters**: Filter large lists to improve performance
3. **Close Unused Tabs**: Keep only necessary browser tabs open
4. **Clear Browser Cache**: Periodically clear cache for better performance

### Productivity Tips

1. **Use Keyboard Shortcuts**: Navigate faster with keyboard
2. **Bookmark Frequently Used Pages**: Quick access to common tasks
3. **Use Quick Search**: Find workloads/containers quickly
4. **Set Up Notifications**: Stay informed of important events

### Troubleshooting Tips

1. **Check Browser Console**: Press F12 for error messages
2. **Verify Backend Connection**: Check if API is accessible
3. **Clear Browser Cache**: Resolve display issues
4. **Try Incognito Mode**: Test without extensions
5. **Check Network Tab**: Identify failed requests

## Browser Compatibility

**Supported Browsers:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Recommended:**
- Chrome (latest version)
- Firefox (latest version)

## Mobile Access

The UI is responsive and works on mobile devices:

**Supported:**
- iOS Safari 14+
- Chrome Mobile 90+
- Firefox Mobile 88+

**Note:** Some features may have limited functionality on mobile devices.

## Next Steps

- Review [CLI_GUIDE.md](CLI_GUIDE.md) for command-line usage
- Check [API_REFERENCE.md](API_REFERENCE.md) for API integration
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
