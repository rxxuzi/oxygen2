document.addEventListener('DOMContentLoaded', () => {
    // Initialize tabs
    const tabs = document.querySelectorAll('.tabs button');
    const tabContents = document.querySelectorAll('.tab');

    // Set initial active tab
    setActiveTab(tabs[0], tabContents[0]);

    tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => {
            setActiveTab(tab, tabContents[index]);
        });
    });

    function setActiveTab(activeTab, activeContent) {
        tabs.forEach(t => t.classList.remove('active'));
        tabContents.forEach(c => c.style.display = 'none');

        activeTab.classList.add('active');
        activeContent.style.display = 'block';
    }

    // Smooth progress bar animation
    function updateProgressBar(progress) {
        const progressBar = document.getElementById('progress-bar');
        progressBar.style.transition = 'width 0.3s ease-in-out, background-color 0.3s ease-in-out';
        progressBar.style.width = `${progress * 100}%`;

        // Convert progress to percentage (0-100)
        const percentage = progress * 100;

        // Define color stages
        const colorStages = [
            { color: { r: 220, g: 53, b: 69 }, position: 0 },    // Red #dc3545
            { color: { r: 255, g: 193, b: 7 }, position: 33 },   // Yellow #ffc107
            { color: { r: 40, g: 167, b: 69 }, position: 66 },   // Green #28a745
            { color: { r: 0, g: 123, b: 255 }, position: 100 }   // Blue #007bff
        ];

        // Find the current color stage
        let startColor, endColor, startPosition, endPosition;

        for (let i = 0; i < colorStages.length - 1; i++) {
            if (percentage >= colorStages[i].position && percentage <= colorStages[i + 1].position) {
                startColor = colorStages[i].color;
                endColor = colorStages[i + 1].color;
                startPosition = colorStages[i].position;
                endPosition = colorStages[i + 1].position;
                break;
            }
        }

        // Calculate the interpolation ratio
        const ratio = (percentage - startPosition) / (endPosition - startPosition);

        // Interpolate between colors
        const currentColor = {
            r: Math.round(startColor.r + (endColor.r - startColor.r) * ratio),
            g: Math.round(startColor.g + (endColor.g - startColor.g) * ratio),
            b: Math.round(startColor.b + (endColor.b - startColor.b) * ratio)
        };

        progressBar.style.backgroundColor = `rgb(${currentColor.r}, ${currentColor.g}, ${currentColor.b})`;
    }

// Replace the existing setProgressBar function
    eel.expose(setProgressBar);
    function setProgressBar(progress) {
        updateProgressBar(progress);
    }

    // Enhance button interactions
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('mousedown', () => {
            button.style.transform = 'scale(0.95)';
        });
        button.addEventListener('mouseup', () => {
            button.style.transform = 'scale(1)';
        });
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'scale(1)';
        });
    });

    // Smooth scrolling for the download list
    const downloadList = document.getElementById('console');
    downloadList.addEventListener('input', () => {
        downloadList.scrollTop = downloadList.scrollHeight;
    });

    // Enhanced checkbox interactions
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            if (checkbox.checked) {
                checkbox.parentElement.style.color = 'var(--primary-blue)';
            } else {
                checkbox.parentElement.style.color = 'var(--text-primary)';
            }
        });
    });
});