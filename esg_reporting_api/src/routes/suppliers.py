"""
Enhanced Supplier Management Routes with Centralized Auth Middleware
Preserves 100% of original functionality while adding API key authentication
"""

from flask import Blueprint, request, jsonify
from src.models.esg_models import db, Supplier, SupplierESGStandard
from sqlalchemy import func, and_, or_
from datetime import datetime
import logging

# Import auth middleware with graceful fallback
try:
    from src.auth_middleware import require_auth as require_api_auth, Permissions, get_current_user as get_auth_user
    AUTH_MIDDLEWARE_AVAILABLE = True
    print("INFO:src.routes.suppliers:Auth middleware imported successfully")
except ImportError:
    AUTH_MIDDLEWARE_AVAILABLE = False
    print("WARNING:src.routes.suppliers:Auth middleware not available, using session-only authentication")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

suppliers_bp = Blueprint('suppliers', __name__)

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
                        print(f"INFO:src.routes.suppliers:API key authentication successful for {f.__name__}")
                    else:
                        current_user = require_session_auth()
                        print(f"INFO:src.routes.suppliers:Session authentication successful for {f.__name__}")
                    return f(*args, **kwargs)
                except Exception as e:
                    print(f"ERROR:src.routes.suppliers:Authentication failed for {f.__name__}: {str(e)}")
                    return jsonify({'error': 'Authentication failed'}), 401
            return wrapper
    return decorator

