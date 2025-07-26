#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced AI-Powered Website Extractor
نظام استخراج المواقع المدعوم بالذكاء الاصطناعي المتقدم
"""

import logging
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import json

class EnhancedAIExtractor:
    """مستخرج مواقع محسن بالذكاء الاصطناعي"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # قوائم التحليل الذكي
        self.content_patterns = {
            'ecommerce': ['product', 'price', 'cart', 'buy', 'shop', 'store'],
            'news': ['article', 'news', 'headline', 'breaking', 'report'],
            'blog': ['post', 'author', 'comment', 'share', 'blog'],
            'portfolio': ['portfolio', 'work', 'project', 'gallery', 'showcase'],
            'education': ['course', 'lesson', 'learn', 'study', 'education'],
            'business': ['company', 'service', 'contact', 'about', 'team']
        }
        
        self.sentiment_keywords = {
            'positive': ['excellent', 'great', 'amazing', 'wonderful', 'رائع', 'ممتاز', 'جيد'],
            'negative': ['bad', 'terrible', 'awful', 'worst', 'سيء', 'فظيع', 'كريه'],
            'neutral': ['okay', 'normal', 'standard', 'usual', 'عادي', 'طبيعي']
        }

    def analyze_content_type(self, content: str, metadata: Dict) -> Dict[str, Any]:
        """تحليل نوع المحتوى بالذكاء الاصطناعي"""
        content_lower = content.lower()
        scores = {}
        
        for category, keywords in self.content_patterns.items():
            score = sum(content_lower.count(keyword) for keyword in keywords)
            scores[category] = score
        
        # تحديد النوع الأساسي
        primary_type = max(scores, key=scores.get) if scores else 'general'
        confidence = scores.get(primary_type, 0) / max(len(content.split()), 1) * 100
        
        return {
            'primary_type': primary_type,
            'confidence': min(confidence, 100),
            'scores': scores,
            'analysis_time': datetime.now().isoformat()
        }

    def extract_key_information(self, content: str) -> Dict[str, Any]:
        """استخراج المعلومات الأساسية ذكياً"""
        # استخراج الأرقام والأسعار
        prices = re.findall(r'\$\d+\.?\d*|\d+\s*(?:دولار|ريال|جنيه)', content)
        
        # استخراج التواريخ
        dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', content)
        
        # استخراج الإيميلات
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
        
        # استخراج أرقام الهواتف
        phones = re.findall(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', content)
        
        # استخراج الروابط
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        
        return {
            'prices': list(set(prices)),
            'dates': list(set(dates)),
            'emails': list(set(emails)),
            'phones': list(set(phones)),
            'urls': list(set(urls)),
            'extraction_count': {
                'prices': len(set(prices)),
                'dates': len(set(dates)),
                'emails': len(set(emails)),
                'phones': len(set(phones)),
                'urls': len(set(urls))
            }
        }

    def analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """تحليل المشاعر والنبرة"""
        content_lower = content.lower()
        sentiment_scores = {}
        
        for sentiment, keywords in self.sentiment_keywords.items():
            score = sum(content_lower.count(keyword) for keyword in keywords)
            sentiment_scores[sentiment] = score
        
        total_score = sum(sentiment_scores.values())
        if total_score == 0:
            return {
                'dominant_sentiment': 'neutral',
                'confidence': 0,
                'scores': sentiment_scores,
                'summary': 'لا يوجد مؤشرات واضحة للمشاعر'
            }
        
        # تحديد المشاعر السائدة
        dominant = max(sentiment_scores, key=sentiment_scores.get)
        confidence = (sentiment_scores[dominant] / total_score) * 100
        
        return {
            'dominant_sentiment': dominant,
            'confidence': confidence,
            'scores': sentiment_scores,
            'summary': f'النبرة السائدة: {dominant} بثقة {confidence:.1f}%'
        }

    def extract_keywords(self, content: str, max_keywords: int = 20) -> List[Dict[str, Any]]:
        """استخراج الكلمات المفتاحية الذكي"""
        # تنظيف النص
        words = re.findall(r'\b[a-zA-Zأ-ي]{3,}\b', content.lower())
        
        # حساب التكرارات
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # استبعاد الكلمات الشائعة
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                     'من', 'في', 'على', 'إلى', 'مع', 'هذا', 'هذه', 'ذلك', 'التي', 'الذي'}
        
        filtered_words = {word: freq for word, freq in word_freq.items() 
                         if word not in stop_words and freq > 1}
        
        # ترتيب بالتكرار
        sorted_words = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)
        
        keywords = []
        for word, freq in sorted_words[:max_keywords]:
            keywords.append({
                'word': word,
                'frequency': freq,
                'relevance_score': freq / len(words) * 100
            })
        
        return keywords

    def analyze_readability(self, content: str) -> Dict[str, Any]:
        """تحليل سهولة القراءة"""
        sentences = re.split(r'[.!?]+', content)
        words = content.split()
        
        if not sentences or not words:
            return {
                'score': 0,
                'level': 'غير محدد',
                'statistics': {}
            }
        
        # إحصائيات أساسية
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # حساب درجة سهولة القراءة (مبسط)
        readability_score = 100 - (avg_sentence_length * 1.5) - (avg_word_length * 2)
        readability_score = max(0, min(100, readability_score))
        
        # تحديد المستوى
        if readability_score >= 80:
            level = 'سهل جداً'
        elif readability_score >= 60:
            level = 'سهل'
        elif readability_score >= 40:
            level = 'متوسط'
        elif readability_score >= 20:
            level = 'صعب'
        else:
            level = 'صعب جداً'
        
        return {
            'score': round(readability_score, 1),
            'level': level,
            'statistics': {
                'total_words': len(words),
                'total_sentences': len(sentences),
                'avg_sentence_length': round(avg_sentence_length, 1),
                'avg_word_length': round(avg_word_length, 1)
            }
        }

    def smart_content_summary(self, content: str, max_sentences: int = 3) -> Dict[str, Any]:
        """تلخيص ذكي للمحتوى"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if len(sentences) <= max_sentences:
            return {
                'summary': ' '.join(sentences),
                'compression_ratio': 100,
                'original_sentences': len(sentences),
                'summary_sentences': len(sentences)
            }
        
        # تقييم أهمية الجمل (مبسط)
        sentence_scores = {}
        word_freq = {}
        
        # حساب تكرار الكلمات
        all_words = content.lower().split()
        for word in all_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # تقييم الجمل
        for i, sentence in enumerate(sentences):
            words = sentence.lower().split()
            score = sum(word_freq.get(word, 0) for word in words)
            # إضافة وزن للجمل الأولى والأخيرة
            if i < 2:
                score *= 1.5
            elif i >= len(sentences) - 2:
                score *= 1.3
            sentence_scores[sentence] = score
        
        # اختيار أفضل الجمل
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:max_sentences]
        
        # ترتيب حسب الظهور الأصلي
        summary_sentences = []
        for sentence in sentences:
            if any(sentence == s[0] for s in top_sentences):
                summary_sentences.append(sentence)
            if len(summary_sentences) >= max_sentences:
                break
        
        summary = ' '.join(summary_sentences)
        compression_ratio = (len(summary) / len(content)) * 100
        
        return {
            'summary': summary,
            'compression_ratio': round(compression_ratio, 1),
            'original_sentences': len(sentences),
            'summary_sentences': len(summary_sentences)
        }

    def comprehensive_ai_analysis(self, content: str, metadata: Dict = None) -> Dict[str, Any]:
        """تحليل شامل بالذكاء الاصطناعي"""
        if metadata is None:
            metadata = {}
        
        self.logger.info("بدء التحليل الشامل بالذكاء الاصطناعي")
        
        analysis_result = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'content_length': len(content),
                'analyzer_version': '2.0'
            }
        }
        
        try:
            # تحليل نوع المحتوى
            analysis_result['content_type'] = self.analyze_content_type(content, metadata)
            
            # استخراج المعلومات الأساسية
            analysis_result['key_information'] = self.extract_key_information(content)
            
            # تحليل المشاعر
            analysis_result['sentiment_analysis'] = self.analyze_sentiment(content)
            
            # استخراج الكلمات المفتاحية
            analysis_result['keywords'] = self.extract_keywords(content)
            
            # تحليل سهولة القراءة
            analysis_result['readability'] = self.analyze_readability(content)
            
            # تلخيص ذكي
            analysis_result['smart_summary'] = self.smart_content_summary(content)
            
            # تقييم شامل
            analysis_result['overall_assessment'] = self._generate_overall_assessment(analysis_result)
            
            self.logger.info("تم إكمال التحليل الشامل بنجاح")
            
        except Exception as e:
            self.logger.error(f"خطأ في التحليل الشامل: {e}")
            analysis_result['error'] = str(e)
        
        return analysis_result

    def _generate_overall_assessment(self, analysis: Dict) -> Dict[str, Any]:
        """إنشاء تقييم شامل للتحليل"""
        assessment = {
            'quality_score': 0,
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
        
        # تقييم جودة المحتوى
        readability_score = analysis.get('readability', {}).get('score', 0)
        keyword_count = len(analysis.get('keywords', []))
        content_length = analysis.get('analysis_metadata', {}).get('content_length', 0)
        
        quality_score = (readability_score * 0.4) + (min(keyword_count, 20) * 2.5) + (min(content_length / 100, 30))
        assessment['quality_score'] = min(100, max(0, quality_score))
        
        # نقاط القوة
        if readability_score >= 60:
            assessment['strengths'].append('محتوى سهل القراءة')
        if keyword_count >= 10:
            assessment['strengths'].append('ثراء في المفردات')
        if content_length >= 500:
            assessment['strengths'].append('محتوى شامل ومفصل')
        
        # نقاط الضعف
        if readability_score < 40:
            assessment['weaknesses'].append('صعوبة في القراءة')
        if keyword_count < 5:
            assessment['weaknesses'].append('محدودية في المفردات')
        if content_length < 200:
            assessment['weaknesses'].append('محتوى قصير')
        
        # التوصيات
        if readability_score < 50:
            assessment['recommendations'].append('تبسيط اللغة والجمل')
        if keyword_count < 10:
            assessment['recommendations'].append('إثراء المحتوى بمفردات متنوعة')
        
        return assessment