#!/usr/bin/env python3
"""
اختبار خاص للتعامل مع مواقع Cloudflare المحمية
"""

import requests
import cloudscraper
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path

def test_cloudflare_bypass():
    """اختبار تجاوز حماية Cloudflare"""
    url = "https://ak.sv/"
    
    print(f"🔄 اختبار تجاوز حماية Cloudflare للموقع: {url}")
    
    # محاولة 1: CloudScraper المتقدم
    try:
        print("1️⃣ محاولة CloudScraper...")
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        response = scraper.get(url, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Content length: {len(response.text)}")
        
        if "Just a moment" not in response.text:
            print("   ✅ نجح تجاوز الحماية!")
            return response
        else:
            print("   ⚠️ لا يزال محمي")
            
    except Exception as e:
        print(f"   ❌ CloudScraper فشل: {e}")
    
    # محاولة 2: استخراج ما يمكن من المحتوى المحمي
    try:
        print("2️⃣ استخراج المحتوى المحمي...")
        
        # حتى لو كان محمي، نحفظ ما نستطيع
        response = requests.get(url, verify=False, timeout=15)
        
        # إنشاء مجلد النتائج
        output_dir = Path("ak_sv_protected_content")
        output_dir.mkdir(exist_ok=True)
        
        # حفظ المحتوى الخام
        with open(output_dir / "raw_response.html", 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # تحليل ما يمكن تحليله
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # استخراج المعلومات الأساسية
        info = {
            'url': url,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'protection_detected': True,
            'protection_type': 'Cloudflare',
            'content_size': len(response.text),
            'title': soup.title.string if soup.title else 'No title',
            'meta_tags': [],
            'links': [],
            'scripts': []
        }
        
        # استخراج meta tags
        for meta in soup.find_all('meta'):
            meta_info = {}
            for attr in ['name', 'content', 'property', 'http-equiv']:
                if meta.get(attr):
                    meta_info[attr] = meta.get(attr)
            if meta_info:
                info['meta_tags'].append(meta_info)
        
        # استخراج الروابط
        for link in soup.find_all('a', href=True):
            info['links'].append(link['href'])
        
        # استخراج السكريبت
        for script in soup.find_all('script'):
            if script.get('src'):
                info['scripts'].append(script['src'])
        
        # حفظ المعلومات المستخرجة
        with open(output_dir / "extracted_info.json", 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ تم حفظ المعلومات في: {output_dir}")
        print(f"   📊 المعلومات المستخرجة:")
        print(f"      - العنوان: {info['title']}")
        print(f"      - حالة الاستجابة: {info['status_code']}")
        print(f"      - حجم المحتوى: {info['content_size']} حرف")
        print(f"      - عدد Meta tags: {len(info['meta_tags'])}")
        print(f"      - عدد الروابط: {len(info['links'])}")
        print(f"      - عدد السكريپت: {len(info['scripts'])}")
        
        return info
        
    except Exception as e:
        print(f"   ❌ فشل في الاستخراج: {e}")
        return None

if __name__ == "__main__":
    result = test_cloudflare_bypass()
    
    if result:
        print("\n🎯 الخلاصة:")
        print("تم استخراج ما يمكن استخراجه من الموقع المحمي")
        print("المحتوى محفوظ في مجلد ak_sv_protected_content")
    else:
        print("\n❌ فشل في استخراج أي محتوى")