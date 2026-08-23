/* DupeManager — Dashboard View */

const Dashboard = {
    async render() {
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="space-y-6">
                <div class="flex items-center justify-between">
                    <h2 class="text-2xl font-bold">Dashboard</h2>
                    <div class="flex gap-3">
                        <button id="btn-review" class="btn-primary" disabled>
                            🔄 Revisar Duplicados
                        </button>
                        <button id="btn-scan" class="btn-ghost border border-slate-600">
                            🔍 Escanear Ahora
                        </button>
                    </div>
                </div>

                <!-- Stats Cards -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4" id="stats-cards">
                    <div class="stat-card">
                        <div class="text-slate-400 text-sm">Episodios</div>
                        <div class="text-2xl font-bold text-blue-400" id="stat-episodes">—</div>
                    </div>
                    <div class="stat-card">
                        <div class="text-slate-400 text-sm">Películas</div>
                        <div class="text-2xl font-bold text-purple-400" id="stat-movies">—</div>
                    </div>
                    <div class="stat-card">
                        <div class="text-slate-400 text-sm">Duplicados</div>
                        <div class="text-2xl font-bold text-yellow-400" id="stat-duplicates">—</div>
                    </div>
                    <div class="stat-card">
                        <div class="text-slate-400 text-sm">Espacio recuperable</div>
                        <div class="text-2xl font-bold text-green-400" id="stat-size">—</div>
                    </div>
                </div>

                <!-- Last Scan -->
                <div class="glass-card p-4 flex items-center justify-between">
                    <div>
                        <span class="text-slate-400 text-sm">Último escaneo: </span>
                        <span id="last-scan" class="text-white">Nunca</span>
                    </div>
                </div>

                <!-- Loading -->
                <div id="dashboard-loading" class="text-center py-12 text-slate-400">
                    Cargando datos...
                </div>
            </div>
        `;

        // Load data
        await this.loadData();

        // Event listeners
        document.getElementById('btn-scan').addEventListener('click', () => this.startScan());
        document.getElementById('btn-review').addEventListener('click', () => Wizard.open());
    },

    async loadData() {
        try {
            const data = await API.get('/dashboard');
            if (!data) return;

            document.getElementById('stat-episodes').textContent = data.pendingEpisodes.toLocaleString();
            document.getElementById('stat-movies').textContent = data.pendingMovies.toLocaleString();
            document.getElementById('stat-duplicates').textContent = data.totalDuplicates.toLocaleString();
            document.getElementById('stat-size').textContent = `${data.recoverableSizeGB} GB`;
            document.getElementById('last-scan').textContent = data.lastScan
                ? new Date(data.lastScan).toLocaleString('es-ES')
                : 'Nunca';

            document.getElementById('dashboard-loading').classList.add('hidden');

            if (data.totalDuplicates > 0) {
                document.getElementById('btn-review').disabled = false;
            }
        } catch (err) {
            Toast.error('Error al cargar el dashboard');
        }
    },

    async startScan() {
        const btn = document.getElementById('btn-scan');
        btn.disabled = true;
        btn.textContent = '⏳ Escaneando...';

        Toast.progress('Iniciando escaneo...', 0);

        try {
            // TODO: Implement polling for scan progress
            const result = await API.post('/scan');
            Toast.closeProgress();
            Toast.success('Escaneo completado');
            await this.loadData();
        } catch (err) {
            Toast.closeProgress();
            Toast.error(`Error en el escaneo: ${err.message}`);
        } finally {
            btn.disabled = false;
            btn.textContent = '🔍 Escanear Ahora';
        }
    }
};
