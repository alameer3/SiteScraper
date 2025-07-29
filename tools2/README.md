# أداة الاستخراج المتطورة
# Advanced Website Extraction Tool

أداة شاملة ومتطورة لاستخراج وتحليل المواقع الإلكترونية مع ميزات أمان متقدمة ونظام تصدير شامل.

## ✨ المميزات الرئيسية

### 🎯 أنواع الاستخراج المتعددة
- **أساسي (Basic)**: استخراج سريع للمعلومات الأساسية
- **قياسي (Standard)**: تحليل متوسط مع استخراج الأصول
- **متقدم (Advanced)**: تحليل شامل مع فحص الأمان
- **كامل (Complete)**: جميع الميزات مع إنشاء أرشيف

### 🔒 ميزات الأمان
- تحليل شهادات SSL/TLS
- فحص رؤوس الأمان (Security Headers)
- كشف الثغرات الأمنية الشائعة
- تحليل أمان النماذج والمحتوى
- تقييم مستوى الخصوصية

### 📊 تحليلات شاملة
- تحليل SEO متقدم مع توصيات
- تحليل الأداء وسرعة التحميل
- كشف التقنيات المستخدمة
- تحليل هيكل الموقع
- فحص العناصر التفاعلية

### 💾 إدارة الملفات المتطورة
- تنظيم تلقائي للملفات المستخرجة
- تحميل آمن للأصول (صور، CSS، JS)
- تصدير متعدد الصيغ (JSON, CSV, HTML, PDF)
- إنشاء أرشيف مضغوط
- تقارير HTML تفاعلية

## 🚀 التثبيت والاستخدام

### المتطلبات
```bash
pip install requests beautifulsoup4 urllib3
```

### الاستخدام البسيط
```python
from tools2.advanced_extractor import AdvancedExtractor

# إنشاء أداة الاستخراج
extractor = AdvancedExtractor()

# استخراج أساسي
result = extractor.extract_basic("https://example.com")

# استخراج متقدم
result = extractor.extract_advanced("https://example.com")

print(f"النتيجة: {result['success']}")
print(f"العنوان: {result['title']}")
print(f"عدد الروابط: {result['links_count']}")
```

### الاستخدام المتقدم
```python
from tools2.advanced_extractor import AdvancedExtractor, ExtractionConfig

# إعدادات مخصصة
config = ExtractionConfig(
    extraction_type="advanced",
    extract_assets=True,
    capture_screenshots=True,
    analyze_security=True,
    max_pages=50,
    timeout=30
)

extractor = AdvancedExtractor()
result = extractor.extract_with_custom_config("https://example.com", config.to_dict())
```

### استخراج مواقع متعددة
```python
from tools2.advanced_extractor import extract_multiple_urls

urls = [
    "https://example1.com",
    "https://example2.com", 
    "https://example3.com"
]

results = extract_multiple_urls(urls, "standard")
print(f"تم استخراج {results['successful_extractions']} موقع بنجاح")
```

## 📁 هيكل الملفات

```
tools2/
├── core/                    # النواة الأساسية
│   ├── __init__.py         # تصدير الكلاسات الرئيسية
│   ├── config.py           # إعدادات الاستخراج
│   ├── session_manager.py  # إدارة الاتصالات الآمنة
│   ├── file_manager.py     # إدارة الملفات والمجلدات
│   ├── content_extractor.py # استخراج المحتوى
│   ├── security_analyzer.py # تحليل الأمان
│   ├── asset_downloader.py # تحميل الأصول
│   └── extractor_engine.py # المحرك الرئيسي
├── advanced_extractor.py   # الواجهة الرئيسية
└── README.md               # هذا الملف
```

## 🔧 التكوين والإعدادات

### الإعدادات الأساسية
```python
config = ExtractionConfig(
    target_url="https://example.com",
    extraction_type="standard",  # basic, standard, advanced, complete
    output_directory="extracted_files",
    timeout=30,
    max_retries=3,
    verify_ssl=True
)
```

### ميزات الاستخراج
```python
config = ExtractionConfig(
    extract_content=True,     # استخراج المحتوى
    extract_assets=True,      # تحميل الأصول
    extract_images=True,      # تحميل الصور
    extract_css=True,         # تحميل ملفات CSS
    extract_js=True,          # تحميل ملفات JavaScript
    capture_screenshots=False, # التقاط لقطات الشاشة
    analyze_seo=True,         # تحليل SEO
    analyze_security=True,    # تحليل الأمان
    analyze_performance=True  # تحليل الأداء
)
```

