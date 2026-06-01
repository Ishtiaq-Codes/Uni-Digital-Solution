/**
 * UAF Smart Dashboard - Main JavaScript
 * Toast notifications, sidebar toggle, CSRF handling, utilities
 */

// ==========================================
// CSRF Token Handler (for all AJAX/fetch)
// ==========================================
const CSRFToken = {
    /**
     * Get the CSRF token from the cookie.
     * This is the Django-recommended approach for AJAX.
     */
    get() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        // Fallback: try reading from the hidden input in the DOM
        if (!cookieValue) {
            const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (input) {
                cookieValue = input.value;
            }
        }
        return cookieValue;
    },

    /**
     * Get headers object for fetch() calls.
     * Usage: fetch(url, { method: 'POST', headers: CSRFToken.headers(), ... })
     */
    headers() {
        return {
            'X-CSRFToken': this.get(),
            'X-Requested-With': 'XMLHttpRequest',
        };
    },

    /**
     * Check if a method requires CSRF protection.
     */
    methodRequiresCSRF(method) {
        return !(/^(GET|HEAD|OPTIONS|TRACE)$/i.test(method));
    }
};

/**
 * Enhanced fetch wrapper that automatically includes CSRF token.
 * Usage: csrfFetch('/api/endpoint/', { method: 'POST', body: ... })
 */
function csrfFetch(url, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    if (CSRFToken.methodRequiresCSRF(method)) {
        options.headers = {
            ...options.headers,
            'X-CSRFToken': CSRFToken.get(),
            'X-Requested-With': 'XMLHttpRequest',
        };
    }
    // Ensure credentials are sent (cookies)
    options.credentials = options.credentials || 'same-origin';
    return fetch(url, options);
}


