"""
Enhanced ESG Targets Management Routes with Centralized Auth Middleware
Supports both session-based and API key authentication
"""

from flask import Blueprint, request, jsonify, session
from src.models.esg_models import db, ESGTarget
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

targets_bp = Blueprint('targets', __name__)

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

# ENHANCED: Get targets with dual authentication
@targets_bp.route('/targets', methods=['GET'])
@dual_auth(permissions=[Permissions.ESG_TARGETS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_targets():
    """Get all ESG targets with optional filtering"""
    try:
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} fetching targets via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} fetching targets via session")
        
        # Get query parameters for filtering
        target_type = request.args.get('target_type')
        scope = request.args.get('scope', type=int)
        status = request.args.get('status')
        search = request.args.get('search')
        
        logger.info(f"Fetching targets with filters - type: {target_type}, scope: {scope}, status: {status}, search: {search}")
        
        # Build query
        query = ESGTarget.query
        
        if target_type and target_type != 'all':
            query = query.filter(ESGTarget.target_type == target_type)
        if scope:
            query = query.filter(ESGTarget.scope == scope)
        if status and status != 'all':
            query = query.filter(ESGTarget.status == status)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    ESGTarget.name.ilike(search_filter),
                    ESGTarget.description.ilike(search_filter)
                )
            )
        
        # Order by target year, then by name
        query = query.order_by(ESGTarget.target_year, ESGTarget.name)
        
        targets = query.all()
        
        logger.info(f"Successfully fetched {len(targets)} targets")
        
        return jsonify({
            'success': True,
            'data': [target.to_dict() for target in targets]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching targets: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch targets: {str(e)}'
        }), 500

