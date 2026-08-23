/* DupeManager — Wizard Modal */

const Wizard = {
    groups: [],
    currentIndex: 0,
    type: 'episode',
    selectedCopies: {},  // { groupId: [copyId1, copyId2] }

    async open() {
        try {
            const episodes = await API.get('/episodes');
            const movies = await API.get('/movies');

            this.groups = [
                ...(episodes || []).filter(g => g.status === 'pending'),
                ...(movies || []).filter(g => g.status === 'pending'),
            ];

            this.groups.sort((a, b) => (b.totalSize || 0) - (a.totalSize || 0));

            if (this.groups.length === 0) {
                Toast.info('No hay duplicados pendientes para revisar');
                return;
            }

            this.currentIndex = 0;
            this.selectedCopies = {};
            this.renderModal();
        } catch (err) {
            Toast.error('Error al cargar duplicados');
        }
    },

    async openGroup(groupId, type) {
        try {
            const endpoint = type === 'episode' ? '/episodes' : '/movies';
            const group = await API.get(`${endpoint}/${groupId}`);

            if (!group || group.error) {
                Toast.error(group.error || 'Grupo no encontrado');
                return;
            }

            this.groups = [group];
            this.currentIndex = 0;
            this.type = type;
            this.selectedCopies = {};
            this.renderModal();
        } catch (err) {
            Toast.error('Error al cargar el grupo');
        }
    },

    getSelectedCopies() {
        const group = this.groups[this.currentIndex];
        if (!group) return [];
        return this.selectedCopies[group.groupId] || [];
    },

    toggleCopySelection(copyId) {
        const group = this.groups[this.currentIndex];
        if (!group) return;

        if (!this.selectedCopies[group.groupId]) {
            this.selectedCopies[group.groupId] = [];
        }

        const selected = this.selectedCopies[group.groupId];
        const idx = selected.indexOf(copyId);

        if (idx === -1) {
            selected.push(copyId);
        } else {
            selected.splice(idx, 1);
        }

        this.updateCopyCards();
        this.updateActionButtons();
    },

    selectBest() {
        const group = this.groups[this.currentIndex];
        if (!group || !group.copies) return;

        // Find best copy by score
        const best = group.copies.reduce((best, copy) =>
            (copy.qualityScore > (best?.qualityScore || -1)) ? copy : best
        , null);

        if (best) {
            this.selectedCopies[group.groupId] = [best.id];
            this.updateCopyCards();
            this.updateActionButtons();
        }
    },

    updateCopyCards() {
        const group = this.groups[this.currentIndex];
        if (!group) return;

        const selected = this.getSelectedCopies();

        group.copies.forEach(copy => {
            const card = document.getElementById(`copy-card-${copy.id}`);
            if (!card) return;

            const isSelected = selected.includes(copy.id);
            card.classList.toggle('selected', isSelected);

            // Update badge text
            const badge = card.querySelector('.quality-badge');
            if (badge) {
                if (isSelected) {
                    badge.className = 'quality-badge quality-selected';
                    badge.textContent = '☑️ Seleccionada';
                } else if (copy.id === group.copies.reduce((best, c) =>
                    (c.qualityScore > (best?.qualityScore || -1)) ? c : best, null)?.id) {
                    badge.className = 'quality-badge quality-best';
                    badge.textContent = '✅ Mejor';
                } else {
                    badge.className = 'quality-badge quality-normal';
                    badge.textContent = '⚪ Copia';
                }
            }
        });
    },

    updateActionButtons() {
        const selected = this.getSelectedCopies();
        const keepBtn = document.getElementById('btn-keep-selected');
        if (keepBtn) {
            keepBtn.disabled = selected.length === 0;
            keepBtn.textContent = selected.length > 0
                ? `✅ Conservar ${selected.length} seleccionada${selected.length > 1 ? 's' : ''}`
                : '✅ Conservar seleccionadas';
        }
    },

    toggleTracks(type, copyId) {
        const container = document.getElementById(`${type}-tracks-${copyId}`);
        const btn = document.getElementById(`${type}-toggle-${copyId}`);
        if (!container || !btn) return;

        const isExpanded = container.classList.contains('expanded');
        container.classList.toggle('expanded');
        btn.textContent = isExpanded ? btn.dataset.collapsedText : btn.dataset.expandedText;
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
        const selected = this.getSelectedCopies();

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
                <div class="p-6 overflow-y-auto" style="max-height: 60vh;">
                    <div class="mb-4">
                        <h4 class="text-xl font-bold text-blue-400">${title}</h4>
                    </div>

                    <!-- Copies -->
                    <div class="space-y-4 mb-6">
                        ${(group.copies || []).map(copy => this.renderCopyCard(copy, bestId, selected)).join('')}
                    </div>
                </div>

                <!-- Actions -->
                <div class="p-4 border-t border-slate-700 bg-slate-900/30">
                    <div class="flex flex-wrap gap-3 justify-center">
                        <button onclick="Wizard.selectBest()" class="btn-ghost border border-slate-600 text-sm">
                            🎯 Seleccionar mejor
                        </button>
                        <button id="btn-keep-selected" onclick="Wizard.actionKeepSelected()" class="btn-success" disabled>
                            ✅ Conservar seleccionadas
                        </button>
                        <button onclick="Wizard.action('ignore')" class="btn-ghost border border-slate-600">
                            ⏭️ Ignorar
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

        document.getElementById('wizard-overlay')?.remove();
        document.body.appendChild(overlay);
    },

    renderCopyCard(copy, bestId, selected) {
        const isSelected = selected.includes(copy.id);
        const isBest = copy.id === bestId;

        // Build audio string
        const audioStr = (copy.audioTracks || []).map(t => {
            const parts = [];
            if (t.codec) parts.push(t.codec.toUpperCase());
            if (t.channelLayout) parts.push(t.channelLayout);
            else if (t.channels) parts.push(`${t.channels}ch`);
            if (t.title) parts.push(t.title);
            else if (t.language) parts.push(t.language);
            return parts.join(' ');
        }).join(' | ');

        // Build subtitle string
        const subStr = (copy.subtitleTracks || []).map(t => {
            const parts = [];
            if (t.codec) parts.push(t.codec.toUpperCase());
            if (t.title) parts.push(t.title);
            else if (t.language) parts.push(t.language);
            if (t.isForced) parts.push('(Forced)');
            return parts.join(' ');
        }).join(' | ');

        // Short path for display
        const shortPath = copy.path
            ? copy.path.replace(/^\/media\//, '').replace(/\/[^/]+$/, '/')
            : '';

        return `
            <div id="copy-card-${copy.id}" class="copy-card ${isBest ? 'best' : ''} ${isSelected ? 'selected' : ''} cursor-pointer"
                 onclick="Wizard.toggleCopySelection(${copy.id})">
                <!-- Header -->
                <div class="flex items-center gap-3 mb-3">
                    <span class="quality-badge ${isBest ? 'quality-best' : 'quality-normal'}">
                        ${isSelected ? '☑️ Seleccionada' : isBest ? '✅ Mejor' : '⚪ Copia'}
                    </span>
                    <span class="text-sm text-slate-400 ml-auto">Score: ${copy.qualityScore}</span>
                </div>

                <!-- File info -->
                <div class="space-y-1.5 text-sm mb-3">
                    <div class="flex items-center gap-2">
                        <span class="text-slate-500">📁</span>
                        <span class="text-slate-300 truncate" title="${copy.path}">${copy.filename}</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-slate-500">📍</span>
                        <span class="text-slate-400 text-xs truncate" title="${copy.path}">${shortPath}</span>
                    </div>
                </div>

                <!-- Video info -->
                <div class="flex flex-wrap gap-3 text-sm mb-3">
                    <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        🎬 ${copy.resolution || '?'}
                    </span>
                    <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        🎞️ ${(copy.codec || '?').toUpperCase()}
                    </span>
                    <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        📦 ${this.formatSize(copy.size)}
                    </span>
                </div>

                <!-- Audio tracks -->
                ${audioStr ? `
                    <div class="text-sm mb-2">
                        <span class="text-slate-500">🎧</span>
                        <span class="text-slate-300">${audioStr}</span>
                    </div>
                ` : `
                    <div class="text-sm mb-2">
                        <span class="text-slate-500">🎧</span>
                        <span class="text-slate-500 italic">Sin pistas de audio</span>
                    </div>
                `}

                <!-- Subtitle tracks -->
                ${subStr ? `
                    <div class="text-sm">
                        <span class="text-slate-500">📝</span>
                        <span class="text-slate-300">${subStr}</span>
                    </div>
                ` : `
                    <div class="text-sm">
                        <span class="text-slate-500">📝</span>
                        <span class="text-slate-500 italic">Sin subtítulos</span>
                    </div>
                `}
            </div>
        `;
    },

    async actionKeepSelected() {
        const group = this.groups[this.currentIndex];
        if (!group) return;

        const selected = this.getSelectedCopies();
        if (selected.length === 0) {
            Toast.info('Selecciona al menos una copia a conservar');
            return;
        }

        await this.action('keep', selected);
    },

    async action(type, keepCopyIds = null) {
        const group = this.groups[this.currentIndex];
        if (!group) return;

        try {
            const endpoint = this.type === 'episode' ? '/episodes' : '/movies';
            const body = { action: type };
            if (keepCopyIds) body.keepCopyIds = keepCopyIds;

            await API.post(`${endpoint}/${group.groupId}/action`, body);

            const messages = {
                keep: keepCopyIds && keepCopyIds.length > 0
                    ? `${keepCopyIds.length} copia(s) conservada(s), el resto eliminada(s)`
                    : 'Mejor copia conservada, peores eliminadas',
                ignore: 'Grupo marcado como ignorado',
                skip: 'Omitido, permanece pendiente',
            };

            Toast.success(messages[type]);

            if (type !== 'skip') {
                // Remove current group - next group takes its position
                this.groups.splice(this.currentIndex, 1);
                // Keep index same (next group is now at currentIndex)
                // If we removed the last item, go back one
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
