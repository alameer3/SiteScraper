
// ملف JavaScript الرئيسي للموقع المطابق

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل الموقع المطابق بنجاح');
    
    // إضافة تفاعلات أساسية
    initializeBasicInteractions();
    
    // تحسين الأداء
    optimizePerformance();
});

function initializeBasicInteractions() {
    // إضافة تأثيرات للعناصر
    const headings = document.querySelectorAll('.heading');
    headings.forEach(heading => {
        heading.addEventListener('mouseover', function() {
            this.style.color = '#007bff';
        });
        
        heading.addEventListener('mouseout', function() {
            this.style.color = '#2c3e50';
        });
    });
    
    // تحسين التمرير
    window.addEventListener('scroll', function() {
        const header = document.querySelector('.main-header');
        if (window.scrollY > 100) {
            header.style.position = 'fixed';
            header.style.top = '0';
            header.style.width = '100%';
            header.style.zIndex = '1000';
        } else {
            header.style.position = 'static';
        }
    });
}

function optimizePerformance() {
    // تحسين تحميل الصور
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.loading = 'lazy';
    });
    
    // إضافة مؤشر التحميل
    const loadingIndicator = document.createElement('div');
    loadingIndicator.innerHTML = 'جاري التحميل...';
    loadingIndicator.style.display = 'none';
    document.body.appendChild(loadingIndicator);
}

// وظائف مساعدة
function showLoading() {
    document.querySelector('div[innerHTML*="جاري التحميل"]').style.display = 'block';
}

function hideLoading() {
    document.querySelector('div[innerHTML*="جاري التحميل"]').style.display = 'none';
}
