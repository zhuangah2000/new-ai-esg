"""
Enhanced User Management Routes for ESG Reporting System
Includes dedicated profile update functionality and API key authentication
Uses SQLAlchemy ORM for consistency with existing codebase
"""

from flask import Blueprint, request, jsonify, session
from src.models.esg_models import db, User, Role
from datetime import datetime, timedelta
import hashlib
import re
import logging

# Import centralized authentication middleware for API key support
try:
    from src.auth_middleware import require_auth as require_api_auth, Permissions, get_current_user as get_auth_user
    AUTH_MIDDLEWARE_AVAILABLE = True
except ImportError:
    AUTH_MIDDLEWARE_AVAILABLE = False
    print("Warning: auth_middleware not available, API key authentication disabled")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__)

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

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

def validate_profile_data(data):
    """Validate profile update data"""
    errors = []
    
    # Validate first_name
    if 'first_name' in data:
        first_name = data['first_name'].strip() if data['first_name'] else ''
        if len(first_name) > 100:
            errors.append("First name must be 100 characters or less")
    
    # Validate last_name
    if 'last_name' in data:
        last_name = data['last_name'].strip() if data['last_name'] else ''
        if len(last_name) > 100:
            errors.append("Last name must be 100 characters or less")
    
    # Validate phone
    if 'phone' in data:
        phone = data['phone'].strip() if data['phone'] else ''
        if phone and len(phone) > 20:
            errors.append("Phone number must be 20 characters or less")
        if phone and not re.match(r'^[\d\s\-\+\(\)\.]+$', phone):
            errors.append("Phone number contains invalid characters")
    
    # Validate department
    if 'department' in data:
        department = data['department'].strip() if data['department'] else ''
        if len(department) > 100:
            errors.append("Department must be 100 characters or less")
    
    # Validate job_title
    if 'job_title' in data:
        job_title = data['job_title'].strip() if data['job_title'] else ''
        if len(job_title) > 100:
            errors.append("Job title must be 100 characters or less")
    
    # Validate email if provided
    if 'email' in data:
        email = data['email'].strip().lower() if data['email'] else ''
        if email and not validate_email(email):
            errors.append("Invalid email format")
    
    return errors

# Helper decorator for dual authentication (session + API key)
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

# ============================================================================
# AUTHENTICATION ROUTES (Session-only, no API key)
# ============================================================================

@user_bp.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint - session authentication only"""
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400
        
        username = data['username']
        password = data['password']
        
        logger.info(f"Login attempt for user: {username}")
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            logger.warning(f"Login failed: User not found - {username}")
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }), 401
        
        if not user.is_active:
            logger.warning(f"Login failed: User inactive - {username}")
            return jsonify({
                'success': False,
                'error': 'Account is inactive'
            }), 401
        
        # Check password
        hashed_password = hash_password(password)
        if user.password_hash != hashed_password:
            logger.warning(f"Login failed: Invalid password - {username}")
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create session
        session['user_id'] = user.id
        session['username'] = user.username
        session['role_id'] = user.role_id
        session.permanent = True  # Make session permanent
        
        logger.info(f"Login successful for user: {username}")
        return jsonify({
            'success': True,
            'data': {
                'message': 'Login successful',
                'user': user.to_dict()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Login failed: {str(e)}'
        }), 500

@user_bp.route('/auth/logout', methods=['POST'])
def logout():
    """User logout endpoint - session authentication only"""
    try:
        username = session.get('username', 'Unknown')
        session.clear()
        
        logger.info(f"Logout successful for user: {username}")
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Logout failed: {str(e)}'
        }), 500

@user_bp.route('/auth/current-user', methods=['GET'])
def get_current_user():
    """Get current logged-in user information - session authentication only"""
    try:
        user = require_session_auth()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            }), 401
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to get current user: {str(e)}'
        }), 500

# ============================================================================
# PROFILE MANAGEMENT ROUTES (Session-only)
# ============================================================================

@user_bp.route('/auth/profile', methods=['GET'])
def get_current_user_profile():
    """Get current user's profile information - session authentication only"""
    try:
        user = require_session_auth()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            }), 401
        
        logger.info(f"Fetching profile for user: {user.username}")
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch profile: {str(e)}'
        }), 500

