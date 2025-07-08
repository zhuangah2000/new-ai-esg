"""
Enhanced Role Management Routes with Centralized Auth Middleware
Supports both session-based and API key authentication
"""

from flask import Blueprint, request, jsonify, session
from src.models.esg_models import db, Role, User
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

role_bp = Blueprint('role', __name__)

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

# ENHANCED: Default module permissions structure with all modules
DEFAULT_MODULES = [
    'dashboard',
    'emission_factors', 
    'measurements',
    'suppliers',
    'projects',
    'esg_targets',
    'assets',
    'reports',
    'settings',
    'company',      # Added for Settings unified permission
    'users',        # Added for Settings unified permission
    'roles',        # Added for Settings unified permission
    'api_keys'      # Added for Settings unified permission
]

def get_default_permissions():
    """Get default permissions structure with all modules"""
    permissions = {}
    for module in DEFAULT_MODULES:
        permissions[module] = {
            'read': False,
            'write': False,
            'delete': False
        }
    return permissions

def create_role_permissions(role_name):
    """Create default permissions based on role name"""
    permissions = get_default_permissions()
    
    if role_name.lower() == 'administrator':
        # Full access to everything
        for module in DEFAULT_MODULES:
            permissions[module] = {'read': True, 'write': True, 'delete': True}
    elif role_name.lower() == 'manager':
        # Read/write access to most modules, limited delete
        for module in DEFAULT_MODULES:
            if module in ['users', 'roles', 'api_keys']:
                permissions[module] = {'read': True, 'write': True, 'delete': False}
            else:
                permissions[module] = {'read': True, 'write': True, 'delete': True}
    elif role_name.lower() == 'analyst':
        # Read/write access to data modules, read-only for admin modules
        data_modules = ['dashboard', 'emission_factors', 'measurements', 'suppliers', 'projects', 'esg_targets', 'assets', 'reports']
        for module in DEFAULT_MODULES:
            if module in data_modules:
                permissions[module] = {'read': True, 'write': True, 'delete': False}
            else:
                permissions[module] = {'read': True, 'write': False, 'delete': False}
    elif role_name.lower() == 'viewer':
        # Read-only access to most modules
        for module in DEFAULT_MODULES:
            if module in ['dashboard', 'reports', 'company']:
                permissions[module] = {'read': True, 'write': False, 'delete': False}
            else:
                permissions[module] = {'read': False, 'write': False, 'delete': False}
    elif role_name.lower() == 'intern':
        # Very limited access
        for module in DEFAULT_MODULES:
            if module == 'dashboard':
                permissions[module] = {'read': True, 'write': False, 'delete': False}
            else:
                permissions[module] = {'read': False, 'write': False, 'delete': False}
    
    return permissions

# ENHANCED: Get all roles with dual authentication
@role_bp.route('/roles', methods=['GET'])
@dual_auth(permissions=[Permissions.ROLES_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_roles():
    """Get all roles with user counts"""
    try:
        logger.info("Fetching all roles")
        
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} accessing roles via API key")
            except:
                # Fallback to session user
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} accessing roles via session")
        
        # Query all roles with user counts
        roles = db.session.query(
            Role,
            db.func.count(User.id).label('user_count')
        ).outerjoin(User, Role.id == User.role_id).group_by(Role.id).all()
        
        roles_data = []
        for role, user_count in roles:
            role_dict = role.to_dict()
            role_dict['user_count'] = user_count
            roles_data.append(role_dict)
        
        logger.info(f"Successfully fetched {len(roles_data)} roles")
        return jsonify({
            'success': True,
            'data': roles_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching roles: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch roles: {str(e)}'
        }), 500

