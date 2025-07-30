/**
 * نظام الاستجابة الفائقة - Ultra Fast Response System
 */

class FastResponseManager {
    constructor() {
        this.startTime = null;
        this.responseTimer = null;
        this.maxWaitTime = 5000; // 5 ثواني كحد أقصى
        this.init();
    }

    init() {
        // مراقبة إرسال النماذج
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleFormSubmit(e);
            });
        });

        // إضافة مؤشر التحميل المحسن
        this.setupLoadingIndicators();
    }

    handleFormSubmit(event) {
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            this.startLoading(submitBtn);
            this.startResponseTimer();
        }
    }

    startLoading(btn) {
        this.startTime = Date.now();
        
        // إخفاء النص الأصلي وإظهار التحميل
        const btnText = btn.querySelector('.btn-text');
        const btnLoading = btn.querySelector('.btn-loading');
        
        if (btnText && btnLoading) {
            btnText.classList.add('d-none');
            btnLoading.classList.remove('d-none');
        }
        
        // تعطيل الزر
        btn.disabled = true;
        
        // إضافة animation
        btn.classList.add('loading-animation');
        
        // عداد الوقت المباشر
        this.updateLoadingText(btn);
    }

    updateLoadingText(btn) {
        const loadingSpan = btn.querySelector('.btn-loading');
        let seconds = 0;
        
        const timer = setInterval(() => {
            seconds++;
            if (loadingSpan) {
                loadingSpan.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    جاري التحليل... (${seconds}s)
                `;
            }
            
            // إذا تجاوز 5 ثوان، أظهر رسالة
            if (seconds >= 5) {
                if (loadingSpan) {
                    loadingSpan.innerHTML = `
                        <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                        المعالجة تستغرق وقتاً أطول... (${seconds}s)
                    `;
                }
            }
        }, 1000);
        
        // حفظ المؤقت لإيقافه لاحقاً
        btn.dataset.timer = timer;
    }

    startResponseTimer() {
        // مراقبة وقت الاستجابة
        this.responseTimer = setTimeout(() => {
            this.showSlowResponseWarning();
        }, this.maxWaitTime);
    }

    showSlowResponseWarning() {
        // إظهار تحذير إذا كانت الاستجابة بطيئة
        const warningDiv = document.createElement('div');
        warningDiv.className = 'alert alert-warning mt-3 fade-in';
        warningDiv.innerHTML = `
            <i class="fas fa-clock me-2"></i>
            <strong>الاستجابة تستغرق وقتاً أطول من المعتاد</strong><br>
            <small>قد يكون الموقع محمي أو بطيء الاستجابة. جاري المحاولة بطرق بديلة...</small>
        `;
        
        // إضافة التحذير بعد النموذج
        const form = document.querySelector('form');
        if (form && !document.querySelector('.slow-response-warning')) {
            warningDiv.classList.add('slow-response-warning');
            form.parentNode.insertBefore(warningDiv, form.nextSibling);
        }
    }

    stopLoading(btn) {
        const responseTime = Date.now() - this.startTime;
        
        // إيقاف المؤقتات
        if (this.responseTimer) {
            clearTimeout(this.responseTimer);
        }
        
        const timer = btn.dataset.timer;
        if (timer) {
            clearInterval(timer);
        }
        
        // استعادة الزر
        btn.disabled = false;
        btn.classList.remove('loading-animation');
        
        const btnText = btn.querySelector('.btn-text');
        const btnLoading = btn.querySelector('.btn-loading');
        
        if (btnText && btnLoading) {
            btnText.classList.remove('d-none');
            btnLoading.classList.add('d-none');
        }
        
        // إظهار وقت الاستجابة
        this.showResponseTime(responseTime);
        
        // إزالة تحذير البطء إن وجد
        const warning = document.querySelector('.slow-response-warning');
        if (warning) {
            warning.remove();
        }
    }

    showResponseTime(responseTime) {
        const timeInSeconds = (responseTime / 1000).toFixed(2);
        
        // إنشاء رسالة الوقت
        const timeDiv = document.createElement('div');
        timeDiv.className = 'alert alert-info mt-2 fade-in response-time-info';
        
        let emoji = '⚡';
        let message = 'فائق السرعة';
        
        if (responseTime < 2000) {
            emoji = '⚡';
            message = 'فائق السرعة';
        } else if (responseTime < 5000) {
            emoji = '🚀';
            message = 'سريع';
        } else {
            emoji = '⏱️';
            message = 'عادي';
        }
        
        timeDiv.innerHTML = `
            ${emoji} <strong>وقت الاستجابة:</strong> ${timeInSeconds} ثانية (${message})
        `;
        
        // إضافة رسالة الوقت
        const resultsContainer = document.querySelector('.results-container');
        if (resultsContainer) {
            // إزالة رسالة الوقت السابقة
            const oldTimeInfo = document.querySelector('.response-time-info');
            if (oldTimeInfo) {
                oldTimeInfo.remove();
            }
            
            resultsContainer.insertBefore(timeDiv, resultsContainer.firstChild);
            
            // إزالة الرسالة بعد 5 ثوان
            setTimeout(() => {
                if (timeDiv.parentNode) {
                    timeDiv.classList.add('fade-out');
                    setTimeout(() => timeDiv.remove(), 500);
                }
            }, 5000);
        }
    }

    setupLoadingIndicators() {
        // إضافة CSS للحركات
        const style = document.createElement('style');
        style.textContent = `
            .loading-animation {
                position: relative;
                overflow: hidden;
            }
            
            .loading-animation::after {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
                animation: shimmer 1.5s infinite;
            }
            
            @keyframes shimmer {
                0% { left: -100%; }
                100% { left: 100%; }
            }
            
            .fade-in {
                animation: fadeIn 0.5s ease-in;
            }
            
            .fade-out {
                animation: fadeOut 0.5s ease-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes fadeOut {
                from { opacity: 1; transform: translateY(0); }
                to { opacity: 0; transform: translateY(-10px); }
            }
        `;
        document.head.appendChild(style);
    }

    // فحص سريع لحالة الخادم
    async checkServerHealth() {
        try {
            const response = await fetch('/api/health', { 
                method: 'GET',
                timeout: 2000 
            });
            return response.ok;
        } catch (error) {
            console.warn('فحص حالة الخادم فشل:', error);
            return false;
        }
    }
}

// تهيئة المدير عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    window.fastResponseManager = new FastResponseManager();
    
    // فحص دوري لحالة الخادم
    setInterval(() => {
        window.fastResponseManager.checkServerHealth();
    }, 30000); // كل 30 ثانية
});

// مراقبة تحميل الصفحة وإيقاف التحميل عند الانتهاء
window.addEventListener('load', () => {
    // إيقاف جميع مؤشرات التحميل عند تحميل الصفحة
    document.querySelectorAll('button[disabled]').forEach(btn => {
        if (window.fastResponseManager) {
            window.fastResponseManager.stopLoading(btn);
        }
    });
});