"""
محرك لقطات الشاشة المتطور
Advanced Screenshot Engine
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
from .session_manager import SessionManager


class ScreenshotEngine:
    """محرك لقطات شاشة متطور مع دعم مختلف أحجام الشاشات"""
    
    def __init__(self, session_manager: SessionManager):
        self.session = session_manager
        self.supported_engines = self._check_available_engines()
        
    def _check_available_engines(self) -> Dict[str, bool]:
        """فحص محركات لقطات الشاشة المتاحة"""
        engines = {
            'selenium': False,
            'playwright': False,
            'pyppeteer': False,
            'requests_html': False
        }
        
        try:
            import selenium
            engines['selenium'] = True
        except ImportError:
            pass
            
        try:
            import playwright
            engines['playwright'] = True
        except ImportError:
            pass
            
        try:
            import pyppeteer
            engines['pyppeteer'] = True
        except ImportError:
            pass
            
        try:
            import requests_html
            engines['requests_html'] = True
        except ImportError:
            pass
            
        return engines
    
    def capture_screenshots(self, url: str, output_folder: Path, 
                          capture_mobile: bool = True,
                          capture_tablet: bool = True,
                          capture_full_page: bool = True) -> Dict[str, Any]:
        """التقاط لقطات شاشة متعددة الأحجام"""
        
        result = {
            'success': False,
            'screenshots': [],
            'errors': [],
            'engine_used': None,
            'total_screenshots': 0
        }
        
        # اختيار أفضل محرك متاح
        engine = self._select_best_engine()
        if not engine:
            result['errors'].append("لا يوجد محرك لقطات شاشة متاح")
            return result
        
        result['engine_used'] = engine
        
        try:
            if engine == 'selenium':
                screenshots = self._capture_with_selenium(url, output_folder, 
                                                        capture_mobile, capture_tablet, capture_full_page)
            elif engine == 'playwright':
                screenshots = self._capture_with_playwright(url, output_folder,
                                                          capture_mobile, capture_tablet, capture_full_page)
            elif engine == 'pyppeteer':
                screenshots = self._capture_with_pyppeteer(url, output_folder,
                                                         capture_mobile, capture_tablet, capture_full_page)
            else:
                # استخدام طريقة مبسطة
                screenshots = self._capture_simple(url, output_folder)
            
            result['screenshots'] = screenshots
            result['total_screenshots'] = len(screenshots)
            result['success'] = len(screenshots) > 0
            
        except Exception as e:
            result['errors'].append(f"خطأ في التقاط لقطات الشاشة: {str(e)}")
            
        return result
    
    def _select_best_engine(self) -> Optional[str]:
        """اختيار أفضل محرك متاح"""
        # ترتيب الأولويات
        preferred_order = ['playwright', 'selenium', 'pyppeteer', 'requests_html']
        
        for engine in preferred_order:
            if self.supported_engines.get(engine, False):
                return engine
        
        return None
    
    def _capture_with_selenium(self, url: str, output_folder: Path,
                             capture_mobile: bool, capture_tablet: bool, 
                             capture_full_page: bool) -> List[Dict[str, str]]:
        """التقاط لقطات باستخدام Selenium"""
        screenshots = []
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # إعداد Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # أحجام الشاشات المختلفة
            screen_sizes = [
                {'name': 'desktop', 'width': 1920, 'height': 1080, 'enabled': True},
                {'name': 'tablet', 'width': 768, 'height': 1024, 'enabled': capture_tablet},
                {'name': 'mobile', 'width': 375, 'height': 667, 'enabled': capture_mobile}
            ]
            
            for size in screen_sizes:
                if not size['enabled']:
                    continue
                    
                try:
                    driver = webdriver.Chrome(options=chrome_options)
                    driver.set_window_size(size['width'], size['height'])
                    driver.get(url)
                    
                    # انتظار تحميل الصفحة
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    time.sleep(2)  # وقت إضافي للتحميل
                    
                    # اسم الملف
                    domain = urlparse(url).netloc.replace('.', '_')
                    timestamp = int(time.time())
                    filename = f"screenshot_{domain}_{size['name']}_{timestamp}.png"
                    filepath = output_folder / 'screenshots' / filename
                    
                    # إنشاء مجلد لقطات الشاشة
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    
                    # التقاط لقطة الشاشة
                    if capture_full_page:
                        # لقطة شاشة كاملة
                        total_height = driver.execute_script("return document.body.scrollHeight")
                        driver.set_window_size(size['width'], total_height)
                        time.sleep(1)
                    
                    driver.save_screenshot(str(filepath))
                    
                    screenshots.append({
                        'device': size['name'],
                        'filename': filename,
                        'filepath': str(filepath),
                        'width': size['width'],
                        'height': size['height'],
                        'full_page': capture_full_page,
                        'file_size': os.path.getsize(filepath) if filepath.exists() else 0
                    })
                    
                    driver.quit()
                    
                except Exception as e:
                    print(f"خطأ في التقاط لقطة {size['name']}: {e}")
                    if 'driver' in locals():
                        driver.quit()
                    continue
                        
        except ImportError:
            raise Exception("Selenium غير مثبت")
            
        return screenshots
    
    def _capture_with_playwright(self, url: str, output_folder: Path,
                                capture_mobile: bool, capture_tablet: bool, 
                                capture_full_page: bool) -> List[Dict[str, str]]:
        """التقاط لقطات باستخدام Playwright"""
        screenshots = []
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                
                # أحجام الشاشات
                screen_sizes = [
                    {'name': 'desktop', 'width': 1920, 'height': 1080, 'enabled': True},
                    {'name': 'tablet', 'width': 768, 'height': 1024, 'enabled': capture_tablet},
                    {'name': 'mobile', 'width': 375, 'height': 667, 'enabled': capture_mobile}
                ]
                
                for size in screen_sizes:
                    if not size['enabled']:
                        continue
                        
                    try:
                        page = browser.new_page(
                            viewport={'width': size['width'], 'height': size['height']}
                        )
                        
                        page.goto(url, wait_until='networkidle')
                        page.wait_for_timeout(2000)  # انتظار إضافي
                        
                        # اسم الملف
                        domain = urlparse(url).netloc.replace('.', '_')
                        timestamp = int(time.time())
                        filename = f"screenshot_{domain}_{size['name']}_{timestamp}.png"
                        filepath = output_folder / 'screenshots' / filename
                        
                        # إنشاء مجلد
                        filepath.parent.mkdir(parents=True, exist_ok=True)
                        
                        # التقاط لقطة الشاشة
                        page.screenshot(
                            path=str(filepath),
                            full_page=capture_full_page
                        )
                        
                        screenshots.append({
                            'device': size['name'],
                            'filename': filename,
                            'filepath': str(filepath),
                            'width': size['width'],
                            'height': size['height'],
                            'full_page': capture_full_page,
                            'file_size': os.path.getsize(filepath) if filepath.exists() else 0
                        })
                        
                        page.close()
                        
                    except Exception as e:
                        print(f"خطأ في التقاط لقطة {size['name']}: {e}")
                        continue
                
                browser.close()
                
        except ImportError:
            raise Exception("Playwright غير مثبت")
            
        return screenshots
    
    def _capture_with_pyppeteer(self, url: str, output_folder: Path,
                              capture_mobile: bool, capture_tablet: bool, 
                              capture_full_page: bool) -> List[Dict[str, str]]:
        """التقاط لقطات باستخدام Pyppeteer"""
        screenshots = []
        
        try:
            import asyncio
            from pyppeteer import launch
            
            async def capture_async():
                browser = await launch(headless=True)
                
                screen_sizes = [
                    {'name': 'desktop', 'width': 1920, 'height': 1080, 'enabled': True},
                    {'name': 'tablet', 'width': 768, 'height': 1024, 'enabled': capture_tablet},
                    {'name': 'mobile', 'width': 375, 'height': 667, 'enabled': capture_mobile}
                ]
                
                for size in screen_sizes:
                    if not size['enabled']:
                        continue
                        
                    try:
                        page = await browser.newPage()
                        await page.setViewport({'width': size['width'], 'height': size['height']})
                        await page.goto(url, {'waitUntil': 'networkidle2'})
                        await page.waitFor(2000)
                        
                        # اسم الملف
                        domain = urlparse(url).netloc.replace('.', '_')
                        timestamp = int(time.time())
                        filename = f"screenshot_{domain}_{size['name']}_{timestamp}.png"
                        filepath = output_folder / 'screenshots' / filename
                        
                        # إنشاء مجلد
                        filepath.parent.mkdir(parents=True, exist_ok=True)
                        
                        # التقاط لقطة الشاشة
                        await page.screenshot({
                            'path': str(filepath),
                            'fullPage': capture_full_page
                        })
                        
                        screenshots.append({
                            'device': size['name'],
                            'filename': filename,
                            'filepath': str(filepath),
                            'width': size['width'],
                            'height': size['height'],
                            'full_page': capture_full_page,
                            'file_size': os.path.getsize(filepath) if filepath.exists() else 0
                        })
                        
                        await page.close()
                        
                    except Exception as e:
                        print(f"خطأ في التقاط لقطة {size['name']}: {e}")
                        continue
                
                await browser.close()
                return screenshots
            
            # تشغيل الدالة الغير متزامنة
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            screenshots = loop.run_until_complete(capture_async())
            loop.close()
            
        except ImportError:
            raise Exception("Pyppeteer غير مثبت")
            
        return screenshots
    
    def _capture_simple(self, url: str, output_folder: Path) -> List[Dict[str, str]]:
        """طريقة مبسطة لالتقاط لقطة واحدة (تحتاج تطوير)"""
        # هذه طريقة مبسطة كبديل عندما لا تتوفر المحركات الأخرى
        # يمكن تطويرها لاحقاً باستخدام مكتبات أخرى أو API خارجي
        
        screenshots = []
        domain = urlparse(url).netloc.replace('.', '_')
        timestamp = int(time.time())
        filename = f"screenshot_{domain}_simple_{timestamp}.txt"
        filepath = output_folder / 'screenshots' / filename
        
        # إنشاء مجلد
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # ملف نصي كبديل
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"لقطة شاشة مبسطة لـ: {url}\n")
            f.write(f"التاريخ: {time.ctime()}\n")
            f.write("ملاحظة: لم يتم العثور على محرك لقطات شاشة متاح\n")
            f.write("لالتقاط لقطات شاشة حقيقية، يُرجى تثبيت:\n")
            f.write("- selenium\n- playwright\n- pyppeteer\n")
        
        screenshots.append({
            'device': 'simple',
            'filename': filename,
            'filepath': str(filepath),
            'width': 0,
            'height': 0,
            'full_page': False,
            'file_size': os.path.getsize(filepath),
            'note': 'ملف نصي - ليس لقطة شاشة حقيقية'
        })
        
        return screenshots
    
    def get_engine_status(self) -> Dict[str, Any]:
        """الحصول على حالة محركات لقطات الشاشة"""
        return {
            'supported_engines': self.supported_engines,
            'recommended_engine': self._select_best_engine(),
            'installation_commands': {
                'selenium': 'pip install selenium',
                'playwright': 'pip install playwright && playwright install',
                'pyppeteer': 'pip install pyppeteer',
                'requests_html': 'pip install requests-html'
            }
        }