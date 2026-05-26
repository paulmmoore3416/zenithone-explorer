/**
 * ZenithOne Explorer - Configuration
 * 
 * Application configuration and constants
 */

const CONFIG = {
    // API Configuration
    API_BASE_URL: 'http://localhost:8000',
    API_VERSION: 'v1',
    API_TIMEOUT: 30000,
    
    // Authentication
    TOKEN_KEY: 'zenith_token',
    USER_KEY: 'zenith_user',
    
    // Refresh Intervals (milliseconds)
    DASHBOARD_REFRESH: 5000,
    METRICS_REFRESH: 3000,
    ACTIVITY_REFRESH: 10000,
    
    // Pagination
    DEFAULT_PAGE_SIZE: 20,
    MAX_PAGE_SIZE: 100,
    
    // Chart Colors
    CHART_COLORS: {
        primary: '#0530AD',
        secondary: '#009688',
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
        info: '#3B82F6',
        purple: '#9C27B0',
        orange: '#FF9800',
    },
    
    // Status Colors
    STATUS_COLORS: {
        running: '#10B981',
        stopped: '#6B7280',
        pending: '#F59E0B',
        failed: '#EF4444',
        completed: '#3B82F6',
    },
    
    // Workload Types
    WORKLOAD_TYPES: ['batch', 'interactive', 'service', 'scheduled'],
    
    // Priority Levels
    PRIORITY_LEVELS: ['low', 'normal', 'high', 'critical'],
    
    // Subsystems
    SUBSYSTEMS: ['jes', 'cics', 'db2', 'tso'],
};

// Get API URL
function getApiUrl(endpoint = '') {
    const baseUrl = `${CONFIG.API_BASE_URL}/api/${CONFIG.API_VERSION}`;
    return endpoint ? `${baseUrl}${endpoint}` : baseUrl;
}

// Get stored token
function getToken() {
    return localStorage.getItem(CONFIG.TOKEN_KEY);
}

// Set token
function setToken(token) {
    localStorage.setItem(CONFIG.TOKEN_KEY, token);
}

// Clear token
function clearToken() {
    localStorage.removeItem(CONFIG.TOKEN_KEY);
    localStorage.removeItem(CONFIG.USER_KEY);
}

// Get stored user
function getUser() {
    const userJson = localStorage.getItem(CONFIG.USER_KEY);
    return userJson ? JSON.parse(userJson) : null;
}

// Set user
function setUser(user) {
    localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(user));
}

// Check if authenticated
function isAuthenticated() {
    return !!getToken();
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Format relative time
function formatRelativeTime(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffSecs < 60) return 'just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return formatDate(dateString);
}

// Format bytes
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Format percentage
function formatPercentage(value, decimals = 1) {
    return `${parseFloat(value).toFixed(decimals)}%`;
}

// Get status color
function getStatusColor(status) {
    return CONFIG.STATUS_COLORS[status] || CONFIG.STATUS_COLORS.stopped;
}

// Show notification
function showNotification(message, type = 'info') {
    // Simple notification implementation
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background-color: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CONFIG,
        getApiUrl,
        getToken,
        setToken,
        clearToken,
        getUser,
        setUser,
        isAuthenticated,
        formatDate,
        formatRelativeTime,
        formatBytes,
        formatPercentage,
        getStatusColor,
        showNotification,
        debounce,
    };
}
