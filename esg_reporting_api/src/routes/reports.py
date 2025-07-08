"""
Enhanced Reports Management Routes with Centralized Auth Middleware
Supports both session-based and API key authentication
COMPLETE VERSION - All original functionality preserved
"""

from flask import Blueprint, jsonify, request, send_file, session
from src.models.esg_models import db, Project, ProjectActivity, Measurement, EmissionFactor, ESGTarget, Supplier, SupplierData
from datetime import datetime, timedelta
from sqlalchemy import func, extract
import io
import logging
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

reports_bp = Blueprint('reports', __name__)

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

# ESG Framework configurations
ESG_FRAMEWORKS = {
    'gri': {
        'name': 'Global Reporting Initiative (GRI)',
        'description': 'Comprehensive sustainability reporting with stakeholder focus',
        'sections': ['governance', 'strategy', 'impacts', 'performance'],
        'focus': 'Comprehensive ESG impacts and stakeholder engagement'
    },
    'sasb': {
        'name': 'Sustainability Accounting Standards Board (SASB)',
        'description': 'Industry-specific financially material sustainability factors',
        'sections': ['governance', 'strategy', 'metrics', 'targets'],
        'focus': 'Financially material sustainability factors'
    },
    'tcfd': {
        'name': 'Task Force on Climate-related Financial Disclosures (TCFD)',
        'description': 'Climate-related risks and opportunities disclosure',
        'sections': ['governance', 'strategy', 'risk_management', 'metrics_targets'],
        'focus': 'Climate-related financial risks and opportunities'
    },
    'cdp': {
        'name': 'Carbon Disclosure Project (CDP)',
        'description': 'Environmental transparency and performance improvement',
        'sections': ['governance', 'risks_opportunities', 'business_strategy', 'targets_performance'],
        'focus': 'Environmental transparency and climate action'
    },
    'ifrs': {
        'name': 'IFRS Sustainability Disclosure Standards',
        'description': 'Global baseline for sustainability-related financial disclosures',
        'sections': ['governance', 'strategy', 'risk_management', 'metrics_targets'],
        'focus': 'Sustainability-related financial information'
    }
}

