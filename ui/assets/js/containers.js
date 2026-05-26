/**
 * ZenithOne Explorer - Containers Page
 * 
 * Container management functionality
 */

let currentFilters = {};

/**
 * Initialize containers page
 */
document.addEventListener('DOMContentLoaded', async () => {
    await loadContainers();
    initializeEventListeners();
});

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Refresh button
    document.getElementById('refreshBtn')?.addEventListener('click', () => {
        loadContainers();
    });
    
    // Create container button
    document.getElementById('createContainerBtn')?.addEventListener('click', () => {
        alert('Container creation interface coming soon!\n\nFor now, use the CLI:\nzenith container create --name mycontainer --image python:3.14');
    });
    
    // Filters
    document.getElementById('statusFilter')?.addEventListener('change', handleFilterChange);
    document.getElementById('clearFiltersBtn')?.addEventListener('click', clearFilters);
    
    // Search
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce((e) => {
            currentFilters.search = e.target.value.trim();
            loadContainers();
        }, 300));
    }
}

/**
 * Load containers
 */
async function loadContainers() {
    try {
        const containers = await api.listContainers(currentFilters);
        
        renderContainersTable(containers);
        updateStats(containers);
    } catch (error) {
        console.error('Failed to load containers:', error);
        handleApiError(error, 'loading containers');
        renderEmptyState('Failed to load containers');
    }
}

/**
 * Render containers table
 */
