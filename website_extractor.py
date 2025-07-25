"""
أداة متطورة لاستخراج وتنظيف محتوى المواقع
- استخراج المحتوى النصي
- استخراج الصور والملفات
- استخراج CSS و JavaScript
- تنظيف الكود من التتبع والإعلانات
- إعادة تنظيم الهيكل ليكون جاهزاً للاستخدام
"""

import os
import re
import json
import requests
import trafilatura
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import logging
from pathlib import Path
import hashlib
import mimetypes
from typing import Dict, List, Tuple, Optional
import time
import cssutils
import base64

# تكوين المسجل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebsiteExtractor:
    """استخراج شامل لمحتوى المواقع مع التنظيف والتحسين"""
    
    def __init__(self, base_url: str, output_dir: str = "extracted_website"):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # إنشاء مجلدات الإخراج
        self.create_directories()
        
        # تفعيل نظام حجب الإعلانات المتطور
        from advanced_ad_blocker import AdvancedAdBlocker
        self.ad_blocker = AdvancedAdBlocker()
        
        # قوائم التنظيف التقليدية (احتياطية)
        self.ad_selectors = [
            '[class*="ad"]', '[id*="ad"]', '[class*="advertisement"]',
            '[class*="banner"]', '[class*="popup"]', '[class*="modal"]',
            '.google-ads', '.adsense', '[class*="promo"]',
            '[data-ad]', '[data-google-ad]', '[class*="sponsor"]'
        ]
        
        self.tracking_domains = [
            'google-analytics.com', 'googletagmanager.com', 'facebook.com',
            'doubleclick.net', 'googlesyndication.com', 'amazon-adsystem.com',
            'adsystem.amazon.com', 'googleadservices.com'
        ]
        
        # إحصائيات
        self.stats = {
            'pages_extracted': 0,
            'images_downloaded': 0,
            'css_files': 0,
            'js_files': 0,
            'ads_removed': 0,
            'tracking_removed': 0
        }

    def create_directories(self):
        """إنشاء هيكل المجلدات"""
        directories = [
            self.output_dir,
            self.output_dir / 'pages',
            self.output_dir / 'assets' / 'images',
            self.output_dir / 'assets' / 'css',
            self.output_dir / 'assets' / 'js',
            self.output_dir / 'assets' / 'fonts',
            self.output_dir / 'content',
            self.output_dir / 'data'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"تم إنشاء مجلدات الإخراج في: {self.output_dir}")

    def extract_complete_website(self, max_pages: int = 50) -> Dict:
        """استخراج شامل للموقع"""
        logger.info(f"بدء استخراج الموقع: {self.base_url}")
        
        extraction_report = {
            'url': self.base_url,
            'start_time': time.time(),
            'pages': [],
            'assets': {
                'images': [],
                'css': [],
                'js': [],
                'fonts': []
            },
            'content_summary': {},
            'cleaned_elements': {},
            'stats': {}
        }
        
        try:
            # 1. استخراج الصفحة الرئيسية
            main_page = self.extract_page(self.base_url)
            if main_page:
                extraction_report['pages'].append(main_page)
                self.stats['pages_extracted'] += 1
            
            # 2. العثور على الروابط الداخلية
            internal_links = self.find_internal_links(self.base_url)
            logger.info(f"تم العثور على {len(internal_links)} رابط داخلي")
            
            # 3. استخراج الصفحات الإضافية
            for i, link in enumerate(internal_links[:max_pages-1]):
                try:
                    logger.info(f"استخراج الصفحة {i+2}/{min(max_pages, len(internal_links)+1)}: {link}")
                    page_data = self.extract_page(link)
                    if page_data:
                        extraction_report['pages'].append(page_data)
                        self.stats['pages_extracted'] += 1
                    time.sleep(0.5)  # تأخير بسيط
                except Exception as e:
                    logger.error(f"خطأ في استخراج الصفحة {link}: {e}")
            
            # 4. إنشاء ملخص المحتوى
            extraction_report['content_summary'] = self.create_content_summary(extraction_report['pages'])
            
            # 5. إنشاء ملفات تنظيم الموقع
            self.create_site_structure(extraction_report)
            
            # 6. إنشاء تقرير التنظيف
            extraction_report['cleaned_elements'] = {
                'ads_removed': self.stats['ads_removed'],
                'tracking_removed': self.stats['tracking_removed'],
                'cleaned_selectors': self.ad_selectors
            }
            
            extraction_report['stats'] = self.stats.copy()
            extraction_report['end_time'] = time.time()
            extraction_report['duration'] = extraction_report['end_time'] - extraction_report['start_time']
            
            # حفظ التقرير
            self.save_extraction_report(extraction_report)
            
            logger.info(f"اكتمل الاستخراج! تم استخراج {self.stats['pages_extracted']} صفحة")
            return extraction_report
            
        except Exception as e:
            logger.error(f"خطأ في الاستخراج الشامل: {e}")
            return extraction_report

    def extract_page(self, url: str) -> Optional[Dict]:
        """استخراج صفحة واحدة بشكل شامل"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # تحليل HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # تنظيف الصفحة من الإعلانات والتتبع
            cleaned_soup = self.clean_page(soup)
            
            # استخراج المحتوى النصي
            text_content = self.extract_text_content(url, cleaned_soup)
            
            # استخراج البيانات المنظمة
            structured_data = self.extract_structured_data(cleaned_soup)
            
            # استخراج الأصول (CSS, JS, Images)
            assets = self.extract_assets(url, cleaned_soup, response.content)
            
            # إنشاء ملف HTML نظيف
            clean_html = self.create_clean_html(cleaned_soup, assets)
            
            page_data = {
                'url': url,
                'title': cleaned_soup.title.get_text().strip() if cleaned_soup.title else 'بدون عنوان',
                'text_content': text_content,
                'structured_data': structured_data,
                'assets': assets,
                'clean_html': clean_html,
                'meta_data': self.extract_meta_data(cleaned_soup),
                'word_count': len(text_content.split()) if text_content else 0,
                'extraction_time': time.time()
            }
            
            # حفظ الصفحة
            self.save_page(page_data)
            
            return page_data
            
        except Exception as e:
            logger.error(f"خطأ في استخراج الصفحة {url}: {e}")
            return None

    def clean_page(self, soup: BeautifulSoup) -> BeautifulSoup:
        """تنظيف متطور للصفحة من الإعلانات والتتبع باستخدام AI"""
        
        # استخدام النظام المتطور لحجب الإعلانات
        html_content = str(soup)
        cleaned_html, cleaning_report = self.ad_blocker.clean_html_content(html_content)
        
        # تحديث الإحصائيات من التقرير المتطور
        ads_blocked = len([x for x in cleaning_report.get('removed_elements', []) if 'CSS:' in x or 'Smart:' in x])
        tracking_blocked = cleaning_report.get('cleaned_scripts', 0)
        
        self.stats['ads_removed'] += ads_blocked
        self.stats['tracking_removed'] += tracking_blocked
        
        # إعادة تحويل HTML المنظف إلى BeautifulSoup
        cleaned_soup = BeautifulSoup(cleaned_html, 'html.parser')
        
        # تطبيق طبقة تنظيف إضافية تقليدية
        cleaned_soup = self._apply_traditional_cleaning(cleaned_soup)
        
        logger.info(f"🛡️ تم تنظيف {ads_blocked} إعلان متطور و {tracking_blocked} عنصر تتبع ذكي")
        
        return cleaned_soup
    
    def _apply_traditional_cleaning(self, soup: BeautifulSoup) -> BeautifulSoup:
        """تطبيق تنظيف تقليدي كطبقة إضافية"""
        
        # إزالة الإعلانات التقليدية المتبقية
        traditional_ads = 0
        for selector in self.ad_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    element.decompose()
                    traditional_ads += 1
            except Exception as e:
                logger.debug(f"تحذير في selector {selector}: {e}")
        
        # إزالة سكريپت التتبع التقليدي المتبقي
        traditional_tracking = 0
        scripts = soup.find_all('script')
        for script in scripts:
            if script.get('src'):
                src = script.get('src')
                if any(domain in src for domain in self.tracking_domains):
                    script.decompose()
                    traditional_tracking += 1
            elif script.string:
                script_content = script.string.lower()
                if any(domain in script_content for domain in self.tracking_domains):
                    script.decompose()
                    traditional_tracking += 1
        
        # تنظيف التعليقات المشبوهة
        from bs4 import Comment
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment_text = str(comment).lower()
            if any(keyword in comment_text for keyword in ['ad', 'track', 'analytics', 'google']):
                comment.extract()
        
        # إزالة العناصر المخفية المشبوهة
        hidden_elements = soup.find_all(attrs={'style': re.compile(r'display\s*:\s*none|visibility\s*:\s*hidden')})
        for element in hidden_elements:
            element_text = element.get_text(strip=True).lower()
            if any(keyword in element_text for keyword in ['ad', 'advertisement', 'sponsor', 'promo']):
                element.decompose()
        
        if traditional_ads > 0 or traditional_tracking > 0:
            logger.info(f"➕ طبقة إضافية: {traditional_ads} إعلان تقليدي و {traditional_tracking} تتبع تقليدي")
        
        return soup

    def extract_text_content(self, url: str, soup: BeautifulSoup) -> str:
        """استخراج المحتوى النصي المفيد"""
        try:
            # استخدام trafilatura لاستخراج المحتوى الرئيسي
            html_content = str(soup)
            extracted_text = trafilatura.extract(html_content, include_comments=False, include_tables=True)
            
            if extracted_text:
                return extracted_text
            
            # طريقة احتياطية
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            main_content = soup.find('main') or soup.find('article') or soup.find(class_=re.compile(r'content|main|article'))
            if main_content:
                return main_content.get_text(separator=' ', strip=True)
            
            return soup.get_text(separator=' ', strip=True)
            
        except Exception as e:
            logger.error(f"خطأ في استخراج النص من {url}: {e}")
            return ""

    def extract_structured_data(self, soup: BeautifulSoup) -> Dict:
        """استخراج البيانات المنظمة (JSON-LD, microdata, etc.)"""
        structured_data = {
            'json_ld': [],
            'meta_tags': {},
            'open_graph': {},
            'twitter_card': {},
            'schema_org': []
        }
        
        # JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                structured_data['json_ld'].append(data)
            except:
                pass
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property') or meta.get('itemprop')
            content = meta.get('content')
            if name and content:
                structured_data['meta_tags'][name] = content
                
                # Open Graph
                if name.startswith('og:'):
                    structured_data['open_graph'][name[3:]] = content
                
                # Twitter Card
                if name.startswith('twitter:'):
                    structured_data['twitter_card'][name[8:]] = content
        
        return structured_data

    def extract_assets(self, page_url: str, soup: BeautifulSoup, page_content: bytes) -> Dict:
        """استخراج وتحميل جميع الأصول"""
        assets = {
            'images': [],
            'css': [],
            'js': [],
            'fonts': []
        }
        
        # استخراج الصور
        images = soup.find_all(['img', 'picture', 'source'])
        for img in images:
            src = img.get('src') or img.get('data-src') or img.get('srcset', '').split()[0] if img.get('srcset') else None
            if src:
                full_url = urljoin(page_url, src)
                saved_path = self.download_asset(full_url, 'images')
                if saved_path:
                    assets['images'].append({
                        'original_url': full_url,
                        'local_path': saved_path,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
        
        # استخراج ملفات CSS
        css_links = soup.find_all('link', rel='stylesheet')
        for link in css_links:
            href = link.get('href')
            if href:
                full_url = urljoin(page_url, href)
                saved_path = self.download_and_clean_css(full_url)
                if saved_path:
                    assets['css'].append({
                        'original_url': full_url,
                        'local_path': saved_path
                    })
        
        # استخراج ملفات JavaScript
        js_scripts = soup.find_all('script', src=True)
        for script in js_scripts:
            src = script.get('src')
            if src and not any(domain in src for domain in self.tracking_domains):
                full_url = urljoin(page_url, src)
                saved_path = self.download_asset(full_url, 'js')
                if saved_path:
                    assets['js'].append({
                        'original_url': full_url,
                        'local_path': saved_path
                    })
        
        return assets

    def download_asset(self, url: str, asset_type: str) -> Optional[str]:
        """تحميل الأصول"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # تحديد اسم الملف
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path) or f"asset_{hashlib.md5(url.encode()).hexdigest()[:8]}"
            
            # تحديد الامتداد
            content_type = response.headers.get('content-type', '')
            if not '.' in filename:
                extension = mimetypes.guess_extension(content_type) or ''
                filename += extension
            
            # مسار الحفظ
            save_path = self.output_dir / 'assets' / asset_type / filename
            
            # حفظ الملف
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            if asset_type == 'images':
                self.stats['images_downloaded'] += 1
            elif asset_type == 'css':
                self.stats['css_files'] += 1
            elif asset_type == 'js':
                self.stats['js_files'] += 1
            
            return str(save_path.relative_to(self.output_dir))
            
        except Exception as e:
            logger.error(f"خطأ في تحميل {url}: {e}")
            return None

    def download_and_clean_css(self, url: str) -> Optional[str]:
        """تحميل وتنظيف ملفات CSS مع حماية من الأخطاء"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            css_content = response.text
            
            # تنظيف CSS من الخطوط والموارد الخارجية إذا لزم الأمر
            # يمكن إضافة المزيد من التنظيف هنا
            
            # حفظ الملف
            filename = f"style_{hashlib.md5(url.encode()).hexdigest()[:8]}.css"
            save_path = self.output_dir / 'assets' / 'css' / filename
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
            
            self.stats['css_files'] += 1
            return str(save_path.relative_to(self.output_dir))
            
        except Exception as e:
            logger.warning(f"تخطي ملف CSS {url}: {e}")
            return None

    def find_internal_links(self, url: str) -> List[str]:
        """العثور على الروابط الداخلية"""
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            internal_links = set()
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                # التحقق من أن الرابط داخلي
                if urlparse(full_url).netloc == self.domain:
                    # إزالة المعاملات والمراسي
                    clean_url = full_url.split('#')[0].split('?')[0]
                    if clean_url != url and clean_url not in internal_links:
                        internal_links.add(clean_url)
            
            return list(internal_links)
            
        except Exception as e:
            logger.error(f"خطأ في العثور على الروابط: {e}")
            return []

    def extract_meta_data(self, soup: BeautifulSoup) -> Dict:
        """استخراج البيانات الوصفية"""
        meta_data = {
            'title': soup.title.get_text().strip() if soup.title else '',
            'description': '',
            'keywords': '',
            'author': '',
            'lang': soup.get('lang', ''),
            'charset': ''
        }
        
        # Meta description
        desc_meta = soup.find('meta', attrs={'name': 'description'})
        if desc_meta:
            meta_data['description'] = desc_meta.get('content', '')
        
        # Meta keywords
        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_meta:
            meta_data['keywords'] = keywords_meta.get('content', '')
        
        # Author
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta:
            meta_data['author'] = author_meta.get('content', '')
        
        # Charset
        charset_meta = soup.find('meta', attrs={'charset': True})
        if charset_meta:
            meta_data['charset'] = charset_meta.get('charset', '')
        
        return meta_data

    def create_clean_html(self, soup: BeautifulSoup, assets: Dict) -> str:
        """إنشاء HTML نظيف مع الروابط المحلية"""
        # تحديث روابط الأصول لتشير للملفات المحلية
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                for asset in assets['images']:
                    if asset['original_url'].endswith(src) or src in asset['original_url']:
                        img['src'] = asset['local_path']
                        break
        
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                for asset in assets['css']:
                    if asset['original_url'].endswith(href) or href in asset['original_url']:
                        link['href'] = asset['local_path']
                        break
        
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                for asset in assets['js']:
                    if asset['original_url'].endswith(src) or src in asset['original_url']:
                        script['src'] = asset['local_path']
                        break
        
        return str(soup.prettify())

    def create_content_summary(self, pages: List[Dict]) -> Dict:
        """إنشاء ملخص شامل للمحتوى"""
        summary = {
            'total_pages': len(pages),
            'total_words': 0,
            'common_keywords': [],
            'content_types': {},
            'page_titles': [],
            'meta_descriptions': []
        }
        
        all_text = ""
        for page in pages:
            summary['total_words'] += page.get('word_count', 0)
            all_text += " " + (page.get('text_content', '') or '')
            
            if page.get('title'):
                summary['page_titles'].append(page['title'])
            
            if page.get('meta_data', {}).get('description'):
                summary['meta_descriptions'].append(page['meta_data']['description'])
        
        # استخراج الكلمات المفتاحية الشائعة (تحسين بسيط)
        words = re.findall(r'\b\w+\b', all_text.lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:  # تجاهل الكلمات القصيرة
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # أشهر 20 كلمة
        summary['common_keywords'] = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return summary

    def save_page(self, page_data: Dict):
        """حفظ بيانات الصفحة"""
        url_hash = hashlib.md5(page_data['url'].encode()).hexdigest()[:8]
        
        # حفظ HTML
        html_path = self.output_dir / 'pages' / f"{url_hash}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(page_data['clean_html'])
        
        # حفظ المحتوى النصي
        text_path = self.output_dir / 'content' / f"{url_hash}.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(page_data['text_content'])
        
        # حفظ البيانات الوصفية
        json_path = self.output_dir / 'data' / f"{url_hash}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'url': page_data['url'],
                'title': page_data['title'],
                'meta_data': page_data['meta_data'],
                'structured_data': page_data['structured_data'],
                'word_count': page_data['word_count'],
                'extraction_time': page_data['extraction_time']
            }, f, ensure_ascii=False, indent=2)

    def create_site_structure(self, extraction_report: Dict):
        """إنشاء ملفات تنظيم الموقع"""
        # إنشاء فهرس الصفحات
        index_data = {
            'site_url': self.base_url,
            'extraction_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'pages': [
                {
                    'url': page['url'],
                    'title': page['title'],
                    'word_count': page['word_count']
                }
                for page in extraction_report['pages']
            ]
        }
        
        with open(self.output_dir / 'site_index.json', 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        # إنشاء README
        readme_content = f"""# استخراج الموقع: {self.base_url}

