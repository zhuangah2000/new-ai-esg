"""
Enhanced Company Management Routes with Centralized Auth Middleware
Supports both session-based and API key authentication
"""

from flask import Blueprint, request, jsonify, session
from src.models.esg_models import db, Company
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

company_bp = Blueprint('company', __name__)

# ENHANCED: Import centralized auth middleware (matching user.py structure)
try:
    from src.auth_middleware import require_auth as require_api_auth, Permissions, get_current_user as get_auth_user
    AUTH_MIDDLEWARE_AVAILABLE = True
    logger.info("Auth middleware imported successfully")
except ImportError as e:
    logger.warning(f"Auth middleware not available: {e}")
    AUTH_MIDDLEWARE_AVAILABLE = False

# ENHANCED: Session authentication function (matching user.py structure)
def require_session_auth():
    """Check if user is authenticated via session (renamed to avoid conflict)"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    from src.models.esg_models import User
    user = User.query.get(user_id)
    if not user or not user.is_active:
        session.clear()
        return None
    
    return user

# ENHANCED: Dual authentication decorator (matching user.py structure)
def dual_auth(permissions=None):
    """Decorator that supports both session and API key authentication"""
    def decorator(f):
        if AUTH_MIDDLEWARE_AVAILABLE and permissions:
            # Use the centralized auth system if available and permissions are specified
            return require_api_auth(permissions=permissions)(f)
        else:
            # Fallback to session-only authentication
            def wrapper(*args, **kwargs):
                user = require_session_auth()
                if not user:
                    return jsonify({
                        'success': False,
                        'error': 'Not authenticated'
                    }), 401
                return f(*args, **kwargs)
            return wrapper
    return decorator

# ENHANCED: Get company profile with dual authentication
@company_bp.route('/company/profile', methods=['GET'])
@dual_auth(permissions=[Permissions.COMPANY_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_company_profile():
    """Get company profile information"""
    try:
        logger.info("Fetching company profile")
        
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} accessing company profile via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} accessing company profile via session")
        
        # Get the first (and should be only) company record
        company = Company.query.first()
        
        if not company:
            # Return default structure if no company exists
            return jsonify({
                'success': True,
                'data': {
                    'id': None,
                    'name': '',
                    'legal_name': '',
                    'industry': '',
                    'description': '',
                    'website': '',
                    'email': '',
                    'phone': '',
                    'address_line1': '',
                    'address_line2': '',
                    'city': '',
                    'state': '',
                    'postal_code': '',
                    'country': '',
                    'tax_id': '',
                    'registration_number': '',
                    'reporting_year': datetime.now().year,
                    'fiscal_year_start': '01-01',
                    'fiscal_year_end': '12-31',
                    'currency': 'USD',
                    'timezone': 'UTC',
                    'reporting_frameworks': [],
                    'materiality_topics': [],
                    'logo_url': '',
                    'primary_color': '#10b981',
                    'secondary_color': '#3b82f6'
                }
            }), 200
        
        logger.info(f"Successfully fetched company profile: {company.name}")
        return jsonify({
            'success': True,
            'data': company.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching company profile: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch company profile: {str(e)}'
        }), 500

# ENHANCED: Update company profile with dual authentication
@company_bp.route('/company/profile', methods=['PUT'])
@dual_auth(permissions=[Permissions.COMPANY_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def update_company_profile():
    """Update company profile information"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} updating company profile via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} updating company profile via session")
        
        # Get or create company record
        company = Company.query.first()
        
        if not company:
            # Create new company record
            company = Company()
            db.session.add(company)
            logger.info("Creating new company record")
        else:
            logger.info(f"Updating existing company: {company.name}")
        
        # Update company fields
        updatable_fields = [
            'name', 'legal_name', 'industry', 'description', 'website', 'email', 'phone',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'tax_id', 'registration_number', 'reporting_year', 'fiscal_year_start', 
            'fiscal_year_end', 'currency', 'timezone', 'logo_url', 'primary_color', 'secondary_color'
        ]
        
        updated_fields = []
        for field in updatable_fields:
            if field in data:
                old_value = getattr(company, field, None)
                new_value = data[field]
                
                # Handle special cases
                if field in ['reporting_frameworks', 'materiality_topics']:
                    # These should be JSON arrays
                    if isinstance(new_value, list):
                        new_value = json.dumps(new_value)
                elif field == 'reporting_year':
                    # Ensure it's an integer
                    try:
                        new_value = int(new_value)
                    except (ValueError, TypeError):
                        continue
                
                if old_value != new_value:
                    setattr(company, field, new_value)
                    updated_fields.append(field)
        
        # Handle special JSON fields
        if 'reporting_frameworks' in data:
            frameworks = data['reporting_frameworks']
            if isinstance(frameworks, list):
                company.reporting_frameworks = json.dumps(frameworks)
                updated_fields.append('reporting_frameworks')
        
        if 'materiality_topics' in data:
            topics = data['materiality_topics']
            if isinstance(topics, list):
                company.materiality_topics = json.dumps(topics)
                updated_fields.append('materiality_topics')
        
        # Update timestamp
        company.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Successfully updated company profile. Updated fields: {updated_fields}")
        
        return jsonify({
            'success': True,
            'data': company.to_dict(),
            'message': 'Company profile updated successfully',
            'updated_fields': updated_fields
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating company profile: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to update company profile: {str(e)}'
        }), 500

