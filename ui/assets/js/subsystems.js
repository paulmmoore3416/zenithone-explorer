/**
 * ZenithOne Explorer - Subsystems Page
 * 
 * z/OS subsystem monitoring functionality
 */

const SUBSYSTEMS = ['jes', 'cics', 'db2', 'tso'];

const SUBSYSTEM_INFO = {
    jes: {
        name: 'JES (Job Entry Subsystem)',
        description: 'Manages batch job submission and execution',
        icon: 'fas fa-clipboard-list',
        color: 'jes'
    },
    cics: {
        name: 'CICS (Customer Information Control System)',
        description: 'Transaction processing system',
        icon: 'fas fa-exchange-alt',
        color: 'cics'
    },
    db2: {
        name: 'DB2 Database',
        description: 'Relational database management system',
        icon: 'fas fa-database',
        color: 'db2'
    },
    tso: {
        name: 'TSO (Time Sharing Option)',
        description: 'Interactive time-sharing environment',
        icon: 'fas fa-terminal',
        color: 'tso'
    }
};

/**
 * Initialize subsystems page
 */
document.addEventListener('DOMContentLoaded', async () => {
    await loadSubsystems();
    initializeEventListeners();
});

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Refresh button
    document.getElementById('refreshBtn')?.addEventListener('click', () => {
        loadSubsystems();
    });
}

/**
 * Load subsystems
 */
async function loadSubsystems() {
    try {
        const subsystemsData = await Promise.all(
            SUBSYSTEMS.map(async (subsystem) => {
                try {
                    const status = await api.getSubsystemStatus(subsystem);
                    return { subsystem, status, error: null };
                } catch (error) {
                    console.error(`Failed to load ${subsystem}:`, error);
                    return { subsystem, status: null, error };
                }
            })
        );
        
        renderSubsystems(subsystemsData);
    } catch (error) {
        console.error('Failed to load subsystems:', error);
        handleApiError(error, 'loading subsystems');
        renderErrorState();
    }
}

/**
 * Render subsystems
 */
function renderSubsystems(subsystemsData) {
    const grid = document.getElementById('subsystemsGrid');
    
    grid.innerHTML = subsystemsData.map(({ subsystem, status, error }) => {
        const info = SUBSYSTEM_INFO[subsystem];
        
        if (error) {
            return createErrorCard(subsystem, info);
        }
        
        return createSubsystemCard(subsystem, info, status);
    }).join('');
}

/**
 * Create subsystem card
 */
function createSubsystemCard(subsystem, info, status) {
    const isActive = status?.status === 'active' || status?.active;
    const uptime = status?.uptime || 0;
    const activeJobs = status?.active_jobs || status?.jobs?.active || 0;
    const totalJobs = status?.total_jobs || status?.jobs?.total || 0;
    const connections = status?.connections || status?.active_connections || 0;
    
    return `
        <div class="subsystem-card">
            <div class="subsystem-icon ${info.color}">
                <i class="${info.icon}"></i>
            </div>
            
            <div class="subsystem-header">
                <div>
                    <h3 class="subsystem-title">${info.name}</h3>
                    <p class="subsystem-description">${info.description}</p>
                </div>
                <span class="badge ${isActive ? 'badge-success' : 'badge-error'}">
                    ${isActive ? 'Active' : 'Inactive'}
                </span>
            </div>
            
            <div class="subsystem-stats">
                <div class="stat-item">
                    <span class="stat-label">Uptime</span>
                    <span class="stat-value">${formatUptime(uptime)}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">${subsystem === 'jes' ? 'Active Jobs' : subsystem === 'db2' ? 'Connections' : 'Transactions'}</span>
                    <span class="stat-value">${subsystem === 'db2' ? connections : activeJobs}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">${subsystem === 'jes' ? 'Total Jobs' : subsystem === 'db2' ? 'Queries' : 'Total'}</span>
                    <span class="stat-value">${totalJobs}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Status</span>
                    <span class="stat-value" style="color: ${isActive ? 'var(--status-success)' : 'var(--status-error)'}">
                        ${isActive ? 'Running' : 'Stopped'}
                    </span>
                </div>
            </div>
            
            <div class="subsystem-actions">
                <button class="btn btn-outline btn-sm" onclick="viewSubsystemDetails('${subsystem}')">
                    <i class="fas fa-info-circle"></i>
                    Details
                </button>
                <button class="btn btn-outline btn-sm" onclick="viewSubsystemLogs('${subsystem}')">
                    <i class="fas fa-file-alt"></i>
                    Logs
                </button>
                ${isActive ? `
                    <button class="btn btn-outline btn-sm" onclick="stopSubsystem('${subsystem}')">
                        <i class="fas fa-stop"></i>
                        Stop
                    </button>
                ` : `
                    <button class="btn btn-primary btn-sm" onclick="startSubsystem('${subsystem}')">
                        <i class="fas fa-play"></i>
                        Start
                    </button>
                `}
            </div>
        </div>
    `;
}

