// Advanced Live Dashboard JavaScript
class LiveDashboard {
    constructor() {
        try {
            this.init();
            this.setupAnimations();
            this.initializeCharts();
            this.startLiveUpdates();
        } catch (error) {
            console.warn('LiveDashboard initialization error:', error);
        }
    }

    init() {
        // Initialize Feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }

        // Setup scroll reveal animations only if elements exist
        if (document.querySelectorAll('.scroll-reveal').length > 0) {
            this.setupScrollReveal();
        }
        
        // Initialize counters only if they exist
        if (document.querySelectorAll('.counter').length > 0) {
            this.animateCounters();
        }
        
        // Setup live indicators only if they exist
        if (document.querySelectorAll('[data-live="true"]').length > 0) {
            this.setupLiveIndicators();
        }
    }

    setupAnimations() {
        // Add entrance animations to cards
        const cards = document.querySelectorAll('.card, .glass-card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('scroll-reveal');
        });

        // Setup hover effects for interactive elements
        const interactiveElements = document.querySelectorAll('.stat-card, .glass-card');
        interactiveElements.forEach(element => {
            element.addEventListener('mouseenter', this.addHoverGlow);
            element.addEventListener('mouseleave', this.removeHoverGlow);
        });
    }

    addHoverGlow(e) {
        e.target.style.boxShadow = '0 20px 40px rgba(103, 126, 234, 0.3)';
    }

    removeHoverGlow(e) {
        e.target.style.boxShadow = '';
    }

    setupScrollReveal() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.scroll-reveal').forEach(el => {
            observer.observe(el);
        });
    }

    animateCounters() {
        const counters = document.querySelectorAll('.counter');
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target') || counter.textContent);
            this.animateValue(counter, 0, target, 2000);
        });
    }

    animateValue(element, start, end, duration) {
        const startTime = performance.now();
        const startValue = start;
        const endValue = end;

        const update = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = Math.floor(startValue + (endValue - startValue) * easeOutQuart);
            
            element.textContent = currentValue.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        };

        requestAnimationFrame(update);
    }

    setupLiveIndicators() {
        // Add live indicators where appropriate
        const liveElements = document.querySelectorAll('[data-live="true"]');
        liveElements.forEach(element => {
            if (element && element.appendChild) {
                const indicator = document.createElement('span');
                indicator.className = 'live-indicator';
                indicator.innerHTML = '<span>🔴</span> Live';
                element.appendChild(indicator);
            }
        });
    }

    initializeCharts() {
        // Only initialize charts if Chart.js is available
        if (typeof Chart === 'undefined') {
            return;
        }
        
        // Technology Distribution Chart
        this.createTechChart();
        
        // Assets Breakdown Chart
        this.createAssetsChart();
        
        // SEO Score Chart
        this.createSEOChart();
        
        // Performance Metrics Chart
        this.createPerformanceChart();
    }

    createTechChart() {
        const techCanvas = document.getElementById('techChart');
        if (!techCanvas) return;

        const ctx = techCanvas.getContext('2d');
        const techData = JSON.parse(techCanvas.getAttribute('data-tech') || '{}');
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(techData),
                datasets: [{
                    data: Object.values(techData),
                    backgroundColor: [
                        'rgba(103, 126, 234, 0.8)',
                        'rgba(17, 153, 142, 0.8)',
                        'rgba(240, 147, 251, 0.8)',
                        'rgba(79, 172, 254, 0.8)',
                        'rgba(255, 206, 84, 0.8)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#fff',
                            usePointStyle: true,
                            padding: 20
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 2000
                }
            }
        });
    }

    createAssetsChart() {
        const assetsCanvas = document.getElementById('assetsChart');
        if (!assetsCanvas) return;

        const ctx = assetsCanvas.getContext('2d');
        const assetsData = JSON.parse(assetsCanvas.getAttribute('data-assets') || '{}');

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Images', 'CSS Files', 'JS Files', 'Fonts', 'Other'],
                datasets: [{
                    label: 'Asset Count',
                    data: [
                        assetsData.images || 0,
                        assetsData.css || 0,
                        assetsData.javascript || 0,
                        assetsData.fonts || 0,
                        assetsData.other || 0
                    ],
                    backgroundColor: 'rgba(103, 126, 234, 0.8)',
                    borderColor: 'rgba(103, 126, 234, 1)',
                    borderWidth: 1,
                    borderRadius: 10
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#fff'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#fff'
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeOutBounce'
                }
            }
        });
    }

    createSEOChart() {
        const seoCanvas = document.getElementById('seoChart');
        if (!seoCanvas) return;

        const ctx = seoCanvas.getContext('2d');
        const seoScore = parseInt(seoCanvas.getAttribute('data-seo-score') || '75');

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [seoScore, 100 - seoScore],
                    backgroundColor: [
                        seoScore >= 80 ? 'rgba(17, 153, 142, 0.8)' : 
                        seoScore >= 60 ? 'rgba(255, 206, 84, 0.8)' : 
                        'rgba(240, 147, 251, 0.8)',
                        'rgba(255, 255, 255, 0.1)'
                    ],
                    borderWidth: 0,
                    cutout: '70%'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                animation: {
                    duration: 3000
                }
            },
            plugins: [{
                id: 'centerText',
                beforeDraw: function(chart) {
                    const ctx = chart.ctx;
                    ctx.save();
                    const centerX = chart.chartArea.left + (chart.chartArea.right - chart.chartArea.left) / 2;
                    const centerY = chart.chartArea.top + (chart.chartArea.bottom - chart.chartArea.top) / 2;
                    
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = '#fff';
                    ctx.font = 'bold 24px Arial';
                    ctx.fillText(seoScore + '%', centerX, centerY);
                    ctx.restore();
                }
            }]
        });
    }

    createPerformanceChart() {
        const perfCanvas = document.getElementById('performanceChart');
        if (!perfCanvas) return;

        const ctx = perfCanvas.getContext('2d');
        
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Speed', 'SEO', 'Accessibility', 'Best Practices', 'Structure', 'Content'],
                datasets: [{
                    label: 'Website Performance',
                    data: [75, 85, 90, 80, 95, 88],
                    backgroundColor: 'rgba(103, 126, 234, 0.2)',
                    borderColor: 'rgba(103, 126, 234, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(103, 126, 234, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(103, 126, 234, 1)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff'
                        }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        angleLines: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        pointLabels: {
                            color: '#fff'
                        },
                        ticks: {
                            color: '#fff',
                            backdropColor: 'transparent'
                        }
                    }
                },
                animation: {
                    duration: 2500
                }
            }
        });
    }

    startLiveUpdates() {
        // Only start live updates if elements exist
        if (document.querySelectorAll('[data-live-update="true"]').length > 0) {
            setInterval(() => {
                this.updateLiveElements();
            }, 5000);
        }

        // Update progress bars if they exist
        if (document.querySelectorAll('.progress-bar').length > 0) {
            this.updateProgressBars();
        }
        
        // Start matrix effect for loading states if they exist
        if (document.querySelectorAll('.matrix-loading').length > 0) {
            this.startMatrixEffect();
        }
    }

    updateLiveElements() {
        const liveElements = document.querySelectorAll('[data-live-update="true"]');
        liveElements.forEach(element => {
            // Add subtle pulse animation to show data is updating
            element.style.animation = 'pulse 0.5s ease-in-out';
            setTimeout(() => {
                element.style.animation = '';
            }, 500);
        });
    }

    updateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const targetWidth = bar.getAttribute('data-width') || '0%';
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = targetWidth;
            }, 500);
        });
    }

    startMatrixEffect() {
        const matrixElements = document.querySelectorAll('.matrix-loading');
        matrixElements.forEach(element => {
            this.createMatrixRain(element);
        });
    }

    createMatrixRain(container) {
        if (!container || !container.appendChild) return;
        
        const chars = '0123456789ABCDEF';
        const columns = Math.floor(container.offsetWidth / 10) || 10;
        
        setInterval(() => {
            let text = '';
            for (let i = 0; i < columns; i++) {
                text += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            
            const span = document.createElement('span');
            span.className = 'matrix-text';
            span.textContent = text;
            
            try {
                container.appendChild(span);
                
                // Remove old spans
                if (container.children.length > 20) {
                    container.removeChild(container.firstChild);
                }
            } catch (error) {
                console.warn('Matrix effect error:', error);
            }
        }, 100);
    }

    // Utility function to format numbers
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    // Add ripple effect to buttons
    addRippleEffect() {
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.classList.add('ripple');
                
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const dashboard = new LiveDashboard();
    
    // Add some interactive elements
    dashboard.addRippleEffect();
    
    // Auto-refresh functionality for results pages
    if (window.location.pathname.includes('/results/')) {
        const resultId = window.location.pathname.split('/').pop();
        const statusCheck = setInterval(() => {
            fetch(`/api/status/${resultId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'completed') {
                        clearInterval(statusCheck);
                        if (window.location.search.includes('refresh=true')) {
                            window.location.reload();
                        }
                    }
                })
                .catch(console.error);
        }, 3000);
    }
});

// CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        pointer-events: none;
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);