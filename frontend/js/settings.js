/* DupeManager — Settings View */

const Settings = {
    async render() {
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="space-y-6">
                <h2 class="text-2xl font-bold">Configuración</h2>

                <!-- Trash Section -->
                <div class="glass-card p-6 space-y-4">
                    <h3 class="text-lg font-semibold flex items-center gap-2">🗑️ Papelera de Reciclaje</h3>
                    <div id="trash-settings">
                        <p class="text-slate-400 text-sm">Cargando...</p>
                    </div>
                </div>

                <!-- Auto Scan Section -->
                <div class="glass-card p-6 space-y-4">
                    <h3 class="text-lg font-semibold flex items-center gap-2">⏰ Escaneo Automático</h3>
                    <div id="scan-settings">
                        <p class="text-slate-400 text-sm">Cargando...</p>
                    </div>
                </div>

                <!-- Notifications Section -->
                <div class="glass-card p-6 space-y-4">
                    <h3 class="text-lg font-semibold flex items-center gap-2">🔔 Notificaciones</h3>
                    <div id="notif-settings">
                        <p class="text-slate-400 text-sm">Cargando...</p>
                    </div>
                </div>

                <!-- Advanced Section -->
                <div class="glass-card p-6 space-y-4">
                    <h3 class="text-lg font-semibold flex items-center gap-2">🔧 Avanzado</h3>
                    <div class="flex flex-wrap gap-3">
                        <button id="btn-rebuild" class="btn-ghost border border-slate-600">
                            🔄 Reconstruir Base de Datos
                        </button>
                        <button id="btn-export" class="btn-ghost border border-slate-600">
                            📊 Exportar Resultados
                        </button>
                    </div>
                </div>

                <!-- Save Button -->
                <div class="flex justify-end">
                    <button id="btn-save" class="btn-primary">
                        💾 Guardar Cambios
                    </button>
                </div>
            </div>
        `;

        await this.loadSettings();

        // Event listeners
        document.getElementById('btn-save').addEventListener('click', () => this.saveSettings());
        document.getElementById('btn-rebuild').addEventListener('click', () => this.rebuildDb());
        document.getElementById('btn-export').addEventListener('click', () => this.exportData());
    },

    async loadSettings() {
        try {
            const data = await API.get('/settings');
            if (!data) return;

            // Trash
            document.getElementById('trash-settings').innerHTML = `
                ${Components.toggle('trash-enabled', data.trashEnabled, 'Activar papelera de reciclaje')}
                <p class="text-slate-500 text-xs mt-2 ml-14">
                    Los archivos eliminados se mueven a una carpeta temporal en vez de eliminarse permanentemente.
                </p>
                <div class="mt-4 ml-14 space-y-3">
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Tiempo antes de borrado automático:</label>
                        ${Components.durationSelector('trash-retention', data.trashRetentionValue, data.trashRetentionUnit)}
                    </div>
                    <button id="btn-empty-trash" class="btn-danger text-sm">
                        🗑️ Vaciar Papelera Ahora
                    </button>
                    <p class="text-slate-500 text-xs">⚠️ Esto eliminará permanentemente todos los archivos de la papelera.</p>
                </div>
            `;

            document.getElementById('btn-empty-trash')?.addEventListener('click', () => {
                Components.confirmModal(
                    'Vaciar Papelera',
                    '¿Estás seguro de que quieres eliminar permanentemente todos los archivos de la papelera?',
                    () => this.emptyTrash()
                );
            });

            // Auto Scan
            const lastAutoScan = data.lastAutoScan
                ? new Date(data.lastAutoScan).toLocaleString('es-ES')
                : 'Nunca';
            const nextAutoScan = data.nextAutoScan
                ? new Date(data.nextAutoScan).toLocaleString('es-ES')
                : 'Desactivado';

            document.getElementById('scan-settings').innerHTML = `
                ${Components.toggle('auto-scan-enabled', data.autoScanEnabled, 'Activar escaneo automático')}
                <div class="mt-4 ml-14 space-y-3">
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Frecuencia:</label>
                        ${Components.durationSelector('auto-scan', data.autoScanValue, data.autoScanUnit)}
                    </div>
                    <p class="text-slate-500 text-xs">Unidades: minutos (mín 5), horas (mín 1), días (mín 1), semanas (mín 1), meses (mín 1, máx 12)</p>
                    <div class="mt-3 p-3 bg-slate-800/50 rounded-lg text-sm space-y-1">
                        <div><span class="text-slate-400">Último escaneo automático:</span> <span class="text-white">${lastAutoScan}</span></div>
                        <div><span class="text-slate-400">Próximo escaneo programado:</span> <span class="text-white">${nextAutoScan}</span></div>
                    </div>
                </div>
            `;

            // Notifications
            document.getElementById('notif-settings').innerHTML = `
                <div class="space-y-4">
                    ${Components.toggle('notif-browser', data.notificationsBrowser, 'Notificaciones del navegador (Push)')}
                    <p class="text-slate-500 text-xs ml-14">Recibe alertas cuando se detecten nuevos duplicados. Solo funciona con el navegador abierto.</p>

                    <hr class="border-slate-700">

                    ${Components.toggle('notif-webhook', data.notificationsWebhookEnabled, 'Webhook')}
                    <div class="ml-14 space-y-3">
                        ${Components.textInput('notif-webhook-url', data.notificationsWebhookUrl, 'URL del webhook', 'url', 'https://ntfy.sh/mi-canal')}
                        <p class="text-slate-500 text-xs">Servicios compatibles: ntfy, Gotify, Discord, Telegram, Slack</p>
                        <button id="btn-test-webhook" class="btn-ghost text-sm border border-slate-600">
                            📤 Enviar prueba de webhook
                        </button>
                    </div>

                    <hr class="border-slate-700">

                    ${Components.toggle('notif-email', data.notificationsEmailEnabled, 'Email')}
                    <div class="ml-14 space-y-3">
                        ${Components.textInput('notif-smtp-host', data.notificationsEmailSmtpHost, 'SMTP Host', 'text', 'smtp.gmail.com')}
                        ${Components.textInput('notif-smtp-port', data.notificationsEmailSmtpPort, 'Puerto', 'number', '587')}
                        ${Components.textInput('notif-email-user', data.notificationsEmailUsername, 'Usuario', 'text', 'user@gmail.com')}
                        ${Components.textInput('notif-email-pass', data.notificationsEmailPassword, 'Contraseña', 'password')}
                        ${Components.textInput('notif-email-to', data.notificationsEmailTo, 'Email destino', 'email', 'user@gmail.com')}
                        <button id="btn-test-email" class="btn-ghost text-sm border border-slate-600">
                            ✉️ Enviar email de prueba
                        </button>
                    </div>
                </div>
            `;

            document.getElementById('btn-test-webhook')?.addEventListener('click', () => this.testWebhook());
            document.getElementById('btn-test-email')?.addEventListener('click', () => this.testEmail());

        } catch (err) {
            Toast.error('Error al cargar configuración');
        }
    },

    async saveSettings() {
        try {
            const settings = {
                trashEnabled: document.getElementById('trash-enabled')?.checked ?? true,
                trashRetentionValue: parseInt(document.getElementById('trash-retention-value')?.value || '30'),
                trashRetentionUnit: document.getElementById('trash-retention-unit')?.value || 'days',
                autoScanEnabled: document.getElementById('auto-scan-enabled')?.checked ?? true,
                autoScanValue: parseInt(document.getElementById('auto-scan-value')?.value || '7'),
                autoScanUnit: document.getElementById('auto-scan-unit')?.value || 'days',
                notificationsBrowser: document.getElementById('notif-browser')?.checked ?? false,
                notificationsWebhookEnabled: document.getElementById('notif-webhook')?.checked ?? false,
                notificationsWebhookUrl: document.getElementById('notif-webhook-url')?.value || '',
                notificationsEmailEnabled: document.getElementById('notif-email')?.checked ?? false,
                notificationsEmailSmtpHost: document.getElementById('notif-smtp-host')?.value || '',
                notificationsEmailSmtpPort: parseInt(document.getElementById('notif-smtp-port')?.value || '587'),
                notificationsEmailUsername: document.getElementById('notif-email-user')?.value || '',
                notificationsEmailPassword: document.getElementById('notif-email-pass')?.value || '',
                notificationsEmailTo: document.getElementById('notif-email-to')?.value || '',
            };

            await API.put('/settings', settings);
            Toast.success('Configuración guardada');
        } catch (err) {
            Toast.error('Error al guardar configuración');
        }
    },

    async emptyTrash() {
        try {
            Toast.info('Vaciando papelera...');
            const result = await API.post('/settings/trash/empty');
            Toast.success(`Papelera vaciada (${result.deleted || 0} archivos eliminados)`);
        } catch (err) {
            Toast.error('Error al vaciar la papelera');
        }
    },

    async rebuildDb() {
        Components.confirmModal(
            'Reconstruir Base de Datos',
            'Esto borrará la caché de escaneos y reconstruirá desde cero. ¿Continuar?',
            async () => {
                try {
                    Toast.info('Reconstruyendo base de datos...');
                    await API.post('/settings/rebuild-db');
                    Toast.success('Base de datos reconstruida');
                } catch (err) {
                    Toast.error('Error al reconstruir la BD');
                }
            }
        );
    },

    async exportData() {
        try {
            Toast.info('Exportando datos...');
            // TODO: Implement export endpoint
            Toast.info('Exportación no implementada aún');
        } catch (err) {
            Toast.error('Error al exportar');
        }
    },

    async testWebhook() {
        try {
            Toast.info('Enviando prueba de webhook...');
            await API.post('/settings/notifications/test-webhook');
            Toast.success('Webhook enviado correctamente');
        } catch (err) {
            Toast.error(`Error: ${err.message}`);
        }
    },

    async testEmail() {
        try {
            Toast.info('Enviando email de prueba...');
            await API.post('/settings/notifications/test-email');
            Toast.success('Email enviado correctamente');
        } catch (err) {
            Toast.error(`Error: ${err.message}`);
        }
    }
};
