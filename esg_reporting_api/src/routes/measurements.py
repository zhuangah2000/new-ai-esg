from flask import Blueprint, request, jsonify, session
from src.models.esg_models import db, Measurement, EmissionFactor, EmissionFactorRevision, User
from datetime import datetime
from sqlalchemy import func, desc
from functools import wraps

# Try to import auth middleware, graceful fallback if not available
try:
    from src.auth_middleware import require_auth as require_api_auth, Permissions, get_current_user as get_auth_user
    AUTH_MIDDLEWARE_AVAILABLE = True
    print("INFO:src.routes.measurements:Auth middleware imported successfully")
except ImportError:
    AUTH_MIDDLEWARE_AVAILABLE = False
    print("INFO:src.routes.measurements:Auth middleware not available, using session-only authentication")

measurements_bp = Blueprint('measurements', __name__)

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

def get_active_emission_factor_value(emission_factor_id):
    """Get the active revision value for an emission factor, fallback to base factor"""
    try:
        # First, try to get the active revision
        active_revision = EmissionFactorRevision.query.filter(
            EmissionFactorRevision.parent_factor_id == emission_factor_id,
            EmissionFactorRevision.is_active == True
        ).first()
        
        if active_revision:
            return active_revision.factor_value
        
        # Fallback to the base emission factor
        base_factor = EmissionFactor.query.get(emission_factor_id)
        if base_factor:
            return base_factor.factor_value
            
        return None
    except Exception as e:
        print(f"Error getting active emission factor value: {str(e)}")
        return None

