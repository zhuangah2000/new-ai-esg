from flask import Blueprint, request, jsonify, session
from src.models.esg_models import db, ESGTarget, Measurement, EmissionFactor, User
from datetime import datetime, date
from sqlalchemy import func, extract
from functools import wraps

# Try to import auth middleware, graceful fallback if not available
try:
    from src.auth_middleware import require_auth as require_api_auth, Permissions, get_current_user as get_auth_user
    AUTH_MIDDLEWARE_AVAILABLE = True
    print("INFO:src.routes.dashboard:Auth middleware imported successfully")
except ImportError:
    AUTH_MIDDLEWARE_AVAILABLE = False
    print("INFO:src.routes.dashboard:Auth middleware not available, using session-only authentication")

dashboard_bp = Blueprint('dashboard', __name__)

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

@dashboard_bp.route('/dashboard/overview', methods=['GET'])
@dual_auth(permissions=[Permissions.DASHBOARD_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_dashboard_overview():
    """Get overview data for the main dashboard"""
    try:
        # Get date range parameters (default to current year)
        current_year = date.today().year
        year = request.args.get('year', current_year, type=int)
        
        # Calculate date range for the year
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        # Get total emissions by scope for the year
        scope_emissions = {}
        total_emissions = 0
        
        for scope in [1, 2, 3]:
            scope_query = db.session.query(func.sum(Measurement.calculated_emissions)).join(
                EmissionFactor
            ).filter(
                EmissionFactor.scope == scope,
                Measurement.date >= start_date,
                Measurement.date <= end_date
            ).scalar() or 0
            
            scope_emissions[f'scope_{scope}'] = round(scope_query, 2)
            total_emissions += scope_query
        
        # Get emissions by category
        category_emissions = {}
        category_query = db.session.query(
            Measurement.category,
            func.sum(Measurement.calculated_emissions)
        ).filter(
            Measurement.date >= start_date,
            Measurement.date <= end_date
        ).group_by(Measurement.category).all()
        
        for category, emissions in category_query:
            if category and emissions:
                category_emissions[category] = round(emissions, 2)
        
        # Get monthly emissions trend
        monthly_emissions = []
        for month in range(1, 13):
            month_start = date(year, month, 1)
            if month == 12:
                month_end = date(year + 1, 1, 1)
            else:
                month_end = date(year, month + 1, 1)
            
            month_total = db.session.query(func.sum(Measurement.calculated_emissions)).filter(
                Measurement.date >= month_start,
                Measurement.date < month_end
            ).scalar() or 0
            
            monthly_emissions.append({
                'month': month,
                'emissions': round(month_total, 2)
            })
        
        # Get recent measurements (last 10)
        recent_measurements = Measurement.query.order_by(
            Measurement.created_at.desc()
        ).limit(10).all()
        
        # Get active targets progress
        active_targets = ESGTarget.query.filter_by(status='active').all()
        targets_summary = []
        
        for target in active_targets:
            # Calculate current progress based on current year data
            if target.target_type == 'emissions_reduction' and target.scope:
                current_emissions = db.session.query(func.sum(Measurement.calculated_emissions)).join(
                    EmissionFactor
                ).filter(
                    EmissionFactor.scope == target.scope,
                    Measurement.date >= start_date,
                    Measurement.date <= end_date
                ).scalar() or 0
                
                # Calculate progress percentage
                if target.baseline_value > 0:
                    reduction_achieved = target.baseline_value - current_emissions
                    target_reduction = target.baseline_value - target.target_value
                    if target_reduction > 0:
                        progress = (reduction_achieved / target_reduction) * 100
                        target.progress_percentage = max(0, min(100, progress))
                        target.current_value = current_emissions
            
            targets_summary.append({
                'id': target.id,
                'name': target.name,
                'progress_percentage': round(target.progress_percentage, 1),
                'status': target.status,
                'target_year': target.target_year
            })
        
        # Update targets in database
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'scope_emissions': scope_emissions,
                'total_emissions': round(total_emissions, 2),
                'category_emissions': category_emissions,
                'monthly_trend': monthly_emissions,
                'recent_measurements': [m.to_dict() for m in recent_measurements],
                'targets_summary': targets_summary,
                'year': year
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/dashboard/emissions-trend', methods=['GET'])
@dual_auth(permissions=[Permissions.DASHBOARD_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_emissions_trend():
    """Get emissions trend data for charts"""
    try:
        # Get parameters
        period = request.args.get('period', 'monthly')  # monthly, quarterly, yearly
        years = request.args.get('years', 1, type=int)  # number of years to include
        scope = request.args.get('scope', type=int)  # optional scope filter
        
        current_year = date.today().year
        start_year = current_year - years + 1
        
        trend_data = []
        
        if period == 'monthly':
            for year in range(start_year, current_year + 1):
                for month in range(1, 13):
                    month_start = date(year, month, 1)
                    if month == 12:
                        month_end = date(year + 1, 1, 1)
                    else:
                        month_end = date(year, month + 1, 1)
                    
                    query = db.session.query(func.sum(Measurement.calculated_emissions))
                    
                    if scope:
                        query = query.join(EmissionFactor).filter(EmissionFactor.scope == scope)
                    
                    month_total = query.filter(
                        Measurement.date >= month_start,
                        Measurement.date < month_end
                    ).scalar() or 0
                    
                    trend_data.append({
                        'period': f'{year}-{month:02d}',
                        'year': year,
                        'month': month,
                        'emissions': round(month_total, 2)
                    })
        
        elif period == 'quarterly':
            for year in range(start_year, current_year + 1):
                for quarter in range(1, 5):
                    quarter_start_month = (quarter - 1) * 3 + 1
                    quarter_start = date(year, quarter_start_month, 1)
                    
                    if quarter == 4:
                        quarter_end = date(year + 1, 1, 1)
                    else:
                        quarter_end = date(year, quarter_start_month + 3, 1)
                    
                    query = db.session.query(func.sum(Measurement.calculated_emissions))
                    
                    if scope:
                        query = query.join(EmissionFactor).filter(EmissionFactor.scope == scope)
                    
                    quarter_total = query.filter(
                        Measurement.date >= quarter_start,
                        Measurement.date < quarter_end
                    ).scalar() or 0
                    
                    trend_data.append({
                        'period': f'{year}-Q{quarter}',
                        'year': year,
                        'quarter': quarter,
                        'emissions': round(quarter_total, 2)
                    })
        
        elif period == 'yearly':
            for year in range(start_year, current_year + 1):
                year_start = date(year, 1, 1)
                year_end = date(year + 1, 1, 1)
                
                query = db.session.query(func.sum(Measurement.calculated_emissions))
                
                if scope:
                    query = query.join(EmissionFactor).filter(EmissionFactor.scope == scope)
                
                year_total = query.filter(
                    Measurement.date >= year_start,
                    Measurement.date < year_end
                ).scalar() or 0
                
                trend_data.append({
                    'period': str(year),
                    'year': year,
                    'emissions': round(year_total, 2)
                })
        
        return jsonify({
            'success': True,
            'data': {
                'trend_data': trend_data,
                'period': period,
                'scope': scope,
                'years': years
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/dashboard/intensity-metrics', methods=['GET'])
@dual_auth(permissions=[Permissions.DASHBOARD_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_intensity_metrics():
    """Get emission intensity metrics"""
    try:
        year = request.args.get('year', date.today().year, type=int)
        
        # Get total emissions for the year
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        total_emissions = db.session.query(func.sum(Measurement.calculated_emissions)).filter(
            Measurement.date >= start_date,
            Measurement.date <= end_date
        ).scalar() or 0
        
        # These would typically come from business metrics stored in the database
        # For now, we'll return placeholder data that could be populated from other systems
        intensity_metrics = {
            'emissions_per_revenue': {
                'value': 0,  # Would be calculated as total_emissions / annual_revenue
                'unit': 'tCO2e/million USD',
                'description': 'Total emissions per million USD revenue'
            },
            'emissions_per_employee': {
                'value': 0,  # Would be calculated as total_emissions / employee_count
                'unit': 'tCO2e/employee',
                'description': 'Total emissions per employee'
            },
            'emissions_per_sqft': {
                'value': 0,  # Would be calculated as total_emissions / facility_sqft
                'unit': 'tCO2e/sqft',
                'description': 'Total emissions per square foot of facility'
            }
        }
        
        return jsonify({
            'success': True,
            'data': {
                'total_emissions': round(total_emissions, 2),
                'intensity_metrics': intensity_metrics,
                'year': year,
                'note': 'Intensity metrics require business data (revenue, employees, facility size) to be configured'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/dashboard/targets-progress', methods=['GET'])
@dual_auth(permissions=[Permissions.DASHBOARD_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_targets_progress():
    """Get detailed progress on ESG targets"""
    try:
        targets = ESGTarget.query.filter_by(status='active').all()
        targets_data = []
        
        current_year = date.today().year
        
        for target in targets:
            target_data = target.to_dict()
            
            # Calculate current progress for emission reduction targets
            if target.target_type == 'emissions_reduction' and target.scope:
                start_date = date(current_year, 1, 1)
                end_date = date(current_year, 12, 31)
                
                current_emissions = db.session.query(func.sum(Measurement.calculated_emissions)).join(
                    EmissionFactor
                ).filter(
                    EmissionFactor.scope == target.scope,
                    Measurement.date >= start_date,
                    Measurement.date <= end_date
                ).scalar() or 0
                
                target_data['current_value'] = round(current_emissions, 2)
                
                # Calculate progress percentage
                if target.baseline_value > 0:
                    reduction_achieved = target.baseline_value - current_emissions
                    target_reduction = target.baseline_value - target.target_value
                    if target_reduction > 0:
                        progress = (reduction_achieved / target_reduction) * 100
                        target_data['progress_percentage'] = max(0, min(100, round(progress, 1)))
                    
                    # Determine status based on progress and timeline
                    years_remaining = target.target_year - current_year
                    if years_remaining <= 0:
                        if current_emissions <= target.target_value:
                            target_data['status'] = 'achieved'
                        else:
                            target_data['status'] = 'missed'
                    elif progress < (100 * (current_year - target.baseline_year) / (target.target_year - target.baseline_year)):
                        target_data['status'] = 'at_risk'
                    else:
                        target_data['status'] = 'on_track'
            
            targets_data.append(target_data)
        
        return jsonify({
            'success': True,
            'data': targets_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Settings-based unified access endpoints
@dashboard_bp.route('/settings/dashboard/overview', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_dashboard_overview():
    """Get dashboard overview via settings permission"""
    return get_dashboard_overview()

@dashboard_bp.route('/settings/dashboard/emissions-trend', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_emissions_trend():
    """Get emissions trend via settings permission"""
    return get_emissions_trend()

@dashboard_bp.route('/settings/dashboard/intensity-metrics', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_intensity_metrics():
    """Get intensity metrics via settings permission"""
    return get_intensity_metrics()

@dashboard_bp.route('/settings/dashboard/targets-progress', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_targets_progress():
    """Get targets progress via settings permission"""
    return get_targets_progress()

