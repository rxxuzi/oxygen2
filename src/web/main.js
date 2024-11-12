// main.js

// Initialize Eel
// Expose JavaScript functions to Python
eel.expose(updateDownloadList);
eel.expose(setProgressBar);
eel.expose(updateLogsTable);
eel.expose(setSettingsFromFile);
eel.expose(clearLogsTable);

eel.expose(set_browse_output);
function set_browse_output(outputType, path) {
    if (path) {
        if (outputType === 'video') {
            document.getElementById('video-output-path').value = path;
        } else if (outputType === 'audio') {
            document.getElementById('audio-output-path').value = path;
        }
    }
}

let isDownloading = false;

// Append message to download list
function appendToDownloadList(message) {
    const downloadList = document.getElementById('console');
    downloadList.value += message + '\n';
    downloadList.scrollTop = downloadList.scrollHeight;
}

// Eel-exposed functions
function updateDownloadList(message) {
    appendToDownloadList(message);
}

function setProgressBar(progress) {
    const progressBar = document.getElementById('progress-bar');
    progressBar.style.width = `${progress * 100}%`;
}

function updateLogsTable(logEntry) {
    const logsTableBody = document.getElementById('logs-table').querySelector('tbody');
    const row = document.createElement('tr');
    row.classList.add(logEntry.result === 'Success' ? 'good' : 'bad');
    row.innerHTML = `
        <td>${logEntry.result}</td>
        <td>${logEntry.date}</td>
        <td>${logEntry.url}</td>
        <td>${logEntry.folder}</td>
    `;
    logsTableBody.appendChild(row);
}

function clearLogsTable() {
    const logsTableBody = document.getElementById('logs-table').querySelector('tbody');
    logsTableBody.innerHTML = '';
}

function setSettingsFromFile(settings) {
    // Video Settings
    document.getElementById('quality-select').value = settings.video_quality || 'Best';
    document.getElementById('video-format-select').value = settings.video_format || 'auto';
    document.getElementById('video-output-path').value = settings.video_output_path || '';

    // Audio Settings
    document.getElementById('audio-format-select').value = settings.audio_format || 'auto';
    document.getElementById('audio-output-path').value = settings.audio_output_path || '';

    // Download Settings
    document.getElementById('segments').value = settings.segments || 4;
    document.getElementById('retries').value = settings.retries || 5;
    document.getElementById('buffer-size').value = settings.buffer_size || '16M';

    // Other Settings
    document.getElementById('proxy-input').value = settings.proxy || '';
    document.getElementById('sublangs-input').value = settings.sublangs || '';
    document.getElementById('write-thumbnail-checkbox').checked = settings.write_thumbnail || false;
    document.getElementById('embed-thumbnail-checkbox').checked = settings.embed_thumbnail || false;
}

// Handle changes in the output path input fields
document.getElementById('video-output-path').addEventListener('change', () => {
    const path = document.getElementById('video-output-path').value;
    eel.set_video_output_path(path);
});

document.getElementById('audio-output-path').addEventListener('change', () => {
    const path = document.getElementById('audio-output-path').value;
    eel.set_audio_output_path(path);
});

// Tab Switching Logic and Initialization
document.addEventListener('DOMContentLoaded', () => {
    const mainTabBtn = document.getElementById('main-tab-btn');
    const settingsTabBtn = document.getElementById('settings-tab-btn');
    const logsTabBtn = document.getElementById('logs-tab-btn');
    const authTabBtn = document.getElementById('auth-tab-btn');
    const mainTab = document.getElementById('main-tab');
    const settingsTab = document.getElementById('settings-tab');
    const logsTab = document.getElementById('logs-tab');
    const authTab = document.getElementById('auth-tab');

    mainTabBtn.addEventListener('click', () => {
        activateTab(mainTabBtn, mainTab);
    });

    settingsTabBtn.addEventListener('click', () => {
        activateTab(settingsTabBtn, settingsTab);
    });

    logsTabBtn.addEventListener('click', ()  => {
        activateTab(logsTabBtn, logsTab);
    });

    authTabBtn.addEventListener('click', () => {
        activateTab(authTabBtn, authTab);
    });

    function activateTab(button, tab) {
        document.querySelectorAll('.tabs button').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        button.classList.add('active');
        tab.classList.add('active');
    }

    // Load settings from file
    eel.load_settings()(setSettingsFromFile);

    // Load auth entries
    eel.list_auth_entries()(updateAuthTable);
});

