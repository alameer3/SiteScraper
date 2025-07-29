# Website Analyzer

## Overview

This is a Flask-based web application that provides comprehensive website analysis and extraction capabilities. The application is designed as a unified platform for deep website analysis, content extraction, and intelligent replication using advanced tools and AI-powered features.

**Key Features:**
- **Unified Website Extraction**: Multiple extraction modes (basic, standard, advanced, complete, ultra)
- **Advanced Analysis Tools**: CMS detection, security scanning, sitemap generation, screenshot capture
- **AI-Powered Analysis**: Content categorization, sentiment analysis, pattern recognition
- **Comprehensive Reporting**: Multi-format exports (JSON, CSV, HTML, PDF, Word)
- **Website Cloning**: Intelligent website replication with complete functionality preservation

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a Flask-based web architecture with modular components for different analysis and extraction capabilities.

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL (production) / SQLite (development) via configurable DATABASE_URL
- **Session Management**: Flask sessions with proxy fix for deployment
- **Background Processing**: Threading for long-running extraction tasks
- **Error Handling**: Comprehensive try-catch blocks with fallback mechanisms

### Frontend Architecture
- **Template Engine**: Jinja2 with Bootstrap 5 RTL for Arabic interface
- **Styling**: Glass morphism design with gradient backgrounds
- **Icons**: Feather Icons for consistent UI elements
- **JavaScript**: Vanilla JS for form handling and progress tracking

## Key Components

### Core Extraction Engine
1. **UnifiedWebsiteExtractor** (`unified_extractor.py`):
   - Main extraction orchestrator with 5 extraction modes
   - Content extraction, asset downloading, and analysis coordination
   - Fallback mechanisms for missing advanced tools
   - Organized file structure creation (01_content, 02_assets, 03_analysis, etc.)

2. **Advanced Tools Manager** (`advanced_tools_manager.py`):
   - Coordinates specialized analysis tools
   - CMS detection, security scanning, sitemap generation
   - Screenshot capture and website previews
   - Comprehensive reporting system

3. **Website Cloner Pro** (`tools_pro/website_cloner_pro.py`):
   - Advanced website replication capabilities
   - Complete functionality preservation
   - AI-powered analysis and pattern recognition
   - Database structure extraction

### Analysis Components
1. **CMS Detector** (`cms_detector.py`):
   - Detects 15+ content management systems
   - JavaScript framework identification
   - Technology stack analysis

2. **Security Scanner** (`security_scanner.py`):
   - SSL/TLS certificate validation
   - HTTP security headers analysis
   - Vulnerability scanning (XSS, CSRF, SQL injection)

3. **AI Analysis Engine** (`tools_pro/ai/`):
   - Content categorization and sentiment analysis
   - Pattern recognition for design and code patterns
   - Quality assurance for replicated sites

### File Management
1. **File Organizer** (`file_organizer.py`):
   - Structured organization of extracted content
   - Automatic folder creation and file categorization
   - Archive management and compression

2. **File Manager API** (`file_manager_api.py`):
   - RESTful API for file operations
   - Storage statistics and management
   - Bulk operations and cleanup utilities

## Data Flow

1. **Input**: User provides URL and selects extraction type
2. **Processing**: 
   - URL validation and preprocessing
   - Content extraction using BeautifulSoup/requests
   - Advanced tools execution (if available)
   - AI analysis and pattern recognition
3. **Storage**: 
   - Organized file structure creation
   - Database record creation (PostgreSQL/SQLite)
   - Asset downloading and organization
4. **Output**: 
   - Multi-format reports (HTML, JSON, PDF)
   - Extractable archives
   - Comprehensive analysis dashboards

## External Dependencies

### Core Dependencies
- **Flask**: Web framework with SQLAlchemy ORM
- **Requests**: HTTP client with retry mechanisms
- **BeautifulSoup4**: HTML parsing and content extraction
- **Pathlib**: File system operations

### Optional Advanced Dependencies
- **Playwright/Selenium**: JavaScript-heavy site rendering (optional)
- **OpenAI/AI Libraries**: Advanced content analysis (optional)
- **PIL/Pillow**: Image processing for screenshots (optional)

### Database
- **PostgreSQL**: Primary production database
- **SQLite**: Development and fallback database

## Deployment Strategy

### Development Environment
- **Local Flask server**: `python app.py` or `python main.py`
- **Database**: SQLite with automatic migration
- **Debug mode**: Enabled for development

### Production Environment
- **WSGI Server**: Gunicorn recommended
- **Database**: PostgreSQL via DATABASE_URL environment variable
- **Proxy Configuration**: ProxyFix middleware configured for reverse proxy deployment
- **Environment Variables**: 
  - `DATABASE_URL`: Database connection string
  - `SESSION_SECRET`: Session encryption key

### File Storage
- **Local Storage**: `extracted_files/` directory structure
- **Backup System**: Automatic archiving in `backup_old_project/`
- **Organization**: Tool-specific subdirectories for different extraction types

The application is designed to handle both simple website analysis tasks and complex extraction scenarios with graceful degradation when advanced tools are unavailable.