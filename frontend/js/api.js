/* DupeManager — API Client */

const API = {
    token: localStorage.getItem('dm_token'),
    user: JSON.parse(localStorage.getItem('dm_user') || 'null'),

    async request(method, path, body = null) {
        const headers = { 'Content-Type': 'application/json' };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const options = { method, headers };
        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(`/api${path}`, options);

        if (response.status === 401) {
            this.logout();
            window.location.hash = '#/';
            throw new Error('Sesión expirada, inicia sesión de nuevo');
        }

        if (!response.ok) {
            let detail = 'Error en la petición';
            try {
                const error = await response.json();
                detail = error.detail || detail;
            } catch (e) {
                // Response is not JSON
            }
            throw new Error(detail);
        }

        return response.json();
    },

    get(path) { return this.request('GET', path); },
    post(path, body) { return this.request('POST', path, body); },
    put(path, body) { return this.request('PUT', path, body); },
    delete(path) { return this.request('DELETE', path); },

    setAuth(token, user) {
        this.token = token;
        this.user = user;
        localStorage.setItem('dm_token', token);
        localStorage.setItem('dm_user', JSON.stringify(user));
    },

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('dm_token');
        localStorage.removeItem('dm_user');
    },

    isAuthenticated() {
        return !!this.token;
    }
};