# ENHANCED: Get frameworks with dual authentication
@reports_bp.route('/reports/frameworks', methods=['GET'])
@dual_auth(permissions=[Permissions.REPORTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_frameworks():
    """Get available ESG reporting frameworks"""
    try:
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} accessing frameworks via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} accessing frameworks via session")
        
        logger.info("Fetching ESG reporting frameworks")
        return jsonify({'frameworks': ESG_FRAMEWORKS})
        
    except Exception as e:
        logger.error(f"Error fetching frameworks: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ENHANCED: Get comprehensive report with dual authentication
@reports_bp.route('/reports/comprehensive', methods=['GET'])
@dual_auth(permissions=[Permissions.REPORTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_comprehensive_report():
    """Get comprehensive report data for executive summary"""
    try:
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} generating comprehensive report via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} generating comprehensive report via session")
        
        year = request.args.get('year', datetime.now().year, type=int)
        framework = request.args.get('framework', 'gri')
        
        logger.info(f"Generating comprehensive report for year {year} using {framework} framework")
        
        # Key metrics - using calculated_emissions if available, otherwise calculate from factor_value
        total_emissions = db.session.query(
            func.sum(
                func.coalesce(
                    Measurement.calculated_emissions,
                    Measurement.amount * EmissionFactor.factor_value
                )
            )
        ).join(
            EmissionFactor, Measurement.emission_factor_id == EmissionFactor.id
        ).filter(extract('year', Measurement.date) == year).scalar() or 0
        
        active_targets = ESGTarget.query.filter_by(status='active').count()
        total_projects = Project.query.filter(extract('year', Project.start_date) == year).count()
        total_suppliers = Supplier.query.count()
        
        # Scope emissions breakdown
        scope_emissions = db.session.query(
            EmissionFactor.scope,
            func.sum(
                func.coalesce(
                    Measurement.calculated_emissions,
                    Measurement.amount * EmissionFactor.factor_value
                )
            ).label('total_emissions')
        ).join(Measurement, EmissionFactor.id == Measurement.emission_factor_id).filter(
            extract('year', Measurement.date) == year
        ).group_by(EmissionFactor.scope).all()
        
        scope_data = [{'scope': scope, 'emissions': float(emissions)} for scope, emissions in scope_emissions]
        
        # Category emissions breakdown
        category_emissions = db.session.query(
            EmissionFactor.category,
            func.sum(
                func.coalesce(
                    Measurement.calculated_emissions,
                    Measurement.amount * EmissionFactor.factor_value
                )
            ).label('total_emissions')
        ).join(Measurement, EmissionFactor.id == Measurement.emission_factor_id).filter(
            extract('year', Measurement.date) == year
        ).group_by(EmissionFactor.category).all()
        
        category_data = [{'category': category, 'emissions': float(emissions)} for category, emissions in category_emissions]
        
        # Monthly trend data
        monthly_emissions = db.session.query(
            extract('month', Measurement.date).label('month'),
            func.sum(
                func.coalesce(
                    Measurement.calculated_emissions,
                    Measurement.amount * EmissionFactor.factor_value
                )
            ).label('emissions')
        ).join(EmissionFactor, Measurement.emission_factor_id == EmissionFactor.id).filter(
            extract('year', Measurement.date) == year
        ).group_by(extract('month', Measurement.date)).order_by('month').all()
        
        trend_data = [{'month': int(month), 'emissions': float(emissions)} for month, emissions in monthly_emissions]
        
        logger.info(f"Successfully generated comprehensive report with {len(scope_data)} scope categories")
        
        return jsonify({
            'framework': ESG_FRAMEWORKS.get(framework, ESG_FRAMEWORKS['gri']),
            'summary': {
                'total_emissions': round(total_emissions, 2),
                'active_targets': active_targets,
                'total_projects': total_projects,
                'total_suppliers': total_suppliers
            },
            'scope_emissions': scope_data,
            'category_emissions': category_data,
            'monthly_trend': trend_data
        })
        
    except Exception as e:
        logger.error(f"Error in comprehensive report: {str(e)}")
        print(f"Error in comprehensive report: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ENHANCED: Get emissions report with dual authentication
@reports_bp.route('/reports/emissions', methods=['GET'])
@dual_auth(permissions=[Permissions.REPORTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_emissions_report():
    """Get detailed emissions analysis"""
    try:
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} generating emissions report via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} generating emissions report via session")
        
        year = request.args.get('year', datetime.now().year, type=int)
        
        logger.info(f"Generating emissions report for year {year}")
        
        # Scope breakdown with measurement counts
        scope_data = db.session.query(
            EmissionFactor.scope,
            func.sum(
                func.coalesce(
                    Measurement.calculated_emissions,
                    Measurement.amount * EmissionFactor.factor_value
                )
            ).label('total_emissions'),
            func.count(Measurement.id).label('measurement_count')
        ).join(Measurement, EmissionFactor.id == Measurement.emission_factor_id).filter(
            extract('year', Measurement.date) == year
        ).group_by(EmissionFactor.scope).all()
        
        scope_breakdown = [{
            'scope': scope,
            'emissions': round(float(emissions), 2),
            'measurement_count': count,
            'percentage': 0  # Will be calculated on frontend
        } for scope, emissions, count in scope_data]
        
        # Category breakdown with measurement counts
        category_data = db.session.query(
            EmissionFactor.category,
            func.sum(
                func.coalesce(
                    Measurement.calculated_emissions,
                    Measurement.amount * EmissionFactor.factor_value
                )
            ).label('total_emissions'),
            func.count(Measurement.id).label('measurement_count')
        ).join(Measurement, EmissionFactor.id == Measurement.emission_factor_id).filter(
            extract('year', Measurement.date) == year
        ).group_by(EmissionFactor.category).all()
        
        category_breakdown = [{
            'category': category,
            'emissions': round(float(emissions), 2),
            'measurement_count': count,
            'percentage': 0  # Will be calculated on frontend
        } for category, emissions, count in category_data]
        
        logger.info(f"Successfully generated emissions report with {len(scope_breakdown)} scopes and {len(category_breakdown)} categories")
        
        return jsonify({
            'scope_breakdown': scope_breakdown,
            'category_breakdown': category_breakdown
        })
        
    except Exception as e:
        logger.error(f"Error in emissions report: {str(e)}")
        print(f"Error in emissions report: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ENHANCED: Get targets report with dual authentication
@reports_bp.route('/reports/targets', methods=['GET'])
@dual_auth(permissions=[Permissions.REPORTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_targets_report():
    """Get ESG targets progress report"""
    try:
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} generating targets report via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} generating targets report via session")
        
        year = request.args.get('year', datetime.now().year, type=int)
        
        logger.info(f"Generating targets report for year {year}")
        
        # Get targets that are relevant to the year (target_year >= year)
        targets = ESGTarget.query.filter(
            ESGTarget.target_year >= year
        ).all()
        
        targets_data = []
        for target in targets:
            # Use the progress_percentage from the database if available
            if target.progress_percentage is not None:
                progress = target.progress_percentage
            else:
                # Calculate progress based on current vs baseline vs target
                if target.baseline_value and target.target_value and target.current_value:
                    if target.target_value > target.baseline_value:
                        # Increasing target (e.g., renewable energy %)
                        progress = ((target.current_value - target.baseline_value) / 
                                  (target.target_value - target.baseline_value)) * 100
                    else:
                        # Decreasing target (e.g., emissions reduction)
                        progress = ((target.baseline_value - target.current_value) / 
                                  (target.baseline_value - target.target_value)) * 100
                else:
                    progress = 0
            
            progress = max(0, min(100, progress))  # Clamp between 0-100
            
            # Determine status based on progress
            if progress >= 90:
                status = 'on-track'
            elif progress >= 50:
                status = 'at-risk'
            else:
                status = 'behind'
            
            targets_data.append({
                'id': target.id,
                'name': target.name,
                'description': target.description,
                'category': target.target_type,  # Using target_type as category
                'baseline_value': target.baseline_value,
                'current_value': target.current_value,
                'target_value': target.target_value,
                'unit': target.unit,
                'target_date': f"{target.target_year}-12-31",  # Convert year to date
                'baseline_year': target.baseline_year,
                'target_year': target.target_year,
                'status': status,
                'progress': round(progress, 1)
            })
        
        # Summary statistics
        total_targets = len(targets_data)
        on_track = len([t for t in targets_data if t['status'] == 'on-track'])
        at_risk = len([t for t in targets_data if t['status'] == 'at-risk'])
        
        logger.info(f"Successfully generated targets report with {total_targets} targets")
        
        return jsonify({
            'targets': targets_data,
            'summary': {
                'total': total_targets,
                'on_track': on_track,
                'at_risk': at_risk,
                'behind': total_targets - on_track - at_risk
            }
        })
        
    except Exception as e:
        logger.error(f"Error in targets report: {str(e)}")
        print(f"Error in targets report: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ENHANCED: Get projects report with dual authentication
@reports_bp.route('/reports/projects', methods=['GET'])
@dual_auth(permissions=[Permissions.REPORTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_projects_report():
    """Get projects status and progress report"""
    try:
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} generating projects report via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} generating projects report via session")
        
        year = request.args.get('year', datetime.now().year, type=int)
        
        logger.info(f"Generating projects report for year {year}")
        
        projects = Project.query.filter(
            extract('year', Project.start_date) == year
        ).all()
        
        projects_data = []
        for project in projects:
            # Get activities for this project
            activities = ProjectActivity.query.filter_by(project_id=project.id).all()
            total_activities = len(activities)
            completed_activities = len([a for a in activities if a.status == 'completed'])
            
            # Calculate progress - use a simple percentage based on activities
            if total_activities > 0:
                progress = (completed_activities / total_activities) * 100
            else:
                progress = 0
            
            # Determine category - use a default since it's not in the model
            category = "ESG Initiative"  # Default category
            
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'category': category,
                'status': project.status,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'end_date': project.end_date.isoformat() if project.end_date else None,
                'progress': round(progress, 1),
                'total_activities': total_activities,
                'completed_activities': completed_activities,
                'target_reduction': project.target_reduction_absolute,  # Using absolute reduction
                'target_reduction_unit': project.target_reduction_unit
            })
        
        # Summary statistics
        total_projects = len(projects_data)
        active_projects = len([p for p in projects_data if p['status'] == 'active'])
        completed_projects = len([p for p in projects_data if p['status'] == 'completed'])
        avg_progress = sum([p['progress'] for p in projects_data]) / total_projects if total_projects > 0 else 0
        
        logger.info(f"Successfully generated projects report with {total_projects} projects")
        
        return jsonify({
            'projects': projects_data,
            'summary': {
                'total': total_projects,
                'active': active_projects,
                'completed': completed_projects,
                'average_progress': round(avg_progress, 1)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in projects report: {str(e)}")
        print(f"Error in projects report: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ENHANCED: Get suppliers report with dual authentication
@reports_bp.route('/reports/suppliers', methods=['GET'])
@dual_auth(permissions=[Permissions.REPORTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_suppliers_report():
    """Get suppliers ESG compliance report"""
    try:
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} generating suppliers report via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} generating suppliers report via session")
        
        logger.info("Generating suppliers report")
        
        suppliers = Supplier.query.all()
        
        suppliers_data = []
        for supplier in suppliers:
            # Get supplier data entries for this supplier
            supplier_data_entries = SupplierData.query.filter_by(supplier_id=supplier.id).all()
            
            # Use the data_completeness field from the supplier model
            compliance_score = supplier.data_completeness or 0
            
            # Determine rating based on ESG rating or compliance score
            if supplier.esg_rating:
                rating = supplier.esg_rating
            else:
                # Fallback to compliance score based rating
                if compliance_score >= 80:
                    rating = 'A'
                elif compliance_score >= 60:
                    rating = 'B'
                elif compliance_score >= 40:
                    rating = 'C'
                else:
                    rating = 'D'
            
            suppliers_data.append({
                'id': supplier.id,
                'name': supplier.company_name,  # Using company_name from your model
                'contact_person': supplier.contact_person,
                'email': supplier.email,
                'phone': supplier.phone,
                'industry': supplier.industry,
                'rating': rating,
                'compliance_score': compliance_score,
                'status': supplier.status or 'active',
                'priority_level': supplier.priority_level or 'medium',
                'data_entries': len(supplier_data_entries)
            })
        
        # Summary statistics
        total_suppliers = len(suppliers_data)
        high_rating = len([s for s in suppliers_data if s['rating'] == 'A'])
        avg_compliance = sum([s['compliance_score'] for s in suppliers_data]) / total_suppliers if total_suppliers > 0 else 0
        
        logger.info(f"Successfully generated suppliers report with {total_suppliers} suppliers")
        
        return jsonify({
            'suppliers': suppliers_data,
            'summary': {
                'total': total_suppliers,
                'high_rating': high_rating,
                'average_compliance': round(avg_compliance, 1)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in suppliers report: {str(e)}")
        print(f"Error in suppliers report: {str(e)}")
        return jsonify({'error': str(e)}), 500

def create_comprehensive_pdf_content(story, styles, year, framework):
    """Helper function to create comprehensive PDF content"""
    try:
        # Get data for all sections
        comprehensive_response = get_comprehensive_report()
        emissions_response = get_emissions_report()
        targets_response = get_targets_report()
        projects_response = get_projects_report()
        suppliers_response = get_suppliers_report()
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading1']))
        story.append(Spacer(1, 12))
        
        if comprehensive_response.status_code == 200:
            comp_data = comprehensive_response.get_json()
            summary = comp_data['summary']
            
            summary_text = f"This comprehensive ESG report for {year} presents our organization's environmental, social, and governance performance. "
            summary_text += f"Key highlights include {summary['total_emissions']:.1f} tCO2e total emissions, "
            summary_text += f"{summary['active_targets']} active sustainability targets, "
            summary_text += f"{summary['total_projects']} ESG projects, and "
            summary_text += f"{summary['total_suppliers']} suppliers in our sustainability program."
            
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Page break before emissions section
        story.append(PageBreak())
        
        # Emissions Section
        if emissions_response.status_code == 200:
            emissions_data = emissions_response.get_json()
            story.append(Paragraph("Greenhouse Gas Emissions", styles['Heading1']))
            story.append(Spacer(1, 12))
            
            # Scope breakdown
            if emissions_data['scope_breakdown']:
                story.append(Paragraph("Emissions by Scope", styles['Heading2']))
                scope_data = [['Scope', 'Emissions (tCO2e)', 'Measurements', 'Percentage']]
                total_emissions = sum([item['emissions'] for item in emissions_data['scope_breakdown']])
                
                for item in emissions_data['scope_breakdown']:
                    percentage = (item['emissions'] / total_emissions * 100) if total_emissions > 0 else 0
                    scope_data.append([
                        f"Scope {item['scope']}",
                        f"{item['emissions']:,.2f}",
                        str(item['measurement_count']),
                        f"{percentage:.1f}%"
                    ])
                
                scope_table = Table(scope_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                scope_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(scope_table)
                story.append(Spacer(1, 20))
            
            # Category breakdown
            if emissions_data['category_breakdown']:
                story.append(Paragraph("Emissions by Category", styles['Heading2']))
                category_data = [['Category', 'Emissions (tCO2e)', 'Measurements', 'Percentage']]
                total_emissions = sum([item['emissions'] for item in emissions_data['category_breakdown']])
                
                for item in emissions_data['category_breakdown']:
                    percentage = (item['emissions'] / total_emissions * 100) if total_emissions > 0 else 0
                    category_data.append([
                        item['category'],
                        f"{item['emissions']:,.2f}",
                        str(item['measurement_count']),
                        f"{percentage:.1f}%"
                    ])
                
                category_table = Table(category_data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch])
                category_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(category_table)
                story.append(Spacer(1, 20))
        
        # Page break before next section
        story.append(PageBreak())
        
        # ESG Targets Section
        if targets_response.status_code == 200:
            targets_data = targets_response.get_json()
            story.append(Paragraph("ESG Targets and Performance", styles['Heading1']))
            story.append(Spacer(1, 12))
            
            # Summary
            summary = targets_data['summary']
            story.append(Paragraph(f"Total Targets: {summary['total']} | On Track: {summary['on_track']} | At Risk: {summary['at_risk']} | Behind: {summary['behind']}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            if targets_data['targets']:
                targets_table_data = [['Target Name', 'Category', 'Progress (%)', 'Status', 'Target Year']]
                for target in targets_data['targets']:
                    targets_table_data.append([
                        target['name'][:30] + '...' if len(target['name']) > 30 else target['name'],
                        target['category'],
                        f"{target['progress']:.1f}%",
                        target['status'].title(),
                        str(target['target_year'])
                    ])
                
                targets_table = Table(targets_table_data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
                targets_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8)
                ]))
                story.append(targets_table)
                story.append(Spacer(1, 20))
        
        # Page break before next section
        story.append(PageBreak())
        
        # Projects Section
        if projects_response.status_code == 200:
            projects_data = projects_response.get_json()
            story.append(Paragraph("ESG Projects and Initiatives", styles['Heading1']))
            story.append(Spacer(1, 12))
            
            # Summary
            summary = projects_data['summary']
            story.append(Paragraph(f"Total Projects: {summary['total']} | Active: {summary['active']} | Completed: {summary['completed']} | Average Progress: {summary['average_progress']}%", styles['Normal']))
            story.append(Spacer(1, 12))
            
            if projects_data['projects']:
                projects_table_data = [['Project Name', 'Status', 'Progress (%)', 'Target Reduction', 'Timeline']]
                for project in projects_data['projects']:
                    timeline = f"{project['start_date'][:10] if project['start_date'] else 'N/A'} to {project['end_date'][:10] if project['end_date'] else 'Ongoing'}"
                    target_reduction = f"{project['target_reduction']} {project['target_reduction_unit']}" if project['target_reduction'] else 'N/A'
                    
                    projects_table_data.append([
                        project['name'][:25] + '...' if len(project['name']) > 25 else project['name'],
                        project['status'].title(),
                        f"{project['progress']:.1f}%",
                        target_reduction,
                        timeline
                    ])
                
                projects_table = Table(projects_table_data, colWidths=[2*inch, 1*inch, 1*inch, 1.5*inch, 1.5*inch])
                projects_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightcyan),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8)
                ]))
                story.append(projects_table)
                story.append(Spacer(1, 20))
        
        # Page break before next section
        story.append(PageBreak())
        
        # Suppliers Section
        if suppliers_response.status_code == 200:
            suppliers_data = suppliers_response.get_json()
            story.append(Paragraph("Supplier ESG Performance", styles['Heading1']))
            story.append(Spacer(1, 12))
            
            # Summary
            summary = suppliers_data['summary']
            story.append(Paragraph(f"Total Suppliers: {summary['total']} | High Rating (A): {summary['high_rating']} | Average Compliance: {summary['average_compliance']}%", styles['Normal']))
            story.append(Spacer(1, 12))
            
            if suppliers_data['suppliers']:
                suppliers_table_data = [['Supplier Name', 'Industry', 'ESG Rating', 'Compliance (%)', 'Status']]
                for supplier in suppliers_data['suppliers']:
                    suppliers_table_data.append([
                        supplier['name'][:25] + '...' if len(supplier['name']) > 25 else supplier['name'],
                        supplier['industry'] or 'N/A',
                        supplier['rating'],
                        f"{supplier['compliance_score']:.1f}%",
                        supplier['status'].title()
                    ])
                
                suppliers_table = Table(suppliers_table_data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
                suppliers_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8)
                ]))
                story.append(suppliers_table)
    
    except Exception as e:
        logger.error(f"Error creating comprehensive PDF content: {str(e)}")
        story.append(Paragraph(f"Error generating comprehensive content: {str(e)}", styles['Normal']))

