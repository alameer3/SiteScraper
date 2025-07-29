#!/usr/bin/env python3
"""
اختبار استيراد المكتبات
"""
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    import flask
    print(f"✅ Flask installed: {flask.__version__}")
    from flask import Flask
    print("✅ Flask import successful")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")

try:
    import flask_sqlalchemy
    print(f"✅ SQLAlchemy installed: {flask_sqlalchemy.__version__}")
except ImportError as e:
    print(f"❌ SQLAlchemy import failed: {e}")

try:
    import requests
    print(f"✅ Requests installed: {requests.__version__}")
except ImportError as e:
    print(f"❌ Requests import failed: {e}")

try:
    import bs4
    print(f"✅ BeautifulSoup installed: {bs4.__version__}")
except ImportError as e:
    print(f"❌ BeautifulSoup import failed: {e}")

print("\nPython path:")
for path in sys.path:
    print(f"  {path}")