import requests
import time
import random
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any, Tuple
import logging
import re
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import hashlib
import json
from datetime import datetime, timedelta
from utils.logger import log_execution_time, log_function_call

class WebScraper:
    """
    Robust web scraping system with error handling, rate limiting, and content extraction
    
    Features:
    - Respectful crawling with rate limiting
    - Robot.txt compliance
    - Content extraction and cleaning
    - Data normalization
    - Error handling and retries
    - Session management
    - Content caching
    """
    
    def __init__(self, config=None):
        """
        Initialize the web scraper
        
        Args:
            config: Configuration object with scraping parameters
        """
        self.config = config
        self.logger = logging.getLogger("competitive_analysis")
        
        # Initialize session with realistic headers
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
        # Scraping parameters
        self.max_retries = getattr(config, 'max_retries', 3)
        self.base_delay = getattr(config, 'scraping_delay', 1.0)
        self.timeout = getattr(config, 'request_timeout', 30)
        self.max_pages_per_site = getattr(config, 'max_pages_per_site', 100)
        
        # Content cache
        self.cache = {}
        self.cache_duration = getattr(config, 'cache_duration', 3600)  # 1 hour
        
        # Rate limiting
        self.last_request_time = {}
        self.request_count = {}
        
        # Robots.txt cache
        self.robots_cache = {}
        
        # Initialize session headers
        self._update_session_headers()
    
    def _update_session_headers(self):
        """Update session with rotating user agent and realistic headers"""
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'no-cache'
        })
    
    def _can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt"""
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            if base_url not in self.robots_cache:
                robots_url = urljoin(base_url, '/robots.txt')
                rp = RobotFileParser()
                rp.set_url(robots_url)
                try:
                    rp.read()
                    self.robots_cache[base_url] = rp
                except:
                    # If robots.txt can't be read, assume we can fetch
                    self.robots_cache[base_url] = None
            
            robots = self.robots_cache[base_url]
            if robots:
                return robots.can_fetch(self.session.headers.get('User-Agent', '*'), url)
            return True
            
        except Exception as e:
            self.logger.debug(f"Error checking robots.txt for {url}: {str(e)}")
            return True
    
    def _rate_limit(self, domain: str):
        """Implement rate limiting per domain"""
        now = time.time()
        
        # Check if we need to wait
        if domain in self.last_request_time:
            elapsed = now - self.last_request_time[domain]
            if elapsed < self.base_delay:
                sleep_time = self.base_delay - elapsed
                time.sleep(sleep_time)
        
        # Update request tracking
        self.last_request_time[domain] = time.time()
        self.request_count[domain] = self.request_count.get(domain, 0) + 1
        
        # Add extra delay for many requests
        if self.request_count[domain] > 10:
            time.sleep(self.base_delay * 0.5)
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached content is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get('timestamp', 0)
        return time.time() - cached_time < self.cache_duration
    
    @log_execution_time
    def scrape_page(self, url: str, extract_content: bool = True, country_code: str = 'US') -> Optional[Dict[str, Any]]:
        """
        Scrape a single page with error handling and retries
        
        Args:
            url: URL to scrape
            extract_content: Whether to extract and clean content
            
        Returns:
            Dictionary with scraped data or None if failed
        """
        cache_key = self._get_cache_key(url)
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            self.logger.debug(f"Returning cached content for {url}")
            return self.cache[cache_key]['data']
        
        # Check robots.txt
        if not self._can_fetch(url):
            self.logger.warning(f"Robots.txt disallows fetching {url}")
            return None
        
        domain = urlparse(url).netloc
        
        for attempt in range(self.max_retries):
            try:
                # Rate limiting
                self._rate_limit(domain)
                
                # Rotate user agent occasionally
                if attempt > 0:
                    self._update_session_headers()
                
                self.logger.debug(f"Scraping {url} (attempt {attempt + 1})")
                
                # Make request
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # Process successful response
                result = self._process_response(url, response, extract_content, country_code)
                
                # Cache result
                self.cache[cache_key] = {
                    'data': result,
                    'timestamp': time.time()
                }
                
                return result
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed for {url} (attempt {attempt + 1}): {str(e)}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    sleep_time = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(sleep_time)
                else:
                    self.logger.error(f"Failed to scrape {url} after {self.max_retries} attempts")
                    return None
                    
            except Exception as e:
                self.logger.error(f"Unexpected error scraping {url}: {str(e)}")
                return None
    
    def _process_response(self, url: str, response: requests.Response, extract_content: bool, country_code: str = 'US') -> Dict[str, Any]:
        """Process HTTP response and extract data"""
        result = {
            'url': url,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'scraped_at': datetime.now().isoformat(),
            'content_length': len(response.content),
            'content_type': response.headers.get('Content-Type', '').lower()
        }
        
        # Store raw HTML
        result['raw_html'] = response.text
        
        if extract_content:
            # Parse HTML and extract structured content
            soup = BeautifulSoup(response.text, 'html.parser')
            result.update(self._extract_content(soup, country_code))
        
        return result
    
    def _extract_content(self, soup: BeautifulSoup, country_code: str = 'US') -> Dict[str, Any]:
        """Extract structured content from HTML"""
        content = {}
        
        # Basic metadata
        content['title'] = self._extract_title(soup)
        content['meta_description'] = self._extract_meta_description(soup)
        content['meta_keywords'] = self._extract_meta_keywords(soup)
        
        # Content extraction
        content['headings'] = self._extract_headings(soup)
        content['paragraphs'] = self._extract_paragraphs(soup)
        content['links'] = self._extract_links(soup)
        content['images'] = self._extract_images(soup)
        
        # Structured data
        content['structured_data'] = self._extract_structured_data(soup)
        
        # Page-specific content
        content['pricing_indicators'] = self._extract_pricing_indicators(soup, country_code)
        content['feature_lists'] = self._extract_feature_lists(soup)
        content['contact_info'] = self._extract_contact_info(soup)
        
        # Text content
        content['clean_text'] = self._extract_clean_text(soup)
        content['word_count'] = len(content['clean_text'].split())
        
        return content
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '') if meta_desc else ""
    
    def _extract_meta_keywords(self, soup: BeautifulSoup) -> str:
        """Extract meta keywords"""
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        return meta_keywords.get('content', '') if meta_keywords else ""
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract all headings (h1-h6)"""
        headings = {}
        for i in range(1, 7):
            tag = f'h{i}'
            elements = soup.find_all(tag)
            headings[tag] = [elem.get_text(strip=True) for elem in elements]
        return headings
    
    def _extract_paragraphs(self, soup: BeautifulSoup) -> List[str]:
        """Extract paragraph text"""
        paragraphs = soup.find_all('p')
        return [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    
    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all links with text and href"""
        links = []
        for link in soup.find_all('a', href=True):
            links.append({
                'text': link.get_text(strip=True),
                'href': link.get('href', ''),
                'title': link.get('title', '')
            })
        return links[:50]  # Limit to first 50 links
    
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract image information"""
        images = []
        for img in soup.find_all('img'):
            images.append({
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
        return images[:20]  # Limit to first 20 images
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract JSON-LD structured data"""
        structured_data = []
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                structured_data.append(data)
            except json.JSONDecodeError:
                continue
        
        return structured_data
    
    def _extract_pricing_indicators(self, soup: BeautifulSoup, country_code: str = 'US') -> Dict[str, Any]:
        """Extract pricing-related content"""
        from .country_localization import country_localization
        
        pricing = {
            'currency_symbols': [],
            'price_patterns': [],
            'pricing_terms': []
        }
        
        # Get country-specific currency symbols
        country_symbols = country_localization.get_currency_symbols(country_code)
        
        # Build currency pattern from country symbols
        if country_symbols:
            escaped_symbols = [re.escape(symbol) for symbol in country_symbols]
            currency_pattern = f'[{"".join(escaped_symbols)}][\\d,.]+'
        else:
            currency_pattern = r'[$€£¥₹][\d,.]+'
        
        text = soup.get_text()
        pricing['currency_symbols'] = list(set(re.findall(currency_pattern, text)))
        
        # Get country-specific pricing terms
        pricing_terms = country_localization.get_localized_pricing_patterns(country_code)
        
        found_terms = []
        for term in pricing_terms:
            if term.lower() in text.lower():
                found_terms.append(term)
        
        pricing['pricing_terms'] = found_terms
        
        return pricing
    
    def _extract_feature_lists(self, soup: BeautifulSoup) -> List[str]:
        """Extract feature lists and bullet points"""
        features = []
        
        # Find unordered lists
        lists = soup.find_all(['ul', 'ol'])
        for list_elem in lists:
            items = list_elem.find_all('li')
            for item in items:
                text = item.get_text(strip=True)
                if text and len(text) > 5:  # Filter out very short items
                    features.append(text)
        
        return features[:30]  # Limit to first 30 features
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract contact information"""
        contact = {
            'emails': [],
            'phones': [],
            'addresses': []
        }
        
        text = soup.get_text()
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        contact['emails'] = list(set(re.findall(email_pattern, text)))
        
        # Extract phone numbers
        phone_pattern = r'(\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
        contact['phones'] = list(set(re.findall(phone_pattern, text)))
        
        return contact
    
    def _extract_clean_text(self, soup: BeautifulSoup) -> str:
        """Extract clean, readable text content"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        
        # Clean whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def scrape_multiple_pages(self, urls: List[str], max_pages: Optional[int] = None, country_code: str = 'US') -> Dict[str, Any]:
        """
        Scrape multiple pages with progress tracking
        
        Args:
            urls: List of URLs to scrape
            max_pages: Maximum number of pages to scrape (None for all)
            country_code: Country code for localized analysis
            
        Returns:
            Dictionary with scraping results
        """
        if max_pages:
            urls = urls[:max_pages]
        
        results = {
            'scraped_pages': [],
            'failed_pages': [],
            'summary': {
                'total_attempted': len(urls),
                'successful': 0,
                'failed': 0,
                'start_time': datetime.now().isoformat()
            }
        }
        
        self.logger.info(f"Starting to scrape {len(urls)} pages")
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Scraping page {i}/{len(urls)}: {url}")
            
            scraped_data = self.scrape_page(url, country_code=country_code)
            
            if scraped_data:
                results['scraped_pages'].append(scraped_data)
                results['summary']['successful'] += 1
            else:
                results['failed_pages'].append(url)
                results['summary']['failed'] += 1
        
        results['summary']['end_time'] = datetime.now().isoformat()
        results['summary']['success_rate'] = results['summary']['successful'] / len(urls) * 100
        
        self.logger.info(f"Scraping completed. Success rate: {results['summary']['success_rate']:.1f}%")
        
        return results
    
    def get_scraping_stats(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        return {
            'cache_size': len(self.cache),
            'domains_scraped': len(self.request_count),
            'total_requests': sum(self.request_count.values()),
            'robots_cache_size': len(self.robots_cache),
            'request_count_by_domain': self.request_count
        }
    
    def clear_cache(self):
        """Clear the content cache"""
        self.cache.clear()
        self.logger.info("Scraper cache cleared")

# Utility functions for content analysis
def extract_page_category(scraped_data: Dict[str, Any]) -> str:
    """
    Determine page category based on scraped content
    
    Args:
        scraped_data: Dictionary with scraped page data
        
    Returns:
        Detected page category
    """
    if not scraped_data:
        return "unknown"
    
    title = scraped_data.get('title', '').lower()
    text = scraped_data.get('clean_text', '').lower()
    pricing_indicators = scraped_data.get('pricing_indicators', {})
    
    # Check for pricing page
    if (pricing_indicators.get('currency_symbols') or 
        any(term in title for term in ['pricing', 'plans', 'packages']) or
        any(term in text[:1000] for term in ['pricing', 'subscription', 'plan'])):
        return "pricing"
    
    # Check for features page
    if (any(term in title for term in ['features', 'capabilities', 'product']) or
        len(scraped_data.get('feature_lists', [])) > 5):
        return "features"
    
    # Check for blog/news
    if any(term in title for term in ['blog', 'news', 'article', 'post']):
        return "blog"
    
    # Check for careers
    if any(term in title for term in ['careers', 'jobs', 'employment']):
        return "careers"
    
    # Check for contact
    if (any(term in title for term in ['contact', 'support', 'help']) or
        scraped_data.get('contact_info', {}).get('emails')):
        return "contact"
    
    # Check for about
    if any(term in title for term in ['about', 'company', 'story']):
        return "about"
    
    return "other"

def analyze_content_quality(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the quality and completeness of scraped content
    
    Args:
        scraped_data: Dictionary with scraped page data
        
    Returns:
        Content quality analysis
    """
    quality = {
        'completeness_score': 0,
        'content_richness': 0,
        'structure_quality': 0,
        'issues': []
    }
    
    if not scraped_data:
        quality['issues'].append("No data scraped")
        return quality
    
    # Check completeness
    required_fields = ['title', 'clean_text', 'headings']
    present_fields = sum(1 for field in required_fields if scraped_data.get(field))
    quality['completeness_score'] = (present_fields / len(required_fields)) * 100
    
    # Check content richness
    word_count = scraped_data.get('word_count', 0)
    image_count = len(scraped_data.get('images', []))
    link_count = len(scraped_data.get('links', []))
    
    quality['content_richness'] = min(100, (word_count / 10) + (image_count * 5) + (link_count * 2))
    
    # Check structure quality
    headings = scraped_data.get('headings', {})
    h1_count = len(headings.get('h1', []))
    total_headings = sum(len(h) for h in headings.values())
    
    if h1_count == 0:
        quality['issues'].append("No H1 heading found")
    elif h1_count > 1:
        quality['issues'].append("Multiple H1 headings found")
    
    quality['structure_quality'] = min(100, total_headings * 10)
    
    return quality 