function renderContainersTable(containers) {
    const tbody = document.getElementById('containersTableBody');
    
    if (!containers || containers.length === 0) {
        renderEmptyState('No containers found');
        return;
    }
    
    tbody.innerHTML = containers.map(container => `
        <tr>
            <td><code>${container.id.substring(0, 12)}</code></td>
            <td><strong>${container.name || 'N/A'}</strong></td>
            <td><code>${container.image}</code></td>
            <td>${createStatusBadgeHtml(container.status)}</td>
            <td>${formatRelativeTime(container.created_at)}</td>
            <td>
                <div class="container-actions">
                    ${container.status === 'running' ? `
                        <button class="btn-icon-sm" onclick="stopContainer('${container.id}')" title="Stop">
                            <i class="fas fa-stop"></i>
                        </button>
                        <button class="btn-icon-sm" onclick="pauseContainer('${container.id}')" title="Pause">
                            <i class="fas fa-pause"></i>
                        </button>
                        <button class="btn-icon-sm" onclick="restartContainer('${container.id}')" title="Restart">
                            <i class="fas fa-redo"></i>
                        </button>
                    ` : ''}
                    ${container.status === 'stopped' || container.status === 'exited' ? `
                        <button class="btn-icon-sm" onclick="startContainer('${container.id}')" title="Start">
                            <i class="fas fa-play"></i>
                        </button>
                    ` : ''}
                    ${container.status === 'paused' ? `
                        <button class="btn-icon-sm" onclick="unpauseContainer('${container.id}')" title="Unpause">
                            <i class="fas fa-play"></i>
                        </button>
                    ` : ''}
                    <button class="btn-icon-sm" onclick="viewContainerLogs('${container.id}')" title="View Logs">
                        <i class="fas fa-file-alt"></i>
                    </button>
                    <button class="btn-icon-sm" onclick="inspectContainer('${container.id}')" title="Inspect">
                        <i class="fas fa-info-circle"></i>
                    </button>
                    <button class="btn-icon-sm" onclick="deleteContainer('${container.id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

/**
 * Render empty state
 */
function renderEmptyState(message) {
    const tbody = document.getElementById('containersTableBody');
    tbody.innerHTML = `
        <tr>
            <td colspan="6">
                <div class="empty-state">
                    <div class="empty-state-icon">
                        <i class="fas fa-box"></i>
                    </div>
                    <h3 class="empty-state-title">${message}</h3>
                    <p class="empty-state-description">
                        ${message === 'No containers found' ? 'Create your first container to get started' : ''}
                    </p>
                    ${message === 'No containers found' ? `
                        <button class="btn btn-primary" onclick="document.getElementById('createContainerBtn').click()">
                            <i class="fas fa-plus"></i> Create Container
                        </button>
                    ` : ''}
                </div>
            </td>
        </tr>
    `;
}

/**
 * Create status badge HTML
 */
function createStatusBadgeHtml(status) {
    const badgeClass = {
        'running': 'badge-success',
        'stopped': 'badge-error',
        'paused': 'badge-warning',
        'exited': 'badge-error',
        'created': 'badge-info'
    }[status] || 'badge-info';
    
    return `<span class="badge ${badgeClass}">${status}</span>`;
}

/**
 * Update stats
 */
function updateStats(containers) {
    const total = containers.length;
    const running = containers.filter(c => c.status === 'running').length;
    const stopped = containers.filter(c => c.status === 'stopped' || c.status === 'exited').length;
    const paused = containers.filter(c => c.status === 'paused').length;
    
    document.getElementById('totalContainers').textContent = total;
    document.getElementById('runningContainers').textContent = running;
    document.getElementById('stoppedContainers').textContent = stopped;
    document.getElementById('pausedContainers').textContent = paused;
}

/**
 * Handle filter change
 */
function handleFilterChange(e) {
    const value = e.target.value;
    currentFilters.status = value || undefined;
    loadContainers();
}

/**
 * Clear filters
 */
function clearFilters() {
    currentFilters = {};
    document.getElementById('statusFilter').value = '';
    document.getElementById('searchInput').value = '';
    loadContainers();
}

/**
 * Start container
 */
async function startContainer(id) {
    try {
        showLoading('Starting container...');
        await api.startContainer(id);
        hideLoading();
        
        showNotification('Container started successfully!', 'success');
        loadContainers();
    } catch (error) {
        hideLoading();
        handleApiError(error, 'starting container');
    }
}

/**
 * Stop container
 */
async function stopContainer(id) {
    if (!confirm('Stop this container?')) {
        return;
    }
    
    try {
        showLoading('Stopping container...');
        await api.stopContainer(id);
        hideLoading();
        
        showNotification('Container stopped successfully!', 'success');
        loadContainers();
    } catch (error) {
        hideLoading();
        handleApiError(error, 'stopping container');
    }
}

/**
 * Restart container
 */
async function restartContainer(id) {
    try {
        showLoading('Restarting container...');
        await api.restartContainer(id);
        hideLoading();
        
        showNotification('Container restarted successfully!', 'success');
        loadContainers();
    } catch (error) {
        hideLoading();
        handleApiError(error, 'restarting container');
    }
}

/**
 * Pause container
 */
async function pauseContainer(id) {
    try {
        showLoading('Pausing container...');
        await api.pauseContainer(id);
        hideLoading();
        
        showNotification('Container paused successfully!', 'success');
        loadContainers();
    } catch (error) {
        hideLoading();
        handleApiError(error, 'pausing container');
    }
}

/**
 * Unpause container
 */
async function unpauseContainer(id) {
    try {
        showLoading('Unpausing container...');
        await api.unpauseContainer(id);
        hideLoading();
        
        showNotification('Container unpaused successfully!', 'success');
        loadContainers();
    } catch (error) {
        hideLoading();
        handleApiError(error, 'unpausing container');
    }
}

/**
 * View container logs
 */
async function viewContainerLogs(id) {
    try {
        showLoading('Loading logs...');
        const logs = await api.getContainerLogs(id);
        hideLoading();
        
        // Display logs in a modal
        alert(`Container Logs:\n\n${logs.logs || JSON.stringify(logs, null, 2)}`);
    } catch (error) {
        hideLoading();
        handleApiError(error, 'loading logs');
    }
}

/**
 * Inspect container
 */
async function inspectContainer(id) {
    try {
        showLoading('Inspecting container...');
        const details = await api.inspectContainer(id);
        hideLoading();
        
        // Display details in a modal
        alert(`Container Details:\n\n${JSON.stringify(details, null, 2)}`);
    } catch (error) {
        hideLoading();
        handleApiError(error, 'inspecting container');
    }
}

/**
 * Delete container
 */
async function deleteContainer(id) {
    if (!confirm('Are you sure you want to delete this container? This action cannot be undone.')) {
        return;
    }
    
    try {
        showLoading('Deleting container...');
        await api.deleteContainer(id);
        hideLoading();
        
        showNotification('Container deleted successfully!', 'success');
        loadContainers();
    } catch (error) {
        hideLoading();
        handleApiError(error, 'deleting container');
    }
}

// Auto-refresh every 10 seconds
setInterval(() => {
    loadContainers();
}, 10000);
