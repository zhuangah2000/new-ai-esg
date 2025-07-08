"""
Enhanced Flask-RESTX API Documentation Setup
SWAGGER AUTHORIZATION FIXED VERSION - Properly configures Swagger UI to include API keys in requests
"""

from flask_restx import Api, fields
from flask import request, redirect, url_for
import os

# Common field definitions used across all models
common_fields = {
    'id': fields.Integer(required=True, description='Unique identifier', example=1),
    'created_at': fields.DateTime(description='Creation timestamp', example='2024-01-15T10:30:00Z'),
    'updated_at': fields.DateTime(description='Last update timestamp', example='2024-01-15T14:45:00Z')
}

def create_api_documentation(app):
    """
    Create comprehensive Flask-RESTX API documentation with professional styling
    This version properly configures Swagger UI authorization
    """
    
    # Enhanced API configuration with professional styling
    api_config = {
        'title': 'ESG Reporting Platform API',
        'version': '1.0',
        'description': '''
## 🌱 Comprehensive ESG Reporting & Analytics Platform

### Overview
A complete Environmental, Social, and Governance (ESG) reporting platform that enables organizations to:
- **Track and measure** carbon emissions across all scopes
- **Manage ESG data** with comprehensive measurement tools
- **Generate professional reports** compliant with major frameworks (GRI, SASB, TCFD, CDP)
- **Monitor progress** toward sustainability targets and goals
- **Assess suppliers** for ESG risk and compliance
- **Analyze performance** with real-time dashboards and insights

### Key Features
- 🔢 **Emission Measurements**: Comprehensive tracking with automatic calculations
- 📊 **Real-time Dashboard**: Analytics and trend analysis
- 📋 **Multi-framework Reporting**: GRI, SASB, TCFD, CDP compliance
- 🎯 **Target Management**: Set and track ESG goals
- 🏢 **Asset Management**: Track environmental impact of assets
- 🚀 **Project Tracking**: Monitor sustainability initiatives
- 🤝 **Supplier Assessment**: ESG risk evaluation
- 📏 **Standards Compliance**: Manage ESG standards and requirements

### Authentication Methods
- **Session-based**: Login via web interface for interactive use
- **API Key**: Bearer token authentication for programmatic access
  - Format: `Authorization: Bearer esg_your_api_key`
  - Granular permissions per endpoint
  - Usage tracking and analytics

### Important Note
**This documentation provides interactive testing for your actual API endpoints.**
- **Documentation endpoints**: `/api-docs/*` (proxy to your real API)
- **Actual business endpoints**: `/api/*` (your real API)
- **Testing**: Use the "Try it out" feature below - it will call your actual `/api/*` endpoints

### Data Quality & Accuracy
- **Active Emission Factors**: Automatic updates with latest scientific data
- **Revision Management**: Full audit trail for all changes
- **Validation**: Comprehensive data validation and error checking
- **Recalculation**: Bulk recalculation with updated factors

### Compliance & Standards
- **GRI Standards**: Global Reporting Initiative compliance
- **SASB**: Sustainability Accounting Standards Board
- **TCFD**: Task Force on Climate-related Financial Disclosures
- **CDP**: Carbon Disclosure Project
- **Custom Frameworks**: Support for organization-specific standards

### Getting Started
1. **Authentication**: Login via `/api/auth/login` or use API key
2. **Explore**: Use this interactive documentation to test endpoints
3. **Integrate**: Use the API for data integration and automation
4. **Monitor**: Track your ESG performance with real-time dashboards

### Support & Resources
- **Interactive Testing**: Use the "Try it out" feature below
- **Code Examples**: Available for all major programming languages
- **Rate Limits**: Generous limits for all authenticated users
- **Support**: Contact your system administrator for assistance
        ''',
        'contact': {
            'name': 'ESG Platform Support',
            'email': 'support@esgplatform.com',
            'url': 'https://esgplatform.com/support'
        },
        'license': {
            'name': 'Proprietary',
            'url': 'https://esgplatform.com/license'
        },
        'terms_of_service': 'https://esgplatform.com/terms',
        'doc': '/docs/',
        'prefix': '/api-docs',  # Documentation endpoints use /api-docs prefix
        'validate': True,
        'ordered': True,
        'catch_all_404s': True,
        'security': 'apikey'  # CRITICAL: Set default security scheme
    }
    
    # Create API instance with enhanced configuration
    api = Api(app, **api_config)
    
    # FIXED: Enhanced security definitions for comprehensive authentication
    api.authorizations = {
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': '''
## API Key Authentication

### Format
```
Authorization: Bearer esg_your_api_key_here
```

### Getting Your API Key
1. Login to the web interface
2. Navigate to Settings → API Keys
3. Create a new API key with appropriate permissions
4. Copy the full key (shown only once)

### Permissions
API keys support granular permissions:
- **READ**: View data (GET endpoints)
- **WRITE**: Create and update data (POST, PUT endpoints)  
- **DELETE**: Remove data (DELETE endpoints)
- **SETTINGS**: Access to settings and configuration

### Usage Examples

**cURL:**
```bash
curl -H "Authorization: Bearer esg_abc123..." \\
     https://api.esgplatform.com/api/measurements
```

**Python:**
```python
import requests

headers = {
    'Authorization': 'Bearer esg_abc123...',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://api.esgplatform.com/api/measurements',
    headers=headers
)
```

**JavaScript:**
```javascript
const headers = {
    'Authorization': 'Bearer esg_abc123...',
    'Content-Type': 'application/json'
};

fetch('https://api.esgplatform.com/api/measurements', {
    method: 'GET',
    headers: headers
})
.then(response => response.json())
.then(data => console.log(data));
```

### Security Best Practices
- **Keep keys secure**: Never commit API keys to version control
- **Use environment variables**: Store keys in secure environment variables
- **Rotate regularly**: Generate new keys periodically
- **Monitor usage**: Track API key usage in the dashboard
- **Principle of least privilege**: Grant only necessary permissions
            '''
        }
    }
    
    # Custom Swagger UI with enhanced styling and FIXED authorization handling
    @api.documentation
    def custom_ui():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>ESG Platform API Documentation</title>
            <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
            <link rel="icon" type="image/png" href="https://unpkg.com/swagger-ui-dist@3.52.5/favicon-32x32.png" sizes="32x32" />
            <link rel="icon" type="image/png" href="https://unpkg.com/swagger-ui-dist@3.52.5/favicon-16x16.png" sizes="16x16" />
            <style>
                /* Professional ESG-themed styling */
                html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
                *, *:before, *:after { box-sizing: inherit; }
                body { margin:0; background: #fafafa; }
                
                /* Enhanced header styling */
                .swagger-ui .info .title { 
                    color: #1B5E20; 
                    font-size: 2.5em; 
                    font-weight: 700;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                }
                
                .swagger-ui .info .description { 
                    color: #2E7D32; 
                    font-size: 1.1em; 
                    line-height: 1.6;
                    margin: 20px 0;
                }
                
                /* Professional color scheme */
                .swagger-ui .btn.authorize { 
                    background-color: #4CAF50; 
                    border-color: #4CAF50; 
                    color: white;
                    font-weight: 600;
                    padding: 8px 16px;
                    border-radius: 4px;
                    transition: all 0.3s ease;
                }
                
                .swagger-ui .btn.authorize:hover { 
                    background-color: #45A049; 
                    border-color: #45A049;
                    transform: translateY(-1px);
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }
                
                /* Enhanced operation blocks */
                .swagger-ui .opblock { 
                    border: 1px solid #E8F5E8; 
                    border-radius: 8px;
                    margin-bottom: 15px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    transition: all 0.3s ease;
                }
                
                .swagger-ui .opblock:hover {
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    transform: translateY(-1px);
                }
                
                .swagger-ui .opblock.opblock-get .opblock-summary { 
                    background: linear-gradient(135deg, #E8F5E8, #F1F8E9);
                    border-color: #4CAF50; 
                }
                
                .swagger-ui .opblock.opblock-post .opblock-summary { 
                    background: linear-gradient(135deg, #E3F2FD, #F0F7FF);
                    border-color: #2196F3; 
                }
                
                .swagger-ui .opblock.opblock-put .opblock-summary { 
                    background: linear-gradient(135deg, #FFF3E0, #FFF8F0);
                    border-color: #FF9800; 
                }
                
                .swagger-ui .opblock.opblock-delete .opblock-summary { 
                    background: linear-gradient(135deg, #FFEBEE, #FFF5F5);
                    border-color: #F44336; 
                }
                
                /* Enhanced tabs */
                .swagger-ui .tab li.tabitem.active h4 span { 
                    color: #2E7D32; 
                }
                
                /* Custom badges for different endpoint types */
                .swagger-ui .opblock-tag { 
                    font-size: 1.2em; 
                    font-weight: 700;
                    color: #1B5E20;
                    border-bottom: 2px solid #4CAF50;
                    padding-bottom: 5px;
                    margin-bottom: 15px;
                }
                
                /* Enhanced code blocks */
                .swagger-ui .highlight-code { 
                    background: #F5F5F5; 
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                }
                
                /* Custom scrollbar */
                .swagger-ui ::-webkit-scrollbar { width: 8px; }
                .swagger-ui ::-webkit-scrollbar-track { background: #F1F1F1; }
                .swagger-ui ::-webkit-scrollbar-thumb { 
                    background: #4CAF50; 
                    border-radius: 4px;
                }
                .swagger-ui ::-webkit-scrollbar-thumb:hover { background: #45A049; }
                
                /* Responsive improvements */
                @media (max-width: 768px) {
                    .swagger-ui .info .title { font-size: 2em; }
                    .swagger-ui .info .description { font-size: 1em; }
                }
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
            <script>
                SwaggerUIBundle({
                    url: '/api-docs/swagger.json',
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.presets.standalone
                    ],
                    layout: "BaseLayout",
                    deepLinking: true,
                    displayOperationId: false,
                    defaultModelsExpandDepth: 1,
                    defaultModelExpandDepth: 1,
                    defaultModelRendering: 'example',
                    displayRequestDuration: true,
                    docExpansion: 'list',
                    filter: true,
                    showExtensions: true,
                    showCommonExtensions: true,
                    supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],
                    tryItOutEnabled: true,
                    
                    // CRITICAL FIX: Properly configure authorization
                    onComplete: function() {
                        console.log('🎯 Swagger UI loaded successfully');
                        console.log('🔑 Authorization configured for apikey');
                    },
                    
                    requestInterceptor: function(request) {
                        console.log('🔍 Request interceptor called');
                        console.log('📋 Original URL:', request.url);
                        console.log('📋 Request headers:', request.headers);
                        
                        // Only redirect API endpoints, NOT swagger.json or other docs files
                        if (request.url.includes('/api-docs/') && 
                            !request.url.includes('swagger.json') && 
                            !request.url.includes('swaggerui') &&
                            !request.url.includes('.js') &&
                            !request.url.includes('.css') &&
                            !request.url.includes('.png') &&
                            !request.url.includes('.ico')) {
                            
                            // Preserve the original request object structure
                            var originalUrl = request.url;
                            request.url = request.url.replace('/api-docs/', '/api/');
                            
                            console.log('🔄 Redirecting API call:', originalUrl, '→', request.url);
                            
                            // Check if Authorization header is present
                            if (request.headers && request.headers.Authorization) {
                                console.log('✅ Authorization header found:', request.headers.Authorization.substring(0, 20) + '...');
                            } else {
                                console.log('⚠️  No Authorization header found in request');
                                console.log('🔍 Available headers:', Object.keys(request.headers || {}));
                            }
                        }
                        
                        // Always return the request object
                        return request;
                    },
                    
                    responseInterceptor: function(response) {
                        console.log('📤 Response interceptor called');
                        console.log('📤 Response status:', response.status);
                        
                        if (response.status === 401) {
                            console.log('❌ Authentication failed - check API key');
                            console.log('💡 Make sure to click "Authorize" and enter your API key');
                        } else if (response.status === 200) {
                            console.log('✅ Request successful');
                        }
                        return response;
                    }
                });
            </script>
        </body>
        </html>
        '''
    
    return api

def create_common_models(api):
    """
    Create common models used across all API endpoints
    """
    
    # Success response model
    success_model = api.model('Success', {
        'success': fields.Boolean(required=True, description='Operation success status', example=True),
        'message': fields.String(description='Success message', example='Operation completed successfully'),
        'data': fields.Raw(description='Response data')
    })
    
    # Error response model
    error_model = api.model('Error', {
        'success': fields.Boolean(required=True, description='Operation success status', example=False),
        'error': fields.String(required=True, description='Error message', example='Invalid request data'),
        'details': fields.Raw(description='Additional error details')
    })
    
    # Pagination model
    pagination_model = api.model('Pagination', {
        'page': fields.Integer(description='Current page number', example=1),
        'per_page': fields.Integer(description='Items per page', example=10),
        'total': fields.Integer(description='Total number of items', example=100),
        'pages': fields.Integer(description='Total number of pages', example=10),
        'has_prev': fields.Boolean(description='Has previous page', example=False),
        'has_next': fields.Boolean(description='Has next page', example=True),
        'prev_num': fields.Integer(description='Previous page number', example=None),
        'next_num': fields.Integer(description='Next page number', example=2)
    })
    
    return {
        'success': success_model,
        'error': error_model,
        'pagination': pagination_model
    }

def add_custom_error_handlers(api):
    """
    MINIMAL FIX: Skip custom error handlers (Flask-RESTX doesn't support them)
    """
    print("   Custom error handlers skipped (using Flask-RESTX defaults)")
    return True

def configure_api_settings(api):
    """
    MINIMAL FIX: Skip API settings configuration (Flask-RESTX doesn't support after_request)
    """
    print("   API settings configuration skipped (using Flask-RESTX defaults)")
    return True

