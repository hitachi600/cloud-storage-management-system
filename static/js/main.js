/**
 * Main Global JavaScript Module
 * Provides toast alerts, modal handlers, file icons, and common utility functions.
 */

// Show Toast Notification
function showToast(message, type = 'success', duration = 4000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation';
    const iconColor = type === 'success' ? '#10B981' : '#EF4444';

    toast.innerHTML = `
        <i class="fa-solid ${icon}" style="color: ${iconColor}; font-size: 1.1rem;"></i>
        <div style="flex: 1;">${escapeHTML(message)}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Modal Controllers
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Close modals when clicking backdrop
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
    }
});

// HTML Escaping for security
function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}

// File Icon Helper
function getFileIconClass(fileType) {
    const type = (fileType || '').toLowerCase();
    switch (type) {
        case 'pdf':
            return { icon: 'fa-file-pdf', color: '#EF4444' };
        case 'png':
        case 'jpg':
        case 'jpeg':
        case 'gif':
        case 'svg':
            return { icon: 'fa-file-image', color: '#10B981' };
        case 'docx':
        case 'doc':
            return { icon: 'fa-file-word', color: '#3B82F6' };
        case 'xlsx':
        case 'csv':
            return { icon: 'fa-file-excel', color: '#059669' };
        case 'zip':
        case 'rar':
        case '7z':
        case 'tar':
            return { icon: 'fa-file-zipper', color: '#F59E0B' };
        case 'txt':
            return { icon: 'fa-file-lines', color: '#9CA3AF' };
        default:
            return { icon: 'fa-file', color: '#818CF8' };
    }
}
