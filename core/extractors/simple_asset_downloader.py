"""
Simple Asset Downloader - تحميل مبسط للصور والملفات
"""

import os
import requests
import logging
from urllib.parse import urljoin, urlparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

class SimpleAssetDownloader:
    """محمل مبسط للأصول والملفات"""
    
    def __init__(self, save_directory: str = "downloaded_assets"):
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # إحصائيات التحميل
        self.stats = {
            'downloaded': 0,
            'failed': 0,
            'total_size': 0,
            'start_time': 0,
            'end_time': 0
        }
        
        # قائمة الامتدادات المدعومة
        self.supported_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico',
            '.css', '.js', '.woff', '.woff2', '.ttf', '.eot',
            '.mp4', '.mp3', '.wav', '.pdf'
        }
    
    def download_assets(self, asset_urls: List[str], base_url: str) -> Dict[str, Any]:
        """تحميل قائمة من الأصول"""
        self.stats['start_time'] = time.time()
        self.logger.info(f"بدء تحميل {len(asset_urls)} أصل...")
        
        downloaded_assets = {}
        failed_downloads = []
        
        # إنشاء مجلد خاص بالموقع
        domain = urlparse(base_url).netloc.replace(':', '_')
        site_dir = self.save_directory / domain
        site_dir.mkdir(parents=True, exist_ok=True)
        
        for asset_url in asset_urls:
            try:
                # تحويل الرابط النسبي إلى مطلق
                full_url = urljoin(base_url, asset_url)
                
                # التحقق من الامتداد
                parsed = urlparse(full_url)
                path = parsed.path.lower()
                
                if not any(path.endswith(ext) for ext in self.supported_extensions):
                    continue
                
                # تحميل الملف
                response = requests.get(full_url, timeout=10, 
                                      headers={'User-Agent': 'Mozilla/5.0 (compatible; AssetDownloader/1.0)'})
                
                if response.status_code == 200:
                    # تحديد اسم الملف ومساره
                    filename = os.path.basename(parsed.path) or 'index.html'
                    file_type = self._get_file_type(filename)
                    
                    # إنشاء مجلد النوع
                    type_dir = site_dir / file_type
                    type_dir.mkdir(parents=True, exist_ok=True)
                    
                    # مسار الحفظ النهائي
                    save_path = type_dir / filename
                    
                    # التعامل مع الأسماء المكررة
                    counter = 1
                    original_path = save_path
                    while save_path.exists():
                        stem = original_path.stem
                        suffix = original_path.suffix
                        save_path = original_path.parent / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    # حفظ الملف
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    
                    downloaded_assets[asset_url] = str(save_path)
                    self.stats['downloaded'] += 1
                    self.stats['total_size'] += len(response.content)
                    
                    self.logger.debug(f"تم تحميل: {filename}")
                
                else:
                    failed_downloads.append(asset_url)
                    self.stats['failed'] += 1
                    self.logger.warning(f"فشل تحميل {asset_url}: {response.status_code}")
                    
            except Exception as e:
                failed_downloads.append(asset_url)
                self.stats['failed'] += 1
                self.logger.error(f"خطأ في تحميل {asset_url}: {e}")
        
        self.stats['end_time'] = time.time()
        
        return {
            'downloaded_assets': downloaded_assets,
            'failed_downloads': failed_downloads,
            'statistics': self.stats,
            'save_directory': str(site_dir)
        }
    
    def _get_file_type(self, filename: str) -> str:
        """تحديد نوع الملف للتنظيم"""
        ext = Path(filename).suffix.lower()
        
        type_mapping = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico'],
            'styles': ['.css'],
            'scripts': ['.js'],
            'fonts': ['.woff', '.woff2', '.ttf', '.eot'],
            'media': ['.mp4', '.mp3', '.wav'],
            'documents': ['.pdf']
        }
        
        for file_type, extensions in type_mapping.items():
            if ext in extensions:
                return file_type
        
        return 'other'