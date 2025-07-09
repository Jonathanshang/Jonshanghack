"""
Social Media Scraping Module for Competitive Analysis

This module provides specialized scrapers for different social media platforms
and review sites. It handles dynamic content, implements anti-bot measures,
and provides respectful crawling with rate limiting.

Supported Platforms:
- Facebook
- Twitter/X
- YouTube
- Instagram
- LinkedIn
- Reddit
- G2
- Capterra
- TrustPilot
- GetApp
- Software Advice
"""

import logging
import re
import time
import random
import json
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
import hashlib

# Try to import Selenium, make it optional
try:
    from selenium import webdriver  # type: ignore
    from selenium.webdriver.common.by import By  # type: ignore
    from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
    from selenium.webdriver.support import expected_conditions as EC  # type: ignore
    from selenium.webdriver.chrome.options import Options  # type: ignore
    from selenium.common.exceptions import TimeoutException, WebDriverException  # type: ignore
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    # Create dummy classes for type hints when Selenium is not available
    webdriver = None  # type: ignore
    By = None  # type: ignore
    WebDriverWait = None  # type: ignore
    EC = None  # type: ignore
    
    class Options:  # type: ignore
        def add_argument(self, arg):
            pass
        def add_experimental_option(self, option, value):
            pass
    
    class TimeoutException(Exception):  # type: ignore
        pass
    
    class WebDriverException(Exception):  # type: ignore
        pass

from .scraper import WebScraper
from .country_localization import country_localization
from .logger import log_execution_time, log_function_call

