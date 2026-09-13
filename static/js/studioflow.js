/**
 * StudioFlow Frontend Utilities
 * Powers: loading states, modals, sortable tables, toasts, search autocomplete,
 * keyboard shortcuts, page transitions, and accessible forms
 */

// ============================================================
// 1. TOAST SYSTEM (proper stacking + auto-dismiss + animation)
// ============================================================
const ToastManager = {
    container: null,
    init() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none';
            this.container.style.maxHeight = 'calc(100vh - 2rem)';
            this.container.style.overflowY = 'auto';
            document.body.appendChild(this.container);
        }
    },
    show(message, type = 'info', duration = 4000) {
        this.init();
        const icons = {
            success: '<svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>',
            error: '<svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>',
            warning: '<svg class="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/></svg>',
            info: '<svg class="w-5 h-5 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
        };
        const colors = {
            success: 'bg-green-50 border-green-200 text-green-800',
            error: 'bg-red-50 border-red-200 text-red-800',
            warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
            info: 'bg-brand-50 border-brand-200 text-brand-800',
        };

        const toast = document.createElement('div');
        toast.className = `pointer-events-auto flex items-center gap-3 px-5 py-3.5 rounded-xl text-sm font-medium shadow-lg border transform transition-all duration-300 translate-x-full opacity-0 ${colors[type] || colors.info}`;
        toast.innerHTML = `${icons[type] || icons.info}<span class="flex-1">${message}</span><button onclick="this.parentElement.remove()" class="ml-2 opacity-50 hover:opacity-100">&times;</button>`;
        
        this.container.appendChild(toast);
        requestAnimationFrame(() => {
            toast.classList.remove('translate-x-full', 'opacity-0');
            toast.classList.add('translate-x-0', 'opacity-100');
        });

        setTimeout(() => {
            toast.classList.add('translate-x-full', 'opacity-0');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
};

// Global toast function
window.toast = (msg, type) => ToastManager.show(msg, type);

// ============================================================
// 2. HTMX LOADING STATES (skeleton loaders + spinners)
// ============================================================
document.addEventListener('htmx:configRequest', (e) => {
    const target = document.querySelector(e.detail.target);
    if (target && !e.detail.target.includes('none')) {
        target.classList.add('sf-loading');
    }
});

document.addEventListener('htmx:beforeRequest', (e) => {
    const target = e.detail.target;
    if (target) {
        target.style.opacity = '0.6';
        target.style.pointerEvents = 'none';
    }
});

document.addEventListener('htmx:afterRequest', (e) => {
    const target = e.detail.target;
    if (target) {
        target.style.opacity = '';
        target.style.pointerEvents = '';
        target.classList.remove('sf-loading');
    }
});

document.addEventListener('htmx:afterSwap', (e) => {
    // Trigger page transition animation
    if (e.detail.target) {
        e.detail.target.classList.add('sf-fade-in');
        setTimeout(() => e.detail.target.classList.remove('sf-fade-in'), 300);
    }
});

// ============================================================
// 3. MODAL CONFIRMATION SYSTEM
// ============================================================
const Modal = {
    show(options) {
        const { title, message, confirmText = 'Confirm', cancelText = 'Cancel', type = 'danger', onConfirm } = options;
        const colors = {
            danger: 'bg-red-600 hover:bg-red-700',
            warning: 'bg-yellow-600 hover:bg-yellow-700',
            info: 'bg-brand-600 hover:bg-brand-700',
        };
        const iconColors = {
            danger: 'text-red-600 bg-red-100',
            warning: 'text-yellow-600 bg-yellow-100',
            info: 'text-brand-600 bg-brand-100',
        };
        const icons = {
            danger: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>',
            warning: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>',
            info: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>',
        };

        const overlay = document.createElement('div');
        overlay.className = 'fixed inset-0 z-[9998] bg-black/50 flex items-center justify-center p-4';
        overlay.style.opacity = '0';
        overlay.style.transition = 'opacity 0.2s ease';
        
        overlay.innerHTML = `
            <div class="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 transform transition-all scale-95 opacity-0" id="modal-content">
                <div class="flex items-start gap-4">
                    <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${iconColors[type]}">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">${icons[type]}</svg>
                    </div>
                    <div class="flex-1">
                        <h3 class="text-lg font-semibold text-gray-900">${title}</h3>
                        <p class="mt-2 text-sm text-gray-600">${message}</p>
                    </div>
                </div>
                <div class="mt-6 flex justify-end gap-3">
                    <button class="modal-cancel px-4 py-2 rounded-xl border border-gray-300 text-gray-700 hover:bg-gray-50 text-sm font-medium">${cancelText}</button>
                    <button class="modal-confirm px-4 py-2 rounded-xl text-white text-sm font-medium ${colors[type]}">${confirmText}</button>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);
        requestAnimationFrame(() => {
            overlay.style.opacity = '1';
            overlay.querySelector('#modal-content').classList.remove('scale-95', 'opacity-0');
            overlay.querySelector('#modal-content').classList.add('scale-100', 'opacity-100');
        });

        const close = () => {
            overlay.style.opacity = '0';
            overlay.querySelector('#modal-content').classList.add('scale-95', 'opacity-0');
            setTimeout(() => overlay.remove(), 200);
        };

        overlay.querySelector('.modal-cancel').onclick = close;
        overlay.onclick = (e) => { if (e.target === overlay) close(); };
        overlay.querySelector('.modal-confirm').onclick = () => {
            close();
            if (onConfirm) onConfirm();
        };

        // Escape key
        const escHandler = (e) => { if (e.key === 'Escape') { close(); document.removeEventListener('keydown', escHandler); } };
        document.addEventListener('keydown', escHandler);
    }
};

window.Modal = Modal;

// ============================================================
// 4. SORTABLE DATA TABLES
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('table[data-sortable]').forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach((th, index) => {
            th.classList.add('cursor-pointer', 'select-none', 'hover:bg-gray-100');
            th.innerHTML += ' <span class="text-gray-400 text-xs">↕</span>';
            th.onclick = () => {
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const key = th.dataset.sort;
                const dir = th.dataset.dir === 'asc' ? 'desc' : 'asc';
                th.dataset.dir = dir;

                rows.sort((a, b) => {
                    let aVal = a.cells[index]?.textContent.trim() || '';
                    let bVal = b.cells[index]?.textContent.trim() || '';
                    // Try numeric sort
                    const aNum = parseFloat(aVal.replace(/[₦,]/g, ''));
                    const bNum = parseFloat(bVal.replace(/[₦,]/g, ''));
                    if (!isNaN(aNum) && !isNaN(bNum)) {
                        return dir === 'asc' ? aNum - bNum : bNum - aNum;
                    }
                    return dir === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                });

                rows.forEach(row => tbody.appendChild(row));
                headers.forEach(h => h.querySelector('span') && (h.querySelector('span').textContent = '↕'));
                th.querySelector('span').textContent = dir === 'asc' ? '↑' : '↓';
            };
        });
    });
});

// ============================================================
// 5. GLOBAL SEARCH AUTOCOMPLETE
// ============================================================
const SearchAutocomplete = {
    debounceTimer: null,
    init() {
        const searchInputs = document.querySelectorAll('[data-search-autocomplete]');
        searchInputs.forEach(input => {
            const dropdown = document.createElement('div');
            dropdown.className = 'absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-xl shadow-lg mt-1 max-h-80 overflow-y-auto z-50 hidden';
            input.parentElement.style.position = 'relative';
            input.parentElement.appendChild(dropdown);

            input.addEventListener('input', () => {
                clearTimeout(this.debounceTimer);
                const query = input.value.trim();
                if (query.length < 2) { dropdown.classList.add('hidden'); return; }
                this.debounceTimer = setTimeout(() => this.search(query, dropdown, input), 250);
            });

            input.addEventListener('blur', () => {
                setTimeout(() => dropdown.classList.add('hidden'), 200);
            });
        });
    },
    async search(query, dropdown, input) {
        try {
            const resp = await fetch(`/search/?q=${encodeURIComponent(query)}`, { headers: { 'Accept': 'application/json' } });
            const data = await resp.json();
            if (!data.results || data.results.length === 0) {
                dropdown.innerHTML = '<div class="px-4 py-3 text-sm text-gray-500">No results found</div>';
                dropdown.classList.remove('hidden');
                return;
            }
            dropdown.innerHTML = data.results.slice(0, 8).map(r => `
                <a href="${r.url}" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors">
                    <span class="w-8 h-8 rounded-lg bg-brand-100 text-brand-600 flex items-center justify-center text-xs font-bold">${r.type ? r.type[0].toUpperCase() : '?'}</span>
                    <div class="flex-1 min-w-0">
                        <div class="text-sm font-medium text-gray-900 truncate">${r.title || r.name || ''}</div>
                        <div class="text-xs text-gray-500">${r.type || ''} ${r.subtitle ? '· ' + r.subtitle : ''}</div>
                    </div>
                </a>
            `).join('');
            dropdown.classList.remove('hidden');
        } catch (e) {
            dropdown.classList.add('hidden');
        }
    }
};

// ============================================================
// 6. KEYBOARD SHORTCUTS PANEL
// ============================================================
const KeyboardShortcuts = {
    shortcuts: [
        { key: 'g', desc: 'Go to...', items: [
            { key: 'g d', desc: 'Dashboard', url: '/' },
            { key: 'g b', desc: 'Bookings', url: '/bookings/' },
            { key: 'g c', desc: 'Clients', url: '/clients/' },
            { key: 'g f', desc: 'Finance', url: '/finance/' },
            { key: 'g i', desc: 'Inventory', url: '/inventory/' },
        ]},
        { key: 'n', desc: 'Create new...', items: [
            { key: 'n b', desc: 'New Booking', url: '/bookings/add/' },
            { key: 'n c', desc: 'New Client', url: '/clients/add/' },
            { key: 'n i', desc: 'New Invoice', url: '/finance/invoice/create/' },
        ]},
        { key: '/', desc: 'Focus search' },
        { key: '?', desc: 'Show shortcuts' },
        { key: 'Esc', desc: 'Close modal/search' },
    ],
    init() {
        document.addEventListener('keydown', (e) => {
            // Don't trigger in inputs
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
            
            if (e.key === '?') {
                e.preventDefault();
                this.showPanel();
            }
            if (e.key === '/') {
                e.preventDefault();
                const search = document.querySelector('[data-search-autocomplete]');
                if (search) search.focus();
            }
            if (e.key === 'Escape') {
                this.hidePanel();
            }
        });
    },
    showPanel() {
        if (document.getElementById('shortcuts-panel')) return;
        const panel = document.createElement('div');
        panel.id = 'shortcuts-panel';
        panel.className = 'fixed inset-0 z-[9998] bg-black/50 flex items-center justify-center p-4';
        panel.style.opacity = '0';
        panel.style.transition = 'opacity 0.2s';

        let html = '<div class="bg-white rounded-2xl shadow-xl max-w-lg w-full p-6 max-h-[80vh] overflow-y-auto">';
        html += '<div class="flex items-center justify-between mb-6"><h2 class="text-lg font-bold text-gray-900">Keyboard Shortcuts</h2><button onclick="document.getElementById(\'shortcuts-panel\').remove()" class="text-gray-400 hover:text-gray-600"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg></button></div>';

        this.shortcuts.forEach(group => {
            if (group.items) {
                html += `<div class="mb-4"><div class="text-xs font-semibold text-gray-500 uppercase mb-2">${group.desc}</div>`;
                group.items.forEach(s => {
                    html += `<div class="flex items-center justify-between py-1.5"><span class="text-sm text-gray-700">${s.desc}</span><kbd class="px-2 py-0.5 bg-gray-100 border border-gray-200 rounded text-xs font-mono text-gray-600">${s.key}</kbd></div>`;
                });
                html += '</div>';
            } else {
                html += `<div class="flex items-center justify-between py-1.5"><span class="text-sm text-gray-700">${group.desc}</span><kbd class="px-2 py-0.5 bg-gray-100 border border-gray-200 rounded text-xs font-mono text-gray-600">${group.key}</kbd></div>`;
            }
        });

        html += '</div>';
        panel.innerHTML = html;
        document.body.appendChild(panel);
        requestAnimationFrame(() => { panel.style.opacity = '1'; });
        panel.onclick = (e) => { if (e.target === panel) panel.remove(); };
    },
    hidePanel() {
        const panel = document.getElementById('shortcuts-panel');
        if (panel) panel.remove();
    }
};

// ============================================================
// 7. PAGE TRANSITION ANIMATIONS (HTMX)
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    // Add fade-in to main content on load
    const main = document.querySelector('[hx-boost], .sf-main-content, main');
    if (main) main.classList.add('sf-fade-in');
});

// ============================================================
// 8. ACCESSIBLE FORMS (auto-add ARIA labels)
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    // Add aria-required to required fields
    document.querySelectorAll('input[required], select[required], textarea[required]').forEach(el => {
        el.setAttribute('aria-required', 'true');
    });
    // Add aria-label to icon-only buttons
    document.querySelectorAll('button:not([aria-label])').forEach(btn => {
        if (btn.textContent.trim() === '' && btn.querySelector('svg')) {
            btn.setAttribute('aria-label', btn.title || 'Button');
        }
    });
    // Add role="alert" to error messages
    document.querySelectorAll('.messages .error, [class*="text-red"]').forEach(el => {
        if (el.closest('.messages')) el.setAttribute('role', 'alert');
    });
});

// ============================================================
// 9. CONFIRM DIALOG HELPER (replaces window.confirm)
// ============================================================
window.sfConfirm = (message, onConfirm) => {
    Modal.show({
        title: 'Are you sure?',
        message: message,
        confirmText: 'Yes, proceed',
        cancelText: 'Cancel',
        type: 'danger',
        onConfirm: onConfirm,
    });
};

// Replace all confirm() calls in forms
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('form[data-confirm]').forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const msg = form.dataset.confirm || 'Are you sure you want to proceed?';
            sfConfirm(msg, () => form.submit());
        });
    });
});

// ============================================================
// 10. SKELETON LOADER COMPONENT
// ============================================================
window.sfSkeleton = (lines = 3, type = 'text') => {
    const heights = { text: 'h-4', title: 'h-6', avatar: 'w-10 h-10 rounded-full', card: 'h-24' };
    let html = '<div class="animate-pulse space-y-3">';
    for (let i = 0; i < lines; i++) {
        const h = type === 'mixed' ? (i % 2 === 0 ? 'h-4 w-3/4' : 'h-4 w-1/2') : (heights[type] || 'h-4');
        html += `<div class="${h} bg-gray-200 rounded-lg"></div>`;
    }
    html += '</div>';
    return html;
};

// ============================================================
// INIT
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    ToastManager.init();
    SearchAutocomplete.init();
    KeyboardShortcuts.init();
});
