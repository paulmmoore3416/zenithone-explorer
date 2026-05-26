/**
 * ZenithOne Explorer - Main JavaScript
 * 
 * Global functionality and event handlers
 */

/**
 * Initialize application
 */
document.addEventListener('DOMContentLoaded', () => {
    initializeSidebar();
    initializeSearch();
    initializeNotifications();
});

/**
 * Initialize sidebar functionality
 */
function initializeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    
    // Desktop sidebar toggle
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            document.querySelector('.main-content').classList.toggle('expanded');
        });
    }
    
    // Mobile menu toggle
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }
    
    // Close sidebar on mobile when clicking outside
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 1024) {
            if (!sidebar.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', debounce(() => {
        if (window.innerWidth > 1024) {
            sidebar.classList.remove('active');
        }
    }, 250));
}

/**
 * Initialize search functionality
 */
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce((e) => {
            const query = e.target.value.trim();
            
            if (query.length >= 3) {
                performSearch(query);
            }
        }, 300));
    }
}

/**
 * Perform search
 */
async function performSearch(query) {
    try {
        // This would typically search across workloads, containers, etc.
        console.log('Searching for:', query);
        
        // Example: Search workloads
        const workloads = await api.listWorkloads({ search: query, limit: 10 });
        
        // Display search results (implement as needed)
        console.log('Search results:', workloads);
    } catch (error) {
        console.error('Search failed:', error);
    }
}

/**
 * Initialize notifications
 */
function initializeNotifications() {
    const notificationsBtn = document.getElementById('notificationsBtn');
    
    if (notificationsBtn) {
        notificationsBtn.addEventListener('click', () => {
            showNotificationsPanel();
        });
    }
}

/**
 * Show notifications panel
 */
function showNotificationsPanel() {
    // Implement notifications panel
    showNotification('Notifications feature coming soon!', 'info');
}

/**
 * Handle settings button
 */
document.addEventListener('DOMContentLoaded', () => {
    const settingsBtn = document.getElementById('settingsBtn');
    
    if (settingsBtn) {
        settingsBtn.addEventListener('click', () => {
            window.location.href = '/ui/pages/settings.html';
        });
    }
});

/**
 * Confirm dialog
 */
function confirmDialog(message, onConfirm, onCancel) {
    const confirmed = confirm(message);
    
    if (confirmed && onConfirm) {
        onConfirm();
    } else if (!confirmed && onCancel) {
        onCancel();
    }
    
    return confirmed;
}

/**
 * Show loading overlay
 */
function showLoading(message = 'Loading...') {
    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div style="text-align: center;">
            <div class="spinner spinner-lg"></div>
            <p style="margin-top: 1rem; color: var(--text-secondary);">${message}</p>
        </div>
    `;
    
    document.body.appendChild(overlay);
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

/**
 * Format status badge
 */
function createStatusBadge(status) {
    const badge = document.createElement('span');
    badge.className = 'badge';
    
    const statusMap = {
        'running': 'badge-success',
        'stopped': 'badge-error',
        'pending': 'badge-warning',
        'completed': 'badge-info',
        'failed': 'badge-error',
    };
    
    badge.classList.add(statusMap[status] || 'badge-info');
    badge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    
    return badge;
}

/**
 * Create action button
 */
function createActionButton(icon, title, onClick, variant = 'primary') {
    const button = document.createElement('button');
    button.className = `btn btn-${variant} btn-sm`;
    button.title = title;
    button.innerHTML = `<i class="fas fa-${icon}"></i>`;
    button.addEventListener('click', onClick);
    
    return button;
}

/**
 * Handle API errors
 */
function handleApiError(error, context = '') {
    console.error(`API Error ${context}:`, error);
    
    const message = error.message || 'An error occurred';
    
    // Check for authentication errors
    if (message.includes('401') || message.includes('Unauthorized')) {
        showNotification('Session expired. Please login again.', 'error');
        setTimeout(() => {
            clearToken();
            window.location.href = '/ui/pages/login.html';
        }, 2000);
        return;
    }
    
    // Show error notification
    showNotification(message, 'error');
}

/**
 * Copy to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard!', 'success');
    } catch (error) {
        console.error('Failed to copy:', error);
        showNotification('Failed to copy to clipboard', 'error');
    }
}

/**
 * Download as file
 */
function downloadAsFile(content, filename, mimeType = 'text/plain') {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Validate form
 */
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('error');
        } else {
            input.classList.remove('error');
        }
    });
    
    return isValid;
}

/**
 * Clear form
 */
function clearForm(formElement) {
    formElement.reset();
    
    // Clear any error states
    const inputs = formElement.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.classList.remove('error');
    });
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(element => {
        const text = element.getAttribute('data-tooltip');
        
        const tooltipEl = document.createElement('span');
        tooltipEl.className = 'tooltip-text';
        tooltipEl.textContent = text;
        
        element.classList.add('tooltip');
        element.appendChild(tooltipEl);
    });
}

/**
 * Initialize dropdowns
 */
function initializeDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const trigger = dropdown.querySelector('[data-dropdown-trigger]');
        
        if (trigger) {
            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdown.classList.toggle('active');
            });
        }
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', () => {
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove('active');
        });
    });
}

/**
 * Initialize tabs
 */
function initializeTabs() {
    const tabContainers = document.querySelectorAll('[data-tabs]');
    
    tabContainers.forEach(container => {
        const tabs = container.querySelectorAll('.tab');
        const contents = container.querySelectorAll('.tab-content');
        
        tabs.forEach((tab, index) => {
            tab.addEventListener('click', () => {
                // Remove active class from all tabs and contents
                tabs.forEach(t => t.classList.remove('active'));
                contents.forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding content
                tab.classList.add('active');
                if (contents[index]) {
                    contents[index].classList.add('active');
                }
            });
        });
    });
}

// Initialize components on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeTooltips();
    initializeDropdowns();
    initializeTabs();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
`;
document.head.appendChild(style);
