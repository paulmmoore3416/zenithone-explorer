/**
 * ZenithOne Explorer - Admin Page
 * 
 * Administration and user management functionality
 */

let currentTab = 'users';

/**
 * Initialize admin page
 */
document.addEventListener('DOMContentLoaded', async () => {
    await loadUsers();
    await loadSystemInfo();
    initializeEventListeners();
});

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Tab switching
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            switchTab(e.target.dataset.tab);
        });
    });
    
    // Create user button
    document.getElementById('createUserBtn')?.addEventListener('click', () => {
        openCreateUserModal();
    });
    
    // Modal controls
    document.getElementById('closeUserModalBtn')?.addEventListener('click', closeCreateUserModal);
    document.getElementById('cancelUserModalBtn')?.addEventListener('click', closeCreateUserModal);
    document.getElementById('submitUserBtn')?.addEventListener('click', handleCreateUser);
}

/**
 * Switch tab
 */
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.dataset.tab === tabName) {
            tab.classList.add('active');
        }
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');
    
    currentTab = tabName;
}

/**
 * Load users
 */
async function loadUsers() {
    try {
        const users = await api.listUsers();
        renderUsersTable(users);
    } catch (error) {
        console.error('Failed to load users:', error);
        handleApiError(error, 'loading users');
        renderUsersEmptyState('Failed to load users');
    }
}

/**
 * Render users table
 */
function renderUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    
    if (!users || users.length === 0) {
        renderUsersEmptyState('No users found');
        return;
    }
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td><strong>${user.username}</strong></td>
            <td>${user.email}</td>
            <td><span class="badge ${user.role === 'admin' ? 'badge-error' : 'badge-info'}">${user.role}</span></td>
            <td><span class="badge ${user.is_active ? 'badge-success' : 'badge-error'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>
            <td>${formatRelativeTime(user.created_at)}</td>
            <td>
                <div class="user-actions">
                    <button class="btn-icon-sm" onclick="editUser('${user.id}')" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    ${!user.is_active ? `
                        <button class="btn-icon-sm" onclick="activateUser('${user.id}')" title="Activate">
                            <i class="fas fa-check"></i>
                        </button>
                    ` : `
                        <button class="btn-icon-sm" onclick="deactivateUser('${user.id}')" title="Deactivate">
                            <i class="fas fa-ban"></i>
                        </button>
                    `}
                    <button class="btn-icon-sm" onclick="deleteUser('${user.id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

/**
 * Render users empty state
 */
function renderUsersEmptyState(message) {
    const tbody = document.getElementById('usersTableBody');
    tbody.innerHTML = `
        <tr>
            <td colspan="6">
                <div class="empty-state">
                    <div class="empty-state-icon">
                        <i class="fas fa-users"></i>
                    </div>
                    <h3 class="empty-state-title">${message}</h3>
                    <p class="empty-state-description">
                        ${message === 'No users found' ? 'Create your first user to get started' : ''}
                    </p>
                    ${message === 'No users found' ? `
                        <button class="btn btn-primary" onclick="document.getElementById('createUserBtn').click()">
                            <i class="fas fa-plus"></i> Create User
                        </button>
                    ` : ''}
                </div>
            </td>
        </tr>
    `;
}

/**
 * Load system info
 */
async function loadSystemInfo() {
    try {
        const info = await api.getSystemInfo();
        
        // Platform info
        document.getElementById('osInfo').textContent = info.os || 'Linux';
        document.getElementById('archInfo').textContent = info.architecture || 'x86_64';
        document.getElementById('kernelInfo').textContent = info.kernel || 'Unknown';
        
        // Resources
        document.getElementById('cpuCores').textContent = info.cpu_cores || 'Unknown';
        document.getElementById('totalMemory').textContent = formatBytes(info.total_memory || 0);
        document.getElementById('diskSpace').textContent = formatBytes(info.disk_space || 0);
        
        // Uptime
        document.getElementById('uptimeInfo').textContent = formatUptime(info.uptime || 0);
    } catch (error) {
        console.error('Failed to load system info:', error);
        // Don't show error notification for system info
    }
}

/**
 * Format bytes
 */
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Format uptime
 */
function formatUptime(seconds) {
    if (!seconds || seconds === 0) return '0 seconds';
    
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    const parts = [];
    if (days > 0) parts.push(`${days} day${days > 1 ? 's' : ''}`);
    if (hours > 0) parts.push(`${hours} hour${hours > 1 ? 's' : ''}`);
    if (minutes > 0) parts.push(`${minutes} minute${minutes > 1 ? 's' : ''}`);
    
    return parts.join(', ') || '0 seconds';
}

/**
 * Open create user modal
 */
function openCreateUserModal() {
    document.getElementById('createUserModal').classList.add('active');
    document.getElementById('createUserForm').reset();
}

/**
 * Close create user modal
 */
function closeCreateUserModal() {
    document.getElementById('createUserModal').classList.remove('active');
}

/**
 * Handle create user
 */
async function handleCreateUser() {
    const form = document.getElementById('createUserForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const data = {
        username: document.getElementById('newUsername').value,
        email: document.getElementById('newEmail').value,
        password: document.getElementById('newPassword').value,
        role: document.getElementById('newRole').value
    };
    
    try {
        showLoading('Creating user...');
        await api.createUser(data);
        hideLoading();
        
        showNotification('User created successfully!', 'success');
        closeCreateUserModal();
        loadUsers();
    } catch (error) {
        hideLoading();
        handleApiError(error, 'creating user');
    }
}

/**
 * Edit user
 */
async function editUser(id) {
    alert('Edit user functionality coming soon!\n\nFor now, use the CLI:\nzenith admin user update --id ' + id);
}

/**
 * Activate user
 */
async function activateUser(id) {
    try {
        showLoading('Activating user...');
        await api.updateUser(id, { is_active: true });
        hideLoading();
        
        showNotification('User activated successfully!', 'success');
        loadUsers();
    } catch (error) {
        hideLoading();
        handleApiError(error, 'activating user');
    }
}

/**
 * Deactivate user
 */
async function deactivateUser(id) {
    if (!confirm('Deactivate this user?')) {
        return;
    }
    
    try {
        showLoading('Deactivating user...');
        await api.updateUser(id, { is_active: false });
        hideLoading();
        
        showNotification('User deactivated successfully!', 'success');
        loadUsers();
    } catch (error) {
        hideLoading();
        handleApiError(error, 'deactivating user');
    }
}

/**
 * Delete user
 */
async function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
        return;
    }
    
    try {
        showLoading('Deleting user...');
        await api.deleteUser(id);
        hideLoading();
        
        showNotification('User deleted successfully!', 'success');
        loadUsers();
    } catch (error) {
        hideLoading();
        handleApiError(error, 'deleting user');
    }
}
