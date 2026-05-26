/**
 * ZenithOne Explorer - Metrics Page
 * 
 * System metrics and performance monitoring
 */

let cpuChart, memoryChart, networkChart, workloadChart;
let currentTimeRange = '24h';
let metricsInterval;

/**
 * Initialize metrics page
 */
document.addEventListener('DOMContentLoaded', async () => {
    initializeCharts();
    await loadMetrics();
    initializeEventListeners();
    startAutoRefresh();
});

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Refresh button
    document.getElementById('refreshBtn')?.addEventListener('click', () => {
        loadMetrics();
    });
    
    // Time range selector
    document.querySelectorAll('.time-range-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.time-range-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentTimeRange = e.target.dataset.range;
            loadMetrics();
        });
    });
}

/**
 * Initialize charts
 */
function initializeCharts() {
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(255, 255, 255, 0.05)'
                },
                ticks: {
                    color: '#9ca3af'
                }
            },
            x: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.05)'
                },
                ticks: {
                    color: '#9ca3af'
                }
            }
        }
    };
    
    // CPU Chart
    const cpuCtx = document.getElementById('cpuChart');
    if (cpuCtx) {
        cpuChart = new Chart(cpuCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU Usage (%)',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                ...chartOptions,
                scales: {
                    ...chartOptions.scales,
                    y: {
                        ...chartOptions.scales.y,
                        max: 100
                    }
                }
            }
        });
    }
    
    // Memory Chart
    const memoryCtx = document.getElementById('memoryChart');
    if (memoryCtx) {
        memoryChart = new Chart(memoryCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Memory Usage (%)',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                ...chartOptions,
                scales: {
                    ...chartOptions.scales,
                    y: {
                        ...chartOptions.scales.y,
                        max: 100
                    }
                }
            }
        });
    }
    
    // Network Chart
    const networkCtx = document.getElementById('networkChart');
    if (networkCtx) {
        networkChart = new Chart(networkCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Inbound (MB/s)',
                        data: [],
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Outbound (MB/s)',
                        data: [],
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                ...chartOptions,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: '#9ca3af'
                        }
                    }
                }
            }
        });
    }
    
    // Workload Chart
    const workloadCtx = document.getElementById('workloadChart');
    if (workloadCtx) {
        workloadChart = new Chart(workloadCtx, {
            type: 'doughnut',
            data: {
                labels: ['Running', 'Pending', 'Completed', 'Failed'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        '#10b981',
                        '#f59e0b',
                        '#3b82f6',
                        '#ef4444'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#9ca3af',
                            padding: 15
                        }
                    }
                }
            }
        });
    }
}

/**
 * Load metrics
 */
async function loadMetrics() {
    try {
        const metrics = await api.getSystemMetrics({ range: currentTimeRange });
        
        updateCharts(metrics);
        updateStats(metrics);
    } catch (error) {
        console.error('Failed to load metrics:', error);
        handleApiError(error, 'loading metrics');
    }
}

/**
 * Update charts
 */
function updateCharts(metrics) {
    if (!metrics) return;
    
    // Update CPU Chart
    if (cpuChart && metrics.cpu) {
        const cpuData = metrics.cpu.history || generateMockData(20, 0, 100);
        const labels = cpuData.map((_, i) => formatTimeLabel(i, cpuData.length));
        
        cpuChart.data.labels = labels;
        cpuChart.data.datasets[0].data = cpuData;
        cpuChart.update('none');
    }
    
    // Update Memory Chart
    if (memoryChart && metrics.memory) {
        const memoryData = metrics.memory.history || generateMockData(20, 0, 100);
        const labels = memoryData.map((_, i) => formatTimeLabel(i, memoryData.length));
        
        memoryChart.data.labels = labels;
        memoryChart.data.datasets[0].data = memoryData;
        memoryChart.update('none');
    }
    
    // Update Network Chart
    if (networkChart && metrics.network) {
        const inboundData = metrics.network.inbound_history || generateMockData(20, 0, 100);
        const outboundData = metrics.network.outbound_history || generateMockData(20, 0, 100);
        const labels = inboundData.map((_, i) => formatTimeLabel(i, inboundData.length));
        
        networkChart.data.labels = labels;
        networkChart.data.datasets[0].data = inboundData;
        networkChart.data.datasets[1].data = outboundData;
        networkChart.update('none');
    }
    
    // Update Workload Chart
    if (workloadChart && metrics.workloads) {
        const workloadData = [
            metrics.workloads.running || 0,
            metrics.workloads.pending || 0,
            metrics.workloads.completed || 0,
            metrics.workloads.failed || 0
        ];
        
        workloadChart.data.datasets[0].data = workloadData;
        workloadChart.update('none');
    }
}

/**
 * Update stats
 */
function updateStats(metrics) {
    if (!metrics) return;
    
    // CPU
    const avgCpu = metrics.cpu?.average || metrics.cpu?.current || 0;
    document.getElementById('avgCpu').textContent = `${avgCpu.toFixed(1)}%`;
    
    // Memory
    const avgMemory = metrics.memory?.average || metrics.memory?.current || 0;
    document.getElementById('avgMemory').textContent = `${avgMemory.toFixed(1)}%`;
    
    // Network
    const networkThroughput = metrics.network?.throughput || 0;
    document.getElementById('networkThroughput').textContent = `${networkThroughput.toFixed(2)} MB/s`;
    
    // Disk
    const diskUsage = metrics.disk?.usage || 0;
    document.getElementById('diskUsage').textContent = `${diskUsage.toFixed(1)}%`;
}

/**
 * Format time label
 */
function formatTimeLabel(index, total) {
    const now = new Date();
    const interval = getIntervalMinutes(currentTimeRange);
    const minutesAgo = (total - index - 1) * interval;
    const time = new Date(now.getTime() - minutesAgo * 60000);
    
    return time.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
    });
}

/**
 * Get interval in minutes based on time range
 */
function getIntervalMinutes(range) {
    const intervals = {
        '1h': 3,
        '6h': 18,
        '24h': 72,
        '7d': 504,
        '30d': 2160
    };
    return intervals[range] || 72;
}

/**
 * Generate mock data for testing
 */
function generateMockData(count, min, max) {
    const data = [];
    let current = (min + max) / 2;
    
    for (let i = 0; i < count; i++) {
        const change = (Math.random() - 0.5) * 10;
        current = Math.max(min, Math.min(max, current + change));
        data.push(parseFloat(current.toFixed(2)));
    }
    
    return data;
}

/**
 * Start auto-refresh
 */
function startAutoRefresh() {
    // Refresh every 30 seconds
    metricsInterval = setInterval(() => {
        loadMetrics();
    }, 30000);
}

/**
 * Stop auto-refresh
 */
function stopAutoRefresh() {
    if (metricsInterval) {
        clearInterval(metricsInterval);
        metricsInterval = null;
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
});
