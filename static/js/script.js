document.addEventListener('DOMContentLoaded', function() {
    loadFiles();
});

function loadFiles() {
    fetch('/api/files')
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error(data.error);
                return;
            }
            updateTable(data);
            updateCharts(data);
        })
        .catch(error => console.error('Error fetching files:', error));
}

function updateTable(files) {
    const tableBody = document.querySelector('#filesTable tbody');
    tableBody.innerHTML = '';

    if (files.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="4" class="text-center py-4">No files found.</td></tr>';
        return;
    }

    files.forEach(file => {
        const row = document.createElement('tr');
        const size = file.size ? formatBytes(file.size) : '-';
        
        row.innerHTML = `
            <td class="ps-4 fw-medium text-truncate" style="max-width: 250px;">
                <img src="${getIconForType(file.mimeType)}" width="20" class="me-2" alt="icon">
                ${file.name}
            </td>
            <td class="text-muted small">${file.mimeType}</td>
            <td class="text-muted small">${size}</td>
            <td class="text-end pe-4">
                <a href="/api/sync/download/${file.id}" class="btn btn-sm btn-outline-secondary">Download</a>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function updateCharts(files) {
    // Process data for File Types Chart
    const types = {};
    files.forEach(f => {
        const type = f.mimeType.split('/').pop();
        types[type] = (types[type] || 0) + 1;
    });

    const typeCtx = document.getElementById('fileTypeChart').getContext('2d');
    new Chart(typeCtx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(types),
            datasets: [{
                data: Object.values(types),
                backgroundColor: [
                    '#4285F4', '#DB4437', '#F4B400', '#0F9D58', '#AB47BC', '#00ACC1'
                ],
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                }
            }
        }
    });

    // Process data for File Size Chart (Top 10 largest)
    const sortedFiles = [...files].sort((a, b) => (b.size || 0) - (a.size || 0)).slice(0, 10);
    const sizeCtx = document.getElementById('fileSizeChart').getContext('2d');
    new Chart(sizeCtx, {
        type: 'bar',
        data: {
            labels: sortedFiles.map(f => f.name.substring(0, 15) + (f.name.length > 15 ? '...' : '')),
            datasets: [{
                label: 'Size (MB)',
                data: sortedFiles.map(f => ((f.size || 0) / 1024 / 1024).toFixed(2)),
                backgroundColor: '#4285F4',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Size (MB)' }
                }
            }
        }
    });
}

function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (!file) {
        alert("Please select a file first.");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    const progressBar = document.getElementById('uploadProgress');
    progressBar.classList.remove('d-none');

    fetch('/api/sync/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        progressBar.classList.add('d-none');
        if (data.error) {
            alert('Upload failed: ' + data.error);
        } else {
            alert('Upload successful!');
            const modal = bootstrap.Modal.getInstance(document.getElementById('uploadModal'));
            modal.hide();
            loadFiles(); // Refresh list
        }
    })
    .catch(error => {
        progressBar.classList.add('d-none');
        console.error('Error:', error);
        alert('Upload failed.');
    });
}

function formatBytes(bytes, decimals = 2) {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

function getIconForType(mimeType) {
    // Simplified icon logic, would typically use more specific icons
    if (mimeType.includes('folder')) return 'https://img.icons8.com/color/48/folder-invoices--v1.png';
    if (mimeType.includes('image')) return 'https://img.icons8.com/color/48/image-file.png';
    if (mimeType.includes('pdf')) return 'https://img.icons8.com/color/48/pdf.png';
    return 'https://img.icons8.com/color/48/file.png';
}