# ENHANCED: Get specific role with dual authentication
@role_bp.route('/roles/<int:role_id>', methods=['GET'])
@dual_auth(permissions=[Permissions.ROLES_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_role(role_id):
    """Get a specific role by ID"""
    try:
        logger.info(f"Fetching role {role_id}")
        
        role = Role.query.get(role_id)
        if not role:
            return jsonify({
                'success': False,
                'error': 'Role not found'
            }), 404
        
        # Get user count for this role
        user_count = User.query.filter_by(role_id=role_id).count()
        
        role_dict = role.to_dict()
        role_dict['user_count'] = user_count
        
        logger.info(f"Successfully fetched role: {role.name}")
        return jsonify({
            'success': True,
            'data': role_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching role {role_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch role: {str(e)}'
        }), 500

# ENHANCED: Create new role with dual authentication
@role_bp.route('/roles', methods=['POST'])
@dual_auth(permissions=[Permissions.ROLES_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def create_role():
    """Create a new role"""
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
                logger.info(f"User {current_user.username} creating new role via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} creating new role via session")
        
        # Validate required fields
        if 'name' not in data or not data['name']:
            return jsonify({
                'success': False,
                'error': 'Role name is required'
            }), 400
        
        name = data['name'].strip()
        
        # Check if role name already exists
        existing_role = Role.query.filter_by(name=name).first()
        if existing_role:
            return jsonify({
                'success': False,
                'error': f'Role "{name}" already exists'
            }), 400
        
        # Get or create permissions
        permissions = data.get('permissions', {})
        if not permissions:
            permissions = create_role_permissions(name)
        
        # Ensure all modules are present in permissions
        default_permissions = get_default_permissions()
        for module in DEFAULT_MODULES:
            if module not in permissions:
                permissions[module] = default_permissions[module]
        
        # Create new role
        new_role = Role(
            name=name,
            description=data.get('description', '').strip(),
            color=data.get('color', '#6b7280'),
            permissions=json.dumps(permissions),
            is_system_role=False
        )
        
        db.session.add(new_role)
        db.session.commit()
        
        logger.info(f"Successfully created role: {name}")
        
        # Return the created role with user count
        role_dict = new_role.to_dict()
        role_dict['user_count'] = 0
        
        return jsonify({
            'success': True,
            'data': role_dict,
            'message': 'Role created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating role: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to create role: {str(e)}'
        }), 500

# ENHANCED: Update role with dual authentication
@role_bp.route('/roles/<int:role_id>', methods=['PUT'])
@dual_auth(permissions=[Permissions.ROLES_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def update_role(role_id):
    """Update an existing role"""
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({
                'success': False,
                'error': 'Role not found'
            }), 404
        
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} updating role {role.name} via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} updating role {role.name} via session")
        
        # Check if it's a system role
        if role.is_system_role:
            return jsonify({
                'success': False,
                'error': 'Cannot modify system roles'
            }), 403
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Update fields
        if 'name' in data and data['name']:
            new_name = data['name'].strip()
            # Check if new name conflicts with existing role
            if new_name != role.name:
                existing_role = Role.query.filter_by(name=new_name).first()
                if existing_role:
                    return jsonify({
                        'success': False,
                        'error': f'Role "{new_name}" already exists'
                    }), 400
                role.name = new_name
        
        if 'description' in data:
            role.description = data['description'].strip()
        
        if 'color' in data:
            role.color = data['color']
        
        if 'permissions' in data:
            permissions = data['permissions']
            # Ensure all modules are present
            default_permissions = get_default_permissions()
            for module in DEFAULT_MODULES:
                if module not in permissions:
                    permissions[module] = default_permissions[module]
            role.permissions = json.dumps(permissions)
        
        role.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Successfully updated role: {role.name}")
        
        # Return updated role with user count
        user_count = User.query.filter_by(role_id=role_id).count()
        role_dict = role.to_dict()
        role_dict['user_count'] = user_count
        
        return jsonify({
            'success': True,
            'data': role_dict,
            'message': 'Role updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating role {role_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to update role: {str(e)}'
        }), 500

# ENHANCED: Delete role with dual authentication
@role_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@dual_auth(permissions=[Permissions.ROLES_DELETE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def delete_role(role_id):
    """Delete a role"""
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({
                'success': False,
                'error': 'Role not found'
            }), 404
        
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} deleting role {role.name} via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} deleting role {role.name} via session")
        
        # Check if it's a system role
        if role.is_system_role:
            return jsonify({
                'success': False,
                'error': 'Cannot delete system roles'
            }), 403
        
        # Check if role has users assigned
        user_count = User.query.filter_by(role_id=role_id).count()
        if user_count > 0:
            return jsonify({
                'success': False,
                'error': f'Cannot delete role. {user_count} users are assigned to this role.'
            }), 400
        
        role_name = role.name
        db.session.delete(role)
        db.session.commit()
        
        logger.info(f"Successfully deleted role: {role_name}")
        
        return jsonify({
            'success': True,
            'message': f'Role "{role_name}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting role {role_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to delete role: {str(e)}'
        }), 500

# ENHANCED: Get role permissions with dual authentication
@role_bp.route('/roles/<int:role_id>/permissions', methods=['GET'])
@dual_auth(permissions=[Permissions.ROLES_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_role_permissions(role_id):
    """Get permissions for a specific role"""
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({
                'success': False,
                'error': 'Role not found'
            }), 404
        
        # Parse permissions JSON
        try:
            permissions = json.loads(role.permissions) if role.permissions else {}
        except json.JSONDecodeError:
            permissions = {}
        
        # Ensure all modules are present
        default_permissions = get_default_permissions()
        for module in DEFAULT_MODULES:
            if module not in permissions:
                permissions[module] = default_permissions[module]
        
        logger.info(f"Successfully fetched permissions for role: {role.name}")
        
        return jsonify({
            'success': True,
            'data': {
                'role_id': role_id,
                'role_name': role.name,
                'permissions': permissions,
                'available_modules': DEFAULT_MODULES
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching permissions for role {role_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch role permissions: {str(e)}'
        }), 500

# ENHANCED: Update role permissions with dual authentication
@role_bp.route('/roles/<int:role_id>/permissions', methods=['PUT'])
@dual_auth(permissions=[Permissions.ROLES_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def update_role_permissions(role_id):
    """Update permissions for a specific role"""
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({
                'success': False,
                'error': 'Role not found'
            }), 404
        
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} updating permissions for role {role.name} via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} updating permissions for role {role.name} via session")
        
        # Check if it's a system role
        if role.is_system_role:
            return jsonify({
                'success': False,
                'error': 'Cannot modify permissions for system roles'
            }), 403
        
        data = request.get_json()
        if not data or 'permissions' not in data:
            return jsonify({
                'success': False,
                'error': 'Permissions data is required'
            }), 400
        
        permissions = data['permissions']
        
        # Ensure all modules are present
        default_permissions = get_default_permissions()
        for module in DEFAULT_MODULES:
            if module not in permissions:
                permissions[module] = default_permissions[module]
        
        # Update role permissions
        role.permissions = json.dumps(permissions)
        role.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Successfully updated permissions for role: {role.name}")
        
        return jsonify({
            'success': True,
            'data': {
                'role_id': role_id,
                'role_name': role.name,
                'permissions': permissions
            },
            'message': 'Role permissions updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating permissions for role {role_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to update role permissions: {str(e)}'
        }), 500

# ENHANCED: Settings-based endpoints for unified permission access
@role_bp.route('/settings/roles', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_roles():
    """Get all roles via settings permission"""
    return get_roles()

@role_bp.route('/settings/roles', methods=['POST'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_create_role():
    """Create role via settings permission"""
    return create_role()

@role_bp.route('/settings/roles/<int:role_id>', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_role(role_id):
    """Get specific role via settings permission"""
    return get_role(role_id)

@role_bp.route('/settings/roles/<int:role_id>', methods=['PUT'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_update_role(role_id):
    """Update role via settings permission"""
    return update_role(role_id)

@role_bp.route('/settings/roles/<int:role_id>', methods=['DELETE'])
@dual_auth(permissions=[Permissions.SETTINGS_DELETE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_delete_role(role_id):
    """Delete role via settings permission"""
    return delete_role(role_id)

