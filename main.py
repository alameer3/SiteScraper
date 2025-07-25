from app import app
import routes  # استيراد ملف الطرق الجديد والمنظم

# تسجيل أداة الاستخراج المتطورة
try:
    from extraction_ui_handler import ExtractionUIHandler
    extraction_handler = ExtractionUIHandler(app)
    extraction_handler.register_routes()
    print("✅ تم تحميل أداة الاستخراج المتطورة بنجاح")
except ImportError as e:
    print(f"⚠️ تحذير: لم يتم تحميل أداة الاستخراج المتطورة: {e}")