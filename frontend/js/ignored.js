/* DupeManager — Ignored View */

const Ignored = {
    async render() {
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="space-y-6">
                <div class="flex items-center justify-between">
                    <h2 class="text-2xl font-bold">Duplicados Ignorados</h2>
                    <button id="btn-restore-selected" class="btn-ghost border border-slate-600" disabled>
                        🔄 Restaurar seleccionados
                    </button>
                </div>

                <div class="glass-card p-4 text-slate-400 text-sm">
                    Estos duplicados no se mostrarán en el dashboard ni en el wizard de revisión.
                    Puedes restaurarlos si cambias de opinión.
                </div>

                <!-- Table -->
                <div class="glass-card overflow-hidden">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th><input type="checkbox" id="ign-select-all" class="rounded"></th>
                                <th>Nombre</th>
                                <th>Tipo</th>
                                <th>Ignorado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="ign-table-body">
                            <tr>
                                <td colspan="5" class="text-center py-8 text-slate-400">Cargando...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        // Event listeners
        document.getElementById('ign-select-all').addEventListener('change', (e) => {
            document.querySelectorAll('.ign-checkbox').forEach(cb => {
                cb.checked = e.target.checked;
            });
            this.updateRestoreButton();
        });

        document.getElementById('btn-restore-selected').addEventListener('click', () => this.restoreSelected());

        await this.loadData();
    },

    async loadData() {
        try {
            const data = await API.get('/ignored');
            if (!data) return;

            const tbody = document.getElementById('ign-table-body');
            if (!data.length) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center py-8 text-slate-400">No hay duplicados ignorados</td></tr>';
                return;
            }

            tbody.innerHTML = data.map(item => `
                <tr>
                    <td><input type="checkbox" class="ign-checkbox rounded" value="${item.groupId}" onchange="Ignored.updateRestoreButton()"></td>
                    <td class="font-medium">${item.name}</td>
                    <td class="text-slate-400">${item.itemType === 'episode' ? 'Episodio' : 'Película'}</td>
                    <td class="text-slate-400">${new Date(item.ignoredAt).toLocaleDateString('es-ES')}</td>
                    <td>
                        <button class="text-blue-400 hover:text-blue-300 text-sm" onclick="Ignored.restore('${item.groupId}')">
                            Restaurar
                        </button>
                    </td>
                </tr>
            `).join('');
        } catch (err) {
            Toast.error('Error al cargar ignorados');
        }
    },

    updateRestoreButton() {
        const checked = document.querySelectorAll('.ign-checkbox:checked').length;
        document.getElementById('btn-restore-selected').disabled = checked === 0;
    },

    async restore(groupId) {
        try {
            await API.post(`/ignored/${groupId}/restore`);
            Toast.success('Duplicado restaurado');
            await this.loadData();
        } catch (err) {
            Toast.error('Error al restaurar');
        }
    },

    async restoreSelected() {
        const checked = document.querySelectorAll('.ign-checkbox:checked');
        const ids = Array.from(checked).map(cb => cb.value);

        if (ids.length === 0) return;

        Components.confirmModal(
            'Restaurar duplicados',
            `¿Restaurar ${ids.length} duplicado(s) ignorado(s)?`,
            async () => {
                try {
                    await API.post('/ignored/restore-many', { groupIds: ids });
                    Toast.success(`${ids.length} duplicado(s) restaurado(s)`);
                    await this.loadData();
                } catch (err) {
                    Toast.error('Error al restaurar');
                }
            }
        );
    }
};
