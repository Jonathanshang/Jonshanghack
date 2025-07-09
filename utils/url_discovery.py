import requests
import re
import time
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Set, Tuple
import logging
from utils.logger import log_execution_time, log_function_call

class URLDiscovery:
    """
    Automated URL discovery system for competitor analysis
    
    This class implements multiple strategies to discover important pages on competitor websites:
    - Sitemap parsing
    - Navigation menu analysis
    - URL pattern matching
    - Footer link analysis
    - Breadcrumb analysis
    """
    
    def __init__(self, base_url: str, config=None):
        """
        Initialize URL discovery for a competitor website
        
        Args:
            base_url: The main website URL to analyze
            config: Configuration object with timeout, user agent, etc.
        """
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.config = config
        self.logger = logging.getLogger("competitive_analysis")
        
        # Configure session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': getattr(config, 'user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Page type patterns for URL matching
        self.page_patterns = {
            'pricing': [
                r'pricing', r'price', r'cost', r'plans', r'packages', r'subscription',
                r'buy', r'purchase', r'checkout', r'payment', r'billing'
            ],
            'features': [
                r'features', r'capabilities', r'functionality', r'what-we-do',
                r'services', r'solutions', r'product', r'overview'
            ],
            'blog': [
                r'blog', r'news', r'articles', r'insights', r'resources',
                r'press', r'announcements', r'updates', r'stories'
            ],
            'careers': [
                r'careers', r'jobs', r'employment', r'hiring', r'work-with-us',
                r'join', r'team', r'opportunities', r'positions'
            ],
            'contact': [
                r'contact', r'support', r'help', r'customer-service',
                r'get-in-touch', r'reach-us'
            ],
            'about': [
                r'about', r'company', r'who-we-are', r'our-story',
                r'mission', r'vision', r'history'
            ]
        }
        
        # Common navigation selectors
        self.nav_selectors = [
            'nav', 'navigation', '.nav', '.navigation', '.menu', '.main-menu',
            'header nav', 'header ul', '.header-nav', '.top-nav', '.primary-nav',
            'footer nav', 'footer ul', '.footer-nav', '.footer-menu'
        ]
        
        # Discovered URLs storage
        self.discovered_urls = {
            'pricing': [],
            'features': [],
            'blog': [],
            'careers': [],
            'contact': [],
            'about': [],
            'other': []
        }
        
        # Set to track processed URLs to avoid duplicates
        self.processed_urls = set()
    
    @log_execution_time
    def discover_all_pages(self) -> Dict[str, List[str]]:
        """
        Main method to discover all page types using multiple strategies
        
        Returns:
            Dictionary with page types as keys and lists of discovered URLs as values
        """
        self.logger.info(f"Starting URL discovery for {self.base_url}")
        
        try:
            # Strategy 1: Sitemap parsing
            self.logger.info("Strategy 1: Parsing sitemaps")
            self._parse_sitemaps()
            
            # Strategy 2: Navigation analysis
            self.logger.info("Strategy 2: Analyzing navigation")
            self._analyze_navigation()
            
            # Strategy 3: Common URL patterns
            self.logger.info("Strategy 3: Checking common URL patterns")
            self._check_common_patterns()
            
            # Strategy 4: Footer analysis
            self.logger.info("Strategy 4: Analyzing footer links")
            self._analyze_footer()
            
            # Remove duplicates and validate URLs
            self._clean_and_validate_urls()
            
            self.logger.info(f"URL discovery completed. Found {sum(len(urls) for urls in self.discovered_urls.values())} URLs")
            return self.discovered_urls
            
        except Exception as e:
            self.logger.error(f"Error in URL discovery: {str(e)}")
            return self.discovered_urls
    
    def _parse_sitemaps(self) -> None:
        """Parse XML sitemaps to discover URLs"""
        sitemap_urls = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/sitemaps.xml",
            f"{self.base_url}/sitemap_index.xml",
            f"{self.base_url}/sitemap/sitemap.xml"
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                self.logger.debug(f"Checking sitemap: {sitemap_url}")
                response = self.session.get(sitemap_url, timeout=10)
                
                if response.status_code == 200:
                    self.logger.info(f"Found sitemap: {sitemap_url}")
                    self._parse_sitemap_content(response.text)
                    break
                    
            except Exception as e:
                self.logger.debug(f"Sitemap not found or error: {sitemap_url} - {str(e)}")
                continue
    
    def _parse_sitemap_content(self, content: str) -> None:
        """Parse sitemap XML content and extract URLs"""
        try:
            soup = BeautifulSoup(content, 'xml')
            
            # Handle sitemap index files
            sitemaps = soup.find_all('sitemap')
            if sitemaps:
                for sitemap in sitemaps:
                    loc = sitemap.find('loc')
                    if loc and hasattr(loc, 'text'):
                        self._parse_individual_sitemap(loc.text)
            
            # Handle individual sitemap files
            urls = soup.find_all('url')
            for url in urls:
                loc = url.find('loc')
                if loc and hasattr(loc, 'text'):
                    self._categorize_url(loc.text)
                    
        except Exception as e:
            self.logger.error(f"Error parsing sitemap content: {str(e)}")
    
    def _parse_individual_sitemap(self, sitemap_url: str) -> None:
        """Parse individual sitemap from sitemap index"""
        try:
            response = self.session.get(sitemap_url, timeout=10)
            if response.status_code == 200:
                self._parse_sitemap_content(response.text)
        except Exception as e:
            self.logger.debug(f"Error parsing individual sitemap {sitemap_url}: {str(e)}")
    
    def _analyze_navigation(self) -> None:
        """Analyze website navigation to find important pages"""
        try:
            response = self.session.get(self.base_url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract navigation links
                nav_links = set()
                for selector in self.nav_selectors:
                    elements = soup.select(selector)
                    for element in elements:
                        links = element.find_all('a', href=True)
                        for link in links:
                            href = link.get('href')
                            if href and isinstance(href, str):
                                full_url = urljoin(self.base_url, href)
                                if self._is_internal_url(full_url):
                                    nav_links.add(full_url)
                                    link_text = link.get_text(strip=True) if hasattr(link, 'get_text') else ""
                                    self._categorize_url(full_url, link_text)
                
                self.logger.info(f"Found {len(nav_links)} navigation links")
                
        except Exception as e:
            self.logger.error(f"Error analyzing navigation: {str(e)}")
    
    def _check_common_patterns(self) -> None:
        """Check common URL patterns for different page types"""
        common_paths = {
            'pricing': ['/pricing', '/price', '/plans', '/packages', '/subscription', '/buy'],
            'features': ['/features', '/capabilities', '/product', '/solutions', '/services'],
            'blog': ['/blog', '/news', '/articles', '/insights', '/resources'],
            'careers': ['/careers', '/jobs', '/employment', '/hiring', '/join-us'],
            'contact': ['/contact', '/support', '/help', '/customer-service'],
            'about': ['/about', '/company', '/who-we-are', '/our-story']
        }
        
        for page_type, paths in common_paths.items():
            for path in paths:
                url = f"{self.base_url}{path}"
                if self._check_url_exists(url):
                    self.discovered_urls[page_type].append(url)
                    self.logger.debug(f"Found {page_type} page: {url}")
    
    def _analyze_footer(self) -> None:
        """Analyze footer links for additional pages"""
        try:
            response = self.session.get(self.base_url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find footer elements
                footer_selectors = ['footer', '.footer', '#footer', '.site-footer']
                footer_links = set()
                
                for selector in footer_selectors:
                    footer = soup.select_one(selector)
                    if footer:
                        links = footer.find_all('a', href=True)
                        for link in links:
                            href = link.get('href')
                            if href and isinstance(href, str):
                                full_url = urljoin(self.base_url, href)
                                if self._is_internal_url(full_url):
                                    footer_links.add(full_url)
                                    link_text = link.get_text(strip=True) if hasattr(link, 'get_text') else ""
                                    self._categorize_url(full_url, link_text)
                
                self.logger.info(f"Found {len(footer_links)} footer links")
                
        except Exception as e:
            self.logger.error(f"Error analyzing footer: {str(e)}")
    
    def _categorize_url(self, url: str, link_text: str = "") -> None:
        """Categorize URL based on patterns and link text"""
        if url in self.processed_urls:
            return
        
        self.processed_urls.add(url)
        
        # Clean URL for pattern matching
        clean_url = url.lower()
        clean_text = link_text.lower() if link_text else ""
        
        # Check against patterns
        for page_type, patterns in self.page_patterns.items():
            for pattern in patterns:
                if re.search(pattern, clean_url) or re.search(pattern, clean_text):
                    self.discovered_urls[page_type].append(url)
                    self.logger.debug(f"Categorized {url} as {page_type}")
                    return
        
        # If no category found, add to 'other'
        self.discovered_urls['other'].append(url)
    
    def _is_internal_url(self, url: str) -> bool:
        """Check if URL is internal to the domain"""
        parsed = urlparse(url)
        return (parsed.netloc == self.domain or 
                parsed.netloc == '' or 
                parsed.netloc.endswith(f'.{self.domain}'))
    
    def _check_url_exists(self, url: str) -> bool:
        """Check if URL exists and is accessible"""
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
    
    def _clean_and_validate_urls(self) -> None:
        """Remove duplicates and validate URLs"""
        for page_type in self.discovered_urls:
            # Remove duplicates
            unique_urls = list(set(self.discovered_urls[page_type]))
            
            # Validate URLs
            validated_urls = []
            for url in unique_urls:
                if self._is_internal_url(url) and url.startswith(('http://', 'https://')):
                    validated_urls.append(url)
            
            self.discovered_urls[page_type] = validated_urls
            
            # Log results
            if validated_urls:
                self.logger.info(f"Found {len(validated_urls)} {page_type} URLs")
                for url in validated_urls:
                    self.logger.debug(f"  - {url}")
    
    def get_page_content(self, url: str) -> Optional[str]:
        """
        Fetch content from a specific URL
        
        Args:
            url: URL to fetch content from
            
        Returns:
            HTML content or None if failed
        """
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                return response.text
            else:
                self.logger.warning(f"Failed to fetch {url}: Status {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def get_page_metadata(self, url: str) -> Dict[str, str]:
        """
        Extract metadata from a page
        
        Args:
            url: URL to extract metadata from
            
        Returns:
            Dictionary with title, description, and other metadata
        """
        metadata = {
            'title': '',
            'description': '',
            'keywords': '',
            'url': url
        }
        
        try:
            content = self.get_page_content(url)
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract title
                title_tag = soup.find('title')
                if title_tag:
                    metadata['title'] = title_tag.get_text(strip=True)
                
                # Extract meta description
                desc_tag = soup.find('meta', attrs={'name': 'description'})
                if desc_tag:
                    metadata['description'] = desc_tag.get('content', '')
                
                # Extract meta keywords
                keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
                if keywords_tag:
                    metadata['keywords'] = keywords_tag.get('content', '')
                
        except Exception as e:
            self.logger.error(f"Error extracting metadata from {url}: {str(e)}")
        
        return metadata
    
    def get_discovery_summary(self) -> Dict[str, any]:
        """
        Get a summary of the discovery process
        
        Returns:
            Dictionary with discovery statistics and results
        """
        summary = {
            'base_url': self.base_url,
            'domain': self.domain,
            'total_urls_found': sum(len(urls) for urls in self.discovered_urls.values()),
            'pages_by_type': {k: len(v) for k, v in self.discovered_urls.items()},
            'discovered_urls': self.discovered_urls,
            'processed_urls_count': len(self.processed_urls)
        }
        
        return summary

# Utility functions for URL discovery
def discover_competitor_urls(base_url: str, config=None) -> Dict[str, List[str]]:
    """
    Convenience function to discover URLs for a competitor
    
    Args:
        base_url: Competitor's website URL
        config: Configuration object
        
    Returns:
        Dictionary with discovered URLs by page type
    """
    discovery = URLDiscovery(base_url, config)
    return discovery.discover_all_pages()

def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except:
        return False

def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing trailing slashes and fragments
    
    Args:
        url: URL to normalize
        
    Returns:
        Normalized URL
    """
    try:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
    except:
        return url 