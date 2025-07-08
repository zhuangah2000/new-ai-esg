from flask import Blueprint, request, jsonify, session
from src.models.esg_models import db, EmissionFactor, EmissionFactorRevision, User
from sqlalchemy import func, desc, text
from datetime import datetime
from functools import wraps

# Try to import auth middleware, graceful fallback if not available
try:
    from src.auth_middleware import require_auth as require_api_auth, Permissions, get_current_user as get_auth_user
    AUTH_MIDDLEWARE_AVAILABLE = True
    print("INFO:src.routes.emission_factors:Auth middleware imported successfully")
except ImportError:
    AUTH_MIDDLEWARE_AVAILABLE = False
    print("INFO:src.routes.emission_factors:Auth middleware not available, using session-only authentication")

emission_factors_bp = Blueprint('emission_factors', __name__)

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

# Helper decorator for dual authentication (session + API key) - FIXED VERSION
def dual_auth(permissions=None):
    """Decorator that supports both session and API key authentication"""
    def decorator(f):
        if AUTH_MIDDLEWARE_AVAILABLE and permissions:
            # Use the centralized auth system if available and permissions are specified
            return require_api_auth(permissions=permissions)(f)
        else:
            # Fallback to session-only authentication
            @wraps(f)
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

@emission_factors_bp.route('/emission-factors', methods=['GET'])
@dual_auth(permissions=[Permissions.EMISSION_FACTORS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_emission_factors():
    """Get all emission factors with their active revisions and revision counts"""
    try:
        # Get all emission factors with their revision counts
        factors = EmissionFactor.query.all()
        
        factors_list = []
        for factor in factors:
            # Count revisions for this factor
            revision_count = EmissionFactorRevision.query.filter(
                EmissionFactorRevision.parent_factor_id == factor.id
            ).count()
            
            # Get the active revision if it exists
            active_revision = EmissionFactorRevision.query.filter(
                EmissionFactorRevision.parent_factor_id == factor.id,
                EmissionFactorRevision.is_active == True
            ).first()
            
            # Get the latest version number
            latest_version = db.session.query(func.max(EmissionFactorRevision.version)).filter(
                EmissionFactorRevision.parent_factor_id == factor.id
            ).scalar() or 1

            # Use active revision data if available, otherwise use base factor data
            if active_revision:
                factor_data = {
                    'id': factor.id,
                    'name': active_revision.name,
                    'scope': active_revision.scope,
                    'category': active_revision.category,
                    'sub_category': active_revision.sub_category,
                    'factor_value': float(active_revision.factor_value),
                    'unit': active_revision.unit,
                    'source': active_revision.source,
                    'link': active_revision.link,
                    'effective_date': active_revision.effective_date.isoformat() if active_revision.effective_date else None,
                    'description': active_revision.description,
                    'revision_count': revision_count,
                    'current_revision': active_revision.version
                }
            else:
                factor_data = {
                    'id': factor.id,
                    'name': factor.name,
                    'scope': factor.scope,
                    'category': factor.category,
                    'sub_category': factor.sub_category,
                    'factor_value': float(factor.factor_value),
                    'unit': factor.unit,
                    'source': factor.source,
                    'link': getattr(factor, 'link', None),  # Safe access to link field
                    'effective_date': factor.effective_date.isoformat() if factor.effective_date else None,
                    'description': factor.description,
                    'revision_count': revision_count,
                    'current_revision': latest_version
                }
            
            factors_list.append(factor_data)

        return jsonify({
            'success': True,
            'data': factors_list,
            'count': len(factors_list)
        })

    except Exception as e:
        print(f"Error fetching emission factors: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emission_factors_bp.route('/emission-factors', methods=['POST'])
@dual_auth(permissions=[Permissions.EMISSION_FACTORS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def create_emission_factor():
    """Create a new emission factor"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'scope', 'category', 'factor_value', 'unit', 'source', 'effective_date']
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # Create new emission factor
        new_factor = EmissionFactor(
            name=data['name'],
            scope=int(data['scope']),
            category=data['category'],
            sub_category=data.get('sub_category'),
            factor_value=float(data['factor_value']),
            unit=data['unit'],
            source=data['source'],
            effective_date=datetime.fromisoformat(data['effective_date']),
            description=data.get('description'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add link if the field exists in the model
        if hasattr(new_factor, 'link'):
            new_factor.link = data.get('link')

        db.session.add(new_factor)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Emission factor created successfully',
            'data': {
                'id': new_factor.id,
                'name': new_factor.name
            }
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid data format: {str(e)}'
        }), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error creating emission factor: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emission_factors_bp.route('/emission-factors/<int:factor_id>/revisions', methods=['GET'])
@dual_auth(permissions=[Permissions.EMISSION_FACTORS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_revision_history(factor_id):
    """Get revision history for a specific emission factor"""
    try:
        # Check if factor exists
        factor = EmissionFactor.query.get(factor_id)
        if not factor:
            return jsonify({
                'success': False,
                'error': 'Emission factor not found'
            }), 404

        # Get all revisions for this factor, ordered by version descending
        revisions = EmissionFactorRevision.query.filter(
            EmissionFactorRevision.parent_factor_id == factor_id
        ).order_by(desc(EmissionFactorRevision.version)).all()

        revisions_list = []
        for revision in revisions:
            revision_data = {
                'id': revision.id,
                'parent_factor_id': revision.parent_factor_id,
                'name': revision.name,
                'scope': revision.scope,
                'category': revision.category,
                'sub_category': revision.sub_category,
                'factor_value': float(revision.factor_value),
                'unit': revision.unit,
                'source': revision.source,
                'link': getattr(revision, 'link', None),  # Safe access to link field
                'effective_date': revision.effective_date.isoformat() if revision.effective_date else None,
                'description': revision.description,
                'revision_notes': revision.revision_notes,
                'version': revision.version,
                'is_active': revision.is_active,
                'created_at': revision.created_at.isoformat() if revision.created_at else None,
                'created_by': revision.created_by
            }
            revisions_list.append(revision_data)

        return jsonify({
            'success': True,
            'data': revisions_list,
            'count': len(revisions_list)
        })

    except Exception as e:
        print(f"Error fetching revision history: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emission_factors_bp.route('/emission-factors/<int:factor_id>/revisions', methods=['POST'])
@dual_auth(permissions=[Permissions.EMISSION_FACTORS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def create_revision(factor_id):
    """Create a new revision for an existing emission factor"""
    try:
        data = request.get_json()
        
        # Check if factor exists
        factor = EmissionFactor.query.get(factor_id)
        if not factor:
            return jsonify({
                'success': False,
                'error': 'Emission factor not found'
            }), 404

        # Validate required fields
        required_fields = ['name', 'scope', 'category', 'factor_value', 'unit', 'source', 'effective_date', 'revision_notes']
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # Get the next version number
        max_version = db.session.query(func.max(EmissionFactorRevision.version)).filter(
            EmissionFactorRevision.parent_factor_id == factor_id
        ).scalar() or 0
        next_version = max_version + 1

        # Create new revision
        new_revision = EmissionFactorRevision(
            parent_factor_id=factor_id,
            name=data['name'],
            scope=int(data['scope']),
            category=data['category'],
            sub_category=data.get('sub_category'),
            factor_value=float(data['factor_value']),
            unit=data['unit'],
            source=data['source'],
            effective_date=datetime.fromisoformat(data['effective_date']),
            description=data.get('description'),
            revision_notes=data['revision_notes'],
            version=next_version,
            is_active=False,  # New revisions are not active by default
            created_at=datetime.utcnow(),
            created_by=data.get('created_by', 'System')
        )
        
        # Add link if the field exists in the model
        if hasattr(new_revision, 'link'):
            new_revision.link = data.get('link')

        db.session.add(new_revision)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Revision v{next_version} created successfully',
            'data': {
                'id': new_revision.id,
                'version': new_revision.version,
                'factor_id': factor_id
            }
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid data format: {str(e)}'
        }), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error creating revision: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emission_factors_bp.route('/emission-factors/revisions/<int:revision_id>/activate', methods=['POST'])
@dual_auth(permissions=[Permissions.EMISSION_FACTORS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def activate_revision(revision_id):
    """Activate a specific revision"""
    try:
        # Get the revision
        revision = EmissionFactorRevision.query.get(revision_id)
        if not revision:
            return jsonify({
                'success': False,
                'error': 'Revision not found'
            }), 404

        # Deactivate all other revisions for this factor
        EmissionFactorRevision.query.filter(
            EmissionFactorRevision.parent_factor_id == revision.parent_factor_id
        ).update({'is_active': False})

        # Activate this revision
        revision.is_active = True

        # Update the main factor with the active revision data
        factor = EmissionFactor.query.get(revision.parent_factor_id)
        if factor:
            factor.name = revision.name
            factor.scope = revision.scope
            factor.category = revision.category
            factor.sub_category = revision.sub_category
            factor.factor_value = revision.factor_value
            factor.unit = revision.unit
            factor.source = revision.source
            factor.effective_date = revision.effective_date
            factor.description = revision.description
            factor.updated_at = datetime.utcnow()
            
            # Update link if both models have the field
            if hasattr(factor, 'link') and hasattr(revision, 'link'):
                factor.link = revision.link

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Revision v{revision.version} activated successfully'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error activating revision: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emission_factors_bp.route('/emission-factors/revisions/<int:revision_id>', methods=['DELETE'])
@dual_auth(permissions=[Permissions.EMISSION_FACTORS_DELETE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def delete_revision(revision_id):
    """Delete a specific revision"""
    try:
        # Get the revision
        revision = EmissionFactorRevision.query.get(revision_id)
        if not revision:
            return jsonify({
                'success': False,
                'error': 'Revision not found'
            }), 404

        # Check if this is the active revision
        if revision.is_active:
            return jsonify({
                'success': False,
                'error': 'Cannot delete the active revision. Please activate another revision first.'
            }), 400

        # Check if this is the only revision
        revision_count = EmissionFactorRevision.query.filter(
            EmissionFactorRevision.parent_factor_id == revision.parent_factor_id
        ).count()
        
        if revision_count <= 1:
            return jsonify({
                'success': False,
                'error': 'Cannot delete the only revision. Each emission factor must have at least one revision.'
            }), 400

        # Delete the revision
        db.session.delete(revision)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Revision v{revision.version} deleted successfully'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error deleting revision: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emission_factors_bp.route('/emission-factors/<int:factor_id>', methods=['DELETE'])
@dual_auth(permissions=[Permissions.EMISSION_FACTORS_DELETE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def delete_emission_factor(factor_id):
    """Delete an emission factor and all its revisions"""
    try:
        # Get the factor
        factor = EmissionFactor.query.get(factor_id)
        if not factor:
            return jsonify({
                'success': False,
                'error': 'Emission factor not found'
            }), 404

        # Delete all revisions first (due to foreign key constraint)
        EmissionFactorRevision.query.filter(
            EmissionFactorRevision.parent_factor_id == factor_id
        ).delete()

        # Delete the factor
        db.session.delete(factor)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Emission factor and all revisions deleted successfully'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error deleting emission factor: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emission_factors_bp.route('/emission-factors/categories', methods=['GET'])
@dual_auth(permissions=[Permissions.EMISSION_FACTORS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_categories():
    """Get unique categories"""
    try:
        categories = db.session.query(EmissionFactor.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({
            'success': True,
            'data': sorted(category_list)
        })
    except Exception as e:
        print(f"Error fetching categories: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emission_factors_bp.route('/emission-factors/subcategories', methods=['GET'])
@dual_auth(permissions=[Permissions.EMISSION_FACTORS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_subcategories():
    """Get unique subcategories, optionally filtered by category"""
    try:
        category = request.args.get('category')
        
        query = db.session.query(EmissionFactor.sub_category).distinct()
        if category and category != 'all':
            query = query.filter(EmissionFactor.category == category)
        
        subcategories = query.all()
        subcategory_list = [subcat[0] for subcat in subcategories if subcat[0]]
        
        return jsonify({
            'success': True,
            'data': sorted(subcategory_list)
        })
    except Exception as e:
        print(f"Error fetching subcategories: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Settings-based unified access endpoints
@emission_factors_bp.route('/settings/emission-factors', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_emission_factors():
    """Get emission factors via settings permission"""
    return get_emission_factors()

@emission_factors_bp.route('/settings/emission-factors', methods=['POST'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_create_emission_factor():
    """Create emission factor via settings permission"""
    return create_emission_factor()

@emission_factors_bp.route('/settings/emission-factors/<int:factor_id>/revisions', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_revision_history(factor_id):
    """Get revision history via settings permission"""
    return get_revision_history(factor_id)

@emission_factors_bp.route('/settings/emission-factors/<int:factor_id>/revisions', methods=['POST'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_create_revision(factor_id):
    """Create revision via settings permission"""
    return create_revision(factor_id)

@emission_factors_bp.route('/settings/emission-factors/revisions/<int:revision_id>/activate', methods=['POST'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_activate_revision(revision_id):
    """Activate revision via settings permission"""
    return activate_revision(revision_id)

@emission_factors_bp.route('/settings/emission-factors/revisions/<int:revision_id>', methods=['DELETE'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_delete_revision(revision_id):
    """Delete revision via settings permission"""
    return delete_revision(revision_id)

@emission_factors_bp.route('/settings/emission-factors/<int:factor_id>', methods=['DELETE'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_delete_emission_factor(factor_id):
    """Delete emission factor via settings permission"""
    return delete_emission_factor(factor_id)

@emission_factors_bp.route('/settings/emission-factors/categories', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_categories():
    """Get categories via settings permission"""
    return get_categories()

@emission_factors_bp.route('/settings/emission-factors/subcategories', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_subcategories():
    """Get subcategories via settings permission"""
    return get_subcategories()