## معلومات الاستخراج
- تاريخ الاستخراج: {time.strftime('%Y-%m-%d %H:%M:%S')}
- عدد الصفحات: {self.stats['pages_extracted']}
- عدد الصور: {self.stats['images_downloaded']}
- ملفات CSS: {self.stats['css_files']}
- ملفات JavaScript: {self.stats['js_files']}

## التنظيف المطبق
- إعلانات محذوفة: {self.stats['ads_removed']}
- عناصر تتبع محذوفة: {self.stats['tracking_removed']}

## هيكل المجلدات
- `pages/`: ملفات HTML النظيفة
- `content/`: المحتوى النصي المستخرج
- `assets/`: جميع الأصول (صور، CSS، JS)
- `data/`: البيانات الوصفية والمنظمة

## طريقة الاستخدام
1. انسخ الملفات من مجلد `pages/` كنقطة بداية
2. استخدم المحتوى من `content/` لإعادة الكتابة
3. استخدم الأصول من `assets/` حسب الحاجة
4. راجع `data/` للبيانات المنظمة والوصفية
"""
        
        with open(self.output_dir / 'README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)

    def save_extraction_report(self, report: Dict):
        """حفظ تقرير الاستخراج الشامل"""
        with open(self.output_dir / 'extraction_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"تم حفظ التقرير الشامل في: {self.output_dir / 'extraction_report.json'}")

def extract_website_cli():
    """واجهة سطر الأوامر"""
    import argparse
    
    parser = argparse.ArgumentParser(description='استخراج وتنظيف مواقع الويب')
    parser.add_argument('url', help='رابط الموقع المراد استخراجه')
    parser.add_argument('-o', '--output', default='extracted_website', help='مجلد الإخراج')
    parser.add_argument('-p', '--pages', type=int, default=50, help='عدد الصفحات القصوى')
    
    args = parser.parse_args()
    
    extractor = WebsiteExtractor(args.url, args.output)
    report = extractor.extract_complete_website(args.pages)
    
    print(f"\n✅ اكتمل الاستخراج!")
    print(f"📄 عدد الصفحات: {report['stats']['pages_extracted']}")
    print(f"🖼️ عدد الصور: {report['stats']['images_downloaded']}")
    print(f"🎨 ملفات CSS: {report['stats']['css_files']}")
    print(f"⚡ ملفات JS: {report['stats']['js_files']}")
    print(f"🧹 إعلانات محذوفة: {report['stats']['ads_removed']}")
    print(f"📍 مجلد الإخراج: {args.output}")

if __name__ == '__main__':
    extract_website_cli()