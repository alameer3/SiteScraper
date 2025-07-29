"""
محرك الزحف المتقدم - Advanced Spider Engine
يوفر زحف متعدد الصفحات واكتشاف الروابط الخفية
"""

import asyncio
import aiohttp
import time
from typing import Dict, List, Any, Set, Optional
from urllib.parse import urljoin, urlparse
from pathlib import Path
from dataclasses import dataclass
from bs4 import BeautifulSoup

from .session_manager import SessionManager
from .content_extractor import ContentExtractor
from .config import ExtractionConfig


@dataclass
class SpiderConfig:
    """إعدادات محرك الزحف"""
    max_pages: int = 100
    max_depth: int = 3
    delay_between_requests: float = 1.0
    follow_external_links: bool = False
    extract_sitemap: bool = True
    discover_hidden_pages: bool = True
    analyze_robots_txt: bool = True
    max_concurrent_requests: int = 5


class AdvancedSpiderEngine:
    """محرك زحف متقدم لاستكشاف المواقع بعمق"""
    
    def __init__(self, config: Optional[SpiderConfig] = None):
        self.config = config or SpiderConfig()
        self.session_manager = SessionManager()
        self.content_extractor = ContentExtractor()
        
        # تتبع الزحف
        self.visited_urls: Set[str] = set()
        self.discovered_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.crawl_queue: List[Dict[str, Any]] = []
        self.results: Dict[str, Any] = {}
        
    async def crawl_website(self, start_url: str, extraction_config: ExtractionConfig) -> Dict[str, Any]:
        """زحف شامل للموقع"""
        start_time = time.time()
        domain = urlparse(start_url).netloc
        
        crawl_result = {
            'start_url': start_url,
            'domain': domain,
            'start_time': time.time(),
            'pages_crawled': {},
            'sitemap_analysis': {},
            'robots_analysis': {},
            'hidden_pages': [],
            'statistics': {},
            'errors': []
        }
        
        try:
            session = await self.session_manager.get_session()
            
            # المرحلة 1: تحليل robots.txt
            if self.config.analyze_robots_txt:
                robots_analysis = await self._analyze_robots_txt(start_url, session)
                crawl_result['robots_analysis'] = robots_analysis
            
            # المرحلة 2: استخراج sitemap
            if self.config.extract_sitemap:
                sitemap_analysis = await self._extract_sitemap(start_url, session)
                crawl_result['sitemap_analysis'] = sitemap_analysis
                
                # إضافة URLs من sitemap لقائمة الزحف
                for url in sitemap_analysis.get('urls_found', []):
                    self._add_to_crawl_queue(url, 0, 'sitemap')
                
            # المرحلة 3: بدء الزحف من الصفحة الرئيسية
            self._add_to_crawl_queue(start_url, 0, 'start_page')
                
                # المرحلة 4: زحف متوازي
                semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
                tasks = []
                
                while self.crawl_queue and len(self.visited_urls) < self.config.max_pages:
                    current_batch = []
                    
                    # أخذ دفعة من الصفحات للزحف
                    for _ in range(min(self.config.max_concurrent_requests, len(self.crawl_queue))):
                        if self.crawl_queue:
                            current_batch.append(self.crawl_queue.pop(0))
                    
                    # إنشاء مهام الزحف
                    for page_info in current_batch:
                        if page_info['url'] not in self.visited_urls:
                            task = self._crawl_single_page(
                                semaphore, session, page_info, 
                                domain, extraction_config
                            )
                            tasks.append(task)
                    
                    # تنفيذ المهام وانتظار النتائج
                    if tasks:
                        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                        
                        for result in batch_results:
                            if isinstance(result, dict) and 'url' in result:
                                crawl_result['pages_crawled'][result['url']] = result
                                
                                # اكتشاف روابط جديدة
                                if result.get('links'):
                                    self._discover_new_links(
                                        result['links'], result['depth'], domain
                                    )
                        
                        tasks.clear()
                
                # المرحلة 5: اكتشاف الصفحات الخفية
                if self.config.discover_hidden_pages:
                    hidden_pages = await self._discover_hidden_pages(start_url, session, domain)
                    crawl_result['hidden_pages'] = hidden_pages
                
                # إحصائيات نهائية
                crawl_result['statistics'] = self._calculate_crawl_statistics(crawl_result)
                crawl_result['duration'] = time.time() - start_time
                crawl_result['success'] = True
                
        except Exception as e:
            crawl_result['success'] = False
            crawl_result['error'] = str(e)
            crawl_result['duration'] = time.time() - start_time
        
        return crawl_result
    
    async def _crawl_single_page(self, semaphore: asyncio.Semaphore, 
                                session: aiohttp.ClientSession,
                                page_info: Dict[str, Any],
                                domain: str,
                                extraction_config: ExtractionConfig) -> Dict[str, Any]:
        """زحف صفحة واحدة"""
        
        async with semaphore:
            url = page_info['url']
            depth = page_info['depth']
            source = page_info['source']
            
            if url in self.visited_urls:
                return {'url': url, 'status': 'already_visited'}
            
            self.visited_urls.add(url)
            
            try:
                # تأخير بين الطلبات
                if self.config.delay_between_requests > 0:
                    await asyncio.sleep(self.config.delay_between_requests)
                
                # جلب الصفحة
                timeout = aiohttp.ClientTimeout(total=30)
                async with session.get(url, timeout=timeout) as response:
                    if response.status != 200:
                        return {
                            'url': url, 
                            'status': 'failed',
                            'status_code': response.status,
                            'depth': depth,
                            'source': source
                        }
                    
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                
                # استخراج المحتوى الأساسي
                extraction_result = {
                    'title': soup.title.string if soup.title else '',
                    'description': '',
                    'content_text': soup.get_text()[:1000]  # أول 1000 حرف
                }
                
                # استخراج الروابط
                links = self._extract_links(soup, url, domain)
                
                return {
                    'url': url,
                    'status': 'success',
                    'depth': depth,
                    'source': source,
                    'title': extraction_result.get('title', ''),
                    'content_length': len(content),
                    'links': links,
                    'images_count': len(soup.find_all('img')),
                    'extraction_data': extraction_result,
                    'timestamp': time.time()
                }
                
            except Exception as e:
                self.failed_urls.add(url)
                return {
                    'url': url,
                    'status': 'error',
                    'error': str(e),
                    'depth': depth,
                    'source': source
                }
    
    def _extract_links(self, soup: BeautifulSoup, current_url: str, domain: str) -> List[Dict[str, str]]:
        """استخراج جميع الروابط من الصفحة"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = str(link.get('href', ''))
            if not href:
                continue
            
            # تحويل الروابط النسبية إلى مطلقة
            absolute_url = urljoin(current_url, href)
            parsed_url = urlparse(absolute_url)
            
            # تصنيف الرابط
            link_type = 'external'
            if parsed_url.netloc == domain or parsed_url.netloc == '':
                link_type = 'internal'
            
            # تنظيف الرابط
            clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            if parsed_url.query:
                clean_url += f"?{parsed_url.query}"
            
            links.append({
                'url': clean_url,
                'text': link.get_text(strip=True)[:100],
                'type': link_type,
                'original_href': href
            })
        
        return links
    
    def _discover_new_links(self, links: List[Dict[str, str]], current_depth: int, domain: str):
        """اكتشاف روابط جديدة وإضافتها لقائمة الزحف"""
        
        if current_depth >= self.config.max_depth:
            return
        
        for link in links:
            url = link['url']
            link_type = link['type']
            
            # تحقق من شروط الإضافة
            if url in self.visited_urls or url in self.discovered_urls:
                continue
            
            if link_type == 'external' and not self.config.follow_external_links:
                continue
            
            # إضافة للقائمة
            self._add_to_crawl_queue(url, current_depth + 1, 'discovered_link')
            self.discovered_urls.add(url)
    
    def _add_to_crawl_queue(self, url: str, depth: int, source: str):
        """إضافة URL لقائمة الزحف"""
        
        # تجنب التكرار
        for item in self.crawl_queue:
            if item['url'] == url:
                return
        
        self.crawl_queue.append({
            'url': url,
            'depth': depth,
            'source': source,
            'priority': self._calculate_url_priority(url, source)
        })
        
        # ترتيب حسب الأولوية
        self.crawl_queue.sort(key=lambda x: x['priority'], reverse=True)
    
    def _calculate_url_priority(self, url: str, source: str) -> int:
        """حساب أولوية الرابط"""
        priority = 0
        
        # أولوية حسب المصدر
        if source == 'start_page':
            priority += 100
        elif source == 'sitemap':
            priority += 80
        elif source == 'discovered_link':
            priority += 50
        
        # أولوية حسب نوع الصفحة
        url_lower = url.lower()
        if any(keyword in url_lower for keyword in ['about', 'contact', 'services']):
            priority += 20
        elif any(keyword in url_lower for keyword in ['blog', 'news', 'article']):
            priority += 15
        elif any(keyword in url_lower for keyword in ['admin', 'login', 'dashboard']):
            priority += 30
        
        return priority
    
    async def _analyze_robots_txt(self, base_url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """تحليل ملف robots.txt"""
        
        robots_url = urljoin(base_url, '/robots.txt')
        analysis = {
            'url': robots_url,
            'exists': False,
            'rules': [],
            'sitemaps': [],
            'disallowed_paths': [],
            'allowed_paths': []
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with session.get(robots_url, timeout=timeout) as response:
                if response.status == 200:
                    content = await response.text()
                    analysis['exists'] = True
                    analysis['content'] = content
                    
                    # تحليل القواعد
                    lines = content.split('\n')
                    current_user_agent = None
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith('User-agent:'):
                            current_user_agent = line.split(':', 1)[1].strip()
                        elif line.startswith('Disallow:'):
                            path = line.split(':', 1)[1].strip()
                            analysis['disallowed_paths'].append({
                                'user_agent': current_user_agent,
                                'path': path
                            })
                        elif line.startswith('Allow:'):
                            path = line.split(':', 1)[1].strip()
                            analysis['allowed_paths'].append({
                                'user_agent': current_user_agent,
                                'path': path
                            })
                        elif line.startswith('Sitemap:'):
                            sitemap_url = line.split(':', 1)[1].strip()
                            analysis['sitemaps'].append(sitemap_url)
                
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    async def _extract_sitemap(self, base_url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """استخراج وتحليل sitemap"""
        
        sitemap_analysis = {
            'urls_found': [],
            'sitemaps_checked': [],
            'total_urls': 0,
            'errors': []
        }
        
        # قائمة المسارات المحتملة لـ sitemap
        sitemap_paths = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap.txt',
            '/sitemaps.xml'
        ]
        
        for path in sitemap_paths:
            sitemap_url = urljoin(base_url, path)
            try:
                timeout = aiohttp.ClientTimeout(total=15)
                async with session.get(sitemap_url, timeout=timeout) as response:
                    if response.status == 200:
                        content = await response.text()
                        sitemap_analysis['sitemaps_checked'].append({
                            'url': sitemap_url,
                            'status': 'found',
                            'size': len(content)
                        })
                        
                        # تحليل محتوى sitemap
                        urls = self._parse_sitemap_content(content, sitemap_url)
                        sitemap_analysis['urls_found'].extend(urls)
                    else:
                        sitemap_analysis['sitemaps_checked'].append({
                            'url': sitemap_url,
                            'status': 'not_found',
                            'status_code': response.status
                        })
                        
            except Exception as e:
                sitemap_analysis['errors'].append({
                    'url': sitemap_url,
                    'error': str(e)
                })
        
        sitemap_analysis['total_urls'] = len(sitemap_analysis['urls_found'])
        return sitemap_analysis
    
    def _parse_sitemap_content(self, content: str, sitemap_url: str) -> List[str]:
        """تحليل محتوى sitemap واستخراج URLs"""
        urls = []
        
        try:
            # تحقق من نوع sitemap
            if content.strip().startswith('<?xml'):
                # XML sitemap
                soup = BeautifulSoup(content, 'xml')
                
                # البحث عن عناصر URL
                for url_element in soup.find_all('url'):
                    loc_element = url_element.find('loc')
                    if loc_element and hasattr(loc_element, 'text') and loc_element.text:
                        urls.append(loc_element.text.strip())
                
                # البحث عن sitemaps فرعية
                for sitemap_element in soup.find_all('sitemap'):
                    loc_element = sitemap_element.find('loc')
                    if loc_element and hasattr(loc_element, 'text') and loc_element.text:
                        # يمكن إضافة منطق لجلب sitemaps فرعية هنا
                        pass
            
            else:
                # Text sitemap
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and line.startswith('http'):
                        urls.append(line)
        
        except Exception as e:
            print(f"خطأ في تحليل sitemap {sitemap_url}: {e}")
        
        return urls
    
    async def _discover_hidden_pages(self, base_url: str, session: aiohttp.ClientSession, 
                                   domain: str) -> List[Dict[str, Any]]:
        """اكتشاف الصفحات الخفية"""
        
        hidden_pages = []
        
        # قائمة المسارات الشائعة المخفية
        common_paths = [
            '/admin', '/admin/', '/admin/login', '/admin/dashboard',
            '/login', '/login/', '/signin', '/auth',
            '/dashboard', '/dashboard/', '/panel', '/cp',
            '/api', '/api/', '/api/v1', '/api/docs',
            '/docs', '/documentation', '/help',
            '/search', '/upload', '/download',
            '/test', '/demo', '/dev', '/staging',
            '/backup', '/old', '/tmp', '/temp'
        ]
        
        # فحص كل مسار
        for path in common_paths:
            test_url = urljoin(base_url, path)
            
            try:
                timeout = aiohttp.ClientTimeout(total=10)
                async with session.get(test_url, timeout=timeout, allow_redirects=False) as response:
                    if response.status in [200, 301, 302, 403]:
                        hidden_pages.append({
                            'url': test_url,
                            'status_code': response.status,
                            'type': 'common_path',
                            'accessible': response.status == 200
                        })
                        
            except Exception as e:
                # تجاهل الأخطاء للصفحات المخفية
                continue
        
        return hidden_pages
    
    def _calculate_crawl_statistics(self, crawl_result: Dict[str, Any]) -> Dict[str, Any]:
        """حساب إحصائيات الزحف"""
        
        pages_crawled = crawl_result.get('pages_crawled', {})
        
        statistics = {
            'total_pages_crawled': len(pages_crawled),
            'successful_pages': len([p for p in pages_crawled.values() if p.get('status') == 'success']),
            'failed_pages': len([p for p in pages_crawled.values() if p.get('status') == 'error']),
            'total_links_found': 0,
            'internal_links': 0,
            'external_links': 0,
            'average_page_size': 0,
            'total_images': 0,
            'unique_titles': set(),
            'depth_distribution': {}
        }
        
        total_content_length = 0
        
        for page_data in pages_crawled.values():
            if page_data.get('status') == 'success':
                # إحصائيات الروابط
                links = page_data.get('links', [])
                statistics['total_links_found'] += len(links)
                
                for link in links:
                    if link.get('type') == 'internal':
                        statistics['internal_links'] += 1
                    else:
                        statistics['external_links'] += 1
                
                # إحصائيات أخرى
                statistics['total_images'] += page_data.get('images_count', 0)
                total_content_length += page_data.get('content_length', 0)
                
                if page_data.get('title'):
                    statistics['unique_titles'].add(page_data['title'])
                
                # توزيع العمق
                depth = page_data.get('depth', 0)
                statistics['depth_distribution'][depth] = statistics['depth_distribution'].get(depth, 0) + 1
        
        # حساب المتوسطات
        if statistics['successful_pages'] > 0:
            statistics['average_page_size'] = total_content_length / statistics['successful_pages']
        
        statistics['unique_titles_count'] = len(statistics['unique_titles'])
        statistics['unique_titles'] = list(statistics['unique_titles'])  # تحويل لقائمة
        
        return statistics
    
    def get_crawl_summary(self) -> Dict[str, Any]:
        """ملخص سريع لحالة الزحف"""
        return {
            'visited_urls_count': len(self.visited_urls),
            'discovered_urls_count': len(self.discovered_urls),
            'failed_urls_count': len(self.failed_urls),
            'queue_remaining': len(self.crawl_queue),
            'config': {
                'max_pages': self.config.max_pages,
                'max_depth': self.config.max_depth,
                'max_concurrent': self.config.max_concurrent_requests
            }
        }