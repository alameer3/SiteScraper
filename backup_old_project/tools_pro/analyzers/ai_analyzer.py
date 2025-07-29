"""
AI-Powered Website Analysis Module
Advanced artificial intelligence features for content analysis, sentiment analysis, and smart categorization.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from collections import Counter
import json

class AIAnalyzer:
    """Advanced AI-powered website analysis capabilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Keywords for different categories
        self.category_keywords = {
            'ecommerce': ['shop', 'buy', 'cart', 'price', 'product', 'store', 'checkout', 'payment'],
            'news': ['news', 'article', 'breaking', 'latest', 'report', 'journalist', 'media'],
            'blog': ['blog', 'post', 'author', 'comment', 'subscribe', 'archive'],
            'portfolio': ['portfolio', 'work', 'project', 'gallery', 'showcase', 'experience'],
            'business': ['services', 'company', 'about', 'contact', 'team', 'solutions'],
            'education': ['course', 'learn', 'study', 'education', 'university', 'school'],
            'entertainment': ['game', 'video', 'music', 'movie', 'fun', 'entertainment']
        }
        
        # Sentiment keywords
        self.positive_words = ['good', 'great', 'excellent', 'amazing', 'best', 'love', 'perfect', 'awesome']
        self.negative_words = ['bad', 'terrible', 'worst', 'hate', 'awful', 'horrible', 'disappointed']
    
    def analyze_content_with_ai(self, content: str, metadata: Dict) -> Dict[str, Any]:
        """Perform comprehensive AI analysis on website content."""
        try:
            analysis = {
                'content_category': self._categorize_content(content),
                'sentiment_analysis': self._analyze_sentiment(content),
                'keyword_extraction': self._extract_keywords(content),
                'content_quality': self._assess_content_quality(content),
                'readability_score': self._calculate_readability(content),
                'language_detection': self._detect_language(content),
                'topics': self._extract_topics(content),
                'entities': self._extract_entities(content)
            }
            
            # Add metadata analysis
            if metadata:
                analysis['metadata_insights'] = self._analyze_metadata(metadata)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return {'error': str(e)}
    
    def _categorize_content(self, content: str) -> Dict[str, Any]:
        """Categorize website content using AI-like keyword analysis."""
        content_lower = content.lower()
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = sum(content_lower.count(keyword) for keyword in keywords)
            if score > 0:
                category_scores[category] = score
        
        if not category_scores:
            return {'primary_category': 'general', 'confidence': 0.5, 'scores': {}}
        
        primary_category = max(category_scores.keys(), key=lambda x: category_scores[x])
        total_score = sum(category_scores.values())
        confidence = category_scores[primary_category] / total_score if total_score > 0 else 0
        
        return {
            'primary_category': primary_category,
            'confidence': min(confidence, 1.0),
            'scores': category_scores,
            'all_categories': list(category_scores.keys())
        }
    
    def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment of the content."""
        content_lower = content.lower()
        
        positive_count = sum(content_lower.count(word) for word in self.positive_words)
        negative_count = sum(content_lower.count(word) for word in self.negative_words)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            sentiment = 'neutral'
            score = 0.0
        elif positive_count > negative_count:
            sentiment = 'positive'
            score = positive_count / total_sentiment_words
        else:
            sentiment = 'negative'
            score = negative_count / total_sentiment_words
        
        return {
            'sentiment': sentiment,
            'score': score,
            'positive_indicators': positive_count,
            'negative_indicators': negative_count,
            'confidence': min(score * 2, 1.0) if score > 0 else 0.5
        }
    
    def _extract_keywords(self, content: str) -> Dict[str, Any]:
        """Extract important keywords from content."""
        # Clean and tokenize content
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Remove common stop words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequency
        word_freq = Counter(filtered_words)
        
        # Get top keywords
        top_keywords = word_freq.most_common(20)
        
        return {
            'top_keywords': top_keywords[:10],
            'all_keywords': dict(top_keywords),
            'total_unique_words': len(word_freq),
            'keyword_density': len(filtered_words) / max(len(words), 1) if words else 0
        }
    
    def _assess_content_quality(self, content: str) -> Dict[str, Any]:
        """Assess the quality of content."""
        words = content.split()
        sentences = content.split('.')
        
        # Basic quality metrics
        avg_words_per_sentence = len(words) / max(len(sentences), 1)
        unique_words = len(set(word.lower() for word in words if word.isalpha()))
        vocabulary_richness = unique_words / max(len(words), 1) if words else 0
        
        # Quality score calculation
        quality_factors = {
            'length_score': min(len(words) / 500, 1.0),  # Optimal around 500 words
            'sentence_structure': min(avg_words_per_sentence / 15, 1.0),  # Good around 15 words/sentence
            'vocabulary_diversity': vocabulary_richness,
            'formatting_score': self._assess_formatting(content)
        }
        
        overall_quality = sum(quality_factors.values()) / len(quality_factors)
        
        return {
            'overall_score': overall_quality,
            'quality_factors': quality_factors,
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_words_per_sentence': avg_words_per_sentence,
            'vocabulary_richness': vocabulary_richness,
            'quality_rating': self._get_quality_rating(overall_quality)
        }
    
    def _assess_formatting(self, content: str) -> float:
        """Assess content formatting quality."""
        formatting_score = 0.0
        
        # Check for headers
        if re.search(r'<h[1-6]', content, re.IGNORECASE):
            formatting_score += 0.3
        
        # Check for paragraphs
        if re.search(r'<p>', content, re.IGNORECASE):
            formatting_score += 0.2
        
        # Check for lists
        if re.search(r'<[uo]l>', content, re.IGNORECASE):
            formatting_score += 0.2
        
        # Check for line breaks
        if '\n' in content:
            formatting_score += 0.1
        
        # Check for proper punctuation
        if re.search(r'[.!?]', content):
            formatting_score += 0.2
        
        return min(formatting_score, 1.0)
    
    def _calculate_readability(self, content: str) -> Dict[str, Any]:
        """Calculate readability score (simplified Flesch-Kincaid)."""
        words = content.split()
        sentences = content.split('.')
        
        if not words or not sentences:
            return {'score': 0, 'level': 'Unknown', 'description': 'Insufficient content'}
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Simplified syllable count (estimate)
        syllables = sum(self._count_syllables(word) for word in words)
        avg_syllables_per_word = syllables / len(words)
        
        # Simplified Flesch Reading Ease formula
        readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        readability_score = max(0, min(100, readability_score))
        
        level = self._get_readability_level(readability_score)
        
        return {
            'score': round(readability_score, 2),
            'level': level,
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_syllables_per_word': round(avg_syllables_per_word, 2),
            'description': self._get_readability_description(level)
        }
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count in a word."""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_char_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_char_was_vowel:
                    syllable_count += 1
                prev_char_was_vowel = True
            else:
                prev_char_was_vowel = False
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _detect_language(self, content: str) -> Dict[str, Any]:
        """Simple language detection based on common words."""
        content_lower = content.lower()
        
        language_indicators = {
            'english': ['the', 'and', 'to', 'of', 'in', 'you', 'that', 'it', 'for', 'is'],
            'arabic': ['في', 'من', 'على', 'إلى', 'هذا', 'هذه', 'التي', 'الذي', 'كان', 'كانت'],
            'spanish': ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no'],
            'french': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir'],
            'german': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich']
        }
        
        language_scores = {}
        for language, indicators in language_indicators.items():
            score = sum(content_lower.count(indicator) for indicator in indicators)
            if score > 0:
                language_scores[language] = score
        
        if not language_scores:
            return {'detected_language': 'unknown', 'confidence': 0, 'scores': {}}
        
        detected_language = max(language_scores.keys(), key=lambda x: language_scores[x])
        total_score = sum(language_scores.values())
        confidence = language_scores[detected_language] / total_score if total_score > 0 else 0
        
        return {
            'detected_language': detected_language,
            'confidence': round(confidence, 3),
            'scores': language_scores,
            'alternative_languages': sorted(language_scores.keys(), key=lambda x: language_scores[x], reverse=True)[1:3]
        }
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract main topics from content."""
        # This is a simplified topic extraction
        # In a real scenario, you'd use more advanced NLP libraries
        
        topic_keywords = {
            'technology': ['tech', 'software', 'programming', 'computer', 'digital', 'internet', 'ai', 'machine'],
            'business': ['business', 'company', 'market', 'sales', 'profit', 'revenue', 'strategy'],
            'health': ['health', 'medical', 'doctor', 'medicine', 'wellness', 'fitness', 'nutrition'],
            'education': ['education', 'school', 'university', 'learning', 'student', 'teacher', 'knowledge'],
            'travel': ['travel', 'tourism', 'vacation', 'hotel', 'flight', 'destination', 'trip'],
            'food': ['food', 'recipe', 'cooking', 'restaurant', 'cuisine', 'meal', 'ingredients'],
            'sports': ['sport', 'game', 'team', 'player', 'match', 'championship', 'athlete'],
            'entertainment': ['movie', 'music', 'celebrity', 'entertainment', 'show', 'performance']
        }
        
        content_lower = content.lower()
        topic_scores = {}
        
        for topic, keywords in topic_keywords.items():
            score = sum(content_lower.count(keyword) for keyword in keywords)
            if score > 0:
                topic_scores[topic] = score
        
        # Return top 3 topics
        return sorted(topic_scores.keys(), key=lambda x: topic_scores[x], reverse=True)[:3]
    
    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract named entities (simplified approach)."""
        entities = {
            'organizations': [],
            'locations': [],
            'dates': [],
            'emails': [],
            'phones': [],
            'urls': []
        }
        
        # Extract emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
        entities['emails'] = list(set(emails))
        
        # Extract URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        entities['urls'] = list(set(urls))
        
        # Extract phone numbers (simple pattern)
        phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content)
        entities['phones'] = list(set(phones))
        
        # Extract dates (simple patterns)
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b', content)
        entities['dates'] = list(set(dates))
        
        return entities
    
    def _analyze_metadata(self, metadata: Dict) -> Dict[str, Any]:
        """Analyze website metadata for insights."""
        insights = {
            'seo_optimization': 0,
            'social_media_ready': False,
            'mobile_optimized': False,
            'security_indicators': [],
            'performance_hints': []
        }
        
        # Check SEO optimization
        if metadata.get('title'):
            insights['seo_optimization'] += 25
        if metadata.get('description'):
            insights['seo_optimization'] += 25
        if metadata.get('keywords'):
            insights['seo_optimization'] += 25
        if metadata.get('canonical_url'):
            insights['seo_optimization'] += 25
        
        # Check social media optimization
        og_tags = [key for key in metadata.keys() if key.startswith('og:')]
        twitter_tags = [key for key in metadata.keys() if key.startswith('twitter:')]
        insights['social_media_ready'] = len(og_tags) > 2 or len(twitter_tags) > 2
        
        # Check mobile optimization
        viewport = metadata.get('viewport', '')
        insights['mobile_optimized'] = 'width=device-width' in viewport
        
        # Security indicators
        if 'https' in metadata.get('canonical_url', ''):
            insights['security_indicators'].append('HTTPS enabled')
        
        return insights
    
    def _get_quality_rating(self, score: float) -> str:
        """Convert quality score to rating."""
        if score >= 0.8:
            return 'Excellent'
        elif score >= 0.6:
            return 'Good'
        elif score >= 0.4:
            return 'Fair'
        else:
            return 'Poor'
    
    def _get_readability_level(self, score: float) -> str:
        """Convert readability score to level."""
        if score >= 90:
            return 'Very Easy'
        elif score >= 80:
            return 'Easy'
        elif score >= 70:
            return 'Fairly Easy'
        elif score >= 60:
            return 'Standard'
        elif score >= 50:
            return 'Fairly Difficult'
        elif score >= 30:
            return 'Difficult'
        else:
            return 'Very Difficult'
    
    def _get_readability_description(self, level: str) -> str:
        """Get description for readability level."""
        descriptions = {
            'Very Easy': 'Easily understood by 11-year-olds',
            'Easy': 'Easily understood by 12-13 year-olds',
            'Fairly Easy': 'Easily understood by 14-15 year-olds',
            'Standard': 'Easily understood by 16-17 year-olds',
            'Fairly Difficult': 'Understood by college-level readers',
            'Difficult': 'Understood by college graduates',
            'Very Difficult': 'Understood by university graduates'
        }
        return descriptions.get(level, 'Unknown reading level')