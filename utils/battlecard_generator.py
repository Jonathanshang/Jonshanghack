import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from utils.master_prompt_designer import MasterPromptDesigner
import openai
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BattlecardSection:
    """Represents a section in the battlecard"""
    title: str
    content: List[str]
    priority: str  # 'high', 'medium', 'low'
    confidence: float
    source_analysis: List[str]

@dataclass
class SalesBattlecard:
    """Complete sales battlecard structure"""
    competitor_name: str
    last_updated: str
    
    # Executive Summary
    executive_summary: str
    competitive_position: str
    threat_level: str  # 'high', 'medium', 'low'
    
    # Key Sections
    positioning_advantages: BattlecardSection
    objection_handling: BattlecardSection
    talking_points: BattlecardSection
    pricing_strategy: BattlecardSection
    competitive_weaknesses: BattlecardSection
    
    # Strategic Guidance
    sales_strategy: BattlecardSection
    qualifying_questions: BattlecardSection
    demo_focus_areas: BattlecardSection
    
    # Metadata
    confidence_score: float
    data_sources: List[str]
    analysis_completeness: Dict[str, bool]

class BattlecardGenerator:
    """Generates sales battlecards from competitive analysis data"""
    
    def __init__(self):
        self.logger = logger
        self.master_prompt = MasterPromptDesigner()
        
        # StoreHub positioning statements
        self.storehub_positioning = {
            'core_value_props': [
                "All-in-one POS and business management solution",
                "Transparent pricing with no hidden fees",
                "Local market expertise in Southeast Asia",
                "Integrated inventory, payments, and analytics",
                "24/7 customer support with local language support",
                "Flexible payment processing options"
            ],
            'competitive_advantages': [
                "No monthly subscription fees for basic POS",
                "Local market knowledge and support",
                "Integrated e-commerce and delivery platforms",
                "Real-time inventory management",
                "Multi-location management capabilities",
                "Comprehensive reporting and analytics"
            ],
            'target_segments': [
                "Small to medium-sized restaurants",
                "Retail stores and boutiques",
                "Food courts and quick service restaurants",
                "Multi-location businesses",
                "E-commerce enabled businesses"
            ]
        }
    
    def generate_battlecard(self, analysis_data: Dict[str, Any]) -> SalesBattlecard:
        """Generate a complete sales battlecard from analysis data"""
        try:
            self.logger.info(f"Starting battlecard generation for {analysis_data.get('competitor_name', 'Unknown')}")
            
            competitor_name = analysis_data.get('competitor_name', 'Unknown Competitor')
            
            # Analyze competitive positioning
            positioning_analysis = self._analyze_competitive_positioning(analysis_data)
            
            # Generate key battlecard sections
            positioning_advantages = self._generate_positioning_advantages(analysis_data, positioning_analysis)
            objection_handling = self._generate_objection_handling(analysis_data, positioning_analysis)
            talking_points = self._generate_talking_points(analysis_data, positioning_analysis)
            pricing_strategy = self._generate_pricing_strategy(analysis_data)
            competitive_weaknesses = self._generate_competitive_weaknesses(analysis_data)
            
            # Generate strategic guidance
            sales_strategy = self._generate_sales_strategy(analysis_data, positioning_analysis)
            qualifying_questions = self._generate_qualifying_questions(analysis_data)
            demo_focus_areas = self._generate_demo_focus_areas(analysis_data, positioning_analysis)
            
            # Calculate overall confidence and completeness
            confidence_score = self._calculate_confidence_score(analysis_data)
            data_sources = self._identify_data_sources(analysis_data)
            analysis_completeness = self._assess_analysis_completeness(analysis_data)
            
            # Create executive summary
            executive_summary = self._generate_executive_summary(analysis_data, positioning_analysis)
            competitive_position = self._determine_competitive_position(positioning_analysis)
            threat_level = self._assess_threat_level(positioning_analysis)
            
            # Create battlecard
            battlecard = SalesBattlecard(
                competitor_name=competitor_name,
                last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                executive_summary=executive_summary,
                competitive_position=competitive_position,
                threat_level=threat_level,
                positioning_advantages=positioning_advantages,
                objection_handling=objection_handling,
                talking_points=talking_points,
                pricing_strategy=pricing_strategy,
                competitive_weaknesses=competitive_weaknesses,
                sales_strategy=sales_strategy,
                qualifying_questions=qualifying_questions,
                demo_focus_areas=demo_focus_areas,
                confidence_score=confidence_score,
                data_sources=data_sources,
                analysis_completeness=analysis_completeness
            )
            
            self.logger.info(f"Successfully generated battlecard for {competitor_name}")
            return battlecard
            
        except Exception as e:
            self.logger.error(f"Error generating battlecard: {str(e)}")
            raise
    
    def _analyze_competitive_positioning(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive positioning vs StoreHub"""
        positioning = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': [],
            'positioning_gaps': [],
            'differentiation_opportunities': []
        }
        
        # Analyze pricing positioning
        pricing_analysis = analysis_data.get('pricing_analysis', {})
        if pricing_analysis:
            # Hidden fees analysis
            hidden_fees = pricing_analysis.get('hidden_fees', {})
            if hidden_fees.get('risk_level') in ['medium', 'high']:
                positioning['opportunities'].append({
                    'area': 'pricing_transparency',
                    'description': f"Competitor has {hidden_fees.get('risk_level')} hidden fees risk",
                    'storehub_advantage': 'Transparent pricing with no hidden fees'
                })
            
            # Hardware model analysis
            hardware_model = pricing_analysis.get('hardware_pricing', {}).get('model_type', '')
            if hardware_model == 'proprietary':
                positioning['opportunities'].append({
                    'area': 'hardware_flexibility',
                    'description': 'Competitor uses proprietary hardware',
                    'storehub_advantage': 'Flexible hardware options and BYOD support'
                })
        
        # Analyze monetization positioning
        monetization_analysis = analysis_data.get('monetization_analysis', {})
        if monetization_analysis:
            lock_in_strength = monetization_analysis.get('lock_in_strategies', {}).get('lock_in_strength', '')
            if lock_in_strength == 'high':
                positioning['opportunities'].append({
                    'area': 'vendor_freedom',
                    'description': 'Competitor has high customer lock-in',
                    'storehub_advantage': 'Flexible contracts and easy switching'
                })
        
        # Analyze vision and roadmap positioning
        vision_analysis = analysis_data.get('vision_analysis', {})
        if vision_analysis:
            upcoming_features = vision_analysis.get('product_roadmap', {}).get('upcoming_features', [])
            for feature in upcoming_features:
                if feature.get('confidence', 0) > 0.7:
                    positioning['threats'].append({
                        'area': 'feature_development',
                        'description': f"Competitor likely developing: {feature.get('feature')}",
                        'storehub_response': 'Monitor and potentially prioritize similar features'
                    })
        
        # Analyze social complaints for weaknesses
        categorization_report = analysis_data.get('categorization_report', {})
        if categorization_report:
            overall_stats = categorization_report.get('overall_statistics', {})
            category_dist = overall_stats.get('category_distribution', {})
            
            # Top complaint categories become positioning opportunities
            for category, count in sorted(category_dist.items(), key=lambda x: x[1], reverse=True)[:3]:
                if count > 0:
                    positioning['opportunities'].append({
                        'area': f'customer_satisfaction_{category.lower()}',
                        'description': f"Competitor has {count} complaints in {category}",
                        'storehub_advantage': f'Superior {category.lower().replace("_", " ")} experience'
                    })
        
        return positioning
    
    def _generate_positioning_advantages(self, analysis_data: Dict[str, Any], positioning_analysis: Dict[str, Any]) -> BattlecardSection:
        """Generate competitive positioning advantages"""
        advantages = []
        source_analysis = []
        
        # Core StoreHub advantages
        advantages.extend([
            "🎯 **Local Market Expertise**: Deep understanding of Southeast Asian market needs and regulations",
            "💰 **Transparent Pricing**: No hidden fees or surprise charges - what you see is what you pay",
            "🔧 **Flexible Hardware**: BYOD support and multiple hardware options vs proprietary systems",
            "🌐 **Integrated Ecosystem**: Built-in e-commerce, delivery, and payment integrations",
            "📞 **24/7 Local Support**: Customer service in local languages with regional expertise"
        ])
        
        # Add positioning opportunities from analysis
        opportunities = positioning_analysis.get('opportunities', [])
        for opp in opportunities:
            advantages.append(f"✅ **{opp['area'].replace('_', ' ').title()}**: {opp['storehub_advantage']}")
            source_analysis.append(f"Based on {opp['description']}")
        
        # Add pricing-specific advantages
        pricing_analysis = analysis_data.get('pricing_analysis', {})
        if pricing_analysis:
            hidden_fees_risk = pricing_analysis.get('hidden_fees', {}).get('risk_level', 'unknown')
            if hidden_fees_risk in ['medium', 'high']:
                advantages.append(f"💸 **No Hidden Fees**: Competitor has {hidden_fees_risk} risk of hidden fees")
                source_analysis.append("Pricing analysis revealed hidden fee risks")
        
        return BattlecardSection(
            title="Competitive Positioning Advantages",
            content=advantages,
            priority="high",
            confidence=0.9,
            source_analysis=source_analysis
        )
    
    def _generate_objection_handling(self, analysis_data: Dict[str, Any], positioning_analysis: Dict[str, Any]) -> BattlecardSection:
        """Generate objection handling responses"""
        objections = []
        source_analysis = []
        
        # Common objections and responses
        common_objections = [
            {
                "objection": "\"[Competitor] is a bigger, more established company\"",
                "response": "While they may be larger, StoreHub brings local expertise and understanding of the Southeast Asian market that global companies often lack. Our local team provides 24/7 support in your language and understands your specific business needs."
            },
            {
                "objection": "\"[Competitor] has more features\"",
                "response": "Feature quantity doesn't equal business value. StoreHub focuses on the features that matter most to your business success, with seamless integration and ease of use. More features often mean more complexity and higher costs."
            },
            {
                "objection": "\"[Competitor] integrates with more third-party systems\"",
                "response": "StoreHub is built with the most important integrations for Southeast Asian businesses already included - e-commerce platforms, delivery services, and local payment methods. This means fewer integration headaches and faster setup."
            }
        ]
        
        # Add pricing objections based on analysis
        pricing_analysis = analysis_data.get('pricing_analysis', {})
        if pricing_analysis:
            currency = pricing_analysis.get('currency_detected', 'USD')
            software_model = pricing_analysis.get('software_pricing', {}).get('pricing_model', 'unknown')
            
            if software_model == 'subscription':
                common_objections.append({
                    "objection": f"\"[Competitor] offers a subscription model that seems predictable\"",
                    "response": f"Subscription fees add up quickly and often include hidden costs. StoreHub's transparent pricing means you know exactly what you're paying for, with no surprise monthly fees that eat into your profits."
                })
        
        # Add monetization objections
        monetization_analysis = analysis_data.get('monetization_analysis', {})
        if monetization_analysis:
            lock_in_strength = monetization_analysis.get('lock_in_strategies', {}).get('lock_in_strength', '')
            if lock_in_strength == 'high':
                common_objections.append({
                    "objection": "\"[Competitor] offers an integrated solution\"",
                    "response": "Integration shouldn't mean being locked in. StoreHub provides seamless integration while maintaining your flexibility to choose payment processors and other services that work best for your business."
                })
        
        # Add complaint-based objections
        categorization_report = analysis_data.get('categorization_report', {})
        if categorization_report:
            overall_stats = categorization_report.get('overall_statistics', {})
            category_dist = overall_stats.get('category_distribution', {})
            
            if category_dist.get('Support', 0) > 0:
                common_objections.append({
                    "objection": "\"[Competitor] has good customer support\"",
                    "response": "Based on customer feedback, many users report support issues with [Competitor]. StoreHub provides 24/7 local support with dedicated account managers who understand your market and speak your language."
                })
                source_analysis.append("Customer complaint analysis revealed support issues")
        
        # Format objections for battlecard
        for obj in common_objections:
            objections.append(f"**{obj['objection']}**")
            objections.append(f"↳ {obj['response']}")
            objections.append("")  # Empty line for spacing
        
        return BattlecardSection(
            title="Objection Handling",
            content=objections,
            priority="high",
            confidence=0.85,
            source_analysis=source_analysis
        )
    
    def _generate_talking_points(self, analysis_data: Dict[str, Any], positioning_analysis: Dict[str, Any]) -> BattlecardSection:
        """Generate key talking points for sales conversations"""
        talking_points = []
        source_analysis = []
        
        # Core talking points
        talking_points.extend([
            "🎯 **Lead with Local Expertise**: \"Unlike global solutions, StoreHub is built specifically for Southeast Asian businesses\"",
            "💰 **Emphasize Transparent Pricing**: \"No hidden fees, no surprise charges - transparent pricing that protects your bottom line\"",
            "🔧 **Highlight Flexibility**: \"Choose your own hardware, payment processors, and integrations - we don't lock you in\"",
            "📈 **Focus on Business Growth**: \"Our integrated analytics and inventory management help you make data-driven decisions\"",
            "🚀 **Stress Quick Implementation**: \"Get up and running in days, not weeks, with our local support team\""
        ])
        
        # Add pricing-specific talking points
        pricing_analysis = analysis_data.get('pricing_analysis', {})
        if pricing_analysis:
            hidden_fees = pricing_analysis.get('hidden_fees', {})
            if hidden_fees.get('risk_level') in ['medium', 'high']:
                talking_points.append(f"💸 **Address Hidden Costs**: \"While [Competitor] may seem cheaper upfront, hidden fees can significantly impact your costs\"")
                source_analysis.append("Hidden fee analysis supports pricing transparency messaging")
            
            hardware_model = pricing_analysis.get('hardware_pricing', {}).get('model_type', '')
            if hardware_model == 'proprietary':
                talking_points.append(f"🔧 **Hardware Freedom**: \"[Competitor] locks you into their hardware - we give you the freedom to choose\"")
                source_analysis.append("Proprietary hardware analysis supports flexibility messaging")
        
        # Add monetization talking points
        monetization_analysis = analysis_data.get('monetization_analysis', {})
        if monetization_analysis:
            revenue_streams = monetization_analysis.get('revenue_streams', {}).get('primary_streams', [])
            for stream in revenue_streams:
                if stream.get('type') == 'payment_processing' and stream.get('confidence', 0) > 0.7:
                    talking_points.append(f"💳 **Payment Processing Freedom**: \"Choose your payment processor and rates - don't be forced into expensive payment processing\"")
                    source_analysis.append("Payment processing revenue stream analysis")
        
        # Add vision-based talking points
        vision_analysis = analysis_data.get('vision_analysis', {})
        if vision_analysis:
            upcoming_features = vision_analysis.get('product_roadmap', {}).get('upcoming_features', [])
            ai_features = [f for f in upcoming_features if 'ai' in f.get('feature', '').lower()]
            if ai_features:
                talking_points.append(f"🤖 **AI Innovation**: \"While [Competitor] is still planning AI features, StoreHub already offers intelligent insights\"")
                source_analysis.append("Competitive roadmap analysis reveals AI development plans")
        
        # Add weakness-based talking points
        categorization_report = analysis_data.get('categorization_report', {})
        if categorization_report:
            overall_stats = categorization_report.get('overall_statistics', {})
            category_dist = overall_stats.get('category_distribution', {})
            
            # Top complaint categories
            top_complaint = max(category_dist.items(), key=lambda x: x[1]) if category_dist else None
            if top_complaint and top_complaint[1] > 0:
                category_name = top_complaint[0].replace('_', ' ').lower()
                talking_points.append(f"⚠️ **Address Known Issues**: \"Many [Competitor] users report {category_name} issues - this is where StoreHub excels\"")
                source_analysis.append(f"Customer complaint analysis revealed {category_name} as top issue")
        
        return BattlecardSection(
            title="Key Talking Points",
            content=talking_points,
            priority="high",
            confidence=0.9,
            source_analysis=source_analysis
        )
    
    def _generate_pricing_strategy(self, analysis_data: Dict[str, Any]) -> BattlecardSection:
        """Generate pricing strategy recommendations"""
        pricing_strategies = []
        source_analysis = []
        
        pricing_analysis = analysis_data.get('pricing_analysis', {})
        if pricing_analysis:
            currency = pricing_analysis.get('currency_detected', 'USD')
            software_model = pricing_analysis.get('software_pricing', {}).get('pricing_model', 'unknown')
            hidden_fees_risk = pricing_analysis.get('hidden_fees', {}).get('risk_level', 'unknown')
            
            # Base pricing strategy
            pricing_strategies.append(f"💰 **Currency Context**: Analysis shows competitor pricing in {currency}")
            pricing_strategies.append(f"📊 **Their Model**: {software_model.title()} pricing model")
            
            # Hidden fees strategy
            if hidden_fees_risk in ['medium', 'high']:
                pricing_strategies.append(f"⚠️ **Hidden Fees Risk**: {hidden_fees_risk.title()} risk of surprise costs")
                pricing_strategies.append(f"✅ **Our Advantage**: Emphasize transparent, all-inclusive pricing")
                source_analysis.append("Hidden fees analysis supports transparency positioning")
            
            # Hardware cost strategy
            hardware_pricing = pricing_analysis.get('hardware_pricing', {})
            if hardware_pricing.get('model_type') == 'proprietary':
                pricing_strategies.append(f"🔧 **Hardware Lock-in**: Competitor uses proprietary hardware")
                pricing_strategies.append(f"💡 **Position BYOD**: Highlight hardware flexibility and cost savings")
                source_analysis.append("Hardware model analysis supports flexibility messaging")
            
            # Software pricing strategy
            software_pricing = pricing_analysis.get('software_pricing', {})
            tier_breakdown = software_pricing.get('tier_breakdown', [])
            if tier_breakdown:
                pricing_strategies.append(f"📈 **Tier Analysis**: Competitor has {len(tier_breakdown)} pricing tiers")
                pricing_strategies.append(f"🎯 **Simplicity Advantage**: Position StoreHub's simpler pricing structure")
                source_analysis.append("Pricing tier analysis supports simplicity messaging")
        
        # Monetization strategy
        monetization_analysis = analysis_data.get('monetization_analysis', {})
        if monetization_analysis:
            revenue_streams = monetization_analysis.get('revenue_streams', {}).get('primary_streams', [])
            payment_stream = next((s for s in revenue_streams if s.get('type') == 'payment_processing'), None)
            
            if payment_stream:
                pricing_strategies.append(f"💳 **Payment Processing**: Competitor likely charges for payment processing")
                pricing_strategies.append(f"🔓 **Freedom Positioning**: Emphasize choice in payment processors")
                source_analysis.append("Revenue stream analysis reveals payment processing dependency")
        
        if not pricing_strategies:
            pricing_strategies.append("📊 **General Strategy**: Position StoreHub's transparent, local-market pricing")
            pricing_strategies.append("🏷️ **Value Focus**: Emphasize total cost of ownership vs. upfront costs")
        
        return BattlecardSection(
            title="Pricing Strategy",
            content=pricing_strategies,
            priority="high",
            confidence=0.8,
            source_analysis=source_analysis
        )
    
    def _generate_competitive_weaknesses(self, analysis_data: Dict[str, Any]) -> BattlecardSection:
        """Generate competitive weaknesses to exploit"""
        weaknesses = []
        source_analysis = []
        
        # Analyze pricing weaknesses
        pricing_analysis = analysis_data.get('pricing_analysis', {})
        if pricing_analysis:
            hidden_fees = pricing_analysis.get('hidden_fees', {})
            if hidden_fees.get('risk_level') in ['medium', 'high']:
                weaknesses.append(f"💸 **Hidden Costs**: {hidden_fees.get('risk_level').title()} risk of surprise fees")
                source_analysis.append("Pricing analysis revealed hidden fee risks")
            
            hardware_model = pricing_analysis.get('hardware_pricing', {}).get('model_type', '')
            if hardware_model == 'proprietary':
                weaknesses.append(f"🔒 **Hardware Lock-in**: Proprietary hardware limits flexibility")
                source_analysis.append("Hardware analysis shows proprietary system")
        
        # Analyze monetization weaknesses
        monetization_analysis = analysis_data.get('monetization_analysis', {})
        if monetization_analysis:
            lock_in_strength = monetization_analysis.get('lock_in_strategies', {}).get('lock_in_strength', '')
            if lock_in_strength == 'high':
                weaknesses.append(f"⛓️ **Vendor Lock-in**: High switching costs and dependency")
                source_analysis.append("Monetization analysis reveals high lock-in strategy")
        
        # Analyze customer complaints
        categorization_report = analysis_data.get('categorization_report', {})
        if categorization_report:
            overall_stats = categorization_report.get('overall_statistics', {})
            category_dist = overall_stats.get('category_distribution', {})
            
            # Top 3 complaint categories
            top_complaints = sorted(category_dist.items(), key=lambda x: x[1], reverse=True)[:3]
            for category, count in top_complaints:
                if count > 0:
                    category_clean = category.replace('_', ' ').title()
                    weaknesses.append(f"⚠️ **{category_clean} Issues**: {count} customer complaints in this area")
                    source_analysis.append(f"Customer complaint analysis: {count} {category} complaints")
        
        # Analyze social media weaknesses
        complaint_analysis = analysis_data.get('complaint_analysis', {})
        if complaint_analysis:
            platforms = complaint_analysis.get('platforms', {})
            total_complaints = complaint_analysis.get('total_complaints', 0)
            
            if total_complaints > 0:
                weaknesses.append(f"📱 **Social Media Complaints**: {total_complaints} complaints across platforms")
                source_analysis.append("Social media analysis reveals customer satisfaction issues")
        
        # If no specific weaknesses found, add general ones
        if not weaknesses:
            weaknesses.extend([
                "🌍 **Global vs Local**: May lack local market understanding",
                "🏢 **Size Disadvantage**: Large company may be slower to adapt",
                "💰 **Complex Pricing**: More complex pricing structure"
            ])
        
        return BattlecardSection(
            title="Competitive Weaknesses to Exploit",
            content=weaknesses,
            priority="medium",
            confidence=0.7,
            source_analysis=source_analysis
        )
    
    def _generate_sales_strategy(self, analysis_data: Dict[str, Any], positioning_analysis: Dict[str, Any]) -> BattlecardSection:
        """Generate sales strategy recommendations"""
        strategies = []
        source_analysis = []
        
        # Core sales strategy
        strategies.extend([
            "🎯 **Discovery First**: Understand their current pain points before positioning",
            "💡 **Value-Based Selling**: Focus on business outcomes, not just features",
            "🏆 **Differentiation**: Emphasize local expertise and transparent pricing",
            "📊 **ROI Focus**: Show clear return on investment and cost savings",
            "🤝 **Relationship Building**: Leverage local presence and support"
        ])
        
        # Strategy based on competitive analysis
        threat_level = self._assess_threat_level(positioning_analysis)
        
        if threat_level == 'high':
            strategies.append("⚡ **Aggressive Positioning**: This is a strong competitor - focus on clear differentiation")
            strategies.append("💰 **Total Cost Analysis**: Emphasize hidden costs and long-term value")
        elif threat_level == 'medium':
            strategies.append("⚖️ **Balanced Approach**: Acknowledge their strengths while highlighting ours")
            strategies.append("🎯 **Targeted Messaging**: Focus on specific areas where we excel")
        else:
            strategies.append("🎪 **Confident Positioning**: We have clear advantages - be confident")
            strategies.append("🚀 **Innovation Focus**: Emphasize our advanced features and roadmap")
        
        # Pricing strategy
        pricing_analysis = analysis_data.get('pricing_analysis', {})
        if pricing_analysis:
            if pricing_analysis.get('hidden_fees', {}).get('risk_level') in ['medium', 'high']:
                strategies.append("💸 **Cost Transparency**: Lead with transparent pricing discussion")
                source_analysis.append("Hidden fees analysis supports cost transparency strategy")
        
        # Monetization strategy
        monetization_analysis = analysis_data.get('monetization_analysis', {})
        if monetization_analysis:
            if monetization_analysis.get('lock_in_strategies', {}).get('lock_in_strength') == 'high':
                strategies.append("🔓 **Freedom Positioning**: Emphasize flexibility and no lock-in")
                source_analysis.append("Lock-in analysis supports freedom positioning")
        
        # Customer complaint strategy
        categorization_report = analysis_data.get('categorization_report', {})
        if categorization_report:
            overall_stats = categorization_report.get('overall_statistics', {})
            if overall_stats.get('total_complaints', 0) > 0:
                strategies.append("⚠️ **Address Known Issues**: Proactively address competitor weaknesses")
                source_analysis.append("Customer complaint analysis informs competitive positioning")
        
        return BattlecardSection(
            title="Sales Strategy",
            content=strategies,
            priority="high",
            confidence=0.85,
            source_analysis=source_analysis
        )
    
    def _generate_qualifying_questions(self, analysis_data: Dict[str, Any]) -> BattlecardSection:
        """Generate qualifying questions for sales conversations"""
        questions = []
        source_analysis = []
        
        # Core qualifying questions
        questions.extend([
            "🏢 **Business Context**: \"What's your current POS setup and what challenges are you facing?\"",
            "💰 **Budget Reality**: \"What's your budget range, and are you aware of all costs involved?\"",
            "🎯 **Decision Process**: \"Who else is involved in this decision?\"",
            "⏰ **Timeline**: \"When do you need this implemented?\"",
            "🔧 **Technical Requirements**: \"What integrations are critical for your business?\""
        ])
        
        # Questions based on competitive analysis
        pricing_analysis = analysis_data.get('pricing_analysis', {})
        if pricing_analysis:
            if pricing_analysis.get('hidden_fees', {}).get('risk_level') in ['medium', 'high']:
                questions.append("💸 **Hidden Costs**: \"Are you aware of all potential fees and charges?\"")
                source_analysis.append("Hidden fees analysis suggests cost transparency questions")
            
            hardware_model = pricing_analysis.get('hardware_pricing', {}).get('model_type', '')
            if hardware_model == 'proprietary':
                questions.append("🔧 **Hardware Flexibility**: \"How important is hardware choice flexibility to you?\"")
                source_analysis.append("Hardware analysis suggests flexibility questions")
        
        # Questions based on monetization analysis
        monetization_analysis = analysis_data.get('monetization_analysis', {})
        if monetization_analysis:
            if monetization_analysis.get('lock_in_strategies', {}).get('lock_in_strength') == 'high':
                questions.append("🔓 **Vendor Freedom**: \"How important is it to avoid being locked into one vendor?\"")
                source_analysis.append("Lock-in analysis suggests vendor freedom questions")
        
        # Questions based on customer complaints
        categorization_report = analysis_data.get('categorization_report', {})
        if categorization_report:
            overall_stats = categorization_report.get('overall_statistics', {})
            category_dist = overall_stats.get('category_distribution', {})
            
            if category_dist.get('Support', 0) > 0:
                questions.append("📞 **Support Expectations**: \"How important is responsive customer support to you?\"")
                source_analysis.append("Support complaints suggest support quality questions")
            
            if category_dist.get('Performance', 0) > 0:
                questions.append("⚡ **Performance Requirements**: \"How critical is system performance during peak hours?\"")
                source_analysis.append("Performance complaints suggest reliability questions")
        
        return BattlecardSection(
            title="Qualifying Questions",
            content=questions,
            priority="medium",
            confidence=0.8,
            source_analysis=source_analysis
        )
    
    def _generate_demo_focus_areas(self, analysis_data: Dict[str, Any], positioning_analysis: Dict[str, Any]) -> BattlecardSection:
        """Generate demo focus areas"""
        focus_areas = []
        source_analysis = []
        
        # Core demo areas
        focus_areas.extend([
            "🎯 **Local Features**: Show features specific to Southeast Asian market",
            "💰 **Transparent Pricing**: Demonstrate clear, upfront pricing structure",
            "🔧 **Hardware Flexibility**: Show BYOD and hardware options",
            "📊 **Integrated Analytics**: Demonstrate real-time reporting and insights",
            "🤝 **Support Experience**: Show local support and onboarding process"
        ])
        
        # Demo areas based on competitive weaknesses
        opportunities = positioning_analysis.get('opportunities', [])
        for opp in opportunities:
            if opp['area'] == 'pricing_transparency':
                focus_areas.append("💸 **No Hidden Fees**: Clearly show all-inclusive pricing")
                source_analysis.append("Pricing analysis reveals hidden fee opportunity")
            elif opp['area'] == 'hardware_flexibility':
                focus_areas.append("🔧 **BYOD Demo**: Show bringing own device capabilities")
                source_analysis.append("Hardware analysis reveals flexibility opportunity")
        
        # Demo areas based on customer complaints
        categorization_report = analysis_data.get('categorization_report', {})
        if categorization_report:
            overall_stats = categorization_report.get('overall_statistics', {})
            category_dist = overall_stats.get('category_distribution', {})
            
            top_complaint = max(category_dist.items(), key=lambda x: x[1]) if category_dist else None
            if top_complaint and top_complaint[1] > 0:
                category_name = top_complaint[0].replace('_', ' ').lower()
                focus_areas.append(f"✅ **{category_name.title()} Excellence**: Demo superior {category_name} capabilities")
                source_analysis.append(f"Customer complaints reveal {category_name} opportunity")
        
        # Vision-based demo areas
        vision_analysis = analysis_data.get('vision_analysis', {})
        if vision_analysis:
            upcoming_features = vision_analysis.get('product_roadmap', {}).get('upcoming_features', [])
            ai_features = [f for f in upcoming_features if 'ai' in f.get('feature', '').lower()]
            if ai_features:
                focus_areas.append("🤖 **AI Capabilities**: Show existing AI features vs their roadmap")
                source_analysis.append("Vision analysis reveals AI development opportunity")
        
        return BattlecardSection(
            title="Demo Focus Areas",
            content=focus_areas,
            priority="medium",
            confidence=0.75,
            source_analysis=source_analysis
        )
    
    def _generate_executive_summary(self, analysis_data: Dict[str, Any], positioning_analysis: Dict[str, Any]) -> str:
        """Generate executive summary for the battlecard"""
        competitor_name = analysis_data.get('competitor_name', 'Unknown')
        
        # Assess competitive strength
        opportunities = len(positioning_analysis.get('opportunities', []))
        threats = len(positioning_analysis.get('threats', []))
        
        if opportunities > threats:
            competitive_assessment = "favorable"
        elif threats > opportunities:
            competitive_assessment = "challenging"
        else:
            competitive_assessment = "balanced"
        
        # Generate summary based on key findings
        summary_parts = [
            f"{competitor_name} represents a {competitive_assessment} competitive scenario."
        ]
        
        # Add pricing insights
        pricing_analysis = analysis_data.get('pricing_analysis', {})
        if pricing_analysis:
            hidden_fees_risk = pricing_analysis.get('hidden_fees', {}).get('risk_level', '')
            if hidden_fees_risk in ['medium', 'high']:
                summary_parts.append(f"Their pricing model shows {hidden_fees_risk} hidden fee risks, creating transparency opportunities.")
        
        # Add customer satisfaction insights
        categorization_report = analysis_data.get('categorization_report', {})
        if categorization_report:
            total_complaints = categorization_report.get('overall_statistics', {}).get('total_complaints', 0)
            if total_complaints > 0:
                summary_parts.append(f"Customer feedback analysis reveals {total_complaints} complaints, indicating satisfaction gaps.")
        
        # Add strategic recommendation
        summary_parts.append("Focus on local expertise, transparent pricing, and superior customer support to win deals.")
        
        return " ".join(summary_parts)
    
    def _determine_competitive_position(self, positioning_analysis: Dict[str, Any]) -> str:
        """Determine overall competitive position"""
        opportunities = len(positioning_analysis.get('opportunities', []))
        threats = len(positioning_analysis.get('threats', []))
        
        if opportunities > threats * 2:
            return "Strong Advantage"
        elif opportunities > threats:
            return "Moderate Advantage"
        elif threats > opportunities:
            return "Competitive Challenge"
        else:
            return "Balanced Competition"
    
    def _assess_threat_level(self, positioning_analysis: Dict[str, Any]) -> str:
        """Assess threat level of competitor"""
        opportunities = len(positioning_analysis.get('opportunities', []))
        threats = len(positioning_analysis.get('threats', []))
        
        if threats > opportunities * 2:
            return "high"
        elif threats > opportunities:
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence_score(self, analysis_data: Dict[str, Any]) -> float:
        """Calculate overall confidence score based on data quality"""
        confidence_factors = []
        
        # Check data completeness
        if analysis_data.get('pricing_analysis'):
            confidence_factors.append(0.9)
        if analysis_data.get('monetization_analysis'):
            confidence_factors.append(0.85)
        if analysis_data.get('vision_analysis'):
            confidence_factors.append(0.8)
        if analysis_data.get('categorization_report'):
            confidence_factors.append(0.7)
        if analysis_data.get('complaint_analysis'):
            confidence_factors.append(0.75)
        
        # Calculate average confidence
        if confidence_factors:
            return sum(confidence_factors) / len(confidence_factors)
        else:
            return 0.5  # Default moderate confidence
    
    def _identify_data_sources(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Identify data sources used in analysis"""
        sources = []
        
        if analysis_data.get('pricing_analysis'):
            sources.append("Pricing Analysis")
        if analysis_data.get('monetization_analysis'):
            sources.append("Monetization Analysis")
        if analysis_data.get('vision_analysis'):
            sources.append("Vision & Roadmap Analysis")
        if analysis_data.get('categorization_report'):
            sources.append("Customer Complaints Analysis")
        if analysis_data.get('complaint_analysis'):
            sources.append("Social Media Analysis")
        if analysis_data.get('discovery_summary'):
            sources.append("Website Analysis")
        
        return sources
    
    def _assess_analysis_completeness(self, analysis_data: Dict[str, Any]) -> Dict[str, bool]:
        """Assess completeness of different analysis types"""
        return {
            'pricing_analysis': bool(analysis_data.get('pricing_analysis')),
            'monetization_analysis': bool(analysis_data.get('monetization_analysis')),
            'vision_analysis': bool(analysis_data.get('vision_analysis')),
            'customer_complaints': bool(analysis_data.get('categorization_report')),
            'social_media': bool(analysis_data.get('complaint_analysis')),
            'website_analysis': bool(analysis_data.get('discovery_summary'))
        }
    
    def export_battlecard_json(self, battlecard: SalesBattlecard) -> str:
        """Export battlecard as JSON"""
        return json.dumps(asdict(battlecard), indent=2, default=str)
    
    def export_battlecard_markdown(self, battlecard: SalesBattlecard) -> str:
        """Export battlecard as Markdown"""
        md_content = f"""# Sales Battlecard: {battlecard.competitor_name}

**Last Updated:** {battlecard.last_updated}  
**Competitive Position:** {battlecard.competitive_position}  
**Threat Level:** {battlecard.threat_level.upper()}  
**Confidence Score:** {battlecard.confidence_score:.2f}

## Executive Summary

{battlecard.executive_summary}

## {battlecard.positioning_advantages.title}

{chr(10).join(battlecard.positioning_advantages.content)}

## {battlecard.objection_handling.title}

{chr(10).join(battlecard.objection_handling.content)}

## {battlecard.talking_points.title}

{chr(10).join(battlecard.talking_points.content)}

## {battlecard.pricing_strategy.title}

{chr(10).join(battlecard.pricing_strategy.content)}

## {battlecard.competitive_weaknesses.title}

{chr(10).join(battlecard.competitive_weaknesses.content)}

## {battlecard.sales_strategy.title}

{chr(10).join(battlecard.sales_strategy.content)}

## {battlecard.qualifying_questions.title}

{chr(10).join(battlecard.qualifying_questions.content)}

## {battlecard.demo_focus_areas.title}

{chr(10).join(battlecard.demo_focus_areas.content)}

---

**Data Sources:** {', '.join(battlecard.data_sources)}  
**Analysis Completeness:** {sum(battlecard.analysis_completeness.values())}/{len(battlecard.analysis_completeness)} modules completed
"""
        return md_content 