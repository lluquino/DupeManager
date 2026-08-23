/* DupeManager — Movies View */

const Movies = {
    currentPage: 1,
    pageSize: 25,
    filter: '',

    async render() {
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="space-y-6">
                <div class="flex items-center justify-between">
                    <h2 class="text-2xl font-bold">Películas Duplicadas</h2>
                </div>

                <!-- Filters -->
                <div class="glass-card p-4 flex flex-wrap gap-4 items-center">
                    <input type="text" id="movie-search" placeholder="Buscar película..."
                        class="flex-1 min-w-[200px] px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <label class="flex items-center gap-2 text-sm text-slate-400">
                        <input type="checkbox" id="movie-pending-only" class="rounded">
                        Solo pendientes
                    </label>
                </div>

                <!-- Table -->
                <div class="glass-card overflow-hidden">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Película</th>
                                <th>Año</th>
                                <th>Copias</th>
                                <th>Tamaño</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="movie-table-body">
                            <tr>
                                <td colspan="7" class="text-center py-8 text-slate-400">Cargando...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Pagination -->
                <div id="movie-pagination" class="flex items-center justify-between text-sm text-slate-400">
                    <span></span>
                    <div class="flex gap-2"></div>
                </div>
            </div>
        `;

        // Event listeners
        document.getElementById('movie-search').addEventListener('input', (e) => {
            this.filter = e.target.value;
            this.currentPage = 1;
            this.loadData();
        });

        document.getElementById('movie-pending-only').addEventListener('change', () => {
            this.currentPage = 1;
            this.loadData();
        });

        await this.loadData();
    },

    async loadData() {
        try {
            const data = await API.get('/movies');
            if (!data) return;

            const tbody = document.getElementById('movie-table-body');
            if (!data.length) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center py-8 text-slate-400">No se encontraron duplicados</td></tr>';
                return;
            }

            // Apply filter
            let filtered = data;
            if (this.filter) {
                const term = this.filter.toLowerCase();
                filtered = data.filter(m =>
                    m.name?.toLowerCase().includes(term)
                );
            }

            // Pending only
            const pendingOnly = document.getElementById('movie-pending-only')?.checked;
            if (pendingOnly) {
                filtered = filtered.filter(m => m.status === 'pending');
            }

            // Pagination
            const total = filtered.length;
            const totalPages = Math.ceil(total / this.pageSize);
            const start = (this.currentPage - 1) * this.pageSize;
            const page = filtered.slice(start, start + this.pageSize);

            tbody.innerHTML = page.map((movie, i) => `
                <tr>
                    <td class="text-slate-500">${start + i + 1}</td>
                    <td class="font-medium">${movie.name || 'Desconocida'}</td>
                    <td class="text-slate-400">${movie.year || '—'}</td>
                    <td>${movie.copies?.length || 0}</td>
                    <td>${this.formatSize(movie.totalSize)}</td>
                    <td>${this.statusBadge(movie.status)}</td>
                    <td>
                        <button class="text-blue-400 hover:text-blue-300 text-sm" onclick="Wizard.openGroup('${movie.groupId}', 'movie')">
                            Ver detalles
                        </button>
                    </td>
                </tr>
            `).join('');

            // Update pagination
            document.getElementById('movie-pagination').innerHTML = `
                <span>Mostrando ${start + 1}-${Math.min(start + this.pageSize, total)} de ${total}</span>
                <div class="flex gap-2">
                    <button class="btn-ghost text-sm" ${this.currentPage <= 1 ? 'disabled' : ''} onclick="Movies.goToPage(${this.currentPage - 1})">← Anterior</button>
                    <button class="btn-ghost text-sm" ${this.currentPage >= totalPages ? 'disabled' : ''} onclick="Movies.goToPage(${this.currentPage + 1})">Siguiente →</button>
                </div>
            `;
        } catch (err) {
            Toast.error('Error al cargar películas');
        }
    },

    goToPage(page) {
        this.currentPage = page;
        this.loadData();
    },

    formatSize(bytes) {
        if (!bytes) return '—';
        const gb = bytes / (1024 * 1024 * 1024);
        if (gb >= 1) return `${gb.toFixed(1)} GB`;
        const mb = bytes / (1024 * 1024);
        return `${mb.toFixed(0)} MB`;
    },

    statusBadge(status) {
        const badges = {
            pending: '<span class="quality-badge quality-normal">Pendiente</span>',
            resolved: '<span class="quality-badge quality-best">Resuelto</span>',
            ignored: '<span class="quality-badge quality-poor">Ignorado</span>',
        };
        return badges[status] || status;
    }
};
