from flask import Blueprint, request, jsonify
from src.models.esg_models import db, Supplier, SupplierESGStandard
from datetime import datetime

esg_standards_bp = Blueprint('esg_standards', __name__)

# Predefined options for ESG standards
STANDARDS_OPTIONS = {
    'standards': ['GHG Protocol', 'ISO 14064', 'ISO 14001', 'ISO 50001'],
    'frameworks': ['GRI', 'TCFD', 'UNSDGs', 'ESRS'],
    'assessments': ['COSIRI', 'EcoVadis', 'FTSE4Good', 'CDP']
}

@esg_standards_bp.route('/suppliers/<int:supplier_id>/esg-standards', methods=['GET'])
def get_supplier_esg_standards(supplier_id):
    """Get all ESG standards for a specific supplier"""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        standards = SupplierESGStandard.query.filter_by(supplier_id=supplier_id).all()
        
        return jsonify({
            'success': True,
            'data': [standard.to_dict() for standard in standards]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@esg_standards_bp.route('/suppliers/<int:supplier_id>/esg-standards', methods=['POST'])
def create_supplier_esg_standard(supplier_id):
    """Create a new ESG standard entry for a supplier"""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['standard_type', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Validate standard_type
        if data['standard_type'] not in ['standard', 'framework', 'assessment']:
            return jsonify({'success': False, 'error': 'Invalid standard_type. Must be: standard, framework, or assessment'}), 400
        
        # Create new ESG standard entry
        esg_standard = SupplierESGStandard(
            supplier_id=supplier_id,
            standard_type=data['standard_type'],
            name=data['name'],
            submission_year=data.get('submission_year'),
            document_link=data.get('document_link'),
            status=data.get('status', 'active'),
            score_rating=data.get('score_rating'),
            notes=data.get('notes')
        )
        
        db.session.add(esg_standard)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': esg_standard.to_dict(),
            'message': 'ESG standard created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@esg_standards_bp.route('/suppliers/<int:supplier_id>/esg-standards/<int:standard_id>', methods=['PUT'])
def update_supplier_esg_standard(supplier_id, standard_id):
    """Update an existing ESG standard entry"""
    try:
        standard = SupplierESGStandard.query.filter_by(
            id=standard_id, 
            supplier_id=supplier_id
        ).first_or_404()
        
        data = request.get_json()
        
        # Update fields if provided
        if 'standard_type' in data:
            if data['standard_type'] not in ['standard', 'framework', 'assessment']:
                return jsonify({'success': False, 'error': 'Invalid standard_type'}), 400
            standard.standard_type = data['standard_type']
        if 'name' in data:
            standard.name = data['name']
        if 'submission_year' in data:
            standard.submission_year = data['submission_year']
        if 'document_link' in data:
            standard.document_link = data['document_link']
        if 'status' in data:
            standard.status = data['status']
        if 'score_rating' in data:
            standard.score_rating = data['score_rating']
        if 'notes' in data:
            standard.notes = data['notes']
        
        standard.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': standard.to_dict(),
            'message': 'ESG standard updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@esg_standards_bp.route('/suppliers/<int:supplier_id>/esg-standards/<int:standard_id>', methods=['DELETE'])
def delete_supplier_esg_standard(supplier_id, standard_id):
    """Delete an ESG standard entry"""
    try:
        standard = SupplierESGStandard.query.filter_by(
            id=standard_id, 
            supplier_id=supplier_id
        ).first_or_404()
        
        db.session.delete(standard)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'ESG standard deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@esg_standards_bp.route('/esg-standards/options', methods=['GET'])
def get_esg_standards_options():
    """Get predefined options for ESG standards, frameworks, and assessments"""
    try:
        return jsonify({
            'success': True,
            'data': STANDARDS_OPTIONS
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

