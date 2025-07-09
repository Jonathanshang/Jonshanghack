"""
Monetization Analysis Module for Competitive Analysis Tool

This module provides comprehensive monetization strategy analysis including:
- Primary revenue streams identification and breakdown
- Customer lock-in strategy analysis
- Expansion revenue model assessment
- Revenue diversification analysis
- AI-powered monetization insights
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from utils.ai_analysis_engine import AIAnalysisEngine
from utils.master_prompt_designer import MasterPromptDesigner

class MonetizationAnalyzer:
    """
    Advanced monetization analysis engine that extracts and analyzes competitor 
    revenue models and monetization strategies using AI-powered analysis.
    """
    
    def __init__(self, api_key: str, model_name: str = "gpt-4", logger: Optional[logging.Logger] = None):
        """
        Initialize the monetization analyzer with AI capabilities.
        
        Args:
            api_key: OpenAI API key
            model_name: AI model to use for analysis
            logger: Logger instance for tracking operations
        """
        self.api_key = api_key
        self.model_name = model_name
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize AI components
        self.ai_engine = AIAnalysisEngine(api_key, model_name, logger)
        self.prompt_designer = MasterPromptDesigner()
        
        # Revenue stream indicators
        self.revenue_stream_patterns = {
            'subscription': [
                'monthly subscription', 'annual subscription', 'saas', 'recurring revenue',
                'monthly fee', 'annual fee', 'subscription model', 'per month', 'per year',
                'recurring charge', 'subscription plan', 'monthly plan', 'yearly plan'
            ],
            'transaction_fees': [
                'transaction fee', 'processing fee', 'payment processing', 'per transaction',
                'commission', 'percentage of sales', '% of revenue', 'transaction charge',
                'payment fee', 'processing charge', 'gateway fee', 'interchange fee'
            ],
            'hardware_sales': [
                'hardware cost', 'device purchase', 'terminal cost', 'equipment fee',
                'hardware sales', 'device sales', 'pos terminal', 'equipment purchase',
                'hardware lease', 'device lease', 'terminal lease', 'equipment rental'
            ],
            'setup_fees': [
                'setup fee', 'onboarding fee', 'implementation fee', 'installation fee',
                'activation fee', 'account setup', 'initial setup', 'configuration fee',
                'deployment fee', 'integration fee', 'migration fee', 'training fee'
            ],
            'support_fees': [
                'support fee', 'maintenance fee', 'premium support', 'technical support',
                'customer support', 'help desk', 'support plan', 'service fee',
                'maintenance plan', 'support subscription', 'priority support'
            ],
            'add_on_services': [
                'add-on', 'additional service', 'premium feature', 'optional service',
                'upgrade', 'enhancement', 'plugin', 'extension', 'module',
                'additional module', 'extra feature', 'premium add-on'
            ],
            'third_party_integrations': [
                'integration fee', 'api access', 'third-party', 'marketplace',
                'app store', 'partner fee', 'connector fee', 'sync fee',
                'integration service', 'custom integration', 'api fee'
            ]
        }
        
        # Lock-in strategy indicators
        self.lock_in_patterns = {
            'proprietary_hardware': [
                'proprietary', 'exclusive hardware', 'custom hardware', 'branded device',
                'locked device', 'exclusive terminal', 'proprietary terminal',
                'custom pos', 'branded pos', 'exclusive pos'
            ],
            'data_integration': [
                'data migration', 'data export', 'data portability', 'data lock-in',
                'integrated data', 'centralized data', 'data sync', 'unified data',
                'data warehouse', 'analytics platform', 'reporting system'
            ],
            'contract_terms': [
                'contract', 'agreement', 'commitment', 'term', 'cancellation fee',
                'early termination', 'minimum commitment', 'long-term agreement',
                'binding contract', 'service agreement', 'penalty fee'
            ],
            'ecosystem_integration': [
                'ecosystem', 'integrated platform', 'all-in-one', 'unified system',
                'seamless integration', 'connected services', 'platform approach',
                'comprehensive solution', 'end-to-end solution'
            ],
            'switching_costs': [
                'switching cost', 'migration cost', 'transition fee', 'change fee',
                'replacement cost', 'conversion cost', 'onboarding cost',
                'training cost', 'setup cost', 'implementation cost'
            ]
        }
        
        # Expansion revenue indicators
        self.expansion_patterns = {
            'tiered_pricing': [
                'tier', 'plan', 'package', 'level', 'edition', 'version',
                'starter', 'basic', 'standard', 'professional', 'enterprise',
                'premium', 'advanced', 'pro', 'business', 'growth'
            ],
            'usage_based': [
                'usage-based', 'pay-per-use', 'consumption-based', 'volume-based',
                'transaction-based', 'activity-based', 'per-transaction', 'per-user',
                'per-location', 'per-terminal', 'scalable pricing'
            ],
            'feature_gating': [
                'feature limitation', 'advanced feature', 'premium feature', 'pro feature',
                'enterprise feature', 'unlock feature', 'upgrade to access',
                'available in higher tier', 'premium functionality'
            ],
            'volume_discounts': [
                'volume discount', 'bulk pricing', 'enterprise pricing', 'quantity discount',
                'scale pricing', 'volume tier', 'bulk rate', 'enterprise rate',
                'high-volume pricing', 'quantity-based pricing'
            ],
            'upselling_opportunities': [
                'upsell', 'cross-sell', 'upgrade', 'add-on', 'enhancement',
                'additional service', 'premium service', 'advanced service',
                'professional service', 'consulting service', 'training service'
            ]
        }
    
    def analyze_competitor_monetization(
        self, 
        competitor_name: str,
        scraped_content: List[Dict[str, Any]],
        pricing_analysis: Optional[Dict[str, Any]] = None,
        country_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive monetization analysis on competitor data.
        
        Args:
            competitor_name: Name of the competitor being analyzed
            scraped_content: List of scraped page content
            pricing_analysis: Previous pricing analysis results
            country_context: Country-specific context for analysis
            
        Returns:
            Comprehensive monetization analysis results
        """
        self.logger.info(f"Starting monetization analysis for {competitor_name}")
        
        try:
            # Extract monetization data from content
            monetization_data = self._extract_monetization_data(scraped_content)
            
            # Analyze revenue streams
            revenue_streams = self._analyze_revenue_streams(monetization_data)
            
            # Analyze customer lock-in strategies
            lock_in_analysis = self._analyze_lock_in_strategies(monetization_data)
            
            # Analyze expansion revenue opportunities
            expansion_analysis = self._analyze_expansion_revenue(monetization_data)
            
            # Generate AI-powered monetization insights
            ai_insights = self._generate_monetization_insights(
                competitor_name, monetization_data, revenue_streams,
                lock_in_analysis, expansion_analysis, pricing_analysis, country_context
            )
            
            # Compile comprehensive analysis
            analysis_result = {
                'competitor': competitor_name,
                'analysis_date': datetime.now().isoformat(),
                'revenue_streams': revenue_streams,
                'lock_in_strategies': lock_in_analysis,
                'expansion_revenue': expansion_analysis,
                'monetization_insights': ai_insights.get('monetization_insights', {}),
                'competitive_positioning': ai_insights.get('competitive_positioning', {}),
                'recommendations': ai_insights.get('recommendations', []),
                'revenue_diversification': self._analyze_revenue_diversification(revenue_streams),
                'market_positioning': self._analyze_market_positioning(monetization_data),
                'confidence_scores': self._calculate_confidence_scores(monetization_data)
            }
            
            self.logger.info(f"Monetization analysis completed for {competitor_name}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error in monetization analysis: {str(e)}", exc_info=True)
            return self._generate_error_response(competitor_name, str(e))
    
    def _extract_monetization_data(self, scraped_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract monetization information from scraped content."""
        monetization_data = {
            'revenue_stream_mentions': {},
            'lock_in_mentions': {},
            'expansion_mentions': {},
            'monetization_pages': [],
            'pricing_context': [],
            'business_model_indicators': [],
            'revenue_keywords': []
        }
        
        # Initialize mention counters
        for stream_type in self.revenue_stream_patterns:
            monetization_data['revenue_stream_mentions'][stream_type] = []
        
        for lock_type in self.lock_in_patterns:
            monetization_data['lock_in_mentions'][lock_type] = []
        
        for expansion_type in self.expansion_patterns:
            monetization_data['expansion_mentions'][expansion_type] = []
        
        for page in scraped_content:
            if not page.get('content'):
                continue
                
            content = page['content'].lower()
            
            # Check if page is relevant for monetization analysis
            if self._is_monetization_relevant(content):
                monetization_data['monetization_pages'].append({
                    'url': page.get('url', ''),
                    'title': page.get('title', ''),
                    'category': page.get('category', 'unknown'),
                    'content_length': len(content)
                })
                
                # Extract revenue stream mentions
                self._extract_revenue_stream_mentions(content, monetization_data, page)
                
                # Extract lock-in strategy mentions
                self._extract_lock_in_mentions(content, monetization_data, page)
                
                # Extract expansion revenue mentions
                self._extract_expansion_mentions(content, monetization_data, page)
                
                # Extract business model indicators
                self._extract_business_model_indicators(content, monetization_data, page)
        
        return monetization_data
    
    def _is_monetization_relevant(self, content: str) -> bool:
        """Check if content is relevant for monetization analysis."""
        monetization_keywords = [
            'pricing', 'price', 'cost', 'fee', 'revenue', 'subscription',
            'plan', 'package', 'tier', 'business model', 'monetization',
            'payment', 'billing', 'transaction', 'commission', 'sales',
            'contract', 'agreement', 'service', 'platform', 'solution'
        ]
        
        return any(keyword in content for keyword in monetization_keywords)
    
    def _extract_revenue_stream_mentions(self, content: str, monetization_data: Dict[str, Any], page: Dict[str, Any]) -> None:
        """Extract revenue stream mentions from content."""
        for stream_type, patterns in self.revenue_stream_patterns.items():
            for pattern in patterns:
                if pattern in content:
                    context = self._extract_context(content, pattern)
                    monetization_data['revenue_stream_mentions'][stream_type].append({
                        'pattern': pattern,
                        'context': context,
                        'page_url': page.get('url', ''),
                        'page_title': page.get('title', ''),
                        'page_category': page.get('category', 'unknown')
                    })
    
    def _extract_lock_in_mentions(self, content: str, monetization_data: Dict[str, Any], page: Dict[str, Any]) -> None:
        """Extract lock-in strategy mentions from content."""
        for lock_type, patterns in self.lock_in_patterns.items():
            for pattern in patterns:
                if pattern in content:
                    context = self._extract_context(content, pattern)
                    monetization_data['lock_in_mentions'][lock_type].append({
                        'pattern': pattern,
                        'context': context,
                        'page_url': page.get('url', ''),
                        'page_title': page.get('title', ''),
                        'page_category': page.get('category', 'unknown')
                    })
    
    def _extract_expansion_mentions(self, content: str, monetization_data: Dict[str, Any], page: Dict[str, Any]) -> None:
        """Extract expansion revenue mentions from content."""
        for expansion_type, patterns in self.expansion_patterns.items():
            for pattern in patterns:
                if pattern in content:
                    context = self._extract_context(content, pattern)
                    monetization_data['expansion_mentions'][expansion_type].append({
                        'pattern': pattern,
                        'context': context,
                        'page_url': page.get('url', ''),
                        'page_title': page.get('title', ''),
                        'page_category': page.get('category', 'unknown')
                    })
    
    def _extract_business_model_indicators(self, content: str, monetization_data: Dict[str, Any], page: Dict[str, Any]) -> None:
        """Extract business model indicators from content."""
        business_model_keywords = [
            'saas', 'software as a service', 'platform', 'marketplace',
            'freemium', 'enterprise', 'b2b', 'b2c', 'self-service',
            'full-service', 'managed service', 'hybrid model',
            'subscription-based', 'transaction-based', 'usage-based'
        ]
        
        for keyword in business_model_keywords:
            if keyword in content:
                context = self._extract_context(content, keyword)
                monetization_data['business_model_indicators'].append({
                    'keyword': keyword,
                    'context': context,
                    'page_url': page.get('url', ''),
                    'page_title': page.get('title', ''),
                    'page_category': page.get('category', 'unknown')
                })
    
    def _extract_context(self, content: str, keyword: str) -> str:
        """Extract context around a keyword mention."""
        keyword_index = content.lower().find(keyword.lower())
        if keyword_index == -1:
            return ""
        
        # Get surrounding context (100 characters before and after)
        start = max(0, keyword_index - 100)
        end = min(len(content), keyword_index + len(keyword) + 100)
        
        return content[start:end].strip()
    
    def _analyze_revenue_streams(self, monetization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze revenue streams from extracted data."""
        revenue_streams = {
            'primary_streams': [],
            'secondary_streams': [],
            'stream_breakdown': {},
            'revenue_model_type': 'unknown',
            'confidence_score': 0.0
        }
        
        stream_mentions = monetization_data.get('revenue_stream_mentions', {})
        
        # Count mentions for each revenue stream
        stream_counts = {}
        for stream_type, mentions in stream_mentions.items():
            stream_counts[stream_type] = len(mentions)
        
        # Identify primary and secondary streams
        sorted_streams = sorted(stream_counts.items(), key=lambda x: x[1], reverse=True)
        
        for stream_type, count in sorted_streams:
            if count > 0:
                stream_info = {
                    'type': stream_type,
                    'mention_count': count,
                    'confidence': min(1.0, count * 0.2),
                    'evidence': stream_mentions[stream_type][:3]  # Top 3 pieces of evidence
                }
                
                if count >= 3:
                    revenue_streams['primary_streams'].append(stream_info)
                elif count >= 1:
                    revenue_streams['secondary_streams'].append(stream_info)
        
        # Determine revenue model type
        if stream_counts.get('subscription', 0) > 2:
            revenue_streams['revenue_model_type'] = 'subscription-based'
        elif stream_counts.get('transaction_fees', 0) > 2:
            revenue_streams['revenue_model_type'] = 'transaction-based'
        elif stream_counts.get('hardware_sales', 0) > 2:
            revenue_streams['revenue_model_type'] = 'product-based'
        elif len([s for s in stream_counts.values() if s > 0]) >= 3:
            revenue_streams['revenue_model_type'] = 'hybrid'
        
        # Calculate confidence score
        total_mentions = sum(stream_counts.values())
        revenue_streams['confidence_score'] = min(1.0, total_mentions * 0.1)
        
        # Stream breakdown
        revenue_streams['stream_breakdown'] = stream_counts
        
        return revenue_streams
    
    def _analyze_lock_in_strategies(self, monetization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer lock-in strategies from extracted data."""
        lock_in_analysis = {
            'lock_in_mechanisms': [],
            'switching_barriers': [],
            'lock_in_strength': 'low',  # low, medium, high
            'confidence_score': 0.0
        }
        
        lock_in_mentions = monetization_data.get('lock_in_mentions', {})
        
        # Count mentions for each lock-in mechanism
        lock_in_counts = {}
        for lock_type, mentions in lock_in_mentions.items():
            lock_in_counts[lock_type] = len(mentions)
        
        # Identify lock-in mechanisms
        sorted_mechanisms = sorted(lock_in_counts.items(), key=lambda x: x[1], reverse=True)
        
        for lock_type, count in sorted_mechanisms:
            if count > 0:
                mechanism_info = {
                    'type': lock_type,
                    'mention_count': count,
                    'strength': self._assess_lock_in_strength(lock_type, count),
                    'evidence': lock_in_mentions[lock_type][:2]  # Top 2 pieces of evidence
                }
                lock_in_analysis['lock_in_mechanisms'].append(mechanism_info)
        
        # Determine overall lock-in strength
        total_mentions = sum(lock_in_counts.values())
        high_strength_mechanisms = ['proprietary_hardware', 'data_integration', 'contract_terms']
        high_strength_count = sum(lock_in_counts.get(mechanism, 0) for mechanism in high_strength_mechanisms)
        
        if high_strength_count >= 5:
            lock_in_analysis['lock_in_strength'] = 'high'
        elif high_strength_count >= 2 or total_mentions >= 4:
            lock_in_analysis['lock_in_strength'] = 'medium'
        
        # Calculate confidence score
        lock_in_analysis['confidence_score'] = min(1.0, total_mentions * 0.15)
        
        return lock_in_analysis
    
    def _assess_lock_in_strength(self, lock_type: str, mention_count: int) -> str:
        """Assess the strength of a lock-in mechanism."""
        strength_mapping = {
            'proprietary_hardware': 'high',
            'data_integration': 'high',
            'contract_terms': 'high',
            'ecosystem_integration': 'medium',
            'switching_costs': 'medium'
        }
        
        base_strength = strength_mapping.get(lock_type, 'low')
        
        # Adjust based on mention count
        if mention_count >= 3:
            return 'high' if base_strength in ['medium', 'high'] else 'medium'
        elif mention_count >= 2:
            return base_strength
        else:
            return 'low' if base_strength == 'high' else base_strength
    
    def _analyze_expansion_revenue(self, monetization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze expansion revenue opportunities from extracted data."""
        expansion_analysis = {
            'expansion_mechanisms': [],
            'upselling_opportunities': [],
            'expansion_potential': 'low',  # low, medium, high
            'confidence_score': 0.0
        }
        
        expansion_mentions = monetization_data.get('expansion_mentions', {})
        
        # Count mentions for each expansion mechanism
        expansion_counts = {}
        for expansion_type, mentions in expansion_mentions.items():
            expansion_counts[expansion_type] = len(mentions)
        
        # Identify expansion mechanisms
        sorted_mechanisms = sorted(expansion_counts.items(), key=lambda x: x[1], reverse=True)
        
        for expansion_type, count in sorted_mechanisms:
            if count > 0:
                mechanism_info = {
                    'type': expansion_type,
                    'mention_count': count,
                    'potential': self._assess_expansion_potential(expansion_type, count),
                    'evidence': expansion_mentions[expansion_type][:2]  # Top 2 pieces of evidence
                }
                expansion_analysis['expansion_mechanisms'].append(mechanism_info)
        
        # Determine overall expansion potential
        total_mentions = sum(expansion_counts.values())
        high_potential_mechanisms = ['tiered_pricing', 'usage_based', 'upselling_opportunities']
        high_potential_count = sum(expansion_counts.get(mechanism, 0) for mechanism in high_potential_mechanisms)
        
        if high_potential_count >= 4:
            expansion_analysis['expansion_potential'] = 'high'
        elif high_potential_count >= 2 or total_mentions >= 3:
            expansion_analysis['expansion_potential'] = 'medium'
        
        # Calculate confidence score
        expansion_analysis['confidence_score'] = min(1.0, total_mentions * 0.2)
        
        return expansion_analysis
    
    def _assess_expansion_potential(self, expansion_type: str, mention_count: int) -> str:
        """Assess the potential of an expansion mechanism."""
        potential_mapping = {
            'tiered_pricing': 'high',
            'usage_based': 'high',
            'upselling_opportunities': 'high',
            'feature_gating': 'medium',
            'volume_discounts': 'medium'
        }
        
        base_potential = potential_mapping.get(expansion_type, 'low')
        
        # Adjust based on mention count
        if mention_count >= 3:
            return 'high' if base_potential in ['medium', 'high'] else 'medium'
        elif mention_count >= 2:
            return base_potential
        else:
            return 'low' if base_potential == 'high' else base_potential
    
    def _analyze_revenue_diversification(self, revenue_streams: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze revenue diversification strategy."""
        diversification = {
            'diversification_level': 'low',
            'stream_count': 0,
            'primary_dependency': 'unknown',
            'risk_assessment': 'medium'
        }
        
        primary_streams = revenue_streams.get('primary_streams', [])
        secondary_streams = revenue_streams.get('secondary_streams', [])
        
        total_streams = len(primary_streams) + len(secondary_streams)
        diversification['stream_count'] = total_streams
        
        if total_streams >= 4:
            diversification['diversification_level'] = 'high'
            diversification['risk_assessment'] = 'low'
        elif total_streams >= 2:
            diversification['diversification_level'] = 'medium'
            diversification['risk_assessment'] = 'medium'
        else:
            diversification['risk_assessment'] = 'high'
        
        # Identify primary dependency
        if primary_streams:
            top_stream = primary_streams[0]
            diversification['primary_dependency'] = top_stream['type']
        
        return diversification
    
    def _analyze_market_positioning(self, monetization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market positioning based on monetization strategy."""
        positioning = {
            'target_market': 'unknown',
            'positioning_strategy': 'unknown',
            'value_proposition': 'unknown',
            'competitive_approach': 'unknown'
        }
        
        business_indicators = monetization_data.get('business_model_indicators', [])
        
        # Analyze business model indicators
        indicator_counts = {}
        for indicator in business_indicators:
            keyword = indicator['keyword']
            indicator_counts[keyword] = indicator_counts.get(keyword, 0) + 1
        
        # Determine target market
        if indicator_counts.get('enterprise', 0) > 0:
            positioning['target_market'] = 'enterprise'
        elif indicator_counts.get('b2b', 0) > 0:
            positioning['target_market'] = 'small_to_medium_business'
        elif indicator_counts.get('self-service', 0) > 0:
            positioning['target_market'] = 'self_service'
        
        # Determine positioning strategy
        if indicator_counts.get('full-service', 0) > 0:
            positioning['positioning_strategy'] = 'full_service'
        elif indicator_counts.get('platform', 0) > 0:
            positioning['positioning_strategy'] = 'platform_approach'
        elif indicator_counts.get('saas', 0) > 0:
            positioning['positioning_strategy'] = 'saas_focused'
        
        return positioning
    
    def _generate_monetization_insights(
        self,
        competitor_name: str,
        monetization_data: Dict[str, Any],
        revenue_streams: Dict[str, Any],
        lock_in_analysis: Dict[str, Any],
        expansion_analysis: Dict[str, Any],
        pricing_analysis: Optional[Dict[str, Any]] = None,
        country_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate AI-powered monetization insights."""
        try:
            # Prepare context for AI analysis
            analysis_context = {
                'competitor_name': competitor_name,
                'revenue_streams': revenue_streams,
                'lock_in_strategies': lock_in_analysis,
                'expansion_revenue': expansion_analysis,
                'monetization_data_summary': {
                    'relevant_pages': len(monetization_data.get('monetization_pages', [])),
                    'total_revenue_mentions': sum(len(mentions) for mentions in monetization_data.get('revenue_stream_mentions', {}).values()),
                    'total_lock_in_mentions': sum(len(mentions) for mentions in monetization_data.get('lock_in_mentions', {}).values()),
                    'total_expansion_mentions': sum(len(mentions) for mentions in monetization_data.get('expansion_mentions', {}).values())
                },
                'pricing_analysis': pricing_analysis,
                'country_context': country_context or {}
            }
            
            # Get monetization analysis prompt
            monetization_prompt = self.prompt_designer.get_monetization_analysis_prompt(
                competitor_name, analysis_context
            )
            
            # Generate AI insights
            ai_response = self.ai_engine.analyze_with_prompt(
                prompt=monetization_prompt,
                context=analysis_context,
                analysis_type="monetization_strategy"
            )
            
            return ai_response
            
        except Exception as e:
            self.logger.error(f"Error generating AI monetization insights: {str(e)}")
            return {
                'monetization_insights': {'error': str(e)},
                'competitive_positioning': {'error': str(e)},
                'recommendations': ['Unable to generate AI insights due to error']
            }
    
    def _calculate_confidence_scores(self, monetization_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for different aspects of the analysis."""
        scores = {
            'overall_confidence': 0.0,
            'revenue_streams_confidence': 0.0,
            'lock_in_confidence': 0.0,
            'expansion_confidence': 0.0,
            'data_quality': 0.0
        }
        
        # Calculate based on data availability and quality
        total_mentions = (
            sum(len(mentions) for mentions in monetization_data.get('revenue_stream_mentions', {}).values()) +
            sum(len(mentions) for mentions in monetization_data.get('lock_in_mentions', {}).values()) +
            sum(len(mentions) for mentions in monetization_data.get('expansion_mentions', {}).values())
        )
        
        relevant_pages = len(monetization_data.get('monetization_pages', []))
        
        scores['data_quality'] = min(1.0, (total_mentions * 0.05) + (relevant_pages * 0.1))
        scores['overall_confidence'] = scores['data_quality']
        
        # Individual confidence scores
        scores['revenue_streams_confidence'] = min(1.0, 
            sum(len(mentions) for mentions in monetization_data.get('revenue_stream_mentions', {}).values()) * 0.1)
        scores['lock_in_confidence'] = min(1.0, 
            sum(len(mentions) for mentions in monetization_data.get('lock_in_mentions', {}).values()) * 0.15)
        scores['expansion_confidence'] = min(1.0, 
            sum(len(mentions) for mentions in monetization_data.get('expansion_mentions', {}).values()) * 0.2)
        
        return scores
    
    def _generate_error_response(self, competitor_name: str, error_message: str) -> Dict[str, Any]:
        """Generate error response for failed analysis."""
        return {
            'competitor': competitor_name,
            'analysis_date': datetime.now().isoformat(),
            'error': error_message,
            'status': 'failed',
            'revenue_streams': {'error': 'Analysis failed'},
            'lock_in_strategies': {'error': 'Analysis failed'},
            'expansion_revenue': {'error': 'Analysis failed'},
            'monetization_insights': {'error': 'Analysis failed'},
            'competitive_positioning': {'error': 'Analysis failed'},
            'recommendations': ['Unable to analyze due to error'],
            'confidence_scores': {'overall_confidence': 0.0}
        }
    
    def generate_monetization_report(self, analysis_result: Dict[str, Any]) -> str:
        """Generate a formatted monetization analysis report."""
        if analysis_result.get('error'):
            return f"Monetization analysis failed: {analysis_result['error']}"
        
        competitor = analysis_result.get('competitor', 'Unknown')
        
        report = f"""
# Monetization Analysis Report: {competitor}

## Executive Summary
- **Analysis Date**: {analysis_result.get('analysis_date', 'Unknown')}
- **Overall Confidence**: {analysis_result.get('confidence_scores', {}).get('overall_confidence', 0):.2f}

## Revenue Streams Analysis
- **Primary Revenue Model**: {analysis_result.get('revenue_streams', {}).get('revenue_model_type', 'Unknown')}
- **Primary Streams**: {len(analysis_result.get('revenue_streams', {}).get('primary_streams', []))}
- **Secondary Streams**: {len(analysis_result.get('revenue_streams', {}).get('secondary_streams', []))}

## Customer Lock-in Analysis
- **Lock-in Strength**: {analysis_result.get('lock_in_strategies', {}).get('lock_in_strength', 'Unknown')}
- **Lock-in Mechanisms**: {len(analysis_result.get('lock_in_strategies', {}).get('lock_in_mechanisms', []))}

## Expansion Revenue Analysis
- **Expansion Potential**: {analysis_result.get('expansion_revenue', {}).get('expansion_potential', 'Unknown')}
- **Expansion Mechanisms**: {len(analysis_result.get('expansion_revenue', {}).get('expansion_mechanisms', []))}

## AI-Generated Insights
{self._format_ai_insights(analysis_result.get('monetization_insights', {}))}

## Recommendations
{self._format_recommendations(analysis_result.get('recommendations', []))}
"""
        
        return report
    
    def _format_ai_insights(self, insights: Dict[str, Any]) -> str:
        """Format AI insights for the report."""
        if insights.get('error'):
            return f"AI insights unavailable: {insights['error']}"
        
        formatted = ""
        for key, value in insights.items():
            if isinstance(value, str):
                formatted += f"- **{key.replace('_', ' ').title()}**: {value}\n"
            elif isinstance(value, list):
                formatted += f"- **{key.replace('_', ' ').title()}**: {', '.join(value)}\n"
        
        return formatted
    
    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations for the report."""
        if not recommendations:
            return "No recommendations available."
        
        formatted = ""
        for i, rec in enumerate(recommendations, 1):
            formatted += f"{i}. {rec}\n"
        
        return formatted 