// Download Button Logic
document.getElementById('download-btn').addEventListener('click', () => {
    if (isDownloading) {
        alert('A download is already in progress.');
        return;
    }

    const url = document.getElementById('url-input').value.trim();
    const quality = document.getElementById('quality-select').value;
    const audioOnly = document.getElementById('audio-checkbox').checked;

    if (!url) {
        alert('Please enter a URL.');
        return;
    }

    const segments = parseInt(document.getElementById('segments').value) || 4;
    const retries = parseInt(document.getElementById('retries').value) || 5;
    const bufferSize = document.getElementById('buffer-size').value.trim();

    // Validate buffer size
    const bufferSizeRegex = /^\d+[KMG]?$/i;
    const validBufferSize = bufferSizeRegex.test(bufferSize) ? bufferSize : '1M';

    isDownloading = true;
    toggleDownloadButtons(true);

    // Pass quality and additional settings to backend via settings
    eel.set_video_quality(quality);
    eel.set_segments(segments);
    eel.set_retries(retries);
    eel.set_buffer_size(validBufferSize);

    eel.add_to_queue(url, audioOnly);
    appendToDownloadList('Download started...');
    document.getElementById('url-input').value = '';
});

// Browse Button Logic for Video
document.getElementById('video-browse-btn').addEventListener('click', () => {
    eel.browse_output('video')();
});

// Browse Button Logic for Audio
document.getElementById('audio-browse-btn').addEventListener('click', () => {
    eel.browse_output('audio')();
});

// Clear Console
document.getElementById('clear-console-btn').addEventListener('click', () => {
    document.getElementById('console').value = '';
});

// Open Folder
document.getElementById('open-folder-btn').addEventListener('click', () => {
    eel.open_download_folder();
});

// Open Logs Folder
document.getElementById('open-logs-btn').addEventListener('click', () => {
    eel.open_logs_folder();
});

// Load Logs
document.getElementById('load-logs-btn').addEventListener('click', () => {
    eel.load_logs();
});

// Reset Settings
document.getElementById('reset-settings-btn').addEventListener('click', () => {
    if (confirm('Are you sure you want to reset settings to defaults?')) {
        eel.reset_settings()(setSettingsFromFile);
    }
});

// Handle settings changes
document.getElementById('quality-select').addEventListener('change', () => {
    const quality = document.getElementById('quality-select').value;
    eel.set_video_quality(quality);
});

document.getElementById('video-format-select').addEventListener('change', () => {
    const videoFormat = document.getElementById('video-format-select').value;
    eel.set_video_format(videoFormat);
});

document.getElementById('audio-format-select').addEventListener('change', () => {
    const audioFormat = document.getElementById('audio-format-select').value;
    eel.set_audio_format(audioFormat);
});

document.getElementById('proxy-input').addEventListener('change', () => {
    const proxy = document.getElementById('proxy-input').value;
    eel.set_proxy(proxy);
});

document.getElementById('sublangs-input').addEventListener('change', () => {
    const sublangs = document.getElementById('sublangs-input').value;
    eel.set_sublangs(sublangs);
});

document.getElementById('write-thumbnail-checkbox').addEventListener('change', () => {
    const writeThumbnail = document.getElementById('write-thumbnail-checkbox').checked;
    eel.set_write_thumbnail(writeThumbnail);
});

document.getElementById('embed-thumbnail-checkbox').addEventListener('change', () => {
    const embedThumbnail = document.getElementById('embed-thumbnail-checkbox').checked;
    eel.set_embed_thumbnail(embedThumbnail);
});

