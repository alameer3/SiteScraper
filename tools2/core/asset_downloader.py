"""
منزل الأصول المتطور
Advanced Asset Downloader
"""

import os
import mimetypes
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Any, Optional, Set
from bs4 import BeautifulSoup, Tag
from .config import ExtractionConfig
from .session_manager import SessionManager
from .file_manager import FileManager


class AssetDownloader:
    """منزل أصول متطور وآمن"""
    
    def __init__(self, config: ExtractionConfig, session_manager: SessionManager, file_manager: FileManager):
        self.config = config
        self.session = session_manager
        self.file_manager = file_manager
        self.downloaded_assets = set()
        
    def download_all_assets(self, soup: BeautifulSoup, base_url: str, extraction_folder: Path) -> Dict[str, Any]:
        """تحميل جميع الأصول من الصفحة"""
        
        download_results = {
            'images': [],
            'css': [],
            'js': [],
            'fonts': [],
            'documents': [],
            'other': [],
            'failed': [],
            'statistics': {
                'total_found': 0,
                'total_downloaded': 0,
                'total_failed': 0,
                'total_size_mb': 0
            }
        }
        
        if not self.config.extract_assets:
            return download_results
        
        # تحميل الصور
        if self.config.extract_images:
            images_result = self._download_images(soup, base_url, extraction_folder)
            download_results['images'] = images_result
        
        # تحميل ملفات CSS
        if self.config.extract_css:
            css_result = self._download_css_files(soup, base_url, extraction_folder)
            download_results['css'] = css_result
        
        # تحميل ملفات JavaScript
        if self.config.extract_js:
            js_result = self._download_js_files(soup, base_url, extraction_folder)
            download_results['js'] = js_result
        
        # تحميل الخطوط
        fonts_result = self._download_fonts(soup, base_url, extraction_folder)
        download_results['fonts'] = fonts_result
        
        # تحميل المستندات
        documents_result = self._download_documents(soup, base_url, extraction_folder)
        download_results['documents'] = documents_result
        
        # تحديث الإحصائيات
        download_results['statistics'] = self._calculate_download_statistics(download_results)
        
        return download_results
    
    def _download_images(self, soup: BeautifulSoup, base_url: str, extraction_folder: Path) -> List[Dict[str, Any]]:
        """تحميل الصور"""
        images_result = []
        images = soup.find_all('img', src=True)
        
        for img in images[:20]:  # أول 20 صورة
            if not isinstance(img, Tag):
                continue
                
            src = img.get('src')
            if not src or src.startswith('data:'):
                continue
            
            # تحويل الرابط النسبي إلى مطلق
            if not src.startswith(('http://', 'https://')):
                src = urljoin(base_url, src)
            
            # تجنب التحميل المكرر
            if src in self.downloaded_assets:
                continue
            
            try:
                # تحميل الصورة
                response = self.session.make_request(src)
                if not response:
                    images_result.append({
                        'src': src,
                        'status': 'failed',
                        'error': 'فشل في الاتصال'
                    })
                    continue
                
                # تحديد اسم الملف
                filename = self._get_filename_from_url(src, 'image')
                
                # تحديد نوع الملف
                content_type = response.headers.get('Content-Type', '')
                file_extension = self._get_extension_from_content_type(content_type) or self._get_extension_from_url(src)
                
                if file_extension and not filename.endswith(file_extension):
                    filename += file_extension
                
                # حفظ الصورة
                saved_path = self.file_manager.save_asset_file(
                    response.content, 
                    extraction_folder, 
                    filename, 
                    'images'
                )
                
                if saved_path:
                    self.downloaded_assets.add(src)
                    images_result.append({
                        'src': src,
                        'saved_path': str(saved_path),
                        'filename': filename,
                        'size_bytes': len(response.content),
                        'content_type': content_type,
                        'status': 'success'
                    })
                else:
                    images_result.append({
                        'src': src,
                        'status': 'failed',
                        'error': 'فشل في حفظ الملف'
                    })
                    
            except Exception as e:
                images_result.append({
                    'src': src,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return images_result
    
    def _download_css_files(self, soup: BeautifulSoup, base_url: str, extraction_folder: Path) -> List[Dict[str, Any]]:
        """تحميل ملفات CSS"""
        css_result = []
        css_links = soup.find_all('link', rel='stylesheet', href=True)
        
        for link in css_links[:10]:  # أول 10 ملفات CSS
            if not isinstance(link, Tag):
                continue
                
            href = link.get('href')
            if not href:
                continue
            
            # تحويل الرابط النسبي إلى مطلق
            if not href.startswith(('http://', 'https://')):
                href = urljoin(base_url, href)
            
            # تجنب التحميل المكرر
            if href in self.downloaded_assets:
                continue
            
            try:
                response = self.session.make_request(href)
                if not response:
                    css_result.append({
                        'href': href,
                        'status': 'failed',
                        'error': 'فشل في الاتصال'
                    })
                    continue
                
                filename = self._get_filename_from_url(href, 'style') + '.css'
                
                # حفظ ملف CSS
                saved_path = self.file_manager.save_asset_file(
                    response.content, 
                    extraction_folder, 
                    filename, 
                    'css'
                )
                
                if saved_path:
                    self.downloaded_assets.add(href)
                    
                    # تحليل CSS للبحث عن موارد إضافية
                    css_content = response.text
                    embedded_resources = self._extract_css_resources(css_content, href, extraction_folder)
                    
                    css_result.append({
                        'href': href,
                        'saved_path': str(saved_path),
                        'filename': filename,
                        'size_bytes': len(response.content),
                        'embedded_resources': embedded_resources,
                        'status': 'success'
                    })
                else:
                    css_result.append({
                        'href': href,
                        'status': 'failed',
                        'error': 'فشل في حفظ الملف'
                    })
                    
            except Exception as e:
                css_result.append({
                    'href': href,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return css_result
    
    def _download_js_files(self, soup: BeautifulSoup, base_url: str, extraction_folder: Path) -> List[Dict[str, Any]]:
        """تحميل ملفات JavaScript"""
        js_result = []
        js_scripts = soup.find_all('script', src=True)
        
        for script in js_scripts[:10]:  # أول 10 سكريبتات
            if not isinstance(script, Tag):
                continue
                
            src = script.get('src')
            if not src:
                continue
            
            # تحويل الرابط النسبي إلى مطلق
            if not src.startswith(('http://', 'https://')):
                src = urljoin(base_url, src)
            
            # تجنب التحميل المكرر
            if src in self.downloaded_assets:
                continue
            
            try:
                response = self.session.make_request(src)
                if not response:
                    js_result.append({
                        'src': src,
                        'status': 'failed',
                        'error': 'فشل في الاتصال'
                    })
                    continue
                
                filename = self._get_filename_from_url(src, 'script') + '.js'
                
                # حفظ ملف JavaScript
                saved_path = self.file_manager.save_asset_file(
                    response.content, 
                    extraction_folder, 
                    filename, 
                    'js'
                )
                
                if saved_path:
                    self.downloaded_assets.add(src)
                    js_result.append({
                        'src': src,
                        'saved_path': str(saved_path),
                        'filename': filename,
                        'size_bytes': len(response.content),
                        'status': 'success'
                    })
                else:
                    js_result.append({
                        'src': src,
                        'status': 'failed',
                        'error': 'فشل في حفظ الملف'
                    })
                    
            except Exception as e:
                js_result.append({
                    'src': src,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return js_result
    
    def _download_fonts(self, soup: BeautifulSoup, base_url: str, extraction_folder: Path) -> List[Dict[str, Any]]:
        """تحميل الخطوط"""
        fonts_result = []
        
        # البحث عن روابط الخطوط في CSS
        style_tags = soup.find_all('style')
        link_tags = soup.find_all('link', rel='stylesheet')
        
        font_urls = set()
        
        # استخراج روابط الخطوط من style tags
        for style in style_tags:
            if style.string:
                font_urls.update(self._extract_font_urls_from_css(style.string, base_url))
        
        # استخراج روابط الخطوط من Google Fonts وغيرها
        for link in link_tags:
            if isinstance(link, Tag):
                href = link.get('href', '')
                if 'fonts.googleapis.com' in href or 'fonts.gstatic.com' in href:
                    font_urls.add(href)
        
        # تحميل الخطوط
        for font_url in list(font_urls)[:5]:  # أول 5 خطوط
            try:
                response = self.session.make_request(font_url)
                if not response:
                    continue
                
                filename = self._get_filename_from_url(font_url, 'font')
                file_extension = self._get_extension_from_url(font_url) or '.woff2'
                
                if not filename.endswith(file_extension):
                    filename += file_extension
                
                saved_path = self.file_manager.save_asset_file(
                    response.content, 
                    extraction_folder, 
                    filename, 
                    'fonts'
                )
                
                if saved_path:
                    fonts_result.append({
                        'url': font_url,
                        'saved_path': str(saved_path),
                        'filename': filename,
                        'size_bytes': len(response.content),
                        'status': 'success'
                    })
                    
            except Exception as e:
                fonts_result.append({
                    'url': font_url,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return fonts_result
    
    def _download_documents(self, soup: BeautifulSoup, base_url: str, extraction_folder: Path) -> List[Dict[str, Any]]:
        """تحميل المستندات"""
        documents_result = []
        
        # البحث عن روابط المستندات
        document_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.zip']
        links = soup.find_all('a', href=True)
        
        for link in links:
            if not isinstance(link, Tag):
                continue
                
            href = link.get('href')
            if not href:
                continue
            
            # فحص امتداد الملف
            if not any(href.lower().endswith(ext) for ext in document_extensions):
                continue
            
            # تحويل الرابط النسبي إلى مطلق
            if not href.startswith(('http://', 'https://')):
                href = urljoin(base_url, href)
            
            # تجنب التحميل المكرر
            if href in self.downloaded_assets:
                continue
            
            try:
                response = self.session.make_request(href)
                if not response:
                    continue
                
                filename = self._get_filename_from_url(href, 'document')
                file_extension = self._get_extension_from_url(href)
                
                if file_extension and not filename.endswith(file_extension):
                    filename += file_extension
                
                saved_path = self.file_manager.save_asset_file(
                    response.content, 
                    extraction_folder, 
                    filename, 
                    'documents'
                )
                
                if saved_path:
                    self.downloaded_assets.add(href)
                    documents_result.append({
                        'href': href,
                        'saved_path': str(saved_path),
                        'filename': filename,
                        'size_bytes': len(response.content),
                        'document_type': self._get_document_type_from_extension(file_extension),
                        'status': 'success'
                    })
                    
                # حد أقصى 3 مستندات
                if len(documents_result) >= 3:
                    break
                    
            except Exception as e:
                documents_result.append({
                    'href': href,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return documents_result
    
    def _extract_css_resources(self, css_content: str, css_url: str, extraction_folder: Path) -> List[Dict[str, Any]]:
        """استخراج الموارد المضمنة في CSS"""
        import re
        
        resources = []
        
        # البحث عن روابط الصور في CSS
        url_pattern = r'url\(["\']?([^"\')\s]+)["\']?\)'
        matches = re.findall(url_pattern, css_content)
        
        for match in matches[:5]:  # أول 5 موارد
            resource_url = match
            
            # تحويل الرابط النسبي إلى مطلق
            if not resource_url.startswith(('http://', 'https://', 'data:')):
                css_base = '/'.join(css_url.split('/')[:-1])
                resource_url = urljoin(css_base + '/', resource_url)
            
            # تجاهل data URLs
            if resource_url.startswith('data:'):
                continue
            
            try:
                response = self.session.make_request(resource_url)
                if response:
                    filename = self._get_filename_from_url(resource_url, 'css_resource')
                    file_extension = self._get_extension_from_url(resource_url)
                    
                    if file_extension and not filename.endswith(file_extension):
                        filename += file_extension
                    
                    saved_path = self.file_manager.save_asset_file(
                        response.content, 
                        extraction_folder, 
                        filename, 
                        'css_resources'
                    )
                    
                    if saved_path:
                        resources.append({
                            'original_url': match,
                            'full_url': resource_url,
                            'saved_path': str(saved_path),
                            'filename': filename,
                            'size_bytes': len(response.content),
                            'status': 'success'
                        })
                        
            except Exception as e:
                resources.append({
                    'original_url': match,
                    'full_url': resource_url,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return resources
    
    def _extract_font_urls_from_css(self, css_content: str, base_url: str) -> Set[str]:
        """استخراج روابط الخطوط من CSS"""
        import re
        
        font_urls = set()
        
        # البحث عن @font-face rules
        font_face_pattern = r'@font-face\s*{[^}]*url\(["\']?([^"\')\s]+)["\']?\)[^}]*}'
        matches = re.findall(font_face_pattern, css_content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            if not match.startswith(('http://', 'https://', 'data:')):
                font_url = urljoin(base_url, match)
            else:
                font_url = match
            
            if not font_url.startswith('data:'):
                font_urls.add(font_url)
        
        return font_urls
    
    def _get_filename_from_url(self, url: str, prefix: str = 'file') -> str:
        """استخراج اسم الملف من الرابط"""
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        
        # إزالة المعاملات من اسم الملف
        if '?' in filename:
            filename = filename.split('?')[0]
        
        # تنظيف اسم الملف
        filename = self.file_manager._sanitize_filename(filename)
        
        # إذا لم يكن هناك اسم ملف مناسب، إنشاء واحد
        if not filename or len(filename) < 3:
            import hashlib
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"{prefix}_{url_hash}"
        
        return filename
    
    def _get_extension_from_url(self, url: str) -> str:
        """استخراج امتداد الملف من الرابط"""
        parsed = urlparse(url)
        path = parsed.path
        
        if '.' in path:
            extension = '.' + path.split('.')[-1].split('?')[0].lower()
            # التحقق من أن الامتداد صالح
            if len(extension) <= 6 and extension.replace('.', '').isalnum():
                return extension
        
        return ''
    
    def _get_extension_from_content_type(self, content_type: str) -> str:
        """تحديد امتداد الملف من نوع المحتوى"""
        content_type_map = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/svg+xml': '.svg',
            'text/css': '.css',
            'application/javascript': '.js',
            'text/javascript': '.js',
            'application/pdf': '.pdf',
            'font/woff': '.woff',
            'font/woff2': '.woff2',
            'application/font-woff': '.woff',
            'application/font-woff2': '.woff2'
        }
        
        # إزالة المعاملات الإضافية من content type
        clean_content_type = content_type.split(';')[0].strip().lower()
        
        return content_type_map.get(clean_content_type, '')
    
    def _get_document_type_from_extension(self, extension: str) -> str:
        """تحديد نوع المستند من الامتداد"""
        doc_types = {
            '.pdf': 'PDF Document',
            '.doc': 'Word Document',
            '.docx': 'Word Document',
            '.xls': 'Excel Spreadsheet',
            '.xlsx': 'Excel Spreadsheet',
            '.ppt': 'PowerPoint Presentation',
            '.pptx': 'PowerPoint Presentation',
            '.txt': 'Text Document',
            '.zip': 'Archive File'
        }
        
        return doc_types.get(extension.lower(), 'Unknown Document')
    
    def _calculate_download_statistics(self, download_results: Dict[str, Any]) -> Dict[str, Any]:
        """حساب إحصائيات التحميل"""
        total_found = 0
        total_downloaded = 0
        total_failed = 0
        total_size_bytes = 0
        
        for category in ['images', 'css', 'js', 'fonts', 'documents']:
            category_data = download_results.get(category, [])
            if isinstance(category_data, list):
                total_found += len(category_data)
                
                for item in category_data:
                    if item.get('status') == 'success':
                        total_downloaded += 1
                        total_size_bytes += item.get('size_bytes', 0)
                    elif item.get('status') == 'failed':
                        total_failed += 1
        
        return {
            'total_found': total_found,
            'total_downloaded': total_downloaded,
            'total_failed': total_failed,
            'success_rate': round((total_downloaded / max(total_found, 1)) * 100, 1),
            'total_size_bytes': total_size_bytes,
            'total_size_mb': round(total_size_bytes / (1024 * 1024), 2),
            'average_file_size_kb': round(total_size_bytes / max(total_downloaded, 1) / 1024, 1) if total_downloaded > 0 else 0
        }