"""
مدير الجلسات والاتصالات الآمنة
Secure Session and Connection Manager
"""

import requests
import time
import ssl
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from typing import Dict, Optional, Any
import urllib3
from .config import ExtractionConfig


class SessionManager:
    """مدير الجلسات الآمن والموثوق"""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.session = self._create_secure_session()
        self.request_count = 0
        self.last_request_time = 0
        
    def _create_secure_session(self) -> requests.Session:
        """إنشاء جلسة HTTP آمنة ومحسنة"""
        session = requests.Session()
        
        # إعداد استراتيجية إعادة المحاولة
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # إعداد headers آمنة
        session.headers.update({
            'User-Agent': self.config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # إعداد SSL بناءً على الإعدادات
        if not self.config.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        return session
    
    def _enforce_rate_limit(self):
        """تطبيق حد معدل الطلبات"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.config.delay_between_requests:
            sleep_time = self.config.delay_between_requests - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """تنفيذ طلب HTTP آمن مع معالجة الأخطاء"""
        self._enforce_rate_limit()
        self.request_count += 1
        
        try:
            # إعداد المعاملات الافتراضية
            request_kwargs = {
                'timeout': self.config.timeout,
                'verify': self.config.verify_ssl,
                'allow_redirects': True,
                'stream': False
            }
            request_kwargs.update(kwargs)
            
            # تحقق من حجم الاستجابة المتوقع
            if 'stream' not in kwargs:
                # طلب HEAD أولاً للتحقق من الحجم
                try:
                    head_response = self.session.head(url, timeout=10, verify=self.config.verify_ssl)
                    content_length = head_response.headers.get('Content-Length')
                    
                    if content_length and int(content_length) > self.config.max_file_size_mb * 1024 * 1024:
                        raise ValueError(f"File too large: {content_length} bytes")
                        
                except Exception:
                    # إذا فشل HEAD request، نتابع بحذر
                    pass
            
            # تنفيذ الطلب
            response = self.session.request(method, url, **request_kwargs)
            
            # التحقق من حجم المحتوى الفعلي
            if hasattr(response, 'content') and len(response.content) > self.config.max_file_size_mb * 1024 * 1024:
                raise ValueError(f"Response too large: {len(response.content)} bytes")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout:
            print(f"Timeout error for URL: {url}")
            return None
            
        except requests.exceptions.ConnectionError:
            print(f"Connection error for URL: {url}")
            return None
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error {e.response.status_code} for URL: {url}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Request error for URL: {url}: {str(e)}")
            return None
            
        except ValueError as e:
            print(f"Validation error for URL: {url}: {str(e)}")
            return None
            
        except Exception as e:
            print(f"Unexpected error for URL: {url}: {str(e)}")
            return None
    
    def download_file(self, url: str, file_path: str, chunk_size: int = 8192) -> bool:
        """تحميل ملف بشكل آمن مع التحقق من الحجم"""
        try:
            response = self.make_request(url, stream=True)
            if not response:
                return False
            
            total_size = 0
            max_size = self.config.max_file_size_mb * 1024 * 1024
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        total_size += len(chunk)
                        
                        # التحقق من الحجم أثناء التحميل
                        if total_size > max_size:
                            f.close()
                            import os
                            os.remove(file_path)
                            raise ValueError(f"File exceeds maximum size: {total_size} bytes")
                        
                        f.write(chunk)
            
            return True
            
        except Exception as e:
            print(f"Error downloading file {url}: {str(e)}")
            return False
    
    def get_session_stats(self) -> Dict[str, Any]:
        """إحصائيات الجلسة"""
        return {
            'total_requests': self.request_count,
            'session_active': bool(self.session),
            'verify_ssl': self.config.verify_ssl,
            'timeout': self.config.timeout,
            'max_retries': self.config.max_retries,
            'delay_between_requests': self.config.delay_between_requests
        }
    
    def close(self):
        """إغلاق الجلسة وتنظيف الموارد"""
        if self.session:
            self.session.close()
            self.session = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()