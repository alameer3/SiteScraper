from app import app  # noqa: F401
import enhanced_routes  # noqa: F401
from enhanced_routes import *  # Import enhanced routes
from scraper import WebScraper
from analyzer import WebsiteAnalyzer
from security_analyzer import SecurityAnalyzer
from models import db, ScrapeResult
import threading
import time
import json

@app.route('/history')
def history():
    """Display analysis history"""
    results = ScrapeResult.query.order_by(ScrapeResult.created_at.desc()).limit(20).all()
    return render_template('history.html', results=results)

@app.route('/security_analysis')
def security_analysis_form():
    """عرض نموذج تحليل الأمان"""
    return render_template('security_analysis.html')

@app.route('/analyze_security', methods=['POST'])
def analyze_security():
    """تحليل أمان متقدم للموقع"""
    try:
        url = request.form.get('url', '').strip()

        if not url:
            flash('يرجى إدخال رابط صحيح', 'error')
            return redirect(url_for('security_analysis_form'))

        # التحقق من صحة الرابط
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # إنشاء محلل الأمان
        security_analyzer = SecurityAnalyzer()

        def run_security_analysis():
            with app.app_context():
                try:
                    # تشغيل التحليل الأمني
                    analysis_result = security_analyzer.analyze_security(url)

                    # حفظ النتائج
                    result = ScrapeResult(
                        url=url,
                        status='completed',
                        data=json.dumps(analysis_result),
                        analysis_type='security'
                    )
                    db.session.add(result)
                    db.session.commit()

                    flash('تم تحليل الأمان بنجاح!', 'success')

                except Exception as e:
                    app.logger.error(f"خطأ في تحليل الأمان: {e}")
                    # حفظ خطأ
                    result = ScrapeResult(
                        url=url,
                        status='error',
                        data=json.dumps({'error': str(e)}),
                        analysis_type='security'
                    )
                    db.session.add(result)
                    db.session.commit()

        # تشغيل التحليل في الخلفية
        thread = threading.Thread(target=run_security_analysis)
        thread.daemon = True
        thread.start()

        flash('تم بدء تحليل الأمان. ستظهر النتائج قريباً...', 'info')

        # توجيه إلى صفحة انتظار أو النتائج
        time.sleep(2)  # انتظار قصير

        # البحث عن أحدث نتيجة
        latest_result = ScrapeResult.query.filter_by(
            url=url, 
            analysis_type='security'
        ).order_by(ScrapeResult.created_at.desc()).first()

        if latest_result and latest_result.status == 'completed':
            return redirect(url_for('security_results', result_id=latest_result.id))
        else:
            return redirect(url_for('security_analysis_form'))

    except Exception as e:
        app.logger.error(f"خطأ في معالجة طلب تحليل الأمان: {e}")
        flash(f'حدث خطأ: {str(e)}', 'error')
        return redirect(url_for('security_analysis_form'))

@app.route('/security_results/<int:result_id>')
def security_results(result_id):
    """عرض نتائج تحليل الأمان"""
    try:
        result = ScrapeResult.query.get_or_404(result_id)

        if result.status != 'completed':
            flash('التحليل لم يكتمل بعد', 'warning')
            return redirect(url_for('security_analysis_form'))

        analysis_data = json.loads(result.data)

        return render_template('advanced_security_analysis.html', 
                             analysis=analysis_data,
                             result=result)

    except Exception as e:
        app.logger.error(f"خطأ في عرض نتائج الأمان: {e}")
        flash(f'خطأ في عرض النتائج: {str(e)}', 'error')
        return redirect(url_for('security_analysis_form'))

@app.route('/export_security_report/<path:url>')
def export_security_report(url):
    """تصدير تقرير الأمان كـ JSON"""
    try:
        # البحث عن آخر تحليل أمان للرابط
        result = ScrapeResult.query.filter_by(
            url=url,
            analysis_type='security',
            status='completed'
        ).order_by(ScrapeResult.created_at.desc()).first()

        if not result:
            flash('لا توجد نتائج أمان لهذا الرابط', 'error')
            return redirect(url_for('security_analysis_form'))

        analysis_data = json.loads(result.data)

        # إنشاء استجابة JSON
        response = make_response(json.dumps(analysis_data, indent=2, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=security_report_{result.id}.json'

        return response

    except Exception as e:
        app.logger.error(f"خطأ في تصدير تقرير الأمان: {e}")
        flash(f'خطأ في التصدير: {str(e)}', 'error')
        return redirect(url_for('security_analysis_form'))