"""
محلل الذكاء الاصطناعي البسيط
Basic AI Content Analyzer
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
from bs4 import BeautifulSoup, Tag


class BasicAIAnalyzer:
    """محلل ذكي بسيط للمحتوى (بدون APIs خارجية)"""
    
    def __init__(self):
        self.sentiment_words = self._load_sentiment_lexicon()
        self.category_keywords = self._load_category_keywords()
        
    def _load_sentiment_lexicon(self) -> Dict[str, List[str]]:
        """تحميل معجم المشاعر الأساسي"""
        return {
            'positive': [
                'ممتاز', 'رائع', 'جيد', 'مذهل', 'عظيم', 'سعيد', 'جميل', 'مفيد',
                'excellent', 'amazing', 'great', 'good', 'wonderful', 'happy',
                'beautiful', 'useful', 'perfect', 'best', 'love', 'awesome'
            ],
            'negative': [
                'سيئ', 'فظيع', 'مروع', 'حزين', 'غاضب', 'مؤلم', 'صعب',
                'bad', 'terrible', 'awful', 'sad', 'angry', 'painful', 'difficult',
                'hate', 'worst', 'horrible', 'disgusting', 'annoying', 'boring'
            ],
            'neutral': [
                'عادي', 'طبيعي', 'متوسط', 'محايد',
                'normal', 'average', 'neutral', 'regular', 'standard', 'typical'
            ]
        }
    
    def _load_category_keywords(self) -> Dict[str, List[str]]:
        """تحميل كلمات مفتاحية للتصنيفات"""
        return {
            'technology': [
                'تقنية', 'تكنولوجيا', 'برمجة', 'كمبيوتر', 'ذكي', 'رقمي',
                'technology', 'programming', 'computer', 'software', 'digital',
                'ai', 'machine learning', 'blockchain', 'cloud', 'app', 'api'
            ],
            'business': [
                'أعمال', 'تجارة', 'شركة', 'استثمار', 'مال', 'ربح', 'مبيعات',
                'business', 'company', 'investment', 'money', 'profit', 'sales',
                'market', 'finance', 'startup', 'entrepreneur', 'revenue'
            ],
            'education': [
                'تعليم', 'تعلم', 'دراسة', 'مدرسة', 'جامعة', 'كتاب', 'درس',
                'education', 'learning', 'study', 'school', 'university', 'course',
                'tutorial', 'lesson', 'knowledge', 'research', 'academic'
            ],
            'health': [
                'صحة', 'طب', 'علاج', 'مرض', 'دواء', 'طبيب', 'مستشفى',
                'health', 'medical', 'treatment', 'disease', 'medicine', 'doctor',
                'hospital', 'wellness', 'fitness', 'nutrition', 'therapy'
            ],
            'news': [
                'أخبار', 'جديد', 'حدث', 'تطور', 'تحديث', 'عاجل',
                'news', 'breaking', 'update', 'latest', 'recent', 'current',
                'event', 'happening', 'development', 'announcement'
            ],
            'entertainment': [
                'ترفيه', 'فيلم', 'موسيقى', 'لعبة', 'رياضة', 'فن',
                'entertainment', 'movie', 'music', 'game', 'sport', 'art',
                'fun', 'comedy', 'drama', 'celebrity', 'show', 'performance'
            ],
            'shopping': [
                'تسوق', 'شراء', 'بيع', 'متجر', 'سعر', 'عرض', 'خصم',
                'shopping', 'buy', 'sell', 'store', 'price', 'discount',
                'product', 'offer', 'deal', 'cart', 'checkout', 'payment'
            ]
        }
    
    def analyze_content(self, soup: BeautifulSoup, url: str, content: str) -> Dict[str, Any]:
        """تحليل شامل للمحتوى"""
        
        analysis_result = {
            'content_analysis': {},
            'sentiment_analysis': {},
            'category_classification': {},
            'text_statistics': {},
            'content_quality': {},
            'readability_score': 0,
            'language_detection': {}
        }
        
        # استخراج النصوص
        text_content = self._extract_text_content(soup)
        
        # 1. تحليل المشاعر
        sentiment = self._analyze_sentiment(text_content)
        analysis_result['sentiment_analysis'] = sentiment
        
        # 2. تصنيف المحتوى
        categories = self._classify_content(text_content)
        analysis_result['category_classification'] = categories
        
        # 3. إحصائيات النص
        statistics = self._calculate_text_statistics(text_content)
        analysis_result['text_statistics'] = statistics
        
        # 4. تقييم جودة المحتوى
        quality = self._assess_content_quality(soup, text_content)
        analysis_result['content_quality'] = quality
        
        # 5. نقاط القابلية للقراءة
        readability = self._calculate_readability(text_content)
        analysis_result['readability_score'] = readability
        
        # 6. اكتشاف اللغة
        language = self._detect_language(text_content)
        analysis_result['language_detection'] = language
        
        # 7. تحليل الهيكل
        structure = self._analyze_content_structure(soup)
        analysis_result['content_structure'] = structure
        
        return analysis_result
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """استخراج النص الرئيسي من الصفحة"""
        
        # إزالة العناصر غير المرغوبة
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # استخراج النص من العناصر الرئيسية
        main_content = []
        
        # البحث عن المحتوى الرئيسي
        main_selectors = ['main', 'article', '.content', '.post', '.entry', '#content']
        for selector in main_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    text = element.get_text(separator=' ', strip=True)
                    if len(text) > 100:  # تجاهل النصوص القصيرة
                        main_content.append(text)
                break
        
        # إذا لم نجد محتوى رئيسي، استخدم body
        if not main_content:
            body = soup.find('body')
            if body:
                main_content.append(body.get_text(separator=' ', strip=True))
        
        return ' '.join(main_content)
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """تحليل المشاعر في النص"""
        
        text_lower = text.lower()
        sentiment_scores = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for sentiment, words in self.sentiment_words.items():
            for word in words:
                count = text_lower.count(word.lower())
                sentiment_scores[sentiment] += count
        
        total_sentiment_words = sum(sentiment_scores.values())
        
        if total_sentiment_words == 0:
            dominant_sentiment = 'neutral'
            confidence = 0
        else:
            dominant_sentiment = max(sentiment_scores.items(), key=lambda x: x[1])[0]
            confidence = (sentiment_scores[dominant_sentiment] / total_sentiment_words) * 100
        
        return {
            'dominant_sentiment': dominant_sentiment,
            'confidence': round(confidence, 2),
            'sentiment_breakdown': {
                'positive': round((sentiment_scores['positive'] / max(total_sentiment_words, 1)) * 100, 2),
                'negative': round((sentiment_scores['negative'] / max(total_sentiment_words, 1)) * 100, 2),
                'neutral': round((sentiment_scores['neutral'] / max(total_sentiment_words, 1)) * 100, 2)
            },
            'total_sentiment_words': total_sentiment_words
        }
    
    def _classify_content(self, text: str) -> Dict[str, Any]:
        """تصنيف المحتوى حسب الموضوع"""
        
        text_lower = text.lower()
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            found_keywords = []
            
            for keyword in keywords:
                count = text_lower.count(keyword.lower())
                if count > 0:
                    score += count
                    found_keywords.append(keyword)
            
            if score > 0:
                category_scores[category] = {
                    'score': score,
                    'keywords_found': found_keywords,
                    'relevance': min(score * 5, 100)  # تحويل إلى نسبة مئوية
                }
        
        # ترتيب حسب النتيجة
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        primary_category = sorted_categories[0][0] if sorted_categories else 'general'
        
        return {
            'primary_category': primary_category,
            'all_categories': dict(sorted_categories),
            'category_count': len(category_scores),
            'confidence': category_scores.get(primary_category, {}).get('relevance', 0)
        }
    
    def _calculate_text_statistics(self, text: str) -> Dict[str, Any]:
        """حساب إحصائيات النص"""
        
        # تقسيم النص
        words = re.findall(r'\b\w+\b', text.lower())
        sentences = re.split(r'[.!?]+', text)
        paragraphs = text.split('\n\n')
        
        # إحصائيات أساسية
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        paragraph_count = len([p for p in paragraphs if p.strip()])
        char_count = len(text)
        
        # متوسطات
        avg_words_per_sentence = word_count / max(sentence_count, 1)
        avg_chars_per_word = char_count / max(word_count, 1)
        
        # الكلمات الأكثر شيوعاً
        word_frequency = Counter(words)
        most_common_words = word_frequency.most_common(10)
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count,
            'character_count': char_count,
            'average_words_per_sentence': round(avg_words_per_sentence, 2),
            'average_characters_per_word': round(avg_chars_per_word, 2),
            'most_common_words': most_common_words,
            'unique_words': len(word_frequency),
            'lexical_diversity': round(len(word_frequency) / max(word_count, 1), 2)
        }
    
    def _assess_content_quality(self, soup: BeautifulSoup, text: str) -> Dict[str, Any]:
        """تقييم جودة المحتوى"""
        
        quality_score = 0
        issues = []
        strengths = []
        
        # طول المحتوى
        word_count = len(text.split())
        if word_count > 300:
            quality_score += 20
            strengths.append("محتوى طويل ومفصل")
        elif word_count < 100:
            issues.append("محتوى قصير جداً")
        else:
            quality_score += 10
        
        # وجود عناوين
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if headings:
            quality_score += 15
            strengths.append(f"يحتوي على {len(headings)} عنوان")
        else:
            issues.append("لا توجد عناوين تنظيمية")
        
        # وجود قوائم
        lists = soup.find_all(['ul', 'ol'])
        if lists:
            quality_score += 10
            strengths.append("يحتوي على قوائم منظمة")
        
        # وجود روابط
        links = soup.find_all('a', href=True)
        if len(links) > 5:
            quality_score += 10
            strengths.append("يحتوي على روابط مفيدة")
        elif len(links) == 0:
            issues.append("لا توجد روابط")
        
        # وجود صور
        images = soup.find_all('img')
        if images:
            quality_score += 10
            strengths.append("يحتوي على صور")
        
        # تنوع النص
        unique_words = len(set(text.lower().split()))
        total_words = len(text.split())
        diversity = unique_words / max(total_words, 1)
        
        if diversity > 0.7:
            quality_score += 15
            strengths.append("تنوع عالي في المفردات")
        elif diversity < 0.3:
            issues.append("تكرار مفرط في المفردات")
        
        # تقييم نهائي
        if quality_score >= 70:
            grade = 'A'
        elif quality_score >= 50:
            grade = 'B'
        elif quality_score >= 30:
            grade = 'C'
        else:
            grade = 'D'
        
        return {
            'quality_score': min(quality_score, 100),
            'grade': grade,
            'strengths': strengths,
            'issues': issues,
            'recommendations': self._generate_content_recommendations(issues, word_count)
        }
    
    def _calculate_readability(self, text: str) -> float:
        """حساب سهولة القراءة (Flesch Reading Ease مبسط)"""
        
        words = re.findall(r'\b\w+\b', text)
        sentences = re.split(r'[.!?]+', text)
        
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        
        if sentence_count == 0:
            return 0
        
        # حساب متوسط طول الكلمة (كمؤشر على الصعوبة)
        avg_word_length = sum(len(word) for word in words) / max(word_count, 1)
        avg_sentence_length = word_count / sentence_count
        
        # تركيبة مبسطة لحساب سهولة القراءة
        readability = 100 - (avg_word_length * 10) - (avg_sentence_length * 0.5)
        
        return max(0, min(readability, 100))
    
    def _detect_language(self, text: str) -> Dict[str, Any]:
        """اكتشاف لغة النص (مبسط)"""
        
        # عينة من الكلمات الشائعة
        language_indicators = {
            'arabic': ['في', 'من', 'إلى', 'على', 'هذا', 'التي', 'أن', 'كان', 'يتم', 'لقد'],
            'english': ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had'],
            'french': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir'],
            'spanish': ['de', 'la', 'que', 'el', 'en', 'y', 'a', 'es', 'se', 'no'],
            'german': ['der', 'die', 'und', 'zu', 'den', 'das', 'nicht', 'von', 'sie', 'ist']
        }
        
        text_lower = text.lower()
        language_scores = {}
        
        for lang, indicators in language_indicators.items():
            score = sum(text_lower.count(word) for word in indicators)
            if score > 0:
                language_scores[lang] = score
        
        if not language_scores:
            return {'detected_language': 'unknown', 'confidence': 0}
        
        detected_lang = max(language_scores.items(), key=lambda x: x[1])[0]
        total_indicators = sum(language_scores.values())
        confidence = (language_scores[detected_lang] / total_indicators) * 100
        
        return {
            'detected_language': detected_lang,
            'confidence': round(confidence, 2),
            'language_scores': language_scores
        }
    
    def _analyze_content_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """تحليل هيكل المحتوى"""
        
        structure = {
            'heading_hierarchy': [],
            'content_sections': 0,
            'navigation_elements': 0,
            'interactive_elements': 0,
            'media_elements': 0
        }
        
        # تحليل العناوين
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for heading in headings:
            if isinstance(heading, Tag):
                structure['heading_hierarchy'].append({
                    'level': int(heading.name[1]),
                    'text': heading.get_text().strip()[:50],
                    'length': len(heading.get_text().strip())
                })
        
        # عد الأقسام
        sections = soup.find_all(['section', 'article', 'div'])
        structure['content_sections'] = len([s for s in sections if isinstance(s, Tag)])
        
        # عناصر التنقل
        nav_elements = soup.find_all(['nav', 'menu'])
        structure['navigation_elements'] = len(nav_elements)
        
        # عناصر تفاعلية
        interactive = soup.find_all(['button', 'input', 'select', 'textarea', 'form'])
        structure['interactive_elements'] = len(interactive)
        
        # عناصر الوسائط
        media = soup.find_all(['img', 'video', 'audio', 'iframe'])
        structure['media_elements'] = len(media)
        
        return structure
    
    def _generate_content_recommendations(self, issues: List[str], word_count: int) -> List[str]:
        """توليد توصيات لتحسين المحتوى"""
        recommendations = []
        
        if word_count < 300:
            recommendations.append("أضف المزيد من التفاصيل والشرح")
        
        if "لا توجد عناوين تنظيمية" in issues:
            recommendations.append("أضف عناوين فرعية لتنظيم المحتوى")
        
        if "لا توجد روابط" in issues:
            recommendations.append("أضف روابط لمصادر موثوقة")
        
        if "تكرار مفرط في المفردات" in issues:
            recommendations.append("استخدم مفردات أكثر تنوعاً")
        
        # توصيات عامة
        recommendations.extend([
            "استخدم فقرات قصيرة لسهولة القراءة",
            "أضف قوائم نقطية للمعلومات المهمة",
            "تأكد من صحة القواعد النحوية والإملائية"
        ])
        
        return recommendations[:5]  # أول 5 توصيات