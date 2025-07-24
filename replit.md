# Website Analyzer

## Overview

This is a Flask-based web application that provides comprehensive website analysis capabilities. The application allows users to input a URL and receive detailed insights about the website's structure, technology stack, SEO optimization, and navigation patterns. It combines web scraping, content analysis, and technology detection to provide actionable intelligence for understanding and potentially replicating website architectures.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a traditional Flask MVC architecture with the following key characteristics:

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite for development (configurable to other databases via DATABASE_URL environment variable)
- **Threading**: Background processing for website analysis to prevent UI blocking
- **Session Management**: Flask sessions with configurable secret keys

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme
- **Styling**: Custom CSS with Bootstrap integration
- **JavaScript**: Vanilla JavaScript for form validation and progress tracking
- **Icons**: Feather Icons for consistent UI elements
- **Visualization**: Chart.js for analytics display

## Key Components

### Core Analysis Engine
1. **WebScraper Class** (`scraper.py`):
   - Implements respectful crawling with robots.txt compliance
   - Configurable crawl depth and delay settings
   - Session-based HTTP requests with proper user agent headers
   - URL validation and domain boundary enforcement

2. **WebsiteAnalyzer Class** (`analyzer.py`):
   - Technology stack detection using pattern matching
   - CMS identification (WordPress, Drupal, Joomla, etc.)
   - Framework detection (React, Vue, Angular, jQuery, etc.)
   - Optional builtwith library integration for enhanced detection

3. **Database Models** (`models.py`):
   - ScrapeResult model with JSON storage for analysis data
   - Structured data storage for different analysis categories
   - Status tracking for async operations

### Data Categories
The system analyzes and stores five main categories of website data:
- **Structure Data**: HTML structure and semantic analysis
- **Assets Data**: Images, CSS, JavaScript files inventory
- **Technology Data**: Framework, library, and CMS detection
- **SEO Data**: Meta tags, titles, optimization metrics
- **Navigation Data**: Site structure and link analysis

## Data Flow

1. **User Input**: URL submission through web interface with validation
2. **Background Processing**: Threaded analysis to maintain UI responsiveness
3. **Web Scraping**: Respectful crawling with configurable depth limits
4. **Content Analysis**: Multi-faceted analysis of scraped content
5. **Data Storage**: JSON serialization of analysis results in SQLite
6. **Results Display**: Dynamic rendering of analysis results with visualizations

## External Dependencies

### Python Libraries
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **BeautifulSoup4**: HTML parsing and content extraction
- **Requests**: HTTP client for web scraping
- **builtwith** (optional): Enhanced technology detection

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme
- **Chart.js**: Data visualization and analytics charts
- **Feather Icons**: Consistent iconography

### Development Tools
- **Werkzeug ProxyFix**: Production deployment middleware
- **Python logging**: Comprehensive error tracking and debugging

## Deployment Strategy

### Environment Configuration
- **Database**: Environment-configurable DATABASE_URL (defaults to SQLite)
- **Security**: SESSION_SECRET environment variable for production
- **Proxy Support**: ProxyFix middleware for reverse proxy deployments

### Production Considerations
- **Database Migration**: Automatic table creation on startup
- **Error Handling**: Comprehensive logging and user-friendly error messages
- **Performance**: Connection pooling and database pre-ping enabled
- **Security**: Configurable session secrets and proxy-aware deployment

### Scalability Features
- **Background Processing**: Non-blocking analysis operations
- **Database Abstraction**: Easy migration to PostgreSQL or other databases
- **Modular Architecture**: Separate concerns for easy horizontal scaling
- **Session Management**: Stateless design for load balancer compatibility

## Recent Changes (July 24, 2025)

### Added Advanced Ad Blocking System
- **New Feature**: Comprehensive advertisement filtering system
- **AdBlocker Module**: Created dedicated `ad_blocker.py` with intelligent ad detection
- **Filtering Capabilities**: 
  - Removes common ad containers and promotional content
  - Filters ad networks (Google Ads, Facebook, Amazon, etc.)
  - Blocks tracking scripts and analytics
  - Cleans promotional text content
- **User Control**: Added toggle switch in analysis form to enable/disable ad blocking
- **Statistics**: Real-time reporting of blocked advertisements and filtering effectiveness
- **Clean Results**: Provides cleaner, more focused website analysis without advertising clutter

### Technical Implementation
- **Smart Detection**: Uses CSS selectors, domain patterns, and content analysis
- **Performance**: Filters assets and content during crawling process
- **Statistics**: Tracks and reports blocking effectiveness in analysis results
- **User Interface**: Added shield icon and ad blocking statistics in results view

The application is designed to be both development-friendly with SQLite defaults and production-ready with environment-based configuration for database connections and security settings.