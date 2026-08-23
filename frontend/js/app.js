/* DupeManager — App Router */

const App = {
    currentRoute: '/',

    init() {
        Auth.init();
        Toast.init();

        // Check auth state
        if (API.isAuthenticated()) {
            this.showMainView();
        } else {
            this.showLoginView();
        }

        // Listen for hash changes
        window.addEventListener('hashchange', () => this.handleRoute());
    },

    showLoginView() {
        document.getElementById('login-view').classList.remove('hidden');
        document.getElementById('main-view').classList.add('hidden');
    },

    showMainView() {
        document.getElementById('login-view').classList.add('hidden');
        document.getElementById('main-view').classList.remove('hidden');

        // Set user name
        if (API.user) {
            document.getElementById('user-name').textContent = API.user.name;
        }

        // Handle initial route
        this.handleRoute();
    },

    handleRoute() {
        const hash = window.location.hash.slice(1) || '/';
        this.currentRoute = hash;

        // Update nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            const route = link.getAttribute('data-route');
            link.classList.toggle('active', route === hash);
        });

        // Render view
        switch (hash) {
            case '/':
                Dashboard.render();
                break;
            case '/episodes':
                Episodes.render();
                break;
            case '/movies':
                Movies.render();
                break;
            case '/ignored':
                Ignored.render();
                break;
            case '/settings':
                Settings.render();
                break;
            default:
                Dashboard.render();
        }
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => App.init());