class SocialMediaScraperBase:
    """
    Base class for social media scrapers with common functionality
    """
    
    def __init__(self, config=None):
        """
        Initialize base social media scraper
        
        Args:
            config: Configuration object with scraping parameters
        """
        self.config = config
        self.logger = logging.getLogger("competitive_analysis")
        
        # Common scraping parameters
        self.request_delay = getattr(config, 'social_media_delay', 3.0)
        self.max_retries = getattr(config, 'max_retries', 3)
        self.timeout = getattr(config, 'request_timeout', 30)
        self.use_selenium = getattr(config, 'use_selenium', False) and SELENIUM_AVAILABLE
        
        # Log Selenium availability
        if not SELENIUM_AVAILABLE:
            self.logger.warning("Selenium not available. JavaScript-heavy sites may not work properly.")
            self.use_selenium = False
        
        # Initialize basic scraper
        self.scraper = WebScraper(config)
        
        # Selenium driver (initialized when needed)
        self.driver = None
        self.driver_options = None
        
        # Anti-bot measures
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        # Rate limiting tracking
        self.last_request_time = {}
        self.request_count = {}
        
        # Content cache
        self.content_cache = {}
        self.cache_duration = 3600  # 1 hour
    
    def _setup_selenium_driver(self) -> bool:
        """
        Set up Selenium Chrome driver with anti-detection measures
        
        Returns:
            True if driver setup successful, False otherwise
        """
        if not SELENIUM_AVAILABLE:
            self.logger.error("Selenium not available. Cannot set up driver.")
            return False
            
        try:
            # Chrome options for anti-detection
            self.driver_options = Options()
            self.driver_options.add_argument('--no-sandbox')
            self.driver_options.add_argument('--disable-dev-shm-usage')
            self.driver_options.add_argument('--disable-blink-features=AutomationControlled')
            self.driver_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            self.driver_options.add_experimental_option('useAutomationExtension', False)
            self.driver_options.add_argument('--disable-extensions')
            self.driver_options.add_argument('--disable-plugins')
            self.driver_options.add_argument('--disable-images')
            self.driver_options.add_argument('--disable-javascript')
            self.driver_options.add_argument(f'--user-agent={random.choice(self.user_agents)}')
            
            # Headless mode for production
            if getattr(self.config, 'headless_browser', True):
                self.driver_options.add_argument('--headless')
            
            # Initialize driver
            self.driver = webdriver.Chrome(options=self.driver_options)  # type: ignore
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")  # type: ignore
            
            self.logger.info("Selenium driver initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup Selenium driver: {str(e)}")
            return False
    
    def _rate_limit(self, platform: str):
        """
        Implement platform-specific rate limiting
        
        Args:
            platform: Platform name for rate limiting
        """
        now = time.time()
        
        # Platform-specific delays
        platform_delays = {
            'facebook': 5.0,
            'twitter': 3.0,
            'youtube': 2.0,
            'instagram': 4.0,
            'linkedin': 3.0,
            'reddit': 2.0,
            'g2': 2.0,
            'capterra': 2.0,
            'trustpilot': 2.0
        }
        
        delay = platform_delays.get(platform.lower(), self.request_delay)
        
        # Check if we need to wait
        if platform in self.last_request_time:
            elapsed = now - self.last_request_time[platform]
            if elapsed < delay:
                sleep_time = delay - elapsed + random.uniform(0, 1)
                time.sleep(sleep_time)
        
        # Update tracking
        self.last_request_time[platform] = time.time()
        self.request_count[platform] = self.request_count.get(platform, 0) + 1
        
        # Add extra delay for high request counts
        if self.request_count[platform] > 10:
            time.sleep(random.uniform(1, 3))
    
    def _extract_content_with_selenium(self, url: str, platform: str) -> Optional[Dict[str, Any]]:
        """
        Extract content using Selenium for JavaScript-heavy sites
        
        Args:
            url: URL to scrape
            platform: Platform name
            
        Returns:
            Extracted content or None if failed
        """
        if not self.driver:
            if not self._setup_selenium_driver():
                return None
        
        try:
            # Navigate to page
            self.driver.get(url)  # type: ignore
            
            # Wait for content to load
            wait = WebDriverWait(self.driver, self.timeout)  # type: ignore
            
            # Platform-specific waiting strategies
            if platform.lower() == 'facebook':
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="post_message"]')))  # type: ignore
                except TimeoutException:  # type: ignore
                    pass
            
            elif platform.lower() == 'twitter':
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweet"]')))  # type: ignore
                except TimeoutException:  # type: ignore
                    pass
            
            elif platform.lower() == 'youtube':
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#comments')))  # type: ignore
                except TimeoutException:  # type: ignore
                    pass
            
            # Random scroll to simulate human behavior
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")  # type: ignore
            time.sleep(random.uniform(1, 2))
            
            # Get page source
            page_source = self.driver.page_source  # type: ignore
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract content based on platform
            return self._extract_platform_content(soup, platform, url)
            
        except Exception as e:
            self.logger.error(f"Error extracting content with Selenium from {url}: {str(e)}")
            return None
    
    def _extract_platform_content(self, soup: BeautifulSoup, platform: str, url: str) -> Dict[str, Any]:
        """
        Extract platform-specific content from parsed HTML
        
        Args:
            soup: BeautifulSoup parsed HTML
            platform: Platform name
            url: Original URL
            
        Returns:
            Extracted content dictionary
        """
        content = {
            'url': url,
            'platform': platform,
            'timestamp': datetime.now().isoformat(),
            'posts': [],
            'comments': [],
            'reviews': [],
            'metadata': {}
        }
        
        # Platform-specific extraction
        if platform.lower() == 'facebook':
            content = self._extract_facebook_content(soup, content)
        elif platform.lower() == 'twitter':
            content = self._extract_twitter_content(soup, content)
        elif platform.lower() == 'youtube':
            content = self._extract_youtube_content(soup, content)
        elif platform.lower() == 'instagram':
            content = self._extract_instagram_content(soup, content)
        elif platform.lower() == 'linkedin':
            content = self._extract_linkedin_content(soup, content)
        elif platform.lower() == 'reddit':
            content = self._extract_reddit_content(soup, content)
        elif platform.lower() in ['g2', 'capterra', 'trustpilot', 'getapp']:
            content = self._extract_review_site_content(soup, content, platform)
        
        return content
    
    def _extract_facebook_content(self, soup: BeautifulSoup, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Facebook-specific content"""
        try:
            # Look for posts
            post_selectors = [
                '[data-testid="story-subtilted-top-level"] [data-testid="story-subtitle"]',
                '[data-ft="top_level_post_id"]',
                '[data-testid="story-subtitle"]',
                '.userContent'
            ]
            
            for selector in post_selectors:
                posts = soup.select(selector)
                for post in posts:
                    text = post.get_text(strip=True)
                    if text and len(text) > 20:
                        content['posts'].append({
                            'text': text,
                            'platform': 'Facebook',
                            'timestamp': datetime.now().isoformat()
                        })
                
                if content['posts']:
                    break
                    
        except Exception as e:
            self.logger.debug(f"Error extracting Facebook content: {str(e)}")
        
        return content
    
    def _extract_twitter_content(self, soup: BeautifulSoup, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Twitter-specific content"""
        try:
            # Look for tweets
            tweet_selectors = [
                '[data-testid="tweet"]',
                '.tweet-text',
                '.TweetTextSize'
            ]
            
            for selector in tweet_selectors:
                tweets = soup.select(selector)
                for tweet in tweets:
                    text = tweet.get_text(strip=True)
                    if text and len(text) > 10:
                        content['posts'].append({
                            'text': text,
                            'platform': 'Twitter',
                            'timestamp': datetime.now().isoformat()
                        })
                
                if content['posts']:
                    break
                    
        except Exception as e:
            self.logger.debug(f"Error extracting Twitter content: {str(e)}")
        
        return content
    
    def _extract_youtube_content(self, soup: BeautifulSoup, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract YouTube-specific content"""
        # YouTube comments
        comments = soup.find_all(['div'], {'id': 'content-text'})
        
        for comment in comments:
            try:
                comment_text = comment.get_text(strip=True)
                if comment_text and len(comment_text) > 10:
                    content['comments'].append({
                        'text': comment_text,
                        'platform': 'youtube',
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                self.logger.debug(f"Error extracting YouTube comment: {str(e)}")
        
        return content
    
    def _extract_instagram_content(self, soup: BeautifulSoup, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Instagram-specific content"""
        # Instagram post captions
        captions = soup.find_all(['div'], {'class': 'C4VMK'})
        
        for caption in captions:
            try:
                caption_text = caption.get_text(strip=True)
                if caption_text:
                    content['posts'].append({
                        'text': caption_text,
                        'platform': 'instagram',
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                self.logger.debug(f"Error extracting Instagram caption: {str(e)}")
        
        return content
    
    def _extract_linkedin_content(self, soup: BeautifulSoup, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract LinkedIn-specific content"""
        # LinkedIn post content
        posts = soup.find_all(['div'], {'class': 'feed-shared-update-v2__description'})
        
        for post in posts:
            try:
                post_text = post.get_text(strip=True)
                if post_text:
                    content['posts'].append({
                        'text': post_text,
                        'platform': 'linkedin',
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                self.logger.debug(f"Error extracting LinkedIn post: {str(e)}")
        
        return content
    
    def _extract_reddit_content(self, soup: BeautifulSoup, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Reddit-specific content"""
        # Reddit post titles and content
        posts = soup.find_all(['div'], {'class': 'Post'})
        
        for post in posts:
            try:
                # Post title
                title_elem = post.find(['h3'])
                title = title_elem.get_text(strip=True) if title_elem else ""
                
                # Post content
                content_elem = post.find(['div'], {'class': 'RichTextJSON-root'})
                post_content = content_elem.get_text(strip=True) if content_elem else ""
                
                if title or post_content:
                    content['posts'].append({
                        'title': title,
                        'text': post_content,
                        'platform': 'reddit',
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                self.logger.debug(f"Error extracting Reddit post: {str(e)}")
        
        # Reddit comments
        comments = soup.find_all(['div'], {'class': 'Comment'})
        
        for comment in comments:
            try:
                comment_elem = comment.find(['div'], {'class': 'RichTextJSON-root'})
                if comment_elem:
                    comment_text = comment_elem.get_text(strip=True)
                    if comment_text:
                        content['comments'].append({
                            'text': comment_text,
                            'platform': 'reddit',
                            'timestamp': datetime.now().isoformat()
                        })
            except Exception as e:
                self.logger.debug(f"Error extracting Reddit comment: {str(e)}")
        
        return content
    
    def _extract_review_site_content(self, soup: BeautifulSoup, content: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Extract review site-specific content"""
        # Generic review extraction
        review_selectors = {
            'g2': ['div[data-testid="review-text"]', '.review-text', '.review-content'],
            'capterra': ['.review-text', '.review-content', '.review-body'],
            'trustpilot': ['.review-content', '.review-text', '[data-service-review-text-typography]'],
            'getapp': ['.review-text', '.review-content', '.review-body']
        }
        
        selectors = review_selectors.get(platform.lower(), ['.review-text', '.review-content'])
        
        for selector in selectors:
            try:
                reviews = soup.select(selector)
                for review in reviews:
                    review_text = review.get_text(strip=True)
                    if review_text and len(review_text) > 20:
                        # Extract rating if available
                        rating = self._extract_review_rating(review.parent)
                        
                        content['reviews'].append({
                            'text': review_text,
                            'rating': rating,
                            'platform': platform,
                            'timestamp': datetime.now().isoformat()
                        })
                
                if content['reviews']:
                    break  # Stop if we found reviews
                    
            except Exception as e:
                self.logger.debug(f"Error extracting {platform} reviews with selector {selector}: {str(e)}")
        
        return content
    
    def _extract_review_rating(self, review_parent) -> Optional[float]:
        """Extract review rating from parent element"""
        try:
            # Common rating patterns
            rating_patterns = [
                r'(\d+(?:\.\d+)?)\s*(?:out of|\/)\s*5',
                r'(\d+(?:\.\d+)?)\s*star',
                r'rating[:\s]*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*\/\s*5'
            ]
            
            text = review_parent.get_text().lower()
            
            for pattern in rating_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    return float(matches[0])
            
            # Look for star elements
            stars = review_parent.find_all(['span', 'div'], {'class': re.compile(r'star|rating')})
            if stars:
                for star in stars:
                    star_text = star.get_text(strip=True)
                    numbers = re.findall(r'\d+(?:\.\d+)?', star_text)
                    if numbers:
                        return float(numbers[0])
        
        except Exception as e:
            self.logger.debug(f"Error extracting review rating: {str(e)}")
        
        return None
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"Error cleaning up Selenium driver: {str(e)}")
            finally:
                self.driver = None


class SocialMediaScraper(SocialMediaScraperBase):
    """
    Main social media scraper that coordinates different platform scrapers
    """
    
    def __init__(self, config=None):
        """
        Initialize social media scraper
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        self.scraped_content = {}
        self.scraping_stats = {
            'total_urls': 0,
            'successful_urls': 0,
            'failed_urls': 0,
            'platforms': {},
            'start_time': None,
            'end_time': None
        }
    
    @log_execution_time
    def scrape_social_media_urls(self, urls: List[Dict[str, str]], country_code: str = 'US') -> Dict[str, Any]:
        """
        Scrape multiple social media URLs
        
        Args:
            urls: List of dictionaries with 'url' and 'platform' keys
            country_code: Country code for localized analysis
            
        Returns:
            Dictionary with scraping results
        """
        self.logger.info(f"Starting social media scraping for {len(urls)} URLs")
        
        self.scraping_stats['start_time'] = datetime.now()
        self.scraping_stats['total_urls'] = len(urls)
        
        results = {
            'scraped_content': [],
            'failed_urls': [],
            'summary': {
                'total_urls': len(urls),
                'successful': 0,
                'failed': 0,
                'platforms_scraped': set(),
                'country_code': country_code
            }
        }
        
        for i, url_info in enumerate(urls, 1):
            url = url_info.get('url', '')
            platform = url_info.get('platform', 'unknown')
            
            self.logger.info(f"Scraping {i}/{len(urls)}: {platform} - {url}")
            
            try:
                # Rate limiting
                self._rate_limit(platform)
                
                # Scrape content
                content = self._scrape_single_url(url, platform, country_code)
                
                if content:
                    results['scraped_content'].append(content)
                    results['summary']['successful'] += 1
                    results['summary']['platforms_scraped'].add(platform)
                    
                    # Update platform stats
                    if platform not in self.scraping_stats['platforms']:
                        self.scraping_stats['platforms'][platform] = {'successful': 0, 'failed': 0}
                    self.scraping_stats['platforms'][platform]['successful'] += 1
                    
                    self.logger.debug(f"Successfully scraped {platform} content from {url}")
                else:
                    results['failed_urls'].append({'url': url, 'platform': platform, 'reason': 'No content extracted'})
                    results['summary']['failed'] += 1
                    
                    if platform not in self.scraping_stats['platforms']:
                        self.scraping_stats['platforms'][platform] = {'successful': 0, 'failed': 0}
                    self.scraping_stats['platforms'][platform]['failed'] += 1
                    
            except Exception as e:
                self.logger.error(f"Error scraping {platform} URL {url}: {str(e)}")
                results['failed_urls'].append({'url': url, 'platform': platform, 'reason': str(e)})
                results['summary']['failed'] += 1
                
                if platform not in self.scraping_stats['platforms']:
                    self.scraping_stats['platforms'][platform] = {'successful': 0, 'failed': 0}
                self.scraping_stats['platforms'][platform]['failed'] += 1
        
        # Finalize results
        results['summary']['platforms_scraped'] = list(results['summary']['platforms_scraped'])
        results['summary']['success_rate'] = (results['summary']['successful'] / len(urls)) * 100 if urls else 0
        
        self.scraping_stats['end_time'] = datetime.now()
        self.scraping_stats['successful_urls'] = results['summary']['successful']
        self.scraping_stats['failed_urls'] = results['summary']['failed']
        
        self.logger.info(f"Social media scraping completed. Success rate: {results['summary']['success_rate']:.1f}%")
        
        return results
    
    def _scrape_single_url(self, url: str, platform: str, country_code: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single social media URL
        
        Args:
            url: URL to scrape
            platform: Platform name
            country_code: Country code
            
        Returns:
            Scraped content or None if failed
        """
        try:
            # Check if platform requires Selenium
            js_heavy_platforms = ['facebook', 'twitter', 'instagram', 'youtube']
            
            if platform.lower() in js_heavy_platforms and self.use_selenium:
                # Use Selenium for JavaScript-heavy platforms
                content = self._extract_content_with_selenium(url, platform)
            else:
                # Use regular HTTP scraping
                scraped_data = self.scraper.scrape_page(url, extract_content=True, country_code=country_code)
                
                if scraped_data:
                    soup = BeautifulSoup(scraped_data.get('html', ''), 'html.parser')
                    content = self._extract_platform_content(soup, platform, url)
                else:
                    content = None
            
            # Post-process content
            if content:
                content = self._post_process_content(content, platform, country_code)
                
                # Add metadata
                content['scraping_metadata'] = {
                    'scraping_method': 'selenium' if platform.lower() in js_heavy_platforms and self.use_selenium else 'http',
                    'country_code': country_code,
                    'scraping_timestamp': datetime.now().isoformat()
                }
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error scraping {platform} URL {url}: {str(e)}")
            return None
    
    def _post_process_content(self, content: Dict[str, Any], platform: str, country_code: str) -> Dict[str, Any]:
        """
        Post-process scraped content
        
        Args:
            content: Raw scraped content
            platform: Platform name
            country_code: Country code
            
        Returns:
            Processed content
        """
        # Add complaint scoring
        for post in content.get('posts', []):
            post['complaint_score'] = self._calculate_complaint_score(post.get('text', ''))
        
        for comment in content.get('comments', []):
            comment['complaint_score'] = self._calculate_complaint_score(comment.get('text', ''))
        
        for review in content.get('reviews', []):
            review['complaint_score'] = self._calculate_complaint_score(review.get('text', ''))
        
        # Add language detection
        content['detected_language'] = self._detect_language(content)
        
        # Add platform-specific metrics
        content['content_metrics'] = {
            'total_posts': len(content.get('posts', [])),
            'total_comments': len(content.get('comments', [])),
            'total_reviews': len(content.get('reviews', [])),
            'avg_complaint_score': self._calculate_avg_complaint_score(content)
        }
        
        return content
    
    def _calculate_complaint_score(self, text: str) -> float:
        """
        Calculate complaint score for text content
        
        Args:
            text: Text content to analyze
            
        Returns:
            Complaint score (0-1)
        """
        if not text:
            return 0.0
        
        text_lower = text.lower()
        
        # Complaint keywords with weights
        complaint_keywords = {
            'terrible': 0.9, 'awful': 0.9, 'worst': 0.8, 'hate': 0.8,
            'disappointed': 0.7, 'frustrated': 0.7, 'angry': 0.7,
            'complaint': 0.8, 'problem': 0.7, 'issue': 0.6, 'bug': 0.6,
            'broken': 0.8, 'doesn\'t work': 0.9, 'not working': 0.8,
            'support': 0.5, 'help': 0.4, 'slow': 0.6, 'expensive': 0.6,
            'overpriced': 0.7, 'waste of money': 0.9, 'regret': 0.8,
            'avoid': 0.9, 'poor quality': 0.8, 'unreliable': 0.7,
            'crashed': 0.8, 'down': 0.6, 'offline': 0.7, 'glitch': 0.7,
            'fails': 0.7, 'error': 0.6, 'timeout': 0.6, 'freeze': 0.7,
            'unstable': 0.7, 'buggy': 0.8, 'useless': 0.8, 'horrible': 0.9
        }
        
        score = 0.0
        word_count = 0
        
        for keyword, weight in complaint_keywords.items():
            if keyword in text_lower:
                score += weight
                word_count += 1
        
        # Normalize score
        if word_count > 0:
            score = min(score / word_count, 1.0)
        
        return score
    
    def _detect_language(self, content: Dict[str, Any]) -> str:
        """
        Detect primary language of content
        
        Args:
            content: Content dictionary
            
        Returns:
            Language code (default: 'en')
        """
        # Simple language detection based on common words
        # In a production system, you'd use a proper language detection library
        
        all_text = ""
        for post in content.get('posts', []):
            all_text += post.get('text', '') + " "
        for comment in content.get('comments', []):
            all_text += comment.get('text', '') + " "
        for review in content.get('reviews', []):
            all_text += review.get('text', '') + " "
        
        # Basic language detection patterns
        if re.search(r'[一-龯]', all_text):
            return 'zh'
        elif re.search(r'[а-яё]', all_text, re.IGNORECASE):
            return 'ru'
        elif re.search(r'[あ-んア-ンー]', all_text):
            return 'ja'
        elif re.search(r'[가-힣]', all_text):
            return 'ko'
        else:
            return 'en'
    
    def _calculate_avg_complaint_score(self, content: Dict[str, Any]) -> float:
        """
        Calculate average complaint score for all content
        
        Args:
            content: Content dictionary
            
        Returns:
            Average complaint score
        """
        scores = []
        
        for post in content.get('posts', []):
            scores.append(post.get('complaint_score', 0))
        
        for comment in content.get('comments', []):
            scores.append(comment.get('complaint_score', 0))
        
        for review in content.get('reviews', []):
            scores.append(review.get('complaint_score', 0))
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def get_scraping_stats(self) -> Dict[str, Any]:
        """
        Get scraping statistics
        
        Returns:
            Dictionary with scraping statistics
        """
        return self.scraping_stats
    
    def cleanup(self):
        """Clean up resources"""
        super().cleanup()
        self.scraped_content.clear()


def create_social_media_urls_from_search_results(search_results: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Create social media URLs list from Google search results
    
    Args:
        search_results: Results from GoogleSearchScraper
        
    Returns:
        List of URL dictionaries for social media scraping
    """
    urls = []
    
    for platform, platform_data in search_results.get('platforms', {}).items():
        for result in platform_data.get('search_results', []):
            url = result.get('url', '')
            if url:
                urls.append({
                    'url': url,
                    'platform': platform,
                    'title': result.get('title', ''),
                    'description': result.get('description', ''),
                    'complaint_score': result.get('complaint_score', 0),
                    'query': result.get('query', '')
                })
    
    return urls


def analyze_social_media_content(scraping_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze social media scraping results
    
    Args:
        scraping_results: Results from SocialMediaScraper
        
    Returns:
        Analysis of social media content
    """
    analysis = {
        'total_content_pieces': 0,
        'platforms': {},
        'complaint_analysis': {
            'high_complaint_content': [],
            'medium_complaint_content': [],
            'low_complaint_content': []
        },
        'language_distribution': {},
        'content_types': {
            'posts': 0,
            'comments': 0,
            'reviews': 0
        }
    }
    
    for content in scraping_results.get('scraped_content', []):
        platform = content.get('platform', 'unknown')
        
        # Platform analysis
        if platform not in analysis['platforms']:
            analysis['platforms'][platform] = {
                'content_count': 0,
                'avg_complaint_score': 0,
                'top_complaints': []
            }
        
        # Count content pieces
        posts = content.get('posts', [])
        comments = content.get('comments', [])
        reviews = content.get('reviews', [])
        
        analysis['content_types']['posts'] += len(posts)
        analysis['content_types']['comments'] += len(comments)
        analysis['content_types']['reviews'] += len(reviews)
        
        total_pieces = len(posts) + len(comments) + len(reviews)
        analysis['total_content_pieces'] += total_pieces
        analysis['platforms'][platform]['content_count'] += total_pieces
        
        # Language distribution
        language = content.get('detected_language', 'en')
        analysis['language_distribution'][language] = analysis['language_distribution'].get(language, 0) + 1
        
        # Complaint analysis
        all_content = posts + comments + reviews
        high_complaints = []
        medium_complaints = []
        low_complaints = []
        
        for item in all_content:
            score = item.get('complaint_score', 0)
            if score >= 0.7:
                high_complaints.append(item)
            elif score >= 0.4:
                medium_complaints.append(item)
            else:
                low_complaints.append(item)
        
        analysis['complaint_analysis']['high_complaint_content'].extend(high_complaints)
        analysis['complaint_analysis']['medium_complaint_content'].extend(medium_complaints)
        analysis['complaint_analysis']['low_complaint_content'].extend(low_complaints)
        
        # Platform-specific metrics
        if all_content:
            avg_score = sum(item.get('complaint_score', 0) for item in all_content) / len(all_content)
            analysis['platforms'][platform]['avg_complaint_score'] = avg_score
            
            # Top complaints for this platform
            top_complaints = sorted(all_content, key=lambda x: x.get('complaint_score', 0), reverse=True)[:5]
            analysis['platforms'][platform]['top_complaints'] = top_complaints
    
    return analysis 