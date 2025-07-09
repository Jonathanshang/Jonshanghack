import streamlit as st
import pandas as pd
from datetime import datetime
import time
import sys
import os
from typing import Dict, List, Any, Optional

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import utilities
from config import Config
from utils.url_discovery import URLDiscovery
from utils.scraper import WebScraper, extract_page_category, analyze_content_quality
from utils.google_search import GoogleSearchScraper, analyze_complaint_patterns
from utils.social_media_scraper import SocialMediaScraper
from utils.complaint_categorization import ComplaintCategorizer
from utils.pricing_analysis import PricingAnalyzer
from utils.monetization_analysis import MonetizationAnalyzer
from utils.vision_analysis import VisionAnalyzer
from utils import country_localization
from utils.logger import setup_logger
from utils.country_localization import country_localization
from utils.google_search import GoogleSearchScraper, analyze_complaint_patterns
from utils.social_media_scraper import SocialMediaScraper, create_social_media_urls_from_search_results, analyze_social_media_content
from utils.master_prompt_designer import MasterPromptDesigner
from utils.export_manager import ExportManager
from utils.battlecard_generator import BattlecardGenerator
import utils.country_localization as country_localization
import requests
import json
from utils.battlecard_generator import BattlecardGenerator

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
                "Official Website URL (Optional)",
                placeholder="https://www.competitor.com (leave empty for auto-discovery)",
                help="Enter the main website URL of the competitor, or leave empty to automatically find it"
            )
            
            # Show auto-discovery status
            if competitor_name and not competitor_url:
                st.info("💡 URL will be automatically discovered via Google search")
            elif competitor_url:
                st.success("✅ Using provided URL")
        
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
    
    # Analysis Objective Selection
    with st.expander("🎯 Select Analysis Objective", expanded=True):
        st.markdown("**Choose your analysis objective:**")
        
        analysis_objectives = [
            "💰 Hardware & Software Pricing Analysis",
            "🎯 Existing Feature Analysis", 
            "🔮 Vision & Upcoming Features",
            "📱 Socially-Sourced Weaknesses"
        ]
        
        selected_objective = st.selectbox(
            "Analysis Objective",
            options=analysis_objectives,
            help="Select the type of analysis you want to perform"
        )
        
        # Map objectives to phases
        phase_mapping = {
            "💰 Hardware & Software Pricing Analysis": {
                'phase1_enabled': True,   # URL Discovery (to find pricing pages)
                'phase2_enabled': True,   # Content Scraping (to scrape pricing content)
                'phase3_enabled': True,   # Content Analysis (to analyze pricing content)
                'phase4_enabled': False,  # Not needed for pricing
                'phase5_enabled': False,  # Not needed for pricing
                'phase6_enabled': False   # Not needed for pricing
            },
            "🎯 Existing Feature Analysis": {
                'phase1_enabled': True,   # URL Discovery (to find feature pages)
                'phase2_enabled': True,   # Content Scraping (to scrape feature content)
                'phase3_enabled': True,   # Content Analysis (to analyze feature content)
                'phase4_enabled': False,  # Not needed for features
                'phase5_enabled': False,  # Not needed for features
                'phase6_enabled': False   # Not needed for features
            },
            "🔮 Vision & Upcoming Features": {
                'phase1_enabled': True,   # URL Discovery (to find blog, careers, news pages)
                'phase2_enabled': True,   # Content Scraping (to scrape blog/news content)
                'phase3_enabled': True,   # Content Analysis (to analyze content)
                'phase4_enabled': False,  # Not needed for vision
                'phase5_enabled': False,  # Not needed for vision
                'phase6_enabled': False   # Not needed for vision
            },
            "📱 Socially-Sourced Weaknesses": {
                'phase1_enabled': False,  # Not needed for social analysis
                'phase2_enabled': False,  # Not needed for social analysis
                'phase3_enabled': False,  # Not needed for social analysis
                'phase4_enabled': True,   # Google Search for Complaints
                'phase5_enabled': True,   # Social Media Scraping
                'phase6_enabled': True    # AI Complaint Categorization
            }
        }
        
        # Get phases for selected objective
        phase_config = phase_mapping[selected_objective]
        
        # Extract phase variables
        phase1_enabled = phase_config['phase1_enabled']
        phase2_enabled = phase_config['phase2_enabled']
        phase3_enabled = phase_config['phase3_enabled']
        phase4_enabled = phase_config['phase4_enabled']
        phase5_enabled = phase_config['phase5_enabled']
        phase6_enabled = phase_config['phase6_enabled']
        
        # Show what phases will be executed
        st.markdown("**Analysis phases that will be executed:**")
        phase_descriptions = {
            'phase1': "🔍 Phase 1: URL Discovery - Discover competitor pages",
            'phase2': "📄 Phase 2: Content Scraping - Scrape discovered pages",
            'phase3': "🧠 Phase 3: Content Analysis - Analyze scraped content",
            'phase4': "🔎 Phase 4: Google Search - Search for complaints",
            'phase5': "📱 Phase 5: Social Media Scraping - Scrape social content",
            'phase6': "🤖 Phase 6: AI Categorization - Categorize complaints"
        }
        
        for phase_key, enabled in phase_config.items():
            phase_num = phase_key.replace('_enabled', '')
            if enabled:
                st.markdown(f"✅ {phase_descriptions[phase_num]}")
            else:
                st.markdown(f"⏭️ {phase_descriptions[phase_num]} - *Skipped*")
    
    # Auto-trigger analysis if competitor name is provided
    if competitor_name:
        # Store phase selection in session state
        st.session_state.phase_config = phase_config
        st.session_state.selected_objective = selected_objective
        
        # Calculate total phases to run for progress tracking
        total_phases = sum([phase1_enabled, phase2_enabled, phase3_enabled, phase4_enabled, phase5_enabled, phase6_enabled])
        
        # Add website discovery phase if URL is not provided
        if not competitor_url:
            total_phases += 1
        
        current_phase = 0
        
        logger.info(f"Starting analysis for {competitor_name} for country {country_code}")
        logger.info(f"Selected objective: {selected_objective}")
        logger.info(f"Selected phases: {[f'Phase {i+1}' for i, enabled in enumerate([phase1_enabled, phase2_enabled, phase3_enabled, phase4_enabled, phase5_enabled, phase6_enabled]) if enabled]}")
        
        # Update session state
        st.session_state.analysis_status = "Running"
        st.session_state.current_competitor = competitor_name
        st.session_state.current_country = country_code
        
        # Real URL discovery process
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Phase 0: Website Discovery (if URL not provided)
        if not competitor_url:
            current_phase += 1
            progress_percent = int((current_phase / total_phases) * 100)
            status_text.text(f'🔍 Phase 0: Auto-discovering competitor website... ({current_phase}/{total_phases})')
            progress_bar.progress(progress_percent)
            
            try:
                # Initialize Google search scraper
                google_scraper = GoogleSearchScraper(config)
                
                # Search for competitor's official website
                website_search_results = google_scraper.search_competitor_website(competitor_name, country_code)
                
                # Get discovered URL
                discovered_url = website_search_results.get('official_website')
                
                if discovered_url:
                    competitor_url = discovered_url
                    st.session_state.current_url = competitor_url
                    st.session_state.website_discovery_results = website_search_results
                    
                    st.success(f"✅ Auto-discovered website: {competitor_url}")
                    logger.info(f"Auto-discovered website for {competitor_name}: {competitor_url}")
                else:
                    st.error("❌ Could not auto-discover competitor website. Please provide the URL manually.")
                    logger.error(f"Failed to auto-discover website for {competitor_name}")
                    st.session_state.analysis_status = "Error"
                    return
                    
            except Exception as e:
                st.error(f"❌ Error during website discovery: {str(e)}")
                logger.error(f"Error during website discovery for {competitor_name}: {str(e)}")
                st.session_state.analysis_status = "Error"
                return
        else:
            st.session_state.current_url = competitor_url
            st.session_state.website_discovery_results = None
        
        # Add to recent analyses
        if 'recent_analyses' not in st.session_state:
            st.session_state.recent_analyses = []
        
        st.session_state.recent_analyses.append({
            'competitor': competitor_name,
            'url': competitor_url,
            'country': country_code,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'objective': selected_objective
        })
        
        st.success(f"Analysis started for {competitor_name} in {country_code}")
        st.info(f"🎯 Objective: {selected_objective}")
        st.info(f"🌐 Target URL: {competitor_url}")
        
        try:
            # Phase 1: URL Discovery
            if phase1_enabled:
                current_phase += 1
                progress_percent = int((current_phase / total_phases) * 100)
                status_text.text(f'🔍 Phase 1: Discovering competitor pages... ({current_phase}/{total_phases})')
                progress_bar.progress(progress_percent)
                
                discovery = URLDiscovery(competitor_url, config)
                discovered_urls = discovery.discover_all_pages()
                
                # Store discovered URLs in session state
                st.session_state.discovered_urls = discovered_urls
                st.session_state.discovery_summary = discovery.get_discovery_summary()
            else:
                # Set empty results if Phase 1 is skipped
                st.session_state.discovered_urls = {}
                st.session_state.discovery_summary = {}
                logger.info("Phase 1 (URL Discovery) skipped")
            
            # Phase 2: Content Scraping
            if phase2_enabled:
                status_text.text('📄 Phase 2: Scraping competitor pages...')
                
                # Select pages to scrape (limit to prevent timeout)
                pages_to_scrape = []
                for page_type in ['pricing', 'features', 'about', 'contact']:
                    if page_type in discovered_urls:
                        pages_to_scrape.extend(discovered_urls[page_type][:3])  # Max 3 per type
                
                # Limit total pages to prevent timeout
                pages_to_scrape = pages_to_scrape[:12]  # Max 12 pages total
                
                # Scrape pages
                scraper = WebScraper(config)
                scraping_results = scraper.scrape_pages(pages_to_scrape)
                
                # Store scraping results in session state
                st.session_state.scraping_results = scraping_results
                st.session_state.scraping_summary = scraper.get_scraping_summary()
            else:
                # Set empty results if Phase 2 is skipped
                st.session_state.scraping_results = {}
                st.session_state.scraping_summary = {}
                logger.info("Phase 2 (Content Scraping) skipped")
            
            # Phase 3: Content Analysis
            if phase3_enabled:
                status_text.text('🧠 Phase 3: Analyzing scraped content...')
                
                # Analyze scraped content
                analyzed_pages = []
                for scraped_page in scraping_results.get('scraped_pages', []):
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
            else:
                # Set empty results if Phase 3 is skipped
                st.session_state.analyzed_pages = []
                logger.info("Phase 3 (Content Analysis) skipped")
            
            # Pricing Analysis (specialized analysis using scraped content)
            if phase2_enabled or phase3_enabled:  # Only run if we have scraped content
                status_text.text(f'💰 Specialized Analysis: Analyzing pricing strategy...')
                
                try:
                    # Initialize pricing analyzer
                    pricing_analyzer = PricingAnalyzer(
                        api_key=config.openai_api_key,
                        model_name=config.model_name,
                        logger=logger
                    )
                    
                    # Get scraped content for pricing analysis
                    scraping_results = st.session_state.get('scraping_results', {})
                    scraped_pages = scraping_results.get('scraped_pages', [])
                    
                    if scraped_pages:
                        # Get country context for pricing analysis
                        country_context = country_localization.get_competitor_context(country_code)
                        
                        # Perform pricing analysis
                        pricing_analysis = pricing_analyzer.analyze_competitor_pricing(
                            competitor_name=competitor_name,
                            scraped_content=scraped_pages,
                            country_context=country_context
                        )
                        
                        # Store results in session state
                        st.session_state.pricing_analysis = pricing_analysis
                        
                        # Log pricing analysis summary
                        logger.info(f"Pricing analysis completed for {competitor_name}")
                        logger.info(f"Currency detected: {pricing_analysis.get('currency_detected', 'Unknown')}")
                        logger.info(f"Hardware model: {pricing_analysis.get('hardware_pricing', {}).get('model_type', 'Unknown')}")
                        logger.info(f"Software model: {pricing_analysis.get('software_pricing', {}).get('pricing_model', 'Unknown')}")
                        logger.info(f"Hidden fees risk: {pricing_analysis.get('hidden_fees', {}).get('risk_level', 'Unknown')}")
                        
                    else:
                        logger.info("No scraped content available for pricing analysis")
                        st.session_state.pricing_analysis = None
                        
                except Exception as e:
                    logger.error(f"Error during pricing analysis: {str(e)}")
                    st.warning(f"Pricing analysis failed: {str(e)} - continuing with available analysis")
                    st.session_state.pricing_analysis = None
            else:
                # Set empty results if prerequisite phases are skipped
                st.session_state.pricing_analysis = None
                logger.info("Pricing analysis skipped - no scraped content available")
            
            # Monetization Analysis (specialized analysis using scraped content and pricing data)
            if phase2_enabled or phase3_enabled:  # Only run if we have scraped content
                status_text.text(f'💰 Specialized Analysis: Analyzing monetization strategy...')
                
                try:
                    # Initialize monetization analyzer
                    monetization_analyzer = MonetizationAnalyzer(
                        api_key=config.openai_api_key,
                        model_name=config.model_name,
                        logger=logger
                    )
                    
                    # Get scraped content and pricing analysis for monetization analysis
                    scraping_results = st.session_state.get('scraping_results', {})
                    scraped_pages = scraping_results.get('scraped_pages', [])
                    pricing_analysis = st.session_state.get('pricing_analysis', None)
                    
                    if scraped_pages:
                        # Get country context for monetization analysis
                        country_context = country_localization.get_competitor_context(country_code)
                        
                        # Perform monetization analysis
                        monetization_analysis = monetization_analyzer.analyze_competitor_monetization(
                            competitor_name=competitor_name,
                            scraped_content=scraped_pages,
                            pricing_analysis=pricing_analysis,
                            country_context=country_context
                        )
                        
                        # Store results in session state
                        st.session_state.monetization_analysis = monetization_analysis
                        
                        # Log monetization analysis summary
                        logger.info(f"Monetization analysis completed for {competitor_name}")
                        logger.info(f"Revenue model: {monetization_analysis.get('revenue_streams', {}).get('revenue_model_type', 'Unknown')}")
                        logger.info(f"Lock-in strength: {monetization_analysis.get('lock_in_strategies', {}).get('lock_in_strength', 'Unknown')}")
                        logger.info(f"Expansion potential: {monetization_analysis.get('expansion_revenue', {}).get('expansion_potential', 'Unknown')}")
                        logger.info(f"Primary streams: {len(monetization_analysis.get('revenue_streams', {}).get('primary_streams', []))}")
                        
                    else:
                        logger.info("No scraped content available for monetization analysis")
                        st.session_state.monetization_analysis = None
                        
                except Exception as e:
                    logger.error(f"Error during monetization analysis: {str(e)}")
                    st.warning(f"Monetization analysis failed: {str(e)} - continuing with available analysis")
                    st.session_state.monetization_analysis = None
            else:
                # Set empty results if prerequisite phases are skipped
                st.session_state.monetization_analysis = None
                logger.info("Monetization analysis skipped - no scraped content available")
            
            # Vision Analysis (specialized analysis using scraped content for strategic direction)
            if phase2_enabled or phase3_enabled:  # Only run if we have scraped content
                status_text.text(f'🔮 Specialized Analysis: Analyzing competitor vision & roadmap...')
                
                try:
                    # Initialize vision analyzer
                    vision_analyzer = VisionAnalyzer(
                        api_key=config.openai_api_key,
                        model_name=config.model_name,
                        logger=logger
                    )
                    
                    # Get scraped content for vision analysis
                    scraping_results = st.session_state.get('scraping_results', {})
                    scraped_pages = scraping_results.get('scraped_pages', [])
                    
                    if scraped_pages:
                        # Get country context for vision analysis
                        country_context = country_localization.get_competitor_context(country_code)
                        
                        # Perform vision analysis
                        vision_analysis = vision_analyzer.analyze_competitor_vision(
                            competitor_name=competitor_name,
                            scraped_content=scraped_pages,
                            country_context=country_context
                        )
                        
                        # Store results in session state
                        st.session_state.vision_analysis = vision_analysis
                        
                        # Log vision analysis summary
                        logger.info(f"Vision analysis completed for {competitor_name}")
                        logger.info(f"Product roadmap signals: {len(vision_analysis.get('product_roadmap', {}).get('upcoming_features', []))}")
                        logger.info(f"Technology investment areas: {len(vision_analysis.get('technology_investments', {}).get('investment_areas', []))}")
                        logger.info(f"Market expansion signals: {len(vision_analysis.get('market_expansion', {}).get('geographic_targets', []))}")
                        logger.info(f"Strategic partnerships: {len(vision_analysis.get('strategic_partnerships', {}).get('partnership_opportunities', []))}")
                        logger.info(f"Hiring growth areas: {len(vision_analysis.get('hiring_patterns', {}).get('growth_areas', []))}")
                        
                    else:
                        logger.info("No scraped content available for vision analysis")
                        st.session_state.vision_analysis = None
                        
                except Exception as e:
                    logger.error(f"Error during vision analysis: {str(e)}")
                    st.warning(f"Vision analysis failed: {str(e)} - continuing with available analysis")
                    st.session_state.vision_analysis = None
            else:
                # Set empty results if prerequisite phases are skipped
                st.session_state.vision_analysis = None
                logger.info("Vision analysis skipped - no scraped content available")
            
            # Phase 4: Google Search for Social Media Complaints
            if phase4_enabled:
                current_phase += 1
                progress_percent = int((current_phase / total_phases) * 100)
                status_text.text(f'🔍 Phase 4: Searching for social media complaints... ({current_phase}/{total_phases})')
                progress_bar.progress(progress_percent)
                
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
                    
                    # Log complaint search summary
                    logger.info(f"Google search completed for {competitor_name}")
                    logger.info(f"Total complaints found: {complaint_analysis.get('total_complaints', 0)}")
                    logger.info(f"Platforms searched: {list(complaint_search_results.get('platforms', {}).keys())}")
                    
                except Exception as e:
                    logger.error(f"Error during Google search: {str(e)}")
                    st.warning(f"Google search failed: {str(e)} - continuing with available analysis")
                    st.session_state.complaint_search_results = {}
                    st.session_state.complaint_analysis = {}
            else:
                # Set empty results if Phase 4 is skipped
                st.session_state.complaint_search_results = {}
                st.session_state.complaint_analysis = {}
                logger.info("Phase 4 (Google Search) skipped")
            
            # Phase 5: Social Media Scraping
            if phase5_enabled:
                current_phase += 1
                progress_percent = int((current_phase / total_phases) * 100)
                status_text.text(f'📱 Phase 5: Scraping social media content... ({current_phase}/{total_phases})')
                progress_bar.progress(progress_percent)
                
                try:
                    # Initialize social media scraper
                    social_scraper = SocialMediaScraper(config)
                    
                    # Get complaint search results
                    complaint_search_results = st.session_state.get('complaint_search_results', {})
                    
                    # Create social media URLs from search results
                    social_media_urls = create_social_media_urls_from_search_results(
                        complaint_search_results, 
                        competitor_name, 
                        country_code
                    )
                    
                    # Scrape social media content
                    social_media_results = social_scraper.scrape_social_media_content(
                        social_media_urls
                    )
                    
                    # Analyze social media content
                    social_media_analysis = analyze_social_media_content(
                        social_media_results, 
                        competitor_name
                    )
                    
                    # Store results in session state
                    st.session_state.social_media_results = social_media_results
                    st.session_state.social_media_analysis = social_media_analysis
                    
                    # Log social media scraping summary
                    logger.info(f"Social media scraping completed for {competitor_name}")
                    logger.info(f"Social media pages scraped: {len(social_media_results.get('scraped_pages', []))}")
                    logger.info(f"Social media posts analyzed: {len(social_media_analysis.get('analyzed_posts', []))}")
                    
                except Exception as e:
                    logger.error(f"Error during social media scraping: {str(e)}")
                    st.warning(f"Social media scraping failed: {str(e)} - continuing with available analysis")
                    st.session_state.social_media_results = {}
                    st.session_state.social_media_analysis = {}
            else:
                # Set empty results if Phase 5 is skipped
                st.session_state.social_media_results = {}
                st.session_state.social_media_analysis = {}
                logger.info("Phase 5 (Social Media Scraping) skipped")
            
            # Phase 6: AI Complaint Categorization
            if phase6_enabled:
                current_phase += 1
                progress_percent = int((current_phase / total_phases) * 100)
                status_text.text(f'🤖 Phase 6: AI categorization of complaints... ({current_phase}/{total_phases})')
                progress_bar.progress(progress_percent)
                
                try:
                    # Initialize complaint categorizer
                    categorizer = ComplaintCategorizer(
                        api_key=config.openai_api_key,
                        model_name=config.model_name,
                        logger=logger
                    )
                    
                    # Get complaint data from previous phases
                    complaint_search_results = st.session_state.get('complaint_search_results', {})
                    social_media_results = st.session_state.get('social_media_results', {})
                    
                    # Categorize complaints
                    categorization_report = categorizer.categorize_complaints(
                        complaint_search_results,
                        social_media_results,
                        competitor_name,
                        country_code
                    )
                    
                    # Store results in session state
                    st.session_state.categorization_report = categorization_report
                    
                    # Log categorization summary
                    logger.info(f"AI categorization completed for {competitor_name}")
                    logger.info(f"Total complaints categorized: {len(categorization_report.get('categorized_complaints', []))}")
                    logger.info(f"Categories found: {list(categorization_report.get('category_analysis', {}).keys())}")
                    
                except Exception as e:
                    logger.error(f"Error during AI categorization: {str(e)}")
                    st.warning(f"AI categorization failed: {str(e)} - continuing with available analysis")
                    st.session_state.categorization_report = {}
            else:
                # Set empty results if Phase 6 is skipped
                st.session_state.categorization_report = {}
                logger.info("Phase 6 (AI Categorization) skipped")
            
            # Analysis complete
            progress_bar.progress(100)
            status_text.text(f'✅ Analysis complete! View results in the Reports tab.')
            
            # Update session state
            st.session_state.analysis_status = "Completed"
            
            # Show completion message
            st.success("🎉 Analysis completed successfully!")
            st.info("📊 Switch to the **Reports** tab to view detailed results.")
            
            # Log completion
            logger.info(f"Analysis completed for {competitor_name}")
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            st.error(f"An error occurred during analysis: {str(e)}")
            st.session_state.analysis_status = "Error"
    
    elif competitor_name:
        st.info("💡 Enter the competitor name to start analysis. URL will be discovered automatically if not provided.")
    else:
        st.info("💡 Enter the competitor name to start analysis.")

