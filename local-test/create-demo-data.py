#!/usr/bin/env python3
"""
Create comprehensive demo data for Aura Desktop Assistant
Professional test data generation for hackathon demonstration
"""

import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

def create_demo_spreadsheet():
    """Create a realistic budget spreadsheet for demo"""
    print("📊 Creating demo spreadsheet...")
    
    # Realistic financial data
    data = {
        'Date': [
            '2024-01-01', '2024-01-15', '2024-02-01', '2024-02-15',
            '2024-03-01', '2024-03-15', '2024-04-01', '2024-04-15',
            '2024-05-01', '2024-05-15', '2024-06-01', '2024-06-15'
        ],
        'Category': [
            'Salary', 'Freelance', 'Salary', 'Consulting',
            'Salary', 'Investment', 'Salary', 'Bonus',
            'Salary', 'Side Project', 'Salary', 'Dividend'
        ],
        'Description': [
            'Monthly Salary - Software Engineer',
            'Web Development Project',
            'Monthly Salary - Software Engineer', 
            'AI Consulting Work',
            'Monthly Salary - Software Engineer',
            'Stock Portfolio Returns',
            'Monthly Salary - Software Engineer',
            'Performance Bonus Q1',
            'Monthly Salary - Software Engineer',
            'Mobile App Revenue',
            'Monthly Salary - Software Engineer',
            'Investment Dividend'
        ],
        'Amount': [
            6500, 2500, 6500, 3200,
            6500, 1800, 6500, 4000,
            6500, 1500, 6500, 800
        ],
        'Type': [
            'Income', 'Income', 'Income', 'Income',
            'Income', 'Income', 'Income', 'Income', 
            'Income', 'Income', 'Income', 'Income'
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Ensure directories exist
    docs_dir = Path('documents')
    docs_dir.mkdir(exist_ok=True)
    
    # Save as Excel and CSV
    excel_path = docs_dir / 'sample-budget.xlsx'
    csv_path = docs_dir / 'sample-budget.csv'
    
    df.to_excel(excel_path, index=False, sheet_name='Income')
    df.to_csv(csv_path, index=False)
    
    print(f"✅ Created: {excel_path}")
    print(f"✅ Created: {csv_path}")
    
    # Print summary
    total_income = df['Amount'].sum()
    avg_monthly = total_income / 6  # 6 months of data
    
    print(f"   📈 Total Income: ${total_income:,.2f}")
    print(f"   📊 Average Monthly: ${avg_monthly:,.2f}")
    print(f"   📋 Records: {len(df)} entries")

def create_demo_document():
    """Create a comprehensive project document"""
    print("📄 Creating demo document...")
    
    content = """# Aura Desktop Assistant - Technical Overview

## Executive Summary

Aura Desktop Assistant represents a paradigm shift in AI-powered productivity tools, combining cutting-edge artificial intelligence with uncompromising privacy protection. Built for the modern professional who demands both intelligence and data sovereignty, Aura delivers enterprise-grade functionality while ensuring all sensitive information remains under user control.

## Core Innovation

### Privacy-First Architecture
Unlike cloud-dependent assistants that transmit voice data to remote servers, Aura processes all voice commands locally using advanced on-device models. This approach eliminates privacy concerns while delivering comparable accuracy to cloud-based solutions.

### Intelligent Natural Language Processing
Aura's sophisticated NLP engine understands complex, multi-step commands and can execute intricate workflows through simple conversational interfaces. Users can request document creation, data analysis, and content generation using natural speech patterns.

### Desktop-Native Performance
Built with Tauri and Rust, Aura delivers native desktop performance that significantly outperforms browser-based alternatives. The application integrates seamlessly with the operating system, providing global shortcuts, system tray functionality, and always-available assistance.

## Technical Architecture

### Frontend Layer
- **Framework**: React 18 with TypeScript for type-safe development
- **State Management**: XState for robust workflow orchestration
- **UI Components**: Custom components with Tailwind CSS styling
- **Desktop Integration**: Tauri for native OS functionality

### Backend Services
- **API Framework**: FastAPI for high-performance REST endpoints
- **Data Processing**: Pandas and NumPy for spreadsheet analysis
- **Document Handling**: PyPDF2 and python-docx for file operations
- **AI Integration**: Local models with optional cloud enhancement

### Voice Processing Pipeline
- **Speech Recognition**: Vosk for offline processing, Whisper for accuracy
- **Intent Recognition**: Custom NLP models for command understanding
- **Response Generation**: Template-based and AI-powered responses
- **Audio Output**: Multiple TTS providers with quality optimization

## Key Capabilities

### File Operations
- Intelligent document creation with content generation
- Spreadsheet analysis and calculation automation
- PDF processing and content extraction
- Cross-format file conversion and manipulation

### Data Intelligence
- Automatic column detection in spreadsheets
- Statistical analysis and trend identification
- Data visualization and report generation
- Integration with popular data formats

### Workflow Automation
- Multi-step task execution from single commands
- Custom workflow creation and management
- Integration with external tools and services
- Scheduled task execution and monitoring

## Market Positioning

### Target Segments
- **Enterprise Users**: Organizations requiring data privacy compliance
- **Privacy-Conscious Professionals**: Users seeking alternatives to big tech solutions
- **Developers and Technical Users**: Power users wanting extensible automation
- **Content Creators**: Professionals needing intelligent document processing

### Competitive Advantages
1. **Privacy Leadership**: Local processing eliminates data privacy concerns
2. **Performance Excellence**: Native desktop performance vs. web limitations
3. **Extensibility**: Open architecture supporting custom integrations
4. **Cost Efficiency**: No per-user cloud costs or API limitations

## Implementation Quality

### Code Excellence
- Comprehensive TypeScript coverage with strict type checking
- Extensive test suites covering unit, integration, and E2E scenarios
- Professional CI/CD pipeline with automated quality gates
- Security-first development with threat modeling and validation

### User Experience
- Intuitive voice interface with visual feedback
- Responsive design adapting to different screen sizes
- Accessibility compliance with WCAG 2.1 guidelines
- Professional polish in every interaction detail

### Security Framework
- Input validation and sanitization at all entry points
- Path traversal protection for file operations
- Encrypted storage for sensitive configuration data
- Regular security audits and vulnerability assessments

## Future Roadmap

### Phase 1: Enhanced Intelligence
- Advanced NLP models with improved accuracy
- Multi-language support for global deployment
- Custom model training for domain-specific tasks
- Enhanced context awareness and memory

### Phase 2: Enterprise Features
- Team collaboration and shared workflows
- Advanced security controls and audit logging
- Custom deployment options and white-labeling
- Integration marketplace and plugin ecosystem

### Phase 3: Platform Expansion
- Mobile companion applications
- Web-based management interface
- Cloud synchronization with privacy controls
- API ecosystem for third-party integrations

## Conclusion

Aura Desktop Assistant demonstrates that privacy and functionality are not mutually exclusive. By combining innovative local processing with professional-grade engineering, Aura delivers a compelling alternative to cloud-dependent solutions while maintaining the intelligence and convenience users expect from modern AI assistants.

The project represents not just technical achievement, but a vision for the future of human-computer interaction where privacy, performance, and intelligence converge to create truly empowering productivity tools.

---

*This document was generated as part of the Aura Desktop Assistant demonstration. For technical details, API documentation, and implementation guides, please refer to the comprehensive project repository.*"""
    
    docs_dir = Path('documents')
    docs_dir.mkdir(exist_ok=True)
    
    doc_path = docs_dir / 'aura-technical-overview.md'
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created: {doc_path}")
    print(f"   📝 {len(content.split())} words")
    print(f"   📄 {len(content.split('.'))} sentences")

def create_test_configuration():
    """Create test configuration files"""
    print("⚙️ Creating test configuration...")
    
    # Create data directory
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Test configuration
    test_config = {
        "test_scenarios": [
            {
                "name": "File Creation Test",
                "command": "Create a meeting notes document titled 'Test Meeting' and write 'This is a test document created by Aura'",
                "expected_file": "documents/Test Meeting.txt",
                "expected_content": "This is a test document created by Aura"
            },
            {
                "name": "Spreadsheet Analysis Test", 
                "command": "Analyze my sample budget spreadsheet and calculate the total income",
                "expected_result": "Total income calculation from sample-budget.csv"
            },
            {
                "name": "Document Summary Test",
                "command": "Summarize the technical overview document in three bullet points",
                "expected_result": "Three coherent bullet points about Aura"
            }
        ],
        "performance_benchmarks": {
            "voice_recognition_ms": 1000,
            "intent_parsing_ms": 500,
            "file_operation_ms": 200,
            "api_response_ms": 100
        },
        "quality_metrics": {
            "accuracy_threshold": 0.95,
            "response_time_p95": 2000,
            "ui_fps_target": 60,
            "memory_usage_mb_max": 512
        }
    }
    
    config_path = data_dir / 'test-config.json'
    with open(config_path, 'w') as f:
        json.dump(test_config, f, indent=2)
    
    print(f"✅ Created: {config_path}")

def create_presentation_data():
    """Create data optimized for presentations"""
    print("🎪 Creating presentation data...")
    
    # Create a simple, impressive spreadsheet for demos
    demo_data = {
        'Quarter': ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024'],
        'Revenue': [125000, 142000, 158000, 175000],
        'Expenses': [85000, 92000, 98000, 105000],
        'Profit': [40000, 50000, 60000, 70000],
        'Growth': ['15%', '18%', '22%', '25%']
    }
    
    df = pd.DataFrame(demo_data)
    
    docs_dir = Path('documents')
    demo_path = docs_dir / 'quarterly-results.xlsx'
    df.to_excel(demo_path, index=False, sheet_name='Results')
    
    print(f"✅ Created: {demo_path}")
    print(f"   📊 Total Revenue: ${df['Revenue'].sum():,}")
    print(f"   💰 Total Profit: ${df['Profit'].sum():,}")

def main():
    """Create all demo data"""
    print("🚀 Aura Desktop Assistant - Demo Data Creation")
    print("=" * 50)
    
    try:
        create_demo_spreadsheet()
        create_demo_document()
        create_test_configuration()
        create_presentation_data()
        
        print("\n" + "=" * 50)
        print("🎉 Demo data creation complete!")
        print("\n📁 Created files:")
        print("   📊 documents/sample-budget.xlsx - Comprehensive financial data")
        print("   📊 documents/quarterly-results.xlsx - Presentation-ready data")
        print("   📄 documents/aura-technical-overview.md - Detailed project documentation")
        print("   ⚙️ data/test-config.json - Test configuration and benchmarks")
        print("\n🎯 Ready for comprehensive testing and demonstration!")
        
    except Exception as e:
        print(f"\n❌ Error creating demo data: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)