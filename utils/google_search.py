"""
Google Search Query System for Social Media Complaints & Reviews

This module generates targeted search queries to find competitor complaints and reviews
across social media platforms, review sites, and forums. It integrates with the country
localization system to provide region-specific search queries.
"""

import logging
import re
import time
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import quote, urlencode, urlparse, parse_qs
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random

from .scraper import WebScraper
from .country_localization import country_localization
from .logger import log_execution_time, log_function_call

class GoogleSearchQueryGenerator:
    """
    Generates targeted Google search queries for finding competitor complaints and reviews
    
    Features:
    - Platform-specific query generation
    - Country-specific search domains
    - Complaint-focused keywords
    - Review site targeting
    - Social media platform queries
    """
    
    def __init__(self, config=None):
        """
        Initialize the Google search query generator
        
        Args:
            config: Configuration object with search parameters
        """
        self.config = config
        self.logger = logging.getLogger("competitive_analysis")
        
        # Initialize complaint-focused keywords
        self.complaint_keywords = [
            'problem', 'issue', 'complaint', 'bug', 'error', 'broken', 'terrible', 
            'awful', 'worst', 'hate', 'disappointed', 'frustrated', 'angry',
            'support', 'help', 'slow', 'expensive', 'overpriced', 'hidden fee',
            'crashed', 'down', 'offline', 'glitch', 'fails', 'doesn\'t work',
            'poor quality', 'unreliable', 'waste of money', 'regret', 'avoid'
        ]
        
        # Support-related keywords
        self.support_keywords = [
            'support', 'customer service', 'help desk', 'response time',
            'no response', 'ignored', 'waiting', 'hours', 'days', 'slow support',
            'unhelpful', 'rude', 'difficult', 'phone number', 'contact'
        ]
        
        # Billing and contract keywords
        self.billing_keywords = [
            'billing', 'invoice', 'payment', 'charge', 'fee', 'cost', 'price',
            'contract', 'cancel', 'refund', 'subscription', 'overcharge',
            'hidden cost', 'surprise fee', 'expensive', 'money back'
        ]
        
        # Performance keywords
        self.performance_keywords = [
            'slow', 'lag', 'performance', 'speed', 'loading', 'timeout',
            'freeze', 'crash', 'unstable', 'downtime', 'outage', 'offline'
        ]
    
    def generate_platform_queries(self, competitor_name: str, country_code: str = 'US') -> Dict[str, List[str]]:
        """
        Generate search queries for specific social media platforms
        
        Args:
            competitor_name: Name of the competitor
            country_code: Country code for localized search
            
        Returns:
            Dictionary with platform-specific queries
        """
        queries = {}
        
        # Get country-specific social platforms
        social_platforms = country_localization.get_social_platforms(country_code)
        
        # Facebook queries
        if 'Facebook' in social_platforms:
            queries['Facebook'] = self._generate_facebook_queries(competitor_name, country_code)
        
        # Twitter/X queries
        if 'Twitter' in social_platforms:
            queries['Twitter'] = self._generate_twitter_queries(competitor_name, country_code)
        
        # YouTube queries
        if 'YouTube' in social_platforms:
            queries['YouTube'] = self._generate_youtube_queries(competitor_name, country_code)
        
        # Instagram queries
        if 'Instagram' in social_platforms:
            queries['Instagram'] = self._generate_instagram_queries(competitor_name, country_code)
        
        # LinkedIn queries
        if 'LinkedIn' in social_platforms:
            queries['LinkedIn'] = self._generate_linkedin_queries(competitor_name, country_code)
        
        # Reddit queries
        if 'Reddit' in social_platforms:
            queries['Reddit'] = self._generate_reddit_queries(competitor_name, country_code)
        
        # Platform-specific queries for different countries
        if country_code == 'CN' and 'WeChat' in social_platforms:
            queries['WeChat'] = self._generate_wechat_queries(competitor_name, country_code)
        
        if country_code == 'RU' and 'VK' in social_platforms:
            queries['VK'] = self._generate_vk_queries(competitor_name, country_code)
        
        if country_code in ['TH', 'JP'] and 'LINE' in social_platforms:
            queries['LINE'] = self._generate_line_queries(competitor_name, country_code)
        
        return queries
    
    def generate_review_site_queries(self, competitor_name: str, country_code: str = 'US') -> Dict[str, List[str]]:
        """
        Generate search queries for review sites
        
        Args:
            competitor_name: Name of the competitor
            country_code: Country code for localized search
            
        Returns:
            Dictionary with review site queries
        """
        queries = {}
        
        # Get country-specific review sites
        review_sites = country_localization.get_review_sites(country_code)
        
        # G2 queries
        if 'G2' in review_sites:
            queries['G2'] = self._generate_g2_queries(competitor_name, country_code)
        
        # Capterra queries
        if 'Capterra' in review_sites:
            queries['Capterra'] = self._generate_capterra_queries(competitor_name, country_code)
        
        # TrustPilot queries
        if 'TrustPilot' in review_sites:
            queries['TrustPilot'] = self._generate_trustpilot_queries(competitor_name, country_code)
        
        # GetApp queries
        if 'GetApp' in review_sites:
            queries['GetApp'] = self._generate_getapp_queries(competitor_name, country_code)
        
        # Software Advice queries
        if 'Software Advice' in review_sites:
            queries['Software Advice'] = self._generate_software_advice_queries(competitor_name, country_code)
        
        return queries
    
    def _generate_facebook_queries(self, competitor_name: str, country_code: str) -> List[str]:
        """Generate Facebook-specific search queries"""
        queries = []
        
        # Basic complaint queries
        for keyword in self.complaint_keywords[:10]:  # Top 10 complaint keywords
            queries.append(f'site:facebook.com "{competitor_name}" {keyword}')
        
        # Support-related queries
        for keyword in self.support_keywords[:5]:
            queries.append(f'site:facebook.com "{competitor_name}" "{keyword}"')
        
        # Billing queries
        for keyword in self.billing_keywords[:5]:
            queries.append(f'site:facebook.com "{competitor_name}" "{keyword}"')
        
        # Performance queries
        for keyword in self.performance_keywords[:5]:
            queries.append(f'site:facebook.com "{competitor_name}" "{keyword}"')
        
        return queries
    
    def _generate_twitter_queries(self, competitor_name: str, country_code: str) -> List[str]:
        """Generate Twitter/X-specific search queries"""
        queries = []
        
        # Twitter domain variations
        twitter_domains = ['twitter.com', 'x.com']
        
        for domain in twitter_domains:
            # Basic complaint queries
            queries.append(f'site:{domain} "{competitor_name}" problem OR issue OR complaint')
            queries.append(f'site:{domain} "{competitor_name}" terrible OR awful OR worst')
            queries.append(f'site:{domain} "{competitor_name}" support OR help OR "customer service"')
            queries.append(f'site:{domain} "{competitor_name}" billing OR payment OR "hidden fee"')
            queries.append(f'site:{domain} "{competitor_name}" slow OR crash OR down OR offline')
            
            # Specific complaint patterns
            queries.append(f'site:{domain} "{competitor_name}" "doesn\'t work" OR "not working"')
            queries.append(f'site:{domain} "{competitor_name}" "waste of money" OR "regret buying"')
            queries.append(f'site:{domain} "{competitor_name}" "avoid" OR "don\'t use"')
        
        return queries
    
    def _generate_youtube_queries(self, competitor_name: str, country_code: str) -> List[str]:
        """Generate YouTube-specific search queries"""
        queries = []
        
        # Review and comparison videos
        queries.append(f'site:youtube.com "{competitor_name} review" problems OR issues')
        queries.append(f'site:youtube.com "{competitor_name} vs" comparison complaints')
        queries.append(f'site:youtube.com "{competitor_name}" "not good" OR "disappointed"')
        queries.append(f'site:youtube.com "{competitor_name}" "problems with" OR "issues with"')
        queries.append(f'site:youtube.com "{competitor_name}" "why I stopped using"')
        queries.append(f'site:youtube.com "{competitor_name}" "honest review" OR "real review"')
        
        return queries
    
    def _generate_instagram_queries(self, competitor_name: str, country_code: str) -> List[str]:
        """Generate Instagram-specific search queries"""
        queries = []
        
        # Instagram complaint queries (limited due to platform restrictions)
        queries.append(f'site:instagram.com "{competitor_name}" problem OR issue')
        queries.append(f'site:instagram.com "{competitor_name}" support OR help')
        queries.append(f'site:instagram.com "{competitor_name}" disappointed OR frustrated')
        
        return queries
    
    def _generate_linkedin_queries(self, competitor_name: str, country_code: str) -> List[str]:
        """Generate LinkedIn-specific search queries"""
        queries = []
        
        # Professional complaints and discussions
        queries.append(f'site:linkedin.com "{competitor_name}" challenges OR problems')
        queries.append(f'site:linkedin.com "{competitor_name}" "customer experience" issues')
        queries.append(f'site:linkedin.com "{competitor_name}" "not recommended" OR "avoid"')
        queries.append(f'site:linkedin.com "{competitor_name}" "poor service" OR "bad experience"')
        
        return queries
    
    def _generate_reddit_queries(self, competitor_name: str, country_code: str) -> List[str]:
        """Generate Reddit-specific search queries"""
        queries = []
        
        # Reddit complaint discussions
        queries.append(f'site:reddit.com "{competitor_name}" complaints OR problems')
        queries.append(f'site:reddit.com "{competitor_name}" "bad experience" OR "terrible"')
        queries.append(f'site:reddit.com "{competitor_name}" "customer service" OR support')
        queries.append(f'site:reddit.com "{competitor_name}" "not worth it" OR "waste of money"')
        queries.append(f'site:reddit.com "{competitor_name}" "alternatives to" OR "better than"')
        queries.append(f'site:reddit.com "{competitor_name}" billing OR pricing OR "hidden fees"')
        
        return queries
    
    def _generate_wechat_queries(self, competitor_name: str, country_code: str) -> List[str]:
        """Generate WeChat-specific search queries (for Chinese market)"""
        queries = []
        
        # WeChat public account complaints
        queries.append(f'site:weixin.qq.com "{competitor_name}" 问题 OR 投诉')  # problems or complaints
        queries.append(f'site:weixin.qq.com "{competitor_name}" 服务 OR 支持')    # service or support
        
        return queries
    
    def _generate_vk_queries(self, competitor_name: str, country_code: str) -> List[str]:
        """Generate VK-specific search queries (for Russian market)"""
        queries = []
        
        # VK complaints in Russian
        queries.append(f'site:vk.com "{competitor_name}" проблема OR жалоба')  # problem or complaint
        queries.append(f'site:vk.com "{competitor_name}" поддержка OR помощь')  # support or help
        
        return queries
    
    def _generate_line_queries(self, competitor_name: str, country_code: str) -> List[str]:
        """Generate LINE-specific search queries (for Thai/Japanese market)"""
        queries = []
        
        # LINE platform queries
        queries.append(f'site:line.me "{competitor_name}" problem OR issue')
        queries.append(f'site:line.me "{competitor_name}" support OR help')
        
        return queries
    
    def _generate_g2_queries(self, competitor_name: str, country_code: str) -> List[str]:
        """Generate G2-specific search queries"""
        queries = []
        
        # G2 review site queries
        queries.append(f'site:g2.com "{competitor_name}" negative OR disappointed')
        queries.append(f'site:g2.com "{competitor_name}" "not recommended" OR "avoid"')
        queries.append(f'site:g2.com "{competitor_name}" problems OR issues OR complaints')
        queries.append(f'site:g2.com "{competitor_name}" "poor support" OR "bad service"')
        queries.append(f'site:g2.com "{competitor_name}" "expensive" OR "overpriced"')
        
        return queries
    
    def _generate_capterra_queries(self, competitor_name: str, country_code: str) -> List[str]:
        """Generate Capterra-specific search queries"""
        queries = []
        
        # Capterra review queries
        queries.append(f'site:capterra.com "{competitor_name}" negative OR disappointed')
        queries.append(f'site:capterra.com "{competitor_name}" problems OR issues')
        queries.append(f'site:capterra.com "{competitor_name}" "not satisfied" OR "regret"')
        queries.append(f'site:capterra.com "{competitor_name}" "poor quality" OR "unreliable"')
        
        return queries
    
    def _generate_trustpilot_queries(self, competitor_name: str, country_code: str) -> List[str]:
        """Generate TrustPilot-specific search queries"""
        queries = []
        
        # TrustPilot review queries
        queries.append(f'site:trustpilot.com "{competitor_name}" negative OR "1 star" OR "2 star"')
        queries.append(f'site:trustpilot.com "{competitor_name}" complaints OR problems')
        queries.append(f'site:trustpilot.com "{competitor_name}" "terrible" OR "awful"')
        queries.append(f'site:trustpilot.com "{competitor_name}" "customer service" OR support')
        
        return queries
    
    def _generate_getapp_queries(self, competitor_name: str, country_code: str) -> List[str]:
        """Generate GetApp-specific search queries"""
        queries = []
        
        # GetApp review queries
        queries.append(f'site:getapp.com "{competitor_name}" negative OR disappointed')
        queries.append(f'site:getapp.com "{competitor_name}" problems OR issues')
        queries.append(f'site:getapp.com "{competitor_name}" "not good" OR "poor"')
        
        return queries
    
    def _generate_software_advice_queries(self, competitor_name: str, country_code: str) -> List[str]:
        """Generate Software Advice-specific search queries"""
        queries = []
        
        # Software Advice review queries
        queries.append(f'site:softwareadvice.com "{competitor_name}" negative OR disappointed')
        queries.append(f'site:softwareadvice.com "{competitor_name}" problems OR issues')
        queries.append(f'site:softwareadvice.com "{competitor_name}" "not recommended"')
        
        return queries


