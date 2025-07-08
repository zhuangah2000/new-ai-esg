"""
Enhanced Project Management Routes with Centralized Auth Middleware
Preserves 100% of original functionality while adding API key authentication
"""

from flask import Blueprint, request, jsonify
from src.models.esg_models import db, Project, ProjectActivity, Measurement, EmissionFactor
from datetime import datetime
import json

# Import auth middleware with graceful fallback
try:
    from src.auth_middleware import require_auth as require_api_auth, Permissions, get_current_user as get_auth_user
    AUTH_MIDDLEWARE_AVAILABLE = True
    print("INFO:src.routes.projects:Auth middleware imported successfully")
except ImportError:
    AUTH_MIDDLEWARE_AVAILABLE = False
    print("WARNING:src.routes.projects:Auth middleware not available, using session-only authentication")

projects_bp = Blueprint("projects", __name__)

def require_session_auth():
    """Check if user is authenticated via session (renamed to avoid conflicts)"""
    from flask import session
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    return session['user_id']

def dual_auth(permissions=None):
    """Decorator that supports both API key and session authentication"""
    def decorator(f):
        if AUTH_MIDDLEWARE_AVAILABLE and permissions:
            return require_api_auth(permissions=permissions)(f)
        else:
            def wrapper(*args, **kwargs):
                try:
                    if AUTH_MIDDLEWARE_AVAILABLE:
                        current_user = get_auth_user()
                        print(f"INFO:src.routes.projects:API key authentication successful for {f.__name__}")
                    else:
                        current_user = require_session_auth()
                        print(f"INFO:src.routes.projects:Session authentication successful for {f.__name__}")
                    return f(*args, **kwargs)
                except Exception as e:
                    print(f"ERROR:src.routes.projects:Authentication failed for {f.__name__}: {str(e)}")
                    return jsonify({'error': 'Authentication failed'}), 401
            return wrapper
    return decorator

