"""
Flask Routes for Website Cloner Pro Integration
صفحات ويب لأداة Website Cloner Pro
"""

from flask import render_template, request, jsonify, flash, redirect, url_for
import asyncio
import logging
import json
import os
from datetime import datetime
import threading

# Import Website Cloner Integration
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.extractors.website_cloner_integration import create_integrated_extractor
from website_cloner_pro import WebsiteClonerPro, CloningConfig

def register_cloner_routes(app):
    """تسجيل routes الخاصة بـ Website Cloner Pro"""
    
    @app.route('/website-cloner')
    def website_cloner_page():
        """صفحة أداة نسخ المواقع"""
        return render_template('pages/website_cloner.html')
    
    @app.route('/website-cloner/integrated')
    def integrated_cloner_page():
        """صفحة الأداة المتكاملة"""
        return render_template('pages/integrated_cloner.html')
    
    @app.route('/website-cloner/comparison')
    def cloner_comparison_page():
        """صفحة مقارنة الأدوات"""
        return render_template('pages/cloner_comparison.html')
    
    # API Routes will be handled by the separate API blueprint
    
    return app