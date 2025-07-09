"""
Pricing Analysis Module for Competitive Analysis Tool

This module provides comprehensive pricing analysis functionality including:
- Hardware pricing breakdown (proprietary vs commodity)
- Software pricing tiers and billing models
- Hidden fees identification
- AI-powered pricing strategy analysis
- Comparative pricing insights
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from utils.ai_analysis_engine import AIAnalysisEngine
from utils.master_prompt_designer import MasterPromptDesigner

class PricingAnalyzer:
    """
    Advanced pricing analysis engine that extracts and analyzes competitor pricing
    strategies using AI-powered analysis and pattern recognition.
    """
    
    def __init__(self, api_key: str, model_name: str = "gpt-4", logger: Optional[logging.Logger] = None):
        """
        Initialize the pricing analyzer with AI capabilities.
        
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
        
        # Pricing pattern recognition
        self.currency_patterns = {
            'USD': r'\$[\d,]+(?:\.\d{2})?',
            'EUR': r'€[\d,]+(?:\.\d{2})?',
            'GBP': r'£[\d,]+(?:\.\d{2})?',
            'SGD': r'S\$[\d,]+(?:\.\d{2})?',
            'MYR': r'RM[\d,]+(?:\.\d{2})?',
            'general': r'[\$€£¥₹][\d,]+(?:\.\d{2})?|[\d,]+(?:\.\d{2})?\s*(?:USD|EUR|GBP|SGD|MYR|dollars?|euros?|pounds?)'
        }
        
        self.pricing_keywords = [
            'price', 'pricing', 'cost', 'fee', 'monthly', 'annual', 'yearly',
            'subscription', 'plan', 'tier', 'package', 'bundle', 'license',
            'per terminal', 'per location', 'per user', 'per employee',
            'transaction fee', 'processing fee', 'setup fee', 'implementation',
            'onboarding', 'support', 'maintenance', 'hardware', 'software'
        ]
        
        self.hidden_fee_indicators = [
            'additional', 'extra', 'plus', 'add-on', 'optional', 'premium',
            'implementation', 'setup', 'onboarding', 'training', 'support',
            'maintenance', 'transaction', 'processing', 'payment', 'gateway',
            'integration', 'customization', 'migration', 'data import'
        ]
    
    def analyze_competitor_pricing(
        self, 
        competitor_name: str,
        scraped_content: List[Dict[str, Any]],
        country_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive pricing analysis on competitor data.
        
        Args:
            competitor_name: Name of the competitor being analyzed
            scraped_content: List of scraped page content
            country_context: Country-specific context for pricing analysis
            
        Returns:
            Comprehensive pricing analysis results
        """
        self.logger.info(f"Starting pricing analysis for {competitor_name}")
        
        try:
            # Extract pricing data from content
            pricing_data = self._extract_pricing_data(scraped_content)
            
            # Identify hardware vs software pricing
            hardware_analysis = self._analyze_hardware_pricing(pricing_data)
            software_analysis = self._analyze_software_pricing(pricing_data)
            
            # Detect hidden fees
            hidden_fees = self._detect_hidden_fees(pricing_data)
            
            # Generate AI-powered pricing insights
            ai_insights = self._generate_pricing_insights(
                competitor_name, pricing_data, hardware_analysis, 
                software_analysis, hidden_fees, country_context
            )
            
            # Compile comprehensive analysis
            analysis_result = {
                'competitor': competitor_name,
                'analysis_date': datetime.now().isoformat(),
                'currency_detected': pricing_data.get('primary_currency', 'USD'),
                'hardware_pricing': hardware_analysis,
                'software_pricing': software_analysis,
                'hidden_fees': hidden_fees,
                'pricing_strategy': ai_insights.get('pricing_strategy', {}),
                'competitive_positioning': ai_insights.get('competitive_positioning', {}),
                'pricing_recommendations': ai_insights.get('recommendations', []),
                'cost_breakdown': self._generate_cost_breakdown(pricing_data),
                'pricing_patterns': self._identify_pricing_patterns(pricing_data),
                'confidence_scores': self._calculate_confidence_scores(pricing_data)
            }
            
            self.logger.info(f"Pricing analysis completed for {competitor_name}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error in pricing analysis: {str(e)}", exc_info=True)
            return self._generate_error_response(competitor_name, str(e))
    
    def _extract_pricing_data(self, scraped_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract pricing information from scraped content."""
        pricing_data = {
            'prices_found': [],
            'pricing_pages': [],
            'primary_currency': None,
            'billing_models': [],
            'pricing_tiers': [],
            'hardware_mentions': [],
            'software_mentions': [],
            'fee_mentions': []
        }
        
        for page in scraped_content:
            if not page.get('content'):
                continue
                
            content = page['content'].lower()
            
            # Skip if not a pricing-related page
            if not any(keyword in content for keyword in self.pricing_keywords):
                continue
                
            pricing_data['pricing_pages'].append({
                'url': page.get('url', ''),
                'title': page.get('title', ''),
                'category': page.get('category', 'unknown')
            })
            
            # Extract currency and prices
            self._extract_prices_from_content(content, pricing_data)
            
            # Extract pricing models and tiers
            self._extract_pricing_models(content, pricing_data)
            
            # Extract hardware/software mentions
            self._extract_hardware_software_mentions(content, pricing_data)
            
            # Extract fee mentions
            self._extract_fee_mentions(content, pricing_data)
        
        # Determine primary currency
        pricing_data['primary_currency'] = self._determine_primary_currency(pricing_data['prices_found'])
        
        return pricing_data
    
    def _extract_prices_from_content(self, content: str, pricing_data: Dict[str, Any]) -> None:
        """Extract price values from content."""
        for currency, pattern in self.currency_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                pricing_data['prices_found'].append({
                    'value': match,
                    'currency': currency,
                    'context': self._extract_price_context(content, match)
                })
    
    def _extract_price_context(self, content: str, price: str) -> str:
        """Extract context around a price mention."""
        price_index = content.lower().find(price.lower())
        if price_index == -1:
            return ""
        
        # Get surrounding context (50 characters before and after)
        start = max(0, price_index - 50)
        end = min(len(content), price_index + len(price) + 50)
        
        return content[start:end].strip()
    
    def _extract_pricing_models(self, content: str, pricing_data: Dict[str, Any]) -> None:
        """Extract pricing models and billing patterns."""
        billing_patterns = {
            'monthly': r'(?:per month|monthly|\/month|\/mo)',
            'annual': r'(?:per year|yearly|annually|\/year|\/yr)',
            'per_terminal': r'(?:per terminal|per device|per pos)',
            'per_location': r'(?:per location|per store|per site)',
            'per_user': r'(?:per user|per employee|per staff)',
            'percentage': r'(?:% of sales|percentage of revenue|transaction fee)',
            'one_time': r'(?:one-time|onetime|upfront|initial cost)'
        }
        
        for model, pattern in billing_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                pricing_data['billing_models'].append(model)
    
    def _extract_hardware_software_mentions(self, content: str, pricing_data: Dict[str, Any]) -> None:
        """Extract hardware and software pricing mentions."""
        hardware_keywords = [
            'terminal', 'ipad', 'tablet', 'hardware', 'device', 'pos system',
            'card reader', 'cash drawer', 'receipt printer', 'barcode scanner'
        ]
        
        software_keywords = [
            'software', 'app', 'application', 'subscription', 'saas',
            'license', 'plan', 'tier', 'package', 'feature'
        ]
        
        for keyword in hardware_keywords:
            if keyword in content:
                context = self._extract_keyword_context(content, keyword)
                pricing_data['hardware_mentions'].append({
                    'keyword': keyword,
                    'context': context
                })
        
        for keyword in software_keywords:
            if keyword in content:
                context = self._extract_keyword_context(content, keyword)
                pricing_data['software_mentions'].append({
                    'keyword': keyword,
                    'context': context
                })
    
    def _extract_keyword_context(self, content: str, keyword: str) -> str:
        """Extract context around a keyword mention."""
        keyword_index = content.lower().find(keyword.lower())
        if keyword_index == -1:
            return ""
        
        start = max(0, keyword_index - 30)
        end = min(len(content), keyword_index + len(keyword) + 30)
        
        return content[start:end].strip()
    
    def _extract_fee_mentions(self, content: str, pricing_data: Dict[str, Any]) -> None:
        """Extract mentions of additional fees."""
        for indicator in self.hidden_fee_indicators:
            if indicator in content:
                context = self._extract_keyword_context(content, indicator)
                pricing_data['fee_mentions'].append({
                    'type': indicator,
                    'context': context
                })
    
    def _determine_primary_currency(self, prices: List[Dict[str, Any]]) -> str:
        """Determine the primary currency used in pricing."""
        if not prices:
            return 'USD'
        
        currency_counts = {}
        for price in prices:
            currency = price['currency']
            currency_counts[currency] = currency_counts.get(currency, 0) + 1
        
        return max(currency_counts.items(), key=lambda x: x[1])[0] if currency_counts else 'USD'
    
    def _analyze_hardware_pricing(self, pricing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze hardware pricing strategy."""
        hardware_analysis = {
            'model_type': 'unknown',  # proprietary, commodity, mixed
            'cost_structure': 'unknown',  # one-time, lease, subscription
            'price_range': {'min': None, 'max': None},
            'hardware_strategy': '',
            'devices_mentioned': [],
            'confidence_score': 0.0
        }
        
        hardware_mentions = pricing_data.get('hardware_mentions', [])
        
        if hardware_mentions:
            # Analyze device types
            proprietary_indicators = ['proprietary', 'custom', 'branded', 'exclusive']
            commodity_indicators = ['ipad', 'tablet', 'android', 'standard']
            
            proprietary_count = sum(1 for mention in hardware_mentions 
                                  if any(indicator in mention['context'].lower() 
                                        for indicator in proprietary_indicators))
            
            commodity_count = sum(1 for mention in hardware_mentions 
                                if any(indicator in mention['context'].lower() 
                                      for indicator in commodity_indicators))
            
            if proprietary_count > commodity_count:
                hardware_analysis['model_type'] = 'proprietary'
            elif commodity_count > proprietary_count:
                hardware_analysis['model_type'] = 'commodity'
            elif proprietary_count > 0 and commodity_count > 0:
                hardware_analysis['model_type'] = 'mixed'
            
            hardware_analysis['confidence_score'] = min(1.0, len(hardware_mentions) * 0.2)
            hardware_analysis['devices_mentioned'] = [m['keyword'] for m in hardware_mentions]
        
        return hardware_analysis
    
    def _analyze_software_pricing(self, pricing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze software pricing strategy."""
        software_analysis = {
            'pricing_model': 'unknown',  # subscription, one-time, freemium, tiered
            'billing_frequency': 'unknown',  # monthly, annual, per-transaction
            'billing_axis': 'unknown',  # per-user, per-location, per-terminal, percentage
            'tier_count': 0,
            'features_by_tier': {},
            'price_progression': [],
            'confidence_score': 0.0
        }
        
        billing_models = pricing_data.get('billing_models', [])
        software_mentions = pricing_data.get('software_mentions', [])
        
        if billing_models:
            # Determine billing frequency
            if 'monthly' in billing_models:
                software_analysis['billing_frequency'] = 'monthly'
            elif 'annual' in billing_models:
                software_analysis['billing_frequency'] = 'annual'
            
            # Determine billing axis
            if 'per_terminal' in billing_models:
                software_analysis['billing_axis'] = 'per-terminal'
            elif 'per_location' in billing_models:
                software_analysis['billing_axis'] = 'per-location'
            elif 'per_user' in billing_models:
                software_analysis['billing_axis'] = 'per-user'
            elif 'percentage' in billing_models:
                software_analysis['billing_axis'] = 'percentage-of-sales'
            
            # Determine pricing model
            if any(model in ['monthly', 'annual'] for model in billing_models):
                software_analysis['pricing_model'] = 'subscription'
            elif 'one_time' in billing_models:
                software_analysis['pricing_model'] = 'one-time'
            
            software_analysis['confidence_score'] = min(1.0, len(billing_models) * 0.3)
        
        return software_analysis
    
    def _detect_hidden_fees(self, pricing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect potential hidden fees."""
        hidden_fees = {
            'fees_detected': [],
            'categories': {
                'setup': [],
                'transaction': [],
                'support': [],
                'integration': [],
                'training': []
            },
            'risk_level': 'low',  # low, medium, high
            'confidence_score': 0.0
        }
        
        fee_mentions = pricing_data.get('fee_mentions', [])
        
        fee_categorization = {
            'setup': ['setup', 'implementation', 'onboarding', 'installation'],
            'transaction': ['transaction', 'processing', 'payment', 'gateway'],
            'support': ['support', 'maintenance', 'premium'],
            'integration': ['integration', 'customization', 'migration'],
            'training': ['training', 'education', 'consultation']
        }
        
        for mention in fee_mentions:
            fee_type = mention['type']
            context = mention['context']
            
            # Categorize the fee
            for category, keywords in fee_categorization.items():
                if any(keyword in fee_type or keyword in context.lower() for keyword in keywords):
                    hidden_fees['categories'][category].append({
                        'type': fee_type,
                        'context': context
                    })
                    break
            
            hidden_fees['fees_detected'].append(mention)
        
        # Determine risk level
        total_fees = len(hidden_fees['fees_detected'])
        if total_fees >= 5:
            hidden_fees['risk_level'] = 'high'
        elif total_fees >= 2:
            hidden_fees['risk_level'] = 'medium'
        
        hidden_fees['confidence_score'] = min(1.0, total_fees * 0.2)
        
        return hidden_fees
    
    def _generate_pricing_insights(
        self,
        competitor_name: str,
        pricing_data: Dict[str, Any],
        hardware_analysis: Dict[str, Any],
        software_analysis: Dict[str, Any],
        hidden_fees: Dict[str, Any],
        country_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate AI-powered pricing insights."""
        try:
            # Prepare context for AI analysis
            analysis_context = {
                'competitor_name': competitor_name,
                'pricing_data_summary': {
                    'total_prices_found': len(pricing_data.get('prices_found', [])),
                    'primary_currency': pricing_data.get('primary_currency'),
                    'billing_models': pricing_data.get('billing_models', []),
                    'pricing_pages_count': len(pricing_data.get('pricing_pages', []))
                },
                'hardware_analysis': hardware_analysis,
                'software_analysis': software_analysis,
                'hidden_fees_summary': {
                    'total_fees': len(hidden_fees.get('fees_detected', [])),
                    'risk_level': hidden_fees.get('risk_level'),
                    'fee_categories': list(hidden_fees.get('categories', {}).keys())
                },
                'country_context': country_context or {}
            }
            
            # Get pricing analysis prompt
            pricing_prompt = self.prompt_designer.get_pricing_analysis_prompt(
                competitor_name, analysis_context
            )
            
            # Generate AI insights
            ai_response = self.ai_engine.analyze_with_prompt(
                prompt=pricing_prompt,
                context=analysis_context,
                analysis_type="pricing_strategy"
            )
            
            return ai_response
            
        except Exception as e:
            self.logger.error(f"Error generating AI pricing insights: {str(e)}")
            return {
                'pricing_strategy': {'error': str(e)},
                'competitive_positioning': {'error': str(e)},
                'recommendations': ['Unable to generate AI insights due to error']
            }
    
    def _generate_cost_breakdown(self, pricing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cost breakdown analysis."""
        cost_breakdown = {
            'total_cost_of_ownership': 'unknown',
            'upfront_costs': [],
            'recurring_costs': [],
            'variable_costs': [],
            'cost_comparison': {}
        }
        
        prices = pricing_data.get('prices_found', [])
        billing_models = pricing_data.get('billing_models', [])
        
        for price in prices:
            context = price.get('context', '').lower()
            
            if any(model in billing_models for model in ['one_time']):
                cost_breakdown['upfront_costs'].append(price)
            elif any(model in billing_models for model in ['monthly', 'annual']):
                cost_breakdown['recurring_costs'].append(price)
            elif 'percentage' in billing_models:
                cost_breakdown['variable_costs'].append(price)
        
        return cost_breakdown
    
    def _identify_pricing_patterns(self, pricing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify pricing patterns and strategies."""
        patterns = {
            'pricing_strategy_type': 'unknown',
            'value_proposition': 'unknown',
            'target_market': 'unknown',
            'competitive_approach': 'unknown'
        }
        
        # Analyze based on available data
        if pricing_data.get('billing_models'):
            if 'percentage' in pricing_data['billing_models']:
                patterns['pricing_strategy_type'] = 'revenue_share'
            elif any(model in pricing_data['billing_models'] for model in ['monthly', 'annual']):
                patterns['pricing_strategy_type'] = 'subscription'
            elif 'one_time' in pricing_data['billing_models']:
                patterns['pricing_strategy_type'] = 'one_time_purchase'
        
        return patterns
    
    def _calculate_confidence_scores(self, pricing_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for different aspects of the analysis."""
        scores = {
            'overall_confidence': 0.0,
            'pricing_data_quality': 0.0,
            'hardware_analysis_confidence': 0.0,
            'software_analysis_confidence': 0.0,
            'hidden_fees_confidence': 0.0
        }
        
        # Calculate based on data availability and quality
        total_data_points = (
            len(pricing_data.get('prices_found', [])) +
            len(pricing_data.get('billing_models', [])) +
            len(pricing_data.get('hardware_mentions', [])) +
            len(pricing_data.get('software_mentions', [])) +
            len(pricing_data.get('fee_mentions', []))
        )
        
        scores['pricing_data_quality'] = min(1.0, total_data_points * 0.1)
        scores['overall_confidence'] = scores['pricing_data_quality']
        
        return scores
    
    def _generate_error_response(self, competitor_name: str, error_message: str) -> Dict[str, Any]:
        """Generate error response for failed analysis."""
        return {
            'competitor': competitor_name,
            'analysis_date': datetime.now().isoformat(),
            'error': error_message,
            'status': 'failed',
            'hardware_pricing': {'error': 'Analysis failed'},
            'software_pricing': {'error': 'Analysis failed'},
            'hidden_fees': {'error': 'Analysis failed'},
            'pricing_strategy': {'error': 'Analysis failed'},
            'competitive_positioning': {'error': 'Analysis failed'},
            'pricing_recommendations': ['Unable to analyze due to error'],
            'confidence_scores': {'overall_confidence': 0.0}
        }
    
    def generate_pricing_report(self, analysis_result: Dict[str, Any]) -> str:
        """Generate a formatted pricing analysis report."""
        if analysis_result.get('error'):
            return f"Pricing analysis failed: {analysis_result['error']}"
        
        competitor = analysis_result.get('competitor', 'Unknown')
        
        report = f"""
# Pricing Analysis Report: {competitor}

## Executive Summary
- **Analysis Date**: {analysis_result.get('analysis_date', 'Unknown')}
- **Primary Currency**: {analysis_result.get('currency_detected', 'Unknown')}
- **Overall Confidence**: {analysis_result.get('confidence_scores', {}).get('overall_confidence', 0):.2f}

## Hardware Pricing Analysis
- **Model Type**: {analysis_result.get('hardware_pricing', {}).get('model_type', 'Unknown')}
- **Cost Structure**: {analysis_result.get('hardware_pricing', {}).get('cost_structure', 'Unknown')}
- **Devices Mentioned**: {', '.join(analysis_result.get('hardware_pricing', {}).get('devices_mentioned', []))}

## Software Pricing Analysis
- **Pricing Model**: {analysis_result.get('software_pricing', {}).get('pricing_model', 'Unknown')}
- **Billing Frequency**: {analysis_result.get('software_pricing', {}).get('billing_frequency', 'Unknown')}
- **Billing Axis**: {analysis_result.get('software_pricing', {}).get('billing_axis', 'Unknown')}

## Hidden Fees Analysis
- **Risk Level**: {analysis_result.get('hidden_fees', {}).get('risk_level', 'Unknown')}
- **Fees Detected**: {len(analysis_result.get('hidden_fees', {}).get('fees_detected', []))}

## AI-Generated Insights
{self._format_ai_insights(analysis_result.get('pricing_strategy', {}))}

## Recommendations
{self._format_recommendations(analysis_result.get('pricing_recommendations', []))}
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