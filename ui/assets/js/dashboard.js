/**
 * ZenithOne Explorer - Dashboard
 * 
 * Dashboard page functionality
 */

let refreshInterval = null;
let performanceChart = null;
let workloadChart = null;

/**
 * Initialize dashboard
 */
document.addEventListener('DOMContentLoaded', async () => {
    await loadDashboardData();
    initializeCharts();
    startAutoRefresh();
});

/**
 * Load all dashboard data
 */
async function loadDashboardData() {
    try {
        await Promise.all([
            loadStats(),
            loadActivity(),
            loadSystemStatus(),
        ]);
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        showNotification('Failed to load dashboard data', 'error');
    }
}

/**
 * Load statistics
 */
async function loadStats() {
    try {
        // Get workloads
        const workloads = await api.listWorkloads({ limit: 1000 });
        const activeWorkloads = workloads.filter(w => w.status === 'running').length;
        document.getElementById('activeWorkloads').textContent = activeWorkloads;
        
        // Get containers
        const containers = await api.listContainers();
        const runningContainers = containers.filter(c => c.status === 'running').length;
        document.getElementById('runningContainers').textContent = runningContainers;
        
        // Get system metrics
        const metrics = await api.getSystemMetrics();
        
        if (metrics.cpu) {
            const cpuUsage = metrics.cpu.usage_percent || 0;
            document.getElementById('cpuUsage').textContent = formatPercentage(cpuUsage);
        }
        
        if (metrics.memory) {
            const memoryUsage = metrics.memory.usage_percent || 0;
            document.getElementById('memoryUsage').textContent = formatPercentage(memoryUsage);
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

/**
 * Load recent activity
 */
async function loadActivity() {
    try {
        // This would typically come from an activity/events API endpoint
        // For now, we'll use workload data as a proxy
        const workloads = await api.listWorkloads({ limit: 10 });
        
        const activityList = document.getElementById('activityList');
        if (!activityList) return;
        
        activityList.innerHTML = '';
        
        workloads.slice(0, 5).forEach(workload => {
            const item = createActivityItem(workload);
            activityList.appendChild(item);
        });
    } catch (error) {
        console.error('Failed to load activity:', error);
    }
}

/**
 * Create activity item element
 */
function createActivityItem(workload) {
    const div = document.createElement('div');
    div.className = 'activity-item';
    
    const iconClass = getActivityIconClass(workload.status);
    const iconType = getActivityIconType(workload.status);
    
    div.innerHTML = `
        <div class="activity-icon ${iconClass}">
            <i class="fas fa-${iconType}"></i>
        </div>
        <div class="activity-details">
            <span class="activity-title">Workload ${workload.name} - ${workload.status}</span>
            <span class="activity-time">${formatRelativeTime(workload.updated_at || workload.created_at)}</span>
        </div>
    `;
    
    return div;
}

/**
 * Get activity icon class based on status
 */
function getActivityIconClass(status) {
    const classMap = {
        'completed': 'success',
        'running': 'info',
        'failed': 'error',
        'pending': 'warning',
    };
    return classMap[status] || 'info';
}

/**
 * Get activity icon type based on status
 */
function getActivityIconType(status) {
    const iconMap = {
        'completed': 'check',
        'running': 'play',
        'failed': 'times',
        'pending': 'clock',
    };
    return iconMap[status] || 'info-circle';
}

/**
 * Load system status
 */
async function loadSystemStatus() {
    try {
        const subsystems = ['jes', 'cics', 'db2', 'tso'];
        
        for (const subsystem of subsystems) {
            try {
                const status = await api.getSubsystemStatus(subsystem);
                updateSubsystemStatus(subsystem, status);
            } catch (error) {
                console.error(`Failed to load ${subsystem} status:`, error);
                updateSubsystemStatus(subsystem, { status: 'offline' });
            }
        }
        
        // Update API server status (if we got here, it's online)
        updateApiServerStatus('online');
    } catch (error) {
        console.error('Failed to load system status:', error);
    }
}

/**
 * Update subsystem status display
 */
function updateSubsystemStatus(subsystem, status) {
    const statusElements = document.querySelectorAll('.status-item');
    
    statusElements.forEach(el => {
        const label = el.querySelector('.status-label');
        if (label && label.textContent.toLowerCase().includes(subsystem)) {
            const indicator = el.querySelector('.status-indicator');
            if (indicator) {
                const isOnline = status.status === 'online' || status.status === 'running';
                indicator.className = `status-indicator ${isOnline ? 'online' : 'offline'}`;
                indicator.innerHTML = `<i class="fas fa-circle"></i> ${isOnline ? 'Online' : 'Offline'}`;
            }
        }
    });
}

/**
 * Update API server status
 */
function updateApiServerStatus(status) {
    const statusElements = document.querySelectorAll('.status-item');
    
    statusElements.forEach(el => {
        const label = el.querySelector('.status-label');
        if (label && label.textContent.includes('API Server')) {
            const indicator = el.querySelector('.status-indicator');
            if (indicator) {
                const isOnline = status === 'online';
                indicator.className = `status-indicator ${isOnline ? 'online' : 'offline'}`;
                indicator.innerHTML = `<i class="fas fa-circle"></i> ${isOnline ? 'Online' : 'Offline'}`;
            }
        }
    });
}

/**
 * Initialize charts
 */
function initializeCharts() {
    initializePerformanceChart();
    initializeWorkloadChart();
}

/**
 * Initialize performance chart
 */
function initializePerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;
    
    performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'CPU Usage',
                    data: [],
                    borderColor: CONFIG.CHART_COLORS.primary,
                    backgroundColor: CONFIG.CHART_COLORS.primary + '20',
                    tension: 0.4,
                },
                {
                    label: 'Memory Usage',
                    data: [],
                    borderColor: CONFIG.CHART_COLORS.secondary,
                    backgroundColor: CONFIG.CHART_COLORS.secondary + '20',
                    tension: 0.4,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#B0B8C4',
                    },
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: '#B0B8C4',
                        callback: (value) => value + '%',
                    },
                    grid: {
                        color: '#2D3548',
                    },
                },
                x: {
                    ticks: {
                        color: '#B0B8C4',
                    },
                    grid: {
                        color: '#2D3548',
                    },
                },
            },
        },
    });
    
    // Load initial data
    updatePerformanceChart();
}

