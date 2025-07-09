import json
import re
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import logging
from datetime import datetime

@dataclass
class CategorizedComplaint:
    """Represents a categorized complaint with detailed analysis"""
    original_text: str
    source: str
    url: str
    category: str
    subcategory: str
    severity: str
    confidence: float
    keywords: List[str]
    summary: str
    actionable_insight: str
    timestamp: datetime
    platform: str

@dataclass
class CategoryAnalysis:
    """Analysis results for a specific complaint category"""
    category: str
    total_complaints: int
    severity_distribution: Dict[str, int]
    common_keywords: List[Tuple[str, int]]
    top_complaints: List[CategorizedComplaint]
    actionable_insights: List[str]
    trend_analysis: str
    recommendations: List[str]

class ComplaintCategorizer:
    """
    AI-powered complaint categorization system using OpenAI GPT-4
    
    Categorizes complaints into:
    - Product Gaps: Missing features, functionality limitations
    - Service & Support: Customer service issues, response times
    - Billing & Contract: Pricing, hidden fees, contract problems
    - Performance Issues: Speed, reliability, downtime problems
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4", logger: Optional[logging.Logger] = None):
        """
        Initialize the complaint categorizer
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
            logger: Optional logger instance
        """
        self.api_key = api_key
        self.model = model
        self.logger = logger or logging.getLogger(__name__)
        
        # Store API key for client initialization
        # Client will be initialized per request
        
        # Define categories and their characteristics
        self.categories = {
            "Product Gaps": {
                "description": "Missing features, functionality limitations, integration issues",
                "keywords": [
                    "missing feature", "doesn't support", "can't do", "limitation", "lacks",
                    "need feature", "would like", "wish it had", "integration", "compatibility",
                    "functionality", "capability", "feature request", "enhancement"
                ],
                "subcategories": [
                    "Missing Core Features",
                    "Integration Issues", 
                    "Functionality Limitations",
                    "Compatibility Problems",
                    "User Experience Gaps"
                ]
            },
            "Service & Support": {
                "description": "Customer service issues, response times, help quality",
                "keywords": [
                    "support", "customer service", "help", "response time", "slow support",
                    "poor service", "unhelpful", "rude", "unprofessional", "waited",
                    "no response", "ignored", "ticket", "chat", "phone support"
                ],
                "subcategories": [
                    "Poor Response Times",
                    "Unhelpful Support Staff",
                    "Lack of Documentation",
                    "Training Issues",
                    "Communication Problems"
                ]
            },
            "Billing & Contract": {
                "description": "Pricing issues, hidden fees, contract problems, billing errors",
                "keywords": [
                    "price", "cost", "expensive", "hidden fee", "billing", "charge",
                    "overcharged", "contract", "cancellation", "refund", "payment",
                    "subscription", "plan", "tier", "upgrade", "downgrade"
                ],
                "subcategories": [
                    "Hidden Fees",
                    "Billing Errors",
                    "Contract Issues",
                    "Pricing Transparency",
                    "Cancellation Problems"
                ]
            },
            "Performance Issues": {
                "description": "Speed, reliability, downtime, system performance problems",
                "keywords": [
                    "slow", "lag", "down", "outage", "crash", "freeze", "hang",
                    "performance", "speed", "loading", "timeout", "error", "bug",
                    "glitch", "unstable", "unreliable", "broken"
                ],
                "subcategories": [
                    "System Downtime",
                    "Slow Performance",
                    "Bugs and Glitches",
                    "Reliability Issues",
                    "Loading Problems"
                ]
            }
        }
        
        # Severity levels
        self.severity_levels = ["Low", "Medium", "High", "Critical"]
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
        
    def _rate_limit(self):
        """Implement rate limiting for API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _create_categorization_prompt(self, complaint_text: str, competitor_name: str) -> str:
        """Create the prompt for OpenAI GPT-4 categorization"""
        
        categories_desc = "\n".join([
            f"- {cat}: {info['description']}"
            for cat, info in self.categories.items()
        ])
        
        prompt = f"""
You are an expert business analyst specializing in competitive intelligence and customer feedback analysis. 
Your task is to analyze a customer complaint about {competitor_name} and categorize it systematically.

COMPLAINT TEXT:
"{complaint_text}"

CATEGORIZATION FRAMEWORK:
{categories_desc}

ANALYSIS REQUIREMENTS:
1. PRIMARY CATEGORY: Choose the most appropriate category from the 4 options above
2. SUBCATEGORY: Identify the specific subcategory within the primary category
3. SEVERITY: Rate as Low, Medium, High, or Critical based on business impact
4. CONFIDENCE: Rate your confidence in the categorization (0.0-1.0)
5. KEYWORDS: Extract 3-5 key terms that led to this categorization
6. SUMMARY: Provide a concise 1-2 sentence summary of the complaint
7. ACTIONABLE INSIGHT: Suggest how {competitor_name}'s competitor (StoreHub) could address this pain point

RESPONSE FORMAT (JSON):
{{
    "category": "Primary Category",
    "subcategory": "Specific Subcategory",
    "severity": "Severity Level",
    "confidence": 0.95,
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "summary": "Brief summary of the complaint",
    "actionable_insight": "How StoreHub could address this pain point",
    "reasoning": "Brief explanation of why this categorization was chosen"
}}

IMPORTANT GUIDELINES:
- If the text doesn't clearly represent a complaint, set category to "Not a Complaint"
- Focus on the core issue, not just emotional language
- Consider the business impact when determining severity
- Be precise with keywords - they should be specific to the complaint type
- Actionable insights should be specific and practical for StoreHub

Analyze the complaint and provide your response in the exact JSON format above.
"""
        
        return prompt.strip()
    
    def _parse_gpt_response(self, response_text: str) -> Dict[str, Any]:
        """Parse GPT response and extract categorization data"""
        try:
            # Clean the response text
            response_text = response_text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                self.logger.warning("No JSON found in GPT response")
                return self._create_fallback_response()
                
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {str(e)}")
            return self._create_fallback_response()
        except Exception as e:
            self.logger.error(f"Error parsing GPT response: {str(e)}")
            return self._create_fallback_response()
    
    def _create_fallback_response(self) -> Dict[str, Any]:
        """Create a fallback response when GPT parsing fails"""
        return {
            "category": "Performance Issues",
            "subcategory": "General Issues",
            "severity": "Medium",
            "confidence": 0.3,
            "keywords": ["issue", "problem"],
            "summary": "Unable to categorize complaint automatically",
            "actionable_insight": "Manual review required for proper categorization",
            "reasoning": "Automatic categorization failed"
        }
    
    def categorize_complaint(self, complaint_text: str, source: str, url: str, 
                           competitor_name: str, platform: str = "unknown") -> CategorizedComplaint:
        """
        Categorize a single complaint using OpenAI GPT-4
        
        Args:
            complaint_text: The complaint text to categorize
            source: Source of the complaint (e.g., "Google Search", "Social Media")
            url: URL where the complaint was found
            competitor_name: Name of the competitor
            platform: Platform where complaint was found
            
        Returns:
            CategorizedComplaint object with detailed analysis
        """
        
        # Rate limiting
        self._rate_limit()
        
        try:
            # Import OpenAI client inside method to avoid import issues
            from openai import OpenAI
            
            # Create client with API key
            client = OpenAI(api_key=self.api_key)
            
            # Create categorization prompt
            prompt = self._create_categorization_prompt(complaint_text, competitor_name)
            
            # Make API call
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert business analyst specializing in competitive intelligence and customer feedback analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse response
            response_text = response.choices[0].message.content
            parsed_response = self._parse_gpt_response(response_text)
            
            # Create categorized complaint
            complaint = CategorizedComplaint(
                original_text=complaint_text,
                source=source,
                url=url,
                category=parsed_response.get("category", "Performance Issues"),
                subcategory=parsed_response.get("subcategory", "General Issues"),
                severity=parsed_response.get("severity", "Medium"),
                confidence=parsed_response.get("confidence", 0.5),
                keywords=parsed_response.get("keywords", []),
                summary=parsed_response.get("summary", "No summary available"),
                actionable_insight=parsed_response.get("actionable_insight", "No actionable insight available"),
                timestamp=datetime.now(),
                platform=platform
            )
            
            self.logger.debug(f"Categorized complaint: {complaint.category} - {complaint.subcategory}")
            return complaint
            
        except Exception as e:
            self.logger.error(f"Error categorizing complaint: {str(e)}")
            
            # Return fallback categorization
            return CategorizedComplaint(
                original_text=complaint_text,
                source=source,
                url=url,
                category="Performance Issues",
                subcategory="General Issues",
                severity="Medium",
                confidence=0.0,
                keywords=["error"],
                summary="Categorization failed",
                actionable_insight="Manual review required",
                timestamp=datetime.now(),
                platform=platform
            )
    
    def categorize_complaints_batch(self, complaints: List[Dict[str, Any]], 
                                  competitor_name: str, batch_size: int = 10) -> List[CategorizedComplaint]:
        """
        Categorize multiple complaints in batches
        
        Args:
            complaints: List of complaint dictionaries with 'text', 'source', 'url', 'platform'
            competitor_name: Name of the competitor
            batch_size: Number of complaints to process at once
            
        Returns:
            List of CategorizedComplaint objects
        """
        
        categorized_complaints = []
        
        for i in range(0, len(complaints), batch_size):
            batch = complaints[i:i + batch_size]
            
            self.logger.info(f"Processing batch {i//batch_size + 1}/{(len(complaints) + batch_size - 1)//batch_size}")
            
            for complaint in batch:
                try:
                    categorized_complaint = self.categorize_complaint(
                        complaint_text=complaint['text'],
                        source=complaint['source'],
                        url=complaint['url'],
                        competitor_name=competitor_name,
                        platform=complaint.get('platform', 'unknown')
                    )
                    categorized_complaints.append(categorized_complaint)
                    
                except Exception as e:
                    self.logger.error(f"Error categorizing complaint in batch: {str(e)}")
                    # Continue with next complaint
                    continue
        
        return categorized_complaints
    
    def analyze_category_trends(self, categorized_complaints: List[CategorizedComplaint]) -> Dict[str, CategoryAnalysis]:
        """
        Analyze trends and patterns within each complaint category
        
        Args:
            categorized_complaints: List of categorized complaints
            
        Returns:
            Dictionary mapping category names to CategoryAnalysis objects
        """
        category_analyses = {}
        
        # Group complaints by category
        complaints_by_category = defaultdict(list)
        for complaint in categorized_complaints:
            if complaint.category != "Error" and complaint.category != "Not a Complaint":
                complaints_by_category[complaint.category].append(complaint)
        
        # Analyze each category
        for category, complaints in complaints_by_category.items():
            if not complaints:
                continue
                
            # Severity distribution
            severity_dist = Counter(c.severity for c in complaints)
            
            # Common keywords analysis
            all_keywords = []
            for complaint in complaints:
                all_keywords.extend(complaint.keywords)
            common_keywords = Counter(all_keywords).most_common(10)
            
            # Top complaints by severity and confidence
            top_complaints = sorted(
                complaints, 
                key=lambda x: (
                    self.severity_levels.index(x.severity) if x.severity in self.severity_levels else 0,
                    x.confidence
                ), 
                reverse=True
            )[:5]
            
            # Collect actionable insights
            actionable_insights = list(set(c.actionable_insight for c in complaints if c.actionable_insight))
            
            # Generate trend analysis using AI
            trend_analysis = self._generate_trend_analysis(category, complaints)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(category, complaints)
            
            category_analyses[category] = CategoryAnalysis(
                category=category,
                total_complaints=len(complaints),
                severity_distribution=dict(severity_dist),
                common_keywords=common_keywords,
                top_complaints=top_complaints,
                actionable_insights=actionable_insights[:10],  # Top 10 insights
                trend_analysis=trend_analysis,
                recommendations=recommendations
            )
        
        return category_analyses
    
    def _generate_trend_analysis(self, category: str, complaints: List[CategorizedComplaint]) -> str:
        """Generate AI-powered trend analysis for a category"""
        try:
            # Create summary of complaints for analysis
            complaint_summaries = [c.summary for c in complaints[:10]]  # Top 10 complaints
            keywords = [keyword for c in complaints for keyword in c.keywords]
            keyword_counts = Counter(keywords).most_common(5)
            
            prompt = f"""
Analyze the following complaint data for the "{category}" category and provide trend insights:

COMPLAINT SUMMARIES:
{'; '.join(complaint_summaries)}

TOP KEYWORDS:
{', '.join([f"{k}({v})" for k, v in keyword_counts])}

TOTAL COMPLAINTS: {len(complaints)}

Provide a 2-3 sentence analysis of the main trends and patterns in this category.
Focus on:
1. What are the most common issues?
2. Are there any emerging patterns?
3. What does this tell us about the competitor's weaknesses?

Keep the response concise and actionable.
"""
            
            self._rate_limit()
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert business analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Error generating trend analysis: {e}")
            return f"Trend analysis unavailable for {category}. Manual review recommended."
    
    def _generate_recommendations(self, category: str, complaints: List[CategorizedComplaint]) -> List[str]:
        """Generate AI-powered recommendations for addressing complaints in a category"""
        try:
            # Get top actionable insights
            insights = list(set(c.actionable_insight for c in complaints if c.actionable_insight))[:5]
            
            prompt = f"""
Based on the following actionable insights for "{category}" complaints, generate 3-5 specific recommendations for StoreHub to gain competitive advantage:

ACTIONABLE INSIGHTS:
{'; '.join(insights)}

Provide specific, actionable recommendations that StoreHub can implement. Focus on:
1. Product/service improvements
2. Marketing messaging opportunities
3. Sales strategies
4. Customer experience enhancements

Format as a numbered list of concise recommendations.
"""
            
            self._rate_limit()
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strategic business consultant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content.strip()
            # Parse numbered list
            recommendations = []
            for line in response_text.split('\n'):
                if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith('-')):
                    recommendations.append(line.strip())
            
            return recommendations[:5]  # Max 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return [f"Recommendations unavailable for {category}. Manual review recommended."]
    
    def generate_comprehensive_report(self, categorized_complaints: List[CategorizedComplaint], 
                                    competitor_name: str) -> Dict[str, Any]:
        """
        Generate a comprehensive analysis report of all categorized complaints
        
        Args:
            categorized_complaints: List of categorized complaints
            competitor_name: Name of the competitor
            
        Returns:
            Comprehensive report dictionary
        """
        # Filter out errors and non-complaints
        valid_complaints = [
            c for c in categorized_complaints 
            if c.category not in ["Error", "Not a Complaint", "Unknown"]
        ]
        
        # Category analysis
        category_analyses = self.analyze_category_trends(valid_complaints)
        
        # Overall statistics
        total_complaints = len(valid_complaints)
        category_distribution = Counter(c.category for c in valid_complaints)
        severity_distribution = Counter(c.severity for c in valid_complaints)
        confidence_distribution = Counter(c.confidence for c in valid_complaints)
        platform_distribution = Counter(c.platform for c in valid_complaints)
        
        # Top weaknesses across all categories
        all_insights = []
        for complaint in valid_complaints:
            if complaint.actionable_insight:
                all_insights.append(complaint.actionable_insight)
        
        top_weaknesses = list(set(all_insights))[:10]
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            competitor_name, valid_complaints, category_analyses
        )
        
        # Compile comprehensive report
        report = {
            "competitor_name": competitor_name,
            "analysis_timestamp": datetime.now().isoformat(),
            "overall_statistics": {
                "total_complaints": total_complaints,
                "category_distribution": dict(category_distribution),
                "severity_distribution": dict(severity_distribution),
                "confidence_distribution": dict(confidence_distribution),
                "platform_distribution": dict(platform_distribution),
                "avg_confidence": sum(c.confidence for c in valid_complaints) / len(valid_complaints) if valid_complaints else 0,
                "most_common_keywords": keyword_counts.most_common(20),
                "high_severity_count": severity_distribution.get('High', 0) + severity_distribution.get('Critical', 0),
                "actionable_insights_count": len([c for c in valid_complaints if c.actionable_insight and c.actionable_insight != "No actionable insight available"])
            },
            "category_analyses": {
                category: {
                    "category": analysis.category,
                    "total_complaints": analysis.total_complaints,
                    "severity_distribution": analysis.severity_distribution,
                    "common_keywords": analysis.common_keywords,
                    "top_complaints": [
                        {
                            "text": c.original_text,
                            "category": c.category,
                            "subcategory": c.subcategory,
                            "severity": c.severity,
                            "confidence": c.confidence,
                            "keywords": c.keywords,
                            "summary": c.summary,
                            "actionable_insight": c.actionable_insight,
                            "source": c.source,
                            "platform": c.platform
                        }
                        for c in analysis.top_complaints
                    ],
                    "actionable_insights": analysis.actionable_insights,
                    "trend_analysis": analysis.trend_analysis,
                    "recommendations": analysis.recommendations
                }
                for category, analysis in category_analyses.items()
            },
            "top_weaknesses": top_weaknesses,
            "raw_complaints": [
                {
                    "text": c.original_text,
                    "category": c.category,
                    "subcategory": c.subcategory,
                    "severity": c.severity,
                    "confidence": c.confidence,
                    "summary": c.summary,
                    "source": c.source,
                    "platform": c.platform,
                    "url": c.url
                }
                for c in valid_complaints
            ],
            "executive_summary": executive_summary,
            "strategic_recommendations": strategic_recommendations
        }
        
        return report
    
    def _generate_executive_summary(self, competitor_name: str, complaints: List[CategorizedComplaint], 
                                  category_analyses: Dict[str, CategoryAnalysis]) -> str:
        """Generate executive summary of complaint analysis"""
        try:
            # Prepare data for summary
            total_complaints = len(complaints)
            top_categories = sorted(
                category_analyses.items(),
                key=lambda x: x[1].total_complaints,
                reverse=True
            )[:3]
            
            category_summary = "; ".join([
                f"{cat}: {analysis.total_complaints} complaints" 
                for cat, analysis in top_categories
            ])
            
            prompt = f"""
Generate a concise executive summary for a competitive analysis report on {competitor_name}.

KEY DATA:
- Total complaints analyzed: {total_complaints}
- Top complaint categories: {category_summary}
- Analysis focuses on social media and review site complaints

The summary should be 3-4 sentences and highlight:
1. Overall complaint volume and main categories
2. Key weaknesses identified
3. Strategic implications for competitors

Write in a professional, analytical tone suitable for C-level executives.
"""
            
            self._rate_limit()
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strategic business consultant writing for C-level executives."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Error generating executive summary: {e}")
            return f"Executive summary unavailable. Analyzed {len(complaints)} complaints across {len(category_analyses)} categories for {competitor_name}." 