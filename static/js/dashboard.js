/**
 * Dashboard Management Module
 * Fetches user metrics, storage quota analytics, and recent uploads.
 */

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
});

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/dashboard');
        if (!response.ok) {
            throw new Error('Failed to fetch dashboard metrics');
        }

        const result = await response.json();
        if (result.success && result.metrics) {
            renderMetrics(result.metrics);
        }
    } catch (err) {
        console.error('Error loading dashboard:', err);
        showToast('Could not load dashboard statistics.', 'error');
    }
}

function renderMetrics(metrics) {
    // Update Stats Cards
    const totalFilesEl = document.getElementById('stat-total-files');
    const storageUsedEl = document.getElementById('stat-storage-used');
    const quotaPercentEl = document.getElementById('stat-quota-percent');
    const storageModeEl = document.getElementById('stat-storage-mode');

    if (totalFilesEl) totalFilesEl.textContent = metrics.total_files;
    if (storageUsedEl) storageUsedEl.textContent = metrics.formatted_storage;
    if (quotaPercentEl) quotaPercentEl.textContent = `${metrics.storage_percentage}%`;
    if (storageModeEl) storageModeEl.textContent = (metrics.storage_mode || 'LOCAL').toUpperCase();

    // Update Quota Progress Bar
    const progressFill = document.getElementById('storage-progress-fill');
    const quotaText = document.getElementById('quota-text');

    if (progressFill) {
        progressFill.style.width = `${Math.max(metrics.storage_percentage, 1)}%`;
        if (metrics.storage_percentage > 85) {
            progressFill.style.background = 'linear-gradient(135deg, #EF4444 0%, #F59E0B 100%)';
        }
    }

    if (quotaText) {
        quotaText.textContent = `${metrics.formatted_storage} used of ${metrics.formatted_quota} (${metrics.storage_percentage}%)`;
    }

    // Render Recent Files Table
    renderRecentFiles(metrics.recent_files);
}

function renderRecentFiles(files) {
    const tableBody = document.getElementById('recent-files-body');
    if (!tableBody) return;

    if (!files || files.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="empty-state">
                        <div class="empty-icon"><i class="fa-solid fa-cloud-arrow-up"></i></div>
                        <h4 style="font-size: 1.1rem; margin-bottom: 0.35rem;">No files uploaded yet</h4>
                        <p style="font-size: 0.875rem; margin-bottom: 1.25rem;">Start uploading documents or images to see them here.</p>
                        <a href="/upload" class="btn btn-primary btn-sm"><i class="fa-solid fa-plus"></i> Upload First File</a>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = files.map(f => {
        const iconInfo = getFileIconClass(f.file_type);
        return `
            <tr>
                <td>
                    <div class="file-name-cell">
                        <i class="fa-solid ${iconInfo.icon}" style="color: ${iconInfo.color}; font-size: 1.2rem;"></i>
                        <span title="${escapeHTML(f.original_filename)}">${escapeHTML(f.original_filename)}</span>
                    </div>
                </td>
                <td><span class="file-ext-badge">.${escapeHTML(f.file_type)}</span></td>
                <td>${escapeHTML(f.formatted_size)}</td>
                <td style="color: var(--text-secondary); font-size: 0.85rem;">${escapeHTML(f.uploaded_at)}</td>
                <td>
                    <span class="chip" style="font-size: 0.7rem;">
                        <i class="fa-solid ${f.storage_type === 's3' ? 'fa-cubes' : 'fa-hard-drive'}"></i>
                        ${escapeHTML(f.storage_type.toUpperCase())}
                    </span>
                </td>
                <td style="text-align: right;">
                    <a href="/api/download/${f.id}" class="action-btn" title="Download File">
                        <i class="fa-solid fa-download"></i>
                    </a>
                </td>
            </tr>
        `;
    }).join('');
}
