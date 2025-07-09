#!/usr/bin/env python3
"""
Test script for export functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.export_manager import ExportManager
from datetime import datetime

def test_export_functionality():
    """Test the export functionality with sample data"""
    print("🧪 Testing Export Functionality")
    print("=" * 50)
    
    # Initialize export manager
    export_manager = ExportManager()
    
    # Check available formats
    available_formats = export_manager.get_available_formats()
    print(f"📋 Available export formats: {available_formats}")
    
    if not available_formats:
        print("⚠️  No export formats available.")
        print("💡 Install dependencies: pip install reportlab python-docx openpyxl")
        return False
    
    # Sample data for testing
    sample_data = {
        'competitor_name': 'Test Competitor',
        'competitor_url': 'https://example.com',
        'country': 'US',
        'selected_objective': '💰 Hardware & Software Pricing Analysis',
        'phase_config': {
            'phase1_enabled': True,
            'phase2_enabled': True,
            'phase3_enabled': True,
            'phase4_enabled': False,
            'phase5_enabled': False,
            'phase6_enabled': False
        },
        'discovery_summary': {
            'total_urls_found': 25,
            'strategies_used': 4,
            'success_rate': 85.5,
            'total_time': 12.3
        },
        'discovered_urls': {
            'pricing': ['https://example.com/pricing'],
            'features': ['https://example.com/features'],
            'blog': ['https://example.com/blog']
        },
        'analyzed_pages': [
            {
                'title': 'Test Page 1',
                'category': 'pricing',
                'url': 'https://example.com/pricing',
                'word_count': 500,
                'quality': {'completeness_score': 85.5},
                'meta_description': 'Test page description'
            }
        ],
        'pricing_analysis': {
            'currency_detected': 'USD',
            'hardware_pricing': {'model_type': 'proprietary'},
            'software_pricing': {'pricing_model': 'subscription'},
            'hidden_fees': {'risk_level': 'medium'}
        },
        'monetization_analysis': {
            'revenue_streams': {'revenue_model_type': 'saas'},
            'lock_in_strategies': {'lock_in_strength': 'medium'},
            'expansion_revenue': {'expansion_potential': 'high'}
        },
        'vision_analysis': {
            'product_roadmap': {'upcoming_features': [{'feature': 'AI Integration', 'confidence': 0.8}]},
            'technology_investments': {'investment_areas': [{'area': 'machine_learning', 'investment_level': 'high'}]},
            'market_expansion': {'geographic_targets': [{'region': 'APAC', 'probability': 'high'}]}
        }
    }
    
    # Test each available format
    for format_type in available_formats:
        print(f"\n🔍 Testing {format_type} export...")
        
        try:
            # Generate export
            buffer = export_manager.export_report(format_type, sample_data)
            
            # Check if buffer has content
            if buffer.getvalue():
                print(f"✅ {format_type} export successful - {len(buffer.getvalue())} bytes")
                
                # Generate filename
                filename = export_manager.get_export_filename(format_type, 'Test Competitor')
                print(f"📄 Generated filename: {filename}")
                
                # Optionally save to file for manual verification
                # with open(f"test_output_{filename}", 'wb') as f:
                #     f.write(buffer.getvalue())
                
            else:
                print(f"❌ {format_type} export failed - empty buffer")
                
        except Exception as e:
            print(f"❌ {format_type} export failed: {str(e)}")
    
    print("\n🎉 Export functionality test completed!")
    return True

if __name__ == "__main__":
    test_export_functionality() 