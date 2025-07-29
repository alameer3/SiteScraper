# أداة الاستخراج المتطورة - Advanced Website Extraction Tool

## نظرة عامة

أداة استخراج مواقع متطورة وشاملة تم بناؤها بأحدث التقنيات لتوفير تحليل شامل ودقيق للمواقع الإلكترونية. تتميز الأداة بالتنظيم المُحكم والأمان العالي وسهولة الاستخدام.

## 🚀 الميزات الرئيسية

### ✨ أنواع الاستخراج المتعددة
- **أساسي (Basic)**: استخراج سريع للمعلومات الأساسية
- **قياسي (Standard)**: تحليل متقدم مع SEO والأداء
- **متقدم (Advanced)**: تحميل الأصول مع لقطات الشاشة
- **شامل (Complete)**: جميع الميزات مع تحليل أمني شامل

### 🔒 تحليل أمني متطور
- فحص شهادات SSL/TLS
- تحليل headers الأمان
- كشف الثغرات الأمنية الشائعة
- تحليل سياسات الخصوصية

### 📊 تحليلات شاملة
- تحسين محركات البحث (SEO)
- تحليل الأداء والسرعة
- هيكل الموقع والوصولية
- اكتشاف التقنيات المستخدمة

### 💾 إدارة الأصول
- تحميل آمن للصور وملفات CSS/JS
- تنظيم تلقائي للملفات
- ضغط وأرشفة النتائج
- إحصائيات مفصلة عن التحميل

### 📈 تقارير متنوعة
- تقارير HTML تفاعلية
- تصدير JSON و CSV
- إحصائيات مرئية
- تقارير PDF (اختياري)

## 🏗️ البنية المعمارية

```
tools2/
├── core/                    # النواة الأساسية
│   ├── __init__.py         # واجهة المودیول
│   ├── config.py           # إعدادات النظام
│   ├── session_manager.py  # إدارة الاتصالات
│   ├── file_manager.py     # إدارة الملفات
│   ├── content_extractor.py # استخراج المحتوى
│   ├── security_analyzer.py # تحليل الأمان
│   ├── asset_downloader.py # تحميل الأصول
│   └── extractor_engine.py # المحرك الرئيسي
├── advanced_extractor.py   # الواجهة المبسطة
└── README.md               # هذا الملف
```

## 🛠️ الاستخدام

### الاستخدام الأساسي

```python
from tools2 import AdvancedWebsiteExtractor

# إنشاء مُستخرج
extractor = AdvancedWebsiteExtractor()

# استخراج أساسي
result = extractor.extract_basic("https://example.com")

# استخراج قياسي
result = extractor.extract_standard("https://example.com")

# استخراج متقدم
result = extractor.extract_advanced("https://example.com")

# استخراج شامل
result = extractor.extract_complete("https://example.com")
```

### الاستخدام المتقدم

```python
# إعدادات مخصصة
custom_config = extractor.create_custom_config(
    extraction_type="advanced",
    extract_assets=True,
    capture_screenshots=True,
    analyze_security=True,
    export_formats=['json', 'html', 'csv']
)

result = extractor.extract_with_custom_config("https://example.com", custom_config)
```

### الاستخراج السريع

```python
from tools2.advanced_extractor import quick_extract, extract_complete_analysis

# استخراج سريع
result = quick_extract("https://example.com", "standard")

# تحليل شامل
result = extract_complete_analysis("https://example.com")
```

### الاستخراج المتعدد

```python
from tools2.advanced_extractor import batch_extract

urls = [
    "https://example1.com",
    "https://example2.com", 
    "https://example3.com"
]

results = batch_extract(urls, "standard")
print(f"تم استخراج {results['successful_extractions']} موقع بنجاح")
```

## ⚙️ الإعدادات

### إعدادات الاستخراج الأساسية

```python
config = {
    "target_url": "https://example.com",
    "extraction_type": "standard",
    "timeout": 30,
    "max_retries": 3,
    "verify_ssl": True,
    "max_depth": 3,
    "max_pages": 100
}
```

### إعدادات الميزات

```python
features = {
    "extract_content": True,
    "extract_assets": True,
    "extract_images": True,
    "capture_screenshots": False,
    "analyze_seo": True,
    "analyze_security": True,
    "detect_technologies": True
}
```

