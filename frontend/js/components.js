/* DupeManager — Reusable Components */

const Components = {
    /**
     * Creates a duration selector (value + unit)
     */
    durationSelector(id, value, unit, options = {}) {
        const units = [
            { value: 'minutes', label: 'minutos' },
            { value: 'hours', label: 'horas' },
            { value: 'days', label: 'días' },
            { value: 'weeks', label: 'semanas' },
            { value: 'months', label: 'meses' },
        ];

        const unitOptions = units
            .map(u => `<option value="${u.value}" ${u.value === unit ? 'selected' : ''}>${u.label}</option>`)
            .join('');

        return `
            <div class="duration-selector">
                <input type="number" id="${id}-value" value="${value}" min="1"
                    class="duration-value px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <select id="${id}-unit"
                    class="px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    ${unitOptions}
                </select>
            </div>
        `;
    },

    /**
     * Creates a toggle switch
     */
    toggle(id, checked, label) {
        return `
            <label class="flex items-center gap-3 cursor-pointer">
                <div class="relative">
                    <input type="checkbox" id="${id}" ${checked ? 'checked' : ''} class="sr-only peer">
                    <div class="w-11 h-6 bg-slate-600 rounded-full peer peer-checked:bg-blue-600 transition-colors"></div>
                    <div class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                </div>
                <span class="text-sm text-slate-300">${label}</span>
            </label>
        `;
    },

    /**
     * Creates a text input
     */
    textInput(id, value, label, type = 'text', placeholder = '') {
        return `
            <div>
                <label class="block text-sm font-medium text-slate-300 mb-1">${label}</label>
                <input type="${type}" id="${id}" value="${value || ''}" placeholder="${placeholder}"
                    class="w-full px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            </div>
        `;
    },

    /**
     * Creates a confirmation modal
     */
    confirmModal(title, message, onConfirm, onCancel) {
        const overlay = document.createElement('div');
        overlay.className = 'wizard-overlay';
        overlay.innerHTML = `
            <div class="wizard-content p-6 max-w-md">
                <h3 class="text-xl font-bold mb-4">${title}</h3>
                <p class="text-slate-400 mb-6">${message}</p>
                <div class="flex gap-3 justify-end">
                    <button class="btn-ghost" id="confirm-cancel">Cancelar</button>
                    <button class="btn-danger" id="confirm-ok">Confirmar</button>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);

        overlay.querySelector('#confirm-cancel').addEventListener('click', () => {
            overlay.remove();
            if (onCancel) onCancel();
        });

        overlay.querySelector('#confirm-ok').addEventListener('click', () => {
            overlay.remove();
            if (onConfirm) onConfirm();
        });

        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.remove();
                if (onCancel) onCancel();
            }
        });
    }
};