// ==========================================
// Toast Notification System
// ==========================================
const Toast = {
    container: null,

    init() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'fixed top-4 right-4 z-50 flex flex-col gap-3';
            document.body.appendChild(this.container);
        }
    },

    show(message, type = 'info', duration = 4000) {
        if (!this.container) this.init();

        const icons = {
            success: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>`,
            error: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>`,
            warning: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path></svg>`,
            info: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
        };

        const colors = {
            success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
            error: 'bg-rose-50 border-rose-200 text-rose-800',
            warning: 'bg-amber-50 border-amber-200 text-amber-800',
            info: 'bg-blue-50 border-blue-200 text-blue-800',
        };

        const toast = document.createElement('div');
        toast.className = `flex items-center gap-3 px-4 py-3 rounded-xl border shadow-lg min-w-[320px] max-w-md toast-enter ${colors[type] || colors.info}`;
        toast.innerHTML = `
            <span class="flex-shrink-0">${icons[type] || icons.info}</span>
            <p class="text-sm font-medium flex-1">${message}</p>
            <button onclick="this.parentElement.remove()" class="flex-shrink-0 opacity-60 hover:opacity-100 transition-opacity">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        `;

        this.container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('toast-exit');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
};


// ==========================================
// Sidebar Toggle
// ==========================================
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    if (sidebar) {
        sidebar.classList.toggle('-translate-x-full');
    }
    if (overlay) {
        overlay.classList.toggle('hidden');
    }
}


// ==========================================
// DOM Ready Initialization
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    // Close sidebar on overlay click
    const overlay = document.getElementById('sidebar-overlay');
    if (overlay) {
        overlay.addEventListener('click', toggleSidebar);
    }

    // Initialize toast
    Toast.init();

    // Show Django messages as toasts
    const djangoMessages = document.querySelectorAll('.django-message');
    djangoMessages.forEach(msg => {
        const type = msg.dataset.type || 'info';
        const text = msg.textContent.trim();
        if (text) {
            Toast.show(text, type);
        }
        msg.remove();
    });

    // Notification dropdown
    const notifBtn = document.getElementById('notification-btn');
    const notifDropdown = document.getElementById('notification-dropdown');
    if (notifBtn && notifDropdown) {
        notifBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            notifDropdown.classList.toggle('hidden');
            if (!notifDropdown.classList.contains('hidden')) {
                loadNotifications();
            }
        });

        document.addEventListener('click', function() {
            notifDropdown.classList.add('hidden');
        });

        notifDropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    // User menu dropdown
    const userBtn = document.getElementById('user-menu-btn');
    const userDropdown = document.getElementById('user-dropdown');
    if (userBtn && userDropdown) {
        userBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('hidden');
        });
        document.addEventListener('click', function() {
            userDropdown.classList.add('hidden');
        });
    }

    // Auto-dismiss alerts
    setTimeout(function() {
        const alerts = document.querySelectorAll('.auto-dismiss');
        alerts.forEach(alert => {
            alert.classList.add('toast-exit');
            setTimeout(() => alert.remove(), 300);
        });
    }, 5000);

    // ==========================================
    // Protect all forms: ensure CSRF token is fresh
    // ==========================================
    document.querySelectorAll('form[method="post"], form[method="POST"]').forEach(form => {
        // If form doesn't have a CSRF token input, inject one
        if (!form.querySelector('input[name="csrfmiddlewaretoken"]')) {
            const token = CSRFToken.get();
            if (token) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'csrfmiddlewaretoken';
                input.value = token;
                form.prepend(input);
            }
        }
    });

    // Keep CSRF tokens in sync with cookie (handles token rotation)
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const tokenInput = this.querySelector('input[name="csrfmiddlewaretoken"]');
            const freshToken = CSRFToken.get();
            if (tokenInput && freshToken) {
                tokenInput.value = freshToken;
            }
        });
    });
});


// ==========================================
// AJAX Functions
// ==========================================

// Load notifications via AJAX (uses csrfFetch)
function loadNotifications() {
    const container = document.getElementById('notification-items');
    if (!container) return;

    fetch('/notifications/api/dropdown/', {
        credentials: 'same-origin',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
        .then(r => r.json())
        .then(data => {
            if (data.notifications.length === 0) {
                container.innerHTML = `
                    <div class="px-4 py-8 text-center text-slate-400 text-sm">
                        <svg class="w-8 h-8 mx-auto mb-2 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
                        No notifications
                    </div>`;
                return;
            }

            container.innerHTML = data.notifications.map(n => `
                <a href="${n.link || '#'}" class="block px-4 py-3 hover:bg-slate-50 transition-colors ${n.is_read ? 'opacity-60' : ''}">
                    <p class="text-sm font-medium text-slate-900 ${n.is_read ? '' : 'font-semibold'}">${n.title}</p>
                    <p class="text-xs text-slate-500 mt-0.5">${n.message}</p>
                    <p class="text-xs text-slate-400 mt-1">${n.created_at}</p>
                </a>
            `).join('');

            // Update badge
            const badge = document.getElementById('notification-badge');
            if (badge) {
                if (data.unread_count > 0) {
                    badge.textContent = data.unread_count;
                    badge.classList.remove('hidden');
                } else {
                    badge.classList.add('hidden');
                }
            }
        })
        .catch(() => {
            container.innerHTML = '<div class="px-4 py-8 text-center text-slate-400 text-sm">Failed to load</div>';
        });
}

// Confirm delete modal
function confirmAction(message, url) {
    if (confirm(message)) {
        window.location.href = url;
    }
}

// Counter animation for stats
function animateCounter(element, target, duration = 1500) {
    let start = 0;
    const increment = target / (duration / 16);
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(start).toLocaleString();
        }
    }, 16);
}

// Initialize counters on scroll
const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const target = parseInt(entry.target.dataset.target);
            if (target) animateCounter(entry.target, target);
            counterObserver.unobserve(entry.target);
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-counter]').forEach(el => {
        counterObserver.observe(el);
    });
});