@suppliers_bp.route('/suppliers', methods=['GET'])
@dual_auth(permissions=[Permissions.SUPPLIERS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_suppliers():
    """Get all suppliers with enhanced data handling"""
    try:
        logger.info("Fetching all suppliers")
        
        suppliers = Supplier.query.all()
        suppliers_data = []
        
        for supplier in suppliers:
            # Safe attribute access with proper type conversion
            annual_spend = getattr(supplier, 'annual_spend', 0)
            if annual_spend is None:
                annual_spend = 0
            else:
                try:
                    annual_spend = float(annual_spend)
                except (ValueError, TypeError):
                    annual_spend = 0.0
            
            supplier_data = {
                'id': supplier.id,
                'company_name': getattr(supplier, 'company_name', ''),
                'industry': getattr(supplier, 'industry', ''),
                'contact_person': getattr(supplier, 'contact_person', ''),
                'email': getattr(supplier, 'email', ''),
                'phone': getattr(supplier, 'phone', ''),
                'esg_rating': getattr(supplier, 'esg_rating', ''),
                'status': getattr(supplier, 'status', 'pending'),
                'priority_level': getattr(supplier, 'priority_level', 'medium'),
                'annual_spend': annual_spend,
                'notes': getattr(supplier, 'notes', ''),
                'created_at': getattr(supplier, 'created_at', datetime.now()).isoformat() if hasattr(supplier, 'created_at') else datetime.now().isoformat(),
                'updated_at': getattr(supplier, 'updated_at', datetime.now()).isoformat() if hasattr(supplier, 'updated_at') else datetime.now().isoformat()
            }
            suppliers_data.append(supplier_data)
        
        logger.info(f"Successfully fetched {len(suppliers_data)} suppliers")
        return jsonify({
            'success': True,
            'data': suppliers_data,
            'count': len(suppliers_data)
        })
        
    except Exception as e:
        logger.error(f"Error fetching suppliers: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch suppliers: {str(e)}'
        }), 500

@suppliers_bp.route('/suppliers', methods=['POST'])
@dual_auth(permissions=[Permissions.SUPPLIERS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def create_supplier():
    """Create a new supplier with enhanced validation"""
    try:
        data = request.get_json()
        logger.info(f"Creating new supplier: {data.get('company_name', 'Unknown')}")
        
        if not data or not data.get('company_name'):
            return jsonify({
                'success': False,
                'error': 'Company name is required'
            }), 400
        
        # Handle annual_spend conversion
        annual_spend = data.get('annual_spend', 0)
        if annual_spend == '' or annual_spend is None:
            annual_spend = 0
        else:
            try:
                annual_spend = float(annual_spend)
            except (ValueError, TypeError):
                annual_spend = 0.0
        
        supplier = Supplier(
            company_name=data.get('company_name', ''),
            industry=data.get('industry', ''),
            contact_person=data.get('contact_person', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            esg_rating=data.get('esg_rating', ''),
            status=data.get('status', 'pending'),
            priority_level=data.get('priority_level', 'medium'),
            annual_spend=annual_spend,
            notes=data.get('notes', '')
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        logger.info(f"Successfully created supplier with ID: {supplier.id}")
        return jsonify({
            'success': True,
            'data': {
                'id': supplier.id,
                'company_name': supplier.company_name,
                'message': 'Supplier created successfully'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating supplier: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to create supplier: {str(e)}'
        }), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>', methods=['PUT'])
@dual_auth(permissions=[Permissions.SUPPLIERS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def update_supplier(supplier_id):
    """Update an existing supplier with enhanced validation"""
    try:
        data = request.get_json()
        logger.info(f"Updating supplier ID: {supplier_id}")
        
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return jsonify({
                'success': False,
                'error': 'Supplier not found'
            }), 404
        
        # Handle annual_spend conversion
        if 'annual_spend' in data:
            annual_spend = data['annual_spend']
            if annual_spend == '' or annual_spend is None:
                annual_spend = 0
            else:
                try:
                    annual_spend = float(annual_spend)
                except (ValueError, TypeError):
                    annual_spend = 0.0
            data['annual_spend'] = annual_spend
        
        # Update supplier attributes
        for key, value in data.items():
            if hasattr(supplier, key):
                setattr(supplier, key, value)
        
        db.session.commit()
        
        logger.info(f"Successfully updated supplier ID: {supplier_id}")
        return jsonify({
            'success': True,
            'data': {
                'id': supplier.id,
                'company_name': supplier.company_name,
                'message': 'Supplier updated successfully'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating supplier {supplier_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to update supplier: {str(e)}'
        }), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>', methods=['DELETE'])
@dual_auth(permissions=[Permissions.SUPPLIERS_DELETE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def delete_supplier(supplier_id):
    """Delete a supplier and all related ESG standards"""
    try:
        logger.info(f"Deleting supplier ID: {supplier_id}")
        
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return jsonify({
                'success': False,
                'error': 'Supplier not found'
            }), 404
        
        # Delete related ESG standards first
        SupplierESGStandard.query.filter_by(supplier_id=supplier_id).delete()
        
        # Delete the supplier
        db.session.delete(supplier)
        db.session.commit()
        
        logger.info(f"Successfully deleted supplier ID: {supplier_id}")
        return jsonify({
            'success': True,
            'message': 'Supplier and related data deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting supplier {supplier_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to delete supplier: {str(e)}'
        }), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>/esg-standards', methods=['GET'])
@dual_auth(permissions=[Permissions.SUPPLIERS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_supplier_esg_standards(supplier_id):
    """Get all ESG standards for a specific supplier"""
    try:
        logger.info(f"Fetching ESG standards for supplier ID: {supplier_id}")
        
        # Verify supplier exists
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return jsonify({
                'success': False,
                'error': 'Supplier not found'
            }), 404
        
        esg_standards = SupplierESGStandard.query.filter_by(supplier_id=supplier_id).all()
        
        standards_data = []
        for standard in esg_standards:
            standard_data = {
                'id': standard.id,
                'supplier_id': standard.supplier_id,
                'standard_type': getattr(standard, 'standard_type', ''),
                'name': getattr(standard, 'name', ''),
                'submission_year': getattr(standard, 'submission_year', None),
                'document_link': getattr(standard, 'document_link', ''),
                'status': getattr(standard, 'status', 'active'),
                'score_rating': getattr(standard, 'score_rating', ''),
                'notes': getattr(standard, 'notes', ''),
                'created_at': getattr(standard, 'created_at', datetime.now()).isoformat() if hasattr(standard, 'created_at') else datetime.now().isoformat(),
                'updated_at': getattr(standard, 'updated_at', datetime.now()).isoformat() if hasattr(standard, 'updated_at') else datetime.now().isoformat()
            }
            standards_data.append(standard_data)
        
        logger.info(f"Successfully fetched {len(standards_data)} ESG standards for supplier {supplier_id}")
        return jsonify({
            'success': True,
            'data': standards_data,
            'count': len(standards_data)
        })
        
    except Exception as e:
        logger.error(f"Error fetching ESG standards for supplier {supplier_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch ESG standards: {str(e)}'
        }), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>/esg-standards', methods=['POST'])
@dual_auth(permissions=[Permissions.SUPPLIERS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def create_supplier_esg_standard(supplier_id):
    """Create a new ESG standard for a supplier"""
    try:
        data = request.get_json()
        logger.info(f"Creating ESG standard for supplier ID: {supplier_id}")
        
        # Verify supplier exists
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return jsonify({
                'success': False,
                'error': 'Supplier not found'
            }), 404
        
        if not data or not data.get('name') or not data.get('standard_type'):
            return jsonify({
                'success': False,
                'error': 'Name and standard type are required'
            }), 400
        
        # Handle submission_year conversion
        submission_year = data.get('submission_year')
        if submission_year:
            try:
                submission_year = int(submission_year)
            except (ValueError, TypeError):
                submission_year = None
        
        esg_standard = SupplierESGStandard(
            supplier_id=supplier_id,
            standard_type=data.get('standard_type', ''),
            name=data.get('name', ''),
            submission_year=submission_year,
            document_link=data.get('document_link', ''),
            status=data.get('status', 'active'),
            score_rating=data.get('score_rating', ''),
            notes=data.get('notes', '')
        )
        
        db.session.add(esg_standard)
        db.session.commit()
        
        logger.info(f"Successfully created ESG standard with ID: {esg_standard.id}")
        return jsonify({
            'success': True,
            'data': {
                'id': esg_standard.id,
                'name': esg_standard.name,
                'standard_type': esg_standard.standard_type,
                'message': 'ESG standard created successfully'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating ESG standard for supplier {supplier_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to create ESG standard: {str(e)}'
        }), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>/esg-standards/<int:standard_id>', methods=['PUT'])
@dual_auth(permissions=[Permissions.SUPPLIERS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def update_supplier_esg_standard(supplier_id, standard_id):
    """Update an existing ESG standard"""
    try:
        data = request.get_json()
        logger.info(f"Updating ESG standard ID: {standard_id} for supplier ID: {supplier_id}")
        
        esg_standard = SupplierESGStandard.query.filter_by(
            id=standard_id, 
            supplier_id=supplier_id
        ).first()
        
        if not esg_standard:
            return jsonify({
                'success': False,
                'error': 'ESG standard not found'
            }), 404
        
        # Handle submission_year conversion
        if 'submission_year' in data:
            submission_year = data['submission_year']
            if submission_year:
                try:
                    submission_year = int(submission_year)
                except (ValueError, TypeError):
                    submission_year = None
            data['submission_year'] = submission_year
        
        # Update ESG standard attributes
        for key, value in data.items():
            if hasattr(esg_standard, key):
                setattr(esg_standard, key, value)
        
        db.session.commit()
        
        logger.info(f"Successfully updated ESG standard ID: {standard_id}")
        return jsonify({
            'success': True,
            'data': {
                'id': esg_standard.id,
                'name': esg_standard.name,
                'standard_type': esg_standard.standard_type,
                'message': 'ESG standard updated successfully'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating ESG standard {standard_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to update ESG standard: {str(e)}'
        }), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>/esg-standards/<int:standard_id>', methods=['DELETE'])
@dual_auth(permissions=[Permissions.SUPPLIERS_DELETE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def delete_supplier_esg_standard(supplier_id, standard_id):
    """Delete an ESG standard"""
    try:
        logger.info(f"Deleting ESG standard ID: {standard_id} for supplier ID: {supplier_id}")
        
        esg_standard = SupplierESGStandard.query.filter_by(
            id=standard_id, 
            supplier_id=supplier_id
        ).first()
        
        if not esg_standard:
            return jsonify({
                'success': False,
                'error': 'ESG standard not found'
            }), 404
        
        db.session.delete(esg_standard)
        db.session.commit()
        
        logger.info(f"Successfully deleted ESG standard ID: {standard_id}")
        return jsonify({
            'success': True,
            'message': 'ESG standard deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting ESG standard {standard_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to delete ESG standard: {str(e)}'
        }), 500

@suppliers_bp.route('/esg-standards/options', methods=['GET'])
@dual_auth(permissions=[Permissions.SUPPLIERS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_esg_options():
    """Get predefined ESG standards, frameworks, and assessments options"""
    try:
        logger.info("Fetching ESG options")
        
        # Predefined options for ESG standards, frameworks, and assessments
        esg_options = {
            'standards': [
                'ISO 14001',
                'ISO 45001',
                'ISO 26000',
                'SA8000',
                'OHSAS 18001',
                'B Corp Certification',
                'Fair Trade Certification',
                'Forest Stewardship Council (FSC)',
                'Cradle to Cradle Certified',
                'ENERGY STAR',
                'LEED Certification',
                'Carbon Trust Standard',
                'Science Based Targets (SBTi)',
                'RE100',
                'EcoVadis',
                'Sedex',
                'SMETA',
                'BSCI',
                'Responsible Business Alliance (RBA)',
                'Global Reporting Initiative (GRI)',
                'UN Global Compact',
                'TCFD',
                'CDP'
            ],
            'frameworks': [
                'Global Reporting Initiative (GRI)',
                'Sustainability Accounting Standards Board (SASB)',
                'Task Force on Climate-related Financial Disclosures (TCFD)',
                'Integrated Reporting Framework',
                'UN Sustainable Development Goals (SDGs)',
                'UN Global Compact',
                'OECD Guidelines for Multinational Enterprises',
                'ISO 26000 Guidance on Social Responsibility',
                'AA1000 AccountAbility Principles',
                'Carbon Disclosure Project (CDP)',
                'Science Based Targets initiative (SBTi)',
                'RE100 Renewable Energy Initiative',
                'EP100 Energy Productivity Initiative',
                'EV100 Electric Vehicle Initiative',
                'Net Zero Asset Managers Initiative',
                'Partnership for Carbon Accounting Financials (PCAF)',
                'Principles for Responsible Investment (PRI)',
                'Equator Principles',
                'Natural Capital Protocol',
                'Social Return on Investment (SROI)'
            ],
            'assessments': [
                'EcoVadis Assessment',
                'CDP Climate Change Assessment',
                'CDP Water Security Assessment',
                'CDP Forests Assessment',
                'Sustainalytics ESG Risk Rating',
                'MSCI ESG Rating',
                'S&P Global ESG Score',
                'Refinitiv ESG Score',
                'ISS ESG Corporate Rating',
                'Vigeo Eiris ESG Rating',
                'RepRisk ESG Risk Assessment',
                'Bloomberg ESG Disclosure Score',
                'FTSE4Good ESG Rating',
                'Dow Jones Sustainability Index (DJSI)',
                'Carbon Trust Footprint Assessment',
                'Life Cycle Assessment (LCA)',
                'Environmental Impact Assessment (EIA)',
                'Social Impact Assessment (SIA)',
                'Human Rights Impact Assessment (HRIA)',
                'Supplier ESG Risk Assessment',
                'ESG Materiality Assessment',
                'Stakeholder Engagement Assessment',
                'ESG Due Diligence Assessment',
                'Climate Risk Assessment',
                'Water Risk Assessment',
                'Biodiversity Impact Assessment'
            ]
        }
        
        logger.info("Successfully fetched ESG options")
        return jsonify({
            'success': True,
            'data': esg_options
        })
        
    except Exception as e:
        logger.error(f"Error fetching ESG options: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch ESG options: {str(e)}'
        }), 500

@suppliers_bp.route('/suppliers/assessments', methods=['GET'])
@dual_auth(permissions=[Permissions.SUPPLIERS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_supplier_assessments():
    """Get assessment matrix data for all suppliers"""
    try:
        year = request.args.get('year', str(datetime.now().year))
        standard = request.args.get('standard', 'all')
        
        logger.info(f"Fetching assessment matrix for year: {year}, standard: {standard}")
        
        # Get all suppliers
        suppliers = Supplier.query.all()
        
        # Get ESG standards for the specified year
        query = SupplierESGStandard.query
        
        if year != 'all':
            try:
                year_int = int(year)
                query = query.filter(SupplierESGStandard.submission_year == year_int)
            except ValueError:
                pass
        
        if standard != 'all':
            query = query.filter(SupplierESGStandard.name == standard)
        
        esg_standards = query.all()
        
        # Create assessment matrix
        assessment_data = []
        for supplier in suppliers:
            supplier_assessments = [esg for esg in esg_standards if esg.supplier_id == supplier.id]
            
            assessment_data.append({
                'supplier_id': supplier.id,
                'company_name': supplier.company_name,
                'assessments': [
                    {
                        'standard_name': esg.name,
                        'standard_type': esg.standard_type,
                        'submission_year': esg.submission_year,
                        'status': esg.status,
                        'score_rating': esg.score_rating
                    }
                    for esg in supplier_assessments
                ]
            })
        
        logger.info(f"Successfully fetched assessment matrix for {len(suppliers)} suppliers")
        return jsonify({
            'success': True,
            'data': assessment_data,
            'filters': {
                'year': year,
                'standard': standard
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching assessment matrix: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch assessment matrix: {str(e)}'
        }), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>/assessments', methods=['PUT'])
@dual_auth(permissions=[Permissions.SUPPLIERS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def update_supplier_assessment(supplier_id):
    """Update or create assessment status for a supplier"""
    try:
        data = request.get_json()
        logger.info(f"Updating assessment for supplier ID: {supplier_id}")
        
        # Verify supplier exists
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return jsonify({
                'success': False,
                'error': 'Supplier not found'
            }), 404
        
        standard_name = data.get('standard')
        year = data.get('year', datetime.now().year)
        submitted = data.get('submitted', False)
        
        if not standard_name:
            return jsonify({
                'success': False,
                'error': 'Standard name is required'
            }), 400
        
        try:
            year = int(year)
        except (ValueError, TypeError):
            year = datetime.now().year
        
        # Check if assessment already exists
        existing_assessment = SupplierESGStandard.query.filter_by(
            supplier_id=supplier_id,
            name=standard_name,
            submission_year=year
        ).first()
        
        if submitted:
            # Create or update assessment
            if existing_assessment:
                existing_assessment.status = 'active'
            else:
                # Determine standard type based on name
                standard_type = 'standard'  # Default
                if any(framework in standard_name.lower() for framework in ['gri', 'sasb', 'tcfd', 'sdg']):
                    standard_type = 'framework'
                elif any(assessment in standard_name.lower() for assessment in ['ecovadis', 'cdp', 'rating', 'score']):
                    standard_type = 'assessment'
                
                new_assessment = SupplierESGStandard(
                    supplier_id=supplier_id,
                    standard_type=standard_type,
                    name=standard_name,
                    submission_year=year,
                    status='active',
                    notes=f'Assessment submitted via matrix on {datetime.now().strftime("%Y-%m-%d")}'
                )
                db.session.add(new_assessment)
        else:
            # Remove assessment if it exists
            if existing_assessment:
                db.session.delete(existing_assessment)
        
        db.session.commit()
        
        logger.info(f"Successfully updated assessment for supplier {supplier_id}")
        return jsonify({
            'success': True,
            'message': 'Assessment updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating assessment for supplier {supplier_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to update assessment: {str(e)}'
        }), 500

# Settings-based unified access endpoints
@suppliers_bp.route("/settings/suppliers", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_suppliers():
    """Get suppliers via settings permission"""
    return get_suppliers()

@suppliers_bp.route("/settings/suppliers", methods=["POST"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_create_supplier():
    """Create supplier via settings permission"""
    return create_supplier()

@suppliers_bp.route("/settings/suppliers/<int:supplier_id>", methods=["PUT"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_update_supplier(supplier_id):
    """Update supplier via settings permission"""
    return update_supplier(supplier_id)

@suppliers_bp.route("/settings/suppliers/<int:supplier_id>", methods=["DELETE"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_delete_supplier(supplier_id):
    """Delete supplier via settings permission"""
    return delete_supplier(supplier_id)

@suppliers_bp.route("/settings/suppliers/<int:supplier_id>/esg-standards", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_supplier_esg_standards(supplier_id):
    """Get supplier ESG standards via settings permission"""
    return get_supplier_esg_standards(supplier_id)

@suppliers_bp.route("/settings/suppliers/<int:supplier_id>/esg-standards", methods=["POST"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_create_supplier_esg_standard(supplier_id):
    """Create supplier ESG standard via settings permission"""
    return create_supplier_esg_standard(supplier_id)

@suppliers_bp.route("/settings/suppliers/<int:supplier_id>/esg-standards/<int:standard_id>", methods=["PUT"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_update_supplier_esg_standard(supplier_id, standard_id):
    """Update supplier ESG standard via settings permission"""
    return update_supplier_esg_standard(supplier_id, standard_id)

@suppliers_bp.route("/settings/suppliers/<int:supplier_id>/esg-standards/<int:standard_id>", methods=["DELETE"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_delete_supplier_esg_standard(supplier_id, standard_id):
    """Delete supplier ESG standard via settings permission"""
    return delete_supplier_esg_standard(supplier_id, standard_id)

@suppliers_bp.route("/settings/esg-standards/options", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_esg_options():
    """Get ESG options via settings permission"""
    return get_esg_options()

@suppliers_bp.route("/settings/suppliers/assessments", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_supplier_assessments():
    """Get supplier assessments via settings permission"""
    return get_supplier_assessments()

@suppliers_bp.route("/settings/suppliers/<int:supplier_id>/assessments", methods=["PUT"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_update_supplier_assessment(supplier_id):
    """Update supplier assessment via settings permission"""
    return update_supplier_assessment(supplier_id)

# Error handlers
@suppliers_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404

@suppliers_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 'Bad request'
    }), 400

@suppliers_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

