/**
 * ZenithOne Explorer - Workloads Page
 * 
 * Workload management functionality
 */

let currentPage = 1;
let pageSize = 20;
let totalWorkloads = 0;
let currentFilters = {};

/**
 * Initialize workloads page
 */
document.addEventListener('DOMContentLoaded', async () => {
    await loadWorkloads();
    initializeEventListeners();
});

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Refresh button
    document.getElementById('refreshBtn')?.addEventListener('click', () => {
        loadWorkloads();
    });
    
    // Create workload button
    document.getElementById('createWorkloadBtn')?.addEventListener('click', () => {
        openCreateModal();
    });
    
    // Modal controls
    document.getElementById('closeModalBtn')?.addEventListener('click', closeCreateModal);
    document.getElementById('cancelModalBtn')?.addEventListener('click', closeCreateModal);
    document.getElementById('submitWorkloadBtn')?.addEventListener('click', handleCreateWorkload);
    
    // Filters
    document.getElementById('statusFilter')?.addEventListener('change', handleFilterChange);
    document.getElementById('typeFilter')?.addEventListener('change', handleFilterChange);
    document.getElementById('priorityFilter')?.addEventListener('change', handleFilterChange);
    document.getElementById('clearFiltersBtn')?.addEventListener('click', clearFilters);
    
    // Search
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce((e) => {
            currentFilters.search = e.target.value.trim();
            currentPage = 1;
            loadWorkloads();
        }, 300));
    }
}

/**
 * Load workloads
 */
async function loadWorkloads() {
    try {
        const params = {
            limit: pageSize,
            offset: (currentPage - 1) * pageSize,
            ...currentFilters
        };
        
        const workloads = await api.listWorkloads(params);
        totalWorkloads = workloads.length; // In real API, this would come from response
        
        renderWorkloadsTable(workloads);
        updatePagination();
        updateCounts(workloads.length);
    } catch (error) {
        console.error('Failed to load workloads:', error);
        handleApiError(error, 'loading workloads');
        renderEmptyState('Failed to load workloads');
    }
}

/**
 * Render workloads table
 */
