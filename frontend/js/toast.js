/* DupeManager — Toast System */

const Toast = {
    container: null,

    init() {
        this.container = document.getElementById('toast-container');
    },

    show(message, type = 'info', duration = 3000) {
        if (!this.container) this.init();

        const toast = document.createElement('div');
        toast.className = `toast-enter flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg max-w-sm ${this.getStyles(type)}`;

        const icon = this.getIcon(type);
        toast.innerHTML = `
            <span class="text-lg">${icon}</span>
            <span class="text-sm flex-1">${message}</span>
            <button onclick="this.parentElement.remove()" class="text-white/60 hover:text-white ml-2">&times;</button>
        `;

        this.container.appendChild(toast);

        if (duration > 0) {
            setTimeout(() => {
                toast.classList.remove('toast-enter');
                toast.classList.add('toast-exit');
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }

        return toast;
    },

    success(message, duration = 0) {
        return this.show(message, 'success', duration);
    },

    error(message, duration = 0) {
        return this.show(message, 'error', duration);
    },

    info(message, duration = 5000) {
        return this.show(message, 'info', duration);
    },

    progress(message, progress = 0) {
        if (!this.container) this.init();

        // Update existing progress toast instead of recreating
        const existing = document.getElementById('toast-progress');
        if (existing) {
            const fill = existing.querySelector('.progress-fill');
            const pct = existing.querySelector('.progress-pct');
            const msg = existing.querySelector('.progress-msg');
            if (fill) fill.style.width = `${progress}%`;
            if (pct) pct.textContent = `${Math.round(progress)}%`;
            if (msg) msg.textContent = message;
            return existing;
        }

        const toast = document.createElement('div');
        toast.id = 'toast-progress';
        toast.className = 'toast-enter flex flex-col gap-2 px-4 py-3 rounded-lg shadow-lg max-w-sm bg-blue-900/90 border border-blue-700';

        toast.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="text-lg">⏳</span>
                <span class="text-sm flex-1 progress-msg">${message}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${progress}%"></div>
            </div>
            <span class="text-xs text-blue-300 text-right progress-pct">${Math.round(progress)}%</span>
        `;

        this.container.appendChild(toast);
        return toast;
    },

    closeProgress() {
        const toast = document.getElementById('toast-progress');
        if (toast) {
            toast.classList.remove('toast-enter');
            toast.classList.add('toast-exit');
            setTimeout(() => toast.remove(), 300);
        }
    },

    getStyles(type) {
        switch (type) {
            case 'success': return 'bg-green-900/90 border border-green-700 text-green-100';
            case 'error': return 'bg-red-900/90 border border-red-700 text-red-100';
            case 'info': return 'bg-slate-800/90 border border-slate-600 text-slate-100';
            default: return 'bg-slate-800/90 border border-slate-600 text-slate-100';
        }
    },

    getIcon(type) {
        switch (type) {
            case 'success': return '✅';
            case 'error': return '❌';
            case 'info': return 'ℹ️';
            default: return 'ℹ️';
        }
    }
};