# ENHANCED: Get company settings with dual authentication
@company_bp.route('/company/settings', methods=['GET'])
@dual_auth(permissions=[Permissions.COMPANY_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_company_settings():
    """Get company-specific settings and configurations"""
    try:
        logger.info("Fetching company settings")
        
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} accessing company settings via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} accessing company settings via session")
        
        company = Company.query.first()
        
        if not company:
            return jsonify({
                'success': False,
                'error': 'Company profile not found. Please create company profile first.'
            }), 404
        
        # Extract settings-specific information
        settings_data = {
            'reporting_year': company.reporting_year,
            'fiscal_year_start': company.fiscal_year_start,
            'fiscal_year_end': company.fiscal_year_end,
            'currency': company.currency,
            'timezone': company.timezone,
            'reporting_frameworks': json.loads(company.reporting_frameworks) if company.reporting_frameworks else [],
            'materiality_topics': json.loads(company.materiality_topics) if company.materiality_topics else [],
            'primary_color': company.primary_color,
            'secondary_color': company.secondary_color
        }
        
        logger.info("Successfully fetched company settings")
        return jsonify({
            'success': True,
            'data': settings_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching company settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch company settings: {str(e)}'
        }), 500

# ENHANCED: Update company settings with dual authentication
@company_bp.route('/company/settings', methods=['PUT'])
@dual_auth(permissions=[Permissions.COMPANY_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def update_company_settings():
    """Update company-specific settings and configurations"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} updating company settings via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} updating company settings via session")
        
        company = Company.query.first()
        if not company:
            return jsonify({
                'success': False,
                'error': 'Company profile not found. Please create company profile first.'
            }), 404
        
        # Update settings fields
        settings_fields = [
            'reporting_year', 'fiscal_year_start', 'fiscal_year_end', 
            'currency', 'timezone', 'primary_color', 'secondary_color'
        ]
        
        updated_fields = []
        for field in settings_fields:
            if field in data:
                old_value = getattr(company, field, None)
                new_value = data[field]
                
                if field == 'reporting_year':
                    try:
                        new_value = int(new_value)
                    except (ValueError, TypeError):
                        continue
                
                if old_value != new_value:
                    setattr(company, field, new_value)
                    updated_fields.append(field)
        
        # Handle JSON fields
        if 'reporting_frameworks' in data:
            frameworks = data['reporting_frameworks']
            if isinstance(frameworks, list):
                old_frameworks = json.loads(company.reporting_frameworks) if company.reporting_frameworks else []
                if old_frameworks != frameworks:
                    company.reporting_frameworks = json.dumps(frameworks)
                    updated_fields.append('reporting_frameworks')
        
        if 'materiality_topics' in data:
            topics = data['materiality_topics']
            if isinstance(topics, list):
                old_topics = json.loads(company.materiality_topics) if company.materiality_topics else []
                if old_topics != topics:
                    company.materiality_topics = json.dumps(topics)
                    updated_fields.append('materiality_topics')
        
        company.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Successfully updated company settings. Updated fields: {updated_fields}")
        
        return jsonify({
            'success': True,
            'message': 'Company settings updated successfully',
            'updated_fields': updated_fields
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating company settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to update company settings: {str(e)}'
        }), 500

# ENHANCED: Get company statistics with dual authentication
@company_bp.route('/company/stats', methods=['GET'])
@dual_auth(permissions=[Permissions.COMPANY_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_company_stats():
    """Get company statistics and metrics"""
    try:
        logger.info("Fetching company statistics")
        
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} accessing company stats via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} accessing company stats via session")
        
        company = Company.query.first()
        if not company:
            return jsonify({
                'success': False,
                'error': 'Company profile not found'
            }), 404
        
        # Calculate basic statistics
        from src.models.esg_models import User, Role
        
        stats = {
            'company_name': company.name,
            'total_users': User.query.filter_by(is_active=True).count(),
            'total_roles': Role.query.count(),
            'reporting_year': company.reporting_year,
            'profile_completeness': calculate_profile_completeness(company),
            'last_updated': company.updated_at.isoformat() if company.updated_at else None,
            'created_at': company.created_at.isoformat() if company.created_at else None
        }
        
        logger.info("Successfully fetched company statistics")
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching company statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch company statistics: {str(e)}'
        }), 500

def calculate_profile_completeness(company):
    """Calculate what percentage of the company profile is complete"""
    required_fields = [
        'name', 'legal_name', 'industry', 'email', 'country', 
        'reporting_year', 'fiscal_year_start', 'fiscal_year_end'
    ]
    
    completed_fields = 0
    for field in required_fields:
        value = getattr(company, field, None)
        if value and str(value).strip():
            completed_fields += 1
    
    return round((completed_fields / len(required_fields)) * 100, 1)

# ENHANCED: Settings-based endpoints for unified permission access
@company_bp.route('/settings/company/profile', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_company_profile():
    """Get company profile via settings permission"""
    return get_company_profile()

@company_bp.route('/settings/company/profile', methods=['PUT'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_update_company_profile():
    """Update company profile via settings permission"""
    return update_company_profile()

@company_bp.route('/settings/company/settings', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_company_settings():
    """Get company settings via settings permission"""
    return get_company_settings()

@company_bp.route('/settings/company/settings', methods=['PUT'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_update_company_settings():
    """Update company settings via settings permission"""
    return update_company_settings()

@company_bp.route('/settings/company/stats', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_company_stats():
    """Get company statistics via settings permission"""
    return get_company_stats()

