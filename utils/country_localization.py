"""
Country-specific localization and configuration for competitive analysis.
This module handles country-specific search domains, social media platforms,
currencies, and localized analysis strategies.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CountryConfig:
    """Configuration for country-specific analysis"""
    code: str
    name: str
    google_domain: str
    primary_currency: str
    secondary_currencies: List[str]
    social_platforms: List[str]
    review_sites: List[str]
    language_codes: List[str]
    timezone: str
    business_context: str

class CountryLocalization:
    """Handles country-specific localization for competitive analysis"""
    
    # Comprehensive country configurations
    COUNTRIES = {
        'US': CountryConfig(
            code='US',
            name='United States',
            google_domain='google.com',
            primary_currency='USD',
            secondary_currencies=['CAD'],
            social_platforms=['facebook.com', 'twitter.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'reddit.com'],
            review_sites=['g2.com', 'capterra.com', 'trustpilot.com', 'yelp.com'],
            language_codes=['en'],
            timezone='America/New_York',
            business_context='B2B SaaS focused, high competition, mature market'
        ),
        'UK': CountryConfig(
            code='UK',
            name='United Kingdom',
            google_domain='google.co.uk',
            primary_currency='GBP',
            secondary_currencies=['EUR', 'USD'],
            social_platforms=['facebook.com', 'twitter.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'reddit.com'],
            review_sites=['trustpilot.com', 'g2.com', 'capterra.com', 'reviews.co.uk'],
            language_codes=['en'],
            timezone='Europe/London',
            business_context='GDPR compliant, VAT considerations, mature fintech market'
        ),
        'AU': CountryConfig(
            code='AU',
            name='Australia',
            google_domain='google.com.au',
            primary_currency='AUD',
            secondary_currencies=['USD', 'NZD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'productreview.com.au', 'g2.com'],
            language_codes=['en'],
            timezone='Australia/Sydney',
            business_context='Growing fintech market, strict financial regulations'
        ),
        'CA': CountryConfig(
            code='CA',
            name='Canada',
            google_domain='google.ca',
            primary_currency='CAD',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'twitter.com', 'instagram.com', 'youtube.com', 'linkedin.com'],
            review_sites=['g2.com', 'capterra.com', 'trustpilot.com'],
            language_codes=['en', 'fr'],
            timezone='America/Toronto',
            business_context='Bilingual market, similar to US but with different regulations'
        ),
        'SG': CountryConfig(
            code='SG',
            name='Singapore',
            google_domain='google.com.sg',
            primary_currency='SGD',
            secondary_currencies=['USD', 'MYR'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['en', 'zh', 'ms', 'ta'],
            timezone='Asia/Singapore',
            business_context='FinTech hub, multicultural market, high digital adoption'
        ),
        'MY': CountryConfig(
            code='MY',
            name='Malaysia',
            google_domain='google.com.my',
            primary_currency='MYR',
            secondary_currencies=['SGD', 'USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'twitter.com'],
            review_sites=['trustpilot.com'],
            language_codes=['ms', 'en', 'zh'],
            timezone='Asia/Kuala_Lumpur',
            business_context='Growing digital economy, diverse cultural market'
        ),
        'DE': CountryConfig(
            code='DE',
            name='Germany',
            google_domain='google.de',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'xing.com'],
            review_sites=['trustpilot.com', 'g2.com', 'capterra.com'],
            language_codes=['de'],
            timezone='Europe/Berlin',
            business_context='Largest EU market, strong data privacy laws, traditional business culture'
        ),
        'FR': CountryConfig(
            code='FR',
            name='France',
            google_domain='google.fr',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['fr'],
            timezone='Europe/Paris',
            business_context='Strong local business culture, EU regulations, growing fintech'
        ),
        'JP': CountryConfig(
            code='JP',
            name='Japan',
            google_domain='google.co.jp',
            primary_currency='JPY',
            secondary_currencies=['USD'],
            social_platforms=['twitter.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'line.me'],
            review_sites=['trustpilot.com'],
            language_codes=['ja'],
            timezone='Asia/Tokyo',
            business_context='Unique business culture, mobile-first market, LINE dominance'
        ),
        'IN': CountryConfig(
            code='IN',
            name='India',
            google_domain='google.co.in',
            primary_currency='INR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['en', 'hi'],
            timezone='Asia/Kolkata',
            business_context='Rapidly growing digital economy, price-sensitive market'
        ),
        
        # Additional Asian Countries
        'CN': CountryConfig(
            code='CN',
            name='China',
            google_domain='google.com.hk',  # Google blocked in mainland China
            primary_currency='CNY',
            secondary_currencies=['USD', 'HKD'],
            social_platforms=['weibo.com', 'wechat.com', 'douyin.com', 'linkedin.com'],
            review_sites=['trustpilot.com'],
            language_codes=['zh'],
            timezone='Asia/Shanghai',
            business_context='Large but restricted market, unique digital ecosystem, government regulations'
        ),
        'KR': CountryConfig(
            code='KR',
            name='South Korea',
            google_domain='google.co.kr',
            primary_currency='KRW',
            secondary_currencies=['USD'],
            social_platforms=['instagram.com', 'youtube.com', 'facebook.com', 'twitter.com', 'linkedin.com'],
            review_sites=['trustpilot.com'],
            language_codes=['ko'],
            timezone='Asia/Seoul',
            business_context='Advanced digital economy, high smartphone penetration, tech-savvy consumers'
        ),
        'TH': CountryConfig(
            code='TH',
            name='Thailand',
            google_domain='google.co.th',
            primary_currency='THB',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'line.me', 'twitter.com'],
            review_sites=['trustpilot.com'],
            language_codes=['th', 'en'],
            timezone='Asia/Bangkok',
            business_context='Growing digital economy, LINE messaging dominance, tourism-focused market'
        ),
        'VN': CountryConfig(
            code='VN',
            name='Vietnam',
            google_domain='google.com.vn',
            primary_currency='VND',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com'],
            language_codes=['vi', 'en'],
            timezone='Asia/Ho_Chi_Minh',
            business_context='Fast-growing economy, young population, increasing digital adoption'
        ),
        'ID': CountryConfig(
            code='ID',
            name='Indonesia',
            google_domain='google.co.id',
            primary_currency='IDR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'twitter.com', 'linkedin.com'],
            review_sites=['trustpilot.com'],
            language_codes=['id', 'en'],
            timezone='Asia/Jakarta',
            business_context='Largest Southeast Asian economy, mobile-first market, diverse archipelago'
        ),
        'PH': CountryConfig(
            code='PH',
            name='Philippines',
            google_domain='google.com.ph',
            primary_currency='PHP',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'twitter.com', 'linkedin.com'],
            review_sites=['trustpilot.com'],
            language_codes=['en', 'fil'],
            timezone='Asia/Manila',
            business_context='English-speaking market, strong social media usage, growing BPO sector'
        ),
        'TW': CountryConfig(
            code='TW',
            name='Taiwan',
            google_domain='google.com.tw',
            primary_currency='TWD',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'line.me', 'linkedin.com'],
            review_sites=['trustpilot.com'],
            language_codes=['zh', 'en'],
            timezone='Asia/Taipei',
            business_context='Advanced technology market, strong manufacturing base, high digital adoption'
        ),
        'HK': CountryConfig(
            code='HK',
            name='Hong Kong',
            google_domain='google.com.hk',
            primary_currency='HKD',
            secondary_currencies=['USD', 'CNY'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com'],
            language_codes=['en', 'zh'],
            timezone='Asia/Hong_Kong',
            business_context='International financial hub, bridge to Chinese market, high business density'
        ),
        'KZ': CountryConfig(
            code='KZ',
            name='Kazakhstan',
            google_domain='google.kz',
            primary_currency='KZT',
            secondary_currencies=['USD', 'RUB'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'vk.com', 'linkedin.com'],
            review_sites=['trustpilot.com'],
            language_codes=['kk', 'ru', 'en'],
            timezone='Asia/Almaty',
            business_context='Oil-rich economy, Russian cultural influence, growing tech sector'
        ),
        'UZ': CountryConfig(
            code='UZ',
            name='Uzbekistan',
            google_domain='google.com',
            primary_currency='UZS',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'telegram.org'],
            review_sites=['trustpilot.com'],
            language_codes=['uz', 'ru'],
            timezone='Asia/Tashkent',
            business_context='Emerging market, economic reforms, growing digital infrastructure'
        ),
        
        # European Countries
        'ES': CountryConfig(
            code='ES',
            name='Spain',
            google_domain='google.es',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'twitter.com', 'linkedin.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['es', 'ca', 'gl', 'eu'],
            timezone='Europe/Madrid',
            business_context='Large EU market, strong tourism sector, growing startup ecosystem'
        ),
        'IT': CountryConfig(
            code='IT',
            name='Italy',
            google_domain='google.it',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'twitter.com', 'linkedin.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['it'],
            timezone='Europe/Rome',
            business_context='Major EU economy, strong manufacturing, traditional business culture'
        ),
        'NL': CountryConfig(
            code='NL',
            name='Netherlands',
            google_domain='google.nl',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['nl', 'en'],
            timezone='Europe/Amsterdam',
            business_context='Advanced digital economy, high English proficiency, innovation hub'
        ),
        'BE': CountryConfig(
            code='BE',
            name='Belgium',
            google_domain='google.be',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['nl', 'fr', 'de'],
            timezone='Europe/Brussels',
            business_context='EU headquarters, multilingual market, strong B2B focus'
        ),
        'CH': CountryConfig(
            code='CH',
            name='Switzerland',
            google_domain='google.ch',
            primary_currency='CHF',
            secondary_currencies=['EUR', 'USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['de', 'fr', 'it', 'rm'],
            timezone='Europe/Zurich',
            business_context='High-income market, financial services hub, quality-focused consumers'
        ),
        'AT': CountryConfig(
            code='AT',
            name='Austria',
            google_domain='google.at',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'xing.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['de'],
            timezone='Europe/Vienna',
            business_context='German-speaking market, strong industrial base, conservative business culture'
        ),
        'SE': CountryConfig(
            code='SE',
            name='Sweden',
            google_domain='google.se',
            primary_currency='SEK',
            secondary_currencies=['EUR', 'USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['sv', 'en'],
            timezone='Europe/Stockholm',
            business_context='Innovation leader, high digital adoption, sustainability focus'
        ),
        'NO': CountryConfig(
            code='NO',
            name='Norway',
            google_domain='google.no',
            primary_currency='NOK',
            secondary_currencies=['EUR', 'USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['no', 'en'],
            timezone='Europe/Oslo',
            business_context='Oil-rich economy, high income levels, strong worker protections'
        ),
        'DK': CountryConfig(
            code='DK',
            name='Denmark',
            google_domain='google.dk',
            primary_currency='DKK',
            secondary_currencies=['EUR', 'USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['da', 'en'],
            timezone='Europe/Copenhagen',
            business_context='Digital government leader, high trust society, green technology focus'
        ),
        'FI': CountryConfig(
            code='FI',
            name='Finland',
            google_domain='google.fi',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['fi', 'sv', 'en'],
            timezone='Europe/Helsinki',
            business_context='Tech innovation hub, Nokia legacy, high education levels'
        ),
        'PL': CountryConfig(
            code='PL',
            name='Poland',
            google_domain='google.pl',
            primary_currency='PLN',
            secondary_currencies=['EUR', 'USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['pl'],
            timezone='Europe/Warsaw',
            business_context='Largest Eastern European economy, growing tech sector, EU member'
        ),
        'CZ': CountryConfig(
            code='CZ',
            name='Czech Republic',
            google_domain='google.cz',
            primary_currency='CZK',
            secondary_currencies=['EUR', 'USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['cs'],
            timezone='Europe/Prague',
            business_context='Central European hub, strong manufacturing, growing services sector'
        ),
        'HU': CountryConfig(
            code='HU',
            name='Hungary',
            google_domain='google.hu',
            primary_currency='HUF',
            secondary_currencies=['EUR', 'USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['hu'],
            timezone='Europe/Budapest',
            business_context='Central European market, automotive industry, EU member'
        ),
        'RO': CountryConfig(
            code='RO',
            name='Romania',
            google_domain='google.ro',
            primary_currency='RON',
            secondary_currencies=['EUR', 'USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['ro'],
            timezone='Europe/Bucharest',
            business_context='Emerging market, IT outsourcing hub, growing economy'
        ),
        'BG': CountryConfig(
            code='BG',
            name='Bulgaria',
            google_domain='google.bg',
            primary_currency='BGN',
            secondary_currencies=['EUR', 'USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com'],
            language_codes=['bg'],
            timezone='Europe/Sofia',
            business_context='Lower-cost EU market, growing IT sector, tourism industry'
        ),
        'GR': CountryConfig(
            code='GR',
            name='Greece',
            google_domain='google.gr',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com'],
            language_codes=['el'],
            timezone='Europe/Athens',
            business_context='Tourism-focused economy, shipping industry, recovering from financial crisis'
        ),
        'PT': CountryConfig(
            code='PT',
            name='Portugal',
            google_domain='google.pt',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com'],
            language_codes=['pt'],
            timezone='Europe/Lisbon',
            business_context='Growing startup ecosystem, tourism industry, EU member'
        ),
        'IE': CountryConfig(
            code='IE',
            name='Ireland',
            google_domain='google.ie',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com', 'g2.com'],
            language_codes=['en', 'ga'],
            timezone='Europe/Dublin',
            business_context='European tech hub, multinational headquarters, English-speaking EU market'
        ),
        'SK': CountryConfig(
            code='SK',
            name='Slovakia',
            google_domain='google.sk',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com'],
            language_codes=['sk'],
            timezone='Europe/Bratislava',
            business_context='Central European market, automotive industry, EU member'
        ),
        'SI': CountryConfig(
            code='SI',
            name='Slovenia',
            google_domain='google.si',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com'],
            language_codes=['sl'],
            timezone='Europe/Ljubljana',
            business_context='Small but developed market, Alpine tourism, EU member'
        ),
        'HR': CountryConfig(
            code='HR',
            name='Croatia',
            google_domain='google.hr',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com'],
            language_codes=['hr'],
            timezone='Europe/Zagreb',
            business_context='Tourism-focused economy, recent EU member, growing IT sector'
        ),
        'EE': CountryConfig(
            code='EE',
            name='Estonia',
            google_domain='google.ee',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com'],
            language_codes=['et', 'en'],
            timezone='Europe/Tallinn',
            business_context='Digital society leader, e-governance pioneer, startup ecosystem'
        ),
        'LV': CountryConfig(
            code='LV',
            name='Latvia',
            google_domain='google.lv',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com'],
            language_codes=['lv', 'en'],
            timezone='Europe/Riga',
            business_context='Baltic economy, growing tech sector, EU member'
        ),
        'LT': CountryConfig(
            code='LT',
            name='Lithuania',
            google_domain='google.lt',
            primary_currency='EUR',
            secondary_currencies=['USD'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'twitter.com'],
            review_sites=['trustpilot.com'],
            language_codes=['lt', 'en'],
            timezone='Europe/Vilnius',
            business_context='Baltic economy, fintech innovation, EU member'
        ),
        'RU': CountryConfig(
            code='RU',
            name='Russia',
            google_domain='google.ru',
            primary_currency='RUB',
            secondary_currencies=['USD', 'EUR'],
            social_platforms=['vk.com', 'ok.ru', 'youtube.com', 'instagram.com', 'telegram.org'],
            review_sites=['trustpilot.com'],
            language_codes=['ru'],
            timezone='Europe/Moscow',
            business_context='Large market with unique platforms, sanctions impact, tech sector'
        ),
        'TR': CountryConfig(
            code='TR',
            name='Turkey',
            google_domain='google.com.tr',
            primary_currency='TRY',
            secondary_currencies=['USD', 'EUR'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'twitter.com', 'linkedin.com'],
            review_sites=['trustpilot.com'],
            language_codes=['tr'],
            timezone='Europe/Istanbul',
            business_context='Bridge between Europe and Asia, large population, growing tech sector'
        ),
        'UA': CountryConfig(
            code='UA',
            name='Ukraine',
            google_domain='google.com.ua',
            primary_currency='UAH',
            secondary_currencies=['USD', 'EUR'],
            social_platforms=['facebook.com', 'instagram.com', 'youtube.com', 'telegram.org', 'linkedin.com'],
            review_sites=['trustpilot.com'],
            language_codes=['uk', 'ru'],
            timezone='Europe/Kiev',
            business_context='IT outsourcing hub, ongoing conflict impact, resilient tech sector'
        ),
        
        # Global option for non-country-targeted analysis
        'GLOBAL': CountryConfig(
            code='GLOBAL',
            name='Global (All Countries)',
            google_domain='google.com',
            primary_currency='USD',
            secondary_currencies=['EUR', 'GBP', 'JPY', 'CNY'],
            social_platforms=['facebook.com', 'twitter.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'reddit.com'],
            review_sites=['g2.com', 'capterra.com', 'trustpilot.com'],
            language_codes=['en'],
            timezone='UTC',
            business_context='Global analysis without country-specific targeting, broader market perspective'
        )
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_country_config(self, country_code: str) -> Optional[CountryConfig]:
        """Get country configuration by code"""
        return self.COUNTRIES.get(country_code.upper())
    
    def get_available_countries(self) -> List[Tuple[str, str]]:
        """Get list of available countries as (code, name) tuples, with Global option first, then alphabetically sorted"""
        # Separate global option from specific countries
        global_option = None
        specific_countries = []
        
        for code, config in self.COUNTRIES.items():
            if code == 'GLOBAL':
                global_option = (code, config.name)
            else:
                specific_countries.append((code, config.name))
        
        # Sort specific countries alphabetically
        specific_countries.sort(key=lambda x: x[1])
        
        # Return global option first, then sorted countries
        result = []
        if global_option:
            result.append(global_option)
        result.extend(specific_countries)
        
        return result
    
    def get_google_search_domain(self, country_code: str) -> str:
        """Get Google search domain for country"""
        config = self.get_country_config(country_code)
        return config.google_domain if config else 'google.com'
    
    def get_currency_symbols(self, country_code: str) -> List[str]:
        """Get currency symbols to look for in pricing analysis"""
        config = self.get_country_config(country_code)
        if not config:
            return ['$', '€', '£', '¥', '₹']
        
        currency_symbols = {
            'USD': '$', 'CAD': 'C$', 'GBP': '£', 'EUR': '€', 
            'AUD': 'A$', 'SGD': 'S$', 'MYR': 'RM', 'JPY': '¥', 
            'INR': '₹', 'CNY': '¥', 'KRW': '₩', 'THB': '฿', 
            'VND': '₫', 'IDR': 'Rp', 'PHP': '₱', 'TWD': 'NT$',
            'HKD': 'HK$', 'KZT': '₸', 'UZS': 'лв', 'SEK': 'kr',
            'NOK': 'kr', 'DKK': 'kr', 'PLN': 'zł', 'CZK': 'Kč',
            'HUF': 'Ft', 'RON': 'lei', 'BGN': 'лв', 'CHF': 'CHF',
            'RUB': '₽', 'TRY': '₺', 'UAH': '₴'
        }
        
        # For global analysis, include major currency symbols
        if country_code == 'GLOBAL':
            return ['$', '€', '£', '¥', '₹', '₩', '₽', 'C$', 'A$', 'CHF']
        
        symbols = []
        if config.primary_currency in currency_symbols:
            symbols.append(currency_symbols[config.primary_currency])
        
        for currency in config.secondary_currencies:
            if currency in currency_symbols:
                symbols.append(currency_symbols[currency])
        
        return symbols
    
    def get_social_platforms(self, country_code: str) -> List[str]:
        """Get prioritized social media platforms for country"""
        config = self.get_country_config(country_code)
        return config.social_platforms if config else ['facebook.com', 'twitter.com', 'instagram.com', 'youtube.com']
    
    def get_review_sites(self, country_code: str) -> List[str]:
        """Get review sites relevant for country"""
        config = self.get_country_config(country_code)
        return config.review_sites if config else ['g2.com', 'capterra.com', 'trustpilot.com']
    
    def generate_search_queries(self, competitor_name: str, country_code: str) -> List[Dict[str, str]]:
        """Generate country-specific search queries for competitor analysis"""
        config = self.get_country_config(country_code)
        if not config:
            config = self.COUNTRIES['US']  # Default to US
        
        queries = []
        
        # Social media complaints
        for platform in config.social_platforms[:4]:  # Top 4 platforms
            queries.append({
                'platform': platform,
                'query': f'site:{platform} "{competitor_name}" problem OR issue OR complaint OR terrible OR broken OR support',
                'type': 'social_complaint'
            })
        
        # Review sites
        for site in config.review_sites:
            queries.append({
                'platform': site,
                'query': f'site:{site} "{competitor_name}" review OR complaint OR problem',
                'type': 'review'
            })
        
        # General complaints with country context
        queries.append({
            'platform': 'general',
            'query': f'"{competitor_name}" complaint OR problem OR issue OR terrible {config.name}',
            'type': 'general_complaint'
        })
        
        # Country-specific competitor analysis
        queries.append({
            'platform': 'general',
            'query': f'"{competitor_name}" vs OR alternative OR competitor {config.name}',
            'type': 'competitive'
        })
        
        # Pricing complaints
        queries.append({
            'platform': 'general',
            'query': f'"{competitor_name}" pricing OR expensive OR cost OR fee {config.primary_currency}',
            'type': 'pricing_complaint'
        })
        
        return queries
    
    def get_localized_pricing_patterns(self, country_code: str) -> List[str]:
        """Get country-specific pricing patterns to look for"""
        config = self.get_country_config(country_code)
        if not config:
            return ['price', 'cost', 'fee', 'subscription', 'monthly', 'annual']
        
        base_patterns = ['price', 'cost', 'fee', 'subscription', 'monthly', 'annual']
        
        # For global analysis, include common pricing terms from major languages
        if config.primary_currency == 'USD' and country_code == 'GLOBAL':
            base_patterns.extend([
                'per month', 'per year', 'one-time', 'setup fee',  # English
                'pro Monat', 'pro Jahr', 'einmalig',  # German
                'mensuel', 'annuel',  # French
                'per mese', 'per anno',  # Italian
                'per månad', 'per år',  # Swedish/Norwegian/Danish
                'miesięcznie', 'rocznie'  # Polish
            ])
            return base_patterns
        
        # For global analysis, use common English patterns
        if country_code == 'GLOBAL':
            base_patterns.extend(['per month', 'per year', 'monthly', 'yearly', 'annual', 'one-time', 'setup fee', 'subscription'])
            return base_patterns
        
        # Add currency-specific patterns
        if config.primary_currency == 'USD':
            base_patterns.extend(['per month', 'per year', 'one-time', 'setup fee'])
        elif config.primary_currency == 'EUR':
            base_patterns.extend(['pro Monat', 'pro Jahr', 'einmalig', 'mensuel', 'annuel', 'per mese', 'per anno'])
        elif config.primary_currency == 'GBP':
            base_patterns.extend(['per month', 'per year', 'one-off', 'setup charge'])
        elif config.primary_currency == 'JPY':
            base_patterns.extend(['月額', '年額', '一回', '初期費用'])
        elif config.primary_currency == 'CNY':
            base_patterns.extend(['每月', '每年', '一次性', '设置费'])
        elif config.primary_currency == 'KRW':
            base_patterns.extend(['월간', '연간', '일회성', '설정비'])
        elif config.primary_currency == 'THB':
            base_patterns.extend(['ต่อเดือน', 'ต่อปี', 'ครั้งเดียว'])
        elif config.primary_currency == 'VND':
            base_patterns.extend(['mỗi tháng', 'mỗi năm', 'một lần'])
        elif config.primary_currency == 'IDR':
            base_patterns.extend(['per bulan', 'per tahun', 'sekali bayar'])
        elif config.primary_currency == 'PHP':
            base_patterns.extend(['per month', 'per year', 'one-time'])
        elif config.primary_currency in ['SEK', 'NOK', 'DKK']:
            base_patterns.extend(['per månad', 'per år', 'engångsavgift'])
        elif config.primary_currency == 'PLN':
            base_patterns.extend(['miesięcznie', 'rocznie', 'jednorazowo'])
        elif config.primary_currency == 'CZK':
            base_patterns.extend(['měsíčně', 'ročně', 'jednorázově'])
        elif config.primary_currency == 'HUF':
            base_patterns.extend(['havonta', 'évente', 'egyszeri'])
        elif config.primary_currency == 'RUB':
            base_patterns.extend(['в месяц', 'в год', 'единоразово'])
        elif config.primary_currency == 'TRY':
            base_patterns.extend(['aylık', 'yıllık', 'tek seferlik'])
        elif config.primary_currency == 'UAH':
            base_patterns.extend(['на місяць', 'на рік', 'одноразово'])
        
        return base_patterns
    
    def get_business_context(self, country_code: str) -> str:
        """Get business context for country"""
        config = self.get_country_config(country_code)
        return config.business_context if config else 'General competitive market'
    
    def format_currency(self, amount: float, country_code: str) -> str:
        """Format currency amount for country"""
        config = self.get_country_config(country_code)
        if not config:
            return f"${amount:.2f}"
        
        # For global analysis, use USD as default
        if country_code == 'GLOBAL':
            return f"${amount:.2f}"
        
        currency_formats = {
            'USD': f"${amount:.2f}",
            'CAD': f"C${amount:.2f}",
            'GBP': f"£{amount:.2f}",
            'EUR': f"€{amount:.2f}",
            'AUD': f"A${amount:.2f}",
            'SGD': f"S${amount:.2f}",
            'MYR': f"RM{amount:.2f}",
            'JPY': f"¥{amount:.0f}",
            'INR': f"₹{amount:.2f}",
            'CNY': f"¥{amount:.2f}",
            'KRW': f"₩{amount:.0f}",
            'THB': f"฿{amount:.2f}",
            'VND': f"₫{amount:.0f}",
            'IDR': f"Rp{amount:.0f}",
            'PHP': f"₱{amount:.2f}",
            'TWD': f"NT${amount:.2f}",
            'HKD': f"HK${amount:.2f}",
            'KZT': f"₸{amount:.0f}",
            'UZS': f"лв{amount:.0f}",
            'SEK': f"{amount:.2f}kr",
            'NOK': f"{amount:.2f}kr",
            'DKK': f"{amount:.2f}kr",
            'PLN': f"{amount:.2f}zł",
            'CZK': f"{amount:.2f}Kč",
            'HUF': f"{amount:.0f}Ft",
            'RON': f"{amount:.2f}lei",
            'BGN': f"{amount:.2f}лв",
            'CHF': f"CHF{amount:.2f}",
            'RUB': f"₽{amount:.2f}",
            'TRY': f"₺{amount:.2f}",
            'UAH': f"₴{amount:.2f}"
        }
        
        return currency_formats.get(config.primary_currency, f"${amount:.2f}")
    
    def get_competitor_context(self, country_code: str) -> Dict[str, Any]:
        """Get comprehensive competitor analysis context for country"""
        config = self.get_country_config(country_code)
        if not config:
            config = self.COUNTRIES['US']
        
        return {
            'country': config.name,
            'currency': config.primary_currency,
            'currency_symbols': self.get_currency_symbols(country_code),
            'social_platforms': config.social_platforms,
            'review_sites': config.review_sites,
            'google_domain': config.google_domain,
            'business_context': config.business_context,
            'pricing_patterns': self.get_localized_pricing_patterns(country_code),
            'language_codes': config.language_codes,
            'timezone': config.timezone
        }

# Global instance
_country_localization = CountryLocalization()

# Module-level functions for backward compatibility
def get_available_countries():
    """Get list of available countries as (code, name) tuples"""
    return _country_localization.get_available_countries()

def get_competitor_context(country_code: str):
    """Get comprehensive competitor analysis context for country"""
    return _country_localization.get_competitor_context(country_code)

def get_google_search_domain(country_code: str):
    """Get Google search domain for country"""
    return _country_localization.get_google_search_domain(country_code)

def get_currency_symbols(country_code: str):
    """Get currency symbols to look for in pricing analysis"""
    return _country_localization.get_currency_symbols(country_code)

def get_social_platforms(country_code: str):
    """Get prioritized social media platforms for country"""
    return _country_localization.get_social_platforms(country_code)

def get_review_sites(country_code: str):
    """Get review sites relevant for country"""
    return _country_localization.get_review_sites(country_code)

def generate_search_queries(competitor_name: str, country_code: str):
    """Generate country-specific search queries for competitor analysis"""
    return _country_localization.generate_search_queries(competitor_name, country_code)

def get_localized_pricing_patterns(country_code: str):
    """Get country-specific pricing patterns to look for"""
    return _country_localization.get_localized_pricing_patterns(country_code)

def get_business_context(country_code: str):
    """Get business context for country"""
    return _country_localization.get_business_context(country_code)

def format_currency(amount: float, country_code: str):
    """Format currency amount for country"""
    return _country_localization.format_currency(amount, country_code)

def get_country_config(country_code: str):
    """Get country configuration"""
    return _country_localization.get_country_config(country_code)

# For backward compatibility, also create a module-level instance
country_localization = _country_localization 