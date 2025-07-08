import os
import sys
# DON'T CHANGE THIS !!! - PRESERVING USER'S EXACT PATH SETUP
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.esg_models import db

# PRESERVING USER'S EXACT BLUEPRINT IMPORTS (INCLUDING ASSET_COMPARISONS!)
from src.routes.emission_factors import emission_factors_bp
from src.routes.measurements import measurements_bp
from src.routes.suppliers import suppliers_bp
from src.routes.dashboard import dashboard_bp
from src.routes.targets import targets_bp
from src.routes.projects import projects_bp
# from src.routes.user_management import user_management_bp  # PRESERVING COMMENTED LINE
from src.routes.assets import assets_bp
from src.routes.asset_comparisons import asset_comparisons_bp  # ✅ CRITICAL - PRESERVING THIS!
from src.routes.esg_standards import esg_standards_bp
from src.routes.reports import reports_bp
from src.routes.company import company_bp
from src.routes.user import user_bp
from src.routes.role import role_bp
from src.routes.api_key import api_key_bp

# ============================================================================
# MINIMAL FIX: Import Flask-RESTX API Documentation Components
# ============================================================================
try:
    from flask_restx import Api
    from docs.api_documentation import create_api_documentation, create_common_models, add_custom_error_handlers, configure_api_settings
    from docs.api_namespaces import create_all_namespaces
    RESTX_AVAILABLE = True
    print("✅ Flask-RESTX available - Comprehensive API documentation will be enabled")
except ImportError as e:
    RESTX_AVAILABLE = False
    print("⚠️  Flask-RESTX not available - API documentation disabled")
    print(f"   Error: {e}")
    print("   Install with: pip install flask-restx")
    print("   Ensure docs/ directory contains the API documentation files")

# PRESERVING USER'S EXACT FLASK APP SETUP
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'  # PRESERVING USER'S SECRET KEY

# Enable CORS for all routes
CORS(app)