@measurements_bp.route('/measurements', methods=['GET'])
@dual_auth(permissions=[Permissions.MEASUREMENTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_measurements():
    """Get all measurements with optional filtering"""
    try:
        # Get query parameters for filtering
        category = request.args.get('category')
        location = request.args.get('location')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        year = request.args.get('year')
        month = request.args.get('month')
        
        # Build query
        query = Measurement.query
        
        if category:
            query = query.filter(Measurement.category.ilike(f'%{category}%'))
        if location:
            query = query.filter(Measurement.location.ilike(f'%{location}%'))
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Measurement.date >= start_date_obj)
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Measurement.date <= end_date_obj)
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
        
        # Filter by year
        if year:
            try:
                year_int = int(year)
                query = query.filter(func.extract('year', Measurement.date) == year_int)
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid year format'}), 400
        
        # Filter by month
        if month:
            try:
                month_int = int(month)
                query = query.filter(func.extract('month', Measurement.date) == month_int)
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid month format'}), 400
        
        # Order by date descending
        query = query.order_by(Measurement.date.desc())
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)  # Increased default
        
        # Execute query with pagination
        paginated_measurements = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Enhanced measurement data with active emission factor info
        measurements_data = []
        for measurement in paginated_measurements.items:
            measurement_dict = measurement.to_dict()
            
            # Get emission factor info with active revision details
            if measurement.emission_factor_id:
                emission_factor = EmissionFactor.query.get(measurement.emission_factor_id)
                if emission_factor:
                    # Get revision count
                    revision_count = EmissionFactorRevision.query.filter(
                        EmissionFactorRevision.parent_factor_id == emission_factor.id
                    ).count()
                    
                    # Get active revision
                    active_revision = EmissionFactorRevision.query.filter(
                        EmissionFactorRevision.parent_factor_id == emission_factor.id,
                        EmissionFactorRevision.is_active == True
                    ).first()
                    
                    # Get current version (latest version number)
                    current_version = db.session.query(func.max(EmissionFactorRevision.version)).filter(
                        EmissionFactorRevision.parent_factor_id == emission_factor.id
                    ).scalar() or 1
                    
                    # Use active revision data if available, otherwise base factor
                    if active_revision:
                        factor_info = {
                            'id': emission_factor.id,
                            'name': active_revision.name,
                            'category': active_revision.category,
                            'sub_category': active_revision.sub_category,
                            'factor_value': float(active_revision.factor_value),
                            'unit': active_revision.unit,
                            'source': active_revision.source,
                            'revision_count': revision_count,
                            'current_revision': active_revision.version,
                            'is_using_revision': True
                        }
                        # Recalculate emissions using active revision
                        measurement_dict['calculated_emissions'] = measurement.amount * active_revision.factor_value
                    else:
                        factor_info = {
                            'id': emission_factor.id,
                            'name': emission_factor.name,
                            'category': emission_factor.category,
                            'sub_category': emission_factor.sub_category,
                            'factor_value': float(emission_factor.factor_value),
                            'unit': emission_factor.unit,
                            'source': emission_factor.source,
                            'revision_count': revision_count,
                            'current_revision': current_version,
                            'is_using_revision': False
                        }
                    
                    measurement_dict['emission_factor'] = factor_info
        
            measurements_data.append(measurement_dict)
        
        return jsonify({
            'success': True,
            'data': measurements_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated_measurements.total,
                'pages': paginated_measurements.pages
            }
        })
    except Exception as e:
        print(f"Error fetching measurements: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@measurements_bp.route('/measurements', methods=['POST'])
@dual_auth(permissions=[Permissions.MEASUREMENTS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def create_measurement():
    """Create a new measurement using active emission factor revision"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['date', 'category', 'amount', 'unit', 'emission_factor_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Parse date
        try:
            measurement_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Validate emission factor exists
        emission_factor = EmissionFactor.query.get(data['emission_factor_id'])
        if not emission_factor:
            return jsonify({'success': False, 'error': 'Invalid emission factor ID'}), 400
        
        # Get active emission factor value (from revision if available)
        active_factor_value = get_active_emission_factor_value(data['emission_factor_id'])
        if active_factor_value is None:
            return jsonify({'success': False, 'error': 'Could not determine emission factor value'}), 400
        
        # Calculate emissions using active factor value
        calculated_emissions = data['amount'] * active_factor_value
        
        # Create new measurement
        measurement = Measurement(
            date=measurement_date,
            location=data.get('location'),
            category=data['category'],
            sub_category=data.get('sub_category'),
            amount=data['amount'],
            unit=data['unit'],
            emission_factor_id=data['emission_factor_id'],
            calculated_emissions=calculated_emissions,
            notes=data.get('notes')
        )
        
        db.session.add(measurement)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': measurement.to_dict(),
            'message': f'Measurement created successfully using active emission factor (value: {active_factor_value})'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating measurement: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@measurements_bp.route('/measurements/<int:measurement_id>', methods=['GET'])
@dual_auth(permissions=[Permissions.MEASUREMENTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_measurement(measurement_id):
    """Get a specific measurement by ID"""
    try:
        measurement = Measurement.query.get_or_404(measurement_id)
        measurement_dict = measurement.to_dict()
        
        # Add emission factor details with active revision info
        if measurement.emission_factor_id:
            emission_factor = EmissionFactor.query.get(measurement.emission_factor_id)
            if emission_factor:
                # Get active revision info
                active_revision = EmissionFactorRevision.query.filter(
                    EmissionFactorRevision.parent_factor_id == emission_factor.id,
                    EmissionFactorRevision.is_active == True
                ).first()
                
                revision_count = EmissionFactorRevision.query.filter(
                    EmissionFactorRevision.parent_factor_id == emission_factor.id
                ).count()
                
                if active_revision:
                    factor_info = {
                        'id': emission_factor.id,
                        'name': active_revision.name,
                        'category': active_revision.category,
                        'factor_value': float(active_revision.factor_value),
                        'unit': active_revision.unit,
                        'source': active_revision.source,
                        'revision_count': revision_count,
                        'current_revision': active_revision.version,
                        'is_using_revision': True
                    }
                else:
                    factor_info = emission_factor.to_dict()
                    factor_info['revision_count'] = revision_count
                    factor_info['is_using_revision'] = False
                
                measurement_dict['emission_factor'] = factor_info
        
        return jsonify({
            'success': True,
            'data': measurement_dict
        })
    except Exception as e:
        print(f"Error fetching measurement: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@measurements_bp.route('/measurements/<int:measurement_id>', methods=['PUT'])
@dual_auth(permissions=[Permissions.MEASUREMENTS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def update_measurement(measurement_id):
    """Update an existing measurement using active emission factor revision"""
    try:
        measurement = Measurement.query.get_or_404(measurement_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'date' in data:
            try:
                measurement.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        if 'location' in data:
            measurement.location = data['location']
        if 'category' in data:
            measurement.category = data['category']
        if 'sub_category' in data:
            measurement.sub_category = data['sub_category']
        if 'amount' in data:
            measurement.amount = data['amount']
        if 'unit' in data:
            measurement.unit = data['unit']
        if 'emission_factor_id' in data:
            # Validate emission factor exists
            emission_factor = EmissionFactor.query.get(data['emission_factor_id'])
            if not emission_factor:
                return jsonify({'success': False, 'error': 'Invalid emission factor ID'}), 400
            measurement.emission_factor_id = data['emission_factor_id']
        if 'notes' in data:
            measurement.notes = data['notes']
        
        # Recalculate emissions if amount or emission factor changed using active revision
        if 'amount' in data or 'emission_factor_id' in data:
            active_factor_value = get_active_emission_factor_value(measurement.emission_factor_id)
            if active_factor_value is not None:
                measurement.calculated_emissions = measurement.amount * active_factor_value
            else:
                return jsonify({'success': False, 'error': 'Could not determine emission factor value'}), 400
        
        measurement.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': measurement.to_dict(),
            'message': 'Measurement updated successfully using active emission factor'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating measurement: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@measurements_bp.route('/measurements/<int:measurement_id>', methods=['DELETE'])
@dual_auth(permissions=[Permissions.MEASUREMENTS_DELETE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def delete_measurement(measurement_id):
    """Delete a measurement"""
    try:
        measurement = Measurement.query.get_or_404(measurement_id)
        
        db.session.delete(measurement)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Measurement deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting measurement: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@measurements_bp.route('/measurements/summary', methods=['GET'])
@dual_auth(permissions=[Permissions.MEASUREMENTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_measurements_summary():
    """Get summary statistics for measurements using active emission factors"""
    try:
        # Get date range parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        year = request.args.get('year')
        month = request.args.get('month')
        
        # Build base query
        query = Measurement.query
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Measurement.date >= start_date_obj)
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Measurement.date <= end_date_obj)
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
        if year:
            try:
                year_int = int(year)
                query = query.filter(func.extract('year', Measurement.date) == year_int)
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid year format'}), 400
        if month:
            try:
                month_int = int(month)
                query = query.filter(func.extract('month', Measurement.date) == month_int)
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid month format'}), 400
        
        # Get all measurements in the filtered range
        measurements = query.all()
        
        # Recalculate emissions using active factors
        total_emissions = 0
        scope_emissions = {1: 0, 2: 0, 3: 0}
        category_emissions = {}
        
        for measurement in measurements:
            # Get active emission factor value
            active_factor_value = get_active_emission_factor_value(measurement.emission_factor_id)
            if active_factor_value:
                # Recalculate emissions using active factor
                emissions = measurement.amount * active_factor_value
                total_emissions += emissions
                
                # Get emission factor for scope and category info
                emission_factor = EmissionFactor.query.get(measurement.emission_factor_id)
                if emission_factor:
                    # Add to scope emissions
                    scope_emissions[emission_factor.scope] += emissions
                    
                    # Add to category emissions
                    category = measurement.category
                    if category:
                        category_emissions[category] = category_emissions.get(category, 0) + emissions
        
        # Round values
        total_emissions = round(total_emissions, 2)
        scope_emissions = {f'scope_{k}': round(v, 2) for k, v in scope_emissions.items()}
        category_emissions = {k: round(v, 2) for k, v in category_emissions.items()}
        
        # Get total measurements count
        total_measurements = len(measurements)
        
        return jsonify({
            'success': True,
            'data': {
                'scope_emissions': scope_emissions,
                'category_emissions': category_emissions,
                'total_measurements': total_measurements,
                'total_emissions': total_emissions,
                'note': 'Emissions calculated using active emission factor revisions'
            }
        })
        
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@measurements_bp.route('/measurements/recalculate', methods=['POST'])
@dual_auth(permissions=[Permissions.MEASUREMENTS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def recalculate_all_emissions():
    """Recalculate all measurement emissions using current active emission factors"""
    try:
        measurements = Measurement.query.all()
        updated_count = 0
        
        for measurement in measurements:
            active_factor_value = get_active_emission_factor_value(measurement.emission_factor_id)
            if active_factor_value:
                old_emissions = measurement.calculated_emissions
                new_emissions = measurement.amount * active_factor_value
                
                if abs(old_emissions - new_emissions) > 0.001:  # Only update if there's a meaningful difference
                    measurement.calculated_emissions = new_emissions
                    measurement.updated_at = datetime.utcnow()
                    updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Recalculated emissions for {updated_count} measurements using active emission factors',
            'updated_count': updated_count,
            'total_measurements': len(measurements)
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error recalculating emissions: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# Settings-based unified access endpoints
@measurements_bp.route('/settings/measurements', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_measurements():
    """Get measurements via settings permission"""
    return get_measurements()

@measurements_bp.route('/settings/measurements', methods=['POST'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_create_measurement():
    """Create measurement via settings permission"""
    return create_measurement()

@measurements_bp.route('/settings/measurements/<int:measurement_id>', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_measurement(measurement_id):
    """Get specific measurement via settings permission"""
    return get_measurement(measurement_id)

@measurements_bp.route('/settings/measurements/<int:measurement_id>', methods=['PUT'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_update_measurement(measurement_id):
    """Update measurement via settings permission"""
    return update_measurement(measurement_id)

@measurements_bp.route('/settings/measurements/<int:measurement_id>', methods=['DELETE'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_delete_measurement(measurement_id):
    """Delete measurement via settings permission"""
    return delete_measurement(measurement_id)

@measurements_bp.route('/settings/measurements/summary', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_measurements_summary():
    """Get measurements summary via settings permission"""
    return get_measurements_summary()

@measurements_bp.route('/settings/measurements/recalculate', methods=['POST'])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_recalculate_all_emissions():
    """Recalculate all emissions via settings permission"""
    return recalculate_all_emissions()