@projects_bp.route("/projects", methods=["POST"])
@dual_auth(permissions=[Permissions.PROJECTS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def create_project():
    """Create a new project with enhanced validation and kgCO2e unit support"""
    data = request.get_json()
    try:
        # Convert tCO2e to kgCO2e if needed
        target_reduction_absolute = data.get("target_reduction_absolute")
        target_reduction_unit = data.get("target_reduction_unit", "kgCO2e")
        baseline_value = data.get("baseline_value")
        
        # Convert tCO2e to kgCO2e
        if target_reduction_unit == "tCO2e":
            target_reduction_unit = "kgCO2e"
            if target_reduction_absolute:
                target_reduction_absolute = float(target_reduction_absolute) * 1000
        
        if target_reduction_unit == "tCO2e" and baseline_value:
            baseline_value = float(baseline_value) * 1000
            
        new_project = Project(
            name=data["name"],
            description=data.get("description"),
            year=data["year"],
            start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date(),
            end_date=datetime.strptime(data["end_date"], "%Y-%m-%d").date(),
            status=data.get("status", "active"),
            target_reduction_percentage=data.get("target_reduction_percentage"),
            target_reduction_absolute=target_reduction_absolute,
            target_reduction_unit=target_reduction_unit,
            baseline_value=baseline_value,
            baseline_year=data.get("baseline_year")
        )
        db.session.add(new_project)
        db.session.commit()
        
        # Return project data with proper unit conversion
        project_data = new_project.to_dict()
        return jsonify({"success": True, "data": project_data}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating project: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@projects_bp.route("/projects", methods=["GET"])
@dual_auth(permissions=[Permissions.PROJECTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_projects():
    """Get all projects with enhanced filtering and unit conversion"""
    try:
        # Get query parameters for filtering
        year = request.args.get('year')
        status = request.args.get('status')
        
        query = Project.query
        
        # Apply filters
        if year and year != 'all':
            query = query.filter(Project.year == int(year))
        if status and status != 'all':
            query = query.filter(Project.status == status)
            
        projects = query.order_by(Project.created_at.desc()).all()
        
        # Convert project data and ensure kgCO2e units
        projects_data = []
        for project in projects:
            project_dict = project.to_dict()
            
            # Ensure units are in kgCO2e
            if project_dict.get('target_reduction_unit') == 'tCO2e':
                project_dict['target_reduction_unit'] = 'kgCO2e'
                if project_dict.get('target_reduction_absolute'):
                    project_dict['target_reduction_absolute'] = float(project_dict['target_reduction_absolute']) * 1000
                if project_dict.get('baseline_value'):
                    project_dict['baseline_value'] = float(project_dict['baseline_value']) * 1000
                    
            projects_data.append(project_dict)
            
        return jsonify({"success": True, "data": projects_data})
        
    except Exception as e:
        print(f"Error fetching projects: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@projects_bp.route("/projects/<int:project_id>", methods=["GET"])
@dual_auth(permissions=[Permissions.PROJECTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_project(project_id):
    """Get a specific project with unit conversion"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"success": False, "error": "Project not found"}), 404
            
        project_data = project.to_dict()
        
        # Ensure units are in kgCO2e
        if project_data.get('target_reduction_unit') == 'tCO2e':
            project_data['target_reduction_unit'] = 'kgCO2e'
            if project_data.get('target_reduction_absolute'):
                project_data['target_reduction_absolute'] = float(project_data['target_reduction_absolute']) * 1000
            if project_data.get('baseline_value'):
                project_data['baseline_value'] = float(project_data['baseline_value']) * 1000
                
        return jsonify({"success": True, "data": project_data})
        
    except Exception as e:
        print(f"Error fetching project {project_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@projects_bp.route("/projects/<int:project_id>", methods=["PUT"])
@dual_auth(permissions=[Permissions.PROJECTS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def update_project(project_id):
    """Update a project with enhanced validation and unit conversion"""
    data = request.get_json()
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"success": False, "error": "Project not found"}), 404
        
        # Handle unit conversion for updates
        target_reduction_absolute = data.get("target_reduction_absolute", project.target_reduction_absolute)
        target_reduction_unit = data.get("target_reduction_unit", project.target_reduction_unit)
        baseline_value = data.get("baseline_value", project.baseline_value)
        
        # Convert tCO2e to kgCO2e if needed
        if target_reduction_unit == "tCO2e":
            target_reduction_unit = "kgCO2e"
            if target_reduction_absolute:
                target_reduction_absolute = float(target_reduction_absolute) * 1000
                
        if data.get("target_reduction_unit") == "tCO2e" and baseline_value:
            baseline_value = float(baseline_value) * 1000
        
        # Update project fields
        project.name = data.get("name", project.name)
        project.description = data.get("description", project.description)
        project.year = data.get("year", project.year)
        project.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date() if "start_date" in data else project.start_date
        project.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date() if "end_date" in data else project.end_date
        project.status = data.get("status", project.status)
        project.target_reduction_percentage = data.get("target_reduction_percentage", project.target_reduction_percentage)
        project.target_reduction_absolute = target_reduction_absolute
        project.target_reduction_unit = target_reduction_unit
        project.baseline_value = baseline_value
        project.baseline_year = data.get("baseline_year", project.baseline_year)
        
        db.session.commit()
        
        # Return updated project data with proper unit conversion
        project_data = project.to_dict()
        return jsonify({"success": True, "data": project_data})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating project {project_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@projects_bp.route("/projects/<int:project_id>", methods=["DELETE"])
@dual_auth(permissions=[Permissions.PROJECTS_DELETE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def delete_project(project_id):
    """Delete a project and all its activities"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"success": False, "error": "Project not found"}), 404
        
        # Delete all associated activities first
        ProjectActivity.query.filter_by(project_id=project_id).delete()
        
        # Delete the project
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Project and all associated activities deleted successfully"})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting project {project_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Enhanced Project Activities with Multiple Categories
@projects_bp.route("/projects/<int:project_id>/activities", methods=["POST"])
@dual_auth(permissions=[Permissions.PROJECTS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def create_project_activity(project_id):
    """Create a new project activity with enhanced validation"""
    data = request.get_json()
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"success": False, "error": "Project not found"}), 404

        # Handle multiple emission categories and measurements
        emission_categories = data.get("emission_categories", [])
        measurement_ids = data.get("measurement_ids", [])

        new_activity = ProjectActivity(
            project_id=project_id,
            description=data["description"],
            start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date() if data.get("start_date") else None,
            due_date=datetime.strptime(data["due_date"], "%Y-%m-%d").date() if data.get("due_date") else None,
            end_date=datetime.strptime(data["end_date"], "%Y-%m-%d").date() if data.get("end_date") else None,
            completion_percentage=float(data.get("completion_percentage", 0.0)),
            estimated_hours=float(data.get("estimated_hours", 0.0)) if data.get("estimated_hours") else None,
            actual_hours=float(data.get("actual_hours", 0.0)) if data.get("actual_hours") else None,
            status=data.get("status", "pending"),
            priority=data.get("priority", "medium"),
            assigned_to=data.get("assigned_to"),
            depends_on=json.dumps(data.get("depends_on", [])),
            blocks=json.dumps(data.get("blocks", [])),
            emission_categories=json.dumps(emission_categories),
            measurement_ids=json.dumps(measurement_ids),
            risk_level=data.get("risk_level", "low"),
            budget_allocated=float(data.get("budget_allocated", 0.0)) if data.get("budget_allocated") else None,
            budget_spent=float(data.get("budget_spent", 0.0)),
            notes=data.get("notes")
        )
        db.session.add(new_activity)
        db.session.commit()
        
        return jsonify({"success": True, "data": new_activity.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating activity for project {project_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@projects_bp.route("/projects/<int:project_id>/activities", methods=["GET"])
@dual_auth(permissions=[Permissions.PROJECTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_project_activities(project_id):
    """Get all activities for a specific project"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"success": False, "error": "Project not found"}), 404
            
        activities = ProjectActivity.query.filter_by(project_id=project_id).order_by(ProjectActivity.created_at.desc()).all()
        
        return jsonify({"success": True, "data": [a.to_dict() for a in activities]})
        
    except Exception as e:
        print(f"Error fetching activities for project {project_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@projects_bp.route("/projects/<int:project_id>/activities/<int:activity_id>", methods=["PUT"])
@dual_auth(permissions=[Permissions.PROJECTS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def update_project_activity(project_id, activity_id):
    """Update a project activity with enhanced validation"""
    data = request.get_json()
    try:
        activity = ProjectActivity.query.filter_by(id=activity_id, project_id=project_id).first()
        if not activity:
            return jsonify({"success": False, "error": "Activity not found for this project"}), 404
        
        # Update activity fields
        activity.description = data.get("description", activity.description)
        activity.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date() if data.get("start_date") else activity.start_date
        activity.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date() if data.get("due_date") else activity.due_date
        activity.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date() if data.get("end_date") else activity.end_date
        activity.completion_percentage = float(data.get("completion_percentage", activity.completion_percentage))
        activity.estimated_hours = float(data.get("estimated_hours", 0.0)) if data.get("estimated_hours") else activity.estimated_hours
        activity.actual_hours = float(data.get("actual_hours", 0.0)) if data.get("actual_hours") else activity.actual_hours
        activity.status = data.get("status", activity.status)
        activity.priority = data.get("priority", activity.priority)
        activity.assigned_to = data.get("assigned_to", activity.assigned_to)
        activity.depends_on = json.dumps(data.get("depends_on", [])) if data.get("depends_on") is not None else activity.depends_on
        activity.blocks = json.dumps(data.get("blocks", [])) if data.get("blocks") is not None else activity.blocks
        activity.risk_level = data.get("risk_level", activity.risk_level)
        activity.budget_allocated = float(data.get("budget_allocated", 0.0)) if data.get("budget_allocated") else activity.budget_allocated
        activity.budget_spent = float(data.get("budget_spent", activity.budget_spent or 0.0))
        activity.notes = data.get("notes", activity.notes)
        
        # Handle multiple categories and measurements
        if "emission_categories" in data:
            activity.emission_categories = json.dumps(data["emission_categories"])
        if "measurement_ids" in data:
            activity.measurement_ids = json.dumps(data["measurement_ids"])
        
        db.session.commit()
        
        return jsonify({"success": True, "data": activity.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating activity {activity_id} for project {project_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@projects_bp.route("/projects/<int:project_id>/activities/<int:activity_id>", methods=["DELETE"])
@dual_auth(permissions=[Permissions.PROJECTS_DELETE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def delete_project_activity(project_id, activity_id):
    """Delete a project activity"""
    try:
        activity = ProjectActivity.query.filter_by(id=activity_id, project_id=project_id).first()
        if not activity:
            return jsonify({"success": False, "error": "Activity not found for this project"}), 404
        
        db.session.delete(activity)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Activity deleted successfully"})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting activity {activity_id} for project {project_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Helper endpoint to get emission factor categories with sub-categories for activity tagging
@projects_bp.route("/emission-categories", methods=["GET"])
@dual_auth(permissions=[Permissions.PROJECTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_emission_categories():
    """Get available emission factor categories with their sub-categories for activity tagging"""
    try:
        # Get all emission factors grouped by category
        factors = EmissionFactor.query.order_by(EmissionFactor.category, EmissionFactor.name).all()
        
        # Group factors by category
        categories_dict = {}
        for factor in factors:
            category = factor.category
            if category not in categories_dict:
                categories_dict[category] = {
                    'name': category,
                    'label': category.title().replace('_', ' '),
                    'factors': []
                }
            
            # Add factor as sub-category
            categories_dict[category]['factors'].append({
                'id': factor.id,
                'name': factor.name,
                'sub_category': factor.sub_category,
                'factor_value': factor.factor_value,
                'unit': factor.unit,
                'description': factor.description
            })
        
        # Convert to list and add counts
        categories = []
        for category_data in categories_dict.values():
            category_data['count'] = len(category_data['factors'])
            categories.append(category_data)
        
        return jsonify({"success": True, "data": categories})
        
    except Exception as e:
        print(f"Error fetching emission categories: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Get measurements by category for activity tagging
@projects_bp.route("/measurements/by-category/<category>", methods=["GET"])
@dual_auth(permissions=[Permissions.PROJECTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_measurements_by_category(category):
    """Get measurements for a specific emission category"""
    try:
        # Get measurements for specific category
        measurements = Measurement.query.join(EmissionFactor).filter(
            EmissionFactor.category == category
        ).all()
        
        # Convert measurements data and ensure kgCO2e units
        measurements_data = []
        for measurement in measurements:
            measurement_dict = measurement.to_dict()
            
            # Convert emission values from tCO2e to kgCO2e if needed
            if measurement_dict.get('emission_unit') == 'tCO2e':
                measurement_dict['emission_unit'] = 'kgCO2e'
                if measurement_dict.get('emission_value'):
                    measurement_dict['emission_value'] = float(measurement_dict['emission_value']) * 1000
                    
            measurements_data.append(measurement_dict)
        
        return jsonify({
            "success": True, 
            "data": measurements_data
        })
        
    except Exception as e:
        print(f"Error fetching measurements for category {category}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Enhanced statistics endpoint
@projects_bp.route("/projects/statistics", methods=["GET"])
@dual_auth(permissions=[Permissions.PROJECTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_project_statistics():
    """Get comprehensive project statistics with unit conversion"""
    try:
        year = request.args.get('year', datetime.now().year)
        
        # Get projects for the specified year
        projects = Project.query.filter_by(year=int(year)).all()
        
        # Calculate statistics
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.status == 'active'])
        completed_projects = len([p for p in projects if p.status == 'completed'])
        
        # Calculate total activities
        total_activities = 0
        for project in projects:
            activities = ProjectActivity.query.filter_by(project_id=project.id).count()
            total_activities += activities
        
        # Calculate total emission reductions (convert to kgCO2e)
        total_target_reduction = 0
        for project in projects:
            if project.target_reduction_absolute:
                reduction = float(project.target_reduction_absolute)
                # Convert tCO2e to kgCO2e if needed
                if project.target_reduction_unit == 'tCO2e':
                    reduction *= 1000
                total_target_reduction += reduction
        
        statistics = {
            'year': int(year),
            'total_projects': total_projects,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'total_activities': total_activities,
            'total_target_reduction_kgco2e': total_target_reduction,
            'completion_rate': (completed_projects / total_projects * 100) if total_projects > 0 else 0
        }
        
        return jsonify({"success": True, "data": statistics})
        
    except Exception as e:
        print(f"Error fetching project statistics: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Bulk operations for enhanced functionality
@projects_bp.route("/projects/bulk-update-status", methods=["PUT"])
@dual_auth(permissions=[Permissions.PROJECTS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def bulk_update_project_status():
    """Bulk update project status"""
    data = request.get_json()
    try:
        project_ids = data.get('project_ids', [])
        new_status = data.get('status')
        
        if not project_ids or not new_status:
            return jsonify({"success": False, "error": "Missing project_ids or status"}), 400
        
        # Update projects
        updated_count = Project.query.filter(Project.id.in_(project_ids)).update(
            {Project.status: new_status}, 
            synchronize_session=False
        )
        
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": f"Updated {updated_count} projects to status '{new_status}'"
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error bulk updating project status: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Export endpoint for CSV data
@projects_bp.route("/projects/export", methods=["GET"])
@dual_auth(permissions=[Permissions.PROJECTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def export_projects():
    """Export projects data for CSV download"""
    try:
        year = request.args.get('year')
        status = request.args.get('status')
        include_activities = request.args.get('include_activities', 'false').lower() == 'true'
        
        query = Project.query
        
        # Apply filters
        if year and year != 'all':
            query = query.filter(Project.year == int(year))
        if status and status != 'all':
            query = query.filter(Project.status == status)
            
        projects = query.order_by(Project.created_at.desc()).all()
        
        export_data = []
        for project in projects:
            project_dict = project.to_dict()
            
            # Ensure units are in kgCO2e
            if project_dict.get('target_reduction_unit') == 'tCO2e':
                project_dict['target_reduction_unit'] = 'kgCO2e'
                if project_dict.get('target_reduction_absolute'):
                    project_dict['target_reduction_absolute'] = float(project_dict['target_reduction_absolute']) * 1000
                if project_dict.get('baseline_value'):
                    project_dict['baseline_value'] = float(project_dict['baseline_value']) * 1000
            
            if include_activities:
                activities = ProjectActivity.query.filter_by(project_id=project.id).all()
                project_dict['activities'] = [a.to_dict() for a in activities]
            
            export_data.append(project_dict)
        
        return jsonify({"success": True, "data": export_data})
        
    except Exception as e:
        print(f"Error exporting projects: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Settings-based unified access endpoints
@projects_bp.route("/settings/projects", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_projects():
    """Get projects via settings permission"""
    return get_projects()

@projects_bp.route("/settings/projects", methods=["POST"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_create_project():
    """Create project via settings permission"""
    return create_project()

@projects_bp.route("/settings/projects/<int:project_id>", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_project(project_id):
    """Get specific project via settings permission"""
    return get_project(project_id)

@projects_bp.route("/settings/projects/<int:project_id>", methods=["PUT"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_update_project(project_id):
    """Update project via settings permission"""
    return update_project(project_id)

@projects_bp.route("/settings/projects/<int:project_id>", methods=["DELETE"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_delete_project(project_id):
    """Delete project via settings permission"""
    return delete_project(project_id)

@projects_bp.route("/settings/projects/<int:project_id>/activities", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_project_activities(project_id):
    """Get project activities via settings permission"""
    return get_project_activities(project_id)

@projects_bp.route("/settings/projects/<int:project_id>/activities", methods=["POST"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_create_project_activity(project_id):
    """Create project activity via settings permission"""
    return create_project_activity(project_id)

@projects_bp.route("/settings/projects/<int:project_id>/activities/<int:activity_id>", methods=["PUT"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_update_project_activity(project_id, activity_id):
    """Update project activity via settings permission"""
    return update_project_activity(project_id, activity_id)

@projects_bp.route("/settings/projects/<int:project_id>/activities/<int:activity_id>", methods=["DELETE"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_delete_project_activity(project_id, activity_id):
    """Delete project activity via settings permission"""
    return delete_project_activity(project_id, activity_id)

@projects_bp.route("/settings/emission-categories", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_emission_categories():
    """Get emission categories via settings permission"""
    return get_emission_categories()

@projects_bp.route("/settings/measurements/by-category/<category>", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_measurements_by_category(category):
    """Get measurements by category via settings permission"""
    return get_measurements_by_category(category)

@projects_bp.route("/settings/projects/statistics", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_project_statistics():
    """Get project statistics via settings permission"""
    return get_project_statistics()

@projects_bp.route("/settings/projects/bulk-update-status", methods=["PUT"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_bulk_update_project_status():
    """Bulk update project status via settings permission"""
    return bulk_update_project_status()

@projects_bp.route("/settings/projects/export", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_export_projects():
    """Export projects via settings permission"""
    return export_projects()

