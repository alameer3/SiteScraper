#!/usr/bin/env python3
"""
نظام استخراج فائق السرعة
Ultra-Fast Website Extractor - Optimized for Maximum Responsiveness
"""

import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import json
import random
from datetime import datetime
import logging
import asyncio
import aiohttp
import concurrent.futures
from threading import Thread

# تعطيل تحذيرات SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class UltraFastExtractor:
    """نظام استخراج فائق السرعة مع استجابة فورية"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.timeout = 3  # timeout فائق السرعة
        self.max_workers = 4  # معالجة متوازية
        
        # User agents محسنة للسرعة
        self.fast_user_agents = [
            'Mozilla/5.0 (compatible; FastBot/1.0)',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
        ]
        
        # المواقع الآمنة للاختبار السريع
        self.instant_test_sites = [
            'https://httpbin.org/',
            'https://example.com/',
            'https://jsonplaceholder.typicode.com/'
        ]
    
    def create_lightning_session(self) -> requests.Session:
        """إنشاء جلسة فائقة السرعة"""
        session = requests.Session()
        
        # إعداد retry فائق السرعة
        retry_strategy = Retry(
            total=1,  # محاولة واحدة فقط
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy, 
            pool_maxsize=2,
            pool_block=False
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers مبسطة للسرعة
        session.headers.update({
            'User-Agent': random.choice(self.fast_user_agents),
            'Accept': 'text/html,*/*;q=0.8',
            'Connection': 'close',  # إغلاق سريع
            'Cache-Control': 'no-cache'
        })
        
        return session
    
    def instant_fetch(self, url: str) -> dict:
        """جلب فوري خلال 3 ثواني أو أقل"""
        start_time = time.time()
        
        result = {
            'success': False,
            'response': None,
            'error': None,
            'method': 'instant_fetch',
            'response_time': 0
        }
        
        try:
            session = self.create_lightning_session()
            
            # جلب فوري مع timeout قصير جداً
            response = session.get(url, timeout=self.timeout, verify=False, stream=False)
            
            result['response_time'] = round(time.time() - start_time, 3)
            
            if response.status_code == 200:
                result['success'] = True
                result['response'] = response
            elif response.status_code == 403:
                result['error'] = f'403 Forbidden - المحتوى محمي'
            elif response.status_code == 404:
                result['error'] = f'404 Not Found - الصفحة غير موجودة'
            else:
                result['error'] = f'HTTP {response.status_code}'
                
        except requests.exceptions.Timeout:
            result['error'] = f'انتهت المهلة ({self.timeout}s)'
            result['response_time'] = self.timeout
        except requests.exceptions.ConnectionError:
            result['error'] = 'فشل في الاتصال'
            result['response_time'] = round(time.time() - start_time, 3)
        except Exception as e:
            result['error'] = f'خطأ: {str(e)[:50]}'
            result['response_time'] = round(time.time() - start_time, 3)
        
        return result
    
    def extract_lightning_fast(self, url: str) -> dict:
        """استخراج فائق السرعة - أقل من 5 ثواني"""
        total_start = time.time()
        
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'total_time': 0,
            'data': {},
            'error': None,
            'suggestions': self.instant_test_sites,
            'performance': {
                'fetch_time': 0,
                'parse_time': 0,
                'analysis_time': 0
            }
        }
        
        try:
            # الخطوة 1: جلب فوري
            fetch_start = time.time()
            fetch_result = self.instant_fetch(url)
            result['performance']['fetch_time'] = round(time.time() - fetch_start, 3)
            
            if not fetch_result['success']:
                result['error'] = fetch_result['error']
                result['total_time'] = round(time.time() - total_start, 3)
                return result
            
            response = fetch_result['response']
            
            # الخطوة 2: تحليل سريع
            parse_start = time.time()
            soup = BeautifulSoup(response.text[:50000], 'html.parser')  # حد أقصى 50KB للسرعة
            result['performance']['parse_time'] = round(time.time() - parse_start, 3)
            
            # الخطوة 3: استخراج أساسي فائق السرعة
            analysis_start = time.time()
            
            # معلومات أساسية
            title_tag = soup.find('title')
            title = title_tag.get_text().strip()[:100] if title_tag else 'بدون عنوان'
            
            # إحصائيات سريعة
            links_count = len(soup.find_all('a', href=True, limit=50))
            images_count = len(soup.find_all('img', limit=20))
            
            # تحليل أساسي للمحتوى
            text_content = soup.get_text()[:1000]  # أول 1000 حرف فقط
            word_count = len(text_content.split())
            
            result['performance']['analysis_time'] = round(time.time() - analysis_start, 3)
            
            # بناء النتيجة
            result['data'] = {
                'basic_info': {
                    'title': title,
                    'url': url,
                    'domain': urlparse(url).netloc,
                    'status_code': response.status_code,
                    'content_size_kb': round(len(response.content) / 1024, 1),
                    'server': response.headers.get('server', 'غير محدد')[:30]
                },
                'quick_stats': {
                    'links': links_count,
                    'images': images_count,
                    'word_count': word_count,
                    'has_forms': bool(soup.find('form')),
                    'has_scripts': bool(soup.find('script'))
                },
                'response_info': {
                    'response_time': fetch_result['response_time'],
                    'https': url.startswith('https://'),
                    'content_type': response.headers.get('content-type', 'غير محدد')[:50]
                }
            }
            
            result['success'] = True
            
        except Exception as e:
            self.logger.error(f"خطأ في التحليل السريع: {str(e)}")
            result['error'] = f"خطأ في التحليل: {str(e)[:100]}"
        
        finally:
            result['total_time'] = round(time.time() - total_start, 3)
        
        return result
    
    def parallel_extract(self, urls: list) -> list:
        """استخراج متوازي لعدة مواقع"""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.extract_lightning_fast, url): url for url in urls}
            
            for future in concurrent.futures.as_completed(future_to_url, timeout=10):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'url': url,
                        'success': False,
                        'error': f'خطأ في المعالجة: {str(e)[:50]}',
                        'total_time': 10
                    })
        
        return results
    
    def health_check(self) -> dict:
        """فحص سريع لصحة النظام"""
        start_time = time.time()
        
        # اختبار موقع سريع
        test_result = self.extract_lightning_fast('https://httpbin.org/')
        
        return {
            'system_healthy': test_result['success'],
            'response_time': test_result.get('total_time', 0),
            'error': test_result.get('error'),
            'timestamp': datetime.now().isoformat(),
            'check_duration': round(time.time() - start_time, 3)
        }

# إنشاء instance عام
ultra_fast_extractor = UltraFastExtractor()