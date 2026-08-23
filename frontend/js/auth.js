/* DupeManager — Auth Module */

const Auth = {
    init() {
        const form = document.getElementById('login-form');
        const error = document.getElementById('login-error');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            error.classList.add('hidden');

            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;

            try {
                const result = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password }),
                });

                const data = await result.json();

                if (!result.ok) {
                    error.textContent = data.detail || 'Error de autenticación';
                    error.classList.remove('hidden');
                    return;
                }

                API.setAuth(data.token, data.user);
                App.showMainView();
                Toast.success(`Bienvenido, ${data.user.name}`);
            } catch (err) {
                error.textContent = 'Error de conexión con el servidor';
                error.classList.remove('hidden');
            }
        });

        // Logout
        document.getElementById('logout-btn').addEventListener('click', () => {
            API.logout();
            App.showLoginView();
            Toast.info('Sesión cerrada');
        });
    }
};
