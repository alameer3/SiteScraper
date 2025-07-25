"""
محلل SEO المتقدم - Advanced SEO Analyzer
يقوم بتحليل شامل لتحسين محركات البحث
"""

import re
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import logging

class SEOAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def analyze_seo(self, url):
        """تحليل SEO شامل للموقع"""
        try:
            seo_report = {
                'url': url,
                'title_analysis': self._analyze_title(url),
                'meta_analysis': self._analyze_meta_tags(url),
                'heading_structure': self._analyze_headings(url),
                'content_analysis': self._analyze_content(url),
                'link_analysis': self._analyze_links(url),
                'image_seo': self._analyze_image_seo(url),
                'technical_seo': self._analyze_technical_seo(url),
                'structured_data': self._analyze_structured_data(url),
                'social_media': self._analyze_social_tags(url),
                'seo_score': 0,
                'recommendations': []
            }
            
            seo_report['seo_score'] = self._calculate_seo_score(seo_report)
            seo_report['recommendations'] = self._generate_seo_recommendations(seo_report)
            
            return seo_report
            
        except Exception as e:
            logging.error(f"خطأ في تحليل SEO: {e}")
            return {'error': str(e)}

    def _analyze_title(self, url):
        """تحليل عنوان الصفحة"""
        title_analysis = {
            'title': '',
            'length': 0,
            'length_status': '',
            'keyword_presence': False,
            'uniqueness_score': 0,
            'issues': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_tag = soup.find('title')
            if title_tag:
                title_analysis['title'] = title_tag.get_text().strip()
                title_analysis['length'] = len(title_analysis['title'])
                
                # تقييم طول العنوان
                if title_analysis['length'] < 30:
                    title_analysis['length_status'] = 'قصير جداً'
                    title_analysis['issues'].append('العنوان قصير جداً - يجب أن يكون 30-60 حرف')
                elif title_analysis['length'] > 60:
                    title_analysis['length_status'] = 'طويل جداً'
                    title_analysis['issues'].append('العنوان طويل جداً - قد يتم قطعه في نتائج البحث')
                else:
                    title_analysis['length_status'] = 'مناسب'
                
                # فحص وجود كلمات مفتاحية (تقدير بسيط)
                domain = urlparse(url).netloc.split('.')[0]
                if domain.lower() in title_analysis['title'].lower():
                    title_analysis['keyword_presence'] = True
            else:
                title_analysis['issues'].append('لا يوجد عنوان للصفحة')
                
        except Exception as e:
            logging.error(f"خطأ في تحليل العنوان: {e}")
            title_analysis['error'] = str(e)
        
        return title_analysis

    def _analyze_meta_tags(self, url):
        """تحليل العلامات الوصفية"""
        meta_analysis = {
            'description': '',
            'description_length': 0,
            'description_status': '',
            'keywords': '',
            'robots': '',
            'canonical': '',
            'viewport': '',
            'missing_tags': [],
            'issues': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # تحليل وصف meta
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                meta_analysis['description'] = meta_desc.get('content', '')
                meta_analysis['description_length'] = len(meta_analysis['description'])
                
                if meta_analysis['description_length'] < 120:
                    meta_analysis['description_status'] = 'قصير'
                    meta_analysis['issues'].append('الوصف قصير - يجب أن يكون 120-160 حرف')
                elif meta_analysis['description_length'] > 160:
                    meta_analysis['description_status'] = 'طويل'
                    meta_analysis['issues'].append('الوصف طويل - قد يتم قطعه')
                else:
                    meta_analysis['description_status'] = 'مناسب'
            else:
                meta_analysis['missing_tags'].append('meta description')
            
            # تحليل الكلمات المفتاحية
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                meta_analysis['keywords'] = meta_keywords.get('content', '')
            
            # تحليل robots
            meta_robots = soup.find('meta', attrs={'name': 'robots'})
            if meta_robots:
                meta_analysis['robots'] = meta_robots.get('content', '')
            else:
                meta_analysis['missing_tags'].append('meta robots')
            
            # تحليل canonical
            canonical = soup.find('link', attrs={'rel': 'canonical'})
            if canonical:
                meta_analysis['canonical'] = canonical.get('href', '')
            
            # تحليل viewport
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            if viewport:
                meta_analysis['viewport'] = viewport.get('content', '')
            else:
                meta_analysis['missing_tags'].append('meta viewport')
                
        except Exception as e:
            logging.error(f"خطأ في تحليل العلامات الوصفية: {e}")
            meta_analysis['error'] = str(e)
        
        return meta_analysis

    def _analyze_headings(self, url):
        """تحليل بنية العناوين"""
        heading_analysis = {
            'h1_count': 0,
            'h1_text': [],
            'heading_structure': {},
            'issues': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # تحليل جميع العناوين
            for i in range(1, 7):
                headings = soup.find_all(f'h{i}')
                heading_analysis['heading_structure'][f'h{i}'] = len(headings)
                
                if i == 1:
                    heading_analysis['h1_count'] = len(headings)
                    heading_analysis['h1_text'] = [h.get_text().strip() for h in headings]
            
            # فحص مشاكل العناوين
            if heading_analysis['h1_count'] == 0:
                heading_analysis['issues'].append('لا يوجد عنوان H1')
            elif heading_analysis['h1_count'] > 1:
                heading_analysis['issues'].append('يوجد أكثر من عنوان H1')
            
            # فحص التسلسل المنطقي
            prev_level = 0
            for level in range(1, 7):
                count = heading_analysis['heading_structure'][f'h{level}']
                if count > 0:
                    if prev_level > 0 and level - prev_level > 1:
                        heading_analysis['issues'].append(f'تخطي مستوى العنوان H{level}')
                    prev_level = level
                    
        except Exception as e:
            logging.error(f"خطأ في تحليل العناوين: {e}")
            heading_analysis['error'] = str(e)
        
        return heading_analysis

    def _analyze_content(self, url):
        """تحليل المحتوى"""
        content_analysis = {
            'word_count': 0,
            'paragraph_count': 0,
            'content_density': 0,
            'readability_score': 0,
            'duplicate_content': False,
            'content_quality': '',
            'issues': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # إزالة النصوص والعلامات غير المرغوبة
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            words = text.split()
            content_analysis['word_count'] = len(words)
            
            paragraphs = soup.find_all('p')
            content_analysis['paragraph_count'] = len(paragraphs)
            
            # تقييم كثافة المحتوى
            if content_analysis['word_count'] < 300:
                content_analysis['content_quality'] = 'قليل'
                content_analysis['issues'].append('المحتوى قليل جداً - يجب أن يكون 300+ كلمة')
            elif content_analysis['word_count'] < 1000:
                content_analysis['content_quality'] = 'متوسط'
            else:
                content_analysis['content_quality'] = 'جيد'
            
            # تقدير نقاط القراءة (بسيط)
            if content_analysis['word_count'] > 0:
                avg_words_per_paragraph = content_analysis['word_count'] / max(content_analysis['paragraph_count'], 1)
                if avg_words_per_paragraph < 50:
                    content_analysis['readability_score'] = 80
                elif avg_words_per_paragraph < 100:
                    content_analysis['readability_score'] = 60
                else:
                    content_analysis['readability_score'] = 40
                    
        except Exception as e:
            logging.error(f"خطأ في تحليل المحتوى: {e}")
            content_analysis['error'] = str(e)
        
        return content_analysis

    def _analyze_links(self, url):
        """تحليل الروابط"""
        link_analysis = {
            'internal_links': 0,
            'external_links': 0,
            'broken_links': 0,
            'nofollow_links': 0,
            'link_text_quality': 0,
            'issues': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            base_domain = urlparse(url).netloc
            
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href')
                if not href:
                    continue
                
                # تحديد نوع الرابط
                if href.startswith('http'):
                    link_domain = urlparse(href).netloc
                    if link_domain == base_domain:
                        link_analysis['internal_links'] += 1
                    else:
                        link_analysis['external_links'] += 1
                elif href.startswith('/') or not href.startswith('#'):
                    link_analysis['internal_links'] += 1
                
                # فحص nofollow
                if 'nofollow' in link.get('rel', []):
                    link_analysis['nofollow_links'] += 1
                
                # فحص جودة نص الرابط
                link_text = link.get_text().strip()
                if link_text in ['click here', 'read more', 'اضغط هنا', 'اقرأ المزيد']:
                    link_analysis['issues'].append('استخدام نص رابط غير وصفي')
            
            # تقييم نسبة الروابط
            total_links = link_analysis['internal_links'] + link_analysis['external_links']
            if total_links > 0:
                internal_ratio = link_analysis['internal_links'] / total_links
                if internal_ratio < 0.7:
                    link_analysis['issues'].append('نسبة الروابط الداخلية منخفضة')
                    
        except Exception as e:
            logging.error(f"خطأ في تحليل الروابط: {e}")
            link_analysis['error'] = str(e)
        
        return link_analysis

    def _analyze_image_seo(self, url):
        """تحليل SEO الصور"""
        image_analysis = {
            'total_images': 0,
            'images_with_alt': 0,
            'images_without_alt': 0,
            'alt_text_quality': 0,
            'large_images': 0,
            'issues': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            images = soup.find_all('img')
            image_analysis['total_images'] = len(images)
            
            for img in images:
                alt_text = img.get('alt')
                if alt_text:
                    image_analysis['images_with_alt'] += 1
                    if len(alt_text.strip()) < 5:
                        image_analysis['issues'].append('نص بديل قصير جداً للصور')
                else:
                    image_analysis['images_without_alt'] += 1
                
                # فحص حجم الصور (تقدير)
                src = img.get('src')
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png']):
                    if not img.get('width') or not img.get('height'):
                        image_analysis['large_images'] += 1
            
            if image_analysis['images_without_alt'] > 0:
                image_analysis['issues'].append(f'{image_analysis["images_without_alt"]} صورة بدون نص بديل')
                
        except Exception as e:
            logging.error(f"خطأ في تحليل SEO الصور: {e}")
            image_analysis['error'] = str(e)
        
        return image_analysis

    def _analyze_technical_seo(self, url):
        """تحليل SEO التقني"""
        technical_analysis = {
            'page_speed': 0,
            'mobile_friendly': False,
            'https_enabled': False,
            'gzip_enabled': False,
            'sitemap_found': False,
            'robots_txt_found': False,
            'issues': []
        }
        
        try:
            # فحص HTTPS
            technical_analysis['https_enabled'] = url.startswith('https://')
            if not technical_analysis['https_enabled']:
                technical_analysis['issues'].append('الموقع لا يستخدم HTTPS')
            
            # قياس سرعة الصفحة (بسيط)
            import time
            start_time = time.time()
            response = self.session.get(url, timeout=10)
            end_time = time.time()
            
            load_time = (end_time - start_time) * 1000
            technical_analysis['page_speed'] = round(load_time, 2)
            
            if load_time > 3000:
                technical_analysis['issues'].append('سرعة الصفحة بطيئة')
            
            # فحص الضغط
            if 'gzip' in response.headers.get('Content-Encoding', ''):
                technical_analysis['gzip_enabled'] = True
            else:
                technical_analysis['issues'].append('ضغط المحتوى غير مفعل')
            
            # فحص الاستجابة للمحمول
            soup = BeautifulSoup(response.content, 'html.parser')
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            technical_analysis['mobile_friendly'] = viewport is not None
            
            if not technical_analysis['mobile_friendly']:
                technical_analysis['issues'].append('الموقع غير متوافق مع الأجهزة المحمولة')
            
            # فحص robots.txt
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            try:
                robots_response = self.session.get(robots_url, timeout=5)
                technical_analysis['robots_txt_found'] = robots_response.status_code == 200
            except:
                pass
            
            # فحص sitemap
            sitemap_urls = [
                f"{parsed_url.scheme}://{parsed_url.netloc}/sitemap.xml",
                f"{parsed_url.scheme}://{parsed_url.netloc}/sitemap_index.xml"
            ]
            
            for sitemap_url in sitemap_urls:
                try:
                    sitemap_response = self.session.get(sitemap_url, timeout=5)
                    if sitemap_response.status_code == 200:
                        technical_analysis['sitemap_found'] = True
                        break
                except:
                    continue
                    
        except Exception as e:
            logging.error(f"خطأ في تحليل SEO التقني: {e}")
            technical_analysis['error'] = str(e)
        
        return technical_analysis

    def _analyze_structured_data(self, url):
        """تحليل البيانات المنظمة"""
        structured_analysis = {
            'json_ld_found': False,
            'microdata_found': False,
            'schema_types': [],
            'open_graph_found': False,
            'twitter_cards_found': False,
            'issues': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # فحص JSON-LD
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            if json_ld_scripts:
                structured_analysis['json_ld_found'] = True
                for script in json_ld_scripts:
                    try:
                        import json
                        data = json.loads(script.string)
                        if '@type' in data:
                            structured_analysis['schema_types'].append(data['@type'])
                    except:
                        pass
            
            # فحص Microdata
            microdata_items = soup.find_all(attrs={'itemtype': True})
            if microdata_items:
                structured_analysis['microdata_found'] = True
            
            # فحص Open Graph
            og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
            structured_analysis['open_graph_found'] = len(og_tags) > 0
            
            # فحص Twitter Cards
            twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
            structured_analysis['twitter_cards_found'] = len(twitter_tags) > 0
            
            # توليد التوصيات
            if not structured_analysis['json_ld_found'] and not structured_analysis['microdata_found']:
                structured_analysis['issues'].append('لا توجد بيانات منظمة (Schema.org)')
            
            if not structured_analysis['open_graph_found']:
                structured_analysis['issues'].append('لا توجد علامات Open Graph')
                
        except Exception as e:
            logging.error(f"خطأ في تحليل البيانات المنظمة: {e}")
            structured_analysis['error'] = str(e)
        
        return structured_analysis

    def _analyze_social_tags(self, url):
        """تحليل علامات وسائل التواصل الاجتماعي"""
        social_analysis = {
            'og_title': '',
            'og_description': '',
            'og_image': '',
            'twitter_title': '',
            'twitter_description': '',
            'twitter_image': '',
            'social_score': 0,
            'issues': []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Open Graph tags
            og_title = soup.find('meta', property='og:title')
            if og_title:
                social_analysis['og_title'] = og_title.get('content', '')
                social_analysis['social_score'] += 25
            
            og_desc = soup.find('meta', property='og:description')
            if og_desc:
                social_analysis['og_description'] = og_desc.get('content', '')
                social_analysis['social_score'] += 25
            
            og_image = soup.find('meta', property='og:image')
            if og_image:
                social_analysis['og_image'] = og_image.get('content', '')
                social_analysis['social_score'] += 25
            
            # Twitter Cards
            twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
            if twitter_title:
                social_analysis['twitter_title'] = twitter_title.get('content', '')
                social_analysis['social_score'] += 25
            
            # توليد التوصيات
            if social_analysis['social_score'] < 50:
                social_analysis['issues'].append('علامات وسائل التواصل الاجتماعي ناقصة')
                
        except Exception as e:
            logging.error(f"خطأ في تحليل علامات التواصل الاجتماعي: {e}")
            social_analysis['error'] = str(e)
        
        return social_analysis

    def _calculate_seo_score(self, seo_report):
        """حساب النقاط الإجمالية للـ SEO"""
        total_score = 0
        
        # نقاط العنوان
        title = seo_report['title_analysis']
        if title.get('title') and title.get('length_status') == 'مناسب':
            total_score += 15
        
        # نقاط الوصف
        meta = seo_report['meta_analysis']
        if meta.get('description') and meta.get('description_status') == 'مناسب':
            total_score += 15
        
        # نقاط العناوين
        headings = seo_report['heading_structure']
        if headings.get('h1_count') == 1:
            total_score += 10
        
        # نقاط المحتوى
        content = seo_report['content_analysis']
        if content.get('word_count', 0) >= 300:
            total_score += 10
        
        # نقاط الروابط
        links = seo_report['link_analysis']
        if links.get('internal_links', 0) > 0:
            total_score += 5
        
        # نقاط الصور
        images = seo_report['image_seo']
        if images.get('total_images', 0) > 0:
            alt_ratio = images.get('images_with_alt', 0) / images.get('total_images', 1)
            total_score += alt_ratio * 10
        
        # نقاط SEO التقني
        technical = seo_report['technical_seo']
        if technical.get('https_enabled'):
            total_score += 10
        if technical.get('mobile_friendly'):
            total_score += 10
        if technical.get('page_speed', 0) < 3000:
            total_score += 5
        
        # نقاط البيانات المنظمة
        structured = seo_report['structured_data']
        if structured.get('json_ld_found') or structured.get('microdata_found'):
            total_score += 5
        
        # نقاط وسائل التواصل
        social_score = seo_report['social_media'].get('social_score', 0)
        total_score += social_score * 0.1
        
        return min(100, round(total_score, 1))

    def _generate_seo_recommendations(self, seo_report):
        """توليد توصيات تحسين SEO"""
        recommendations = []
        
        # جمع جميع المشاكل من التحليلات المختلفة
        for analysis_key, analysis_data in seo_report.items():
            if isinstance(analysis_data, dict) and 'issues' in analysis_data:
                recommendations.extend(analysis_data['issues'])
        
        # إضافة توصيات عامة
        if seo_report['seo_score'] < 70:
            recommendations.append('تحسين شامل لعوامل SEO مطلوب')
        
        if not seo_report['structured_data'].get('json_ld_found'):
            recommendations.append('إضافة بيانات منظمة (Schema.org)')
        
        if seo_report['social_media'].get('social_score', 0) < 75:
            recommendations.append('تحسين علامات وسائل التواصل الاجتماعي')
        
        return recommendations[:15]  # أهم 15 توصية

    def generate_seo_audit(self, analysis_results):
        """توليد تدقيق SEO مفصل"""
        audit = {
            'executive_summary': self._create_seo_summary(analysis_results),
            'detailed_analysis': analysis_results,
            'competitor_insights': self._generate_competitor_insights(),
            'keyword_opportunities': self._identify_keyword_opportunities(analysis_results),
            'action_plan': self._create_seo_action_plan(analysis_results)
        }
        return audit

    def _create_seo_summary(self, analysis):
        """إنشاء ملخص SEO"""
        score = analysis.get('seo_score', 0)
        
        summary = {
            'overall_seo_health': f'النقاط: {score}/100',
            'seo_grade': self._get_seo_grade(score),
            'critical_issues': len([r for r in analysis.get('recommendations', []) if 'ناقص' in r or 'لا يوجد' in r]),
            'optimization_potential': f'{100 - score}% إمكانية تحسين'
        }
        return summary

    def _get_seo_grade(self, score):
        """تحديد درجة SEO"""
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

    def _generate_competitor_insights(self):
        """توليد رؤى المنافسين"""
        return {
            'analysis_note': 'تحليل المنافسين يتطلب URLs إضافية',
            'suggested_tools': ['SEMrush', 'Ahrefs', 'Moz', 'SimilarWeb'],
            'key_metrics': ['Organic Keywords', 'Backlinks', 'Domain Authority', 'Content Gap']
        }

    def _identify_keyword_opportunities(self, analysis):
        """تحديد فرص الكلمات المفتاحية"""
        return {
            'title_keywords': self._extract_keywords(analysis.get('title_analysis', {}).get('title', '')),
            'content_keywords': 'تحليل المحتوى يتطلب أدوات متخصصة',
            'missing_keywords': 'يتطلب بحث تنافسي',
            'long_tail_opportunities': 'استهداف عبارات طويلة مناسبة للمحتوى'
        }

    def _extract_keywords(self, text):
        """استخراج الكلمات المفتاحية من النص"""
        if not text:
            return []
        
        # إزالة كلمات الربط والضمائر
        stop_words = ['في', 'من', 'إلى', 'على', 'عن', 'مع', 'هذا', 'هذه', 'التي', 'الذي']
        words = text.lower().split()
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        return keywords[:5]  # أهم 5 كلمات

    def _create_seo_action_plan(self, analysis):
        """إنشاء خطة عمل SEO"""
        return {
            'immediate_actions': analysis.get('recommendations', [])[:3],
            'short_term_goals': analysis.get('recommendations', [])[3:8],
            'long_term_strategy': analysis.get('recommendations', [])[8:],
            'monitoring_schedule': {
                'weekly': ['Rankings Check', 'Organic Traffic'],
                'monthly': ['Technical SEO Audit', 'Content Performance'],
                'quarterly': ['Competitor Analysis', 'Strategy Review']
            }
        }