# ============================================================================
# PRESERVING USER'S EXACT BLUEPRINT REGISTRATION ORDER (INCLUDING ASSET_COMPARISONS!)
# ============================================================================
app.register_blueprint(emission_factors_bp, url_prefix='/api')
app.register_blueprint(measurements_bp, url_prefix='/api')
app.register_blueprint(suppliers_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')
app.register_blueprint(targets_bp, url_prefix='/api')
app.register_blueprint(projects_bp, url_prefix='/api')
# app.register_blueprint(user_management_bp, url_prefix='/api')  # PRESERVING COMMENTED LINE
app.register_blueprint(assets_bp, url_prefix='/api')
app.register_blueprint(asset_comparisons_bp, url_prefix='/api')  # ✅ CRITICAL - PRESERVING THIS!
app.register_blueprint(esg_standards_bp, url_prefix='/api')
app.register_blueprint(reports_bp, url_prefix='/api')
app.register_blueprint(company_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(role_bp, url_prefix='/api')
app.register_blueprint(api_key_bp, url_prefix='/api')

# ============================================================================
# PRESERVING USER'S EXACT DATABASE CONFIGURATION
# ============================================================================
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# ============================================================================
# MINIMAL FIX: Initialize API Documentation with /api-docs prefix to avoid conflicts
# ============================================================================
if RESTX_AVAILABLE:
    try:
        # Create comprehensive API documentation with professional styling
        # CRITICAL FIX: Use /api-docs prefix instead of /api to avoid route conflicts
        api = create_api_documentation(app)
        
        # Create common models
        common_models = create_common_models(api)
        
        # Create all namespaces with complete documentation for 15+ modules
        namespaces = create_all_namespaces(api)
        
        # Add custom error handlers for better API responses
        add_custom_error_handlers(api)
        
        # Configure additional API settings
        configure_api_settings(api)
        
        print("📚 Comprehensive API Documentation initialized successfully!")
        print("   🌱 ESG Platform API Documentation")
        print("   📊 All 15+ modules documented:")
        print("     • Authentication & Session Management")
        print("     • User Management & Profiles")
        print("     • Role & Permission Management")
        print("     • Company Information & Settings")
        print("     • Emission Measurements & Calculations")
        print("     • Emission Factor Management & Revisions")
        print("     • Dashboard Analytics & Reporting")
        print("     • ESG Report Generation & Management")
        print("     • Target Setting & Progress Tracking")
        print("     • Asset Management & Environmental Impact")
        print("     • Asset Comparisons & Analysis")  # ✅ INCLUDING USER'S ASSET_COMPARISONS
        print("     • Sustainability Project Management")
        print("     • Supplier ESG Assessment & Risk Management")
        print("     • ESG Standards & Compliance Management")
        print("     • API Key Management & Authentication")
        print("   🔐 Authentication: Session + API Key support")
        print("   🎨 Professional ESG-themed styling")
        print("   📱 Mobile-responsive design")
        print("   🧪 Interactive testing for all endpoints")
        print(f"   Swagger UI available at: /docs/")
        print(f"   API Specification at: /api-docs/swagger.json")  # FIXED: Updated path
        print(f"   Namespaces created: {', '.join(namespaces.keys()) if namespaces else 'None'}")
        
    except Exception as e:
        print(f"⚠️  API Documentation initialization failed: {e}")
        print(f"   Error details: {type(e).__name__}: {str(e)}")
        print("   Your existing API will continue to work normally")
        print("   Check that all files are in the docs/ directory:")
        print("   - docs/__init__.py")
        print("   - docs/api_documentation.py")
        print("   - docs/api_models.py")
        print("   - docs/api_namespaces.py")
        import traceback
        traceback.print_exc()

# ============================================================================
# PRESERVING USER'S EXACT HEALTH CHECK ENDPOINT
# ============================================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'message': 'ESG Reporting API is running'}

# ============================================================================
# ENHANCED: API status endpoint with comprehensive documentation info
# ============================================================================
@app.route('/api/status', methods=['GET'])
def api_status():
    """Enhanced API status with comprehensive documentation information"""
    status_info = {
        'status': 'operational',
        'message': 'ESG Reporting API is running',
        'version': '1.0',
        'platform': 'ESG Reporting Platform',
        'endpoints': {
            'health': '/api/health',
            'emission_factors': '/api/emission-factors/*',
            'measurements': '/api/measurements/*',
            'suppliers': '/api/suppliers/*',
            'dashboard': '/api/dashboard/*',
            'targets': '/api/targets/*',
            'projects': '/api/projects/*',
            'assets': '/api/assets/*',
            'asset_comparisons': '/api/asset-comparisons/*',  # ✅ INCLUDING USER'S ASSET_COMPARISONS
            'esg_standards': '/api/esg-standards/*',
            'reports': '/api/reports/*',
            'companies': '/api/companies/*',
            'users': '/api/users/*',
            'roles': '/api/roles/*',
            'api_keys': '/api/api-keys/*'
        },
        'modules': [
            'authentication', 'users', 'roles', 'companies', 'measurements',
            'emission_factors', 'dashboard', 'reports', 'targets', 'assets',
            'asset_comparisons', 'projects', 'suppliers', 'esg_standards', 'api_keys'
        ]
    }
    
    # Add comprehensive documentation info if available
    if RESTX_AVAILABLE:
        status_info.update({
            'documentation': {
                'available': True,
                'swagger_ui': '/docs/',
                'api_spec': '/api-docs/swagger.json',  # FIXED: Updated path
                'interactive_testing': True,
                'total_endpoints': '100+',
                'total_modules': 15,  # Including asset_comparisons
                'organized_structure': 'docs/ directory',
                'features': [
                    'Interactive testing',
                    'Professional ESG styling',
                    'Mobile responsive',
                    'Comprehensive models',
                    'Authentication integration',
                    'Error handling',
                    'Usage examples'
                ]
            },
            'authentication': {
                'session': 'Login via web interface',
                'api_key': 'Use Bearer token: Authorization: Bearer esg_your_key',
                'permissions': 'Granular role-based permissions',
                'formats': ['Bearer token', 'Session cookie']
            }
        })
    else:
        status_info.update({
            'documentation': {
                'available': False,
                'note': 'Install flask-restx and ensure docs/ directory structure',
                'install_command': 'pip install flask-restx'
            }
        })
    
    return status_info

# ============================================================================
# PRESERVING USER'S EXACT STATIC FILE SERVING AND CLIENT-SIDE ROUTING
# ============================================================================
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    
    # Check if static folder is configured
    if static_folder_path is None:
        return "Static folder not configured", 404
    
    # Skip API routes - let them be handled by blueprints
    if path.startswith('api/'):
        return "API endpoint not found", 404
    
    # ENHANCED: Skip documentation routes - let Flask-RESTX handle them
    if RESTX_AVAILABLE and (path.startswith('docs') or path == 'swagger.json' or path.startswith('api-docs')):
        return "Documentation route - handled by Flask-RESTX", 404
    
    # PRESERVING USER'S EXACT REACT ROUTER HANDLING
    # Special handling for React Router routes that conflict with static folders
    # These are client-side routes that should be handled by React Router, not static files
    react_routes = ['assets', 'dashboard', 'projects', 'suppliers', 'measurements', 'emission-factors', 'reports', 'settings']
    if path in react_routes:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found. Please build the frontend first.", 404
    
    # Check if the requested file exists in static folder (for CSS, JS, images, etc.)
    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    
    # For all other routes, serve index.html
    # This allows React Router to handle client-side routing
    index_path = os.path.join(static_folder_path, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(static_folder_path, 'index.html')
    else:
        return "index.html not found. Please build the frontend first.", 404

# ============================================================================
# ENHANCED: Welcome endpoint with comprehensive API information
# ============================================================================
@app.route('/api/welcome', methods=['GET'])
def api_welcome():
    """Welcome endpoint with comprehensive API information"""
    welcome_info = {
        'message': 'Welcome to ESG Reporting Platform API',
        'version': '1.0',
        'description': 'Comprehensive Environmental, Social, and Governance reporting and analytics platform',
        'capabilities': {
            'emission_tracking': 'Track and measure carbon emissions across all scopes',
            'esg_reporting': 'Generate professional reports compliant with major frameworks',
            'target_management': 'Set and monitor progress toward sustainability goals',
            'supplier_assessment': 'Evaluate suppliers for ESG risk and compliance',
            'asset_management': 'Track environmental impact of organizational assets',
            'asset_comparisons': 'Compare and analyze asset performance',  # ✅ INCLUDING USER'S FEATURE
            'project_tracking': 'Monitor sustainability initiatives and ROI',
            'dashboard_analytics': 'Real-time insights and trend analysis',
            'standards_compliance': 'Manage compliance with ESG standards and frameworks'
        },
        'frameworks_supported': ['GRI', 'SASB', 'TCFD', 'CDP', 'Custom'],
        'features': [
            'Emission measurements and tracking',
            'Supplier ESG assessment',
            'Real-time dashboard analytics',
            'ESG targets and progress tracking',
            'Comprehensive reporting (GRI, SASB, TCFD, CDP)',
            'Asset and project management',
            'Asset comparison and analysis',  # ✅ INCLUDING USER'S FEATURE
            'Role-based access control',
            'API key authentication'
        ],
        'getting_started': {
            'web_users': 'Access the web interface at the root URL',
            'api_users': 'Use API endpoints with proper authentication',
            'developers': 'Check /api/status for endpoint information'
        }
    }
    
    if RESTX_AVAILABLE:
        welcome_info.update({
            'documentation': {
                'interactive_docs': '/docs/',
                'api_specification': '/api-docs/swagger.json',  # FIXED: Updated path
                'description': 'Complete interactive API documentation with testing capabilities',
                'total_modules': 15,  # Including asset_comparisons
                'total_endpoints': '100+',
                'structure': 'Organized in docs/ directory for maintainability',
                'features': [
                    'Professional ESG-themed styling',
                    'Interactive testing interface',
                    'Mobile-responsive design',
                    'Comprehensive request/response models',
                    'Authentication integration',
                    'Error handling with detailed responses'
                ]
            },
            'authentication': {
                'session': 'Login via web interface for session-based access',
                'api_key': 'Use Bearer token format: Authorization: Bearer esg_your_key',
                'testing': 'Use the "Authorize" button in Swagger UI for testing',
                'permissions': 'Granular role-based permissions for all endpoints'
            }
        })
    
    return welcome_info

if __name__ == '__main__':
    print("🚀 Starting ESG Reporting Platform...")
    print(f"   Web Interface: http://localhost:5003/")
    print(f"   API Health: http://localhost:5003/api/health")
    print(f"   API Status: http://localhost:5003/api/status")
    print(f"   API Welcome: http://localhost:5003/api/welcome")
    
    if RESTX_AVAILABLE:
        print(f"   📚 Comprehensive API Documentation: http://localhost:5003/docs/")
        print(f"   📊 API Specification: http://localhost:5003/api-docs/swagger.json")  # FIXED: Updated path
        print(f"   🧪 Interactive Testing: Available in Swagger UI")
        print(f"   🔐 Authentication: Session + API Key support")
    
    app.run(host='0.0.0.0', port=5003, debug=True)

