const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

class ApiService {
    constructor() {
        this.token = localStorage.getItem('token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
    }

    getHeaders(isFormData = false) {
        const headers = {};

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        if (!isFormData) {
            headers['Content-Type'] = 'application/json';
        }

        return headers;
    }

    async register(username, password) {
        try {
            const response = await fetch(`${API_URL}/api/auth/register`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async login(username, password) {
        try {
            const response = await fetch(`${API_URL}/api/auth/login`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (data.success && data.token) {
                this.setToken(data.token);
            }

            return data;
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async uploadFile(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${API_URL}/api/upload`, {
                method: 'POST',
                headers: this.getHeaders(true),
                body: formData
            });

            const data = await response.json();
            return data;
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async getFiles() {
        try {
            const response = await fetch(`${API_URL}/api/files`, {
                method: 'GET',
                headers: this.getHeaders()
            });

            const data = await response.json();
            return data;
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async deleteFile(fileId) {
        try {
            const response = await fetch(`${API_URL}/api/files/${fileId}`, {
                method: 'DELETE',
                headers: this.getHeaders()
            });

            const data = await response.json();
            return data;
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async analyzeFile(fileId) {
        try {
            const response = await fetch(`${API_URL}/api/analyze/${fileId}`, {
                method: 'POST',
                headers: this.getHeaders()
            });

            const data = await response.json();
            return data;
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async getAnalysis(fileId) {
        try {
            const response = await fetch(`${API_URL}/api/analysis/${fileId}`, {
                method: 'GET',
                headers: this.getHeaders()
            });

            const data = await response.json();
            return data;
        } catch (error) {
            return { success: false, message: error.message };
        }
    }
}

export default new ApiService();
