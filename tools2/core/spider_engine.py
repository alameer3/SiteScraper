"""
محرك الزحف المتقدم
Advanced Spider Engine for Multi-Page Crawling
"""

import re
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser
from dataclasses import dataclass
from collections import deque
import xml.etree.ElementTree as ET


@dataclass
class SpiderConfig:
    """إعدادات محرك الزحف"""
    max_pages: int = 50
    max_depth: int = 3
    delay_between_requests: float = 1.0
    respect_robots_txt: bool = True
    follow_external_links: bool = False
    allowed_file_types: List[str] = None
    excluded_patterns: List[str] = None
    concurrent_requests: int = 5
    
    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = ['.html', '.htm', '.php', '.asp', '.aspx', '.jsp']
        if self.excluded_patterns is None:
            self.excluded_patterns = ['/admin/', '/login/', '/logout/', '/wp-admin/', '/cgi-bin/']


class AdvancedSpiderEngine:
    """محرك زحف متطور لاستكشاف المواقع"""
    
    def __init__(self, config: SpiderConfig):
        self.config = config
        self.visited_urls = set()
        self.discovered_urls = set()
        self.crawl_queue = deque()
        self.robots_parser = None
        self.sitemap_urls = set()
        self.crawl_errors = []
        
    def crawl_website(self, start_url: str, extraction_config) -> Dict[str, Any]:
        """بدء عملية الزحف الشاملة"""
        
        crawl_result = {
            'start_url': start_url,
            'pages_crawled': [],
            'total_pages_discovered': 0,
            'total_pages_crawled': 0,
            'crawl_depth_reached': 0,
            'sitemap_analysis': {},
            'robots_analysis': {},
            'link_structure': {},
            'content_summary': {},
            'errors': [],
            'crawl_duration': 0
        }
        
        start_time = time.time()
        
        try:
            print(f"🕷️ بدء الزحف من: {start_url}")
            
            # 1. تحليل robots.txt
            robots_analysis = self._analyze_robots_txt(start_url)
            crawl_result['robots_analysis'] = robots_analysis
            
            # 2. البحث عن واستكشاف sitemap
            sitemap_analysis = self._discover_and_analyze_sitemap(start_url)
            crawl_result['sitemap_analysis'] = sitemap_analysis
            
            # 3. إعداد الزحف
            self._initialize_crawl(start_url)
            
            # 4. تنفيذ الزحف
            pages_crawled = self._perform_crawl(start_url, extraction_config)
            crawl_result['pages_crawled'] = pages_crawled
            
            # 5. تحليل بنية الروابط
            link_structure = self._analyze_link_structure()
            crawl_result['link_structure'] = link_structure
            
            # 6. ملخص المحتوى
            content_summary = self._generate_content_summary(pages_crawled)
            crawl_result['content_summary'] = content_summary
            
            # 7. إحصائيات الزحف
            crawl_result['total_pages_discovered'] = len(self.discovered_urls)
            crawl_result['total_pages_crawled'] = len(pages_crawled)
            crawl_result['crawl_depth_reached'] = max([page.get('depth', 0) for page in pages_crawled] + [0])
            crawl_result['errors'] = self.crawl_errors
            
        except Exception as e:
            crawl_result['errors'].append(f"خطأ في الزحف: {str(e)}")
            print(f"❌ خطأ في الزحف: {e}")
        
        crawl_result['crawl_duration'] = round(time.time() - start_time, 2)
        print(f"✅ انتهى الزحف في {crawl_result['crawl_duration']} ثانية")
        
        return crawl_result
    
    def _analyze_robots_txt(self, base_url: str) -> Dict[str, Any]:
        """تحليل ملف robots.txt"""
        
        robots_analysis = {
            'exists': False,
            'user_agents': [],
            'disallowed_paths': [],
            'allowed_paths': [],
            'crawl_delay': None,
            'sitemap_urls': [],
            'compliance_score': 0
        }
        
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            
            # محاولة تحميل robots.txt
            self.robots_parser = RobotFileParser()
            self.robots_parser.set_url(robots_url)
            self.robots_parser.read()
            
            robots_analysis['exists'] = True
            
            # تحليل المحتوى (تحتاج تطوير إضافي)
            # هنا يمكن إضافة تحليل أكثر تفصيلاً
            
            print(f"📋 تم العثور على robots.txt: {robots_url}")
            
        except Exception as e:
            robots_analysis['error'] = str(e)
            print(f"⚠️ لا يمكن الوصول لـ robots.txt: {e}")
        
        return robots_analysis
    
    def _discover_and_analyze_sitemap(self, base_url: str) -> Dict[str, Any]:
        """اكتشاف وتحليل sitemap"""
        
        sitemap_analysis = {
            'sitemaps_found': [],
            'total_urls': 0,
            'url_types': {},
            'last_modified_dates': [],
            'priorities': [],
            'change_frequencies': []
        }
        
        # مواقع محتملة لـ sitemap
        potential_sitemaps = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap.txt',
            '/sitemaps.xml',
            '/wp-sitemap.xml'
        ]
        
        for sitemap_path in potential_sitemaps:
            try:
                sitemap_url = urljoin(base_url, sitemap_path)
                # هنا يمكن إضافة كود لتحميل وتحليل sitemap
                # نحتاج session manager للطلبات
                print(f"🗺️ فحص sitemap: {sitemap_url}")
                
            except Exception as e:
                continue
        
        return sitemap_analysis
    
    def _initialize_crawl(self, start_url: str):
        """تهيئة عملية الزحف"""
        
        # إضافة URL البداية إلى قائمة الانتظار
        parsed_start = urlparse(start_url)
        self.base_domain = parsed_start.netloc
        
        self.crawl_queue.append({
            'url': start_url,
            'depth': 0,
            'parent_url': None,
            'link_text': 'START'
        })
        
        self.discovered_urls.add(start_url)
    
    def _perform_crawl(self, start_url: str, extraction_config) -> List[Dict[str, Any]]:
        """تنفيذ عملية الزحف الرئيسية"""
        
        pages_crawled = []
        
        while self.crawl_queue and len(pages_crawled) < self.config.max_pages:
            
            current_item = self.crawl_queue.popleft()
            current_url = current_item['url']
            current_depth = current_item['depth']
            
            # تحقق من أننا لم نزحف هذا الرابط من قبل
            if current_url in self.visited_urls:
                continue
            
            # تحقق من عمق الزحف
            if current_depth > self.config.max_depth:
                continue
            
            # تحقق من robots.txt
            if self.config.respect_robots_txt and self.robots_parser:
                if not self.robots_parser.can_fetch('*', current_url):
                    print(f"🚫 منع بواسطة robots.txt: {current_url}")
                    continue
            
            try:
                print(f"🔍 زحف: {current_url} (عمق: {current_depth})")
                
                # هنا نحتاج session manager للطلب
                page_data = self._crawl_single_page(current_url, current_depth, current_item)
                
                if page_data:
                    pages_crawled.append(page_data)
                    self.visited_urls.add(current_url)
                    
                    # استخراج الروابط الجديدة
                    if current_depth < self.config.max_depth:
                        new_links = self._extract_links_from_page(page_data, current_url, current_depth)
                        self._add_links_to_queue(new_links, current_depth + 1, current_url)
                
                # تأخير بين الطلبات
                time.sleep(self.config.delay_between_requests)
                
            except Exception as e:
                error_msg = f"خطأ في زحف {current_url}: {str(e)}"
                self.crawl_errors.append(error_msg)
                print(f"❌ {error_msg}")
                continue
        
        return pages_crawled
    
    def _crawl_single_page(self, url: str, depth: int, item_info: Dict) -> Optional[Dict[str, Any]]:
        """زحف صفحة واحدة (يحتاج session manager)"""
        
        # هنا نحتاج session manager للطلب الفعلي
        # حالياً سنرجع بيانات أساسية
        
        page_data = {
            'url': url,
            'depth': depth,
            'parent_url': item_info.get('parent_url'),
            'link_text': item_info.get('link_text', ''),
            'title': '',
            'description': '',
            'content_length': 0,
            'links_count': 0,
            'images_count': 0,
            'response_code': 200,
            'content_type': 'text/html',
            'discovered_links': [],
            'timestamp': time.time()
        }
        
        # محاكاة معالجة الصفحة
        # في التطبيق الحقيقي، هنا سنستخدم session manager للحصول على المحتوى
        # ثم نحلل HTML باستخدام BeautifulSoup
        
        return page_data
    
    def _extract_links_from_page(self, page_data: Dict, base_url: str, current_depth: int) -> List[Dict[str, Any]]:
        """استخراج الروابط من الصفحة"""
        
        links = []
        
        # هنا نحتاج المحتوى الفعلي للصفحة لاستخراج الروابط
        # حالياً سنرجع قائمة فارغة
        
        return links
    
    def _add_links_to_queue(self, links: List[Dict], depth: int, parent_url: str):
        """إضافة روابط جديدة لقائمة الزحف"""
        
        for link in links:
            url = link.get('url', '')
            
            if not url or url in self.visited_urls:
                continue
            
            # تحقق من أنواع الملفات المسموحة
            if not self._is_allowed_url(url):
                continue
            
            # تحقق من الروابط الخارجية
            if not self.config.follow_external_links:
                parsed = urlparse(url)
                if parsed.netloc and parsed.netloc != self.base_domain:
                    continue
            
            # تحقق من الأنماط المستبعدة
            if self._is_excluded_url(url):
                continue
            
            # إضافة إلى قائمة الانتظار
            if url not in self.discovered_urls:
                self.crawl_queue.append({
                    'url': url,
                    'depth': depth,
                    'parent_url': parent_url,
                    'link_text': link.get('text', '')
                })
                self.discovered_urls.add(url)
    
    def _is_allowed_url(self, url: str) -> bool:
        """تحقق من أن الرابط مسموح"""
        
        # تحقق من امتداد الملف
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # إذا لم يكن هناك امتداد، اعتبره مسموح
        if '.' not in path.split('/')[-1]:
            return True
        
        # تحقق من الامتدادات المسموحة
        for ext in self.config.allowed_file_types:
            if path.endswith(ext.lower()):
                return True
        
        return False
    
    def _is_excluded_url(self, url: str) -> bool:
        """تحقق من أن الرابط غير مستبعد"""
        
        url_lower = url.lower()
        
        for pattern in self.config.excluded_patterns:
            if pattern.lower() in url_lower:
                return True
        
        return False
    
    def _analyze_link_structure(self) -> Dict[str, Any]:
        """تحليل بنية الروابط"""
        
        structure = {
            'total_internal_links': 0,
            'total_external_links': 0,
            'depth_distribution': {},
            'most_linked_pages': [],
            'orphan_pages': [],
            'link_density': 0
        }
        
        # تحليل بناءً على البيانات المجمعة
        # هنا يمكن إضافة تحليل أكثر تفصيلاً
        
        return structure
    
    def _generate_content_summary(self, pages_crawled: List[Dict]) -> Dict[str, Any]:
        """توليد ملخص المحتوى"""
        
        summary = {
            'total_pages': len(pages_crawled),
            'average_content_length': 0,
            'content_types_distribution': {},
            'title_analysis': {
                'average_length': 0,
                'most_common_words': []
            },
            'page_types_detected': [],
            'crawl_efficiency': 0
        }
        
        if not pages_crawled:
            return summary
        
        # حساب متوسط طول المحتوى
        total_length = sum(page.get('content_length', 0) for page in pages_crawled)
        summary['average_content_length'] = total_length // len(pages_crawled)
        
        # تحليل أنواع المحتوى
        content_types = {}
        for page in pages_crawled:
            content_type = page.get('content_type', 'unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        summary['content_types_distribution'] = content_types
        
        # حساب كفاءة الزحف
        if self.discovered_urls:
            efficiency = (len(pages_crawled) / len(self.discovered_urls)) * 100
            summary['crawl_efficiency'] = round(efficiency, 2)
        
        return summary
    
    def get_crawl_statistics(self) -> Dict[str, Any]:
        """إحصائيات عملية الزحف"""
        
        return {
            'urls_discovered': len(self.discovered_urls),
            'urls_visited': len(self.visited_urls),
            'urls_in_queue': len(self.crawl_queue),
            'crawl_completion_rate': (len(self.visited_urls) / max(len(self.discovered_urls), 1)) * 100,
            'errors_count': len(self.crawl_errors),
            'base_domain': getattr(self, 'base_domain', ''),
            'config': {
                'max_pages': self.config.max_pages,
                'max_depth': self.config.max_depth,
                'delay_between_requests': self.config.delay_between_requests,
                'respect_robots_txt': self.config.respect_robots_txt
            }
        }
    
    def export_discovered_urls(self, output_file: Path) -> bool:
        """تصدير الروابط المكتشفة"""
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# URLs مكتشفة من الزحف\n")
                f.write(f"# إجمالي: {len(self.discovered_urls)}\n\n")
                
                for url in sorted(self.discovered_urls):
                    status = "✅ تم الزحف" if url in self.visited_urls else "⏳ في الانتظار"
                    f.write(f"{url} - {status}\n")
            
            return True
        
        except Exception as e:
            print(f"خطأ في تصدير الروابط: {e}")
            return False
    
    def cleanup(self):
        """تنظيف الذاكرة"""
        self.visited_urls.clear()
        self.discovered_urls.clear()
        self.crawl_queue.clear()
        self.crawl_errors.clear()
        self.sitemap_urls.clear()
        self.robots_parser = None