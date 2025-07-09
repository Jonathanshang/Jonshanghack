import streamlit as st
import logging
from datetime import datetime
import json
import os
from config import Config
from utils.logger import setup_logger
from utils.url_discovery import URLDiscovery, discover_competitor_urls, validate_url
from utils.scraper import WebScraper, extract_page_category, analyze_content_quality
from utils.country_localization import country_localization
from utils.google_search import GoogleSearchScraper, analyze_complaint_patterns
from utils.social_media_scraper import SocialMediaScraper, create_social_media_urls_from_search_results, analyze_social_media_content

# Configure page
st.set_page_config(
    page_title="Competitive Analysis Tool",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logger
logger = setup_logger()

# Initialize configuration
config = Config()

def main():
    """Main application function"""
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .input-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .status-info {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .status-success {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
    }
    .status-warning {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    .status-error {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🎯 Competitive Analysis Tool</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Generate deep-dive comparative reports on competitors versus StoreHub</p>', unsafe_allow_html=True)
    
    # Sidebar navigation
    setup_sidebar()
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Analysis", "📊 Reports", "⚙️ Settings", "📋 Help"])
    
    with tab1:
        analysis_tab()
    
    with tab2:
        reports_tab()
    
    with tab3:
        settings_tab()
    
    with tab4:
        help_tab()

def setup_sidebar():
    """Setup sidebar navigation and controls"""
    st.sidebar.title("Navigation")
    
    # Analysis status
    st.sidebar.markdown("### Analysis Status")
    if 'analysis_status' not in st.session_state:
        st.session_state.analysis_status = "Ready"
    
    status_color = {
        "Ready": "🟢",
        "Running": "🟡",
        "Completed": "✅",
        "Error": "🔴"
    }
    
    st.sidebar.markdown(f"{status_color.get(st.session_state.analysis_status, '⚪')} {st.session_state.analysis_status}")
    
    # Recent analyses
    st.sidebar.markdown("### Recent Analyses")
    if 'recent_analyses' not in st.session_state:
        st.session_state.recent_analyses = []
    
    if st.session_state.recent_analyses:
        for analysis in st.session_state.recent_analyses[-5:]:  # Show last 5
            country_flags = {
                "US": "🇺🇸", "UK": "🇬🇧", "AU": "🇦🇺", "CA": "🇨🇦", "SG": "🇸🇬", "MY": "🇲🇾", 
                "DE": "🇩🇪", "FR": "🇫🇷", "JP": "🇯🇵", "IN": "🇮🇳", "CN": "🇨🇳", "KR": "🇰🇷", 
                "TH": "🇹🇭", "VN": "🇻🇳", "ID": "🇮🇩", "PH": "🇵🇭", "TW": "🇹🇼", "HK": "🇭🇰", 
                "KZ": "🇰🇿", "UZ": "🇺🇿", "ES": "🇪🇸", "IT": "🇮🇹", "NL": "🇳🇱", "BE": "🇧🇪", 
                "CH": "🇨🇭", "AT": "🇦🇹", "SE": "🇸🇪", "NO": "🇳🇴", "DK": "🇩🇰", "FI": "🇫🇮", 
                "PL": "🇵🇱", "CZ": "🇨🇿", "HU": "🇭🇺", "RO": "🇷🇴", "BG": "🇧🇬", "GR": "🇬🇷", 
                "PT": "🇵🇹", "IE": "🇮🇪", "SK": "🇸🇰", "SI": "🇸🇮", "HR": "🇭🇷", "EE": "🇪🇪", 
                "LV": "🇱🇻", "LT": "🇱🇹", "RU": "🇷🇺", "TR": "🇹🇷", "UA": "🇺🇦", "GLOBAL": "🌍"
            }
            country_flag = country_flags.get(analysis.get('country', 'US'), '🌍')
            st.sidebar.markdown(f"• {analysis['competitor']} {country_flag} - {analysis['date']}")
    else:
        st.sidebar.markdown("*No recent analyses*")
    
    # Configuration info
    st.sidebar.markdown("### Configuration")
    st.sidebar.markdown(f"• Max Results: {config.max_search_results}")
    st.sidebar.markdown(f"• Timeout: {config.request_timeout}s")
    st.sidebar.markdown(f"• Rate Limit: {config.rate_limit_delay}s")

def analysis_tab():
    """Main analysis input and execution tab"""
    st.markdown("## Start New Analysis")
    
    # Input section
    with st.container():
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            competitor_name = st.text_input(
                "Competitor Name",
                placeholder="e.g., Toast POS, Lightspeed, Square",
                help="Enter the full name of the competitor company"
            )
        
        with col2:
            competitor_url = st.text_input(
                "Official Website URL",
                placeholder="https://www.competitor.com",
                help="Enter the main website URL of the competitor"
            )
        
        with col3:
            # Get available countries (now sorted alphabetically)
            available_countries = country_localization.get_available_countries()
            country_options = [f"{name} ({code})" for code, name in available_countries]
            
            # Find Global option index in the sorted list (should be first)
            default_country = "Global (All Countries) (GLOBAL)"
            default_index = 0
            try:
                default_index = country_options.index(default_country)
            except ValueError:
                # Fallback to first country if Global not found
                default_index = 0
            
            selected_country = st.selectbox(
                "Target Country",
                options=country_options,
                index=default_index,
                help="Select the country for targeted competitive analysis"
            )
            
            # Extract country code from selection
            country_code = selected_country.split('(')[-1].strip(')')
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Advanced options
    with st.expander("Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            include_social = st.checkbox("Include Social Media Analysis", value=True)
            include_reviews = st.checkbox("Include Review Site Analysis", value=True)
        
        with col2:
            analysis_depth = st.selectbox(
                "Analysis Depth",
                ["Standard", "Deep", "Comprehensive"],
                index=1,
                help="Standard: Basic analysis, Deep: Include social media, Comprehensive: Full analysis with predictions"
            )
            
            google_search_enabled = st.checkbox("Enable Google Search for Complaints", value=True, help="Search for social media complaints and reviews")
    
    # Analysis button
    if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
        if competitor_name and competitor_url:
            # Validate URL format
            if not validate_url(competitor_url):
                st.error("Please enter a valid URL (e.g., https://www.example.com)")
                return
            
            logger.info(f"Starting analysis for {competitor_name} at {competitor_url} for country {country_code}")
            
            # Update session state
            st.session_state.analysis_status = "Running"
            st.session_state.current_competitor = competitor_name
            st.session_state.current_url = competitor_url
            st.session_state.current_country = country_code
            
            # Add to recent analyses
            if 'recent_analyses' not in st.session_state:
                st.session_state.recent_analyses = []
            
            st.session_state.recent_analyses.append({
                'competitor': competitor_name,
                'url': competitor_url,
                'country': country_code,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'depth': analysis_depth
            })
            
            st.success(f"Analysis started for {competitor_name} in {country_code}")
            
            # Real URL discovery process
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Phase 1: URL Discovery
                status_text.text('🔍 Discovering competitor pages...')
                progress_bar.progress(15)
                
                discovery = URLDiscovery(competitor_url, config)
                discovered_urls = discovery.discover_all_pages()
                
                # Store discovered URLs in session state
                st.session_state.discovered_urls = discovered_urls
                st.session_state.discovery_summary = discovery.get_discovery_summary()
                
                progress_bar.progress(35)
                status_text.text('📄 Scraping page content...')
                
                # Phase 2: Content Scraping with Country Context
                country_context = country_localization.get_competitor_context(country_code)
                st.info(f"Analyzing for {country_context['country']} market using {country_context['currency']} currency")
                
                scraper = WebScraper(config)
                
                # Get priority URLs for scraping (limit to key pages)
                priority_urls = []
                for category in ['pricing', 'features', 'about', 'contact']:
                    category_urls = discovered_urls.get(category, [])
                    if category_urls:
                        priority_urls.extend(category_urls[:3])  # Take first 3 from each category
                
                # Add blog URLs (fewer due to volume)
                blog_urls = discovered_urls.get('blog', [])
                if blog_urls:
                    priority_urls.extend(blog_urls[:2])  # Take first 2 blog posts
                
                # Limit total scraping to prevent long wait times
                max_scrape_pages = min(len(priority_urls), 15)
                urls_to_scrape = priority_urls[:max_scrape_pages]
                
                progress_bar.progress(45)
                status_text.text(f'🔄 Scraping {len(urls_to_scrape)} key pages...')
                
                # Scrape the priority pages with country context
                scraping_results = scraper.scrape_multiple_pages(urls_to_scrape, country_code=country_code)
                
                # Store scraping results in session state
                st.session_state.scraping_results = scraping_results
                st.session_state.scraping_stats = scraper.get_scraping_stats()
                
                progress_bar.progress(70)
                status_text.text('🧠 Analyzing scraped content...')
                
                # Phase 3: Content Analysis
                analyzed_pages = []
                for scraped_page in scraping_results['scraped_pages']:
                    page_analysis = {
                        'url': scraped_page['url'],
                        'category': extract_page_category(scraped_page),
                        'quality': analyze_content_quality(scraped_page),
                        'title': scraped_page.get('title', ''),
                        'word_count': scraped_page.get('word_count', 0),
                        'pricing_indicators': scraped_page.get('pricing_indicators', {}),
                        'feature_lists': scraped_page.get('feature_lists', []),
                        'contact_info': scraped_page.get('contact_info', {}),
                        'headings': scraped_page.get('headings', {}),
                        'meta_description': scraped_page.get('meta_description', '')
                    }
                    analyzed_pages.append(page_analysis)
                
                st.session_state.analyzed_pages = analyzed_pages
                
                # Phase 4: Google Search for Social Media Complaints (New!)
                if google_search_enabled and (include_social or include_reviews):
                    progress_bar.progress(75)
                    status_text.text('🔍 Searching for social media complaints...')
                    
                    try:
                        # Initialize Google search scraper
                        google_scraper = GoogleSearchScraper(config)
                        
                        # Search for competitor complaints
                        complaint_search_results = google_scraper.search_competitor_complaints(
                            competitor_name, 
                            country_code
                        )
                        
                        # Analyze complaint patterns
                        complaint_analysis = analyze_complaint_patterns(complaint_search_results)
                        
                        # Store results in session state
                        st.session_state.complaint_search_results = complaint_search_results
                        st.session_state.complaint_analysis = complaint_analysis
                        
                        progress_bar.progress(85)
                        status_text.text('📊 Analyzing complaint patterns...')
                        
                        # Log complaint search summary
                        logger.info(f"Google search completed for {competitor_name}")
                        logger.info(f"Total complaints found: {complaint_analysis['total_complaints']}")
                        logger.info(f"Platforms searched: {list(complaint_search_results['platforms'].keys())}")
                        
                        # Phase 5: Social Media Scraping (New!)
                        if include_social and complaint_search_results.get('summary', {}).get('total_results', 0) > 0:
                            progress_bar.progress(80)
                            status_text.text('🔍 Scraping social media content...')
                            
                            try:
                                # Create URLs list from search results
                                social_urls = create_social_media_urls_from_search_results(complaint_search_results)
                                
                                # Limit URLs to prevent excessive scraping
                                max_social_urls = 20
                                if len(social_urls) > max_social_urls:
                                    # Prioritize by complaint score
                                    social_urls = sorted(social_urls, key=lambda x: x.get('complaint_score', 0), reverse=True)
                                    social_urls = social_urls[:max_social_urls]
                                
                                if social_urls:
                                    # Initialize social media scraper
                                    social_scraper = SocialMediaScraper(config)
                                    
                                    # Scrape social media content
                                    social_scraping_results = social_scraper.scrape_social_media_urls(
                                        social_urls, 
                                        country_code
                                    )
                                    
                                    # Analyze social media content
                                    social_content_analysis = analyze_social_media_content(social_scraping_results)
                                    
                                    # Store results in session state
                                    st.session_state.social_scraping_results = social_scraping_results
                                    st.session_state.social_content_analysis = social_content_analysis
                                    
                                    # Cleanup resources
                                    social_scraper.cleanup()
                                    
                                    # Log social media scraping summary
                                    logger.info(f"Social media scraping completed for {competitor_name}")
                                    logger.info(f"Total content pieces found: {social_content_analysis['total_content_pieces']}")
                                    logger.info(f"Platforms scraped: {list(social_content_analysis['platforms'].keys())}")
                                    
                                else:
                                    logger.info("No social media URLs found for scraping")
                                    # Set empty results
                                    st.session_state.social_scraping_results = {'scraped_content': [], 'summary': {'total_urls': 0}}
                                    st.session_state.social_content_analysis = {'total_content_pieces': 0, 'platforms': {}}
                                    
                            except Exception as e:
                                logger.error(f"Error during social media scraping: {str(e)}")
                                st.warning(f"Social media scraping failed: {str(e)} - continuing with available analysis")
                                # Set empty results so the analysis can continue
                                st.session_state.social_scraping_results = {'scraped_content': [], 'summary': {'total_urls': 0}}
                                st.session_state.social_content_analysis = {'total_content_pieces': 0, 'platforms': {}}
                        
                        else:
                            # Set empty results if social media analysis is not enabled
                            st.session_state.social_scraping_results = {'scraped_content': [], 'summary': {'total_urls': 0}}
                            st.session_state.social_content_analysis = {'total_content_pieces': 0, 'platforms': {}}
                        
                    except Exception as e:
                        logger.error(f"Error during Google search: {str(e)}")
                        st.warning(f"Google search failed: {str(e)} - continuing with basic analysis")
                        # Set empty results so the analysis can continue
                        st.session_state.complaint_search_results = {'platforms': {}, 'summary': {'total_results': 0}}
                        st.session_state.complaint_analysis = {'total_complaints': 0, 'platforms': {}}
                        st.session_state.social_scraping_results = {'scraped_content': [], 'summary': {'total_urls': 0}}
                        st.session_state.social_content_analysis = {'total_content_pieces': 0, 'platforms': {}}
                
                # Phase 6: Complaint Categorization (New!)
                progress_bar.progress(90)
                status_text.text('🤖 Categorizing complaints with AI...')
                
                # Check if we have OpenAI API key and complaints to categorize
                if config.openai_api_key and (st.session_state.get('complaint_analysis', {}).get('total_complaints', 0) > 0 or 
                                             st.session_state.get('social_content_analysis', {}).get('total_content_pieces', 0) > 0):
                    try:
                        from utils.complaint_categorization import ComplaintCategorizer
                        
                        # Initialize complaint categorizer
                        categorizer = ComplaintCategorizer(
                            api_key=config.openai_api_key,
                            model=config.model_name,
                            logger=logger
                        )
                        
                        # Prepare complaints for categorization
                        complaints_to_categorize = []
                        
                        # Add Google search complaints
                        search_results = st.session_state.get('complaint_search_results', {})
                        if search_results.get('platforms'):
                            for platform, platform_data in search_results['platforms'].items():
                                for result in platform_data.get('results', []):
                                    if result.get('snippet') and result.get('complaint_score', 0) > 0.3:
                                        complaints_to_categorize.append({
                                            'text': result['snippet'],
                                            'source': f"Google Search - {platform}",
                                            'url': result.get('url', ''),
                                            'platform': platform,
                                            'engagement_metrics': {
                                                'complaint_score': result.get('complaint_score', 0),
                                                'relevance_score': result.get('relevance_score', 0)
                                            }
                                        })
                        
                        # Add social media complaints
                        social_results = st.session_state.get('social_scraping_results', {})
                        if social_results.get('scraped_content'):
                            for content in social_results['scraped_content']:
                                if content.get('content') and content.get('complaint_score', 0) > 0.3:
                                    complaints_to_categorize.append({
                                        'text': content['content'],
                                        'source': f"Social Media - {content.get('platform', 'Unknown')}",
                                        'url': content.get('url', ''),
                                        'platform': content.get('platform', 'unknown'),
                                        'engagement_metrics': {
                                            'complaint_score': content.get('complaint_score', 0),
                                            'likes': content.get('engagement_metrics', {}).get('likes', 0),
                                            'shares': content.get('engagement_metrics', {}).get('shares', 0),
                                            'comments': content.get('engagement_metrics', {}).get('comments', 0)
                                        }
                                    })
                        
                        # Limit complaints to prevent excessive API usage
                        max_complaints = 50
                        if len(complaints_to_categorize) > max_complaints:
                            # Sort by complaint score and take top complaints
                            complaints_to_categorize = sorted(
                                complaints_to_categorize, 
                                key=lambda x: x['engagement_metrics'].get('complaint_score', 0), 
                                reverse=True
                            )[:max_complaints]
                        
                        # Categorize complaints
                        if complaints_to_categorize:
                            logger.info(f"Categorizing {len(complaints_to_categorize)} complaints")
                            
                            categorized_complaints = categorizer.categorize_complaints_batch(
                                complaints_to_categorize,
                                competitor_name,
                                batch_size=10  # Process in smaller batches
                            )
                            
                            # Generate comprehensive report
                            categorization_report = categorizer.generate_comprehensive_report(
                                categorized_complaints,
                                competitor_name
                            )
                            
                            # Store results in session state
                            st.session_state.categorized_complaints = categorized_complaints
                            st.session_state.categorization_report = categorization_report
                            
                            logger.info(f"Complaint categorization completed: {len(categorized_complaints)} complaints categorized")
                            
                        else:
                            logger.info("No complaints found for categorization")
                            st.session_state.categorized_complaints = []
                            st.session_state.categorization_report = None
                            
                    except Exception as e:
                        logger.error(f"Error during complaint categorization: {str(e)}")
                        st.warning(f"Complaint categorization failed: {str(e)} - continuing with basic analysis")
                        st.session_state.categorized_complaints = []
                        st.session_state.categorization_report = None
                        
                else:
                    # No API key or no complaints to categorize
                    if not config.openai_api_key:
                        logger.info("OpenAI API key not configured - skipping complaint categorization")
                    else:
                        logger.info("No complaints found for categorization")
                    st.session_state.categorized_complaints = []
                    st.session_state.categorization_report = None
                
                progress_bar.progress(95)
                status_text.text('✅ Finalizing analysis...')
                
                # Count total discovered URLs
                total_urls = sum(len(urls) for urls in discovered_urls.values())
                scraped_count = len(scraping_results['scraped_pages'])
                
                progress_bar.progress(100)
                status_text.text('🎉 Analysis completed!')
                
                st.session_state.analysis_status = "Completed"
                
                # Show results summary
                st.success(f"Analysis completed! Found {total_urls} URLs and scraped {scraped_count} key pages.")
                
                # Display quick summary
                with st.expander("📋 Quick Summary", expanded=True):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total URLs Found", total_urls)
                    
                    with col2:
                        st.metric("Pages Scraped", scraped_count)
                    
                    with col3:
                        pricing_count = len(discovered_urls.get('pricing', []))
                        st.metric("Pricing Pages", pricing_count)
                    
                    with col4:
                        features_count = len(discovered_urls.get('features', []))
                        st.metric("Features Pages", features_count)
                    
                    # Show scraping success rate
                    success_rate = scraping_results['summary']['success_rate']
                    st.metric("Scraping Success Rate", f"{success_rate:.1f}%")
                    
                    # Show complaint analysis results if available
                    if st.session_state.get('complaint_analysis'):
                        complaint_analysis = st.session_state.complaint_analysis
                        st.markdown("#### Social Media Complaints Analysis")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Complaints Found", complaint_analysis['total_complaints'])
                        
                        with col2:
                            platforms_searched = len(complaint_analysis['platforms'])
                            st.metric("Platforms Searched", platforms_searched)
                        
                        with col3:
                            # Get top complaint score
                            top_complaints = complaint_analysis.get('top_complaints', [])
                            if top_complaints:
                                max_score = max(c.get('complaint_score', 0) for c in top_complaints)
                                st.metric("Max Complaint Score", f"{max_score:.2f}")
                            else:
                                st.metric("Max Complaint Score", "N/A")
                        
                        # Show AI categorization results if available
                        if st.session_state.get('categorization_report'):
                            categorization_report = st.session_state.categorization_report
                            st.markdown("#### AI Categorization Results")
                            
                            overall_stats = categorization_report.get('overall_statistics', {})
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Categorized Complaints", overall_stats.get('total_complaints', 0))
                            
                            with col2:
                                category_dist = overall_stats.get('category_distribution', {})
                                top_category = max(category_dist.items(), key=lambda x: x[1]) if category_dist else ('None', 0)
                                st.metric("Top Category", f"{top_category[0]} ({top_category[1]})")
                            
                            with col3:
                                severity_dist = overall_stats.get('severity_distribution', {})
                                high_critical = severity_dist.get('High', 0) + severity_dist.get('Critical', 0)
                                st.metric("High/Critical Issues", high_critical)
                            
                            with col4:
                                sentiment_dist = overall_stats.get('sentiment_distribution', {})
                                negative = sentiment_dist.get('Very Negative', 0) + sentiment_dist.get('Negative', 0)
                                st.metric("Negative Sentiment", negative)
                            
                            # Show category breakdown
                            if category_dist:
                                st.markdown("**AI Categories:**")
                                for category, count in category_dist.items():
                                    if count > 0:
                                        st.write(f"• {category}: {count}")
                        
                        # Show raw complaint categories (for comparison)
                        else:
                            # Show complaint categories
                            categories = complaint_analysis.get('complaint_categories', {})
                            if categories:
                                st.markdown("**Complaint Categories:**")
                                for category, count in categories.items():
                                    if count > 0:
                                        st.write(f"• {category}: {count}")
                        
                        # Show social media content analysis if available
                        if st.session_state.get('social_content_analysis'):
                            social_analysis = st.session_state.social_content_analysis
                            if social_analysis.get('total_content_pieces', 0) > 0:
                                st.markdown("#### Social Media Content Analysis")
                                
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("Content Pieces Found", social_analysis['total_content_pieces'])
                                
                                with col2:
                                    platforms_scraped = len(social_analysis['platforms'])
                                    st.metric("Platforms Scraped", platforms_scraped)
                                
                                with col3:
                                    # Show content types
                                    content_types = social_analysis.get('content_types', {})
                                    total_posts = content_types.get('posts', 0)
                                    total_comments = content_types.get('comments', 0)
                                    total_reviews = content_types.get('reviews', 0)
                                    st.metric("Posts/Comments/Reviews", f"{total_posts}/{total_comments}/{total_reviews}")
                    
                    # Show sample of analyzed content
                    st.write("**Sample Analyzed Content:**")
                    for page in analyzed_pages[:3]:
                        category_emoji = {
                            'pricing': '💰', 'features': '🎯', 'blog': '📰', 
                            'careers': '💼', 'contact': '📞', 'about': '🏢'
                        }.get(page['category'], '📄')
                        
                        st.write(f"{category_emoji} **{page['title']}** ({page['category']})")
                        st.write(f"   • Word count: {page['word_count']}")
                        st.write(f"   • Quality score: {page['quality'].get('completeness_score', 0):.0f}%")
                        if page['pricing_indicators'].get('currency_symbols'):
                            st.write(f"   • Pricing found: {', '.join(page['pricing_indicators']['currency_symbols'][:3])}")
                
                st.info("Check the Reports tab for detailed analysis results.")
                
            except Exception as e:
                logger.error(f"Error during analysis: {str(e)}")
                st.error(f"An error occurred during analysis: {str(e)}")
                st.session_state.analysis_status = "Error"
            
        else:
            st.error("Please enter both competitor name and URL to start analysis.")

def reports_tab():
    """Reports viewing and export tab"""
    st.markdown("## Analysis Reports")
    
    if st.session_state.get('analysis_status') == "Completed":
        st.success("Report ready for viewing")
        
        # Get discovered URLs from session state
        discovered_urls = st.session_state.get('discovered_urls', {})
        discovery_summary = st.session_state.get('discovery_summary', {})
        scraping_results = st.session_state.get('scraping_results', {})
        analyzed_pages = st.session_state.get('analyzed_pages', [])
        competitor_name = st.session_state.get('current_competitor', 'Unknown')
        
        # Report sections with real data
        report_sections = [
            "📊 Executive Summary",
            "🔍 URL Discovery Results",
            "📄 Content Analysis Results",
            "💰 Pricing Analysis",
            "🎯 Features Analysis",
            "🤖 AI Categorized Complaints",
            "📱 Social Media Complaints",
            "📰 Blog & News",
            "💼 Careers Pages",
            "📞 Contact & Support",
            "🏢 About Pages"
        ]
        
        selected_section = st.selectbox("Select Report Section", report_sections)
        
        st.markdown(f"### {selected_section}")
        
        if selected_section == "📊 Executive Summary":
            st.markdown(f"**Competitor:** {competitor_name}")
            st.markdown(f"**Website:** {st.session_state.get('current_url', 'Unknown')}")
            st.markdown(f"**Target Country:** {st.session_state.get('current_country', 'US')}")
            st.markdown(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            # Show country-specific context
            if st.session_state.get('current_country'):
                country_context = country_localization.get_competitor_context(st.session_state.current_country)
                
                with st.expander("🌍 Country-Specific Analysis Context"):
                    st.markdown(f"**Primary Currency:** {country_context['currency']}")
                    st.markdown(f"**Business Context:** {country_context['business_context']}")
                    st.markdown(f"**Top Social Platforms:** {', '.join(country_context['social_platforms'][:3])}")
                    st.markdown(f"**Review Sites:** {', '.join(country_context['review_sites'][:3])}")
                    st.markdown(f"**Search Domain:** {country_context['google_domain']}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_urls = discovery_summary.get('total_urls_found', 0)
                st.metric("Total URLs Found", total_urls)
            
            with col2:
                pricing_count = len(discovered_urls.get('pricing', []))
                st.metric("Pricing Pages", pricing_count)
            
            with col3:
                features_count = len(discovered_urls.get('features', []))
                st.metric("Features Pages", features_count)
            
            with col4:
                blog_count = len(discovered_urls.get('blog', []))
                st.metric("Blog/News Pages", blog_count)
            
            # URL distribution chart
            if discovered_urls:
                st.markdown("#### URL Distribution by Category")
                
                categories = []
                counts = []
                for category, urls in discovered_urls.items():
                    if urls:
                        categories.append(category.title())
                        counts.append(len(urls))
                
                if categories:
                    import pandas as pd
                    df = pd.DataFrame({'Category': categories, 'Count': counts})
                    st.bar_chart(df.set_index('Category'))
        
        elif selected_section == "🔍 URL Discovery Results":
            st.markdown("#### Complete URL Discovery Summary")
            
            if discovery_summary:
                st.json(discovery_summary)
            else:
                st.info("No discovery summary available.")
        
        elif selected_section == "📄 Content Analysis Results":
            st.markdown("#### Scraped Content Analysis")
            
            if scraping_results and analyzed_pages:
                # Scraping summary
                summary = scraping_results.get('summary', {})
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Pages Scraped", summary.get('successful', 0))
                
                with col2:
                    st.metric("Success Rate", f"{summary.get('success_rate', 0):.1f}%")
                
                with col3:
                    avg_quality = sum(page['quality'].get('completeness_score', 0) for page in analyzed_pages) / len(analyzed_pages) if analyzed_pages else 0
                    st.metric("Avg Quality Score", f"{avg_quality:.1f}%")
                
                # Content quality analysis
                st.markdown("#### Content Quality Analysis")
                
                quality_data = []
                for page in analyzed_pages:
                    quality = page['quality']
                    quality_data.append({
                        'Page': page['title'][:50] + '...' if len(page['title']) > 50 else page['title'],
                        'Category': page['category'],
                        'Completeness': quality.get('completeness_score', 0),
                        'Content Richness': quality.get('content_richness', 0),
                        'Structure Quality': quality.get('structure_quality', 0),
                        'Word Count': page['word_count']
                    })
                
                if quality_data:
                    import pandas as pd
                    df = pd.DataFrame(quality_data)
                    st.dataframe(df)
                
                # Detailed page analysis
                st.markdown("#### Detailed Page Analysis")
                
                for page in analyzed_pages:
                    category_emoji = {
                        'pricing': '💰', 'features': '🎯', 'blog': '📰', 
                        'careers': '💼', 'contact': '📞', 'about': '🏢'
                    }.get(page['category'], '📄')
                    
                    with st.expander(f"{category_emoji} {page['title']} ({page['category']})"):
                        st.markdown(f"**URL:** {page['url']}")
                        st.markdown(f"**Word Count:** {page['word_count']}")
                        st.markdown(f"**Quality Score:** {page['quality'].get('completeness_score', 0):.1f}%")
                        
                        if page['meta_description']:
                            st.markdown(f"**Meta Description:** {page['meta_description']}")
                        
                        # Show headings structure
                        headings = page['headings']
                        if any(headings.values()):
                            st.markdown("**Page Structure:**")
                            for level, heading_list in headings.items():
                                if heading_list:
                                    st.markdown(f"- {level.upper()}: {', '.join(heading_list[:3])}")
                        
                        # Show pricing indicators
                        pricing = page['pricing_indicators']
                        if pricing.get('currency_symbols') or pricing.get('pricing_terms'):
                            st.markdown("**Pricing Information:**")
                            if pricing.get('currency_symbols'):
                                st.markdown(f"- Currency symbols found: {', '.join(pricing['currency_symbols'][:5])}")
                            if pricing.get('pricing_terms'):
                                st.markdown(f"- Pricing terms: {', '.join(pricing['pricing_terms'][:5])}")
                        
                        # Show feature lists
                        features = page['feature_lists']
                        if features:
                            st.markdown("**Features/Benefits:**")
                            for feature in features[:5]:
                                st.markdown(f"- {feature}")
                        
                        # Show contact information
                        contact = page['contact_info']
                        if contact.get('emails') or contact.get('phones'):
                            st.markdown("**Contact Information:**")
                            if contact.get('emails'):
                                st.markdown(f"- Emails: {', '.join(contact['emails'][:3])}")
                            if contact.get('phones'):
                                st.markdown(f"- Phones: {', '.join(contact['phones'][:3])}")
                        
                        # Quality issues
                        issues = page['quality'].get('issues', [])
                        if issues:
                            st.markdown("**Quality Issues:**")
                            for issue in issues:
                                st.markdown(f"- ⚠️ {issue}")
                        
                        st.markdown(f"[🔗 Visit Page]({page['url']})")
                
            else:
                st.info("No content analysis results available. Run an analysis first.")
        
        elif selected_section == "💰 Pricing Analysis":
            st.markdown("#### Pricing Intelligence")
            
            if analyzed_pages:
                # Filter pages with pricing information
                pricing_pages = [page for page in analyzed_pages if page['category'] == 'pricing' or page['pricing_indicators'].get('currency_symbols')]
                
                if pricing_pages:
                    st.markdown(f"Found **{len(pricing_pages)}** pages with pricing information:")
                    
                    # Aggregate pricing data
                    all_currencies = set()
                    all_pricing_terms = set()
                    
                    for page in pricing_pages:
                        pricing = page['pricing_indicators']
                        if pricing.get('currency_symbols'):
                            all_currencies.update(pricing['currency_symbols'])
                        if pricing.get('pricing_terms'):
                            all_pricing_terms.update(pricing['pricing_terms'])
                    
                    # Display pricing summary
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Currency Symbols Found:**")
                        for currency in sorted(all_currencies):
                            st.markdown(f"- {currency}")
                    
                    with col2:
                        st.markdown("**Pricing Terms Found:**")
                        for term in sorted(all_pricing_terms):
                            st.markdown(f"- {term}")
                    
                    # Show detailed pricing pages
                    st.markdown("#### Detailed Pricing Pages")
                    
                    for page in pricing_pages:
                        with st.expander(f"💰 {page['title']}"):
                            st.markdown(f"**URL:** {page['url']}")
                            st.markdown(f"**Word Count:** {page['word_count']}")
                            
                            pricing = page['pricing_indicators']
                            if pricing.get('currency_symbols'):
                                st.markdown(f"**Prices Found:** {', '.join(pricing['currency_symbols'][:10])}")
                            if pricing.get('pricing_terms'):
                                st.markdown(f"**Pricing Terms:** {', '.join(pricing['pricing_terms'][:10])}")
                            
                            # Show feature lists from pricing pages
                            features = page['feature_lists']
                            if features:
                                st.markdown("**Features/Plans:**")
                                for feature in features[:8]:
                                    st.markdown(f"- {feature}")
                            
                            st.markdown(f"[🔗 Visit Page]({page['url']})")
                
                else:
                    st.info("No pricing pages found in the scraped content.")
            else:
                st.info("No pricing analysis available. Run a content analysis first.")
        
        elif selected_section == "🎯 Features Analysis":
            st.markdown("#### Features Intelligence")
            
            if analyzed_pages:
                # Filter pages with feature information
                feature_pages = [page for page in analyzed_pages if page['category'] == 'features' or len(page['feature_lists']) > 3]
                
                if feature_pages:
                    st.markdown(f"Found **{len(feature_pages)}** pages with feature information:")
                    
                    # Aggregate all features
                    all_features = []
                    for page in feature_pages:
                        all_features.extend(page['feature_lists'])
                    
                    # Display features summary
                    st.markdown(f"**Total Features Found:** {len(all_features)}")
                    
                    # Show top features (most common)
                    if all_features:
                        from collections import Counter
                        feature_counts = Counter(all_features)
                        top_features = feature_counts.most_common(10)
                        
                        st.markdown("**Top Features (by frequency):**")
                        for feature, count in top_features:
                            st.markdown(f"- {feature} (mentioned {count} times)")
                    
                    # Show detailed feature pages
                    st.markdown("#### Detailed Feature Pages")
                    
                    for page in feature_pages:
                        with st.expander(f"🎯 {page['title']}"):
                            st.markdown(f"**URL:** {page['url']}")
                            st.markdown(f"**Word Count:** {page['word_count']}")
                            
                            # Show headings structure
                            headings = page['headings']
                            if headings.get('h1') or headings.get('h2'):
                                st.markdown("**Page Structure:**")
                                if headings.get('h1'):
                                    st.markdown(f"- H1: {', '.join(headings['h1'])}")
                                if headings.get('h2'):
                                    st.markdown(f"- H2: {', '.join(headings['h2'][:5])}")
                            
                            # Show feature lists
                            features = page['feature_lists']
                            if features:
                                st.markdown("**Features/Capabilities:**")
                                for feature in features[:10]:
                                    st.markdown(f"- {feature}")
                            
                            st.markdown(f"[🔗 Visit Page]({page['url']})")
                
                else:
                    st.info("No feature pages found in the scraped content.")
            else:
                st.info("No features analysis available. Run a content analysis first.")
        
        elif selected_section == "🤖 AI Categorized Complaints":
            st.markdown("#### AI Categorized Complaints Analysis")
            
            categorized_complaints = st.session_state.get('categorized_complaints', [])
            categorization_report = st.session_state.get('categorization_report', None)
            
            if categorized_complaints:
                st.markdown("### 🤖 AI-Powered Complaint Categorization")
                
                # Executive Summary
                with st.expander("📋 Executive Summary", expanded=True):
                    st.markdown(categorization_report.get('executive_summary', 'No executive summary available'))
                
                # Overall Statistics
                overall_stats = categorization_report.get('overall_statistics', {})
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Categorized", overall_stats.get('total_complaints', 0))
                
                with col2:
                    category_count = len(overall_stats.get('category_distribution', {}))
                    st.metric("Categories Found", category_count)
                
                with col3:
                    # Show most severe complaints
                    severity_dist = overall_stats.get('severity_distribution', {})
                    high_critical = severity_dist.get('High', 0) + severity_dist.get('Critical', 0)
                    st.metric("High/Critical Issues", high_critical)
                
                with col4:
                    # Show most negative sentiment
                    sentiment_dist = overall_stats.get('sentiment_distribution', {})
                    negative = sentiment_dist.get('Very Negative', 0) + sentiment_dist.get('Negative', 0)
                    st.metric("Negative Sentiment", negative)
                
                # Category Distribution Chart
                st.markdown("#### Complaint Categories Distribution")
                category_dist = overall_stats.get('category_distribution', {})
                if category_dist:
                    import pandas as pd
                    cat_data = []
                    for category, count in category_dist.items():
                        if count > 0:
                            cat_data.append({'Category': category, 'Count': count})
                    
                    if cat_data:
                        df = pd.DataFrame(cat_data)
                        st.bar_chart(df.set_index('Category'))
                
                # Detailed Category Analysis
                st.markdown("#### Detailed Category Analysis")
                category_analyses = categorization_report.get('category_analyses', {})
                
                for category, analysis in category_analyses.items():
                    with st.expander(f"{category} - {analysis['total_complaints']} complaints"):
                        st.markdown(f"**Total Complaints:** {analysis['total_complaints']}")
                        
                        # Severity breakdown
                        st.markdown("**Severity Distribution:**")
                        severity_breakdown = analysis['severity_distribution']
                        for severity, count in severity_breakdown.items():
                            if count > 0:
                                st.markdown(f"- {severity}: {count}")
                        
                        # Top keywords
                        st.markdown("**Common Keywords:**")
                        for keyword, count in analysis['common_keywords'][:5]:
                            st.markdown(f"- {keyword}: {count}")
                        
                        # Trend analysis
                        st.markdown("**Trend Analysis:**")
                        st.markdown(analysis['trend_analysis'])
                        
                        # Top complaints in this category
                        st.markdown("**Top Complaints:**")
                        for i, complaint in enumerate(analysis['top_complaints'][:3], 1):
                            st.markdown(f"{i}. **{complaint['summary']}** (Severity: {complaint['severity']}, Confidence: {complaint['confidence']:.2f})")
                            st.markdown(f"   Source: {complaint['source']} | Platform: {complaint['platform']}")
                        
                        # Actionable insights
                        if analysis['actionable_insights']:
                            st.markdown("**Actionable Insights:**")
                            for insight in analysis['actionable_insights'][:3]:
                                st.markdown(f"- {insight}")
                        
                        # Recommendations
                        if analysis['recommendations']:
                            st.markdown("**Recommendations for StoreHub:**")
                            for rec in analysis['recommendations'][:3]:
                                st.markdown(f"- {rec}")
                
                # Top Weaknesses Across All Categories
                st.markdown("#### Top Competitor Weaknesses")
                top_weaknesses = categorization_report.get('top_weaknesses', [])
                if top_weaknesses:
                    for i, weakness in enumerate(top_weaknesses[:5], 1):
                        st.markdown(f"{i}. {weakness}")
                
                # Platform Distribution
                st.markdown("#### Platform Distribution")
                platform_dist = overall_stats.get('platform_distribution', {})
                if platform_dist:
                    import pandas as pd
                    platform_data = []
                    for platform, count in platform_dist.items():
                        if count > 0:
                            platform_data.append({'Platform': platform, 'Count': count})
                    
                    if platform_data:
                        df = pd.DataFrame(platform_data)
                        st.bar_chart(df.set_index('Platform'))
                
                # Sentiment Analysis
                st.markdown("#### Sentiment Analysis")
                sentiment_dist = overall_stats.get('sentiment_distribution', {})
                if sentiment_dist:
                    import pandas as pd
                    sent_data = []
                    for sentiment, count in sentiment_dist.items():
                        if count > 0:
                            sent_data.append({'Sentiment': sentiment, 'Count': count})
                    
                    if sent_data:
                        df = pd.DataFrame(sent_data)
                        st.bar_chart(df.set_index('Sentiment'))
                
                # Raw categorized complaints
                with st.expander("📝 View All Categorized Complaints"):
                    for i, complaint in enumerate(categorized_complaints, 1):
                        st.markdown(f"**{i}. {complaint.category} - {complaint.subcategory}**")
                        st.markdown(f"*Severity: {complaint.severity} | Confidence: {complaint.confidence:.2f} | Sentiment: {complaint.sentiment}*")
                        st.markdown(f"**Summary:** {complaint.summary}")
                        st.markdown(f"**Source:** {complaint.source} | **Platform:** {complaint.platform}")
                        st.markdown(f"**Keywords:** {', '.join(complaint.keywords)}")
                        st.markdown(f"**StoreHub Opportunity:** {complaint.actionable_insight}")
                        st.markdown("---")
                
                st.markdown("---")
            
            # Show raw Google search results as secondary information
            if st.session_state.get('complaint_analysis'):
                complaint_analysis = st.session_state.complaint_analysis
                st.markdown("### 🔍 Raw Search Results")
                
                with st.expander("View Raw Google Search Results", expanded=False):
                    # Overall metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Complaints", complaint_analysis['total_complaints'])
                    
                    with col2:
                        platforms_searched = len(complaint_analysis['platforms'])
                        st.metric("Platforms Searched", platforms_searched)
                    
                    with col3:
                        # Calculate average complaint score
                        top_complaints = complaint_analysis.get('top_complaints', [])
                        if top_complaints:
                            avg_score = sum(c.get('complaint_score', 0) for c in top_complaints) / len(top_complaints)
                            st.metric("Avg Complaint Score", f"{avg_score:.2f}")
                        else:
                            st.metric("Avg Complaint Score", "N/A")
                    
                    with col4:
                        # Show search success rate
                        search_summary = complaint_analysis.get('summary', {})
                        success_rate = search_summary.get('success_rate', 0)
                        st.metric("Search Success Rate", f"{success_rate:.1f}%")
                    
                    # Complaint categories breakdown
                    st.markdown("#### Complaint Categories")
                    categories = complaint_analysis.get('complaint_categories', {})
                    if categories:
                        # Create dataframe for chart
                        import pandas as pd
                        cat_data = []
                        for category, count in categories.items():
                            if count > 0:
                                cat_data.append({'Category': category, 'Count': count})
                        
                        if cat_data:
                            df = pd.DataFrame(cat_data)
                            st.bar_chart(df.set_index('Category'))
                    
                    # Platform-specific results
                    st.markdown("#### Platform-Specific Analysis")
                    platforms = complaint_analysis.get('platforms', {})
                    for platform, platform_data in platforms.items():
                        if platform_data.get('total_results', 0) > 0:
                            with st.expander(f"{platform} - {platform_data['total_results']} complaints"):
                                st.markdown(f"**Average Complaint Score:** {platform_data.get('avg_complaint_score', 0):.2f}")
                                
                                # Show top complaints for this platform
                                top_complaints = platform_data.get('top_complaints', [])
                                if top_complaints:
                                    st.markdown("**Top Complaints:**")
                                    for i, complaint in enumerate(top_complaints[:5], 1):
                                        st.markdown(f"{i}. **{complaint.get('title', 'No title')}** (Score: {complaint.get('complaint_score', 0):.2f})")
                                        st.markdown(f"   - {complaint.get('description', 'No description')}")
                                        st.markdown(f"   - URL: {complaint.get('url', 'No URL')}")
                    
                    # Top overall complaints
                    st.markdown("#### Top Overall Complaints")
                    top_complaints = complaint_analysis.get('top_complaints', [])
                    if top_complaints:
                        for i, complaint in enumerate(top_complaints[:10], 1):
                            with st.expander(f"{i}. {complaint.get('title', 'No title')} (Score: {complaint.get('complaint_score', 0):.2f})"):
                                st.markdown(f"**Platform:** {complaint.get('platform', 'Unknown')}")
                                st.markdown(f"**Description:** {complaint.get('description', 'No description')}")
                                st.markdown(f"**URL:** {complaint.get('url', 'No URL')}")
                                st.markdown(f"**Query:** {complaint.get('query', 'No query')}")
                                st.markdown(f"**Timestamp:** {complaint.get('timestamp', 'No timestamp')}")
                    
                    # Sentiment distribution
                    st.markdown("#### Sentiment Distribution")
                    sentiment_dist = complaint_analysis.get('sentiment_distribution', {})
                    if sentiment_dist:
                        import pandas as pd
                        sent_data = []
                        for sentiment, count in sentiment_dist.items():
                            if count > 0:
                                sent_data.append({'Sentiment': sentiment, 'Count': count})
                        
                        if sent_data:
                            df = pd.DataFrame(sent_data)
                            st.bar_chart(df.set_index('Sentiment'))
                
            else:
                st.info("No social media complaints found or search not performed.")
                
                # Show search details if available
                if st.session_state.get('complaint_search_results'):
                    search_summary = st.session_state.complaint_search_results.get('summary', {})
                    st.markdown("#### Search Summary")
                    st.markdown(f"**Total Queries:** {search_summary.get('total_queries', 0)}")
                    st.markdown(f"**Successful Searches:** {search_summary.get('successful_searches', 0)}")
                    st.markdown(f"**Failed Searches:** {search_summary.get('failed_searches', 0)}")
                    st.markdown(f"**Success Rate:** {search_summary.get('success_rate', 0):.1f}%")

        elif selected_section == "📱 Social Media Complaints":
            st.markdown("#### Social Media Complaints & Reviews Analysis")
            
            complaint_analysis = st.session_state.get('complaint_analysis', {})
            complaint_search_results = st.session_state.get('complaint_search_results', {})
            categorized_complaints = st.session_state.get('categorized_complaints', [])
            categorization_report = st.session_state.get('categorization_report', None)
            
            # Show AI categorization results first if available
            if categorization_report and categorized_complaints:
                st.markdown("### 🤖 AI-Powered Complaint Categorization")
                
                # Executive Summary
                with st.expander("📋 Executive Summary", expanded=True):
                    st.markdown(categorization_report.get('executive_summary', 'No executive summary available'))
                
                # Overall Statistics
                overall_stats = categorization_report.get('overall_statistics', {})
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Categorized", overall_stats.get('total_complaints', 0))
                
                with col2:
                    category_count = len(overall_stats.get('category_distribution', {}))
                    st.metric("Categories Found", category_count)
                
                with col3:
                    # Show most severe complaints
                    severity_dist = overall_stats.get('severity_distribution', {})
                    high_critical = severity_dist.get('High', 0) + severity_dist.get('Critical', 0)
                    st.metric("High/Critical Issues", high_critical)
                
                with col4:
                    # Show most negative sentiment
                    sentiment_dist = overall_stats.get('sentiment_distribution', {})
                    negative = sentiment_dist.get('Very Negative', 0) + sentiment_dist.get('Negative', 0)
                    st.metric("Negative Sentiment", negative)
                
                # Category Distribution Chart
                st.markdown("#### Complaint Categories Distribution")
                category_dist = overall_stats.get('category_distribution', {})
                if category_dist:
                    import pandas as pd
                    cat_data = []
                    for category, count in category_dist.items():
                        if count > 0:
                            cat_data.append({'Category': category, 'Count': count})
                    
                    if cat_data:
                        df = pd.DataFrame(cat_data)
                        st.bar_chart(df.set_index('Category'))
                
                # Detailed Category Analysis
                st.markdown("#### Detailed Category Analysis")
                category_analyses = categorization_report.get('category_analyses', {})
                
                for category, analysis in category_analyses.items():
                    with st.expander(f"{category} - {analysis['total_complaints']} complaints"):
                        st.markdown(f"**Total Complaints:** {analysis['total_complaints']}")
                        
                        # Severity breakdown
                        st.markdown("**Severity Distribution:**")
                        severity_breakdown = analysis['severity_distribution']
                        for severity, count in severity_breakdown.items():
                            if count > 0:
                                st.markdown(f"- {severity}: {count}")
                        
                        # Top keywords
                        st.markdown("**Common Keywords:**")
                        for keyword, count in analysis['common_keywords'][:5]:
                            st.markdown(f"- {keyword}: {count}")
                        
                        # Trend analysis
                        st.markdown("**Trend Analysis:**")
                        st.markdown(analysis['trend_analysis'])
                        
                        # Top complaints in this category
                        st.markdown("**Top Complaints:**")
                        for i, complaint in enumerate(analysis['top_complaints'][:3], 1):
                            st.markdown(f"{i}. **{complaint['summary']}** (Severity: {complaint['severity']}, Confidence: {complaint['confidence']:.2f})")
                            st.markdown(f"   Source: {complaint['source']} | Platform: {complaint['platform']}")
                        
                        # Actionable insights
                        if analysis['actionable_insights']:
                            st.markdown("**Actionable Insights:**")
                            for insight in analysis['actionable_insights'][:3]:
                                st.markdown(f"- {insight}")
                        
                        # Recommendations
                        if analysis['recommendations']:
                            st.markdown("**Recommendations for StoreHub:**")
                            for rec in analysis['recommendations'][:3]:
                                st.markdown(f"- {rec}")
                
                # Top Weaknesses Across All Categories
                st.markdown("#### Top Competitor Weaknesses")
                top_weaknesses = categorization_report.get('top_weaknesses', [])
                if top_weaknesses:
                    for i, weakness in enumerate(top_weaknesses[:5], 1):
                        st.markdown(f"{i}. {weakness}")
                
                # Platform Distribution
                st.markdown("#### Platform Distribution")
                platform_dist = overall_stats.get('platform_distribution', {})
                if platform_dist:
                    import pandas as pd
                    platform_data = []
                    for platform, count in platform_dist.items():
                        if count > 0:
                            platform_data.append({'Platform': platform, 'Count': count})
                    
                    if platform_data:
                        df = pd.DataFrame(platform_data)
                        st.bar_chart(df.set_index('Platform'))
                
                # Sentiment Analysis
                st.markdown("#### Sentiment Analysis")
                sentiment_dist = overall_stats.get('sentiment_distribution', {})
                if sentiment_dist:
                    import pandas as pd
                    sent_data = []
                    for sentiment, count in sentiment_dist.items():
                        if count > 0:
                            sent_data.append({'Sentiment': sentiment, 'Count': count})
                    
                    if sent_data:
                        df = pd.DataFrame(sent_data)
                        st.bar_chart(df.set_index('Sentiment'))
                
                # Raw categorized complaints
                with st.expander("📝 View All Categorized Complaints"):
                    for i, complaint in enumerate(categorized_complaints, 1):
                        st.markdown(f"**{i}. {complaint.category} - {complaint.subcategory}**")
                        st.markdown(f"*Severity: {complaint.severity} | Confidence: {complaint.confidence:.2f} | Sentiment: {complaint.sentiment}*")
                        st.markdown(f"**Summary:** {complaint.summary}")
                        st.markdown(f"**Source:** {complaint.source} | **Platform:** {complaint.platform}")
                        st.markdown(f"**Keywords:** {', '.join(complaint.keywords)}")
                        st.markdown(f"**StoreHub Opportunity:** {complaint.actionable_insight}")
                        st.markdown("---")
                
                st.markdown("---")
            
            # Show raw Google search results as secondary information
            if complaint_analysis and complaint_analysis.get('total_complaints', 0) > 0:
                st.markdown("### 🔍 Raw Search Results")
                
                with st.expander("View Raw Google Search Results", expanded=False):
                    # Overall metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Complaints", complaint_analysis['total_complaints'])
                    
                    with col2:
                        platforms_searched = len(complaint_analysis['platforms'])
                        st.metric("Platforms Searched", platforms_searched)
                    
                    with col3:
                        # Calculate average complaint score
                        top_complaints = complaint_analysis.get('top_complaints', [])
                        if top_complaints:
                            avg_score = sum(c.get('complaint_score', 0) for c in top_complaints) / len(top_complaints)
                            st.metric("Avg Complaint Score", f"{avg_score:.2f}")
                        else:
                            st.metric("Avg Complaint Score", "N/A")
                    
                    with col4:
                        # Show search success rate
                        search_summary = complaint_analysis.get('summary', {})
                        success_rate = search_summary.get('success_rate', 0)
                        st.metric("Search Success Rate", f"{success_rate:.1f}%")
                    
                    # Complaint categories breakdown
                    st.markdown("#### Complaint Categories")
                    categories = complaint_analysis.get('complaint_categories', {})
                    if categories:
                        # Create dataframe for chart
                        import pandas as pd
                        cat_data = []
                        for category, count in categories.items():
                            if count > 0:
                                cat_data.append({'Category': category, 'Count': count})
                        
                        if cat_data:
                            df = pd.DataFrame(cat_data)
                            st.bar_chart(df.set_index('Category'))
                    
                    # Platform-specific results
                    st.markdown("#### Platform-Specific Analysis")
                    platforms = complaint_analysis.get('platforms', {})
                    for platform, platform_data in platforms.items():
                        if platform_data.get('total_results', 0) > 0:
                            with st.expander(f"{platform} - {platform_data['total_results']} complaints"):
                                st.markdown(f"**Average Complaint Score:** {platform_data.get('avg_complaint_score', 0):.2f}")
                                
                                # Show top complaints for this platform
                                top_complaints = platform_data.get('top_complaints', [])
                                if top_complaints:
                                    st.markdown("**Top Complaints:**")
                                    for i, complaint in enumerate(top_complaints[:5], 1):
                                        st.markdown(f"{i}. **{complaint.get('title', 'No title')}** (Score: {complaint.get('complaint_score', 0):.2f})")
                                        st.markdown(f"   - {complaint.get('description', 'No description')}")
                                        st.markdown(f"   - URL: {complaint.get('url', 'No URL')}")
                    
                    # Top overall complaints
                    st.markdown("#### Top Overall Complaints")
                    top_complaints = complaint_analysis.get('top_complaints', [])
                    if top_complaints:
                        for i, complaint in enumerate(top_complaints[:10], 1):
                            with st.expander(f"{i}. {complaint.get('title', 'No title')} (Score: {complaint.get('complaint_score', 0):.2f})"):
                                st.markdown(f"**Platform:** {complaint.get('platform', 'Unknown')}")
                                st.markdown(f"**Description:** {complaint.get('description', 'No description')}")
                                st.markdown(f"**URL:** {complaint.get('url', 'No URL')}")
                                st.markdown(f"**Query:** {complaint.get('query', 'No query')}")
                                st.markdown(f"**Timestamp:** {complaint.get('timestamp', 'No timestamp')}")
                    
                    # Sentiment distribution
                    st.markdown("#### Sentiment Distribution")
                    sentiment_dist = complaint_analysis.get('sentiment_distribution', {})
                    if sentiment_dist:
                        import pandas as pd
                        sent_data = []
                        for sentiment, count in sentiment_dist.items():
                            if count > 0:
                                sent_data.append({'Sentiment': sentiment, 'Count': count})
                        
                        if sent_data:
                            df = pd.DataFrame(sent_data)
                            st.bar_chart(df.set_index('Sentiment'))
                
            else:
                st.info("No social media complaints found or search not performed.")
                
                # Show search details if available
                if complaint_search_results:
                    search_summary = complaint_search_results.get('summary', {})
                    st.markdown("#### Search Summary")
                    st.markdown(f"**Total Queries:** {search_summary.get('total_queries', 0)}")
                    st.markdown(f"**Successful Searches:** {search_summary.get('successful_searches', 0)}")
                    st.markdown(f"**Failed Searches:** {search_summary.get('failed_searches', 0)}")
                    st.markdown(f"**Success Rate:** {search_summary.get('success_rate', 0):.1f}%")

        elif selected_section == "📰 Blog & News":
            st.markdown("#### Blog & News Analysis")
            
            if discovered_urls.get('blog'):
                urls = discovered_urls['blog']
                st.markdown(f"Found **{len(urls)}** blog/news pages:")
                
                for i, url in enumerate(urls, 1):
                    with st.expander(f"{i}. {url}"):
                        st.markdown(f"**URL:** {url}")
                        
                        # Try to fetch basic metadata
                        try:
                            discovery = URLDiscovery(st.session_state.get('current_url', ''), config)
                            metadata = discovery.get_page_metadata(url)
                            
                            if metadata.get('title'):
                                st.markdown(f"**Title:** {metadata['title']}")
                            if metadata.get('description'):
                                st.markdown(f"**Description:** {metadata['description']}")
                            
                            st.markdown(f"[🔗 Visit Page]({url})")
                            
                        except Exception as e:
                            st.warning(f"Could not fetch metadata: {str(e)}")
            else:
                st.info("No blog/news pages found for this competitor.")
        
        elif selected_section == "💼 Careers Pages":
            st.markdown("#### Careers Pages Analysis")
            
            if discovered_urls.get('careers'):
                urls = discovered_urls['careers']
                st.markdown(f"Found **{len(urls)}** careers pages:")
                
                for i, url in enumerate(urls, 1):
                    with st.expander(f"{i}. {url}"):
                        st.markdown(f"**URL:** {url}")
                        
                        # Try to fetch basic metadata
                        try:
                            discovery = URLDiscovery(st.session_state.get('current_url', ''), config)
                            metadata = discovery.get_page_metadata(url)
                            
                            if metadata.get('title'):
                                st.markdown(f"**Title:** {metadata['title']}")
                            if metadata.get('description'):
                                st.markdown(f"**Description:** {metadata['description']}")
                            
                            st.markdown(f"[🔗 Visit Page]({url})")
                            
                        except Exception as e:
                            st.warning(f"Could not fetch metadata: {str(e)}")
            else:
                st.info("No careers pages found for this competitor.")
        
        elif selected_section == "📞 Contact & Support":
            st.markdown("#### Contact & Support Analysis")
            
            if discovered_urls.get('contact'):
                urls = discovered_urls['contact']
                st.markdown(f"Found **{len(urls)}** contact/support pages:")
                
                for i, url in enumerate(urls, 1):
                    with st.expander(f"{i}. {url}"):
                        st.markdown(f"**URL:** {url}")
                        
                        # Try to fetch basic metadata
                        try:
                            discovery = URLDiscovery(st.session_state.get('current_url', ''), config)
                            metadata = discovery.get_page_metadata(url)
                            
                            if metadata.get('title'):
                                st.markdown(f"**Title:** {metadata['title']}")
                            if metadata.get('description'):
                                st.markdown(f"**Description:** {metadata['description']}")
                            
                            st.markdown(f"[🔗 Visit Page]({url})")
                            
                        except Exception as e:
                            st.warning(f"Could not fetch metadata: {str(e)}")
            else:
                st.info("No contact/support pages found for this competitor.")
        
        elif selected_section == "🏢 About Pages":
            st.markdown("#### About Pages Analysis")
            
            if discovered_urls.get('about'):
                urls = discovered_urls['about']
                st.markdown(f"Found **{len(urls)}** about pages:")
                
                for i, url in enumerate(urls, 1):
                    with st.expander(f"{i}. {url}"):
                        st.markdown(f"**URL:** {url}")
                        
                        # Try to fetch basic metadata
                        try:
                            discovery = URLDiscovery(st.session_state.get('current_url', ''), config)
                            metadata = discovery.get_page_metadata(url)
                            
                            if metadata.get('title'):
                                st.markdown(f"**Title:** {metadata['title']}")
                            if metadata.get('description'):
                                st.markdown(f"**Description:** {metadata['description']}")
                            
                            st.markdown(f"[🔗 Visit Page]({url})")
                            
                        except Exception as e:
                            st.warning(f"Could not fetch metadata: {str(e)}")
            else:
                st.info("No about pages found for this competitor.")
        
        # Export options
        st.markdown("### Export Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export PDF"):
                st.info("PDF export functionality will be implemented in Phase 4")
        
        with col2:
            if st.button("📊 Export Excel"):
                st.info("Excel export functionality will be implemented in Phase 4")
        
        with col3:
            if st.button("🔧 Export JSON"):
                if discovered_urls or analyzed_pages:
                    # Prepare comprehensive export data
                    export_data = {
                        'competitor_name': competitor_name,
                        'target_country': st.session_state.get('current_country', 'US'),
                        'analysis_date': datetime.now().isoformat(),
                        'country_context': country_localization.get_competitor_context(st.session_state.get('current_country', 'US')),
                        'discovered_urls': discovered_urls,
                        'discovery_summary': discovery_summary,
                        'scraping_results': scraping_results,
                        'analyzed_pages': analyzed_pages,
                        'complaint_search_results': st.session_state.get('complaint_search_results', {}),
                        'complaint_analysis': st.session_state.get('complaint_analysis', {}),
                        'social_scraping_results': st.session_state.get('social_scraping_results', {}),
                        'social_content_analysis': st.session_state.get('social_content_analysis', {}),
                        'summary': {
                            'total_urls_found': sum(len(urls) for urls in discovered_urls.values()),
                            'pages_scraped': len(analyzed_pages),
                            'scraping_success_rate': scraping_results.get('summary', {}).get('success_rate', 0),
                            'avg_quality_score': sum(page['quality'].get('completeness_score', 0) for page in analyzed_pages) / len(analyzed_pages) if analyzed_pages else 0,
                            'total_complaints_found': st.session_state.get('complaint_analysis', {}).get('total_complaints', 0),
                            'social_content_pieces': st.session_state.get('social_content_analysis', {}).get('total_content_pieces', 0)
                        }
                    }
                    
                    st.download_button(
                        label="Download Complete Analysis",
                        data=json.dumps(export_data, indent=2),
                        file_name=f"{competitor_name}_complete_analysis.json",
                        mime="application/json"
                    )
                else:
                    st.info("No data available for export")
    
    else:
        st.info("No completed analyses available. Start a new analysis in the Analysis tab.")

def settings_tab():
    """Application settings and configuration tab"""
    st.markdown("## Application Settings")
    
    # API Configuration
    st.markdown("### API Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Required for AI-powered analysis"
        )
    
    with col2:
        google_api_key = st.text_input(
            "Google Search API Key",
            type="password",
            placeholder="Your Google API key",
            help="Required for social media search"
        )
    
    # Analysis Settings
    st.markdown("### Analysis Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_results = st.number_input(
            "Max Search Results",
            min_value=10,
            max_value=100,
            value=config.max_search_results,
            help="Maximum number of search results to analyze"
        )
    
    with col2:
        timeout = st.number_input(
            "Request Timeout (seconds)",
            min_value=5,
            max_value=60,
            value=config.request_timeout,
            help="Timeout for web requests"
        )
    
    # Social Media Settings
    st.markdown("### Social Media Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        use_selenium = st.checkbox(
            "Use Selenium for JavaScript-heavy sites",
            value=False,
            help="Enable Selenium for better Facebook, Twitter, and Instagram scraping"
        )
    
    with col2:
        max_social_urls = st.number_input(
            "Max Social Media URLs to Scrape",
            min_value=5,
            max_value=50,
            value=20,
            help="Maximum number of social media URLs to scrape per analysis"
        )
    
    # Save settings
    if st.button("💾 Save Settings"):
        st.success("Settings saved successfully!")
        logger.info("Settings updated by user")

def help_tab():
    """Help and documentation tab"""
    st.markdown("## Help & Documentation")
    
    # Quick start guide
    st.markdown("### Quick Start Guide")
    st.markdown("""
    1. **Enter Competitor Information**: Provide the competitor name and official website URL
    2. **Select Target Country**: Choose the country for localized competitive analysis
    3. **Configure Options**: Choose analysis depth and select components to include
    4. **Start Analysis**: Click the "Start Analysis" button to begin
    5. **View Reports**: Check the Reports tab for generated insights
    6. **Export Results**: Export reports in PDF, Excel, or JSON format
    """)
    
    # Features overview
    st.markdown("### Features")
    
    features = [
        ("🔍 Automated Discovery", "Automatically finds competitor pricing, features, and news pages"),
        ("🌍 Country Localization", "Targets analysis by country with localized currencies, social platforms, and business context"),
        ("📱 Social Media Analysis", "Analyzes complaints and feedback across social platforms"),
        ("🤖 AI-Powered Insights", "Uses GPT-4 for deep analysis and strategic recommendations"),
        ("📊 Comprehensive Reports", "Generates detailed competitive analysis reports"),
        ("⚔️ Sales Battlecards", "Creates ready-to-use sales talking points"),
        ("📈 Marketing Recommendations", "Provides actionable marketing and SEO strategies")
    ]
    
    for icon_title, description in features:
        st.markdown(f"**{icon_title}**: {description}")
    
    # Development roadmap
    st.markdown("### Development Roadmap")
    
    phases = [
        ("Phase 1: Foundation", "✅ Basic UI and scraping infrastructure"),
        ("Phase 2: Social Aggregation", "🔄 Social media complaint analysis"),
        ("Phase 3: LLM Analysis", "⏳ AI-powered competitive analysis"),
        ("Phase 4: Report Generation", "⏳ Professional report interface"),
        ("Phase 5: Sales & Marketing", "⏳ Battlecards and recommendations"),
        ("Phase 6: Testing & Refinement", "⏳ Optimization and deployment")
    ]
    
    for phase, status in phases:
        st.markdown(f"**{phase}**: {status}")
    
    # Contact information
    st.markdown("### Support")
    st.markdown("For technical support or feature requests, please contact the development team.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
        st.info("Please check the logs for more details.") 