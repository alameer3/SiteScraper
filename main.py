#!/usr/bin/env python3
"""
نقطة دخول التطبيق الرئيسية - أداة استخراج المواقع
"""
import sys
import os

# Add current directory to path to import working_extractor
sys.path.insert(0, os.path.dirname(__file__))

# Import and run the working extractor
from working_extractor import main

if __name__ == '__main__':
    main()