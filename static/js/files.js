/**
 * File Explorer & Management Module
 * Handles file listing, live searching, file type filtering, modal details, and deletion.
 */

let allFiles = [];
let fileIdToDelete = null;

document.addEventListener('DOMContentLoaded', () => {
    loadFiles();

    const searchBox = document.getElementById('search-box');
    const typeFilter = document.getElementById('type-filter');
    const refreshBtn = document.getElementById('btn-refresh-files');
    const confirmDeleteBtn = document.getElementById('btn-confirm-delete');

    if (searchBox) {
        searchBox.addEventListener('input', () => filterAndRenderFiles());
    }

    if (typeFilter) {
        typeFilter.addEventListener('change', () => filterAndRenderFiles());
    }

    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => loadFiles());
    }

    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', () => executeFileDelete());
    }
});

async function loadFiles() {
    const tableBody = document.getElementById('files-table-body');
    if (!tableBody) return;

    tableBody.innerHTML = `
        <tr>
            <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2.5rem;">
                <i class="fa-solid fa-spinner fa-spin"></i> Loading your cloud files...
            </td>
        </tr>
    `;

    try {
        const response = await fetch('/api/files');
        if (!response.ok) {
            throw new Error('Failed to fetch files');
        }

        const data = await response.json();
        if (data.success) {
            allFiles = data.files || [];
            filterAndRenderFiles();
        }
    } catch (err) {
        console.error('Error fetching files:', err);
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; color: #F87171; padding: 2rem;">
                    <i class="fa-solid fa-triangle-exclamation"></i> Error loading files from server.
                </td>
            </tr>
        `;
        showToast('Error loading files list', 'error');
    }
}

function filterAndRenderFiles() {
    const searchVal = (document.getElementById('search-box')?.value || '').toLowerCase().trim();
    const typeVal = (document.getElementById('type-filter')?.value || '').toLowerCase().trim();

    let filtered = allFiles.filter(f => {
        const matchesName = f.original_filename.toLowerCase().includes(searchVal);
        const matchesType = !typeVal || f.file_type.toLowerCase() === typeVal;
        return matchesName && matchesType;
    });

    renderTableRows(filtered);
}

function renderTableRows(files) {
    const tableBody = document.getElementById('files-table-body');
    if (!tableBody) return;

    if (!files || files.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="empty-state">
                        <div class="empty-icon"><i class="fa-solid fa-folder-open"></i></div>
                        <h4 style="font-size: 1.1rem; margin-bottom: 0.35rem;">No files found</h4>
                        <p style="font-size: 0.875rem; margin-bottom: 1.25rem;">No files matched your search criteria or storage is empty.</p>
                        <a href="/upload" class="btn btn-primary btn-sm"><i class="fa-solid fa-plus"></i> Upload New File</a>
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
                        <i class="fa-solid ${iconInfo.icon}" style="color: ${iconInfo.color}; font-size: 1.25rem;"></i>
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
                    <div class="actions-cell" style="justify-content: flex-end;">
                        <button type="button" class="action-btn" title="File Details" onclick="showFileDetails(${f.id})">
                            <i class="fa-solid fa-info-circle"></i>
                        </button>
                        <a href="/api/download/${f.id}" class="action-btn" title="Download File">
                            <i class="fa-solid fa-download"></i>
                        </a>
                        <button type="button" class="action-btn delete-btn" title="Delete File" onclick="promptDelete(${f.id}, '${escapeHTML(f.original_filename)}')">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

async function showFileDetails(fileId) {
    try {
        const response = await fetch(`/api/files/${fileId}`);
        const data = await response.json();

        if (data.success && data.file) {
            const f = data.file;
            document.getElementById('detail-name').textContent = f.original_filename;
            document.getElementById('detail-type').textContent = `.${f.file_type.toUpperCase()}`;
            document.getElementById('detail-size').textContent = `${f.formatted_size} (${f.file_size.toLocaleString()} bytes)`;
            document.getElementById('detail-storage').textContent = f.storage_type.toUpperCase();
            document.getElementById('detail-key').textContent = f.s3_key;
            document.getElementById('detail-date').textContent = f.uploaded_at;
            document.getElementById('detail-download-btn').href = `/api/download/${f.id}`;

            openModal('file-details-modal');
        }
    } catch (e) {
        showToast('Failed to load file details', 'error');
    }
}

function promptDelete(fileId, filename) {
    fileIdToDelete = fileId;
    const nameEl = document.getElementById('delete-file-name');
    if (nameEl) nameEl.textContent = `"${filename}"`;
    openModal('delete-modal');
}

async function executeFileDelete() {
    if (!fileIdToDelete) return;

    const btn = document.getElementById('btn-confirm-delete');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Deleting...';

    try {
        const response = await fetch(`/api/files/${fileIdToDelete}`, {
            method: 'DELETE'
        });
        const data = await response.json();

        if (response.ok && data.success) {
            showToast('File deleted successfully', 'success');
            closeModal('delete-modal');
            fileIdToDelete = null;
            loadFiles();
        } else {
            showToast(data.error || 'Failed to delete file', 'error');
        }
    } catch (err) {
        showToast('Network error during file deletion', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}
