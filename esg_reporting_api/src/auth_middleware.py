"""
Centralized Authentication Middleware for ESG Reporting System
Supports both session-based and API key authentication
Can be easily applied to any route across all 15 route files
"""

from functools import wraps
from flask import request, jsonify, session, g
from src.models.esg_models import db, APIKey, User
import hashlib
import json
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    def __init__(self, message, status_code=401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def hash_api_key(api_key):
    """Hash API key for secure storage - matches api_key.py implementation"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def extract_api_key_from_header():
    """Extract API key from Authorization header"""
    auth_header = request.headers.get('Authorization', '')
    
    # Support multiple formats:
    # Authorization: Bearer esg_abc123...
    # Authorization: esg_abc123...
    # X-API-Key: esg_abc123...
    
    if auth_header.startswith('Bearer '):
        return auth_header[7:]  # Remove 'Bearer ' prefix
    elif auth_header.startswith('esg_'):
        return auth_header
    
    # Also check X-API-Key header
    api_key_header = request.headers.get('X-API-Key', '')
    if api_key_header.startswith('esg_'):
        return api_key_header
    
    return None

def validate_api_key_auth(api_key_value):
    """Validate API key and return user info"""
    try:
        if not api_key_value:
            return None, "No API key provided"
        
        # Hash the provided key
        key_hash = hash_api_key(api_key_value)
        
        # Find API key in database
        api_key = APIKey.query.filter_by(key_hash=key_hash).first()
        
        if not api_key:
            return None, "Invalid API key"
        
        if not api_key.is_active:
            return None, "API key is inactive"
        
        # Check expiration
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return None, "API key has expired"
        
        # Get the user who owns this API key
        user = User.query.get(api_key.user_id)
        if not user or not user.is_active:
            return None, "API key owner is inactive"
        
        # Update usage statistics
        api_key.usage_count += 1
        api_key.last_used = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"API key authentication successful for user {user.username}")
        
        return {
            'user': user,
            'api_key': api_key,
            'auth_method': 'api_key'
        }, None
        
    except Exception as e:
        logger.error(f"Error validating API key: {str(e)}")
        return None, f"API key validation error: {str(e)}"

def validate_session_auth():
    """Validate session-based authentication"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return None, "No session found"
        
        user = User.query.get(user_id)
        if not user or not user.is_active:
            session.clear()
            return None, "Session user is inactive"
        
        logger.info(f"Session authentication successful for user {user.username}")
        
        return {
            'user': user,
            'api_key': None,
            'auth_method': 'session'
        }, None
        
    except Exception as e:
        logger.error(f"Error validating session: {str(e)}")
        return None, f"Session validation error: {str(e)}"

def check_permissions(auth_info, required_permissions):
    """Check if user has required permissions"""
    if not required_permissions:
        return True, None
    
    user = auth_info['user']
    api_key = auth_info['api_key']
    
    # If using API key, check API key permissions
    if api_key:
        try:
            api_permissions = json.loads(api_key.permissions) if api_key.permissions else {}
            
            # Check each required permission
            for permission in required_permissions:
                if '.' in permission:
                    module, action = permission.split('.', 1)
                    if module not in api_permissions:
                        return False, f"API key missing permission for module: {module}"
                    if action not in api_permissions[module] or not api_permissions[module][action]:
                        return False, f"API key missing permission: {permission}"
                else:
                    # Simple permission check
                    if permission not in api_permissions or not api_permissions[permission]:
                        return False, f"API key missing permission: {permission}"
            
            return True, None
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing API key permissions: {str(e)}")
            return False, "Invalid API key permissions format"
    
    # If using session, check user role permissions
    if user.role:
        try:
            role_permissions = json.loads(user.role.permissions) if user.role.permissions else {}
            
            # Check each required permission
            for permission in required_permissions:
                if '.' in permission:
                    module, action = permission.split('.', 1)
                    if module not in role_permissions:
                        return False, f"User role missing permission for module: {module}"
                    if action not in role_permissions[module] or not role_permissions[module][action]:
                        return False, f"User role missing permission: {permission}"
                else:
                    # Simple permission check
                    if permission not in role_permissions or not role_permissions[permission]:
                        return False, f"User role missing permission: {permission}"
            
            return True, None
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing role permissions: {str(e)}")
            return False, "Invalid role permissions format"
    
    return False, "No permissions found for user"

# MAIN DECORATORS - These are what you'll use in your route files

def require_auth(permissions=None, allow_session=True, allow_api_key=True):
    """
    Main authentication decorator - supports both session and API key auth
    
    Args:
        permissions (list): List of required permissions (e.g., ['users.read', 'users.write'])
        allow_session (bool): Whether to allow session-based authentication
        allow_api_key (bool): Whether to allow API key authentication
    
    Usage:
        @require_auth()  # Any authentication method
        @require_auth(permissions=['users.read'])  # Requires users.read permission
        @require_auth(allow_session=False)  # API key only
        @require_auth(permissions=['users.write'], allow_session=False)  # API key with permission
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_info = None
            error_message = None
            
            # Try API key authentication first
            if allow_api_key:
                api_key_value = extract_api_key_from_header()
                if api_key_value:
                    auth_info, error_message = validate_api_key_auth(api_key_value)
                    if auth_info:
                        logger.info(f"API key authentication successful for {f.__name__}")
                    else:
                        logger.warning(f"API key authentication failed for {f.__name__}: {error_message}")
                        return jsonify({
                            'success': False,
                            'error': error_message
                        }), 401
            
            # Try session authentication if API key didn't work
            if not auth_info and allow_session:
                auth_info, error_message = validate_session_auth()
                if auth_info:
                    logger.info(f"Session authentication successful for {f.__name__}")
                elif not allow_api_key:  # Only show session error if API key not allowed
                    logger.warning(f"Session authentication failed for {f.__name__}: {error_message}")
                    return jsonify({
                        'success': False,
                        'error': error_message
                    }), 401
            
            # If no authentication method worked
            if not auth_info:
                auth_methods = []
                if allow_session:
                    auth_methods.append("session")
                if allow_api_key:
                    auth_methods.append("API key")
                
                return jsonify({
                    'success': False,
                    'error': f"Authentication required. Supported methods: {', '.join(auth_methods)}"
                }), 401
            
            # Check permissions if specified
            if permissions:
                has_permission, permission_error = check_permissions(auth_info, permissions)
                if not has_permission:
                    logger.warning(f"Permission denied for {f.__name__}: {permission_error}")
                    return jsonify({
                        'success': False,
                        'error': f"Permission denied: {permission_error}"
                    }), 403
            
            # Store auth info in Flask's g object for use in the route
            g.current_user = auth_info['user']
            g.current_api_key = auth_info['api_key']
            g.auth_method = auth_info['auth_method']
            
            # Call the original function
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_api_key(permissions=None):
    """
    API key only authentication decorator
    
    Usage:
        @require_api_key()
        @require_api_key(permissions=['users.read'])
    """
    return require_auth(permissions=permissions, allow_session=False, allow_api_key=True)

def require_session(permissions=None):
    """
    Session only authentication decorator
    
    Usage:
        @require_session()
        @require_session(permissions=['users.write'])
    """
    return require_auth(permissions=permissions, allow_session=True, allow_api_key=False)

# UTILITY FUNCTIONS

def get_current_user():
    """Get the current authenticated user from Flask's g object"""
    return getattr(g, 'current_user', None)

def get_current_api_key():
    """Get the current API key from Flask's g object"""
    return getattr(g, 'current_api_key', None)

def get_auth_method():
    """Get the authentication method used ('session' or 'api_key')"""
    return getattr(g, 'auth_method', None)

def is_api_authenticated():
    """Check if current request is authenticated via API key"""
    return get_auth_method() == 'api_key'

def is_session_authenticated():
    """Check if current request is authenticated via session"""
    return get_auth_method() == 'session'

# PERMISSION CONSTANTS - Define your permission structure here
class Permissions:
    """Centralized permission definitions"""
    
    # User permissions
    USERS_READ = 'users.read'
    USERS_WRITE = 'users.write'
    USERS_DELETE = 'users.delete'
    
    # Role permissions
    ROLES_READ = 'roles.read'
    ROLES_WRITE = 'roles.write'
    ROLES_DELETE = 'roles.delete'
    
    # Company permissions
    COMPANY_READ = 'company.read'
    COMPANY_WRITE = 'company.write'
    COMPANY_DELETE = 'company.delete'
    
    # Api_Key permissions
    API_KEYS_READ = 'api_keys.read'
    API_KEYS_WRITE = 'api_keys.write'
    API_KEYS_DELETE = 'api_keys.delete' 
    
    # Settings permissions
    SETTINGS_READ = 'settings.read'
    SETTINGS_WRITE = 'settings.write'
    SETTINGS_DELETE = 'settings.delete'
    
    # Add more as needed for your other modules
    DASHBOARD_READ = 'dashboard.read'
    
    EMISSION_FACTORS_READ = 'emission_factors.read'
    EMISSION_FACTORS_WRITE = 'emission_factors.write'
    EMISSION_FACTORS_DELETE = 'emission_factors.delete'
    
    MEASUREMENTS_READ = 'measurements.read'
    MEASUREMENTS_WRITE = 'measurements.write'
    MEASUREMENTS_DELETE = 'measurements.delete'
    
    SUPPLIERS_READ = 'suppliers.read'
    SUPPLIERS_WRITE = 'suppliers.write'
    SUPPLIERS_DELETE = 'suppliers.delete'
    
    PROJECTS_READ = 'projects.read'
    PROJECTS_WRITE = 'projects.write'
    PROJECTS_DELETE = 'projects.delete'
    
    ESG_TARGETS_READ = 'esg_targets.read'
    ESG_TARGETS_WRITE = 'esg_targets.write'
    ESG_TARGETS_DELETE = 'esg_targets.delete'
    
    ASSETS_READ = 'assets.read'
    ASSETS_WRITE = 'assets.write'
    ASSETS_DELETE = 'assets.delete'
    
    REPORTS_READ = 'reports.read'
    REPORTS_WRITE = 'reports.write'
    REPORTS_DELETE = 'reports.delete'

# RATE LIMITING (Optional - can be added later)
def check_rate_limit(api_key):
    """Check if API key has exceeded rate limit"""
    # Implementation for rate limiting
    # This can be enhanced later with Redis or in-memory caching
    return True, None