/**
 * Create error card
 */
function createErrorCard(subsystem, info) {
    return `
        <div class="subsystem-card">
            <div class="subsystem-icon ${info.color}">
                <i class="${info.icon}"></i>
            </div>
            
            <div class="subsystem-header">
                <div>
                    <h3 class="subsystem-title">${info.name}</h3>
                    <p class="subsystem-description">${info.description}</p>
                </div>
                <span class="badge badge-error">Error</span>
            </div>
            
            <div style="padding: var(--spacing-lg); text-align: center; color: var(--text-tertiary);">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: var(--spacing-md);"></i>
                <p>Failed to load subsystem status</p>
            </div>
            
            <div class="subsystem-actions">
                <button class="btn btn-outline btn-sm" onclick="loadSubsystems()">
                    <i class="fas fa-sync-alt"></i>
                    Retry
                </button>
            </div>
        </div>
    `;
}

/**
 * Render error state
 */
function renderErrorState() {
    const grid = document.getElementById('subsystemsGrid');
    grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
            <div class="empty-state">
                <div class="empty-state-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3 class="empty-state-title">Failed to load subsystems</h3>
                <p class="empty-state-description">Please try again later</p>
                <button class="btn btn-primary" onclick="loadSubsystems()">
                    <i class="fas fa-sync-alt"></i> Retry
                </button>
            </div>
        </div>
    `;
}

/**
 * Format uptime
 */
function formatUptime(seconds) {
    if (!seconds || seconds === 0) return '0s';
    
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
}

/**
 * View subsystem details
 */
async function viewSubsystemDetails(subsystem) {
    try {
        showLoading('Loading details...');
        const status = await api.getSubsystemStatus(subsystem);
        hideLoading();
        
        alert(`${SUBSYSTEM_INFO[subsystem].name} Details:\n\n${JSON.stringify(status, null, 2)}`);
    } catch (error) {
        hideLoading();
        handleApiError(error, 'loading subsystem details');
    }
}

/**
 * View subsystem logs
 */
async function viewSubsystemLogs(subsystem) {
    try {
        showLoading('Loading logs...');
        const logs = await api.getSubsystemLogs(subsystem);
        hideLoading();
        
        alert(`${SUBSYSTEM_INFO[subsystem].name} Logs:\n\n${logs.logs || JSON.stringify(logs, null, 2)}`);
    } catch (error) {
        hideLoading();
        handleApiError(error, 'loading subsystem logs');
    }
}

/**
 * Start subsystem
 */
async function startSubsystem(subsystem) {
    try {
        showLoading(`Starting ${subsystem.toUpperCase()}...`);
        await api.startSubsystem(subsystem);
        hideLoading();
        
        showNotification(`${SUBSYSTEM_INFO[subsystem].name} started successfully!`, 'success');
        loadSubsystems();
    } catch (error) {
        hideLoading();
        handleApiError(error, 'starting subsystem');
    }
}

/**
 * Stop subsystem
 */
async function stopSubsystem(subsystem) {
    if (!confirm(`Stop ${SUBSYSTEM_INFO[subsystem].name}?`)) {
        return;
    }
    
    try {
        showLoading(`Stopping ${subsystem.toUpperCase()}...`);
        await api.stopSubsystem(subsystem);
        hideLoading();
        
        showNotification(`${SUBSYSTEM_INFO[subsystem].name} stopped successfully!`, 'success');
        loadSubsystems();
    } catch (error) {
        hideLoading();
        handleApiError(error, 'stopping subsystem');
    }
}

// Auto-refresh every 15 seconds
setInterval(() => {
    loadSubsystems();
}, 15000);
