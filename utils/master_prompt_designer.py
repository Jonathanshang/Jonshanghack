"""
Master Prompt Designer for Competitive Analysis

This module contains comprehensive prompt templates for AI-powered competitive analysis,
including StoreHub context, pricing analysis, monetization strategy, vision inference,
and competitive positioning prompts.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class AnalysisContext:
    """Context information for competitive analysis"""
    competitor_name: str
    competitor_url: str
    target_country: str
    analysis_date: str
    discovered_pages: Dict[str, List[str]]
    scraped_content: List[Dict[str, Any]]
    complaint_analysis: Dict[str, Any]
    categorized_complaints: List[Any]

class MasterPromptDesigner:
    """
    Master prompt designer for competitive analysis using OpenAI GPT-4
    
    Contains comprehensive prompt templates for:
    - StoreHub context and positioning
    - Pricing analysis and breakdown
    - Monetization strategy analysis
    - Vision and roadmap inference
    - Competitive positioning strategies
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the master prompt designer
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # StoreHub context and positioning
        self.storehub_context = {
            "company_name": "StoreHub",
            "value_proposition": "Comprehensive POS and business management solution for retail and hospitality",
            "key_differentiators": [
                "Integrated POS, inventory, and customer management",
                "Flexible payment processing options",
                "Transparent pricing with no hidden fees",
                "Strong customer support and training",
                "Multi-location and franchise support",
                "Comprehensive analytics and reporting",
                "Easy integration with third-party services"
            ],
            "target_markets": [
                "Retail stores and boutiques",
                "Restaurants and cafes",
                "Service businesses",
                "Multi-location enterprises",
                "Franchises and chains"
            ],
            "pricing_philosophy": "Transparent, fair pricing with no hidden fees or mandatory add-ons",
            "support_philosophy": "Proactive customer success with comprehensive training and support",
            "competitive_advantages": [
                "No payment processing lock-in",
                "Transparent pricing structure",
                "Comprehensive feature set in base package",
                "Strong local market presence",
                "Excellent customer support ratings",
                "Flexible implementation options"
            ]
        }
        
        # Analysis frameworks
        self.analysis_frameworks = {
            "pricing_analysis": {
                "components": [
                    "Hardware costs and models",
                    "Software licensing tiers",
                    "Implementation and setup fees",
                    "Monthly/annual subscription costs",
                    "Transaction fees and processing costs",
                    "Additional service charges",
                    "Hidden fees and surprise costs"
                ],
                "evaluation_criteria": [
                    "Total cost of ownership",
                    "Value for money",
                    "Pricing transparency",
                    "Scalability costs",
                    "Comparison to market standards"
                ]
            },
            "monetization_strategy": {
                "revenue_streams": [
                    "Software subscriptions",
                    "Hardware sales/leasing",
                    "Payment processing fees",
                    "Professional services",
                    "Add-on features and modules",
                    "Training and certification",
                    "Integration and customization"
                ],
                "customer_retention": [
                    "Contract terms and lock-in",
                    "Switching costs",
                    "Integration complexity",
                    "Data portability",
                    "Relationship management"
                ]
            },
            "vision_analysis": {
                "data_sources": [
                    "Press releases and announcements",
                    "Job postings and hiring patterns",
                    "Product roadmap communications",
                    "Partnership announcements",
                    "Investment and funding news",
                    "Technology acquisitions",
                    "Market expansion signals"
                ],
                "prediction_areas": [
                    "New product launches",
                    "Market expansion plans",
                    "Technology investments",
                    "Partnership strategies",
                    "Competitive positioning shifts"
                ]
            }
        }
    
    def create_base_system_prompt(self) -> str:
        """Create the base system prompt with StoreHub context"""
        return f"""
You are a senior business analyst and competitive intelligence expert working for {self.storehub_context['company_name']}. 
Your expertise includes market analysis, pricing strategy, monetization models, and competitive positioning.

STOREHUB CONTEXT:
Company: {self.storehub_context['company_name']}
Value Proposition: {self.storehub_context['value_proposition']}

Key Differentiators:
{chr(10).join(f"• {diff}" for diff in self.storehub_context['key_differentiators'])}

Target Markets:
{chr(10).join(f"• {market}" for market in self.storehub_context['target_markets'])}

Competitive Advantages:
{chr(10).join(f"• {advantage}" for advantage in self.storehub_context['competitive_advantages'])}

Pricing Philosophy: {self.storehub_context['pricing_philosophy']}
Support Philosophy: {self.storehub_context['support_philosophy']}

ANALYSIS PRINCIPLES:
1. Always consider StoreHub's positioning and advantages
2. Identify opportunities for competitive differentiation
3. Focus on actionable insights for sales, marketing, and product teams
4. Maintain objective analysis while highlighting StoreHub's strengths
5. Consider total cost of ownership, not just upfront costs
6. Analyze both direct and indirect competitive threats
7. Provide strategic recommendations based on findings

Your analysis should be thorough, data-driven, and actionable for C-level decision making.
"""
    
    def create_pricing_analysis_prompt(self, context: AnalysisContext) -> str:
        """Create comprehensive pricing analysis prompt"""
        
        base_prompt = self.create_base_system_prompt()
        
        pricing_prompt = f"""
{base_prompt}

PRICING ANALYSIS TASK:
Analyze the pricing structure of {context.competitor_name} and provide a comprehensive breakdown 
with strategic implications for StoreHub.

ANALYSIS FRAMEWORK:
{chr(10).join(f"• {component}" for component in self.analysis_frameworks['pricing_analysis']['components'])}

EVALUATION CRITERIA:
{chr(10).join(f"• {criteria}" for criteria in self.analysis_frameworks['pricing_analysis']['evaluation_criteria'])}

COMPETITOR DATA:
Competitor: {context.competitor_name}
Website: {context.competitor_url}
Target Country: {context.target_country}
Analysis Date: {context.analysis_date}

DISCOVERED PAGES:
{json.dumps(context.discovered_pages, indent=2)}

REQUIRED ANALYSIS OUTPUT:
1. HARDWARE ANALYSIS:
   - Hardware model identification (proprietary vs. commodity)
   - Cost structure (purchase/lease/subscription)
   - Hardware strategy assessment
   - Comparison to StoreHub's hardware approach

2. SOFTWARE PRICING BREAKDOWN:
   - Detailed tier analysis with specific costs
   - Billing methodology (per-terminal/location/employee/revenue)
   - Feature comparison across tiers
   - Hidden fees and additional costs identification

3. TOTAL COST OF OWNERSHIP:
   - Setup and implementation costs
   - Monthly/annual operational costs
   - Transaction and processing fees
   - Support and maintenance costs
   - Upgrade and scaling costs

4. COMPETITIVE POSITIONING:
   - Price positioning vs. market standards
   - Value proposition analysis
   - Pricing transparency assessment
   - Customer lock-in mechanisms

5. STRATEGIC IMPLICATIONS:
   - StoreHub's competitive advantages
   - Pricing-based sales strategies
   - Marketing messaging opportunities
   - Product positioning recommendations

6. ACTIONABLE RECOMMENDATIONS:
   - Sales team talking points
   - Marketing campaign ideas
   - Product pricing adjustments
   - Competitive response strategies

FORMAT: Provide a structured analysis with clear sections, specific data points, 
and actionable recommendations. Use bullet points for clarity and include 
confidence levels for your assessments.
"""
        return pricing_prompt
    
    def create_monetization_strategy_prompt(self, context: AnalysisContext) -> str:
        """Create monetization strategy analysis prompt"""
        
        base_prompt = self.create_base_system_prompt()
        
        monetization_prompt = f"""
{base_prompt}

MONETIZATION STRATEGY ANALYSIS TASK:
Analyze how {context.competitor_name} makes money and retains customers, 
with strategic implications for StoreHub's competitive positioning.

ANALYSIS FRAMEWORK:
Revenue Streams Analysis:
{chr(10).join(f"• {stream}" for stream in self.analysis_frameworks['monetization_strategy']['revenue_streams'])}

Customer Retention Analysis:
{chr(10).join(f"• {retention}" for retention in self.analysis_frameworks['monetization_strategy']['customer_retention'])}

COMPETITOR DATA:
Competitor: {context.competitor_name}
Website: {context.competitor_url}
Target Country: {context.target_country}
Analysis Date: {context.analysis_date}

REQUIRED ANALYSIS OUTPUT:
1. REVENUE MODEL BREAKDOWN:
   - Primary revenue streams with estimated percentages
   - Secondary revenue sources
   - Revenue growth strategies
   - Seasonal/cyclical patterns

2. CUSTOMER ACQUISITION STRATEGY:
   - Lead generation methods
   - Sales process analysis
   - Customer onboarding approach
   - Initial value delivery

3. CUSTOMER RETENTION MECHANISMS:
   - Contract terms and lock-in strategies
   - Switching cost analysis
   - Customer success programs
   - Loyalty and retention incentives

4. EXPANSION REVENUE MODEL:
   - Upselling strategies
   - Cross-selling opportunities
   - Premium service offerings
   - Add-on product ecosystem

5. PRICING PSYCHOLOGY:
   - Pricing model design rationale
   - Customer perception management
   - Value anchoring strategies
   - Competitive pricing responses

6. LOCK-IN ANALYSIS:
   - Technical lock-in mechanisms
   - Data portability barriers
   - Integration complexity
   - Contractual obligations

7. STRATEGIC IMPLICATIONS FOR STOREHUB:
   - Competitive differentiation opportunities
   - Revenue model optimization
   - Customer retention improvements
   - Market positioning strategies

8. ACTIONABLE RECOMMENDATIONS:
   - Sales process improvements
   - Customer success strategies
   - Product development priorities
   - Marketing positioning tactics

FORMAT: Provide detailed analysis with quantified estimates where possible, 
strategic insights, and specific recommendations for StoreHub's competitive response.
"""
        return monetization_prompt
    
    def create_vision_roadmap_prompt(self, context: AnalysisContext) -> str:
        """Create vision and roadmap inference prompt"""
        
        base_prompt = self.create_base_system_prompt()
        
        vision_prompt = f"""
{base_prompt}

VISION & ROADMAP INFERENCE TASK:
Analyze {context.competitor_name}'s strategic direction and predict future moves 
based on available signals, with implications for StoreHub's strategic planning.

ANALYSIS FRAMEWORK:
Data Sources for Inference:
{chr(10).join(f"• {source}" for source in self.analysis_frameworks['vision_analysis']['data_sources'])}

Prediction Areas:
{chr(10).join(f"• {area}" for area in self.analysis_frameworks['vision_analysis']['prediction_areas'])}

COMPETITOR DATA:
Competitor: {context.competitor_name}
Website: {context.competitor_url}
Target Country: {context.target_country}
Analysis Date: {context.analysis_date}

DISCOVERED CONTENT:
Blog/News Pages: {len(context.discovered_pages.get('blog', []))} pages
Careers Pages: {len(context.discovered_pages.get('careers', []))} pages
About Pages: {len(context.discovered_pages.get('about', []))} pages

REQUIRED ANALYSIS OUTPUT:
1. STRATEGIC VISION ANALYSIS:
   - Company mission and vision statements
   - Strategic priorities and focus areas
   - Market positioning strategy
   - Long-term business objectives

2. PRODUCT ROADMAP INFERENCE:
   - Upcoming product features and capabilities
   - Technology investments and trends
   - Integration and partnership strategies
   - Platform evolution predictions

3. MARKET EXPANSION SIGNALS:
   - Geographic expansion plans
   - New market segment targeting
   - Partnership and acquisition strategies
   - Distribution channel development

4. TECHNOLOGY INVESTMENT PATTERNS:
   - R&D focus areas
   - Technology stack evolution
   - Innovation priorities
   - Digital transformation initiatives

5. HIRING AND TALENT STRATEGY:
   - Key role recruitment patterns
   - Skill requirements and focus areas
   - Team expansion indicators
   - Cultural and capability building

6. COMPETITIVE POSITIONING SHIFTS:
   - Market positioning changes
   - Competitive response patterns
   - Differentiation strategy evolution
   - Brand and messaging updates

7. THREAT ASSESSMENT FOR STOREHUB:
   - Direct competitive threats
   - Indirect market disruptions
   - Innovation challenges
   - Market share vulnerabilities

8. STRATEGIC RECOMMENDATIONS:
   - Proactive competitive responses
   - Innovation priorities for StoreHub
   - Market positioning adjustments
   - Partnership and acquisition opportunities

9. PREDICTIVE TIMELINE:
   - Short-term moves (3-6 months)
   - Medium-term strategy (6-18 months)
   - Long-term vision (18+ months)
   - Key milestone predictions

FORMAT: Provide evidence-based predictions with confidence levels, 
strategic implications, and specific recommendations for StoreHub's response strategy.
"""
        return vision_prompt
    
    def create_competitive_positioning_prompt(self, context: AnalysisContext) -> str:
        """Create competitive positioning analysis prompt"""
        
        base_prompt = self.create_base_system_prompt()
        
        positioning_prompt = f"""
{base_prompt}

COMPETITIVE POSITIONING ANALYSIS TASK:
Analyze {context.competitor_name}'s market positioning and develop strategic 
recommendations for StoreHub's competitive response and differentiation.

COMPETITOR DATA:
Competitor: {context.competitor_name}
Website: {context.competitor_url}
Target Country: {context.target_country}
Analysis Date: {context.analysis_date}

COMPLAINT ANALYSIS AVAILABLE:
Total Complaints: {context.complaint_analysis.get('total_complaints', 0)}
Categorized Complaints: {len(context.categorized_complaints)}

REQUIRED ANALYSIS OUTPUT:
1. MARKET POSITIONING ANALYSIS:
   - Brand positioning and messaging
   - Target customer segments
   - Value proposition differentiation
   - Competitive advantages claimed

2. STRENGTHS ASSESSMENT:
   - Core competencies and capabilities
   - Market leadership areas
   - Customer loyalty factors
   - Innovation and technology strengths

3. WEAKNESSES IDENTIFICATION:
   - Product/service limitations
   - Customer pain points and complaints
   - Market vulnerabilities
   - Operational challenges

4. OPPORTUNITY GAPS:
   - Unmet customer needs
   - Market segments underserved
   - Feature gaps and limitations
   - Service delivery weaknesses

5. COMPETITIVE THREATS:
   - Direct competition analysis
   - Indirect market disruptors
   - New entrant threats
   - Technology disruption risks

6. STOREHUB COMPETITIVE ADVANTAGES:
   - Areas where StoreHub excels
   - Differentiation opportunities
   - Unique value propositions
   - Competitive moats

7. STRATEGIC POSITIONING RECOMMENDATIONS:
   - Market positioning strategy
   - Messaging and communication
   - Product positioning tactics
   - Competitive response strategies

8. SALES ENABLEMENT:
   - Battle cards and talking points
   - Objection handling strategies
   - Competitive win scenarios
   - Pricing and value positioning

9. MARKETING STRATEGY:
   - Campaign messaging opportunities
   - Content marketing themes
   - SEO and digital marketing tactics
   - Brand differentiation strategies

10. PRODUCT STRATEGY:
    - Feature prioritization recommendations
    - Innovation opportunities
    - Integration and partnership needs
    - Platform development priorities

FORMAT: Provide comprehensive analysis with specific, actionable recommendations 
for each department (Sales, Marketing, Product, Leadership) with clear prioritization.
"""
        return positioning_prompt
    
    def create_battlecard_generation_prompt(self, context: AnalysisContext) -> str:
        """Create sales battlecard generation prompt"""
        
        base_prompt = self.create_base_system_prompt()
        
        battlecard_prompt = f"""
{base_prompt}

SALES BATTLECARD GENERATION TASK:
Create comprehensive sales battlecards for {context.competitor_name} that enable 
StoreHub sales teams to compete effectively and win deals.

COMPETITOR DATA:
Competitor: {context.competitor_name}
Website: {context.competitor_url}
Target Country: {context.target_country}
Analysis Date: {context.analysis_date}

COMPLAINT INSIGHTS:
Total Complaints: {context.complaint_analysis.get('total_complaints', 0)}
Categorized Complaints: {len(context.categorized_complaints)}

REQUIRED BATTLECARD OUTPUT:
1. COMPETITOR OVERVIEW:
   - Company size and market position
   - Key products and services
   - Target customer segments
   - Pricing model summary

2. COMPETITIVE STRENGTHS:
   - What they do well
   - Market advantages
   - Customer loyalty factors
   - Technology capabilities

3. COMPETITIVE WEAKNESSES:
   - Product limitations
   - Service gaps
   - Customer complaints
   - Market vulnerabilities

4. PRICING TRAPS:
   - Hidden fees and costs
   - Complex pricing structures
   - Total cost of ownership issues
   - Unfavorable contract terms

5. WEAKNESS LANDMINES:
   - Proven customer pain points
   - Service delivery failures
   - Product reliability issues
   - Support and training gaps

6. STOREHUB ADVANTAGES:
   - Clear differentiation points
   - Superior features and capabilities
   - Better pricing or value
   - Enhanced customer experience

7. OBJECTION HANDLING:
   - Common customer objections
   - Competitive claims and responses
   - Proof points and evidence
   - Case studies and references

8. DISCOVERY QUESTIONS:
   - Questions to uncover pain points
   - Qualification criteria
   - Needs assessment probes
   - Competitive intelligence gathering

9. CLOSING STRATEGIES:
   - Value proposition reinforcement
   - Competitive differentiation
   - Risk mitigation messaging
   - Urgency and scarcity tactics

10. SUPPORTING MATERIALS:
    - Case studies and testimonials
    - ROI calculators and tools
    - Competitive comparison charts
    - Reference customers and stories

FORMAT: Create practical, actionable battlecards with specific talking points, 
questions, and responses that sales teams can use immediately in competitive situations.
"""
        return battlecard_prompt
    
    def create_marketing_strategy_prompt(self, context: AnalysisContext) -> str:
        """Create marketing strategy recommendations prompt"""
        
        base_prompt = self.create_base_system_prompt()
        
        marketing_prompt = f"""
{base_prompt}

MARKETING STRATEGY RECOMMENDATIONS TASK:
Develop comprehensive marketing strategies for StoreHub based on competitive analysis 
of {context.competitor_name} and identified market opportunities.

COMPETITOR DATA:
Competitor: {context.competitor_name}
Website: {context.competitor_url}
Target Country: {context.target_country}
Analysis Date: {context.analysis_date}

COMPLAINT INSIGHTS:
Total Complaints: {context.complaint_analysis.get('total_complaints', 0)}
Categorized Complaints: {len(context.categorized_complaints)}

REQUIRED MARKETING STRATEGY OUTPUT:
1. PAIN-POINT CAMPAIGN RECOMMENDATIONS:
   - Top 3 competitor pain points to target
   - Campaign messaging and positioning
   - Content themes and topics
   - Channel-specific strategies

2. TRANSPARENT PRICING HUB:
   - Pricing comparison positioning
   - Value proposition messaging
   - Cost calculator recommendations
   - Transparency advantage communication

3. COMPETITIVE CONTENT STRATEGY:
   - Blog post and article ideas
   - Video content opportunities
   - Infographic and visual content
   - Case study development

4. SEO AND DIGITAL MARKETING:
   - Long-tail keyword opportunities
   - Content gap analysis
   - Search volume and competition
   - Local SEO recommendations

5. SOCIAL MEDIA STRATEGY:
   - Platform-specific messaging
   - Community engagement tactics
   - Influencer and partnership opportunities
   - User-generated content strategies

6. LEAD GENERATION TACTICS:
   - Targeted campaign ideas
   - Lead magnet opportunities
   - Conversion optimization
   - Nurturing sequence development

7. BRAND POSITIONING:
   - Differentiation messaging
   - Brand personality development
   - Competitive advantage communication
   - Market positioning strategy

8. CAMPAIGN EXECUTION:
   - Campaign priorities and timing
   - Budget allocation recommendations
   - Success metrics and KPIs
   - Testing and optimization strategies

9. CUSTOMER TESTIMONIAL STRATEGY:
   - Testimonial collection priorities
   - Case study development
   - Reference customer programs
   - Success story amplification

10. COMPETITIVE MONITORING:
    - Competitor tracking setup
    - Alert and monitoring systems
    - Response strategy development
    - Continuous improvement processes

FORMAT: Provide specific, actionable marketing recommendations with clear priorities, 
timelines, and success metrics that can be implemented immediately.
"""
        return marketing_prompt
    
    def generate_analysis_prompt(self, analysis_type: str, context: AnalysisContext) -> str:
        """
        Generate a specific analysis prompt based on type and context
        
        Args:
            analysis_type: Type of analysis (pricing, monetization, vision, positioning, battlecard, marketing)
            context: Analysis context information
            
        Returns:
            Formatted prompt string for the specified analysis type
        """
        prompt_generators = {
            'pricing': self.create_pricing_analysis_prompt,
            'monetization': self.create_monetization_strategy_prompt,
            'vision': self.create_vision_roadmap_prompt,
            'positioning': self.create_competitive_positioning_prompt,
            'battlecard': self.create_battlecard_generation_prompt,
            'marketing': self.create_marketing_strategy_prompt
        }
        
        if analysis_type not in prompt_generators:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        return prompt_generators[analysis_type](context)
    
    def create_comprehensive_analysis_prompt(self, context: AnalysisContext) -> str:
        """Create a comprehensive analysis prompt that covers all aspects"""
        
        base_prompt = self.create_base_system_prompt()
        
        comprehensive_prompt = f"""
{base_prompt}

COMPREHENSIVE COMPETITIVE ANALYSIS TASK:
Conduct a complete competitive analysis of {context.competitor_name} covering all 
strategic dimensions with actionable recommendations for StoreHub.

COMPETITOR DATA:
Competitor: {context.competitor_name}
Website: {context.competitor_url}
Target Country: {context.target_country}
Analysis Date: {context.analysis_date}

AVAILABLE DATA:
- Discovered Pages: {sum(len(urls) for urls in context.discovered_pages.values())} total pages
- Scraped Content: {len(context.scraped_content)} pages analyzed
- Complaint Analysis: {context.complaint_analysis.get('total_complaints', 0)} complaints
- Categorized Complaints: {len(context.categorized_complaints)} categorized

REQUIRED COMPREHENSIVE OUTPUT:
1. EXECUTIVE SUMMARY (2-3 paragraphs)
   - Key findings and strategic implications
   - Primary competitive threats and opportunities
   - Recommended strategic responses

2. PRICING ANALYSIS
   - Hardware and software pricing breakdown
   - Total cost of ownership analysis
   - Competitive pricing positioning
   - StoreHub pricing advantages

3. MONETIZATION STRATEGY
   - Revenue model analysis
   - Customer acquisition and retention
   - Expansion revenue opportunities
   - Lock-in mechanisms

4. VISION & ROADMAP
   - Strategic direction inference
   - Product roadmap predictions
   - Market expansion signals
   - Technology investment patterns

5. COMPETITIVE POSITIONING
   - Market position analysis
   - Strengths and weaknesses
   - Opportunity gaps
   - Competitive threats

6. CUSTOMER INSIGHTS
   - Complaint analysis summary
   - Pain point identification
   - Satisfaction indicators
   - Loyalty factors

7. STRATEGIC RECOMMENDATIONS
   - Sales enablement strategies
   - Marketing campaign opportunities
   - Product development priorities
   - Competitive response tactics

8. ACTION ITEMS
   - Immediate actions (next 30 days)
   - Short-term initiatives (3-6 months)
   - Long-term strategic moves (6+ months)

FORMAT: Provide a structured, executive-ready report with clear sections, 
data-driven insights, and specific actionable recommendations for each department.
"""
        return comprehensive_prompt
    
    def get_available_analysis_types(self) -> List[str]:
        """Get list of available analysis types"""
        return [
            'pricing',
            'monetization', 
            'vision',
            'positioning',
            'battlecard',
            'marketing',
            'comprehensive'
        ]
    
    def get_storehub_context(self) -> Dict[str, Any]:
        """Get StoreHub context information"""
        return self.storehub_context
    
    def get_analysis_frameworks(self) -> Dict[str, Any]:
        """Get analysis frameworks"""
        return self.analysis_frameworks
    
    def get_monetization_analysis_prompt(self, competitor_name: str, analysis_context: Dict[str, Any]) -> str:
        """Get monetization analysis prompt for the MonetizationAnalyzer"""
        # Create a mock AnalysisContext from the provided data
        mock_context = AnalysisContext(
            competitor_name=competitor_name,
            competitor_url=analysis_context.get('competitor_url', ''),
            target_country=analysis_context.get('country_context', {}).get('country', 'US'),
            analysis_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            discovered_pages=analysis_context.get('discovered_pages', {}),
            scraped_content=analysis_context.get('scraped_content', []),
            complaint_analysis=analysis_context.get('complaint_analysis', {}),
            categorized_complaints=analysis_context.get('categorized_complaints', [])
        )
        
        return self.create_monetization_strategy_prompt(mock_context)
    
    def get_vision_analysis_prompt(self, competitor_name: str, analysis_context: Dict[str, Any]) -> str:
        """Get vision analysis prompt for the VisionAnalyzer"""
        # Create a mock AnalysisContext from the provided data
        mock_context = AnalysisContext(
            competitor_name=competitor_name,
            competitor_url=analysis_context.get('competitor_url', ''),
            target_country=analysis_context.get('country_context', {}).get('country', 'US'),
            analysis_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            discovered_pages=analysis_context.get('discovered_pages', {}),
            scraped_content=analysis_context.get('scraped_content', []),
            complaint_analysis=analysis_context.get('complaint_analysis', {}),
            categorized_complaints=analysis_context.get('categorized_complaints', [])
        )
        
        return self.create_vision_roadmap_prompt(mock_context)
    
    def validate_context(self, context: AnalysisContext) -> bool:
        """Validate analysis context for completeness"""
        required_fields = [
            'competitor_name',
            'competitor_url', 
            'target_country',
            'analysis_date'
        ]
        
        for field in required_fields:
            if not getattr(context, field, None):
                self.logger.error(f"Missing required context field: {field}")
                return False
        
        return True 