"""
Spider Engine - زاحف ذكي يتنقل عبر كامل الموقع
المرحلة الأولى: محرك الاستخراج العميق

هذا المحرك يوفر:
1. زحف ذكي عبر كامل الموقع
2. احترام robots.txt وحدود التأخير
3. كشف الصفحات المخفية والديناميكية
4. تجميع خريطة كاملة للموقع
"""

import asyncio
import aiohttp
import logging
import time
import hashlib
import urllib.robotparser
from typing import Dict, List, Set, Optional, Any
from urllib.parse import urljoin, urlparse, parse_qs
from dataclasses import dataclass
from datetime import datetime
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup, Tag
import requests

@dataclass
class SpiderConfig:
    """تكوين محرك الزحف"""
    max_depth: int = 5
    max_pages: int = 100
    delay_between_requests: float = 1.0
    respect_robots_txt: bool = True
    follow_external_links: bool = False
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_domains: List[str] = None
    blocked_extensions: List[str] = None
    user_agent: str = "Mozilla/5.0 (compatible; WebSpider/1.0)"
    timeout: int = 30
    enable_javascript_discovery: bool = True
    extract_sitemap: bool = True
    follow_redirects: bool = True
    max_redirects: int = 5

class SpiderEngine:
    """محرك الزحف الذكي للمواقع"""
    
    def __init__(self, config: Optional[SpiderConfig] = None):
        self.config = config or SpiderConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # بيانات الزحف
        self.visited_urls: Set[str] = set()
        self.discovered_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.site_map: Dict[str, Dict] = {}
        self.robots_cache: Dict[str, urllib.robotparser.RobotFileParser] = {}
        
        # إحصائيات الزحف
        self.crawl_stats = {
            'total_pages': 0,
            'successful_pages': 0,
            'failed_pages': 0,
            'external_links': 0,
            'internal_links': 0,
            'discovered_assets': 0,
            'start_time': None,
            'end_time': None
        }
        
        # أنواع الملفات المختلفة
        self.asset_types = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico'],
            'stylesheets': ['.css'],
            'scripts': ['.js'],
            'documents': ['.pdf', '.doc', '.docx', '.txt'],
            'media': ['.mp4', '.mp3', '.avi', '.wav', '.webm'],
            'fonts': ['.woff', '.woff2', '.ttf', '.otf', '.eot']
        }
        
        if self.config.blocked_extensions is None:
            self.config.blocked_extensions = ['.zip', '.exe', '.dmg', '.iso']
    
    async def __aenter__(self):
        """بدء جلسة الزحف"""
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': self.config.user_agent}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """إنهاء جلسة الزحف"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def crawl_website(self, start_url: str) -> Dict[str, Any]:
        """بدء زحف الموقع الكامل"""
        logging.info(f"بدء زحف الموقع: {start_url}")
        self.crawl_stats['start_time'] = datetime.now()
        
        # تطبيع الرابط الأساسي
        parsed_url = urlparse(start_url)
        base_domain = parsed_url.netloc
        
        if self.config.allowed_domains is None:
            self.config.allowed_domains = [base_domain]
        
        try:
            # 1. فحص robots.txt
            if self.config.respect_robots_txt:
                await self._load_robots_txt(start_url)
            
            # 2. استخراج sitemap.xml
            if self.config.extract_sitemap:
                await self._discover_sitemap(start_url)
            
            # 3. بدء الزحف العمقي
            await self._crawl_recursive(start_url, depth=0)
            
            # 4. اكتشاف الصفحات من JavaScript
            if self.config.enable_javascript_discovery:
                await self._discover_javascript_urls()
            
            self.crawl_stats['end_time'] = datetime.now()
            
            # إنشاء التقرير النهائي
            crawl_report = self._generate_crawl_report()
            
            return crawl_report
            
        except Exception as e:
            logging.error(f"خطأ في زحف الموقع: {e}")
            return {'error': str(e), 'partial_results': self.site_map}
    
    async def _crawl_recursive(self, url: str, depth: int = 0):
        """زحف تكراري للصفحات"""
        if (depth > self.config.max_depth or 
            len(self.visited_urls) >= self.config.max_pages or
            url in self.visited_urls):
            return
        
        # فحص robots.txt
        if not await self._is_allowed_by_robots(url):
            logging.info(f"تم حظر الرابط بواسطة robots.txt: {url}")
            return
        
        # تأخير بين الطلبات
        if self.visited_urls:
            await asyncio.sleep(self.config.delay_between_requests)
        
        try:
            async with self.session.get(url, allow_redirects=self.config.follow_redirects) as response:
                if response.status != 200:
                    self.failed_urls.add(url)
                    self.crawl_stats['failed_pages'] += 1
                    return
                
                # فحص حجم الملف
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > self.config.max_file_size:
                    logging.warning(f"تم تخطي الملف كبير الحجم: {url}")
                    return
                
                content = await response.text()
                self.visited_urls.add(url)
                self.crawl_stats['successful_pages'] += 1
                
                # تحليل الصفحة
                page_data = await self._analyze_page(url, content, response.headers)
                self.site_map[url] = page_data
                
                # اكتشاف روابط جديدة
                soup = BeautifulSoup(content, 'html.parser')
                new_urls = await self._extract_links(url, soup)
                
                # زحف الروابط الجديدة
                tasks = []
                for new_url in new_urls:
                    if new_url not in self.visited_urls and self._is_valid_url(new_url):
                        task = asyncio.create_task(self._crawl_recursive(new_url, depth + 1))
                        tasks.append(task)
                
                # تنفيذ المهام بالتوازي (محدود)
                if tasks:
                    await asyncio.gather(*tasks[:5], return_exceptions=True)
                
        except Exception as e:
            logging.error(f"خطأ في زحف {url}: {e}")
            self.failed_urls.add(url)
            self.crawl_stats['failed_pages'] += 1
    
    async def _analyze_page(self, url: str, content: str, headers: Dict) -> Dict[str, Any]:
        """تحليل شامل للصفحة"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # معلومات أساسية
        page_data = {
            'url': url,
            'title': self._safe_get_text(soup.find('title')),
            'description': self._get_meta_content(soup, 'description'),
            'content_type': headers.get('content-type', ''),
            'size': len(content),
            'word_count': len(content.split()),
            'discovered_at': datetime.now().isoformat(),
            'depth': len([u for u in self.visited_urls if u in url]),
            
            # بنية الصفحة
            'structure': {
                'headings': self._analyze_headings(soup),
                'forms': self._analyze_forms(soup),
                'tables': len(soup.find_all('table')),
                'images': len(soup.find_all('img')),
                'videos': len(soup.find_all(['video', 'iframe'])),
                'scripts': len(soup.find_all('script')),
                'stylesheets': len(soup.find_all('link', rel='stylesheet'))
            },
            
            # روابط
            'links': {
                'internal': [],
                'external': [],
                'assets': []
            },
            
            # تقنيات مكتشفة
            'technologies': self._detect_technologies(soup, content),
            
            # معلومات SEO
            'seo': {
                'canonical': self._get_canonical_url(soup),
                'meta_robots': self._get_meta_content(soup, 'robots'),
                'og_tags': self._extract_og_tags(soup),
                'schema_markup': self._detect_schema_markup(soup)
            }
        }
        
        return page_data
    
    async def _extract_links(self, base_url: str, soup: BeautifulSoup) -> Set[str]:
        """استخراج جميع الروابط من الصفحة"""
        new_urls = set()
        base_domain = urlparse(base_url).netloc
        
        # روابط HTML
        for link in soup.find_all(['a', 'area'], href=True):
            if isinstance(link, Tag):
                href = link.get('href', '').strip()
                if href and not href.startswith('#'):
                    full_url = urljoin(base_url, href)
                    parsed = urlparse(full_url)
                    
                    # فحص النطاق
                    if self.config.follow_external_links or parsed.netloc == base_domain:
                        if self._is_valid_url(full_url):
                            new_urls.add(full_url)
                            self.discovered_urls.add(full_url)
        
        # روابط من JavaScript (أساسي)
        scripts = soup.find_all('script')
        for script in scripts:
            if isinstance(script, Tag) and script.string:
                # البحث عن patterns URL في JavaScript
                url_patterns = re.findall(r'["\']([^"\']*\.[a-z]{2,4}[^"\']*)["\']', script.string)
                for pattern in url_patterns:
                    if self._looks_like_url(pattern):
                        full_url = urljoin(base_url, pattern)
                        if self._is_valid_url(full_url):
                            new_urls.add(full_url)
        
        return new_urls
    
    async def _load_robots_txt(self, url: str):
        """تحميل وتحليل robots.txt"""
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        try:
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    robots_content = await response.text()
                    rp = urllib.robotparser.RobotFileParser()
                    rp.set_url(robots_url)
                    rp.read()
                    self.robots_cache[parsed.netloc] = rp
                    logging.info(f"تم تحميل robots.txt من {robots_url}")
        except Exception as e:
            logging.warning(f"فشل في تحميل robots.txt: {e}")
    
    async def _discover_sitemap(self, url: str):
        """اكتشاف واستخراج sitemap.xml"""
        parsed = urlparse(url)
        sitemap_urls = [
            f"{parsed.scheme}://{parsed.netloc}/sitemap.xml",
            f"{parsed.scheme}://{parsed.netloc}/sitemap_index.xml",
            f"{parsed.scheme}://{parsed.netloc}/sitemaps.xml"
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                async with self.session.get(sitemap_url) as response:
                    if response.status == 200:
                        sitemap_content = await response.text()
                        urls = self._parse_sitemap(sitemap_content)
                        self.discovered_urls.update(urls)
                        logging.info(f"تم اكتشاف {len(urls)} رابط من {sitemap_url}")
                        break
            except Exception as e:
                logging.debug(f"لم يتم العثور على sitemap في {sitemap_url}")
    
    def _parse_sitemap(self, sitemap_content: str) -> Set[str]:
        """تحليل sitemap.xml"""
        urls = set()
        try:
            soup = BeautifulSoup(sitemap_content, 'xml')
            
            # sitemap عادي
            for loc in soup.find_all('loc'):
                if loc.string:
                    urls.add(loc.string.strip())
            
            # sitemap index
            for sitemap in soup.find_all('sitemap'):
                loc = sitemap.find('loc')
                if loc and loc.string:
                    # يمكن إضافة زحف sitemap فرعي هنا
                    pass
                    
        except Exception as e:
            logging.error(f"خطأ في تحليل sitemap: {e}")
        
        return urls
    
    async def _discover_javascript_urls(self):
        """اكتشاف URLs من ملفات JavaScript"""
        js_urls = set()
        
        for url, page_data in self.site_map.items():
            try:
                async with self.session.get(url) as response:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # تحليل ملفات JS الخارجية
                    for script in soup.find_all('script', src=True):
                        if isinstance(script, Tag):
                            js_url = urljoin(url, script.get('src', ''))
                            try:
                                async with self.session.get(js_url) as js_response:
                                    js_content = await js_response.text()
                                    urls = self._extract_urls_from_js(js_content, url)
                                    js_urls.update(urls)
                            except:
                                pass
            except:
                pass
        
        # إضافة URLs المكتشفة للزحف
        for js_url in js_urls:
            if js_url not in self.visited_urls and self._is_valid_url(js_url):
                await self._crawl_recursive(js_url, depth=self.config.max_depth - 1)
    
    def _extract_urls_from_js(self, js_content: str, base_url: str) -> Set[str]:
        """استخراج URLs من محتوى JavaScript"""
        urls = set()
        
        # patterns شائعة للروابط في JS
        patterns = [
            r'["\']([^"\']*\.html?)["\']',
            r'["\']([^"\']*\.php)["\']',
            r'["\']([^"\']*\.jsp)["\']',
            r'["\']([^"\']*\.asp)["\']',
            r'url\s*:\s*["\']([^"\']+)["\']',
            r'href\s*:\s*["\']([^"\']+)["\']',
            r'location\.href\s*=\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                if self._looks_like_url(match):
                    full_url = urljoin(base_url, match)
                    urls.add(full_url)
        
        return urls
    
    async def _is_allowed_by_robots(self, url: str) -> bool:
        """فحص إذا كان الرابط مسموح في robots.txt"""
        if not self.config.respect_robots_txt:
            return True
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        if domain in self.robots_cache:
            rp = self.robots_cache[domain]
            return rp.can_fetch(self.config.user_agent, url)
        
        return True  # السماح إذا لم يوجد robots.txt
    
    def _is_valid_url(self, url: str) -> bool:
        """فحص صحة الرابط"""
        try:
            parsed = urlparse(url)
            
            # فحص المخطط
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # فحص النطاق المسموح
            if self.config.allowed_domains and parsed.netloc not in self.config.allowed_domains:
                return False
            
            # فحص الامتدادات المحظورة
            path_lower = parsed.path.lower()
            for ext in self.config.blocked_extensions:
                if path_lower.endswith(ext):
                    return False
            
            return True
            
        except:
            return False
    
    def _looks_like_url(self, text: str) -> bool:
        """فحص إذا كان النص يبدو كرابط"""
        if not text or len(text) < 3:
            return False
        
        # patterns أساسية
        url_patterns = [
            r'^https?://',
            r'^/[a-zA-Z0-9]',
            r'\.[a-z]{2,4}(/|$)',
            r'[a-zA-Z0-9]+\.(html?|php|jsp|asp)'
        ]
        
        for pattern in url_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _analyze_headings(self, soup: BeautifulSoup) -> Dict[str, int]:
        """تحليل العناوين"""
        headings = {}
        for i in range(1, 7):
            headings[f'h{i}'] = len(soup.find_all(f'h{i}'))
        return headings
    
    def _analyze_forms(self, soup: BeautifulSoup) -> List[Dict]:
        """تحليل النماذج"""
        forms = []
        for form in soup.find_all('form'):
            if isinstance(form, Tag):
                forms.append({
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get').lower(),
                    'inputs': len(form.find_all('input')),
                    'has_file_upload': bool(form.find('input', type='file'))
                })
        return forms
    
    def _detect_technologies(self, soup: BeautifulSoup, content: str) -> List[str]:
        """كشف التقنيات المستخدمة"""
        technologies = []
        
        # فحص JavaScript frameworks
        js_frameworks = {
            'react': ['react', 'reactdom'],
            'vue': ['vue.js', 'vue.min.js'],
            'angular': ['angular.js', 'angular.min.js'],
            'jquery': ['jquery', 'jquery.min.js']
        }
        
        for tech, patterns in js_frameworks.items():
            for pattern in patterns:
                if pattern in content.lower():
                    technologies.append(tech)
                    break
        
        # فحص CSS frameworks
        if 'bootstrap' in content.lower():
            technologies.append('bootstrap')
        if 'tailwind' in content.lower():
            technologies.append('tailwind')
        
        return list(set(technologies))
    
    def _get_meta_content(self, soup: BeautifulSoup, name: str) -> str:
        """استخراج محتوى meta tag"""
        meta = soup.find('meta', attrs={'name': name}) or soup.find('meta', attrs={'property': name})
        return meta.get('content', '') if meta and isinstance(meta, Tag) else ''
    
    def _get_canonical_url(self, soup: BeautifulSoup) -> str:
        """استخراج canonical URL"""
        canonical = soup.find('link', rel='canonical')
        return canonical.get('href', '') if canonical and isinstance(canonical, Tag) else ''
    
    def _extract_og_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """استخراج Open Graph tags"""
        og_tags = {}
        for meta in soup.find_all('meta', attrs={'property': lambda x: x and x.startswith('og:')}):
            if isinstance(meta, Tag):
                prop = meta.get('property', '')
                content = meta.get('content', '')
                if prop and content:
                    og_tags[prop] = content
        return og_tags
    
    def _detect_schema_markup(self, soup: BeautifulSoup) -> List[str]:
        """كشف Schema.org markup"""
        schemas = []
        
        # JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            if isinstance(script, Tag) and script.string:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and '@type' in data:
                        schemas.append(data['@type'])
                except:
                    pass
        
        # Microdata
        for element in soup.find_all(attrs={'itemtype': True}):
            if isinstance(element, Tag):
                itemtype = element.get('itemtype', '')
                if 'schema.org' in itemtype:
                    schema_type = itemtype.split('/')[-1]
                    schemas.append(schema_type)
        
        return list(set(schemas))
    
    def _safe_get_text(self, element) -> str:
        """استخراج نص آمن من العنصر"""
        if element and hasattr(element, 'get_text'):
            return element.get_text(strip=True)
        return ''
    
    def _generate_crawl_report(self) -> Dict[str, Any]:
        """إنشاء تقرير الزحف النهائي"""
        duration = None
        if self.crawl_stats['start_time'] and self.crawl_stats['end_time']:
            duration = (self.crawl_stats['end_time'] - self.crawl_stats['start_time']).total_seconds()
        
        return {
            'crawl_summary': {
                'total_pages_discovered': len(self.discovered_urls),
                'total_pages_crawled': len(self.visited_urls),
                'successful_pages': self.crawl_stats['successful_pages'],
                'failed_pages': self.crawl_stats['failed_pages'],
                'success_rate': (self.crawl_stats['successful_pages'] / max(len(self.visited_urls), 1)) * 100,
                'crawl_duration_seconds': duration,
                'pages_per_second': len(self.visited_urls) / max(duration, 1) if duration else 0
            },
            
            'site_structure': {
                'total_pages': len(self.site_map),
                'page_types': self._categorize_pages(),
                'technology_stack': self._aggregate_technologies(),
                'common_elements': self._analyze_common_elements()
            },
            
            'discovered_urls': list(self.discovered_urls),
            'failed_urls': list(self.failed_urls),
            'site_map': self.site_map,
            
            'crawl_config': {
                'max_depth': self.config.max_depth,
                'max_pages': self.config.max_pages,
                'respected_robots_txt': self.config.respect_robots_txt,
                'followed_external_links': self.config.follow_external_links
            }
        }
    
    def _categorize_pages(self) -> Dict[str, int]:
        """تصنيف أنواع الصفحات"""
        categories = {
            'homepage': 0,
            'product_pages': 0,
            'blog_posts': 0,
            'contact_pages': 0,
            'about_pages': 0,
            'category_pages': 0,
            'other': 0
        }
        
        for url, page_data in self.site_map.items():
            path = urlparse(url).path.lower()
            title = page_data.get('title', '').lower()
            
            if path in ['/', '/index.html', '/home']:
                categories['homepage'] += 1
            elif any(word in path or word in title for word in ['product', 'item', 'shop']):
                categories['product_pages'] += 1
            elif any(word in path or word in title for word in ['blog', 'article', 'post', 'news']):
                categories['blog_posts'] += 1
            elif any(word in path or word in title for word in ['contact', 'connect', 'reach']):
                categories['contact_pages'] += 1
            elif any(word in path or word in title for word in ['about', 'who', 'team', 'company']):
                categories['about_pages'] += 1
            elif any(word in path or word in title for word in ['category', 'section', 'department']):
                categories['category_pages'] += 1
            else:
                categories['other'] += 1
        
        return categories
    
    def _aggregate_technologies(self) -> Dict[str, int]:
        """تجميع التقنيات المكتشفة"""
        tech_count = {}
        for page_data in self.site_map.values():
            technologies = page_data.get('technologies', [])
            for tech in technologies:
                tech_count[tech] = tech_count.get(tech, 0) + 1
        return tech_count
    
    def _analyze_common_elements(self) -> Dict[str, Any]:
        """تحليل العناصر المشتركة"""
        total_pages = len(self.site_map)
        if total_pages == 0:
            return {}
        
        # تجميع الإحصائيات
        forms_count = sum(len(page.get('structure', {}).get('forms', [])) for page in self.site_map.values())
        images_count = sum(page.get('structure', {}).get('images', 0) for page in self.site_map.values())
        scripts_count = sum(page.get('structure', {}).get('scripts', 0) for page in self.site_map.values())
        
        return {
            'average_forms_per_page': forms_count / total_pages,
            'average_images_per_page': images_count / total_pages,
            'average_scripts_per_page': scripts_count / total_pages,
            'pages_with_schema_markup': len([p for p in self.site_map.values() if p.get('seo', {}).get('schema_markup')]),
            'pages_with_og_tags': len([p for p in self.site_map.values() if p.get('seo', {}).get('og_tags')])
        }