/**
 * Initialize workload chart
 */
function initializeWorkloadChart() {
    const ctx = document.getElementById('workloadChart');
    if (!ctx) return;
    
    workloadChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Running', 'Pending', 'Completed', 'Failed'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: [
                    CONFIG.CHART_COLORS.success,
                    CONFIG.CHART_COLORS.warning,
                    CONFIG.CHART_COLORS.info,
                    CONFIG.CHART_COLORS.error,
                ],
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#B0B8C4',
                        padding: 15,
                    },
                },
            },
        },
    });
    
    // Load initial data
    updateWorkloadChart();
}

/**
 * Update performance chart
 */
async function updatePerformanceChart() {
    if (!performanceChart) return;
    
    try {
        const metrics = await api.getSystemMetrics();
        
        const now = new Date().toLocaleTimeString();
        const cpuUsage = metrics.cpu?.usage_percent || 0;
        const memoryUsage = metrics.memory?.usage_percent || 0;
        
        // Keep last 20 data points
        if (performanceChart.data.labels.length >= 20) {
            performanceChart.data.labels.shift();
            performanceChart.data.datasets[0].data.shift();
            performanceChart.data.datasets[1].data.shift();
        }
        
        performanceChart.data.labels.push(now);
        performanceChart.data.datasets[0].data.push(cpuUsage);
        performanceChart.data.datasets[1].data.push(memoryUsage);
        
        performanceChart.update('none');
    } catch (error) {
        console.error('Failed to update performance chart:', error);
    }
}

/**
 * Update workload chart
 */
async function updateWorkloadChart() {
    if (!workloadChart) return;
    
    try {
        const workloads = await api.listWorkloads({ limit: 1000 });
        
        const statusCounts = {
            running: 0,
            pending: 0,
            completed: 0,
            failed: 0,
        };
        
        workloads.forEach(w => {
            if (statusCounts.hasOwnProperty(w.status)) {
                statusCounts[w.status]++;
            }
        });
        
        workloadChart.data.datasets[0].data = [
            statusCounts.running,
            statusCounts.pending,
            statusCounts.completed,
            statusCounts.failed,
        ];
        
        workloadChart.update('none');
    } catch (error) {
        console.error('Failed to update workload chart:', error);
    }
}

/**
 * Start auto-refresh
 */
function startAutoRefresh() {
    // Refresh stats and charts
    refreshInterval = setInterval(async () => {
        await loadStats();
        await updatePerformanceChart();
        await updateWorkloadChart();
    }, CONFIG.DASHBOARD_REFRESH);
    
    // Refresh activity less frequently
    setInterval(loadActivity, CONFIG.ACTIVITY_REFRESH);
}

/**
 * Stop auto-refresh
 */
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
});