### إعدادات التصدير
```python
config = ExtractionConfig(
    export_json=True,   # تصدير JSON
    export_csv=True,    # تصدير CSV
    export_html=True,   # تصدير تقرير HTML
    export_pdf=False    # تصدير PDF (يتطلب مكتبات إضافية)
)
```

## 📊 مثال على النتائج

```python
{
    "success": True,
    "extraction_id": 1,
    "url": "https://example.com",
    "title": "Example Domain",
    "domain": "example.com",
    "extraction_type": "advanced",
    "duration": 2.5,
    
    # معلومات أساسية
    "links_count": 15,
    "images_count": 8,
    "scripts_count": 3,
    "technologies": ["jQuery", "Bootstrap"],
    
    # تحليل الأمان
    "security_analysis": {
        "ssl_analysis": {"grade": "A", "enabled": True},
        "security_score": {"score": 85, "level": "جيد"}
    },
    
    # تحليل SEO
    "seo_analysis": {
        "seo_score": {"score": 75, "percentage": 75},
        "meta_tags": {"description": "..."},
        "seo_recommendations": [...]
    },
    
    # الملفات المُنشأة
    "extraction_folder": "/path/to/extracted_files/...",
    "assets": {"images": [...], "css": [...], "js": [...]},
    "archive_path": "/path/to/archive.zip"
}
```

## 🛡️ ميزات الأمان

### حماية الشبكة
- تحديد حجم أقصى للملفات المُحمّلة
- تطبيق حدود زمنية للطلبات
- التحقق من شهادات SSL
- إعادة المحاولة الذكية للطلبات الفاشلة

### حماية النظام
- تطهير أسماء الملفات من الأحرف الخطيرة
- فحص أنواع الملفات المسموحة
- منع الكتابة خارج المجلدات المحددة
- تنظيف الملفات المؤقتة تلقائياً

### تحليل الثغرات
- فحص مخاطر XSS
- كشف إمكانية SQL Injection
- فحص تسريب المعلومات الحساسة
- تحليل المكتبات القديمة والغير آمنة

## 🎨 التقارير التفاعلية

تنتج الأداة تقارير HTML تفاعلية تتضمن:
- إحصائيات مرئية للموقع
- تحليل مفصل للتقنيات المستخدمة
- توصيات تحسين الأداء والأمان
- تصميم متجاوب يدعم العربية

## 🔄 مجالات الاستخدام

### للمطورين
- تحليل المنافسين
- فحص أمان المواقع
- استخراج التقنيات المستخدمة
- تحليل هيكل المواقع

### لمحللي الأمان
- فحص الثغرات الأمنية
- تحليل شهادات SSL
- فحص رؤوس الأمان
- تقييم مستوى الخصوصية

### لخبراء SEO
- تحليل عناصر SEO
- فحص هيكل العناوين
- تحليل Meta Tags
- كشف Schema Markup

## 🚧 قيود وملاحظات

### القيود الحالية
- عدم دعم JavaScript المتقدم (يتطلب Selenium/Playwright)
- حد أقصى لحجم الملفات المُحمّلة (50MB افتراضي)
- عدد محدود من الصفحات لكل موقع (100 افتراضي)

### نصائح للأداء الأمثل
- استخدم الاستخراج الأساسي للمواقع الكبيرة
- قم بتخصيص الحد الأقصى للملفات حسب الحاجة
- فعّل التحقق من SSL للأمان الأمثل
- استخدم التأخير بين الطلبات لتجنب الحظر

## 📈 خطط التطوير

### الميزات القادمة
- دعم JavaScript المتطور مع Playwright
- تحليل أعمق لقواعد البيانات
- دعم أفضل للمواقع متعددة اللغات
- واجهة ويب تفاعلية
- دعم للمواقع التي تتطلب تسجيل دخول

### تحسينات مخططة
- تحسين سرعة الاستخراج
- دعم المزيد من صيغ التصدير
- تحليل أكثر تفصيلاً للأداء
- إضافة المزيد من فحوصات الأمان

---

## 📞 الدعم والمساهمة

هذه أداة مفتوحة المصدر ونرحب بالمساهمات والتحسينات.

### الإبلاغ عن المشاكل
- تأكد من توفر جميع المتطلبات
- قدم وصفاً مفصلاً للمشكلة
- أرفق مثالاً على الاستخدام إن أمكن

### طلب ميزات جديدة
- اشرح حالة الاستخدام
- قدم أمثلة عملية
- اقترح تطبيق الميزة

---

تم تطوير هذه الأداة بهدف توفير حل شامل وآمن لاستخراج وتحليل المواقع الإلكترونية باللغة العربية.