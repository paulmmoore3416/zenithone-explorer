# Your First Workload - Complete Tutorial

This tutorial walks you through creating, scheduling, and monitoring your first real workload on ZenithOne Explorer.

## What You'll Learn

- Creating a workload from scratch
- Understanding workload configuration
- Scheduling with AI optimization
- Monitoring workload execution
- Viewing logs and metrics
- Troubleshooting common issues

## Prerequisites

- ZenithOne Explorer installed and running
- Backend server running on `http://localhost:8000`
- CLI installed and configured
- Logged in as a user

## Tutorial Overview

We'll create a Python data processing workload that:
1. Reads sample data
2. Processes the data
3. Generates a report
4. Saves results to a file

**Estimated Time:** 15 minutes

## Step 1: Prepare Your Script

First, let's create a simple Python script that our workload will execute.

### Create the Script

```bash
# Create a directory for our workload
mkdir -p ~/zenithone-workloads/data-processor
cd ~/zenithone-workloads/data-processor

# Create the Python script
cat > process_data.py << 'EOF'
#!/usr/bin/env python3
"""
Simple data processing script for ZenithOne tutorial
"""
import json
import time
from datetime import datetime

def process_data():
    """Process sample data and generate report."""
    print(f"[{datetime.now()}] Starting data processing...")
    
    # Simulate data loading
    print("Loading data...")
    time.sleep(2)
    
    # Sample data
    data = {
        "records": 1000,
        "processed": 0,
        "errors": 0
    }
    
    # Simulate processing
    print("Processing records...")
    for i in range(1, 11):
        time.sleep(1)
        data["processed"] = i * 100
        print(f"Progress: {data['processed']}/{data['records']} records")
    
    # Generate report
    print("Generating report...")
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_records": data["records"],
        "processed_records": data["processed"],
        "error_count": data["errors"],
        "success_rate": 100.0,
        "processing_time": "12 seconds"
    }
    
    # Save report
    with open("/tmp/report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"[{datetime.now()}] Processing complete!")
    print(f"Report saved to: /tmp/report.json")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    process_data()
EOF

# Make it executable
chmod +x process_data.py
```

### Test the Script Locally

```bash
# Test the script
python3 process_data.py
```

You should see output like:
```
[2024-01-01 12:00:00] Starting data processing...
Loading data...
Processing records...
Progress: 100/1000 records
Progress: 200/1000 records
...
[2024-01-01 12:00:12] Processing complete!
```

## Step 2: Create the Workload

Now let's create a workload in ZenithOne to run this script.

### Method 1: Using CLI (Recommended)

```bash
# Create workload with inline command
zenith workload create \
  --name data-processor \
  --type batch \
  --image python:3.14 \
  --command "python3 -c '
import json
import time
from datetime import datetime

print(f\"[{datetime.now()}] Starting data processing...\")
print(\"Loading data...\")
time.sleep(2)

data = {\"records\": 1000, \"processed\": 0, \"errors\": 0}

print(\"Processing records...\")
for i in range(1, 11):
    time.sleep(1)
    data[\"processed\"] = i * 100
    print(f\"Progress: {data[\"processed\"]}/{data[\"records\"]} records\")

print(\"Generating report...\")
report = {
    \"timestamp\": datetime.now().isoformat(),
    \"total_records\": data[\"records\"],
    \"processed_records\": data[\"processed\"],
    \"error_count\": data[\"errors\"],
    \"success_rate\": 100.0,
    \"processing_time\": \"12 seconds\"
}

print(f\"[{datetime.now()}] Processing complete!\")
print(json.dumps(report, indent=2))
'" \
  --priority normal \
  --cpu 1.0 \
  --memory 512
```

**Save the workload ID** from the output:
```
✓ Workload created successfully
ID: wl_abc123
Name: data-processor
Status: pending
```

### Method 2: Using Configuration File

Create a workload configuration file:

```bash
cat > workload-config.json << 'EOF'
{
  "name": "data-processor",
  "type": "batch",
  "image": "python:3.14",
  "command": "python3 -c 'import json, time; from datetime import datetime; ...'",
  "priority": "normal",
  "cpu_limit": 1.0,
  "memory_limit": 512,
  "environment": {
    "PYTHONUNBUFFERED": "1"
  }
}
EOF

# Create workload from file
zenith workload create --file workload-config.json
```

### Method 3: Using Web UI

1. Open browser: `http://localhost:8000`
2. Navigate to "Workloads" page
3. Click "Create Workload" button
4. Fill in the form:
   - **Name**: `data-processor`
   - **Type**: `batch`
   - **Image**: `python:3.14`
   - **Command**: (paste the Python script)
   - **Priority**: `normal`
   - **CPU**: `1.0`
   - **Memory**: `512`
5. Click "Create"

## Step 3: Verify Workload Creation

```bash
# View workload details
zenith workload get wl_abc123

# Or list all workloads
zenith workload list
```

You should see:
```
ID: wl_abc123
Name: data-processor
Type: batch
Status: pending
Priority: normal
CPU Limit: 1.0
Memory Limit: 512 MB
Created: 2024-01-01 12:00:00
```

## Step 4: Schedule the Workload

Now let's schedule the workload for execution.

### Option A: Immediate Scheduling

```bash
zenith workload schedule wl_abc123
```

### Option B: AI-Optimized Scheduling

```bash
zenith workload schedule wl_abc123 --use-ai
```

The AI will analyze:
- Current system load
- Available resources
- Historical patterns
- Workload priority

And provide a recommendation:
```
✓ AI Recommendation:
  Optimal Time: 2024-01-01 14:30:00
  Reason: Low system load predicted, optimal resource availability
  Confidence: 95%

Schedule now? (y/n):
```

