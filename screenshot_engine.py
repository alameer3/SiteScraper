#!/usr/bin/env python3
"""
محرك لقطات الشاشة التلقائية للمواقع
"""
import os
import asyncio
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Any
import base64
import json

class ScreenshotEngine:
    """محرك لقطات الشاشة المتقدم"""
    
    def __init__(self, output_dir: str = "extracted_files"):
        self.output_dir = Path(output_dir)
        self.screenshots_taken = 0
        self.failed_screenshots = 0
        self.supported_sizes = {
            'desktop': {'width': 1920, 'height': 1080},
            'tablet': {'width': 768, 'height': 1024},
            'mobile': {'width': 375, 'height': 667}
        }
        
    async def capture_website_screenshots(self, url: str, extraction_folder: Path, 
                                        capture_responsive: bool = True,
                                        capture_interactions: bool = False) -> Dict[str, Any]:
        """التقاط لقطات شاشة شاملة للموقع"""
        
        results = {
            'total_screenshots': 0,
            'successful_screenshots': 0,
            'failed_screenshots': 0,
            'screenshot_files': [],
            'responsive_views': [],
            'page_analysis': {},
            'capture_timestamp': datetime.now().isoformat()
        }
        
        # إنشاء مجلد لقطات الشاشة
        screenshots_dir = extraction_folder / '05_screenshots'
        screenshots_dir.mkdir(exist_ok=True)
        
        try:
            # فحص توفر playwright
            try:
                from playwright.async_api import async_playwright
                playwright_available = True
            except ImportError:
                playwright_available = False
                
            if playwright_available:
                results.update(await self._capture_with_playwright(
                    url, screenshots_dir, capture_responsive, capture_interactions
                ))
            else:
                # استخدام selenium كبديل
                results.update(await self._capture_with_selenium(
                    url, screenshots_dir, capture_responsive
                ))
                
        except Exception as e:
            results['error'] = str(e)
            results['fallback_method'] = 'basic_screenshot'
            # محاولة التقاط بطريقة أساسية
            results.update(await self._basic_screenshot_capture(url, screenshots_dir))
            
        return results
    
    async def _capture_with_playwright(self, url: str, screenshots_dir: Path, 
                                     capture_responsive: bool, 
                                     capture_interactions: bool) -> Dict[str, Any]:
        """التقاط باستخدام Playwright"""
        from playwright.async_api import async_playwright
        
        results = {
            'method': 'playwright',
            'screenshot_files': [],
            'responsive_views': [],
            'page_analysis': {}
        }
        
        async with async_playwright() as p:
            # استخدام Chromium للحصول على أفضل دعم
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            try:
                page = await browser.new_page()
                
                # تعطيل الصور والخطوط لتسريع التحميل (اختياري)
                # await page.route("**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2}", lambda route: route.abort())
                
                # تحميل الصفحة
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(2000)  # انتظار إضافي للمحتوى الديناميكي
                
                # تحليل الصفحة
                page_info = await self._analyze_page(page)
                results['page_analysis'] = page_info
                
                # التقاط الشاشة الأساسية (سطح المكتب)
                desktop_file = screenshots_dir / f"desktop_{int(time.time())}.png"
                await page.set_viewport_size(width=self.supported_sizes['desktop']['width'], height=self.supported_sizes['desktop']['height'])
                await page.screenshot(path=str(desktop_file), full_page=True)
                results['screenshot_files'].append({
                    'type': 'desktop',
                    'file': str(desktop_file.name),
                    'size': self.supported_sizes['desktop'],
                    'full_page': True
                })
                
                if capture_responsive:
                    # التقاط لقطات متجاوبة
                    for device_name, size in self.supported_sizes.items():
                        if device_name == 'desktop':
                            continue
                            
                        await page.set_viewport_size(width=size['width'], height=size['height'])
                        await page.wait_for_timeout(1000)  # انتظار إعادة التخطيط
                        
                        device_file = screenshots_dir / f"{device_name}_{int(time.time())}.png"
                        await page.screenshot(path=str(device_file), full_page=True)
                        
                        results['responsive_views'].append({
                            'device': device_name,
                            'file': str(device_file.name),
                            'size': size,
                            'full_page': True
                        })
                
                if capture_interactions:
                    # التقاط لقطات للتفاعلات
                    interaction_results = await self._capture_interactions(page, screenshots_dir)
                    results['interactions'] = interaction_results
                
                # التقاط لقطة للجزء المرئي فقط (above fold)
                await page.set_viewport_size(width=self.supported_sizes['desktop']['width'], height=self.supported_sizes['desktop']['height'])
                fold_file = screenshots_dir / f"above_fold_{int(time.time())}.png"
                await page.screenshot(path=str(fold_file), full_page=False)
                results['screenshot_files'].append({
                    'type': 'above_fold',
                    'file': str(fold_file.name),
                    'size': self.supported_sizes['desktop'],
                    'full_page': False
                })
                
            finally:
                await browser.close()
                
        results['successful_screenshots'] = len(results['screenshot_files']) + len(results['responsive_views'])
        results['total_screenshots'] = results['successful_screenshots']
        
        return results
    
    async def _capture_with_selenium(self, url: str, screenshots_dir: Path, 
                                   capture_responsive: bool) -> Dict[str, Any]:
        """التقاط باستخدام Selenium كبديل"""
        results = {
            'method': 'selenium',
            'screenshot_files': [],
            'responsive_views': []
        }
        
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
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # تعيين حجم النافذة للسطح المكتب
                driver.set_window_size(
                    self.supported_sizes['desktop']['width'],
                    self.supported_sizes['desktop']['height']
                )
                
                # تحميل الصفحة
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                time.sleep(2)  # انتظار إضافي
                
                # التقاط الشاشة الأساسية
                desktop_file = screenshots_dir / f"desktop_selenium_{int(time.time())}.png"
                driver.save_screenshot(str(desktop_file))
                results['screenshot_files'].append({
                    'type': 'desktop',
                    'file': str(desktop_file.name),
                    'method': 'selenium'
                })
                
                if capture_responsive:
                    # التقاط لقطات متجاوبة
                    for device_name, size in self.supported_sizes.items():
                        if device_name == 'desktop':
                            continue
                            
                        driver.set_window_size(size['width'], size['height'])
                        time.sleep(1)
                        
                        device_file = screenshots_dir / f"{device_name}_selenium_{int(time.time())}.png"
                        driver.save_screenshot(str(device_file))
                        
                        results['responsive_views'].append({
                            'device': device_name,
                            'file': str(device_file.name),
                            'method': 'selenium'
                        })
                        
            finally:
                driver.quit()
                
        except Exception as e:
            results['error'] = str(e)
            
        results['successful_screenshots'] = len(results['screenshot_files']) + len(results['responsive_views'])
        results['total_screenshots'] = results['successful_screenshots']
        
        return results
    
    async def _basic_screenshot_capture(self, url: str, screenshots_dir: Path) -> Dict[str, Any]:
        """التقاط أساسي باستخدام مكتبات Python البسيطة"""
        results = {
            'method': 'basic',
            'screenshot_files': [],
            'note': 'استخدام التقاط أساسي - قد تكون الجودة محدودة'
        }
        
        # يمكن هنا استخدام مكتبات مثل pyautogui أو مكتبات أخرى
        # لكن هذا يتطلب تثبيت مكتبات إضافية
        
        results['successful_screenshots'] = 0
        results['total_screenshots'] = 0
        
        return results
    
    async def _analyze_page(self, page) -> Dict[str, Any]:
        """تحليل الصفحة للحصول على معلومات إضافية"""
        try:
            analysis = {}
            
            # الحصول على العنوان
            analysis['title'] = await page.title()
            
            # الحصول على الأبعاد
            analysis['viewport'] = await page.evaluate('() => ({ width: window.innerWidth, height: window.innerHeight })')
            analysis['document_size'] = await page.evaluate('() => ({ width: document.body.scrollWidth, height: document.body.scrollHeight })')
            
            # فحص العناصر المرئية
            analysis['visible_images'] = await page.evaluate('() => document.querySelectorAll("img:not([style*=\\"display: none\\"])").length')
            analysis['visible_links'] = await page.evaluate('() => document.querySelectorAll("a").length')
            
            # فحص التقنيات المستخدمة
            analysis['has_react'] = await page.evaluate('() => !!window.React')
            analysis['has_vue'] = await page.evaluate('() => !!window.Vue')
            analysis['has_angular'] = await page.evaluate('() => !!window.angular || !!window.ng')
            analysis['has_jquery'] = await page.evaluate('() => !!window.jQuery || !!window.$')
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _capture_interactions(self, page, screenshots_dir: Path) -> List[Dict[str, Any]]:
        """التقاط لقطات للتفاعلات (buttons, forms, etc.)"""
        interactions = []
        
        try:
            # البحث عن الأزرار
            buttons = await page.query_selector_all('button, input[type="submit"], .btn, [role="button"]')
            
            for i, button in enumerate(buttons[:5]):  # أقصى 5 أزرار
                try:
                    # التمرير إلى الزر
                    await button.scroll_into_view_if_needed()
                    await page.wait_for_timeout(500)
                    
                    # تمييز الزر
                    await page.evaluate('(element) => element.style.outline = "3px solid red"', button)
                    
                    # التقاط لقطة
                    interaction_file = screenshots_dir / f"button_{i}_{int(time.time())}.png"
                    await page.screenshot(path=str(interaction_file))
                    
                    # إزالة التمييز
                    await page.evaluate('(element) => element.style.outline = ""', button)
                    
                    interactions.append({
                        'type': 'button',
                        'index': i,
                        'file': str(interaction_file.name)
                    })
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            pass
            
        return interactions
    
    def create_screenshot_report(self, results: Dict[str, Any], extraction_folder: Path) -> str:
        """إنشاء تقرير لقطات الشاشة"""
        report_file = extraction_folder / '05_screenshots' / 'screenshot_report.json'
        
        # إضافة إحصائيات
        report_data = {
            'extraction_info': results,
            'summary': {
                'total_screenshots': results.get('total_screenshots', 0),
                'successful_screenshots': results.get('successful_screenshots', 0),
                'failed_screenshots': results.get('failed_screenshots', 0),
                'method_used': results.get('method', 'unknown'),
                'capture_timestamp': results.get('capture_timestamp'),
                'responsive_support': len(results.get('responsive_views', [])) > 0,
                'interaction_support': 'interactions' in results
            },
            'files': {
                'desktop_screenshots': results.get('screenshot_files', []),
                'responsive_screenshots': results.get('responsive_views', []),
                'interaction_screenshots': results.get('interactions', [])
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
            
        return str(report_file)