def reports_tab():
    """Reports viewing and export tab"""
    st.markdown("## Analysis Reports")
    
    if st.session_state.get('analysis_status') == "Completed":
        st.success("Report ready for viewing")
        
        # Get data from session state
        phase_config = st.session_state.get('phase_config', {})
        discovered_urls = st.session_state.get('discovered_urls', {})
        discovery_summary = st.session_state.get('discovery_summary', {})
        scraping_results = st.session_state.get('scraping_results', {})
        analyzed_pages = st.session_state.get('analyzed_pages', [])
        competitor_name = st.session_state.get('current_competitor', 'Unknown')
        
        # Export functionality
        st.markdown("### 📤 Export Reports")
        
        # Initialize export manager
        export_manager = ExportManager()
        available_formats = export_manager.get_available_formats()
        
        if available_formats:
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                selected_format = st.selectbox(
                    "Export Format",
                    available_formats,
                    help="Select the format to export your analysis report"
                )
            
            with col2:
                if st.button("📥 Export Report", type="primary"):
                    try:
                        # Prepare export data
                        export_data = {
                            'competitor_name': competitor_name,
                            'competitor_url': st.session_state.get('current_url', 'Unknown'),
                            'country': st.session_state.get('current_country', 'US'),
                            'selected_objective': st.session_state.get('selected_objective', 'General Analysis'),
                            'phase_config': phase_config,
                            'discovered_urls': discovered_urls,
                            'discovery_summary': discovery_summary,
                            'scraping_results': scraping_results,
                            'analyzed_pages': analyzed_pages,
                            'pricing_analysis': st.session_state.get('pricing_analysis'),
                            'monetization_analysis': st.session_state.get('monetization_analysis'),
                            'vision_analysis': st.session_state.get('vision_analysis'),
                            'categorization_report': st.session_state.get('categorization_report'),
                            'complaint_analysis': st.session_state.get('complaint_analysis')
                        }
                        
                        # Generate export
                        buffer = export_manager.export_report(selected_format, export_data)
                        filename = export_manager.get_export_filename(selected_format, competitor_name)
                        
                        # Provide download
                        mime_types = {
                            'PDF': 'application/pdf',
                            'Word': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                            'Excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        }
                        
                        st.download_button(
                            label=f"📥 Download {selected_format} Report",
                            data=buffer,
                            file_name=filename,
                            mime=mime_types.get(selected_format, 'application/octet-stream'),
                            key="download_report"
                        )
                        
                        st.success(f"✅ {selected_format} report generated successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Export failed: {str(e)}")
                        st.info("💡 Tip: Make sure required libraries are installed for your chosen format")
            
            with col3:
                # Export format information
                format_info = {
                    'PDF': '📄 Professional report with formatted tables and charts',
                    'Word': '📝 Editable document for collaboration and customization',
                    'Excel': '📊 Structured data with multiple sheets for analysis'
                }
                
                if selected_format in format_info:
                    st.info(format_info[selected_format])
        else:
            st.warning("⚠️ No export formats available. Please install required libraries:")
            st.code("""
# Install export dependencies
pip install reportlab python-docx openpyxl

# PDF export: reportlab
# Word export: python-docx  
# Excel export: openpyxl
            """)
        
        st.markdown("---")
        
        # Battlecard Generation
        st.markdown("### 🎯 Sales Battlecard Generation")
        
        # Import battlecard generator
        from utils.battlecard_generator import BattlecardGenerator
        
        # Check if we have sufficient data for battlecard generation
        has_pricing = bool(st.session_state.get('pricing_analysis'))
        has_monetization = bool(st.session_state.get('monetization_analysis'))
        has_vision = bool(st.session_state.get('vision_analysis'))
        has_complaints = bool(st.session_state.get('categorization_report'))
        
        data_completeness = sum([has_pricing, has_monetization, has_vision, has_complaints])
        
        if data_completeness >= 2:  # Need at least 2 analysis types
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if st.button("🎯 Generate Sales Battlecard", type="primary"):
                    try:
                        # Initialize battlecard generator
                        battlecard_generator = BattlecardGenerator()
                        
                        # Prepare battlecard data
                        battlecard_data = {
                            'competitor_name': competitor_name,
                            'competitor_url': st.session_state.get('current_url', 'Unknown'),
                            'country': st.session_state.get('current_country', 'US'),
                            'selected_objective': st.session_state.get('selected_objective', 'General Analysis'),
                            'phase_config': phase_config,
                            'discovered_urls': discovered_urls,
                            'discovery_summary': discovery_summary,
                            'scraping_results': scraping_results,
                            'analyzed_pages': analyzed_pages,
                            'pricing_analysis': st.session_state.get('pricing_analysis'),
                            'monetization_analysis': st.session_state.get('monetization_analysis'),
                            'vision_analysis': st.session_state.get('vision_analysis'),
                            'categorization_report': st.session_state.get('categorization_report'),
                            'complaint_analysis': st.session_state.get('complaint_analysis')
                        }
                        
                        # Generate battlecard
                        with st.spinner("Generating sales battlecard..."):
                            battlecard = battlecard_generator.generate_battlecard(battlecard_data)
                            st.session_state.battlecard = battlecard
                            st.session_state.battlecard_generated = True
                        
                        st.success("✅ Sales battlecard generated successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Battlecard generation failed: {str(e)}")
                        st.info("💡 Tip: Ensure you have sufficient analysis data for battlecard generation")
            
            with col2:
                st.info(f"📊 Data completeness: {data_completeness}/4 analysis types available")
                
                # Show data availability
                data_status = {
                    "💰 Pricing Analysis": "✅ Available" if has_pricing else "❌ Missing",
                    "💼 Monetization Analysis": "✅ Available" if has_monetization else "❌ Missing",
                    "🔮 Vision Analysis": "✅ Available" if has_vision else "❌ Missing",
                    "📱 Complaint Analysis": "✅ Available" if has_complaints else "❌ Missing"
                }
                
                for analysis_type, status in data_status.items():
                    st.markdown(f"**{analysis_type}**: {status}")
        else:
            st.warning("⚠️ Insufficient data for battlecard generation. Need at least 2 analysis types.")
            st.info("💡 Run more analysis phases to enable battlecard generation")
        
        # Display generated battlecard
        if st.session_state.get('battlecard_generated', False) and st.session_state.get('battlecard'):
            st.markdown("---")
            st.markdown("### 📋 Generated Sales Battlecard")
            
            battlecard = st.session_state.battlecard
            
            # Battlecard header
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Competitive Position", battlecard.competitive_position)
            
            with col2:
                threat_color = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(battlecard.threat_level, '⚪')
                st.metric("Threat Level", f"{threat_color} {battlecard.threat_level.title()}")
            
            with col3:
                st.metric("Confidence Score", f"{battlecard.confidence_score:.2f}")
            
            # Executive Summary
            st.markdown("#### Executive Summary")
            st.info(battlecard.executive_summary)
            
            # Key battlecard sections in expandable format
            battlecard_sections = [
                (battlecard.positioning_advantages, "🎯"),
                (battlecard.objection_handling, "💬"),
                (battlecard.talking_points, "🗣️"),
                (battlecard.pricing_strategy, "💰"),
                (battlecard.competitive_weaknesses, "⚠️"),
                (battlecard.sales_strategy, "📈"),
                (battlecard.qualifying_questions, "❓"),
                (battlecard.demo_focus_areas, "🎪")
            ]
            
            for section, emoji in battlecard_sections:
                with st.expander(f"{emoji} {section.title}", expanded=False):
                    for item in section.content:
                        if item.strip():  # Skip empty lines
                            st.markdown(item)
            
            # Export battlecard
            st.markdown("#### Export Battlecard")
            col1, col2 = st.columns(2)
            
            with col1:
                # Export as Markdown
                markdown_content = battlecard_generator.export_battlecard_markdown(battlecard)
                st.download_button(
                    label="📝 Download Markdown",
                    data=markdown_content,
                    file_name=f"battlecard_{competitor_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )
            
            with col2:
                # Export as JSON
                json_content = battlecard_generator.export_battlecard_json(battlecard)
                st.download_button(
                    label="📊 Download JSON",
                    data=json_content,
                    file_name=f"battlecard_{competitor_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            
            # Show metadata
            with st.expander("📋 Battlecard Metadata"):
                st.markdown(f"**Data Sources:** {', '.join(battlecard.data_sources)}")
                st.markdown(f"**Analysis Completeness:** {sum(battlecard.analysis_completeness.values())}/{len(battlecard.analysis_completeness)} modules")
                st.markdown(f"**Last Updated:** {battlecard.last_updated}")
        
        st.markdown("---")
        
        # Create tabs for better organization
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", 
            "🔍 Technical Analysis", 
            "💰 Business Intelligence",
            "📱 Competitive Intelligence", 
            "📄 Content Insights"
        ])
        
        # Tab 1: Overview (Executive Summary)
        with tab1:
            st.markdown("### Executive Summary")
            
            # Basic competitor info
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Competitor:** {competitor_name}")
                st.markdown(f"**Website:** {st.session_state.get('current_url', 'Unknown')}")
                st.markdown(f"**Target Country:** {st.session_state.get('current_country', 'US')}")
                st.markdown(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                
                # Show selected objective
                if st.session_state.get('selected_objective'):
                    st.markdown(f"**Analysis Objective:** {st.session_state.get('selected_objective')}")
            
            with col2:
                # Show enabled phases
                if phase_config:
                    st.markdown("**Analysis Phases Executed:**")
                    phase_names = ["URL Discovery", "Content Scraping", "Content Analysis", "Google Search", "Social Media Scraping", "AI Categorization"]
                    phase_keys = ["phase1_enabled", "phase2_enabled", "phase3_enabled", "phase4_enabled", "phase5_enabled", "phase6_enabled"]
                    
                    for i, (name, key) in enumerate(zip(phase_names, phase_keys)):
                        enabled = phase_config.get(key, True)
                        status = "✅" if enabled else "⏭️"
                        st.markdown(f"{status} Phase {i+1}: {name}")
            
            # Key metrics
            st.markdown("#### Key Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if phase_config.get('phase1_enabled', True):
                    total_urls = discovery_summary.get('total_urls_found', 0)
                    st.metric("Total URLs Found", total_urls)
                else:
                    st.metric("Total URLs Found", "Phase Skipped")
            
            with col2:
                if phase_config.get('phase1_enabled', True):
                    pricing_count = len(discovered_urls.get('pricing', []))
                    st.metric("Pricing Pages", pricing_count)
                else:
                    st.metric("Pricing Pages", "Phase Skipped")
            
            with col3:
                if phase_config.get('phase1_enabled', True):
                    features_count = len(discovered_urls.get('features', []))
                    st.metric("Features Pages", features_count)
                else:
                    st.metric("Features Pages", "Phase Skipped")
            
            with col4:
                if phase_config.get('phase1_enabled', True):
                    blog_count = len(discovered_urls.get('blog', []))
                    st.metric("Blog/News Pages", blog_count)
                else:
                    st.metric("Blog/News Pages", "Phase Skipped")
            
            # Country-specific context
            if st.session_state.get('current_country'):
                country_context = country_localization.get_competitor_context(st.session_state.current_country)
                
                with st.expander("🌍 Country-Specific Analysis Context"):
                    st.markdown(f"**Primary Currency:** {country_context['currency']}")
                    st.markdown(f"**Business Context:** {country_context['business_context']}")
                    st.markdown(f"**Top Social Platforms:** {', '.join(country_context['social_platforms'][:3])}")
                    st.markdown(f"**Review Sites:** {', '.join(country_context['review_sites'][:3])}")
                    st.markdown(f"**Search Domain:** {country_context['google_domain']}")
            
            # URL distribution chart
            if phase_config.get('phase1_enabled', True) and discovered_urls:
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
            elif not phase_config.get('phase1_enabled', True):
                st.info("📊 URL distribution chart not available - URL Discovery phase was skipped")
        
        # Tab 2: Technical Analysis
        with tab2:
            st.markdown("### Technical Analysis")
            
            # URL Discovery Results
            st.markdown("#### 🔍 URL Discovery Results")
            if not phase_config.get('phase1_enabled', True):
                st.warning("⏭️ URL Discovery phase was skipped. No results available.")
            else:
                if discovery_summary:
                    # Show discovery stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Discovery Strategies", discovery_summary.get('strategies_used', 0))
                    with col2:
                        st.metric("Success Rate", f"{discovery_summary.get('success_rate', 0):.1f}%")
                    with col3:
                        st.metric("Total Time", f"{discovery_summary.get('total_time', 0):.1f}s")
                    
                    with st.expander("View Complete Discovery Summary"):
                        st.json(discovery_summary)
                else:
                    st.info("No discovery summary available.")
            
            # Content Analysis Results
            st.markdown("#### 📄 Content Analysis Results")
            if not phase_config.get('phase2_enabled', True):
                st.warning("⏭️ Content Scraping phase was skipped. No results available.")
            else:
                if scraping_results and analyzed_pages:
                    # Scraping summary
                    summary = scraping_results.get('summary', {})
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Pages Scraped", summary.get('successful', 0))
                    
                    with col2:
                        st.metric("Success Rate", f"{summary.get('success_rate', 0):.1f}%")
                    
                    with col3:
                        if phase_config.get('phase3_enabled', True):
                            avg_quality = sum(page['quality'].get('completeness_score', 0) for page in analyzed_pages) / len(analyzed_pages) if analyzed_pages else 0
                            st.metric("Avg Quality Score", f"{avg_quality:.1f}%")
                        else:
                            st.metric("Avg Quality Score", "Phase 3 Skipped")
                    
                    # Content quality analysis - only if Phase 3 is enabled
                    if phase_config.get('phase3_enabled', True):
                        st.markdown("##### Content Quality Analysis")
                        
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
                        with st.expander("View Detailed Page Analysis"):
                            for page in analyzed_pages:
                                category_emoji = {
                                    'pricing': '💰', 'features': '🎯', 'blog': '📰', 
                                    'careers': '💼', 'contact': '📞', 'about': '🏢'
                                }.get(page['category'], '📄')
                                
                                st.markdown(f"**{category_emoji} {page['title']} ({page['category']})**")
                                st.markdown(f"- **URL:** {page['url']}")
                                st.markdown(f"- **Word Count:** {page['word_count']}")
                                st.markdown(f"- **Quality Score:** {page['quality'].get('completeness_score', 0):.1f}%")
                                
                                if page['meta_description']:
                                    st.markdown(f"- **Meta Description:** {page['meta_description']}")
                                
                                # Show headings structure
                                headings = page['headings']
                                if any(headings.values()):
                                    st.markdown("- **Page Structure:**")
                                    for level, heading_list in headings.items():
                                        if heading_list:
                                            st.markdown(f"  - {level.upper()}: {', '.join(heading_list[:3])}")
                                st.markdown("---")
                    else:
                        st.info("📊 Content quality analysis not available - Content Analysis phase was skipped")
                else:
                    st.info("No content analysis results available.")
            
            # Features Analysis
            st.markdown("#### 🎯 Features Analysis")
            features_analysis = st.session_state.get('features_analysis', None)
            if features_analysis:
                # Display features analysis results here
                st.info("Features analysis results would be displayed here when available.")
            else:
                st.info("No features analysis available.")
        
        # Tab 3: Business Intelligence  
        with tab3:
            st.markdown("### Business Intelligence")
            
            # Pricing Analysis
            st.markdown("#### 💰 Pricing Analysis")
            if not (phase_config.get('phase2_enabled', True) or phase_config.get('phase3_enabled', True)):
                st.warning("⏭️ Content Scraping/Analysis phases were skipped. No pricing analysis available.")
            else:
                pricing_analysis = st.session_state.get('pricing_analysis', None)
                if pricing_analysis:
                    _render_pricing_analysis_tab(pricing_analysis)
                else:
                    st.info("No pricing analysis available.")
            
            st.markdown("---")
            
            # Monetization Analysis
            st.markdown("#### 💼 Monetization Analysis")
            if not (phase_config.get('phase2_enabled', True) or phase_config.get('phase3_enabled', True)):
                st.warning("⏭️ Content Scraping/Analysis phases were skipped. No monetization analysis available.")
            else:
                monetization_analysis = st.session_state.get('monetization_analysis', None)
                if monetization_analysis:
                    _render_monetization_analysis_tab(monetization_analysis)
                else:
                    st.info("No monetization analysis available.")
            
            st.markdown("---")
            
            # Vision & Roadmap Analysis
            st.markdown("#### 🔮 Vision & Roadmap Analysis")
            if not (phase_config.get('phase2_enabled', True) or phase_config.get('phase3_enabled', True)):
                st.warning("⏭️ Content Scraping/Analysis phases were skipped. No vision analysis available.")
            else:
                vision_analysis = st.session_state.get('vision_analysis', None)
                if vision_analysis:
                    _render_vision_analysis_tab(vision_analysis)
                else:
                    st.info("No vision analysis available.")
        
        # Tab 4: Competitive Intelligence
        with tab4:
            st.markdown("### Competitive Intelligence")
            
            # AI Categorized Complaints
            st.markdown("#### 🤖 AI Categorized Complaints")
            if not (phase_config.get('phase4_enabled', True) or phase_config.get('phase5_enabled', True)):
                st.warning("⏭️ Social media analysis phases were skipped. No complaint analysis available.")
            else:
                categorization_report = st.session_state.get('categorization_report', None)
                if categorization_report:
                    _render_complaint_categorization_tab(categorization_report)
                else:
                    st.info("No complaint categorization results available.")
            
            st.markdown("---")
            
            # Social Media Complaints
            st.markdown("#### 📱 Social Media Complaints")
            if not phase_config.get('phase4_enabled', True):
                st.warning("⏭️ Google Search phase was skipped. No social media complaints available.")
            else:
                complaint_analysis = st.session_state.get('complaint_analysis', None)
                if complaint_analysis:
                    _render_social_complaints_tab(complaint_analysis)
                else:
                    st.info("No social media complaint analysis available.")
        
        # Tab 5: Content Insights
        with tab5:
            st.markdown("### Content Insights")
            
            if not (phase_config.get('phase1_enabled', True) and phase_config.get('phase2_enabled', True)):
                st.warning("⏭️ URL Discovery and Content Scraping phases were skipped. No content insights available.")
            else:
                # Blog & News
                st.markdown("#### 📰 Blog & News")
                blog_pages = [page for page in analyzed_pages if page.get('category') == 'blog'] if analyzed_pages else []
                if blog_pages:
                    for page in blog_pages[:5]:  # Show top 5 blog posts
                        with st.expander(f"📰 {page['title']}"):
                            st.markdown(f"**URL:** {page['url']}")
                            st.markdown(f"**Word Count:** {page['word_count']}")
                            if page.get('meta_description'):
                                st.markdown(f"**Description:** {page['meta_description']}")
                else:
                    st.info("No blog/news content found.")
                
                st.markdown("---")
                
                # Careers Pages
                st.markdown("#### 💼 Careers Pages")
                career_pages = [page for page in analyzed_pages if page.get('category') == 'careers'] if analyzed_pages else []
                if career_pages:
                    for page in career_pages:
                        with st.expander(f"💼 {page['title']}"):
                            st.markdown(f"**URL:** {page['url']}")
                            st.markdown(f"**Word Count:** {page['word_count']}")
                            if page.get('meta_description'):
                                st.markdown(f"**Description:** {page['meta_description']}")
                else:
                    st.info("No careers content found.")
                
                st.markdown("---")
                
                # Contact & Support
                st.markdown("#### 📞 Contact & Support")
                contact_pages = [page for page in analyzed_pages if page.get('category') == 'contact'] if analyzed_pages else []
                if contact_pages:
                    for page in contact_pages:
                        with st.expander(f"�� {page['title']}"):
                            st.markdown(f"**URL:** {page['url']}")
                            st.markdown(f"**Word Count:** {page['word_count']}")
                            if page.get('contact_info'):
                                contact_info = page['contact_info']
                                if contact_info.get('email'):
                                    st.markdown(f"**Email:** {contact_info['email']}")
                                if contact_info.get('phone'):
                                    st.markdown(f"**Phone:** {contact_info['phone']}")
                else:
                    st.info("No contact/support content found.")
                
                st.markdown("---")
                
                # About Pages
                st.markdown("#### 🏢 About Pages")
                about_pages = [page for page in analyzed_pages if page.get('category') == 'about'] if analyzed_pages else []
                if about_pages:
                    for page in about_pages:
                        with st.expander(f"🏢 {page['title']}"):
                            st.markdown(f"**URL:** {page['url']}")
                            st.markdown(f"**Word Count:** {page['word_count']}")
                            if page.get('meta_description'):
                                st.markdown(f"**Description:** {page['meta_description']}")
                else:
                    st.info("No about content found.")
    
    elif st.session_state.get('analysis_status') == "Running":
        st.info("Analysis in progress... Please wait for completion to view reports.")
        
    elif st.session_state.get('analysis_status') == "Error":
        st.error("Analysis encountered an error. Please try running the analysis again.")
        
    else:
        st.info("No analysis results available. Please run an analysis first in the Analysis tab.")

def _render_pricing_analysis_tab(pricing_analysis):
    """Render pricing analysis content in the Business Intelligence tab"""
    competitor_name = pricing_analysis.get('competitor', 'Unknown')
    
    # Executive Summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        currency = pricing_analysis.get('currency_detected', 'USD')
        st.metric("Currency Detected", currency)
    
    with col2:
        hardware_model = pricing_analysis.get('hardware_pricing', {}).get('model_type', 'Unknown')
        st.metric("Hardware Model", hardware_model.title())
    
    with col3:
        software_model = pricing_analysis.get('software_pricing', {}).get('pricing_model', 'Unknown')
        st.metric("Software Model", software_model.title())
    
    with col4:
        hidden_fees_risk = pricing_analysis.get('hidden_fees', {}).get('risk_level', 'Unknown')
        risk_color = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(hidden_fees_risk, '⚪')
        st.metric("Hidden Fees Risk", f"{risk_color} {hidden_fees_risk.title()}")
    
    # Hardware Pricing Details
    with st.expander("🔧 Hardware Pricing Details"):
        hardware_pricing = pricing_analysis.get('hardware_pricing', {})
        if hardware_pricing:
            st.markdown(f"**Model Type:** {hardware_pricing.get('model_type', 'Unknown').title()}")
            st.markdown(f"**Cost Structure:** {hardware_pricing.get('cost_structure', 'Unknown').title()}")
            st.markdown(f"**Hardware Strategy:** {hardware_pricing.get('strategy_analysis', 'No analysis available')}")
            
            if hardware_pricing.get('specific_costs'):
                st.markdown("**Detected Costs:**")
                for cost in hardware_pricing['specific_costs'][:5]:
                    st.markdown(f"- {cost}")
        else:
            st.info("No hardware pricing details available.")
    
    # Software Pricing Details
    with st.expander("💻 Software Pricing Details"):
        software_pricing = pricing_analysis.get('software_pricing', {})
        if software_pricing:
            st.markdown(f"**Pricing Model:** {software_pricing.get('pricing_model', 'Unknown').title()}")
            st.markdown(f"**Billing Axis:** {software_pricing.get('billing_axis', 'Unknown').title()}")
            
            if software_pricing.get('tier_breakdown'):
                st.markdown("**Pricing Tiers:**")
                for tier in software_pricing['tier_breakdown'][:3]:
                    st.markdown(f"- **{tier.get('name', 'Unknown')}:** {tier.get('price', 'Unknown')} - {tier.get('description', 'No description')}")
        else:
            st.info("No software pricing details available.")
    
    # Hidden Fees Analysis
    with st.expander("💸 Hidden Fees Analysis"):
        hidden_fees = pricing_analysis.get('hidden_fees', {})
        if hidden_fees and hidden_fees.get('fees_detected'):
            st.markdown(f"**Risk Level:** {hidden_fees.get('risk_level', 'Unknown').title()}")
            st.markdown(f"**Total Fees Found:** {len(hidden_fees.get('fees_detected', []))}")
            
            st.markdown("**Detected Hidden Fees:**")
            for fee in hidden_fees.get('fees_detected', [])[:5]:
                fee_type = fee.get('type', 'Unknown').replace('_', ' ').title()
                st.markdown(f"- **{fee_type}:** {fee.get('description', 'No description')} (Confidence: {fee.get('confidence', 0):.2f})")
        else:
            st.info("No hidden fees detected.")

def _render_monetization_analysis_tab(monetization_analysis):
    """Render monetization analysis content in the Business Intelligence tab"""
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    revenue_streams = monetization_analysis.get('revenue_streams', {})
    lock_in_strategies = monetization_analysis.get('lock_in_strategies', {})
    expansion_revenue = monetization_analysis.get('expansion_revenue', {})
    
    with col1:
        revenue_model = revenue_streams.get('revenue_model_type', 'Unknown')
        st.metric("Revenue Model", revenue_model.title())
    
    with col2:
        lock_in_strength = lock_in_strategies.get('lock_in_strength', 'Unknown')
        strength_color = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(lock_in_strength, '⚪')
        st.metric("Lock-in Strength", f"{strength_color} {lock_in_strength.title()}")
    
    with col3:
        expansion_potential = expansion_revenue.get('expansion_potential', 'Unknown')
        potential_color = {'low': '🔴', 'medium': '🟡', 'high': '🟢'}.get(expansion_potential, '⚪')
        st.metric("Expansion Potential", f"{potential_color} {expansion_potential.title()}")
    
    with col4:
        confidence = monetization_analysis.get('confidence_scores', {}).get('overall_confidence', 0)
        st.metric("Analysis Confidence", f"{confidence:.2f}")
    
    # Revenue Streams
    with st.expander("💰 Revenue Streams Analysis"):
        primary_streams = revenue_streams.get('primary_streams', [])
        if primary_streams:
            st.markdown("**Primary Revenue Streams:**")
            for stream in primary_streams[:3]:
                stream_type = stream.get('type', 'Unknown').replace('_', ' ').title()
                st.markdown(f"- **{stream_type}** (Confidence: {stream.get('confidence', 0):.2f})")
        else:
            st.info("No revenue streams identified.")
    
    # Customer Lock-in Strategies
    with st.expander("🔒 Customer Lock-in Analysis"):
        lock_in_mechanisms = lock_in_strategies.get('lock_in_mechanisms', [])
        if lock_in_mechanisms:
            st.markdown("**Lock-in Mechanisms:**")
            for mechanism in lock_in_mechanisms[:3]:
                mechanism_type = mechanism.get('type', 'Unknown').replace('_', ' ').title()
                st.markdown(f"- **{mechanism_type}** (Strength: {mechanism.get('strength', 'Unknown')})")
        else:
            st.info("No lock-in mechanisms identified.")
    
    # Expansion Revenue
    with st.expander("📈 Expansion Revenue Analysis"):
        expansion_mechanisms = expansion_revenue.get('expansion_mechanisms', [])
        if expansion_mechanisms:
            st.markdown("**Expansion Mechanisms:**")
            for mechanism in expansion_mechanisms[:3]:
                mechanism_type = mechanism.get('type', 'Unknown').replace('_', ' ').title()
                st.markdown(f"- **{mechanism_type}** (Potential: {mechanism.get('potential', 'Unknown')})")
        else:
            st.info("No expansion mechanisms identified.")

def _render_vision_analysis_tab(vision_analysis):
    """Render vision analysis content in the Business Intelligence tab"""
    competitor_name = vision_analysis.get('competitor', 'Unknown')
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    product_roadmap = vision_analysis.get('product_roadmap', {})
    technology_investments = vision_analysis.get('technology_investments', {})
    market_expansion = vision_analysis.get('market_expansion', {})
    
    with col1:
        roadmap_signals = len(product_roadmap.get('upcoming_features', []))
        st.metric("Roadmap Signals", roadmap_signals)
    
    with col2:
        tech_investments = len(technology_investments.get('investment_areas', []))
        st.metric("Tech Investment Areas", tech_investments)
    
    with col3:
        market_targets = len(market_expansion.get('geographic_targets', []))
        st.metric("Market Expansion Signals", market_targets)
    
    with col4:
        confidence = vision_analysis.get('confidence_scores', {}).get('overall_confidence', 0)
        st.metric("Analysis Confidence", f"{confidence:.2f}")
    
    # Product Roadmap
    with st.expander("🛣️ Product Roadmap Analysis"):
        upcoming_features = product_roadmap.get('upcoming_features', [])
        if upcoming_features:
            st.markdown("**Upcoming Features:**")
            for feature in upcoming_features[:5]:
                st.markdown(f"- **{feature.get('feature', 'Unknown')}** (Confidence: {feature.get('confidence', 0):.2f})")
        else:
            st.info("No product roadmap signals identified.")
    
    # Technology Investments
    with st.expander("💻 Technology Investment Analysis"):
        investment_areas = technology_investments.get('investment_areas', [])
        if investment_areas:
            st.markdown("**Technology Investment Areas:**")
            for area in investment_areas[:5]:
                area_name = area.get('area', 'Unknown').replace('_', ' ').title()
                st.markdown(f"- **{area_name}** (Investment Level: {area.get('investment_level', 'Unknown')})")
        else:
            st.info("No technology investment signals identified.")
    
    # Market Expansion
    with st.expander("🌍 Market Expansion Analysis"):
        geographic_targets = market_expansion.get('geographic_targets', [])
        if geographic_targets:
            st.markdown("**Geographic Expansion Targets:**")
            for target in geographic_targets[:5]:
                st.markdown(f"- **{target.get('region', 'Unknown')}** (Probability: {target.get('probability', 'Unknown')})")
        else:
            st.info("No market expansion signals identified.")

def _render_complaint_categorization_tab(categorization_report):
    """Render complaint categorization content in the Competitive Intelligence tab"""
    overall_stats = categorization_report.get('overall_statistics', {})
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Complaints", overall_stats.get('total_complaints', 0))
    
    with col2:
        category_dist = overall_stats.get('category_distribution', {})
        top_category = max(category_dist.items(), key=lambda x: x[1]) if category_dist else ('None', 0)
        st.metric("Top Category", f"{top_category[0]} ({top_category[1]})")
    
    with col3:
        severity_dist = overall_stats.get('severity_distribution', {})
        high_critical = severity_dist.get('High', 0) + severity_dist.get('Critical', 0)
        st.metric("High/Critical Issues", high_critical)
    
    with col4:
        confidence_dist = overall_stats.get('confidence_distribution', {})
        high_confidence = confidence_dist.get('High', 0)
        st.metric("High Confidence", high_confidence)
    
    # Category Breakdown
    with st.expander("📊 Category Breakdown"):
        if category_dist:
            import pandas as pd
            df = pd.DataFrame(list(category_dist.items()), columns=['Category', 'Count'])
            st.bar_chart(df.set_index('Category'))
        else:
            st.info("No category distribution data available.")
    
    # Severity Analysis
    with st.expander("⚠️ Severity Analysis"):
        if severity_dist:
            import pandas as pd
            df = pd.DataFrame(list(severity_dist.items()), columns=['Severity', 'Count'])
            st.bar_chart(df.set_index('Severity'))
        else:
            st.info("No severity distribution data available.")

def _render_social_complaints_tab(complaint_analysis):
    """Render social complaints content in the Competitive Intelligence tab"""
    # Key Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Complaints", complaint_analysis.get('total_complaints', 0))
    
    with col2:
        platforms_searched = len(complaint_analysis.get('platforms', {}))
        st.metric("Platforms Searched", platforms_searched)
    
    with col3:
        top_complaints = complaint_analysis.get('top_complaints', [])
        if top_complaints:
            max_score = max(c.get('complaint_score', 0) for c in top_complaints)
            st.metric("Max Complaint Score", f"{max_score:.2f}")
        else:
            st.metric("Max Complaint Score", "N/A")
    
    # Platform Breakdown
    with st.expander("📱 Platform Breakdown"):
        platforms = complaint_analysis.get('platforms', {})
        if platforms:
            import pandas as pd
            platform_data = []
            for platform, data in platforms.items():
                platform_data.append({
                    'Platform': platform.title(),
                    'Complaints': data.get('complaint_count', 0),
                    'Sources': data.get('source_count', 0)
                })
            df = pd.DataFrame(platform_data)
            st.dataframe(df)
        else:
            st.info("No platform data available.")
    
    # Top Complaints
    with st.expander("🔥 Top Complaints"):
        if top_complaints:
            for i, complaint in enumerate(top_complaints[:5], 1):
                st.markdown(f"**{i}. {complaint.get('title', 'No title')}**")
                st.markdown(f"Score: {complaint.get('complaint_score', 0):.2f} | Platform: {complaint.get('platform', 'Unknown')}")
                if complaint.get('excerpt'):
                    st.markdown(f"_{complaint['excerpt'][:200]}..._")
                st.markdown("---")
        else:
            st.info("No complaints available.")

def settings_tab():
    """Settings tab"""
    st.markdown("## Settings")
    
    # Configuration settings
    st.markdown("### Configuration Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Current Settings:**")
        st.markdown(f"• Max Results: {config.max_search_results}")
        st.markdown(f"• Request Timeout: {config.request_timeout}s")
        st.markdown(f"• Rate Limit Delay: {config.rate_limit_delay}s")
        st.markdown(f"• Scraping Delay: {config.scraping_delay}s")
        st.markdown(f"• Bypass Robots.txt: {'Yes' if config.bypass_robots_txt else 'No'}")
    
    with col2:
        st.markdown("**API Keys Status:**")
        st.markdown(f"• OpenAI API Key: {'✅ Set' if config.openai_api_key else '❌ Not Set'}")
        st.markdown(f"• Google API Key: {'✅ Set' if config.google_api_key else '❌ Not Set'}")
    
    # Update configuration
    st.markdown("### Update Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_max_results = st.number_input("Max Results", min_value=1, value=int(config.max_search_results), step=1)
        new_request_timeout = st.number_input("Request Timeout (seconds)", min_value=1, value=int(config.request_timeout), step=1)
        new_rate_limit_delay = st.number_input("Rate Limit Delay (seconds)", min_value=1.0, value=float(config.rate_limit_delay), step=1.0)
    
    with col2:
        new_scraping_delay = st.number_input("Scraping Delay (seconds)", min_value=1.0, value=float(config.scraping_delay), step=1.0)
        
        # Robots.txt bypass option with warning
        st.markdown("**⚠️ Advanced Scraping Options**")
        
        bypass_robots_txt = st.checkbox(
            "Bypass Robots.txt Restrictions",
            value=config.bypass_robots_txt,
            help="Enable this to bypass robots.txt restrictions for competitive analysis. Use responsibly and ethically."
        )
        
        if bypass_robots_txt:
            st.warning("⚠️ **Important:** Bypassing robots.txt should only be used for legitimate competitive analysis. "
                      "Ensure you comply with website terms of service and applicable laws. "
                      "Use this feature responsibly and maintain respectful crawling practices.")
    
    # Save changes
    if st.button("Save Configuration"):
        config.set('max_search_results', new_max_results)
        config.set('request_timeout', new_request_timeout)
        config.set('rate_limit_delay', new_rate_limit_delay)
        config.set('scraping_delay', new_scraping_delay)
        config.set('bypass_robots_txt', bypass_robots_txt)
        
        # Save to file
        config.save_config()
        
        st.success("Configuration updated successfully!")
        st.info("Changes will take effect on the next analysis run.")
        
        # Log configuration change
        logger.info(f"Configuration updated: bypass_robots_txt={bypass_robots_txt}")
    
    # Troubleshooting section
    st.markdown("---")
    st.markdown("### 🔧 Troubleshooting")
    
    with st.expander("Common Issues and Solutions"):
        st.markdown("""
        **Problem: "Robots.txt disallows fetching" errors**
        - **Solution:** Enable "Bypass Robots.txt Restrictions" above
        - **Note:** Only use this for legitimate competitive analysis
        - **Impact:** Will allow scraping of competitor pages that block automated access
        
        **Problem: Low scraping success rate**
        - **Solution 1:** Increase scraping delay to reduce rate limiting
        - **Solution 2:** Enable robots.txt bypass if competitor blocks crawlers
        - **Solution 3:** Check if competitor uses anti-bot measures
        
        **Problem: Timeout errors**
        - **Solution:** Increase request timeout setting
        - **Note:** Some sites may be slow to respond or have geographic restrictions
        
        **Problem: No meaningful pricing data**
        - **Solution 1:** Enable robots.txt bypass to access pricing pages
        - **Solution 2:** Manually input URLs if automatic discovery fails
        - **Solution 3:** Use alternative analysis methods (manual research)
        """)
    
    # Reset to defaults
    st.markdown("---")
    if st.button("Reset to Defaults", type="secondary"):
        config.reset_to_defaults()
        st.success("Configuration reset to default values!")
        st.experimental_rerun()

def help_tab():
    """Help tab"""
    st.markdown("## Help")
    st.markdown("### How to Use This Tool")
    st.markdown("1. **Enter Competitor Information:**")
    st.markdown("   - Enter the name and URL of the competitor you want to analyze.")
    st.markdown("2. **Select Analysis Phases:**")
    st.markdown("   - Choose which analysis phases you want to run.")
    st.markdown("3. **Run Analysis:**")
    st.markdown("   - Click the 'Run Analysis' button to start the analysis process.")
    st.markdown("4. **View Results:**")
    st.markdown("   - Go to the 'Reports' tab to view detailed analysis results.")
    st.markdown("5. **Export Data:**")
    st.markdown("   - Use the export options to save your analysis results.")
    st.markdown("### About This Tool")
    st.markdown("This tool uses advanced AI and web scraping techniques to analyze competitors' websites. It provides a deep dive comparative report on the competitor versus StoreHub.")
    st.markdown("### Contact")
    st.markdown("For any questions or feedback, please contact us at [support@storehub.com](mailto:support@storehub.com).")

if __name__ == "__main__":
    main()