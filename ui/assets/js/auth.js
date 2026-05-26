/**
 * ZenithOne Explorer - Authentication
 * 
 * Handles user authentication and authorization
 */

// Check authentication on page load
document.addEventListener('DOMContentLoaded', () => {
    // Skip auth check for login page
    if (window.location.pathname.includes('login.html')) {
        return;
    }
    
    // Redirect to login if not authenticated
    if (!isAuthenticated()) {
        window.location.href = '/ui/pages/login.html';
        return;
    }
    
    // Load user info
    loadUserInfo();
});

/**
 * Load and display user information
 */
async function loadUserInfo() {
    try {
        const user = getUser();
        
        if (user) {
            updateUserDisplay(user);
        } else {
            // Fetch user info from API
            const userData = await api.whoami();
            setUser(userData);
            updateUserDisplay(userData);
        }
    } catch (error) {
        console.error('Failed to load user info:', error);
        // Token might be invalid, redirect to login
        clearToken();
        window.location.href = '/ui/pages/login.html';
    }
}

/**
 * Update user display in UI
 */
function updateUserDisplay(user) {
    const userNameEl = document.getElementById('userName');
    const userRoleEl = document.getElementById('userRole');
    
    if (userNameEl) {
        userNameEl.textContent = user.username || 'User';
    }
    
    if (userRoleEl) {
        userRoleEl.textContent = user.role || 'User';
    }
}

/**
 * Handle login
 */
async function handleLogin(username, password) {
    try {
        const response = await api.login(username, password);
        
        if (response.access_token) {
            showNotification('Login successful!', 'success');
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = '/ui/index.html';
            }, 500);
            
            return true;
        }
        
        return false;
    } catch (error) {
        showNotification(error.message || 'Login failed', 'error');
        return false;
    }
}

/**
 * Handle logout
 */
async function handleLogout() {
    try {
        await api.logout();
        showNotification('Logged out successfully', 'success');
        
        // Redirect to login
        setTimeout(() => {
            window.location.href = '/ui/pages/login.html';
        }, 500);
    } catch (error) {
        console.error('Logout error:', error);
        // Clear token anyway
        clearToken();
        window.location.href = '/ui/pages/login.html';
    }
}

// Setup logout button
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            
            if (confirm('Are you sure you want to logout?')) {
                handleLogout();
            }
        });
    }
});