### Option C: Custom Time

```bash
zenith workload schedule wl_abc123 --at "2024-01-01 14:00:00"
```

## Step 5: Monitor Execution

### Real-Time Monitoring

```bash
# Watch workload status (auto-refresh)
zenith workload get wl_abc123 --watch
```

You'll see status updates:
```
Status: pending → scheduled → running → completed
```

### View Live Logs

```bash
# Stream logs in real-time
zenith workload logs wl_abc123 --follow
```

Output:
```
[2024-01-01 12:00:00] Starting data processing...
Loading data...
Processing records...
Progress: 100/1000 records
Progress: 200/1000 records
...
[2024-01-01 12:00:12] Processing complete!
```

### Check Container Status

```bash
# Find the container
zenith container list --all

# View container details
zenith container get cont_xyz789

# View container stats
zenith container stats cont_xyz789
```

## Step 6: View Results

### Check Workload Status

```bash
zenith workload get wl_abc123
```

Expected output:
```
ID: wl_abc123
Name: data-processor
Type: batch
Status: completed
Exit Code: 0
Started: 2024-01-01 12:00:00
Completed: 2024-01-01 12:00:12
Duration: 12 seconds
```

### View Complete Logs

```bash
# View all logs
zenith workload logs wl_abc123

# Save logs to file
zenith workload logs wl_abc123 > workload-logs.txt
```

### View Metrics

```bash
# View workload metrics
zenith metrics workload wl_abc123
```

Output:
```
CPU Usage:
  Average: 45.5%
  Peak: 78.2%

Memory Usage:
  Average: 256 MB
  Peak: 384 MB

Execution Time: 12 seconds
```

## Step 7: Analyze Performance

### Using CLI

```bash
# View detailed metrics
zenith metrics workload wl_abc123 --range 1h --output json
```

### Using Web UI

1. Navigate to "Workloads" page
2. Click on your workload
3. Go to "Metrics" tab
4. View charts:
   - CPU usage over time
   - Memory usage over time
   - Network I/O
   - Disk I/O

## Common Issues and Solutions

### Issue 1: Workload Stuck in Pending

**Problem:** Workload stays in "pending" status

**Solution:**
```bash
# Check if workload is scheduled
zenith workload get wl_abc123

# Schedule it
zenith workload schedule wl_abc123

# Check system resources
zenith metrics system
```

### Issue 2: Container Fails to Start

**Problem:** Workload fails immediately

**Solution:**
```bash
# Check logs for errors
zenith workload logs wl_abc123

# Common issues:
# - Invalid image name
# - Syntax error in command
# - Insufficient resources

# Fix and recreate workload
zenith workload delete wl_abc123
zenith workload create --name data-processor ...
```

### Issue 3: Out of Memory

**Problem:** Container killed due to memory limit

**Solution:**
```bash
# Increase memory limit
zenith workload update wl_abc123 --memory 1024

# Or recreate with higher limit
zenith workload create \
  --name data-processor \
  --memory 1024 \
  ...
```

### Issue 4: Slow Execution

**Problem:** Workload takes too long

**Solution:**
```bash
# Increase CPU allocation
zenith workload update wl_abc123 --cpu 2.0

# Check system load
zenith metrics system

# Use AI scheduling for optimal time
zenith workload schedule wl_abc123 --use-ai
```

## Advanced: Workload with Volume Mounts

Let's create a workload that reads from and writes to host filesystem:

```bash
# Create data directory
mkdir -p ~/zenithone-data/input
mkdir -p ~/zenithone-data/output

# Create input file
echo "Sample data" > ~/zenithone-data/input/data.txt

# Create workload with volumes
zenith workload create \
  --name file-processor \
  --type batch \
  --image python:3.14 \
  --command "python3 -c '
with open(\"/data/input/data.txt\", \"r\") as f:
    data = f.read()
    
with open(\"/data/output/result.txt\", \"w\") as f:
    f.write(f\"Processed: {data.upper()}\")
    
print(\"File processed successfully\")
'" \
  --volume ~/zenithone-data/input:/data/input \
  --volume ~/zenithone-data/output:/data/output

# Schedule and run
zenith workload schedule <workload-id>

# Check output
cat ~/zenithone-data/output/result.txt
```

## Next Steps

Congratulations! You've successfully:
- ✅ Created a workload
- ✅ Scheduled execution
- ✅ Monitored progress
- ✅ Viewed logs and metrics
- ✅ Analyzed results

### Continue Learning

1. **Try Different Workload Types**
   - Interactive workloads
   - Long-running services
   - Scheduled jobs

2. **Explore Advanced Features**
   - Environment variables
   - Volume mounts
   - Network configuration
   - Resource limits

3. **Use AI Features**
   - AI-optimized scheduling
   - Resource prediction
   - Anomaly detection

4. **Integrate with Your Workflow**
   - Create custom scripts
   - Automate deployments
   - Build CI/CD pipelines

### Additional Resources

- [CLI Guide](../CLI_GUIDE.md) - Complete CLI reference
- [API Reference](../API_REFERENCE.md) - REST API documentation
- [Configuration Guide](../CONFIGURATION.md) - Advanced settings
- [FAQ](FAQ.md) - Frequently asked questions

## Quick Reference

```bash
# Create workload
zenith workload create --name <name> --type <type> --image <image> --command "<cmd>"

# Schedule workload
zenith workload schedule <id>
zenith workload schedule <id> --use-ai

# Monitor workload
zenith workload get <id> --watch
zenith workload logs <id> --follow

# View metrics
zenith metrics workload <id>

# Manage workload
zenith workload cancel <id>
zenith workload delete <id>
```

Happy workload processing! 🚀
