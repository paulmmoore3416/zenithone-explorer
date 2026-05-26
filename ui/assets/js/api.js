/**
 * ZenithOne Explorer - API Client
 * 
 * HTTP client for communicating with the backend API
 */

class APIClient {
    constructor() {
        this.baseUrl = getApiUrl();
        this.timeout = CONFIG.API_TIMEOUT;
    }
    
    /**
     * Make HTTP request
     */
    async request(method, endpoint, data = null, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const token = getToken();
        
        const config = {
            method,
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` }),
                ...options.headers,
            },
            ...options,
        };
        
        if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
            config.body = JSON.stringify(data);
        }
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            
            const response = await fetch(url, {
                ...config,
                signal: controller.signal,
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }
            
            if (response.status === 204) {
                return null;
            }
            
            return await response.json();
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }
    
    // Convenience methods
    get(endpoint, options) {
        return this.request('GET', endpoint, null, options);
    }
    
    post(endpoint, data, options) {
        return this.request('POST', endpoint, data, options);
    }
    
    put(endpoint, data, options) {
        return this.request('PUT', endpoint, data, options);
    }
    
    delete(endpoint, options) {
        return this.request('DELETE', endpoint, null, options);
    }
    
    // Authentication
    async login(username, password) {
        const response = await this.post('/auth/login', { username, password });
        if (response.access_token) {
            setToken(response.access_token);
            if (response.user) {
                setUser(response.user);
            }
        }
        return response;
    }
    
    async logout() {
        try {
            await this.delete('/auth/logout');
        } finally {
            clearToken();
        }
    }
    
    async whoami() {
        return this.get('/auth/me');
    }
    
    // Workloads
    async listWorkloads(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.get(`/workloads${query ? '?' + query : ''}`);
    }
    
    async getWorkload(id) {
        return this.get(`/workloads/${id}`);
    }
    
    async createWorkload(data) {
        return this.post('/workloads', data);
    }
    
    async updateWorkload(id, data) {
        return this.put(`/workloads/${id}`, data);
    }
    
    async deleteWorkload(id) {
        return this.delete(`/workloads/${id}`);
    }
    
    async scheduleWorkload(id) {
        return this.post(`/workloads/${id}/schedule`);
    }
    
    async getWorkloadLogs(id) {
        return this.get(`/workloads/${id}/logs`);
    }
    
    // Containers
    async listContainers(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.get(`/containers${query ? '?' + query : ''}`);
    }
    
    async getContainer(id) {
        return this.get(`/containers/${id}`);
    }
    
    async createContainer(data) {
        return this.post('/containers', data);
    }
    
    async startContainer(id) {
        return this.post(`/containers/${id}/start`);
    }
    
    async stopContainer(id) {
        return this.post(`/containers/${id}/stop`);
    }
    
    async restartContainer(id) {
        return this.post(`/containers/${id}/restart`);
    }
    
    async deleteContainer(id) {
        return this.delete(`/containers/${id}`);
    }
    
    async getContainerLogs(id, params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.get(`/containers/${id}/logs${query ? '?' + query : ''}`);
    }
    
    // Subsystems
    async getSubsystemStatus(subsystem) {
        return this.get(`/subsystems/${subsystem}/status`);
    }
    
    async executeSubsystemCommand(subsystem, command, params = {}) {
        return this.post(`/subsystems/${subsystem}/execute`, { command, params });
    }
    
    // JES
    async submitJob(jcl, priority = 'NORMAL') {
        return this.post('/subsystems/jes/jobs', { jcl, priority });
    }
    
    async getJobStatus(jobId) {
        return this.get(`/subsystems/jes/jobs/${jobId}`);
    }
    
    // CICS
    async processTransaction(program, data) {
        return this.post('/subsystems/cics/transactions', { program, data });
    }
    
    // DB2
    async executeSql(sql) {
        return this.post('/subsystems/db2/query', { sql });
    }
    
    // TSO
    async executeTsoCommand(command) {
        return this.post('/subsystems/tso/execute', { command });
    }
    
    // Metrics
    async getSystemMetrics() {
        return this.get('/metrics/system');
    }
    
    async getWorkloadMetrics(workloadId = null) {
        const endpoint = workloadId ? `/metrics/workloads/${workloadId}` : '/metrics/workloads';
        return this.get(endpoint);
    }
    
    async getContainerMetrics(containerId = null) {
        const endpoint = containerId ? `/metrics/containers/${containerId}` : '/metrics/containers';
        return this.get(endpoint);
    }
    
    // Admin
    async listUsers() {
        return this.get('/admin/users');
    }
    
    async getUser(id) {
        return this.get(`/admin/users/${id}`);
    }
    
    async createUser(data) {
        return this.post('/admin/users', data);
    }
    
    async updateUser(id, data) {
        return this.put(`/admin/users/${id}`, data);
    }
    
    async deleteUser(id) {
        return this.delete(`/admin/users/${id}`);
    }
    
    async listRoles() {
        return this.get('/admin/roles');
    }
    
    async getSystemInfo() {
        return this.get('/admin/system/info');
    }
    
    async getSystemHealth() {
        return this.get('/admin/system/health');
    }
}

// Create global API client instance
const api = new APIClient();
