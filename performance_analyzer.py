"""
محلل الأداء المتقدم - Advanced Performance Analyzer
يقوم بقياس وتحليل أداء المواقع الإلكترونية بشكل شامل
"""

import time
import requests
from urllib.parse import urlparse, urljoin
import re
import json
import logging
from bs4 import BeautifulSoup

class PerformanceAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def analyze_performance(self, url):
        """تحليل أداء شامل للموقع"""
        try:
            performance_report = {
                'url': url,
                'loading_metrics': self._measure_loading_performance(url),
                'resource_analysis': self._analyze_resources(url),
                'optimization_opportunities': self._identify_optimizations(url),
                'caching_analysis': self._analyze_caching(url),
                'compression_analysis': self._analyze_compression(url),
                'mobile_performance': self._analyze_mobile_performance(url),
                'core_web_vitals': self._estimate_core_web_vitals(url),
                'performance_score': 0,
                'recommendations': []
            }
            
            # حساب النقاط الإجمالية
            performance_report['performance_score'] = self._calculate_performance_score(performance_report)
            performance_report['recommendations'] = self._generate_performance_recommendations(performance_report)
            
            return performance_report
            
        except Exception as e:
            logging.error(f"خطأ في تحليل الأداء: {e}")
            return {'error': str(e)}

    def _measure_loading_performance(self, url):
        """قياس أداء التحميل"""
        metrics = {
            'total_load_time': 0,
            'dns_lookup_time': 0,
            'connection_time': 0,
            'ssl_handshake_time': 0,
            'first_byte_time': 0,
            'content_download_time': 0,
            'redirect_count': 0,
            'final_url': url
        }
        
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=30, allow_redirects=True)
            end_time = time.time()
            
            metrics['total_load_time'] = round((end_time - start_time) * 1000, 2)  # milliseconds
            metrics['redirect_count'] = len(response.history)
            metrics['final_url'] = response.url
            metrics['status_code'] = response.status_code
            metrics['content_size'] = len(response.content)
            
            # تقدير أوقات مكونات التحميل
            if hasattr(response, 'elapsed'):
                total_elapsed = response.elapsed.total_seconds() * 1000
                metrics['first_byte_time'] = round(total_elapsed * 0.7, 2)
                metrics['content_download_time'] = round(total_elapsed * 0.3, 2)
            
        except Exception as e:
            logging.error(f"خطأ في قياس الأداء: {e}")
            metrics['error'] = str(e)
        
        return metrics

    def _analyze_resources(self, url):
        """تحليل الموارد والأصول"""
        resources = {
            'total_requests': 0,
            'total_size': 0,
            'images': {'count': 0, 'size': 0, 'unoptimized': []},
            'css': {'count': 0, 'size': 0, 'blocking': []},
            'javascript': {'count': 0, 'size': 0, 'blocking': []},
            'fonts': {'count': 0, 'size': 0},
            'third_party': {'count': 0, 'domains': []},
            'largest_resources': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            base_domain = urlparse(url).netloc
            
            # تحليل الصور
            images = soup.find_all('img')
            resources['images']['count'] = len(images)
            
            for img in images:
                src = img.get('src') or img.get('data-src')
                if src:
                    img_url = urljoin(url, src)
                    if not img.get('width') or not img.get('height'):
                        resources['images']['unoptimized'].append(src)
            
            # تحليل CSS
            css_links = soup.find_all('link', {'rel': 'stylesheet'})
            resources['css']['count'] = len(css_links)
            
            for css in css_links:
                href = css.get('href')
                if href and 'render-blocking' not in css.get('media', ''):
                    resources['css']['blocking'].append(href)
            
            # تحليل JavaScript
            scripts = soup.find_all('script')
            resources['javascript']['count'] = len(scripts)
            
            for script in scripts:
                src = script.get('src')
                if src:
                    if not script.get('async') and not script.get('defer'):
                        resources['javascript']['blocking'].append(src)
                    
                    # فحص النطاقات الخارجية
                    script_domain = urlparse(urljoin(url, src)).netloc
                    if script_domain != base_domain and script_domain not in resources['third_party']['domains']:
                        resources['third_party']['domains'].append(script_domain)
                        resources['third_party']['count'] += 1
            
            # تحليل الخطوط
            font_links = soup.find_all('link', href=re.compile(r'\.(woff|woff2|ttf|eot)'))
            resources['fonts']['count'] = len(font_links)
            
        except Exception as e:
            logging.error(f"خطأ في تحليل الموارد: {e}")
            resources['error'] = str(e)
        
        return resources

    def _identify_optimizations(self, url):
        """تحديد فرص التحسين"""
        optimizations = {
            'image_optimization': [],
            'css_optimization': [],
            'javascript_optimization': [],
            'caching_improvements': [],
            'compression_opportunities': [],
            'critical_path_optimizations': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # تحسين الصور
            images = soup.find_all('img')
            large_images = 0
            for img in images:
                if not img.get('loading') == 'lazy':
                    optimizations['image_optimization'].append('إضافة lazy loading للصور')
                if not img.get('alt'):
                    optimizations['image_optimization'].append('إضافة وصف بديل للصور')
                
                # فحص تنسيقات الصور الحديثة
                src = img.get('src', '')
                if not any(fmt in src.lower() for fmt in ['.webp', '.avif']):
                    optimizations['image_optimization'].append('استخدام تنسيقات صور حديثة (WebP, AVIF)')
            
            # تحسين CSS
            css_links = soup.find_all('link', {'rel': 'stylesheet'})
            if len(css_links) > 3:
                optimizations['css_optimization'].append('دمج ملفات CSS المتعددة')
            
            for css in css_links:
                if not css.get('media'):
                    optimizations['css_optimization'].append('تحديد media queries لملفات CSS')
            
            # تحسين JavaScript
            scripts = soup.find_all('script')
            inline_scripts = len([s for s in scripts if not s.get('src')])
            if inline_scripts > 5:
                optimizations['javascript_optimization'].append('تقليل النصوص المدمجة')
            
            blocking_scripts = len([s for s in scripts if s.get('src') and not s.get('async') and not s.get('defer')])
            if blocking_scripts > 0:
                optimizations['javascript_optimization'].append('إضافة async/defer للنصوص')
            
            # فحص المسار الحرج
            if not soup.find('link', {'rel': 'preload'}):
                optimizations['critical_path_optimizations'].append('إضافة preload للموارد المهمة')
            
            if not soup.find('link', {'rel': 'dns-prefetch'}):
                optimizations['critical_path_optimizations'].append('إضافة DNS prefetch للنطاقات الخارجية')
            
        except Exception as e:
            logging.error(f"خطأ في تحديد التحسينات: {e}")
            optimizations['error'] = str(e)
        
        return optimizations

    def _analyze_caching(self, url):
        """تحليل استراتيجيات التخزين المؤقت"""
        caching = {
            'cache_control': '',
            'expires': '',
            'etag': '',
            'last_modified': '',
            'browser_cache_score': 0,
            'cdn_detected': False,
            'cache_recommendations': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            headers = response.headers
            
            caching['cache_control'] = headers.get('Cache-Control', '')
            caching['expires'] = headers.get('Expires', '')
            caching['etag'] = headers.get('ETag', '')
            caching['last_modified'] = headers.get('Last-Modified', '')
            
            # تقييم التخزين المؤقت
            score = 0
            if caching['cache_control']:
                score += 25
            if caching['expires']:
                score += 25
            if caching['etag']:
                score += 25
            if caching['last_modified']:
                score += 25
            
            caching['browser_cache_score'] = score
            
            # كشف CDN
            cdn_headers = ['cf-ray', 'x-cache', 'x-served-by', 'x-amz-cf-id']
            for header in cdn_headers:
                if header.lower() in [h.lower() for h in headers.keys()]:
                    caching['cdn_detected'] = True
                    break
            
            # توصيات التخزين المؤقت
            if not caching['cache_control']:
                caching['cache_recommendations'].append('إضافة Cache-Control headers')
            if not caching['cdn_detected']:
                caching['cache_recommendations'].append('استخدام CDN لتسريع التحميل')
            
        except Exception as e:
            logging.error(f"خطأ في تحليل التخزين المؤقت: {e}")
            caching['error'] = str(e)
        
        return caching

    def _analyze_compression(self, url):
        """تحليل ضغط المحتوى"""
        compression = {
            'gzip_enabled': False,
            'brotli_enabled': False,
            'content_encoding': '',
            'compression_ratio': 0,
            'uncompressed_size': 0,
            'compressed_size': 0
        }
        
        try:
            # طلب مع قبول الضغط
            headers = {'Accept-Encoding': 'gzip, deflate, br'}
            response = self.session.get(url, headers=headers, timeout=10)
            
            compression['content_encoding'] = response.headers.get('Content-Encoding', '')
            compression['gzip_enabled'] = 'gzip' in compression['content_encoding']
            compression['brotli_enabled'] = 'br' in compression['content_encoding']
            
            # حساب نسبة الضغط
            compressed_size = len(response.content)
            
            # طلب بدون ضغط للمقارنة
            headers_no_compress = {'Accept-Encoding': 'identity'}
            response_uncompressed = self.session.get(url, headers=headers_no_compress, timeout=10)
            uncompressed_size = len(response_uncompressed.content)
            
            compression['compressed_size'] = compressed_size
            compression['uncompressed_size'] = uncompressed_size
            
            if uncompressed_size > 0:
                compression['compression_ratio'] = round(
                    ((uncompressed_size - compressed_size) / uncompressed_size) * 100, 2
                )
            
        except Exception as e:
            logging.error(f"خطأ في تحليل الضغط: {e}")
            compression['error'] = str(e)
        
        return compression

    def _analyze_mobile_performance(self, url):
        """تحليل أداء الهاتف المحمول"""
        mobile = {
            'viewport_configured': False,
            'responsive_design': False,
            'touch_friendly': False,
            'mobile_load_time': 0,
            'mobile_score': 0
        }
        
        try:
            # محاكاة متصفح الهاتف
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15'
            }
            
            start_time = time.time()
            response = self.session.get(url, headers=mobile_headers, timeout=10)
            end_time = time.time()
            
            mobile['mobile_load_time'] = round((end_time - start_time) * 1000, 2)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # فحص viewport
            viewport = soup.find('meta', {'name': 'viewport'})
            mobile['viewport_configured'] = viewport is not None
            
            # فحص التصميم المتجاوب
            css_links = soup.find_all('link', {'rel': 'stylesheet'})
            for link in css_links:
                if 'responsive' in link.get('href', '').lower():
                    mobile['responsive_design'] = True
                    break
            
            # فحص عناصر اللمس
            touch_elements = soup.find_all(['button', 'a'], class_=re.compile(r'touch|mobile|btn'))
            mobile['touch_friendly'] = len(touch_elements) > 0
            
            # حساب نقاط الهاتف المحمول
            score = 0
            if mobile['viewport_configured']:
                score += 30
            if mobile['responsive_design']:
                score += 30
            if mobile['touch_friendly']:
                score += 20
            if mobile['mobile_load_time'] < 3000:
                score += 20
            
            mobile['mobile_score'] = score
            
        except Exception as e:
            logging.error(f"خطأ في تحليل أداء المحمول: {e}")
            mobile['error'] = str(e)
        
        return mobile

    def _estimate_core_web_vitals(self, url):
        """تقدير مؤشرات الويب الأساسية"""
        vitals = {
            'largest_contentful_paint': 0,  # LCP
            'first_input_delay': 0,        # FID
            'cumulative_layout_shift': 0,  # CLS
            'first_contentful_paint': 0,   # FCP
            'time_to_interactive': 0,      # TTI
            'total_blocking_time': 0       # TBT
        }
        
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=10)
            end_time = time.time()
            
            load_time = (end_time - start_time) * 1000
            
            # تقديرات بناءً على وقت التحميل وحجم المحتوى
            content_size = len(response.content)
            
            # LCP تقدير
            vitals['largest_contentful_paint'] = min(load_time * 0.8, 4000)
            
            # FCP تقدير
            vitals['first_contentful_paint'] = min(load_time * 0.3, 2000)
            
            # TTI تقدير
            vitals['time_to_interactive'] = min(load_time * 1.2, 6000)
            
            # TBT تقدير (بناءً على JavaScript)
            soup = BeautifulSoup(response.content, 'html.parser')
            scripts = soup.find_all('script')
            vitals['total_blocking_time'] = len(scripts) * 10
            
            # FID تقدير
            vitals['first_input_delay'] = min(vitals['total_blocking_time'] * 0.1, 300)
            
            # CLS تقدير (بناءً على الصور بدون أبعاد)
            images_without_dimensions = len([
                img for img in soup.find_all('img') 
                if not img.get('width') or not img.get('height')
            ])
            vitals['cumulative_layout_shift'] = min(images_without_dimensions * 0.02, 0.25)
            
        except Exception as e:
            logging.error(f"خطأ في تقدير مؤشرات الويب: {e}")
            vitals['error'] = str(e)
        
        return vitals

    def _calculate_performance_score(self, performance_report):
        """حساب النقاط الإجمالية للأداء"""
        total_score = 100
        
        # خصم نقاط بناءً على وقت التحميل
        load_time = performance_report['loading_metrics'].get('total_load_time', 0)
        if load_time > 3000:  # أكثر من 3 ثواني
            total_score -= 30
        elif load_time > 1500:  # أكثر من 1.5 ثانية
            total_score -= 15
        
        # خصم نقاط للموارد غير المحسنة
        resources = performance_report['resource_analysis']
        if resources.get('images', {}).get('unoptimized'):
            total_score -= 10
        if resources.get('css', {}).get('blocking'):
            total_score -= 10
        if resources.get('javascript', {}).get('blocking'):
            total_score -= 10
        
        # نقاط للتخزين المؤقت
        cache_score = performance_report['caching_analysis'].get('browser_cache_score', 0)
        total_score += (cache_score - 50) * 0.2  # تطبيع النقاط
        
        # نقاط للضغط
        compression = performance_report['compression_analysis']
        if compression.get('gzip_enabled') or compression.get('brotli_enabled'):
            total_score += 5
        
        # نقاط للهاتف المحمول
        mobile_score = performance_report['mobile_performance'].get('mobile_score', 0)
        total_score += (mobile_score - 50) * 0.2
        
        return max(0, min(100, round(total_score, 1)))

    def _generate_performance_recommendations(self, performance_report):
        """توليد توصيات تحسين الأداء"""
        recommendations = []
        
        # توصيات وقت التحميل
        load_time = performance_report['loading_metrics'].get('total_load_time', 0)
        if load_time > 3000:
            recommendations.append('تحسين وقت التحميل - يجب أن يكون أقل من 3 ثواني')
        
        # توصيات الموارد
        optimizations = performance_report['optimization_opportunities']
        for category, items in optimizations.items():
            if items and isinstance(items, list):
                recommendations.extend(items[:2])  # أخذ أول توصيتين من كل فئة
        
        # توصيات التخزين المؤقت
        cache_recs = performance_report['caching_analysis'].get('cache_recommendations', [])
        recommendations.extend(cache_recs)
        
        # توصيات الضغط
        compression = performance_report['compression_analysis']
        if not compression.get('gzip_enabled') and not compression.get('brotli_enabled'):
            recommendations.append('تفعيل ضغط المحتوى (Gzip/Brotli)')
        
        # توصيات الهاتف المحمول
        mobile = performance_report['mobile_performance']
        if not mobile.get('viewport_configured'):
            recommendations.append('إضافة meta viewport للتصميم المتجاوب')
        
        return recommendations[:10]  # أهم 10 توصيات

    def generate_performance_audit(self, analysis_results):
        """توليد تدقيق أداء مفصل"""
        audit = {
            'executive_summary': self._create_performance_summary(analysis_results),
            'detailed_metrics': analysis_results,
            'benchmark_comparison': self._compare_with_benchmarks(analysis_results),
            'improvement_roadmap': self._create_improvement_roadmap(analysis_results),
            'monitoring_suggestions': self._suggest_monitoring_tools()
        }
        return audit

    def _create_performance_summary(self, analysis):
        """إنشاء ملخص الأداء"""
        score = analysis.get('performance_score', 0)
        load_time = analysis.get('loading_metrics', {}).get('total_load_time', 0)
        
        summary = {
            'overall_performance': f'النقاط: {score}/100',
            'load_time_assessment': f'وقت التحميل: {load_time}ms',
            'performance_grade': self._get_performance_grade(score),
            'critical_issues': len([r for r in analysis.get('recommendations', []) if 'وقت التحميل' in r or 'تحسين' in r]),
            'optimization_potential': f'{100 - score}% إمكانية تحسين'
        }
        return summary

    def _get_performance_grade(self, score):
        """تحديد درجة الأداء"""
        if score >= 90:
            return 'ممتاز'
        elif score >= 75:
            return 'جيد'
        elif score >= 60:
            return 'متوسط'
        elif score >= 40:
            return 'ضعيف'
        else:
            return 'سيء جداً'

    def _compare_with_benchmarks(self, analysis):
        """مقارنة مع المعايير القياسية"""
        return {
            'industry_average': 'متوسط الصناعة: 3.5 ثانية',
            'google_target': 'هدف Google: أقل من 2.5 ثانية',
            'mobile_benchmark': 'معيار المحمول: أقل من 3 ثواني',
            'desktop_benchmark': 'معيار سطح المكتب: أقل من 2 ثانية'
        }

    def _create_improvement_roadmap(self, analysis):
        """إنشاء خريطة طريق التحسين"""
        return {
            'immediate': analysis.get('recommendations', [])[:3],
            'short_term': analysis.get('recommendations', [])[3:6],
            'long_term': analysis.get('recommendations', [])[6:]
        }

    def _suggest_monitoring_tools(self):
        """اقتراح أدوات المراقبة"""
        return {
            'free_tools': ['Google PageSpeed Insights', 'GTmetrix', 'WebPageTest'],
            'paid_tools': ['New Relic', 'Pingdom', 'DataDog'],
            'browser_tools': ['Chrome DevTools', 'Firefox Performance Tools'],
            'continuous_monitoring': ['Google Analytics', 'Real User Monitoring (RUM)']
        }