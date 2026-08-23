/* DupeManager — Wizard Modal */

const Wizard = {
    groups: [],
    currentIndex: 0,
    type: 'episode', // 'episode' or 'movie'

    async open() {
        // Load all pending groups
        try {
            const episodes = await API.get('/episodes');
            const movies = await API.get('/movies');

            this.groups = [
                ...(episodes || []).filter(g => g.status === 'pending'),
                ...(movies || []).filter(g => g.status === 'pending'),
            ];

            // Sort by size descending (most recoverable first)
            this.groups.sort((a, b) => (b.totalSize || 0) - (a.totalSize || 0));

            if (this.groups.length === 0) {
                Toast.info('No hay duplicados pendientes para revisar');
                return;
            }

            this.currentIndex = 0;
            this.renderModal();
        } catch (err) {
            Toast.error('Error al cargar duplicados');
        }
    },

    async openGroup(groupId, type) {
        try {
            const endpoint = type === 'episode' ? '/episodes' : '/movies';
            const group = await API.get(`${endpoint}/${groupId}`);

            if (!group) {
                Toast.error('Grupo no encontrado');
                return;
            }

            this.groups = [group];
            this.currentIndex = 0;
            this.type = type;
            this.renderModal();
        } catch (err) {
            Toast.error('Error al cargar el grupo');
        }
    },

    renderModal() {
        const group = this.groups[this.currentIndex];
        if (!group) {
            this.close();
            return;
        }

        const isEpisode = group.seriesName !== undefined;
        this.type = isEpisode ? 'episode' : 'movie';

        const title = isEpisode
            ? `${group.seriesName} — S${String(group.season).padStart(2, '0')}E${String(group.episode).padStart(2, '0')}`
            : `${group.name}${group.year ? ` (${group.year})` : ''}`;

        const progress = ((this.currentIndex + 1) / this.groups.length * 100).toFixed(0);

        // Find best copy
        const bestId = group.copies?.reduce((best, copy) =>
            (copy.qualityScore > (best?.qualityScore || -1)) ? copy : best
        , null)?.id;

        const overlay = document.createElement('div');
        overlay.id = 'wizard-overlay';
        overlay.className = 'wizard-overlay';
        overlay.innerHTML = `
            <div class="wizard-content">
                <!-- Header -->
                <div class="p-4 border-b border-slate-700 flex items-center justify-between">
                    <div>
                        <h3 class="text-lg font-bold">Revisar Duplicados</h3>
                        <p class="text-slate-400 text-sm">Grupo ${this.currentIndex + 1} de ${this.groups.length}</p>
                    </div>
                    <button onclick="Wizard.close()" class="text-slate-400 hover:text-white text-2xl">&times;</button>
                </div>

                <!-- Progress bar -->
                <div class="px-4 py-2 bg-slate-900/50">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%"></div>
                    </div>
                </div>

                <!-- Content -->
                <div class="p-6">
                    <div class="mb-6">
                        <h4 class="text-xl font-bold text-blue-400">${title}</h4>
                    </div>

                    <!-- Copies -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                        ${(group.copies || []).map(copy => `
                            <div class="copy-card ${copy.id === bestId ? 'best' : ''}">
                                <div class="flex items-center justify-between mb-3">
                                    <span class="quality-badge ${copy.id === bestId ? 'quality-best' : 'quality-normal'}">
                                        ${copy.id === bestId ? '✅ Mejor' : '⚪ Copia'}
                                    </span>
                                    <span class="text-sm text-slate-400">Score: ${copy.qualityScore}</span>
                                </div>
                                <div class="space-y-2 text-sm">
                                    <div class="flex items-center gap-2">
                                        <span class="text-slate-500">📁</span>
                                        <span class="text-slate-300 truncate" title="${copy.path}">${copy.filename}</span>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <span class="text-slate-500">🎬</span>
                                        <span class="text-slate-300">${copy.resolution || 'Desconocida'}</span>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <span class="text-slate-500">🎞️</span>
                                        <span class="text-slate-300">${copy.codec || 'Desconocido'}</span>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <span class="text-slate-500">📦</span>
                                        <span class="text-slate-300">${this.formatSize(copy.size)}</span>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- Actions -->
                <div class="p-4 border-t border-slate-700 bg-slate-900/30">
                    <div class="flex flex-wrap gap-3 justify-center">
                        <button onclick="Wizard.action('keep')" class="btn-success">
                            ✅ Conservar la mejor
                        </button>
                        <button onclick="Wizard.action('ignore')" class="btn-ghost border border-slate-600">
                            ⏭️ Ignorar este grupo
                        </button>
                        <button onclick="Wizard.action('skip')" class="btn-ghost border border-slate-600">
                            ⏩ Omitir
                        </button>
                    </div>
                </div>

                <!-- Navigation -->
                <div class="p-4 border-t border-slate-700 flex justify-between">
                    <button onclick="Wizard.prev()" class="btn-ghost" ${this.currentIndex <= 0 ? 'disabled' : ''}>
                        ← Anterior
                    </button>
                    <button onclick="Wizard.next()" class="btn-ghost" ${this.currentIndex >= this.groups.length - 1 ? 'disabled' : ''}>
                        Siguiente →
                    </button>
                </div>
            </div>
        `;

        // Remove existing overlay
        document.getElementById('wizard-overlay')?.remove();
        document.body.appendChild(overlay);
    },

    async action(type) {
        const group = this.groups[this.currentIndex];
        if (!group) return;

        try {
            const endpoint = this.type === 'episode' ? '/episodes' : '/movies';
            await API.post(`${endpoint}/${group.groupId}/action`, { action: type });

            const messages = {
                keep: 'Mejor copia conservada, peores eliminadas',
                ignore: 'Grupo marcado como ignorado',
                skip: 'Omitido, permanece pendiente',
            };

            Toast.success(messages[type]);

            if (type !== 'skip') {
                // Remove from list and continue
                this.groups.splice(this.currentIndex, 1);
                if (this.currentIndex >= this.groups.length) {
                    this.currentIndex = Math.max(0, this.groups.length - 1);
                }
            } else {
                this.next();
            }

            if (this.groups.length === 0) {
                Toast.success('¡Todos los duplicados revisados!');
                this.close();
            } else {
                this.renderModal();
            }
        } catch (err) {
            Toast.error(`Error: ${err.message}`);
        }
    },

    next() {
        if (this.currentIndex < this.groups.length - 1) {
            this.currentIndex++;
            this.renderModal();
        }
    },

    prev() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.renderModal();
        }
    },

    close() {
        document.getElementById('wizard-overlay')?.remove();
        // Refresh current view
        if (typeof Dashboard.loadData === 'function') Dashboard.loadData();
    },

    formatSize(bytes) {
        if (!bytes) return '—';
        const gb = bytes / (1024 * 1024 * 1024);
        if (gb >= 1) return `${gb.toFixed(1)} GB`;
        const mb = bytes / (1024 * 1024);
        return `${mb.toFixed(0)} MB`;
    }
};