# ENHANCED: Create target with dual authentication
@targets_bp.route('/targets', methods=['POST'])
@dual_auth(permissions=[Permissions.ESG_TARGETS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def create_target():
    """Create a new ESG target"""
    try:
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} creating target via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} creating target via session")
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'target_type', 'baseline_value', 'baseline_year', 'target_value', 'target_year', 'unit']
        for field in required_fields:
            if field not in data or data[field] == '':
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate data types and ranges
        try:
            baseline_value = float(data['baseline_value'])
            baseline_year = int(data['baseline_year'])
            target_value = float(data['target_value'])
            target_year = int(data['target_year'])
            
            if baseline_year < 1900 or baseline_year > 2100:
                return jsonify({
                    'success': False,
                    'error': 'Baseline year must be between 1900 and 2100'
                }), 400
            if target_year < 1900 or target_year > 2100:
                return jsonify({
                    'success': False,
                    'error': 'Target year must be between 1900 and 2100'
                }), 400
            if target_year <= baseline_year:
                return jsonify({
                    'success': False,
                    'error': 'Target year must be after baseline year'
                }), 400
                
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': 'Invalid numeric values provided'
            }), 400
        
        # Handle optional fields
        scope = None
        if data.get('scope') and data['scope'] != '':
            try:
                scope = int(data['scope'])
                if scope not in [1, 2, 3]:
                    return jsonify({
                        'success': False,
                        'error': 'Scope must be 1, 2, or 3'
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid scope value'
                }), 400
        
        current_value = None
        if data.get('current_value') and data['current_value'] != '':
            try:
                current_value = float(data['current_value'])
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid current value'
                }), 400
        
        progress_percentage = 0.0
        if data.get('progress_percentage') and data['progress_percentage'] != '':
            try:
                progress_percentage = float(data['progress_percentage'])
                if progress_percentage < 0 or progress_percentage > 100:
                    return jsonify({
                        'success': False,
                        'error': 'Progress percentage must be between 0 and 100'
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid progress percentage'
                }), 400
        
        # Create new target
        target = ESGTarget(
            name=data['name'],
            description=data.get('description', ''),
            target_type=data['target_type'],
            baseline_value=baseline_value,
            baseline_year=baseline_year,
            target_value=target_value,
            target_year=target_year,
            current_value=current_value,
            progress_percentage=progress_percentage,
            unit=data['unit'],
            scope=scope,
            status=data.get('status', 'active'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(target)
        db.session.commit()
        
        logger.info(f"Successfully created target: {target.name} (ID: {target.id})")
        
        return jsonify({
            'success': True,
            'data': target.to_dict(),
            'message': 'Target created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating target: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to create target: {str(e)}'
        }), 500

# ENHANCED: Get single target with dual authentication
@targets_bp.route('/targets/<int:target_id>', methods=['GET'])
@dual_auth(permissions=[Permissions.ESG_TARGETS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_target(target_id):
    """Get a specific ESG target"""
    try:
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} fetching target {target_id} via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} fetching target {target_id} via session")
        
        target = ESGTarget.query.get(target_id)
        if not target:
            return jsonify({
                'success': False,
                'error': 'Target not found'
            }), 404
        
        logger.info(f"Successfully fetched target: {target.name}")
        
        return jsonify({
            'success': True,
            'data': target.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching target {target_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch target: {str(e)}'
        }), 500

# ENHANCED: Update target with dual authentication
@targets_bp.route('/targets/<int:target_id>', methods=['PUT'])
@dual_auth(permissions=[Permissions.ESG_TARGETS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def update_target(target_id):
    """Update an existing ESG target"""
    try:
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} updating target {target_id} via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} updating target {target_id} via session")
        
        target = ESGTarget.query.get(target_id)
        if not target:
            return jsonify({
                'success': False,
                'error': 'Target not found'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Update fields
        updated_fields = []
        
        if 'name' in data:
            target.name = data['name']
            updated_fields.append('name')
        
        if 'description' in data:
            target.description = data['description']
            updated_fields.append('description')
        
        if 'target_type' in data:
            target.target_type = data['target_type']
            updated_fields.append('target_type')
        
        if 'baseline_value' in data:
            try:
                target.baseline_value = float(data['baseline_value'])
                updated_fields.append('baseline_value')
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid baseline value'
                }), 400
        
        if 'baseline_year' in data:
            try:
                baseline_year = int(data['baseline_year'])
                if baseline_year < 1900 or baseline_year > 2100:
                    return jsonify({
                        'success': False,
                        'error': 'Baseline year must be between 1900 and 2100'
                    }), 400
                target.baseline_year = baseline_year
                updated_fields.append('baseline_year')
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid baseline year'
                }), 400
        
        if 'target_value' in data:
            try:
                target.target_value = float(data['target_value'])
                updated_fields.append('target_value')
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid target value'
                }), 400
        
        if 'target_year' in data:
            try:
                target_year = int(data['target_year'])
                if target_year < 1900 or target_year > 2100:
                    return jsonify({
                        'success': False,
                        'error': 'Target year must be between 1900 and 2100'
                    }), 400
                if target_year <= target.baseline_year:
                    return jsonify({
                        'success': False,
                        'error': 'Target year must be after baseline year'
                    }), 400
                target.target_year = target_year
                updated_fields.append('target_year')
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid target year'
                }), 400
        
        if 'current_value' in data:
            if data['current_value'] is not None and data['current_value'] != '':
                try:
                    target.current_value = float(data['current_value'])
                    updated_fields.append('current_value')
                except ValueError:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid current value'
                    }), 400
            else:
                target.current_value = None
                updated_fields.append('current_value')
        
        if 'progress_percentage' in data:
            try:
                progress = float(data['progress_percentage'])
                if progress < 0 or progress > 100:
                    return jsonify({
                        'success': False,
                        'error': 'Progress percentage must be between 0 and 100'
                    }), 400
                target.progress_percentage = progress
                updated_fields.append('progress_percentage')
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid progress percentage'
                }), 400
        
        if 'unit' in data:
            target.unit = data['unit']
            updated_fields.append('unit')
        
        if 'scope' in data:
            if data['scope'] is not None and data['scope'] != '':
                try:
                    scope = int(data['scope'])
                    if scope not in [1, 2, 3]:
                        return jsonify({
                            'success': False,
                            'error': 'Scope must be 1, 2, or 3'
                        }), 400
                    target.scope = scope
                    updated_fields.append('scope')
                except ValueError:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid scope value'
                    }), 400
            else:
                target.scope = None
                updated_fields.append('scope')
        
        if 'status' in data:
            target.status = data['status']
            updated_fields.append('status')
        
        target.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Successfully updated target: {target.name}. Updated fields: {updated_fields}")
        
        return jsonify({
            'success': True,
            'data': target.to_dict(),
            'message': 'Target updated successfully',
            'updated_fields': updated_fields
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating target {target_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to update target: {str(e)}'
        }), 500

# ENHANCED: Delete target with dual authentication
@targets_bp.route('/targets/<int:target_id>', methods=['DELETE'])
@dual_auth(permissions=[Permissions.ESG_TARGETS_DELETE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def delete_target(target_id):
    """Delete an ESG target"""
    try:
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} deleting target {target_id} via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} deleting target {target_id} via session")
        
        target = ESGTarget.query.get(target_id)
        if not target:
            return jsonify({
                'success': False,
                'error': 'Target not found'
            }), 404
        
        target_name = target.name
        db.session.delete(target)
        db.session.commit()
        
        logger.info(f"Successfully deleted target: {target_name}")
        
        return jsonify({
            'success': True,
            'message': f'Target "{target_name}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting target {target_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to delete target: {str(e)}'
        }), 500

# ENHANCED: Get target statistics with dual authentication
@targets_bp.route('/targets/stats', methods=['GET'])
@dual_auth(permissions=[Permissions.ESG_TARGETS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_target_stats():
    """Get target statistics and summary"""
    try:
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} fetching target stats via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} fetching target stats via session")
        
        # Calculate statistics
        total_targets = ESGTarget.query.count()
        active_targets = ESGTarget.query.filter_by(status='active').count()
        completed_targets = ESGTarget.query.filter_by(status='completed').count()
        
        # Average progress
        avg_progress = db.session.query(func.avg(ESGTarget.progress_percentage)).filter_by(status='active').scalar() or 0
        
        # Targets by type
        type_stats = db.session.query(
            ESGTarget.target_type,
            func.count(ESGTarget.id).label('count')
        ).group_by(ESGTarget.target_type).all()
        
        type_breakdown = {target_type: count for target_type, count in type_stats}
        
        # Targets by scope
        scope_stats = db.session.query(
            ESGTarget.scope,
            func.count(ESGTarget.id).label('count')
        ).filter(ESGTarget.scope.isnot(None)).group_by(ESGTarget.scope).all()
        
        scope_breakdown = {f"Scope {scope}": count for scope, count in scope_stats}
        
        # Upcoming deadlines (targets due in next 12 months)
        current_year = datetime.now().year
        upcoming_targets = ESGTarget.query.filter(
            ESGTarget.target_year <= current_year + 1,
            ESGTarget.status == 'active'
        ).count()
        
        stats = {
            'total_targets': total_targets,
            'active_targets': active_targets,
            'completed_targets': completed_targets,
            'average_progress': round(avg_progress, 1),
            'upcoming_deadlines': upcoming_targets,
            'type_breakdown': type_breakdown,
            'scope_breakdown': scope_breakdown
        }
        
        logger.info(f"Successfully generated target statistics")
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching target stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch target statistics: {str(e)}'
        }), 500

# ENHANCED: Settings-based endpoints for unified permission access
@targets_bp.route('/settings/targets', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_targets():
    """Get targets via settings permission"""
    return get_targets()

@targets_bp.route('/settings/targets', methods=['POST'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_create_target():
    """Create target via settings permission"""
    return create_target()

@targets_bp.route('/settings/targets/<int:target_id>', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_target(target_id):
    """Get target via settings permission"""
    return get_target(target_id)

@targets_bp.route('/settings/targets/<int:target_id>', methods=['PUT'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_update_target(target_id):
    """Update target via settings permission"""
    return update_target(target_id)

@targets_bp.route('/settings/targets/<int:target_id>', methods=['DELETE'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_delete_target(target_id):
    """Delete target via settings permission"""
    return delete_target(target_id)

@targets_bp.route('/settings/targets/stats', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_target_stats():
    """Get target stats via settings permission"""
    return get_target_stats()

