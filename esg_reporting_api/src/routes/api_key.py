"""
Enhanced API Key Management Routes with Centralized Auth Middleware
Supports both session-based and API key authentication
"""

from flask import Blueprint, request, jsonify, session
from src.models.esg_models import db, APIKey, User
from datetime import datetime, timedelta
import hashlib
import secrets
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_key_bp = Blueprint('api_key', __name__)

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

def generate_api_key():
    """Generate a secure API key"""
    # Generate random key
    key = secrets.token_urlsafe(32)
    # Add prefix for identification
    prefixed_key = f"esg_{key}"
    return prefixed_key

def hash_api_key(api_key):
    """Hash API key for secure storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def get_key_prefix(api_key):
    """Get the first 12 characters of API key for display"""
    return api_key[:12] + "..."

def create_full_permissions():
    """Create full permissions object for new API keys"""
    return {
        "dashboard": {"read": True, "write": True, "delete": True},
        "users": {"read": True, "write": True, "delete": True},
        "roles": {"read": True, "write": True, "delete": True},
        "company": {"read": True, "write": True, "delete": True},
        "settings": {"read": True, "write": True, "delete": True},
        "api_keys": {"read": True, "write": True, "delete": True},
        "emission_factors": {"read": True, "write": True, "delete": True},
        "measurements": {"read": True, "write": True, "delete": True},
        "suppliers": {"read": True, "write": True, "delete": True},
        "projects": {"read": True, "write": True, "delete": True},
        "esg_targets": {"read": True, "write": True, "delete": True},
        "assets": {"read": True, "write": True, "delete": True},
        "reports": {"read": True, "write": True, "delete": True}
    }

# ENHANCED: Get API keys with dual authentication
@api_key_bp.route('/api-keys', methods=['GET'])
@dual_auth(permissions=[Permissions.API_KEYS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_api_keys():
    """Get all API keys for the current user"""
    try:
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                user_id = current_user.id
                logger.info(f"User {current_user.username} fetching API keys via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    user_id = current_user.id
                    logger.info(f"User {current_user.username} fetching API keys via session")
                else:
                    return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        else:
            current_user = require_session_auth()
            if not current_user:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            user_id = current_user.id
        
        logger.info(f"Fetching API keys for user {user_id}")
        
        # Get API keys created by current user
        api_keys = APIKey.query.filter_by(user_id=user_id).order_by(APIKey.created_at.desc()).all()
        
        api_keys_data = []
        for api_key in api_keys:
            key_dict = api_key.to_dict()
            # Don't include the actual hash in response
            key_dict.pop('key_hash', None)
            api_keys_data.append(key_dict)
        
        logger.info(f"Successfully fetched {len(api_keys_data)} API keys")
        return jsonify({
            'success': True,
            'data': api_keys_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching API keys: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch API keys: {str(e)}'
        }), 500

# ENHANCED: Create API key with dual authentication
@api_key_bp.route('/api-keys', methods=['POST'])
@dual_auth(permissions=[Permissions.API_KEYS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def create_api_key():
    """Create a new API key with enhanced permission handling"""
    try:
        # Get current user
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                user_id = current_user.id
                logger.info(f"User {current_user.username} creating API key via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    user_id = current_user.id
                    logger.info(f"User {current_user.username} creating API key via session")
                else:
                    return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        else:
            current_user = require_session_auth()
            if not current_user:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            user_id = current_user.id
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # ENHANCED: Debug logging to track permission data
        logger.info(f"=== API KEY CREATION DEBUG ===")
        logger.info(f"Raw request data: {data}")
        logger.info(f"Request data type: {type(data)}")
        
        # Validate required fields
        if 'name' not in data or not data['name']:
            return jsonify({
                'success': False,
                'error': 'API key name is required'
            }), 400
        
        # Generate API key
        api_key_value = generate_api_key()
        key_hash = hash_api_key(api_key_value)
        key_prefix = get_key_prefix(api_key_value)
        
        # ENHANCED: Handle permissions with full permissions as default
        permissions_data = data.get('permissions', {})
        if not permissions_data:
            # Create full permissions if none provided
            permissions_data = create_full_permissions()
            logger.info("No permissions provided, creating full permissions")
        
        logger.info(f"Final permissions data: {permissions_data}")
        logger.info(f"Permissions data type: {type(permissions_data)}")
        
        # Convert permissions to JSON string
        permissions_json = json.dumps(permissions_data)
        logger.info(f"Permissions JSON: {permissions_json}")
        
        # Handle optional fields
        description = data.get('description', '')
        ip_whitelist = data.get('ip_whitelist', [])
        rate_limit = data.get('rate_limit', 1000)
        expires_at = None
        
        if data.get('expires_at'):
            try:
                expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid expiration date format'
                }), 400
        
        # Create API key record
        api_key = APIKey(
            name=data['name'],
            description=description,
            key_hash=key_hash,
            key_prefix=key_prefix,
            permissions=permissions_json,  # Store as JSON string
            ip_whitelist=json.dumps(ip_whitelist),
            rate_limit=rate_limit,
            expires_at=expires_at,
            is_active=True,
            usage_count=0,
            last_used=None,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(api_key)
        db.session.commit()
        
        logger.info(f"Successfully created API key: {api_key.name} (ID: {api_key.id})")
        logger.info(f"Stored permissions: {api_key.permissions}")
        
        # Return API key data including the actual key (only time it's shown)
        response_data = api_key.to_dict()
        response_data['api_key'] = api_key_value  # Include actual key in response
        response_data.pop('key_hash', None)  # Remove hash from response
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': 'API key created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating API key: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to create API key: {str(e)}'
        }), 500

# ENHANCED: Update API key with dual authentication
@api_key_bp.route('/api-keys/<int:api_key_id>', methods=['PUT'])
@dual_auth(permissions=[Permissions.API_KEYS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def update_api_key(api_key_id):
    """Update an existing API key"""
    try:
        # Get current user
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                user_id = current_user.id
                logger.info(f"User {current_user.username} updating API key {api_key_id} via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    user_id = current_user.id
                    logger.info(f"User {current_user.username} updating API key {api_key_id} via session")
                else:
                    return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        else:
            current_user = require_session_auth()
            if not current_user:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            user_id = current_user.id
        
        # Get API key
        api_key = APIKey.query.filter_by(id=api_key_id, user_id=user_id).first()
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not found'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Update fields
        if 'name' in data:
            api_key.name = data['name']
        if 'description' in data:
            api_key.description = data['description']
        if 'permissions' in data:
            api_key.permissions = json.dumps(data['permissions'])
        if 'ip_whitelist' in data:
            api_key.ip_whitelist = json.dumps(data['ip_whitelist'])
        if 'rate_limit' in data:
            api_key.rate_limit = data['rate_limit']
        if 'is_active' in data:
            api_key.is_active = data['is_active']
        if 'expires_at' in data:
            if data['expires_at']:
                try:
                    api_key.expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid expiration date format'
                    }), 400
            else:
                api_key.expires_at = None
        
        api_key.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Successfully updated API key: {api_key.name}")
        
        response_data = api_key.to_dict()
        response_data.pop('key_hash', None)
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': 'API key updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating API key: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to update API key: {str(e)}'
        }), 500

# ENHANCED: Delete API key with dual authentication
@api_key_bp.route('/api-keys/<int:api_key_id>', methods=['DELETE'])
@dual_auth(permissions=[Permissions.API_KEYS_DELETE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def delete_api_key(api_key_id):
    """Delete an API key"""
    try:
        # Get current user
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                user_id = current_user.id
                logger.info(f"User {current_user.username} deleting API key {api_key_id} via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    user_id = current_user.id
                    logger.info(f"User {current_user.username} deleting API key {api_key_id} via session")
                else:
                    return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        else:
            current_user = require_session_auth()
            if not current_user:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            user_id = current_user.id
        
        # Get API key
        api_key = APIKey.query.filter_by(id=api_key_id, user_id=user_id).first()
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not found'
            }), 404
        
        api_key_name = api_key.name
        db.session.delete(api_key)
        db.session.commit()
        
        logger.info(f"Successfully deleted API key: {api_key_name}")
        
        return jsonify({
            'success': True,
            'message': f'API key "{api_key_name}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting API key: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to delete API key: {str(e)}'
        }), 500

# ENHANCED: Regenerate API key with dual authentication
@api_key_bp.route('/api-keys/<int:api_key_id>/regenerate', methods=['POST'])
@dual_auth(permissions=[Permissions.API_KEYS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def regenerate_api_key(api_key_id):
    """Regenerate an existing API key"""
    try:
        # Get current user
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                user_id = current_user.id
                logger.info(f"User {current_user.username} regenerating API key {api_key_id} via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    user_id = current_user.id
                    logger.info(f"User {current_user.username} regenerating API key {api_key_id} via session")
                else:
                    return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        else:
            current_user = require_session_auth()
            if not current_user:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            user_id = current_user.id
        
        # Get API key
        api_key = APIKey.query.filter_by(id=api_key_id, user_id=user_id).first()
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not found'
            }), 404
        
        # Generate new key
        new_api_key_value = generate_api_key()
        new_key_hash = hash_api_key(new_api_key_value)
        new_key_prefix = get_key_prefix(new_api_key_value)
        
        # Update API key
        api_key.key_hash = new_key_hash
        api_key.key_prefix = new_key_prefix
        api_key.usage_count = 0
        api_key.last_used = None
        api_key.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Successfully regenerated API key: {api_key.name}")
        
        # Return API key data including the new key
        response_data = api_key.to_dict()
        response_data['api_key'] = new_api_key_value  # Include new key in response
        response_data.pop('key_hash', None)
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': 'API key regenerated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error regenerating API key: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to regenerate API key: {str(e)}'
        }), 500

# ENHANCED: Settings-based endpoints for unified permission access
@api_key_bp.route('/settings/api-keys', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_api_keys():
    """Get API keys via settings permission"""
    return get_api_keys()

@api_key_bp.route('/settings/api-keys', methods=['POST'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_create_api_key():
    """Create API key via settings permission"""
    return create_api_key()

@api_key_bp.route('/settings/api-keys/<int:api_key_id>', methods=['PUT'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_update_api_key(api_key_id):
    """Update API key via settings permission"""
    return update_api_key(api_key_id)

@api_key_bp.route('/settings/api-keys/<int:api_key_id>', methods=['DELETE'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_delete_api_key(api_key_id):
    """Delete API key via settings permission"""
    return delete_api_key(api_key_id)

@api_key_bp.route('/settings/api-keys/<int:api_key_id>/regenerate', methods=['POST'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_regenerate_api_key(api_key_id):
    """Regenerate API key via settings permission"""
    return regenerate_api_key(api_key_id)

