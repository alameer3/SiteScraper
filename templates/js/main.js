// Website Analyzer - Main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons if available
    if (typeof feather !== 'undefined') {
        feather.replace();
    }

    // Form validation and enhancement
    initializeFormValidation();

    // Initialize animations
    initializeAnimations();

    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

function initializeFormValidation() {
    const form = document.getElementById('analysisForm');
    const urlInput = document.getElementById('url');
    const submitBtn = document.getElementById('analyzeBtn');

    if (!form || !urlInput || !submitBtn) {
        return; // Elements not found, skip initialization
    }

    // URL input validation
    urlInput.addEventListener('input', function() {
        const url = this.value.trim();
        const isValid = isValidUrl(url);

        if (url && !isValid) {
            this.classList.add('is-invalid');
        } else {
            this.classList.remove('is-invalid');
        }
    });

    // Form submission
    form.addEventListener('submit', function(e) {
        const url = urlInput.value.trim();

        if (!url) {
            e.preventDefault();
            showAlert('يرجى إدخال رابط الموقع', 'error');
            return false;
        }

        if (!isValidUrl(url)) {
            e.preventDefault();
            showAlert('يرجى إدخال رابط صحيح', 'error');
            return false;
        }

        // Show loading state
        setLoadingState(submitBtn, true);

        // The form will submit normally after this
        return true;
    });
}

function isValidUrl(string) {
    try {
        // Add protocol if missing
        if (!string.startsWith('http://') && !string.startsWith('https://')) {
            string = 'https://' + string;
        }
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

function setLoadingState(button, loading) {
    if (!button) return;

    if (loading) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>جاري التحليل...';
    } else {
        button.disabled = false;
        button.innerHTML = '<i data-feather="zap" class="me-2" width="18" height="18"></i>تحليل الموقع';
        // Re-initialize feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
}

function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Find container to insert alert
    const container = document.querySelector('.flash-messages') || document.querySelector('.container-fluid') || document.querySelector('main') || document.body;
    if (container && container.appendChild) {
        if (container.firstChild) {
            container.insertBefore(alertDiv, container.firstChild);
        } else {
            container.appendChild(alertDiv);
        }

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

function showAdvancedPreview() {
    // Implementation for showing advanced preview
    console.log('Advanced preview functionality activated');
    
    // If there's a modal or preview container, show it
    const previewModal = document.getElementById('advancedPreviewModal');
    if (previewModal && typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(previewModal);
        modal.show();
    } else {
        // Fallback: redirect to advanced extractor page
        window.location.href = '/website-extractor';
    }
}

function initializeAnimations() {
    // Counter animation for stats
    const counters = document.querySelectorAll('.counter');
    counters.forEach(counter => {
        const updateCount = () => {
            const target = +counter.getAttribute('data-target');
            const count = +counter.innerText;
            const increment = target / 200;

            if (count < target) {
                counter.innerText = Math.ceil(count + increment);
                setTimeout(updateCount, 1);
            } else {
                counter.innerText = target;
            }
        };

        // Start animation when element is visible
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateCount();
                    observer.unobserve(entry.target);
                }
            });
        });

        observer.observe(counter);
    });

    // Pulse animation for buttons
    const pulseButtons = document.querySelectorAll('.pulse-btn');
    pulseButtons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });

        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// Progress tracking for analysis page
function updateProgress(resultId) {
    if (!resultId) return;

    fetch(`/api/status/${resultId}`)
        .then(response => response.json())
        .then(data => {
            const progressBar = document.querySelector('.progress-bar');
            const statusText = document.querySelector('.status-text');

            if (progressBar) {
                progressBar.style.width = data.progress + '%';
            }

            if (statusText) {
                statusText.textContent = getStatusText(data.status);
            }

            // If completed, redirect to results
            if (data.status === 'completed') {
                window.location.href = `/results/${resultId}`;
            } else if (data.status === 'failed') {
                showAlert(data.error_message || 'حدث خطأ في التحليل', 'error');
            } else {
                // Continue polling
                setTimeout(() => updateProgress(resultId), 2000);
            }
        })
        .catch(error => {
            console.error('Error checking status:', error);
            setTimeout(() => updateProgress(resultId), 5000);
        });
}

function getStatusText(status) {
    const statusTexts = {
        'pending': 'في الانتظار...',
        'processing': 'جاري التحليل...',
        'completed': 'اكتمل التحليل',
        'failed': 'فشل التحليل'
    };

    return statusTexts[status] || status;
}

// Export functions for use in other scripts
window.WebsiteAnalyzer = {
    updateProgress: updateProgress,
    setLoadingState: setLoadingState,
    showAlert: showAlert
};

// Utility functions
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