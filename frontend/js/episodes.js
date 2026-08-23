/* DupeManager — Episodes View */

const Episodes = {
    currentPage: 1,
    pageSize: 25,
    filter: '',

    async render() {
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="space-y-6">
                <div class="flex items-center justify-between">
                    <h2 class="text-2xl font-bold">Episodios Duplicados</h2>
                </div>

                <!-- Filters -->
                <div class="glass-card p-4 flex flex-wrap gap-4 items-center">
                    <input type="text" id="ep-search" placeholder="Buscar serie o episodio..."
                        class="flex-1 min-w-[200px] px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <label class="flex items-center gap-2 text-sm text-slate-400">
                        <input type="checkbox" id="ep-pending-only" class="rounded">
                        Solo pendientes
                    </label>
                </div>

                <!-- Table -->
                <div class="glass-card overflow-hidden">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Serie</th>
                                <th>Episodio</th>
                                <th>Copias</th>
                                <th>Tamaño</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="ep-table-body">
                            <tr>
                                <td colspan="7" class="text-center py-8 text-slate-400">Cargando...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Pagination -->
                <div id="ep-pagination" class="flex items-center justify-between text-sm text-slate-400">
                    <span></span>
                    <div class="flex gap-2"></div>
                </div>
            </div>
        `;

        // Event listeners
        document.getElementById('ep-search').addEventListener('input', (e) => {
            this.filter = e.target.value;
            this.currentPage = 1;
            this.loadData();
        });

        document.getElementById('ep-pending-only').addEventListener('change', () => {
            this.currentPage = 1;
            this.loadData();
        });

        await this.loadData();
    },

    async loadData() {
        try {
            const data = await API.get('/episodes');
            if (!data) return;

            const tbody = document.getElementById('ep-table-body');
            if (!data.length) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center py-8 text-slate-400">No se encontraron duplicados</td></tr>';
                return;
            }

            // Apply filter
            let filtered = data;
            if (this.filter) {
                const term = this.filter.toLowerCase();
                filtered = data.filter(ep =>
                    ep.seriesName?.toLowerCase().includes(term) ||
                    `S${String(ep.season).padStart(2, '0')}E${String(ep.episode).padStart(2, '0')}`.toLowerCase().includes(term)
                );
            }

            // Pending only
            const pendingOnly = document.getElementById('ep-pending-only')?.checked;
            if (pendingOnly) {
                filtered = filtered.filter(ep => ep.status === 'pending');
            }

            // Pagination
            const total = filtered.length;
            const totalPages = Math.ceil(total / this.pageSize);
            const start = (this.currentPage - 1) * this.pageSize;
            const page = filtered.slice(start, start + this.pageSize);

            tbody.innerHTML = page.map((ep, i) => `
                <tr>
                    <td class="text-slate-500">${start + i + 1}</td>
                    <td class="font-medium">${ep.seriesName || 'Desconocida'}</td>
                    <td class="text-slate-400">S${String(ep.season).padStart(2, '0')}E${String(ep.episode).padStart(2, '0')}</td>
                    <td>${ep.copies?.length || 0}</td>
                    <td>${this.formatSize(ep.totalSize)}</td>
                    <td>${this.statusBadge(ep.status)}</td>
                    <td>
                        <button class="text-blue-400 hover:text-blue-300 text-sm" onclick="Wizard.openGroup('${ep.groupId}', 'episode')">
                            Ver detalles
                        </button>
                    </td>
                </tr>
            `).join('');

            // Update pagination
            document.getElementById('ep-pagination').innerHTML = `
                <span>Mostrando ${start + 1}-${Math.min(start + this.pageSize, total)} de ${total}</span>
                <div class="flex gap-2">
                    <button class="btn-ghost text-sm" ${this.currentPage <= 1 ? 'disabled' : ''} onclick="Episodes.goToPage(${this.currentPage - 1})">← Anterior</button>
                    <button class="btn-ghost text-sm" ${this.currentPage >= totalPages ? 'disabled' : ''} onclick="Episodes.goToPage(${this.currentPage + 1})">Siguiente →</button>
                </div>
            `;
        } catch (err) {
            Toast.error('Error al cargar episodios');
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