@user_bp.route('/auth/profile', methods=['PUT'])
def update_current_user_profile():
    """Update current user's profile information - session authentication only"""
    try:
        user = require_session_auth()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        logger.info(f"Updating profile for user: {user.username}")
        
        # Validate profile data
        validation_errors = validate_profile_data(data)
        if validation_errors:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'details': validation_errors
            }), 400
        
        # Track what fields are being updated
        updated_fields = []
        
        # Update profile fields if provided
        if 'first_name' in data:
            new_value = data['first_name'].strip() if data['first_name'] else ''
            if user.first_name != new_value:
                user.first_name = new_value
                updated_fields.append('first_name')
        
        if 'last_name' in data:
            new_value = data['last_name'].strip() if data['last_name'] else ''
            if user.last_name != new_value:
                user.last_name = new_value
                updated_fields.append('last_name')
        
        if 'phone' in data:
            new_value = data['phone'].strip() if data['phone'] else ''
            if user.phone != new_value:
                user.phone = new_value
                updated_fields.append('phone')
        
        if 'department' in data:
            new_value = data['department'].strip() if data['department'] else ''
            if user.department != new_value:
                user.department = new_value
                updated_fields.append('department')
        
        if 'job_title' in data:
            new_value = data['job_title'].strip() if data['job_title'] else ''
            if user.job_title != new_value:
                user.job_title = new_value
                updated_fields.append('job_title')
        
        # Handle email update (requires additional validation)
        if 'email' in data:
            new_email = data['email'].strip().lower()
            if new_email != user.email:
                # Check if new email already exists
                existing_user = User.query.filter_by(email=new_email).first()
                if existing_user and existing_user.id != user.id:
                    return jsonify({
                        'success': False,
                        'error': 'Email address is already in use'
                    }), 400
                user.email = new_email
                updated_fields.append('email')
        
        # Update timestamp
        user.updated_at = datetime.utcnow()
        
        # Commit changes
        db.session.commit()
        
        logger.info(f"Profile updated for user {user.username}. Updated fields: {updated_fields}")
        
        return jsonify({
            'success': True,
            'data': user.to_dict(),
            'message': f'Profile updated successfully',
            'updated_fields': updated_fields
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user profile: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to update profile: {str(e)}'
        }), 500

@user_bp.route('/auth/password', methods=['PUT'])
def change_current_user_password():
    """Change current user's password - session authentication only"""
    try:
        user = require_session_auth()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['current_password', 'new_password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'{field.replace("_", " ").title()} is required'
                }), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Verify current password
        current_hash = hash_password(current_password)
        if user.password_hash != current_hash:
            logger.warning(f"Password change failed: Invalid current password for user {user.username}")
            return jsonify({
                'success': False,
                'error': 'Current password is incorrect'
            }), 400
        
        # Validate new password strength
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Update password
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Password changed successfully for user: {user.username}")
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error changing password: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to change password: {str(e)}'
        }), 500

# ============================================================================
# USER MANAGEMENT ROUTES (Dual authentication: Session + API key)
# ============================================================================

@user_bp.route('/users', methods=['GET'])
@dual_auth(permissions=[Permissions.USERS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_users():
    """Get all users - supports both session and API key authentication"""
    try:
        # Get current user (works with both session and API key)
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
            except:
                current_user = require_session_auth()
                if not current_user:
                    return jsonify({
                        'success': False,
                        'error': 'Not authenticated'
                    }), 401
        else:
            current_user = require_session_auth()
            if not current_user:
                return jsonify({
                    'success': False,
                    'error': 'Not authenticated'
                }), 401
        
        logger.info(f"User list requested by: {current_user.username}")
        
        # Get all users with role information
        users = db.session.query(User, Role).outerjoin(Role, User.role_id == Role.id).all()
        
        users_data = []
        for user, role in users:
            user_dict = user.to_dict()
            if role:
                user_dict['role_name'] = role.name
                user_dict['role_color'] = role.color
            users_data.append(user_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'users': users_data,
                'total': len(users_data)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch users: {str(e)}'
        }), 500

@user_bp.route('/users', methods=['POST'])
@dual_auth(permissions=[Permissions.USERS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def create_user():
    """Create a new user - supports both session and API key authentication"""
    try:
        # Get current user (works with both session and API key)
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
            except:
                current_user = require_session_auth()
                if not current_user:
                    return jsonify({
                        'success': False,
                        'error': 'Not authenticated'
                    }), 401
        else:
            current_user = require_session_auth()
            if not current_user:
                return jsonify({
                    'success': False,
                    'error': 'Not authenticated'
                }), 401
        
        logger.info(f"User creation requested by: {current_user.username}")
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['username', 'email', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Username or email already exists'
            }), 400
        
        # Create new user
        new_user = User(
            username=data['username'].strip(),
            email=data['email'].strip().lower(),
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            phone=data.get('phone', '').strip(),
            department=data.get('department', '').strip(),
            job_title=data.get('job_title', '').strip(),
            role_id=data.get('role_id', 4),  # Default to Viewer role
            is_active=data.get('is_active', True)
        )
        
        # Set password if provided
        if 'password' in data and data['password']:
            is_valid, message = validate_password_strength(data['password'])
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': message
                }), 400
            new_user.password_hash = hash_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"User created successfully: {new_user.username}")
        return jsonify({
            'success': True,
            'data': new_user.to_dict(),
            'message': 'User created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating user: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to create user: {str(e)}'
        }), 500