class GoogleSearchScraper:
    """
    Scrapes Google search results for competitor complaints and reviews
    
    Features:
    - Country-specific Google domains
    - Search result parsing
    - Rate limiting and respectful crawling
    - Result filtering and ranking
    """
    
    def __init__(self, config=None):
        """
        Initialize the Google search scraper
        
        Args:
            config: Configuration object with scraping parameters
        """
        self.config = config
        self.logger = logging.getLogger("competitive_analysis")
        self.scraper = WebScraper(config)
        
        # Search parameters
        self.results_per_query = getattr(config, 'google_results_per_query', 10)
        self.max_queries_per_platform = getattr(config, 'max_queries_per_platform', 5)
        self.search_delay = getattr(config, 'google_search_delay', 2.0)
        
        # User agents specifically for Google searches
        self.search_user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
    
    @log_execution_time
    @log_function_call
    def search_competitor_complaints(self, competitor_name: str, country_code: str = 'US') -> Dict[str, Any]:
        """
        Search for competitor complaints across all platforms
        
        Args:
            competitor_name: Name of the competitor
            country_code: Country code for localized search
            
        Returns:
            Dictionary with search results organized by platform
        """
        self.logger.info(f"Starting Google search for {competitor_name} complaints (country: {country_code})")
        
        # Initialize query generator
        query_generator = GoogleSearchQueryGenerator(self.config)
        
        # Generate queries for different platforms
        platform_queries = query_generator.generate_platform_queries(competitor_name, country_code)
        review_queries = query_generator.generate_review_site_queries(competitor_name, country_code)
        
        # Combine all queries
        all_queries = {**platform_queries, **review_queries}
        
        results = {
            'competitor_name': competitor_name,
            'country_code': country_code,
            'search_timestamp': datetime.now().isoformat(),
            'platforms': {},
            'summary': {
                'total_platforms': len(all_queries),
                'total_queries': sum(len(queries) for queries in all_queries.values()),
                'successful_searches': 0,
                'failed_searches': 0,
                'total_results': 0
            }
        }
        
        # Execute searches for each platform
        for platform, queries in all_queries.items():
            self.logger.info(f"Searching {platform} for {competitor_name} complaints")
            
            # Limit queries per platform
            limited_queries = queries[:self.max_queries_per_platform]
            
            platform_results = self._search_platform(platform, limited_queries, country_code)
            results['platforms'][platform] = platform_results
            
            # Update summary
            results['summary']['successful_searches'] += platform_results['successful_queries']
            results['summary']['failed_searches'] += platform_results['failed_queries']
            results['summary']['total_results'] += platform_results['total_results']
        
        # Calculate overall success rate
        total_queries = results['summary']['successful_searches'] + results['summary']['failed_searches']
        if total_queries > 0:
            results['summary']['success_rate'] = (results['summary']['successful_searches'] / total_queries) * 100
        else:
            results['summary']['success_rate'] = 0
        
        self.logger.info(f"Google search completed. Success rate: {results['summary']['success_rate']:.1f}%")
        
        return results
    
    @log_execution_time
    @log_function_call
    def search_competitor_website(self, competitor_name: str, country_code: str = 'US') -> Dict[str, Any]:
        """
        Search for competitor's official website using Google search
        
        Args:
            competitor_name: Name of the competitor
            country_code: Country code for localized search
            
        Returns:
            Dictionary with search results including official website URL
        """
        self.logger.info(f"Searching for official website of {competitor_name} in {country_code}")
        
        # Get country-specific Google domain
        google_domain = country_localization.get_google_search_domain(country_code)
        
        # Generate search queries for finding official website
        search_queries = [
            f'"{competitor_name}" official website',
            f'"{competitor_name}" site:',
            f'{competitor_name} POS system',
            f'{competitor_name} company website',
            f'{competitor_name} homepage'
        ]
        
        results = {
            'competitor_name': competitor_name,
            'country_code': country_code,
            'search_queries': search_queries,
            'official_website': None,
            'candidate_urls': [],
            'search_results': []
        }
        
        try:
            for query in search_queries:
                self.logger.info(f"Executing search query: {query}")
                
                # Execute Google search
                search_results = self._execute_google_search(query, google_domain, country_code)
                
                if search_results:
                    results['search_results'].extend(search_results)
                    
                    # Extract potential official website URLs
                    for result in search_results:
                        url = result.get('url', '')
                        title = result.get('title', '')
                        
                        # Score URL based on likelihood of being official website
                        if self._is_likely_official_website(url, title, competitor_name):
                            results['candidate_urls'].append({
                                'url': url,
                                'title': title,
                                'score': self._calculate_website_score(url, title, competitor_name),
                                'description': result.get('description', '')
                            })
                
                # Rate limiting
                time.sleep(self.config.rate_limit_delay if self.config else 2)
            
            # Sort candidates by score and select best match
            if results['candidate_urls']:
                results['candidate_urls'].sort(key=lambda x: x['score'], reverse=True)
                results['official_website'] = results['candidate_urls'][0]['url']
                
            self.logger.info(f"Website search completed for {competitor_name}")
            self.logger.info(f"Official website found: {results['official_website']}")
            self.logger.info(f"Total candidates found: {len(results['candidate_urls'])}")
            
        except Exception as e:
            self.logger.error(f"Error searching for competitor website: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def _search_platform(self, platform: str, queries: List[str], country_code: str) -> Dict[str, Any]:
        """
        Search specific platform with given queries
        
        Args:
            platform: Platform name
            queries: List of search queries
            country_code: Country code for localized search
            
        Returns:
            Platform-specific search results
        """
        platform_results = {
            'platform': platform,
            'queries_executed': [],
            'search_results': [],
            'successful_queries': 0,
            'failed_queries': 0,
            'total_results': 0
        }
        
        # Get country-specific Google domain
        google_domain = country_localization.get_google_search_domain(country_code)
        
        for query in queries:
            try:
                # Rate limiting
                time.sleep(self.search_delay + random.uniform(0, 1))
                
                # Execute search
                search_results = self._execute_google_search(query, google_domain, country_code)
                
                if search_results:
                    query_result = {
                        'query': query,
                        'results': search_results,
                        'result_count': len(search_results),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    platform_results['queries_executed'].append(query_result)
                    platform_results['search_results'].extend(search_results)
                    platform_results['successful_queries'] += 1
                    platform_results['total_results'] += len(search_results)
                    
                    self.logger.debug(f"Query '{query}' returned {len(search_results)} results")
                else:
                    platform_results['failed_queries'] += 1
                    self.logger.warning(f"Query '{query}' failed")
                    
            except Exception as e:
                platform_results['failed_queries'] += 1
                self.logger.error(f"Error executing query '{query}': {str(e)}")
        
        # Remove duplicate results
        platform_results['search_results'] = self._deduplicate_results(platform_results['search_results'])
        platform_results['total_results'] = len(platform_results['search_results'])
        
        return platform_results
    
    def _execute_google_search(self, query: str, google_domain: str, country_code: str) -> List[Dict[str, Any]]:
        """
        Execute a single Google search query
        
        Args:
            query: Search query
            google_domain: Google domain for country
            country_code: Country code
            
        Returns:
            List of search results
        """
        try:
            # Build search URL
            search_url = self._build_search_url(query, google_domain, country_code)
            
            # Use different user agent for Google searches
            original_user_agent = self.scraper.session.headers.get('User-Agent')
            self.scraper.session.headers['User-Agent'] = random.choice(self.search_user_agents)
            
            # Scrape search results page
            scraped_data = self.scraper.scrape_page(search_url, extract_content=True, country_code=country_code)
            
            # Restore original user agent
            if original_user_agent:
                self.scraper.session.headers['User-Agent'] = original_user_agent
            
            if scraped_data:
                # Parse search results
                results = self._parse_google_results(scraped_data, query)
                return results
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error executing Google search for '{query}': {str(e)}")
            return []
    
    def _build_search_url(self, query: str, google_domain: str, country_code: str) -> str:
        """
        Build Google search URL with proper parameters
        
        Args:
            query: Search query
            google_domain: Google domain
            country_code: Country code
            
        Returns:
            Complete search URL
        """
        # Base parameters
        params = {
            'q': query,
            'num': self.results_per_query,
            'hl': 'en',  # Interface language
            'lr': 'lang_en',  # Results language
            'safe': 'off',
            'filter': '0'  # Don't filter similar results
        }
        
        # Add country-specific parameters
        if country_code and country_code != 'GLOBAL':
            params['gl'] = country_code.lower()
        
        # Build URL
        search_url = f"https://{google_domain}/search?{urlencode(params)}"
        
        return search_url
    
    def _parse_google_results(self, scraped_data: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """
        Parse Google search results from scraped data
        
        Args:
            scraped_data: Scraped search results page
            query: Original search query
            
        Returns:
            List of parsed search results
        """
        results = []
        
        try:
            # Parse HTML content
            soup = BeautifulSoup(scraped_data.get('html', ''), 'html.parser')
            
            # Find search result containers
            result_containers = soup.find_all('div', class_='g')
            
            for container in result_containers:
                try:
                    # Extract title
                    title_elem = container.find('h3')
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    
                    # Extract URL
                    link_elem = container.find('a')
                    url = link_elem.get('href') if link_elem else ''
                    
                    # Extract description/snippet
                    desc_elem = container.find('span', class_='st') or container.find('div', class_='s')
                    if not desc_elem:
                        # Try alternative selectors
                        desc_elem = container.find('div', {'data-sncf': '1'}) or container.find('div', class_='IsZvec')
                    
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    # Skip if essential data is missing
                    if not title or not url or not description:
                        continue
                    
                    # Clean URL (remove Google redirect)
                    clean_url = self._clean_google_url(url)
                    
                    # Create result entry
                    result = {
                        'title': title,
                        'url': clean_url,
                        'description': description,
                        'query': query,
                        'platform': self._extract_platform_from_url(clean_url),
                        'complaint_score': self._calculate_complaint_score(title, description),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    self.logger.debug(f"Error parsing individual search result: {str(e)}")
                    continue
            
            self.logger.debug(f"Parsed {len(results)} search results from Google")
            
        except Exception as e:
            self.logger.error(f"Error parsing Google search results: {str(e)}")
        
        return results
    
    def _clean_google_url(self, url: str) -> str:
        """
        Clean Google search result URL (remove redirects)
        
        Args:
            url: Raw URL from Google results
            
        Returns:
            Clean URL
        """
        try:
            # Handle Google redirect URLs
            if url.startswith('/url?'):
                parsed = urlparse(url)
                query_params = parse_qs(parsed.query)
                if 'url' in query_params:
                    return query_params['url'][0]
                elif 'q' in query_params:
                    return query_params['q'][0]
            
            # Handle relative URLs
            elif url.startswith('/'):
                return f"https://www.google.com{url}"
            
            return url
            
        except Exception:
            return url
    
    def _extract_platform_from_url(self, url: str) -> str:
        """
        Extract platform name from URL
        
        Args:
            url: URL to analyze
            
        Returns:
            Platform name
        """
        try:
            domain = urlparse(url).netloc.lower()
            
            # Platform mapping
            platform_map = {
                'facebook.com': 'Facebook',
                'twitter.com': 'Twitter',
                'x.com': 'Twitter',
                'youtube.com': 'YouTube',
                'instagram.com': 'Instagram',
                'linkedin.com': 'LinkedIn',
                'reddit.com': 'Reddit',
                'g2.com': 'G2',
                'capterra.com': 'Capterra',
                'trustpilot.com': 'TrustPilot',
                'getapp.com': 'GetApp',
                'softwareadvice.com': 'Software Advice',
                'weixin.qq.com': 'WeChat',
                'vk.com': 'VK',
                'line.me': 'LINE'
            }
            
            for domain_key, platform in platform_map.items():
                if domain_key in domain:
                    return platform
            
            return 'Other'
            
        except Exception:
            return 'Unknown'
    
    def _calculate_complaint_score(self, title: str, description: str) -> float:
        """
        Calculate complaint relevance score
        
        Args:
            title: Result title
            description: Result description
            
        Returns:
            Complaint score (0-1)
        """
        text = f"{title} {description}".lower()
        
        # Negative keywords with weights
        negative_keywords = {
            'terrible': 0.9, 'awful': 0.9, 'worst': 0.8, 'hate': 0.8,
            'disappointed': 0.7, 'frustrated': 0.7, 'angry': 0.7,
            'complaint': 0.8, 'problem': 0.7, 'issue': 0.6, 'bug': 0.6,
            'broken': 0.8, 'doesn\'t work': 0.9, 'not working': 0.8,
            'support': 0.5, 'help': 0.4, 'slow': 0.6, 'expensive': 0.6,
            'overpriced': 0.7, 'hidden fee': 0.8, 'waste of money': 0.9,
            'regret': 0.8, 'avoid': 0.9, 'poor quality': 0.8,
            'unreliable': 0.7, 'crashed': 0.8, 'down': 0.6, 'offline': 0.7
        }
        
        score = 0.0
        word_count = 0
        
        for keyword, weight in negative_keywords.items():
            if keyword in text:
                score += weight
                word_count += 1
        
        # Normalize score
        if word_count > 0:
            score = min(score / word_count, 1.0)
        
        return score
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate search results
        
        Args:
            results: List of search results
            
        Returns:
            Deduplicated results
        """
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results

    def _is_likely_official_website(self, url: str, title: str, competitor_name: str) -> bool:
        """
        Check if a URL is likely to be the official website of the competitor
        
        Args:
            url: URL to check
            title: Page title
            competitor_name: Name of the competitor
            
        Returns:
            Boolean indicating if URL is likely official website
        """
        if not url:
            return False
        
        # Clean competitor name for comparison
        clean_competitor = competitor_name.lower().replace(' ', '').replace('pos', '').replace('system', '')
        
        # Check if URL contains competitor name
        url_lower = url.lower()
        title_lower = title.lower()
        
        # Positive indicators
        positive_indicators = [
            clean_competitor in url_lower,
            'official' in title_lower,
            'homepage' in title_lower,
            url_lower.startswith('https://www.'),
            url_lower.endswith('.com'),
            url_lower.endswith('.com/'),
            not any(x in url_lower for x in ['review', 'complaint', 'forum', 'reddit', 'facebook', 'twitter', 'linkedin', 'youtube'])
        ]
        
        # Negative indicators
        negative_indicators = [
            'wikipedia' in url_lower,
            'crunchbase' in url_lower,
            'linkedin' in url_lower,
            'facebook' in url_lower,
            'twitter' in url_lower,
            'youtube' in url_lower,
            'reddit' in url_lower,
            'review' in url_lower,
            'complaint' in url_lower,
            'vs' in url_lower,
            'alternative' in url_lower
        ]
        
        return sum(positive_indicators) > sum(negative_indicators)
    
    def _calculate_website_score(self, url: str, title: str, competitor_name: str) -> float:
        """
        Calculate a score for how likely a URL is to be the official website
        
        Args:
            url: URL to score
            title: Page title
            competitor_name: Name of the competitor
            
        Returns:
            Score between 0 and 1
        """
        score = 0.0
        
        if not url:
            return score
        
        # Clean competitor name for comparison
        clean_competitor = competitor_name.lower().replace(' ', '').replace('pos', '').replace('system', '')
        url_lower = url.lower()
        title_lower = title.lower()
        
        # URL structure scoring
        if clean_competitor in url_lower:
            score += 0.4
        if url_lower.startswith('https://www.'):
            score += 0.1
        if url_lower.endswith('.com') or url_lower.endswith('.com/'):
            score += 0.1
        if '/' not in url_lower[8:]:  # Only domain, no path
            score += 0.1
        
        # Title scoring
        if clean_competitor in title_lower:
            score += 0.2
        if 'official' in title_lower:
            score += 0.1
        if 'homepage' in title_lower:
            score += 0.1
        
        # Penalty for third-party sites
        penalty_sites = ['wikipedia', 'crunchbase', 'linkedin', 'facebook', 'twitter', 'youtube', 'reddit', 'review', 'complaint', 'vs', 'alternative', 'comparison']
        for site in penalty_sites:
            if site in url_lower:
                score -= 0.3
                break
        
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1


def analyze_complaint_patterns(search_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze patterns in complaint search results
    
    Args:
        search_results: Search results from GoogleSearchScraper
        
    Returns:
        Analysis of complaint patterns
    """
    analysis = {
        'total_complaints': 0,
        'platforms': {},
        'complaint_categories': {
            'Product Issues': 0,
            'Support Issues': 0,
            'Billing Issues': 0,
            'Performance Issues': 0,
            'General Complaints': 0
        },
        'top_complaints': []
    }
    
    all_results = []
    
    # Collect all results from all platforms
    for platform, platform_data in search_results.get('platforms', {}).items():
        platform_results = platform_data.get('search_results', [])
        all_results.extend(platform_results)
        
        # Platform-specific analysis
        analysis['platforms'][platform] = {
            'total_results': len(platform_results),
            'avg_complaint_score': 0,
            'top_complaints': []
        }
        
        if platform_results:
            # Calculate average complaint score
            scores = [r.get('complaint_score', 0) for r in platform_results]
            analysis['platforms'][platform]['avg_complaint_score'] = sum(scores) / len(scores)
            
            # Get top complaints for this platform
            sorted_results = sorted(platform_results, key=lambda x: x.get('complaint_score', 0), reverse=True)
            analysis['platforms'][platform]['top_complaints'] = sorted_results[:5]
    
    # Overall analysis
    analysis['total_complaints'] = len(all_results)
    
    # Categorize complaints
    for result in all_results:
        title = result.get('title', '').lower()
        description = result.get('description', '').lower()
        text = f"{title} {description}"
        
        # Categorize complaint
        if any(keyword in text for keyword in ['bug', 'broken', 'doesn\'t work', 'error', 'glitch']):
            analysis['complaint_categories']['Product Issues'] += 1
        elif any(keyword in text for keyword in ['support', 'help', 'customer service', 'response']):
            analysis['complaint_categories']['Support Issues'] += 1
        elif any(keyword in text for keyword in ['billing', 'payment', 'fee', 'charge', 'expensive']):
            analysis['complaint_categories']['Billing Issues'] += 1
        elif any(keyword in text for keyword in ['slow', 'performance', 'lag', 'crash', 'timeout']):
            analysis['complaint_categories']['Performance Issues'] += 1
        else:
            analysis['complaint_categories']['General Complaints'] += 1
    
    # Top overall complaints
    sorted_results = sorted(all_results, key=lambda x: x.get('complaint_score', 0), reverse=True)
    analysis['top_complaints'] = sorted_results[:10]
    
    return analysis 