# ENHANCED: Export PDF with dual authentication
@reports_bp.route('/reports/export/pdf', methods=['POST'])
@dual_auth(permissions=[Permissions.REPORTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def export_pdf():
    """Export report as PDF with enhanced formatting and framework support"""
    try:
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} exporting PDF report via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} exporting PDF report via session")
        
        data = request.get_json()
        report_type = data.get('type', 'comprehensive')
        year = data.get('year', datetime.now().year)
        framework = data.get('framework', 'gri')
        
        logger.info(f"Exporting {report_type} report as PDF for year {year}")
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            textColor=colors.grey,
            alignment=1  # Center alignment
        )
        
        # Get framework info
        framework_info = ESG_FRAMEWORKS.get(framework, ESG_FRAMEWORKS['gri'])
        
        # Title page
        if report_type == 'comprehensive':
            title = f"ESG Sustainability Report - {year}"
            subtitle = "Comprehensive ESG Performance Analysis"
        elif report_type == 'emissions':
            title = f"Greenhouse Gas Emissions Report - {year}"
            subtitle = "Detailed Carbon Footprint Analysis"
        elif report_type == 'targets':
            title = f"ESG Targets & Performance Report - {year}"
            subtitle = "Progress Towards Sustainability Goals"
        elif report_type == 'projects':
            title = f"ESG Projects & Initiatives Report - {year}"
            subtitle = "Sustainability Project Portfolio"
        elif report_type == 'suppliers':
            title = f"Supplier ESG Assessment Report - {year}"
            subtitle = "Supply Chain Sustainability Performance"
        else:
            title = f"ESG Report - {year}"
            subtitle = "Environmental, Social & Governance Performance"
        
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(subtitle, subtitle_style))
        story.append(Spacer(1, 30))
        
        # Framework information
        story.append(Paragraph(f"Reporting Framework: {framework_info['name']}", styles['Normal']))
        story.append(Paragraph(f"Focus: {framework_info['focus']}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Report generation info
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Paragraph(f"Reporting Period: {year}", styles['Normal']))
        story.append(Spacer(1, 40))
        
        # Content based on report type
        if report_type == 'comprehensive':
            create_comprehensive_pdf_content(story, styles, year, framework)
        
        elif report_type == 'emissions':
            emissions_response = get_emissions_report()
            if emissions_response.status_code == 200:
                emissions_data = emissions_response.get_json()
                
                story.append(Paragraph("Greenhouse Gas Emissions Analysis", styles['Heading1']))
                story.append(Spacer(1, 12))
                
                # Scope breakdown
                if emissions_data['scope_breakdown']:
                    story.append(Paragraph("Emissions by Scope", styles['Heading2']))
                    scope_data = [['Scope', 'Emissions (tCO2e)', 'Measurements', 'Description']]
                    
                    scope_descriptions = {
                        1: 'Direct emissions from owned/controlled sources',
                        2: 'Indirect emissions from purchased energy',
                        3: 'Other indirect emissions in value chain'
                    }
                    
                    for item in emissions_data['scope_breakdown']:
                        scope_data.append([
                            f"Scope {item['scope']}",
                            f"{item['emissions']:,.2f}",
                            str(item['measurement_count']),
                            scope_descriptions.get(item['scope'], 'Other emissions')
                        ])
                    
                    scope_table = Table(scope_data, colWidths=[1*inch, 1.5*inch, 1*inch, 3.5*inch])
                    scope_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('ALIGN', (3, 1), (3, -1), 'LEFT')  # Left align description
                    ]))
                    story.append(scope_table)
                    story.append(Spacer(1, 20))
                
                # Category breakdown
                if emissions_data['category_breakdown']:
                    story.append(Paragraph("Emissions by Category", styles['Heading2']))
                    category_data = [['Category', 'Emissions (tCO2e)', 'Measurements', 'Percentage']]
                    total_emissions = sum([item['emissions'] for item in emissions_data['category_breakdown']])
                    
                    for item in emissions_data['category_breakdown']:
                        percentage = (item['emissions'] / total_emissions * 100) if total_emissions > 0 else 0
                        category_data.append([
                            item['category'],
                            f"{item['emissions']:,.2f}",
                            str(item['measurement_count']),
                            f"{percentage:.1f}%"
                        ])
                    
                    category_table = Table(category_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1.5*inch])
                    category_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(category_table)
        
        elif report_type == 'targets':
            targets_response = get_targets_report()
            if targets_response.status_code == 200:
                targets_data = targets_response.get_json()
                
                story.append(Paragraph("ESG Targets and Performance", styles['Heading1']))
                story.append(Spacer(1, 12))
                
                # Summary
                summary = targets_data['summary']
                summary_text = f"Performance Summary: {summary['total']} total targets, {summary['on_track']} on track, {summary['at_risk']} at risk, {summary['behind']} behind schedule."
                story.append(Paragraph(summary_text, styles['Normal']))
                story.append(Spacer(1, 20))
                
                if targets_data['targets']:
                    targets_table_data = [['Target Name', 'Category', 'Baseline', 'Current', 'Target', 'Progress', 'Status']]
                    for target in targets_data['targets']:
                        targets_table_data.append([
                            target['name'][:20] + '...' if len(target['name']) > 20 else target['name'],
                            target['category'],
                            f"{target['baseline_value']} {target['unit']}",
                            f"{target['current_value'] or 'N/A'} {target['unit']}",
                            f"{target['target_value']} {target['unit']}",
                            f"{target['progress']:.1f}%",
                            target['status'].title()
                        ])
                    
                    targets_table = Table(targets_table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch, 0.8*inch, 0.7*inch])
                    targets_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTSIZE', (0, 1), (-1, -1), 7)
                    ]))
                    story.append(targets_table)
        
        elif report_type == 'projects':
            projects_response = get_projects_report()
            if projects_response.status_code == 200:
                projects_data = projects_response.get_json()
                
                story.append(Paragraph("ESG Projects and Initiatives", styles['Heading1']))
                story.append(Spacer(1, 12))
                
                # Summary
                summary = projects_data['summary']
                summary_text = f"Project Portfolio: {summary['total']} total projects, {summary['active']} active, {summary['completed']} completed. Average progress: {summary['average_progress']}%"
                story.append(Paragraph(summary_text, styles['Normal']))
                story.append(Spacer(1, 20))
                
                if projects_data['projects']:
                    projects_table_data = [['Project Name', 'Status', 'Progress', 'Activities', 'Target Reduction', 'Timeline']]
                    for project in projects_data['projects']:
                        timeline = f"{project['start_date'][:10] if project['start_date'] else 'N/A'} to {project['end_date'][:10] if project['end_date'] else 'Ongoing'}"
                        target_reduction = f"{project['target_reduction']} {project['target_reduction_unit']}" if project['target_reduction'] else 'N/A'
                        activities = f"{project['completed_activities']}/{project['total_activities']}"
                        
                        projects_table_data.append([
                            project['name'][:20] + '...' if len(project['name']) > 20 else project['name'],
                            project['status'].title(),
                            f"{project['progress']:.1f}%",
                            activities,
                            target_reduction,
                            timeline
                        ])
                    
                    projects_table = Table(projects_table_data, colWidths=[1.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.2*inch, 1.9*inch])
                    projects_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.lightcyan),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTSIZE', (0, 1), (-1, -1), 7)
                    ]))
                    story.append(projects_table)
        
        elif report_type == 'suppliers':
            suppliers_response = get_suppliers_report()
            if suppliers_response.status_code == 200:
                suppliers_data = suppliers_response.get_json()
                
                story.append(Paragraph("Supplier ESG Performance Assessment", styles['Heading1']))
                story.append(Spacer(1, 12))
                
                # Summary
                summary = suppliers_data['summary']
                summary_text = f"Supplier Assessment: {summary['total']} suppliers evaluated, {summary['high_rating']} with high ESG rating (A). Average compliance score: {summary['average_compliance']}%"
                story.append(Paragraph(summary_text, styles['Normal']))
                story.append(Spacer(1, 20))
                
                if suppliers_data['suppliers']:
                    suppliers_table_data = [['Supplier Name', 'Industry', 'ESG Rating', 'Compliance Score', 'Status', 'Priority']]
                    for supplier in suppliers_data['suppliers']:
                        suppliers_table_data.append([
                            supplier['name'][:25] + '...' if len(supplier['name']) > 25 else supplier['name'],
                            supplier['industry'] or 'N/A',
                            supplier['rating'],
                            f"{supplier['compliance_score']:.1f}%",
                            supplier['status'].title(),
                            supplier['priority_level'].title()
                        ])
                    
                    suppliers_table = Table(suppliers_table_data, colWidths=[2*inch, 1.2*inch, 0.8*inch, 1*inch, 0.8*inch, 0.8*inch])
                    suppliers_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTSIZE', (0, 1), (-1, -1), 8)
                    ]))
                    story.append(suppliers_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        logger.info(f"Successfully generated PDF report")
        
        # Return PDF file
        filename = f'ESG_{report_type.title()}_Report_{framework.upper()}_{year}.pdf'
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        print(f"Error generating PDF: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ENHANCED: Export CSV with dual authentication
@reports_bp.route('/reports/export/csv', methods=['POST'])
@dual_auth(permissions=[Permissions.REPORTS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def export_csv():
    """Export report data as CSV"""
    try:
        # Get current user for logging
        if AUTH_MIDDLEWARE_AVAILABLE:
            try:
                current_user = get_auth_user()
                logger.info(f"User {current_user.username} exporting CSV report via API key")
            except:
                current_user = require_session_auth()
                if current_user:
                    logger.info(f"User {current_user.username} exporting CSV report via session")
        
        data = request.get_json()
        report_type = data.get('type', 'emissions')
        year = data.get('year', datetime.now().year)
        
        logger.info(f"Exporting {report_type} report as CSV for year {year}")
        
        if report_type == 'emissions':
            # Export emissions data
            measurements = db.session.query(
                Measurement.date,
                EmissionFactor.category,
                EmissionFactor.sub_category,
                Measurement.amount,
                EmissionFactor.unit,
                EmissionFactor.factor_value,
                func.coalesce(
                    Measurement.calculated_emissions,
                    Measurement.amount * EmissionFactor.factor_value
                ).label('emissions')
            ).join(EmissionFactor, Measurement.emission_factor_id == EmissionFactor.id).filter(
                extract('year', Measurement.date) == year
            ).all()
            
            csv_data = "Date,Category,Sub Category,Amount,Unit,Emission Factor,Total Emissions\n"
            for m in measurements:
                csv_data += f"{m.date},{m.category},{m.sub_category},{m.amount},{m.unit},{m.factor_value},{m.emissions:.2f}\n"
        
        elif report_type == 'projects':
            # Export projects data
            projects = Project.query.filter(extract('year', Project.start_date) == year).all()
            csv_data = "Project Name,Status,Start Date,End Date,Target Reduction,Unit\n"
            for p in projects:
                csv_data += f"{p.name},{p.status},{p.start_date},{p.end_date},{p.target_reduction_absolute},{p.target_reduction_unit}\n"
        
        elif report_type == 'suppliers':
            # Export suppliers data
            suppliers = Supplier.query.all()
            csv_data = "Company Name,Contact Person,Email,Phone,ESG Rating,Data Completeness,Status\n"
            for s in suppliers:
                csv_data += f"{s.company_name},{s.contact_person},{s.email},{s.phone},{s.esg_rating},{s.data_completeness},{s.status}\n"
        
        else:
            csv_data = "No data available for export\n"
        
        # Create CSV response
        output = io.StringIO()
        output.write(csv_data)
        output.seek(0)
        
        logger.info(f"Successfully generated CSV report")
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            as_attachment=True,
            download_name=f'ESG_{report_type.title()}_Data_{year}.csv',
            mimetype='text/csv'
        )
        
    except Exception as e:
        logger.error(f"Error generating CSV: {str(e)}")
        print(f"Error generating CSV: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ENHANCED: Settings-based endpoints for unified permission access
@reports_bp.route('/settings/reports/frameworks', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_frameworks():
    """Get frameworks via settings permission"""
    return get_frameworks()

@reports_bp.route('/settings/reports/comprehensive', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_comprehensive_report():
    """Get comprehensive report via settings permission"""
    return get_comprehensive_report()

@reports_bp.route('/settings/reports/emissions', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_emissions_report():
    """Get emissions report via settings permission"""
    return get_emissions_report()

@reports_bp.route('/settings/reports/targets', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_targets_report():
    """Get targets report via settings permission"""
    return get_targets_report()

@reports_bp.route('/settings/reports/projects', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_projects_report():
    """Get projects report via settings permission"""
    return get_projects_report()

@reports_bp.route('/settings/reports/suppliers', methods=['GET'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_suppliers_report():
    """Get suppliers report via settings permission"""
    return get_suppliers_report()

@reports_bp.route('/settings/reports/export/pdf', methods=['POST'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_export_pdf():
    """Export PDF report via settings permission"""
    return export_pdf()

@reports_bp.route('/settings/reports/export/csv', methods=['POST'])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_export_csv():
    """Export CSV report via settings permission"""
    return export_csv()

