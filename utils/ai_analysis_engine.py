"""
AI Analysis Engine for Competitive Intelligence

This module provides comprehensive AI-powered competitive analysis using the master prompt system
and OpenAI GPT-4 for pricing, monetization, vision, and positioning analysis.
"""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

from .master_prompt_designer import MasterPromptDesigner, AnalysisContext

@dataclass
class AnalysisResult:
    """Result of an AI analysis"""
    analysis_type: str
    competitor_name: str
    analysis_date: str
    content: str
    confidence: float
    processing_time: float
    tokens_used: int
    cost_estimate: float
    key_insights: List[str]
    recommendations: List[str]
    raw_response: str

class AIAnalysisEngine:
    """
    AI-powered competitive analysis engine using OpenAI GPT-4
    
    Provides comprehensive analysis capabilities:
    - Pricing analysis with cost breakdown
    - Monetization strategy assessment
    - Vision and roadmap inference
    - Competitive positioning analysis
    - Sales battlecard generation
    - Marketing strategy recommendations
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4", logger: Optional[logging.Logger] = None):
        """
        Initialize the AI analysis engine
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4)
            logger: Optional logger instance
        """
        self.api_key = api_key
        self.model = model
        self.logger = logger or logging.getLogger(__name__)
        
        # Store API key for client initialization
        # Client will be initialized per request
        
        # Initialize master prompt designer
        self.prompt_designer = MasterPromptDesigner(logger=self.logger)
        
        # Rate limiting settings
        self.last_request_time = 0
        self.min_request_interval = 2.0  # 2 seconds between requests
        
        # Token and cost tracking
        self.token_costs = {
            "gpt-4": {"input": 0.03, "output": 0.06},  # Per 1K tokens
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4o": {"input": 0.005, "output": 0.015}
        }
        
        # Analysis cache
        self.analysis_cache = {}
        
    def _rate_limit(self):
        """Implement rate limiting for API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost for API usage"""
        if self.model in self.token_costs:
            costs = self.token_costs[self.model]
            input_cost = (input_tokens / 1000) * costs["input"]
            output_cost = (output_tokens / 1000) * costs["output"]
            return input_cost + output_cost
        return 0.0
    
    def _extract_key_insights(self, analysis_content: str) -> List[str]:
        """Extract key insights from analysis content"""
        insights = []
        
        # Look for bullet points and numbered lists
        lines = analysis_content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('• ') or line.startswith('- '):
                insights.append(line[2:].strip())
            elif line and line[0].isdigit() and line[1:3] == '. ':
                insights.append(line[3:].strip())
        
        # Return top 10 insights
        return insights[:10]
    
    def _extract_recommendations(self, analysis_content: str) -> List[str]:
        """Extract recommendations from analysis content"""
        recommendations = []
        
        # Look for recommendation sections
        lines = analysis_content.split('\n')
        in_recommendation_section = False
        
        for line in lines:
            line = line.strip()
            
            # Check if we're entering a recommendation section
            if 'recommendation' in line.lower() or 'action' in line.lower():
                in_recommendation_section = True
                continue
            
            # Extract recommendations
            if in_recommendation_section:
                if line.startswith('• ') or line.startswith('- '):
                    recommendations.append(line[2:].strip())
                elif line and line[0].isdigit() and line[1:3] == '. ':
                    recommendations.append(line[3:].strip())
                elif line and not line.startswith(' '):
                    # Stop if we hit a new section
                    in_recommendation_section = False
        
        return recommendations[:10]
    
    def _make_openai_request(self, prompt: str, max_tokens: int = 4000) -> Dict[str, Any]:
        """Make a request to OpenAI API with error handling"""
        try:
            self._rate_limit()
            
            start_time = time.time()
            
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior business analyst and competitive intelligence expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            processing_time = time.time() - start_time
            
            # Extract usage information
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0
            
            # Calculate cost
            cost = self._calculate_cost(input_tokens, output_tokens)
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'processing_time': processing_time,
                'tokens_used': total_tokens,
                'cost_estimate': cost,
                'raw_response': response.model_dump() if hasattr(response, 'model_dump') else str(response)
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI API request failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'content': None,
                'processing_time': 0,
                'tokens_used': 0,
                'cost_estimate': 0.0,
                'raw_response': None
            }
    
    def analyze_pricing(self, context: AnalysisContext) -> AnalysisResult:
        """Perform comprehensive pricing analysis"""
        self.logger.info(f"Starting pricing analysis for {context.competitor_name}")
        
        # Generate pricing analysis prompt
        prompt = self.prompt_designer.create_pricing_analysis_prompt(context)
        
        # Make API request
        response = self._make_openai_request(prompt, max_tokens=4000)
        
        if not response['success']:
            raise Exception(f"Pricing analysis failed: {response['error']}")
        
        # Extract insights and recommendations
        content = response['content']
        key_insights = self._extract_key_insights(content)
        recommendations = self._extract_recommendations(content)
        
        # Create analysis result
        result = AnalysisResult(
            analysis_type="pricing",
            competitor_name=context.competitor_name,
            analysis_date=datetime.now().isoformat(),
            content=content,
            confidence=0.85,  # High confidence for pricing analysis
            processing_time=response['processing_time'],
            tokens_used=response['tokens_used'],
            cost_estimate=response['cost_estimate'],
            key_insights=key_insights,
            recommendations=recommendations,
            raw_response=json.dumps(response['raw_response'], default=str)
        )
        
        self.logger.info(f"Pricing analysis completed for {context.competitor_name}")
        return result
    
    def analyze_monetization(self, context: AnalysisContext) -> AnalysisResult:
        """Perform monetization strategy analysis"""
        self.logger.info(f"Starting monetization analysis for {context.competitor_name}")
        
        # Generate monetization analysis prompt
        prompt = self.prompt_designer.create_monetization_strategy_prompt(context)
        
        # Make API request
        response = self._make_openai_request(prompt, max_tokens=4000)
        
        if not response['success']:
            raise Exception(f"Monetization analysis failed: {response['error']}")
        
        # Extract insights and recommendations
        content = response['content']
        key_insights = self._extract_key_insights(content)
        recommendations = self._extract_recommendations(content)
        
        # Create analysis result
        result = AnalysisResult(
            analysis_type="monetization",
            competitor_name=context.competitor_name,
            analysis_date=datetime.now().isoformat(),
            content=content,
            confidence=0.80,  # Good confidence for monetization analysis
            processing_time=response['processing_time'],
            tokens_used=response['tokens_used'],
            cost_estimate=response['cost_estimate'],
            key_insights=key_insights,
            recommendations=recommendations,
            raw_response=json.dumps(response['raw_response'], default=str)
        )
        
        self.logger.info(f"Monetization analysis completed for {context.competitor_name}")
        return result
    
    def analyze_vision_roadmap(self, context: AnalysisContext) -> AnalysisResult:
        """Perform vision and roadmap inference"""
        self.logger.info(f"Starting vision analysis for {context.competitor_name}")
        
        # Generate vision analysis prompt
        prompt = self.prompt_designer.create_vision_roadmap_prompt(context)
        
        # Make API request
        response = self._make_openai_request(prompt, max_tokens=4000)
        
        if not response['success']:
            raise Exception(f"Vision analysis failed: {response['error']}")
        
        # Extract insights and recommendations
        content = response['content']
        key_insights = self._extract_key_insights(content)
        recommendations = self._extract_recommendations(content)
        
        # Create analysis result
        result = AnalysisResult(
            analysis_type="vision",
            competitor_name=context.competitor_name,
            analysis_date=datetime.now().isoformat(),
            content=content,
            confidence=0.70,  # Moderate confidence for vision inference
            processing_time=response['processing_time'],
            tokens_used=response['tokens_used'],
            cost_estimate=response['cost_estimate'],
            key_insights=key_insights,
            recommendations=recommendations,
            raw_response=json.dumps(response['raw_response'], default=str)
        )
        
        self.logger.info(f"Vision analysis completed for {context.competitor_name}")
        return result
    
    def analyze_competitive_positioning(self, context: AnalysisContext) -> AnalysisResult:
        """Perform competitive positioning analysis"""
        self.logger.info(f"Starting positioning analysis for {context.competitor_name}")
        
        # Generate positioning analysis prompt
        prompt = self.prompt_designer.create_competitive_positioning_prompt(context)
        
        # Make API request
        response = self._make_openai_request(prompt, max_tokens=4000)
        
        if not response['success']:
            raise Exception(f"Positioning analysis failed: {response['error']}")
        
        # Extract insights and recommendations
        content = response['content']
        key_insights = self._extract_key_insights(content)
        recommendations = self._extract_recommendations(content)
        
        # Create analysis result
        result = AnalysisResult(
            analysis_type="positioning",
            competitor_name=context.competitor_name,
            analysis_date=datetime.now().isoformat(),
            content=content,
            confidence=0.85,  # High confidence for positioning analysis
            processing_time=response['processing_time'],
            tokens_used=response['tokens_used'],
            cost_estimate=response['cost_estimate'],
            key_insights=key_insights,
            recommendations=recommendations,
            raw_response=json.dumps(response['raw_response'], default=str)
        )
        
        self.logger.info(f"Positioning analysis completed for {context.competitor_name}")
        return result
    
    def generate_battlecard(self, context: AnalysisContext) -> AnalysisResult:
        """Generate sales battlecard"""
        self.logger.info(f"Starting battlecard generation for {context.competitor_name}")
        
        # Generate battlecard prompt
        prompt = self.prompt_designer.create_battlecard_generation_prompt(context)
        
        # Make API request
        response = self._make_openai_request(prompt, max_tokens=4000)
        
        if not response['success']:
            raise Exception(f"Battlecard generation failed: {response['error']}")
        
        # Extract insights and recommendations
        content = response['content']
        key_insights = self._extract_key_insights(content)
        recommendations = self._extract_recommendations(content)
        
        # Create analysis result
        result = AnalysisResult(
            analysis_type="battlecard",
            competitor_name=context.competitor_name,
            analysis_date=datetime.now().isoformat(),
            content=content,
            confidence=0.90,  # High confidence for battlecard
            processing_time=response['processing_time'],
            tokens_used=response['tokens_used'],
            cost_estimate=response['cost_estimate'],
            key_insights=key_insights,
            recommendations=recommendations,
            raw_response=json.dumps(response['raw_response'], default=str)
        )
        
        self.logger.info(f"Battlecard generation completed for {context.competitor_name}")
        return result
    
    def generate_marketing_strategy(self, context: AnalysisContext) -> AnalysisResult:
        """Generate marketing strategy recommendations"""
        self.logger.info(f"Starting marketing strategy for {context.competitor_name}")
        
        # Generate marketing strategy prompt
        prompt = self.prompt_designer.create_marketing_strategy_prompt(context)
        
        # Make API request
        response = self._make_openai_request(prompt, max_tokens=4000)
        
        if not response['success']:
            raise Exception(f"Marketing strategy failed: {response['error']}")
        
        # Extract insights and recommendations
        content = response['content']
        key_insights = self._extract_key_insights(content)
        recommendations = self._extract_recommendations(content)
        
        # Create analysis result
        result = AnalysisResult(
            analysis_type="marketing",
            competitor_name=context.competitor_name,
            analysis_date=datetime.now().isoformat(),
            content=content,
            confidence=0.85,  # High confidence for marketing strategy
            processing_time=response['processing_time'],
            tokens_used=response['tokens_used'],
            cost_estimate=response['cost_estimate'],
            key_insights=key_insights,
            recommendations=recommendations,
            raw_response=json.dumps(response['raw_response'], default=str)
        )
        
        self.logger.info(f"Marketing strategy completed for {context.competitor_name}")
        return result
    
    def perform_comprehensive_analysis(self, context: AnalysisContext) -> Dict[str, AnalysisResult]:
        """Perform comprehensive analysis covering all aspects"""
        self.logger.info(f"Starting comprehensive analysis for {context.competitor_name}")
        
        results = {}
        
        # Define analysis types to perform
        analysis_types = [
            ('pricing', self.analyze_pricing),
            ('monetization', self.analyze_monetization),
            ('vision', self.analyze_vision_roadmap),
            ('positioning', self.analyze_competitive_positioning),
            ('battlecard', self.generate_battlecard),
            ('marketing', self.generate_marketing_strategy)
        ]
        
        # Perform each analysis
        for analysis_type, analysis_method in analysis_types:
            try:
                self.logger.info(f"Performing {analysis_type} analysis...")
                result = analysis_method(context)
                results[analysis_type] = result
                
                # Add delay between analyses to respect rate limits
                time.sleep(3)
                
            except Exception as e:
                self.logger.error(f"Failed to perform {analysis_type} analysis: {str(e)}")
                # Continue with other analyses
                continue
        
        self.logger.info(f"Comprehensive analysis completed for {context.competitor_name}")
        return results
    
    def get_analysis_summary(self, results: Dict[str, AnalysisResult]) -> Dict[str, Any]:
        """Generate summary of analysis results"""
        if not results:
            return {"error": "No analysis results available"}
        
        total_cost = sum(result.cost_estimate for result in results.values())
        total_tokens = sum(result.tokens_used for result in results.values())
        total_time = sum(result.processing_time for result in results.values())
        
        # Collect all insights and recommendations
        all_insights = []
        all_recommendations = []
        
        for result in results.values():
            all_insights.extend(result.key_insights)
            all_recommendations.extend(result.recommendations)
        
        # Get top insights and recommendations
        top_insights = list(set(all_insights))[:15]
        top_recommendations = list(set(all_recommendations))[:15]
        
        return {
            "analyses_completed": len(results),
            "total_cost_estimate": total_cost,
            "total_tokens_used": total_tokens,
            "total_processing_time": total_time,
            "top_insights": top_insights,
            "top_recommendations": top_recommendations,
            "analysis_types": list(results.keys()),
            "average_confidence": sum(result.confidence for result in results.values()) / len(results)
        }
    
    def export_analysis_results(self, results: Dict[str, AnalysisResult], format: str = "json") -> Any:
        """Export analysis results in specified format"""
        if format == "json":
            return {
                analysis_type: asdict(result) for analysis_type, result in results.items()
            }
        elif format == "summary":
            return self.get_analysis_summary(results)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_available_analyses(self) -> List[str]:
        """Get list of available analysis types"""
        return [
            "pricing",
            "monetization", 
            "vision",
            "positioning",
            "battlecard",
            "marketing",
            "comprehensive"
        ] 