function renderWorkloadsTable(workloads) {
    const tbody = document.getElementById('workloadsTableBody');
    
    if (!workloads || workloads.length === 0) {
        renderEmptyState('No workloads found');
        return;
    }
    
    tbody.innerHTML = workloads.map(workload => `
        <tr>
            <td><code>${workload.id.substring(0, 8)}</code></td>
            <td><strong>${workload.name}</strong></td>
            <td><span class="badge badge-info">${workload.type}</span></td>
            <td>${createStatusBadgeHtml(workload.status)}</td>
            <td>${createPriorityBadgeHtml(workload.priority)}</td>
            <td>${formatRelativeTime(workload.created_at)}</td>
            <td>
                <div class="workload-actions">
                    ${workload.status === 'pending' ? `
                        <button class="btn-icon-sm" onclick="scheduleWorkload('${workload.id}')" title="Schedule">
                            <i class="fas fa-play"></i>
                        </button>
                    ` : ''}
                    <button class="btn-icon-sm" onclick="viewWorkload('${workload.id}')" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-icon-sm" onclick="viewLogs('${workload.id}')" title="View Logs">
                        <i class="fas fa-file-alt"></i>
                    </button>
                    <button class="btn-icon-sm" onclick="deleteWorkload('${workload.id}')" title="Delete">
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
    const tbody = document.getElementById('workloadsTableBody');
    tbody.innerHTML = `
        <tr>
            <td colspan="7">
                <div class="empty-state">
                    <div class="empty-state-icon">
                        <i class="fas fa-tasks"></i>
                    </div>
                    <h3 class="empty-state-title">${message}</h3>
                    <p class="empty-state-description">
                        ${message === 'No workloads found' ? 'Create your first workload to get started' : ''}
                    </p>
                    ${message === 'No workloads found' ? `
                        <button class="btn btn-primary" onclick="document.getElementById('createWorkloadBtn').click()">
                            <i class="fas fa-plus"></i> Create Workload
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
        'pending': 'badge-warning',
        'completed': 'badge-info',
        'failed': 'badge-error',
        'cancelled': 'badge-error'
    }[status] || 'badge-info';
    
    return `<span class="badge ${badgeClass}">${status}</span>`;
}

/**
 * Create priority badge HTML
 */
function createPriorityBadgeHtml(priority) {
    const badgeClass = {
        'critical': 'badge-error',
        'high': 'badge-warning',
        'normal': 'badge-info',
        'low': 'badge-primary'
    }[priority] || 'badge-info';
    
    return `<span class="badge ${badgeClass}">${priority}</span>`;
}

/**
 * Update pagination
 */
function updatePagination() {
    const pagination = document.getElementById('pagination');
    const totalPages = Math.ceil(totalWorkloads / pageSize);
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Previous button
    html += `
        <button class="page-item" ${currentPage === 1 ? 'disabled' : ''} onclick="changePage(${currentPage - 1})">
            <i class="fas fa-chevron-left"></i>
        </button>
    `;
    
    // Page numbers
    for (let i = 1; i <= Math.min(totalPages, 5); i++) {
        html += `
            <button class="page-item ${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">
                ${i}
            </button>
        `;
    }
    
    // Next button
    html += `
        <button class="page-item" ${currentPage === totalPages ? 'disabled' : ''} onclick="changePage(${currentPage + 1})">
            <i class="fas fa-chevron-right"></i>
        </button>
    `;
    
    pagination.innerHTML = html;
}

/**
 * Change page
 */
function changePage(page) {
    currentPage = page;
    loadWorkloads();
}

/**
 * Update counts
 */
function updateCounts(showing) {
    document.getElementById('showingCount').textContent = showing;
    document.getElementById('totalCount').textContent = totalWorkloads;
}

/**
 * Handle filter change
 */
function handleFilterChange(e) {
    const filterId = e.target.id;
    const value = e.target.value;
    
    if (filterId === 'statusFilter') {
        currentFilters.status = value || undefined;
    } else if (filterId === 'typeFilter') {
        currentFilters.type = value || undefined;
    } else if (filterId === 'priorityFilter') {
        currentFilters.priority = value || undefined;
    }
    
    currentPage = 1;
    loadWorkloads();
}

/**
 * Clear filters
 */
function clearFilters() {
    currentFilters = {};
    document.getElementById('statusFilter').value = '';
    document.getElementById('typeFilter').value = '';
    document.getElementById('priorityFilter').value = '';
    document.getElementById('searchInput').value = '';
    currentPage = 1;
    loadWorkloads();
}

/**
 * Open create modal
 */
function openCreateModal() {
    document.getElementById('createWorkloadModal').classList.add('active');
    document.getElementById('createWorkloadForm').reset();
}

/**
 * Close create modal
 */
function closeCreateModal() {
    document.getElementById('createWorkloadModal').classList.remove('active');
}

/**
 * Handle create workload
 */
async function handleCreateWorkload() {
    const form = document.getElementById('createWorkloadForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const data = {
        name: document.getElementById('workloadName').value,
        type: document.getElementById('workloadType').value,
        image: document.getElementById('workloadImage').value,
        priority: document.getElementById('workloadPriority').value,
    };
    
    const command = document.getElementById('workloadCommand').value;
    if (command) data.command = command;
    
    const cpu = document.getElementById('workloadCpu').value;
    if (cpu) data.cpu_limit = parseFloat(cpu);
    
    const memory = document.getElementById('workloadMemory').value;
    if (memory) data.memory_limit = parseInt(memory);
    
    try {
        showLoading('Creating workload...');
        await api.createWorkload(data);
        hideLoading();
        
        showNotification('Workload created successfully!', 'success');
        closeCreateModal();
        loadWorkloads();
    } catch (error) {
        hideLoading();
        handleApiError(error, 'creating workload');
    }
}

/**
 * Schedule workload
 */
async function scheduleWorkload(id) {
    if (!confirm('Schedule this workload for execution?')) {
        return;
    }
    
    try {
        showLoading('Scheduling workload...');
        await api.scheduleWorkload(id);
        hideLoading();
        
        showNotification('Workload scheduled successfully!', 'success');
        loadWorkloads();
    } catch (error) {
        hideLoading();
        handleApiError(error, 'scheduling workload');
    }
}

/**
 * View workload details
 */
async function viewWorkload(id) {
    try {
        showLoading('Loading workload details...');
        const workload = await api.getWorkload(id);
        hideLoading();
        
        // Display workload details in a modal or navigate to details page
        alert(`Workload Details:\n\n${JSON.stringify(workload, null, 2)}`);
    } catch (error) {
        hideLoading();
        handleApiError(error, 'loading workload details');
    }
}

/**
 * View workload logs
 */
async function viewLogs(id) {
    try {
        showLoading('Loading logs...');
        const logs = await api.getWorkloadLogs(id);
        hideLoading();
        
        // Display logs in a modal
        alert(`Workload Logs:\n\n${logs.logs || JSON.stringify(logs, null, 2)}`);
    } catch (error) {
        hideLoading();
        handleApiError(error, 'loading logs');
    }
}

/**
 * Delete workload
 */
async function deleteWorkload(id) {
    if (!confirm('Are you sure you want to delete this workload? This action cannot be undone.')) {
        return;
    }
    
    try {
        showLoading('Deleting workload...');
        await api.deleteWorkload(id);
        hideLoading();
        
        showNotification('Workload deleted successfully!', 'success');
        loadWorkloads();
    } catch (error) {
        hideLoading();
        handleApiError(error, 'deleting workload');
    }
}

// Auto-refresh every 10 seconds
setInterval(() => {
    loadWorkloads();
}, 10000);