### إعدادات التصدير

```python
exports = {
    "export_json": True,
    "export_csv": True,
    "export_html": True,
    "export_pdf": False
}
```

## 📁 هيكل النتائج

```
extracted_files/
├── content/                 # محتوى المواقع المستخرجة
│   └── extraction_123_20250729_143052/
│       ├── html/           # ملفات HTML
│       ├── assets/         # الأصول المحملة
│       │   ├── images/     # الصور
│       │   ├── css/        # ملفات CSS
│       │   ├── js/         # ملفات JavaScript
│       │   └── fonts/      # الخطوط
│       ├── data/           # البيانات المستخرجة
│       ├── analysis/       # تحليلات مفصلة
│       └── exports/        # التقارير والتصديرات
├── reports/                # التقارير العامة
├── screenshots/            # لقطات الشاشة
└── archives/              # الأرشيف المضغوط
```

## 🔧 متطلبات النظام

### المكتبات المطلوبة
- `requests>=2.31.0` - للاتصالات HTTP
- `beautifulsoup4>=4.12.0` - لتحليل HTML
- `urllib3>=2.0.0` - لإدارة الاتصالات
- `pathlib` - لإدارة المسارات (مُضمن في Python 3.4+)

### المكتبات الاختيارية
- `Pillow` - لمعالجة الصور
- `selenium` - للمواقع التفاعلية
- `playwright` - للعرض المتقدم

## 🛡️ الأمان

### الحماية المُدمجة
- ✅ التحقق من شهادات SSL
- ✅ حدود حجم الملفات
- ✅ تطهير أسماء الملفات
- ✅ معدل محدود للطلبات
- ✅ مهلة زمنية للاتصالات

### أفضل الممارسات
- استخدام HTTPS عند الإمكان
- التحقق من المدخلات
- إدارة آمنة للذاكرة
- تسجيل مفصل للأخطاء

## 📊 مثال للنتائج

```json
{
  "extraction_id": 1,
  "url": "https://example.com",
  "success": true,
  "title": "Example Domain",
  "description": "This domain is for use in illustrative examples",
  "domain": "example.com",
  "status_code": 200,
  "content_length": 1256,
  "links_count": 1,
  "images_count": 0,
  "technologies": ["HTML5"],
  "seo_analysis": {
    "score": 75,
    "issues": ["وصف الصفحة قصير"]
  },
  "security_analysis": {
    "ssl_grade": "A",
    "security_score": 85
  },
  "performance_analysis": {
    "response_time_seconds": 0.234,
    "content_size_mb": 0.001,
    "performance_score": 90
  },
  "duration": 2.45,
  "extraction_folder": "/path/to/extracted_files/content/..."
}
```

## 🚀 الأداء

### معدلات السرعة
- **استخراج أساسي**: 1-3 ثوانٍ
- **استخراج قياسي**: 3-8 ثوانٍ  
- **استخراج متقدم**: 10-30 ثانية
- **استخراج شامل**: 30-60 ثانية

### الذاكرة
- استهلاك ذاكرة محسن
- إدارة تلقائية للموارد
- تنظيف دوري للملفات المؤقتة

## 🔄 التحديثات الأخيرة

### الإصدار 1.0.0 (29 يوليو 2025)
- ✅ إعادة بناء كاملة للأداة
- ✅ تقسيم الكود إلى وحدات منفصلة
- ✅ تحسين الأمان والاستقرار
- ✅ واجهة استخدام مبسطة
- ✅ دعم الاستخراج المتعدد
- ✅ تقارير تفاعلية محسنة

## 📞 الدعم الفني

للحصول على المساعدة أو الإبلاغ عن مشاكل:
1. راجع هذا الدليل أولاً
2. تحقق من ملفات السجل (logs)
3. تأكد من إعدادات الشبكة
4. راجع متطلبات النظام

## 📄 الترخيص

هذه الأداة مطورة لأغراض تعليمية وبحثية. يُرجى مراعاة شروط الاستخدام للمواقع المستهدفة واحترام سياسات robots.txt.

---

**تم التطوير بواسطة**: فريق تحليل المواقع المتقدم  
**التحديث الأخير**: 29 يوليو 2025  
**الإصدار**: 1.0.0