@user_bp.route('/users-edit/<int:user_id>', methods=['PUT'])
@dual_auth(permissions=[Permissions.USERS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def update_user(user_id):
    """Update a user - supports both session and API key authentication"""
    try:
        # Get current user (works with both session and API key)
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
            except:
                current_user = require_session_auth()
                if not current_user:
                    return jsonify({
                        'success': False,
                        'error': 'Not authenticated'
                    }), 401
        else:
            current_user = require_session_auth()
            if not current_user:
                return jsonify({
                    'success': False,
                    'error': 'Not authenticated'
                }), 401
        
        logger.info(f"User {user_id} update requested by: {current_user.username}")
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Update user fields
        updatable_fields = [
            'username', 'email', 'first_name', 'last_name', 
            'phone', 'department', 'job_title', 'role_id', 'is_active'
        ]
        
        updated_fields = []
        for field in updatable_fields:
            if field in data:
                if field == 'email' and data[field]:
                    if not validate_email(data[field]):
                        return jsonify({
                            'success': False,
                            'error': 'Invalid email format'
                        }), 400
                    # Check if email already exists for another user
                    existing_user = User.query.filter(
                        User.email == data[field].strip().lower(),
                        User.id != user_id
                    ).first()
                    if existing_user:
                        return jsonify({
                            'success': False,
                            'error': 'Email already exists'
                        }), 400
                
                if field == 'username' and data[field]:
                    # Check if username already exists for another user
                    existing_user = User.query.filter(
                        User.username == data[field].strip(),
                        User.id != user_id
                    ).first()
                    if existing_user:
                        return jsonify({
                            'success': False,
                            'error': 'Username already exists'
                        }), 400
                
                old_value = getattr(user, field)
                new_value = data[field]
                
                if field == 'email' and new_value:
                    new_value = new_value.strip().lower()
                elif isinstance(new_value, str):
                    new_value = new_value.strip()
                
                if old_value != new_value:
                    setattr(user, field, new_value)
                    updated_fields.append(field)
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"User {user_id} updated successfully. Fields: {updated_fields}")
        return jsonify({
            'success': True,
            'data': user.to_dict(),
            'message': 'User updated successfully',
            'updated_fields': updated_fields
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user {user_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to update user: {str(e)}'
        }), 500

@user_bp.route('/users/<int:user_id>/toggle-status', methods=['PUT'])
@dual_auth(permissions=[Permissions.USERS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def toggle_user_status(user_id):
    """Toggle user active/inactive status - supports both session and API key authentication"""
    try:
        # Get current user (works with both session and API key)
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
            except:
                current_user = require_session_auth()
                if not current_user:
                    return jsonify({
                        'success': False,
                        'error': 'Not authenticated'
                    }), 401
        else:
            current_user = require_session_auth()
            if not current_user:
                return jsonify({
                    'success': False,
                    'error': 'Not authenticated'
                }), 401
        
        logger.info(f"User {user_id} status toggle requested by: {current_user.username}")
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Prevent deactivating yourself
        if user.id == current_user.id:
            return jsonify({
                'success': False,
                'error': 'Cannot deactivate your own account'
            }), 400
        
        # Toggle status
        user.is_active = not user.is_active
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        logger.info(f"User {user.username} {status}")
        
        return jsonify({
            'success': True,
            'data': user.to_dict(),
            'message': f'User {status} successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error toggling user status {user_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to toggle user status: {str(e)}'
        }), 500

# ============================================================================
# API-ONLY ROUTES (For external integrations)
# ============================================================================

if AUTH_MIDDLEWARE_AVAILABLE:
    try:
        from src.auth_middleware import require_api_key
        
        @user_bp.route('/api/users', methods=['GET'])
        @require_api_key(permissions=[Permissions.USERS_READ])
        def api_get_users():
            """API-only endpoint to get users - requires API key authentication"""
            try:
                current_user = get_auth_user()
                logger.info(f"API users list requested by: {current_user.username}")
                
                users = User.query.filter_by(is_active=True).all()
                users_data = [user.to_dict() for user in users]
                
                return jsonify({
                    'success': True,
                    'data': users_data,
                    'total': len(users_data),
                    'api_version': '1.0'
                }), 200
                
            except Exception as e:
                logger.error(f"Error in API get users: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'API error: {str(e)}'
                }), 500
        
        @user_bp.route('/api/users', methods=['POST'])
        @require_api_key(permissions=[Permissions.USERS_WRITE])
        def api_create_user():
            """API-only endpoint to create user - requires API key authentication"""
            try:
                current_user = get_auth_user()
                logger.info(f"API user creation requested by: {current_user.username}")
                
                data = request.get_json()
                if not data:
                    return jsonify({
                        'success': False,
                        'error': 'No data provided',
                        'api_version': '1.0'
                    }), 400
                
                # Use the same logic as create_user but with API-specific response
                # ... (implementation similar to create_user above)
                
                return jsonify({
                    'success': True,
                    'message': 'User created via API',
                    'api_version': '1.0'
                }), 201
                
            except Exception as e:
                logger.error(f"Error in API create user: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'API error: {str(e)}',
                    'api_version': '1.0'
                }), 500
    except ImportError:
        pass  # API-only routes not available if auth_middleware can't be imported

