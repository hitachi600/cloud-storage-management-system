/**
 * File Upload Module
 * Implements Drag-and-Drop, XMLHttpRequest upload with live progress tracking, and validation.
 */

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('btn-browse-file');
    const statusCard = document.getElementById('upload-status-card');
    const progressFill = document.getElementById('upload-progress-fill');
    const progressPercent = document.getElementById('upload-percentage');
    const statusText = document.getElementById('upload-status-text');
    const fileNameEl = document.getElementById('selected-file-name');
    const fileSizeEl = document.getElementById('selected-file-size');
    const fileIconEl = document.getElementById('preview-file-icon');
    const viewFilesBtn = document.getElementById('btn-view-files');
    const alertBox = document.getElementById('upload-alert');

    let currentXHR = null;

    if (!dropZone || !fileInput) return;

    // Trigger file browser on button click or dropzone click
    if (browseBtn) {
        browseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });
    }

    dropZone.addEventListener('click', () => fileInput.click());

    // Drag and Drop Events
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files && files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    function showAlert(msg, isSuccess = false) {
        if (!alertBox) return;
        alertBox.textContent = msg;
        alertBox.className = `alert ${isSuccess ? 'alert-success' : 'alert-danger'}`;
        alertBox.style.display = 'flex';
    }

    function hideAlert() {
        if (!alertBox) return;
        alertBox.style.display = 'none';
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        else return (bytes / 1048576).toFixed(1) + ' MB';
    }

    function handleFileUpload(file) {
        hideAlert();

        if (!file) return;

        // Show status card
        statusCard.style.display = 'block';
        fileNameEl.textContent = file.name;
        fileSizeEl.textContent = formatFileSize(file.size);

        const ext = file.name.includes('.') ? file.name.split('.').pop() : '';
        const iconInfo = getFileIconClass(ext);
        fileIconEl.innerHTML = `<i class="fa-solid ${iconInfo.icon}" style="color: ${iconInfo.color};"></i>`;

        // Reset progress UI
        progressFill.style.width = '0%';
        progressFill.style.background = 'var(--accent-gradient)';
        progressPercent.textContent = '0%';
        statusText.textContent = 'Uploading file to storage...';
        viewFilesBtn.style.display = 'none';

        // Prepare FormData
        const formData = new FormData();
        formData.append('file', file);

        // Upload with XMLHttpRequest for real progress monitoring
        const xhr = new XMLHttpRequest();
        currentXHR = xhr;

        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                progressFill.style.width = percent + '%';
                progressPercent.textContent = percent + '%';
                statusText.textContent = `Uploading: ${formatFileSize(e.loaded)} / ${formatFileSize(e.total)}`;
            }
        });

        xhr.addEventListener('load', () => {
            let res = {};
            try {
                res = JSON.parse(xhr.responseText);
            } catch (e) {
                res = { error: 'Unknown server response' };
            }

            if (xhr.status >= 200 && xhr.status < 300 && res.success) {
                progressFill.style.width = '100%';
                progressPercent.textContent = '100%';
                statusText.textContent = 'Upload complete! File stored safely.';
                viewFilesBtn.style.display = 'inline-flex';
                showToast(res.message || 'File uploaded successfully!', 'success');
                fileInput.value = '';
            } else {
                progressFill.style.background = 'var(--danger)';
                statusText.textContent = 'Upload failed.';
                showAlert(res.error || 'Upload error occurred');
                showToast(res.error || 'Failed to upload file', 'error');
            }
        });

        xhr.addEventListener('error', () => {
            progressFill.style.background = 'var(--danger)';
            statusText.textContent = 'Network error during upload.';
            showAlert('Network error. Failed to connect to backend.');
            showToast('Network error during file upload', 'error');
        });

        xhr.open('POST', '/api/upload');
        xhr.send(formData);
    }
});
