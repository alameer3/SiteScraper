"""
محلل المنافسين المتقدم - Advanced Competitor Analyzer
يقوم بتحليل ومقارنة المواقع المنافسة
"""

import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import logging

class CompetitorAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def analyze_competitors(self, main_url, competitor_urls):
        """تحليل مقارن للمنافسين"""
        try:
            analysis = {
                'main_site': self._analyze_single_site(main_url),
                'competitors': {},
                'comparison': {},
                'recommendations': []
            }
            
            # تحليل المواقع المنافسة
            for url in competitor_urls:
                analysis['competitors'][url] = self._analyze_single_site(url)
            
            # إجراء المقارنة
            analysis['comparison'] = self._compare_sites(analysis)
            analysis['recommendations'] = self._generate_competitive_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            logging.error(f"خطأ في تحليل المنافسين: {e}")
            return {'error': str(e)}

    def _analyze_single_site(self, url):
        """تحليل موقع واحد"""
        site_analysis = {
            'url': url,
            'basic_info': {},
            'technology_stack': {},
            'content_metrics': {},
            'seo_factors': {},
            'performance_indicators': {},
            'social_presence': {}
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # معلومات أساسية
            site_analysis['basic_info'] = {
                'title': soup.find('title').get_text() if soup.find('title') else '',
                'description': self._get_meta_content(soup, 'description'),
                'language': soup.find('html').get('lang', 'unknown') if soup.find('html') else 'unknown',
                'status_code': response.status_code,
                'page_size': len(response.content)
            }
            
            # تحليل التقنيات
            site_analysis['technology_stack'] = self._detect_technologies(soup, response)
            
            # مقاييس المحتوى
            site_analysis['content_metrics'] = self._analyze_content_metrics(soup)
            
            # عوامل SEO
            site_analysis['seo_factors'] = self._analyze_seo_factors(soup)
            
            # مؤشرات الأداء
            site_analysis['performance_indicators'] = self._measure_performance(response)
            
            # الحضور الاجتماعي
            site_analysis['social_presence'] = self._analyze_social_presence(soup)
            
        except Exception as e:
            logging.error(f"خطأ في تحليل الموقع {url}: {e}")
            site_analysis['error'] = str(e)
        
        return site_analysis

    def _get_meta_content(self, soup, name):
        """استخراج محتوى meta tag"""
        meta = soup.find('meta', attrs={'name': name})
        return meta.get('content', '') if meta else ''

    def _detect_technologies(self, soup, response):
        """كشف التقنيات المستخدمة"""
        technologies = {
            'cms': 'unknown',
            'frameworks': [],
            'analytics': [],
            'fonts': [],
            'cdn': []
        }
        
        content = str(soup).lower()
        headers = str(response.headers).lower()
        
        # كشف CMS
        cms_patterns = {
            'wordpress': ['wp-content', 'wp-includes'],
            'drupal': ['drupal', 'sites/default'],
            'joomla': ['joomla', 'com_content'],
            'magento': ['magento', 'mage/js'],
            'shopify': ['shopify', 'cdn.shopify']
        }
        
        for cms, patterns in cms_patterns.items():
            if any(pattern in content for pattern in patterns):
                technologies['cms'] = cms
                break
        
        # كشف Frameworks
        framework_patterns = {
            'react': ['react', '_react'],
            'vue': ['vue.js', '__vue__'],
            'angular': ['angular', 'ng-'],
            'bootstrap': ['bootstrap', 'btn-'],
            'jquery': ['jquery', '$']
        }
        
        for framework, patterns in framework_patterns.items():
            if any(pattern in content for pattern in patterns):
                technologies['frameworks'].append(framework)
        
        # كشف Analytics
        analytics_patterns = {
            'google_analytics': ['google-analytics', 'gtag'],
            'facebook_pixel': ['facebook.net', 'fbq'],
            'hotjar': ['hotjar'],
            'mixpanel': ['mixpanel']
        }
        
        for tool, patterns in analytics_patterns.items():
            if any(pattern in content for pattern in patterns):
                technologies['analytics'].append(tool)
        
        return technologies

    def _analyze_content_metrics(self, soup):
        """تحليل مقاييس المحتوى"""
        # إزالة النصوص والعناصر غير المرغوبة
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        text = soup.get_text()
        words = text.split()
        
        return {
            'word_count': len(words),
            'paragraph_count': len(soup.find_all('p')),
            'heading_count': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            'image_count': len(soup.find_all('img')),
            'link_count': len(soup.find_all('a')),
            'list_count': len(soup.find_all(['ul', 'ol'])),
            'table_count': len(soup.find_all('table'))
        }

    def _analyze_seo_factors(self, soup):
        """تحليل عوامل SEO"""
        seo_factors = {
            'meta_title_length': 0,
            'meta_description_length': 0,
            'h1_count': len(soup.find_all('h1')),
            'images_with_alt': 0,
            'internal_links': 0,
            'external_links': 0,
            'has_sitemap': False,
            'has_robots': False
        }
        
        # تحليل العنوان
        title = soup.find('title')
        if title:
            seo_factors['meta_title_length'] = len(title.get_text())
        
        # تحليل الوصف
        description = soup.find('meta', attrs={'name': 'description'})
        if description:
            seo_factors['meta_description_length'] = len(description.get('content', ''))
        
        # تحليل الصور
        images = soup.find_all('img')
        seo_factors['images_with_alt'] = len([img for img in images if img.get('alt')])
        
        # تحليل الروابط
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            if href.startswith('http'):
                seo_factors['external_links'] += 1
            elif href.startswith('/') or not href.startswith('#'):
                seo_factors['internal_links'] += 1
        
        return seo_factors

    def _measure_performance(self, response):
        """قياس مؤشرات الأداء"""
        return {
            'response_time': response.elapsed.total_seconds() * 1000,
            'content_size': len(response.content),
            'status_code': response.status_code,
            'has_gzip': 'gzip' in response.headers.get('Content-Encoding', ''),
            'has_cache_control': 'Cache-Control' in response.headers,
            'server': response.headers.get('Server', 'unknown')
        }

    def _analyze_social_presence(self, soup):
        """تحليل الحضور الاجتماعي"""
        social_presence = {
            'og_tags': 0,
            'twitter_cards': 0,
            'social_links': [],
            'social_widgets': 0
        }
        
        # عد Open Graph tags
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        social_presence['og_tags'] = len(og_tags)
        
        # عد Twitter Cards
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        social_presence['twitter_cards'] = len(twitter_tags)
        
        # البحث عن روابط وسائل التواصل
        social_domains = ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'youtube.com']
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            for domain in social_domains:
                if domain in href:
                    social_presence['social_links'].append(domain)
        
        social_presence['social_links'] = list(set(social_presence['social_links']))
        
        return social_presence

    def _compare_sites(self, analysis):
        """مقارنة المواقع"""
        main_site = analysis['main_site']
        competitors = analysis['competitors']
        
        comparison = {
            'performance_comparison': {},
            'content_comparison': {},
            'seo_comparison': {},
            'technology_comparison': {},
            'strengths_weaknesses': {}
        }
        
        # مقارنة الأداء
        main_perf = main_site.get('performance_indicators', {})
        comparison['performance_comparison'] = {
            'main_site_speed': main_perf.get('response_time', 0),
            'competitors_speed': {},
            'speed_ranking': []
        }
        
        speed_data = [('main_site', main_perf.get('response_time', 0))]
        for url, comp_data in competitors.items():
            comp_speed = comp_data.get('performance_indicators', {}).get('response_time', 0)
            comparison['performance_comparison']['competitors_speed'][url] = comp_speed
            speed_data.append((url, comp_speed))
        
        # ترتيب المواقع حسب السرعة
        speed_data.sort(key=lambda x: x[1])
        comparison['performance_comparison']['speed_ranking'] = speed_data
        
        # مقارنة المحتوى
        main_content = main_site.get('content_metrics', {})
        comparison['content_comparison'] = {
            'word_count_comparison': {},
            'content_richness': {}
        }
        
        comparison['content_comparison']['word_count_comparison']['main_site'] = main_content.get('word_count', 0)
        for url, comp_data in competitors.items():
            comp_words = comp_data.get('content_metrics', {}).get('word_count', 0)
            comparison['content_comparison']['word_count_comparison'][url] = comp_words
        
        # مقارنة SEO
        main_seo = main_site.get('seo_factors', {})
        comparison['seo_comparison'] = {
            'title_length_comparison': {},
            'h1_usage': {},
            'internal_links': {}
        }
        
        comparison['seo_comparison']['title_length_comparison']['main_site'] = main_seo.get('meta_title_length', 0)
        comparison['seo_comparison']['h1_usage']['main_site'] = main_seo.get('h1_count', 0)
        comparison['seo_comparison']['internal_links']['main_site'] = main_seo.get('internal_links', 0)
        
        for url, comp_data in competitors.items():
            comp_seo = comp_data.get('seo_factors', {})
            comparison['seo_comparison']['title_length_comparison'][url] = comp_seo.get('meta_title_length', 0)
            comparison['seo_comparison']['h1_usage'][url] = comp_seo.get('h1_count', 0)
            comparison['seo_comparison']['internal_links'][url] = comp_seo.get('internal_links', 0)
        
        # تحليل نقاط القوة والضعف
        comparison['strengths_weaknesses'] = self._analyze_strengths_weaknesses(analysis)
        
        return comparison

    def _analyze_strengths_weaknesses(self, analysis):
        """تحليل نقاط القوة والضعف"""
        main_site = analysis['main_site']
        competitors = analysis['competitors']
        
        strengths = []
        weaknesses = []
        opportunities = []
        
        # تحليل الأداء
        main_speed = main_site.get('performance_indicators', {}).get('response_time', float('inf'))
        competitor_speeds = [
            comp.get('performance_indicators', {}).get('response_time', float('inf'))
            for comp in competitors.values()
        ]
        
        if competitor_speeds and main_speed < min(competitor_speeds):
            strengths.append('أسرع من جميع المنافسين')
        elif competitor_speeds and main_speed > max(competitor_speeds):
            weaknesses.append('أبطأ من جميع المنافسين')
        
        # تحليل المحتوى
        main_words = main_site.get('content_metrics', {}).get('word_count', 0)
        competitor_words = [
            comp.get('content_metrics', {}).get('word_count', 0)
            for comp in competitors.values()
        ]
        
        if competitor_words and main_words > max(competitor_words):
            strengths.append('محتوى أكثر ثراءً من المنافسين')
        elif competitor_words and main_words < min(competitor_words):
            opportunities.append('زيادة كمية المحتوى')
        
        # تحليل SEO
        main_h1 = main_site.get('seo_factors', {}).get('h1_count', 0)
        if main_h1 == 1:
            strengths.append('استخدام صحيح لعنوان H1')
        elif main_h1 == 0:
            weaknesses.append('لا يوجد عنوان H1')
        elif main_h1 > 1:
            weaknesses.append('أكثر من عنوان H1')
        
        # تحليل التقنيات
        main_tech = main_site.get('technology_stack', {})
        if main_tech.get('analytics'):
            strengths.append('يستخدم أدوات التحليل')
        else:
            opportunities.append('إضافة أدوات التحليل')
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'opportunities': opportunities,
            'threats': ['المنافسة القوية في السوق']
        }

    def _generate_competitive_recommendations(self, analysis):
        """توليد توصيات تنافسية"""
        recommendations = []
        comparison = analysis.get('comparison', {})
        
        # توصيات الأداء
        speed_ranking = comparison.get('performance_comparison', {}).get('speed_ranking', [])
        if speed_ranking and speed_ranking[0][0] != 'main_site':
            recommendations.append(f"تحسين سرعة الموقع - المنافس الأسرع: {speed_ranking[0][1]:.0f}ms")
        
        # توصيات المحتوى
        word_comparison = comparison.get('content_comparison', {}).get('word_count_comparison', {})
        main_words = word_comparison.get('main_site', 0)
        competitor_words = [words for url, words in word_comparison.items() if url != 'main_site']
        
        if competitor_words and main_words < max(competitor_words):
            recommendations.append(f"زيادة المحتوى - أفضل منافس لديه {max(competitor_words)} كلمة")
        
        # توصيات SEO
        h1_comparison = comparison.get('seo_comparison', {}).get('h1_usage', {})
        main_h1 = h1_comparison.get('main_site', 0)
        if main_h1 != 1:
            recommendations.append("تحسين استخدام عناوين H1")
        
        # توصيات التقنيات
        strengths_weaknesses = comparison.get('strengths_weaknesses', {})
        opportunities = strengths_weaknesses.get('opportunities', [])
        recommendations.extend(opportunities)
        
        # توصيات عامة
        recommendations.append("تحليل منتظم للمنافسين")
        recommendations.append("مراقبة أداء المنافسين")
        
        return recommendations[:10]

    def generate_competitive_report(self, analysis):
        """توليد تقرير تنافسي شامل"""
        report = {
            'executive_summary': self._create_competitive_summary(analysis),
            'detailed_comparison': analysis['comparison'],
            'market_position': self._analyze_market_position(analysis),
            'competitive_strategy': self._suggest_competitive_strategy(analysis),
            'monitoring_plan': self._create_monitoring_plan()
        }
        return report

    def _create_competitive_summary(self, analysis):
        """إنشاء ملخص تنافسي"""
        comparison = analysis.get('comparison', {})
        speed_ranking = comparison.get('performance_comparison', {}).get('speed_ranking', [])
        
        main_position = next((i for i, (site, _) in enumerate(speed_ranking) if site == 'main_site'), -1)
        total_sites = len(speed_ranking)
        
        summary = {
            'market_position': f"المرتبة {main_position + 1} من {total_sites} في السرعة" if main_position >= 0 else "غير محدد",
            'competitive_advantages': analysis.get('comparison', {}).get('strengths_weaknesses', {}).get('strengths', []),
            'areas_for_improvement': analysis.get('comparison', {}).get('strengths_weaknesses', {}).get('weaknesses', []),
            'immediate_opportunities': analysis.get('comparison', {}).get('strengths_weaknesses', {}).get('opportunities', [])
        }
        return summary

    def _analyze_market_position(self, analysis):
        """تحليل الموقع في السوق"""
        return {
            'competitive_landscape': 'متنوع مع منافسة قوية',
            'differentiation_opportunities': [
                'تحسين تجربة المستخدم',
                'زيادة سرعة الموقع',
                'تطوير محتوى فريد',
                'تحسين SEO'
            ],
            'market_trends': [
                'التركيز على الأداء',
                'تحسين التجربة المحمولة',
                'أهمية المحتوى المفيد',
                'التحسين المستمر'
            ]
        }

    def _suggest_competitive_strategy(self, analysis):
        """اقتراح استراتيجية تنافسية"""
        return {
            'short_term_tactics': analysis.get('recommendations', [])[:3],
            'medium_term_strategy': [
                'تطوير ميزات فريدة',
                'بناء علامة تجارية قوية',
                'تحسين تجربة العملاء'
            ],
            'long_term_vision': [
                'قيادة السوق في الابتكار',
                'بناء مجتمع مخلص',
                'التوسع في أسواق جديدة'
            ]
        }

    def _create_monitoring_plan(self):
        """إنشاء خطة المراقبة التنافسية"""
        return {
            'weekly_monitoring': [
                'مراقبة أداء المواقع',
                'تتبع التغييرات في المحتوى',
                'مراقبة حملات التسويق'
            ],
            'monthly_analysis': [
                'تحليل شامل للمنافسين',
                'مراجعة الاستراتيجية',
                'تحديث الخطط التنافسية'
            ],
            'quarterly_review': [
                'تقييم الموقع في السوق',
                'تحديد منافسين جدد',
                'مراجعة الأهداف الاستراتيجية'
            ],
            'tools_and_metrics': [
                'أدوات مراقبة المواقع',
                'تحليل حركة المرور',
                'مراقبة وسائل التواصل',
                'تتبع الكلمات المفتاحية'
            ]
        }