document.getElementById('segments').addEventListener('change', () => {
    let segments = parseInt(document.getElementById('segments').value);
    if (isNaN(segments) || segments < 1 || segments > 10) {
        alert('Segments must be a number between 1 and 10.');
        document.getElementById('segments').value = '4';
        segments = 4;
    }
    eel.set_segments(segments);
});

document.getElementById('retries').addEventListener('change', () => {
    let retries = parseInt(document.getElementById('retries').value);
    if (isNaN(retries) || retries < 0) {
        alert('Retries must be a non-negative number.');
        document.getElementById('retries').value = '5';
        retries = 5;
    }
    eel.set_retries(retries);
});

document.getElementById('buffer-size').addEventListener('change', () => {
    let bufferSize = document.getElementById('buffer-size').value.trim();
    const bufferSizeRegex = /^\d+[KMG]?$/i;
    if (!bufferSizeRegex.test(bufferSize)) {
        alert('Invalid buffer size format. Defaulting to 1M.');
        bufferSize = '1M';
        document.getElementById('buffer-size').value = bufferSize;
    }
    eel.set_buffer_size(bufferSize);
});

// Function to toggle download buttons
function toggleDownloadButtons(downloading) {
    document.getElementById('download-btn').disabled = downloading;
}

// After download is completed, reset the download state
eel.expose(resetDownloadState);
function resetDownloadState() {
    isDownloading = false;
    toggleDownloadButtons(false);
}

// Handle cookie upload
document.getElementById('upload-cookie-btn').addEventListener('click', () => {
    const url = document.getElementById('cookie-url').value.trim();
    const fileInput = document.getElementById('cookie-file');
    if (!url || !fileInput.files.length) {
        alert('Please enter a URL and select a cookie file.');
        return;
    }
    const file = fileInput.files[0];
    const reader = new FileReader();
    reader.onload = function(e) {
        const content = e.target.result;
        eel.save_cookie(url, content)().then((result) => {
            if (result) {
                alert('Cookie saved successfully.');
                eel.list_auth_entries()(updateAuthTable);
            } else {
                alert('Failed to save cookie.');
            }
        });
    };
    reader.readAsText(file);
});

// Handle password upload
document.getElementById('upload-pass-btn').addEventListener('click', () => {
    const url = document.getElementById('pass-url').value.trim();
    const username = document.getElementById('pass-username').value.trim();
    const password = document.getElementById('pass-password').value;
    if (!url || !username || !password) {
        alert('Please enter URL, username, and password.');
        return;
    }
    eel.save_credentials(url, username, password)().then((result) => {
        if (result) {
            alert('Credentials saved successfully.');
            eel.list_auth_entries()(updateAuthTable);
        } else {
            alert('Failed to save credentials.');
        }
    });
});

// Function to update auth table
function updateAuthTable(entries) {
    const authTableBody = document.getElementById('auth-table').querySelector('tbody');
    authTableBody.innerHTML = '';
    entries.forEach(entry => {
        const row = document.createElement('tr');
        row.classList.add(entry.status === 'success' ? 'good' : 'bad');
        row.innerHTML = `
            <td>${entry.status}</td>
            <td>${entry.domain}</td>
            <td>${entry.type}</td>
            <td><button class="delete-auth-btn" data-domain="${entry.domain}" data-type="${entry.type}">Delete</button></td>
        `;
        authTableBody.appendChild(row);
    });
    // Add event listeners to delete buttons
    document.querySelectorAll('.delete-auth-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const domain = btn.getAttribute('data-domain');
            const authType = btn.getAttribute('data-type');
            if (confirm(`Are you sure you want to delete auth data for ${domain} (${authType})?`)) {
                eel.delete_auth_entry(domain, authType)().then((result) => {
                    if (result) {
                        alert('Auth data deleted.');
                        eel.list_auth_entries()(updateAuthTable);
                    } else {
                        alert('Failed to delete auth data.');
                    }
                });
            }
        });
    });
}
