// Website Analyzer - Main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap tooltips are available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // URL validation and formatting
    const urlInput = document.getElementById('url');
    if (urlInput) {
        urlInput.addEventListener('blur', function() {
            let url = this.value.trim();
            if (url && !url.match(/^https?:\/\//)) {
                // Auto-add https:// if no protocol specified
                this.value = 'https://' + url;
            }
        });

        // Real-time URL validation
        urlInput.addEventListener('input', function() {
            const url = this.value.trim();
            const isValid = url === '' || isValidUrl(url) || isValidUrl('https://' + url);
            
            if (isValid) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
        });
    }

    // Progress tracking for analysis
    const progressBar = document.getElementById('progressBar');
    if (progressBar) {
        // Animate progress bar
        let progress = 25;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 90) progress = 90;
            progressBar.style.width = progress + '%';
        }, 2000);

        // Clear interval when page is about to unload
        window.addEventListener('beforeunload', () => {
            clearInterval(interval);
        });
    }

    // Auto-refresh functionality for results page
    const resultStatus = document.querySelector('[data-status]');
    if (resultStatus && resultStatus.dataset.status === 'pending') {
        const refreshInterval = setInterval(() => {
            const currentUrl = window.location.href;
            if (currentUrl.includes('/results/')) {
                // Check if we're still on the same page
                fetch(window.location.pathname + '/status', {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'completed' || data.status === 'failed') {
                        window.location.reload();
                    }
                })
                .catch(error => {
                    console.error('Error checking status:', error);
                });
            }
        }, 5000);

        // Clear interval when leaving the page
        window.addEventListener('beforeunload', () => {
            clearInterval(refreshInterval);
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.dataset.copy;
            navigator.clipboard.writeText(textToCopy).then(() => {
                // Show success feedback
                const originalText = this.innerHTML;
                this.innerHTML = '<i data-feather="check" class="me-1"></i>Copied!';
                setTimeout(() => {
                    this.innerHTML = originalText;
                    feather.replace();
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
            });
        });
    });

    // Table sorting functionality
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    sortableHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const column = this.cellIndex;
            const isAscending = this.classList.contains('sort-asc');

            // Sort rows
            rows.sort((a, b) => {
                const aText = a.cells[column].textContent.trim();
                const bText = b.cells[column].textContent.trim();
                
                // Try to parse as numbers first
                const aNum = parseFloat(aText);
                const bNum = parseFloat(bText);
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return isAscending ? bNum - aNum : aNum - bNum;
                } else {
                    return isAscending ? 
                        bText.localeCompare(aText) : 
                        aText.localeCompare(bText);
                }
            });

            // Remove existing sort classes
            sortableHeaders.forEach(h => {
                h.classList.remove('sort-asc', 'sort-desc');
            });

            // Add appropriate class
            this.classList.add(isAscending ? 'sort-desc' : 'sort-asc');

            // Reorder table rows
            rows.forEach(row => tbody.appendChild(row));
        });
    });

    // Enhanced form validation
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                    field.classList.add('is-valid');
                }
            });

            if (!isValid) {
                e.preventDefault();
                const firstInvalid = form.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
        });
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea[data-auto-resize]');
    textareas.forEach(textarea => {
        const resizeTextarea = () => {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        };

        textarea.addEventListener('input', resizeTextarea);
        resizeTextarea(); // Initial resize
    });

    // Loading states for buttons
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                const originalHtml = this.innerHTML;
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                this.disabled = true;

                // Re-enable after 10 seconds as fallback
                setTimeout(() => {
                    this.innerHTML = originalHtml;
                    this.disabled = false;
                }, 10000);
            }
        });
    });
});

// Utility functions
function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Export functions for use in other modules
window.WebAnalyzer = {
    isValidUrl,
    formatBytes,
    formatNumber,
    debounce
};
