"""
مُستخرج المحتوى المتقدم
Advanced Content Extractor
"""

import re
import json
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Any, Optional, Set, Tuple
from bs4 import BeautifulSoup, Tag, NavigableString
from .config import ExtractionConfig
from .session_manager import SessionManager


class ContentExtractor:
    """مُستخرج محتوى متطور وآمن"""
    
    def __init__(self, config: ExtractionConfig, session_manager: SessionManager):
        self.config = config
        self.session = session_manager
        
    def extract_basic_info(self, soup: BeautifulSoup, url: str, response) -> Dict[str, Any]:
        """استخراج المعلومات الأساسية من الصفحة"""
        domain = urlparse(url).netloc
        
        # العنوان
        title = self._extract_title(soup)
        
        # الوصف والكلمات المفتاحية
        description = self._extract_meta_content(soup, 'description')
        keywords = self._extract_meta_content(soup, 'keywords')
        
        # عد العناصر
        counts = self._count_elements(soup)
        
        # معلومات الاستجابة
        response_info = self._extract_response_info(response)
        
        # اكتشاف التقنيات
        technologies = self._detect_technologies(soup, response.text)
        
        return {
            'domain': domain,
            'title': title,
            'description': description,
            'keywords': keywords,
            'url': url,
            'content_length': len(response.text),
            **counts,
            **response_info,
            'technologies': technologies
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """استخراج عنوان الصفحة"""
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        
        # البحث عن عناوين بديلة
        h1_tag = soup.find('h1')
        if h1_tag:
            text = h1_tag.get_text(strip=True)
            if text:
                return text
        
        return 'بدون عنوان'
    
    def _extract_meta_content(self, soup: BeautifulSoup, meta_name: str) -> str:
        """استخراج محتوى meta tag محدد"""
        meta_tag = soup.find('meta', attrs={'name': meta_name})
        if meta_tag and isinstance(meta_tag, Tag):
            content = meta_tag.get('content')
            return str(content) if content else ''
        
        # البحث في property أيضاً
        meta_tag = soup.find('meta', attrs={'property': meta_name})
        if meta_tag and isinstance(meta_tag, Tag):
            content = meta_tag.get('content')
            return str(content) if content else ''
        
        return ''
    
    def _count_elements(self, soup: BeautifulSoup) -> Dict[str, int]:
        """عد العناصر المختلفة في الصفحة"""
        return {
            'links_count': len(soup.find_all('a', href=True)),
            'images_count': len(soup.find_all('img', src=True)),
            'scripts_count': len(soup.find_all('script')),
            'stylesheets_count': len(soup.find_all('link', rel='stylesheet')),
            'forms_count': len(soup.find_all('form')),
            'tables_count': len(soup.find_all('table')),
            'headings_count': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            'paragraphs_count': len(soup.find_all('p'))
        }
    
    def _extract_response_info(self, response) -> Dict[str, Any]:
        """استخراج معلومات الاستجابة"""
        return {
            'status_code': response.status_code,
            'content_type': response.headers.get('Content-Type', ''),
            'server': response.headers.get('Server', ''),
            'response_time': response.elapsed.total_seconds(),
            'encoding': response.encoding or 'utf-8'
        }
    
    def _detect_technologies(self, soup: BeautifulSoup, content: str) -> List[str]:
        """اكتشاف التقنيات المستخدمة في الموقع"""
        technologies = []
        content_lower = content.lower()
        
        # إطارات العمل JavaScript
        js_frameworks = {
            'react': ['react', 'jsx', '_react', 'reactdom'],
            'vue.js': ['vue', 'vuejs', '__vue__'],
            'angular': ['angular', 'ng-', 'angularjs'],
            'jquery': ['jquery', '$.', 'jquery.min'],
            'bootstrap': ['bootstrap', 'bs-', 'btn btn-'],
            'lodash': ['lodash', 'underscore'],
            'moment.js': ['moment', 'moment.js'],
            'axios': ['axios'],
            'd3.js': ['d3.', 'd3.min']
        }
        
        for tech, indicators in js_frameworks.items():
            if any(indicator in content_lower for indicator in indicators):
                technologies.append(tech.title())
        
        # إطارات CSS
        css_frameworks = {
            'tailwind css': ['tailwind', 'tw-'],
            'bulma': ['bulma', 'is-primary'],
            'foundation': ['foundation', 'grid-container'],
            'materialize': ['materialize', 'waves-effect']
        }
        
        for tech, indicators in css_frameworks.items():
            if any(indicator in content_lower for indicator in indicators):
                technologies.append(tech.title())
        
        # أنظمة إدارة المحتوى
        cms_indicators = {
            'wordpress': ['wp-content', 'wp-includes', 'wordpress'],
            'drupal': ['drupal', 'sites/all/'],
            'joomla': ['joomla', 'com_content'],
            'magento': ['magento', 'mage/'],
            'shopify': ['shopify', 'cdn.shopify']
        }
        
        for tech, indicators in cms_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                technologies.append(tech.title())
        
        # أدوات التحليل
        analytics_tools = {
            'google analytics': ['google-analytics', 'gtag', 'ga.js'],
            'facebook pixel': ['facebook.com/tr', 'fbq'],
            'hotjar': ['hotjar'],
            'mixpanel': ['mixpanel'],
            'segment': ['segment.com', 'analytics.js']
        }
        
        for tech, indicators in analytics_tools.items():
            if any(indicator in content_lower for indicator in indicators):
                technologies.append(tech.title())
        
        return list(set(technologies))  # إزالة التكرارات
    
    def extract_links_analysis(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """تحليل شامل للروابط"""
        links = soup.find_all('a', href=True)
        
        internal_links = []
        external_links = []
        email_links = []
        phone_links = []
        document_links = []
        
        base_domain = urlparse(base_url).netloc
        
        for link in links:
            if not isinstance(link, Tag):
                continue
                
            href = link.get('href')
            text = link.get_text(strip=True)
            title = link.get('title', '')
            
            if not href or not isinstance(href, str):
                continue
            
            link_info = {
                'href': href,
                'text': text[:100],  # أول 100 حرف
                'title': title
            }
            
            # تصنيف الروابط
            if href.startswith('mailto:'):
                email_links.append({**link_info, 'email': href[7:]})
            elif href.startswith('tel:'):
                phone_links.append({**link_info, 'phone': href[4:]})
            elif any(href.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']):
                document_links.append({**link_info, 'type': self._get_document_type(href)})
            elif href.startswith(('http://', 'https://')):
                link_domain = urlparse(href).netloc
                if link_domain == base_domain:
                    internal_links.append(link_info)
                else:
                    external_links.append(link_info)
            else:
                # روابط نسبية - تحويلها إلى مطلقة
                full_url = urljoin(base_url, href)
                internal_links.append({**link_info, 'href': full_url})
        
        return {
            'total_links': len(links),
            'internal_links': internal_links[:50],  # أول 50 رابط
            'external_links': external_links[:50],
            'email_links': email_links,
            'phone_links': phone_links,
            'document_links': document_links,
            'counts': {
                'internal': len(internal_links),
                'external': len(external_links),
                'email': len(email_links),
                'phone': len(phone_links),
                'documents': len(document_links)
            }
        }
    
    def _get_document_type(self, href: str) -> str:
        """تحديد نوع المستند"""
        ext = href.lower().split('.')[-1]
        doc_types = {
            'pdf': 'PDF Document',
            'doc': 'Word Document',
            'docx': 'Word Document',
            'xls': 'Excel Spreadsheet',
            'xlsx': 'Excel Spreadsheet',
            'ppt': 'PowerPoint Presentation',
            'pptx': 'PowerPoint Presentation'
        }
        return doc_types.get(ext, 'Unknown Document')
    
    def extract_images_analysis(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """تحليل شامل للصور"""
        images = soup.find_all('img')
        
        image_analysis = []
        formats = {}
        total_estimated_size = 0
        
        for img in images[:30]:  # أول 30 صورة
            if not isinstance(img, Tag):
                continue
                
            src = img.get('src')
            if not src:
                continue
            
            # تحويل الروابط النسبية إلى مطلقة
            if not src.startswith(('http://', 'https://', 'data:')):
                src = urljoin(base_url, src)
            
            # تجاهل الصور data:
            if src.startswith('data:'):
                continue
            
            alt = img.get('alt', '')
            width = img.get('width', '')
            height = img.get('height', '')
            img_class = img.get('class', [])
            loading = img.get('loading', '')
            
            # تحديد تنسيق الصورة
            image_format = self._get_image_format(src)
            formats[image_format] = formats.get(image_format, 0) + 1
            
            # تقدير حجم الصورة
            estimated_size = self._estimate_image_size(width, height, image_format)
            total_estimated_size += estimated_size
            
            image_info = {
                'src': src,
                'alt': alt,
                'width': str(width) if width else '',
                'height': str(height) if height else '',
                'class': img_class if isinstance(img_class, list) else [img_class] if img_class else [],
                'loading': loading,
                'format': image_format,
                'estimated_size_kb': estimated_size
            }
            
            image_analysis.append(image_info)
        
        return {
            'total_images': len(images),
            'analyzed_images': len(image_analysis),
            'images': image_analysis,
            'formats_distribution': formats,
            'lazy_loading_count': len(soup.find_all('img', loading='lazy')),
            'total_estimated_size_mb': round(total_estimated_size / 1024, 2),
            'optimization_suggestions': self._get_image_optimization_suggestions(formats, total_estimated_size)
        }
    
    def _get_image_format(self, src: str) -> str:
        """تحديد تنسيق الصورة من الرابط"""
        if '.' in src:
            ext = src.split('.')[-1].split('?')[0].lower()
            common_formats = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'tiff']
            return ext if ext in common_formats else 'unknown'
        return 'unknown'
    
    def _estimate_image_size(self, width: str, height: str, image_format: str) -> int:
        """تقدير حجم الصورة بالكيلوبايت"""
        try:
            w = int(width) if width else 300
            h = int(height) if height else 200
            
            # معاملات تقدير تقريبية
            format_factors = {
                'jpg': 0.1, 'jpeg': 0.1,
                'png': 0.3,
                'gif': 0.15,
                'webp': 0.08,
                'svg': 0.02,
                'bmp': 3.0
            }
            
            factor = format_factors.get(image_format, 0.2)
            estimated_kb = (w * h * factor) / 1024
            
            return max(1, int(estimated_kb))  # على الأقل 1KB
        except:
            return 50  # تقدير افتراضي
    
    def _get_image_optimization_suggestions(self, formats: Dict[str, int], total_size_mb: float) -> List[str]:
        """اقتراحات تحسين الصور"""
        suggestions = []
        
        if total_size_mb > 5:
            suggestions.append("حجم الصور كبير - يُنصح بضغط الصور")
        
        if 'bmp' in formats:
            suggestions.append("تحويل صور BMP إلى تنسيقات أحدث مثل WEBP أو JPEG")
        
        if formats.get('jpg', 0) + formats.get('jpeg', 0) > formats.get('webp', 0) * 2:
            suggestions.append("استخدام تنسيق WEBP لتحسين الأداء")
        
        if not any(fmt in formats for fmt in ['webp', 'svg']):
            suggestions.append("استخدام تنسيقات حديثة مثل WEBP أو SVG")
        
        return suggestions
    
    def extract_seo_analysis(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل شامل لـ SEO"""
        # Meta tags
        meta_tags = {}
        for meta in soup.find_all('meta'):
            if isinstance(meta, Tag):
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    meta_tags[str(name)] = str(content)
        
        # هيكل العناوين
        headings = {}
        for i in range(1, 7):
            headings[f'h{i}'] = len(soup.find_all(f'h{i}'))
        
        # Schema markup
        schema_data = []
        schema_scripts = soup.find_all('script', type='application/ld+json')
        for script in schema_scripts:
            if script.string:
                try:
                    schema_data.append(json.loads(script.string))
                except json.JSONDecodeError:
                    pass
        
        # تحليل SEO الأساسي
        seo_score = self._calculate_seo_score(soup, meta_tags, headings)
        
        return {
            'meta_tags': meta_tags,
            'headings_structure': headings,
            'schema_markup': schema_data,
            'canonical_url': self._get_canonical_url(soup),
            'robots_meta': meta_tags.get('robots', ''),
            'seo_score': seo_score,
            'seo_recommendations': self._get_seo_recommendations(soup, meta_tags, headings)
        }
    
    def _get_canonical_url(self, soup: BeautifulSoup) -> str:
        """استخراج الرابط الكنوني"""
        canonical_tag = soup.find('link', rel='canonical')
        if canonical_tag and isinstance(canonical_tag, Tag):
            href = canonical_tag.get('href')
            return str(href) if href else ''
        return ''
    
    def _calculate_seo_score(self, soup: BeautifulSoup, meta_tags: Dict, headings: Dict) -> Dict[str, Any]:
        """حساب نقاط SEO"""
        score = 0
        max_score = 100
        issues = []
        
        # فحص العنوان
        title = soup.find('title')
        if title and title.string:
            title_length = len(title.string.strip())
            if 30 <= title_length <= 60:
                score += 15
            elif title_length > 0:
                score += 10
                issues.append("طول العنوان غير مناسب (يُفضل 30-60 حرف)")
        else:
            issues.append("العنوان مفقود")
        
        # فحص الوصف
        if 'description' in meta_tags:
            desc_length = len(meta_tags['description'])
            if 120 <= desc_length <= 160:
                score += 15
            elif desc_length > 0:
                score += 10
                issues.append("طول الوصف غير مناسب (يُفضل 120-160 حرف)")
        else:
            issues.append("وصف الصفحة مفقود")
        
        # فحص H1
        if headings.get('h1', 0) == 1:
            score += 10
        elif headings.get('h1', 0) > 1:
            score += 5
            issues.append("يوجد أكثر من H1 واحد")
        else:
            issues.append("عنوان H1 مفقود")
        
        # فحص هيكل العناوين
        if headings.get('h2', 0) > 0:
            score += 10
        
        # فحص Alt tags للصور
        images_with_alt = len(soup.find_all('img', alt=True))
        total_images = len(soup.find_all('img'))
        if total_images > 0:
            alt_ratio = images_with_alt / total_images
            score += int(alt_ratio * 15)
            if alt_ratio < 0.8:
                issues.append("بعض الصور تفتقر لنص Alt")
        
        # فحص الروابط الداخلية
        internal_links = len(soup.find_all('a', href=True))
        if internal_links > 0:
            score += 10
        
        # فحص Schema markup
        if soup.find_all('script', type='application/ld+json'):
            score += 15
        else:
            issues.append("Schema markup مفقود")
        
        # فحص Canonical URL
        if soup.find('link', rel='canonical'):
            score += 10
        else:
            issues.append("Canonical URL مفقود")
        
        return {
            'score': min(score, max_score),
            'max_score': max_score,
            'percentage': min(int((score / max_score) * 100), 100),
            'issues': issues
        }
    
    def _get_seo_recommendations(self, soup: BeautifulSoup, meta_tags: Dict, headings: Dict) -> List[str]:
        """توصيات تحسين SEO"""
        recommendations = []
        
        title = soup.find('title')
        if not title or not title.string:
            recommendations.append("إضافة عنوان للصفحة")
        elif len(title.string.strip()) > 60:
            recommendations.append("تقصير عنوان الصفحة (أقل من 60 حرف)")
        
        if 'description' not in meta_tags:
            recommendations.append("إضافة وصف meta للصفحة")
        elif len(meta_tags['description']) > 160:
            recommendations.append("تقصير وصف الصفحة (أقل من 160 حرف)")
        
        if headings.get('h1', 0) == 0:
            recommendations.append("إضافة عنوان H1 للصفحة")
        elif headings.get('h1', 0) > 1:
            recommendations.append("استخدام H1 واحد فقط في الصفحة")
        
        images_without_alt = len(soup.find_all('img')) - len(soup.find_all('img', alt=True))
        if images_without_alt > 0:
            recommendations.append(f"إضافة نص Alt لـ {images_without_alt} صورة")
        
        if not soup.find_all('script', type='application/ld+json'):
            recommendations.append("إضافة Schema markup للصفحة")
        
        if not soup.find('link', rel='canonical'):
            recommendations.append("إضافة Canonical URL للصفحة")
        
        return recommendations