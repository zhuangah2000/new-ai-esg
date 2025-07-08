"""
Comprehensive Flask-RESTX API Models for Complete ESG Reporting Platform
Covers ALL 13+ modules with detailed request/response models
"""

from flask_restx import fields
from .api_documentation import common_fields  # ✅ FIXED IMPORT

def create_all_models(api):
    """Create comprehensive API models for all 13+ ESG platform modules"""
    
    models = {}
    
    # ============================================================================
    # COMMON/SHARED MODELS
    # ============================================================================
    
    models['success_response'] = api.model('SuccessResponse', {
        'success': fields.Boolean(required=True, description='Operation success status', example=True),
        'message': fields.String(description='Success message', example='Operation completed successfully'),
        'data': fields.Raw(description='Response data')
    })
    
    models['error_response'] = api.model('ErrorResponse', {
        'success': fields.Boolean(required=True, description='Operation success status', example=False),
        'error': fields.String(required=True, description='Error message', example='Invalid request data'),
        'details': fields.Raw(description='Additional error details')
    })
    
    models['pagination_info'] = api.model('PaginationInfo', {
        'page': fields.Integer(description='Current page number', example=1),
        'per_page': fields.Integer(description='Items per page', example=20),
        'total': fields.Integer(description='Total number of items', example=150),
        'pages': fields.Integer(description='Total number of pages', example=8)
    })
    
    # ============================================================================
    # 1. AUTHENTICATION MODELS
    # ============================================================================
    
    models['login_request'] = api.model('LoginRequest', {
        'email': fields.String(required=True, description='User email address', example='admin@company.com'),
        'password': fields.String(required=True, description='User password', example='securepassword123')
    })
    
    models['login_response'] = api.model('LoginResponse', {
        'success': fields.Boolean(required=True, description='Login success status', example=True),
        'message': fields.String(description='Login message', example='Login successful'),
        'user': fields.Raw(description='User information including role and permissions')
    })
    
    # ============================================================================
    # 2. USER MANAGEMENT MODELS
    # ============================================================================
    
    models['user_base'] = api.model('UserBase', {
        'email': fields.String(required=True, description='User email address', example='john.doe@company.com'),
        'first_name': fields.String(required=True, description='First name', example='John'),
        'last_name': fields.String(required=True, description='Last name', example='Doe'),
        'role_id': fields.Integer(description='Role ID', example=2),
        'department': fields.String(description='Department', example='Sustainability'),
        'job_title': fields.String(description='Job title', example='ESG Analyst'),
        'phone': fields.String(description='Phone number', example='+1-555-0123'),
        'is_active': fields.Boolean(description='Active status', example=True)
    })
    
    models['user_create'] = api.inherit('UserCreate', models['user_base'], {
        'password': fields.String(required=True, description='User password', example='securepassword123')
    })
    
    models['user_response'] = api.inherit('UserResponse', models['user_base'], {
        'id': common_fields['id'],
        'created_at': common_fields['created_at'],
        'updated_at': common_fields['updated_at'],
        'last_login': fields.DateTime(description='Last login timestamp', example='2024-01-15T09:30:00Z'),
        'role': fields.Raw(description='Role information with permissions')
    })
    
    models['user_update'] = api.model('UserUpdate', {
        'first_name': fields.String(description='First name', example='John'),
        'last_name': fields.String(description='Last name', example='Doe'),
        'department': fields.String(description='Department', example='Sustainability'),
        'job_title': fields.String(description='Job title', example='ESG Analyst'),
        'phone': fields.String(description='Phone number', example='+1-555-0123'),
        'is_active': fields.Boolean(description='Active status', example=True),
        'role_id': fields.Integer(description='Role ID', example=2)
    })
    
    # ============================================================================
    # 3. ROLE MANAGEMENT MODELS
    # ============================================================================
    
    models['role_base'] = api.model('RoleBase', {
        'name': fields.String(required=True, description='Role name', example='ESG Analyst'),
        'description': fields.String(description='Role description', example='Responsible for ESG data collection and analysis'),
        'is_system_role': fields.Boolean(description='System role flag', example=False)
    })
    
    models['role_create'] = api.inherit('RoleCreate', models['role_base'], {
        'permissions': fields.List(fields.String, description='List of permission names', 
                                 example=['MEASUREMENTS_READ', 'MEASUREMENTS_WRITE', 'REPORTS_READ'])
    })
    
    models['role_response'] = api.inherit('RoleResponse', models['role_base'], {
        'id': common_fields['id'],
        'created_at': common_fields['created_at'],
        'updated_at': common_fields['updated_at'],
        'permissions': fields.List(fields.Raw, description='List of permissions with details'),
        'user_count': fields.Integer(description='Number of users with this role', example=5)
    })
    
    models['permission_model'] = api.model('Permission', {
        'id': common_fields['id'],
        'name': fields.String(description='Permission name', example='MEASUREMENTS_READ'),
        'description': fields.String(description='Permission description', example='Read access to measurements'),
        'module': fields.String(description='Module name', example='measurements')
    })
    
    # ============================================================================
    # 4. COMPANY MANAGEMENT MODELS
    # ============================================================================
    
    models['company_base'] = api.model('CompanyBase', {
        'name': fields.String(required=True, description='Company name', example='Green Tech Solutions Inc.'),
        'industry': fields.String(description='Industry sector', example='Technology'),
        'description': fields.String(description='Company description', example='Leading provider of sustainable technology solutions'),
        'website': fields.String(description='Company website', example='https://greentech.com'),
        'headquarters_location': fields.String(description='Headquarters location', example='San Francisco, CA'),
        'employee_count': fields.Integer(description='Number of employees', example=500),
        'annual_revenue': fields.Float(description='Annual revenue in USD', example=50000000.00),
        'stock_symbol': fields.String(description='Stock ticker symbol', example='GTECH'),
        'is_public': fields.Boolean(description='Public company status', example=True)
    })
    
    models['company_response'] = api.inherit('CompanyResponse', models['company_base'], {
        'id': common_fields['id'],
        'created_at': common_fields['created_at'],
        'updated_at': common_fields['updated_at'],
        'subsidiaries': fields.List(fields.Raw, description='List of subsidiary companies')
    })
    
    # ============================================================================
    # 5. MEASUREMENTS MODELS
    # ============================================================================
    
    models['measurement_base'] = api.model('MeasurementBase', {
        'date': fields.Date(required=True, description='Measurement date', example='2024-01-15'),
        'category': fields.String(required=True, description='Emission category', example='Energy'),
        'sub_category': fields.String(description='Emission sub-category', example='Electricity'),
        'amount': fields.Float(required=True, description='Measurement amount', example=1500.75),
        'unit': fields.String(required=True, description='Unit of measurement', example='kWh'),
        'emission_factor_id': fields.Integer(required=True, description='Emission factor ID', example=1),
        'location': fields.String(description='Measurement location', example='New York Office'),
        'notes': fields.String(description='Additional notes', example='Monthly electricity consumption')
    })
    
    models['measurement_response'] = api.inherit('MeasurementResponse', models['measurement_base'], {
        'id': common_fields['id'],
        'calculated_emissions': fields.Float(description='Calculated CO2e emissions', example=680.45),
        'created_at': common_fields['created_at'],
        'updated_at': common_fields['updated_at'],
        'emission_factor': fields.Raw(description='Emission factor details with active revision info')
    })
    
    models['measurement_summary'] = api.model('MeasurementSummary', {
        'scope_emissions': fields.Raw(description='Emissions by scope', example={'scope_1': 1200.5, 'scope_2': 800.3, 'scope_3': 2100.7}),
        'category_emissions': fields.Raw(description='Emissions by category'),
        'total_measurements': fields.Integer(description='Total number of measurements', example=150),
        'total_emissions': fields.Float(description='Total emissions in CO2e', example=4101.5),
        'period': fields.String(description='Summary period', example='2024')
    })
    
    models['measurement_recalculate'] = api.model('MeasurementRecalculate', {
        'measurement_ids': fields.List(fields.Integer, description='List of measurement IDs to recalculate', example=[1, 2, 3]),
        'use_active_factors': fields.Boolean(description='Use active emission factor revisions', example=True)
    })
    
    # ============================================================================
    # 6. EMISSION FACTORS MODELS
    # ============================================================================
    
    models['emission_factor_base'] = api.model('EmissionFactorBase', {
        'name': fields.String(required=True, description='Emission factor name', example='US Grid Electricity'),
        'scope': fields.Integer(required=True, description='GHG Protocol scope (1, 2, or 3)', example=2),
        'category': fields.String(required=True, description='Emission category', example='Energy'),
        'sub_category': fields.String(description='Emission sub-category', example='Electricity'),
        'factor_value': fields.Float(required=True, description='Emission factor value', example=0.4532),
        'unit': fields.String(required=True, description='Factor unit', example='kg CO2e/kWh'),
        'source': fields.String(required=True, description='Data source', example='EPA eGRID 2022'),
        'link': fields.String(description='Source link', example='https://www.epa.gov/egrid'),
        'effective_date': fields.Date(required=True, description='Effective date', example='2024-01-01'),
        'description': fields.String(description='Factor description', example='US national average grid emission factor')
    })
    
    models['emission_factor_response'] = api.inherit('EmissionFactorResponse', models['emission_factor_base'], {
        'id': common_fields['id'],
        'created_at': common_fields['created_at'],
        'updated_at': common_fields['updated_at'],
        'revision_count': fields.Integer(description='Number of revisions', example=3),
        'current_revision': fields.Integer(description='Current active revision number', example=2),
        'active_factor_value': fields.Float(description='Currently active factor value', example=0.4532)
    })
    
    models['emission_factor_revision'] = api.inherit('EmissionFactorRevision', models['emission_factor_base'], {
        'parent_factor_id': fields.Integer(required=True, description='Parent factor ID', example=1),
        'revision_notes': fields.String(required=True, description='Revision notes', example='Updated with latest EPA data'),
        'version': fields.Integer(description='Revision version', example=2),
        'is_active': fields.Boolean(description='Active revision status', example=True),
        'created_by': fields.String(description='Created by user', example='admin')
    })
    
    models['emission_factor_categories'] = api.model('EmissionFactorCategories', {
        'categories': fields.List(fields.String, description='Available categories', example=['Energy', 'Transportation', 'Waste']),
        'sub_categories': fields.Raw(description='Sub-categories by category', example={'Energy': ['Electricity', 'Natural Gas']})
    })
    
    # ============================================================================
    # 7. DASHBOARD MODELS
    # ============================================================================
    
    models['dashboard_overview'] = api.model('DashboardOverview', {
        'scope_emissions': fields.Raw(description='Emissions by scope', example={'scope_1': 1200.5, 'scope_2': 800.3, 'scope_3': 2100.7}),
        'total_emissions': fields.Float(description='Total emissions in tCO2e', example=4101.5),
        'category_emissions': fields.Raw(description='Emissions by category'),
        'monthly_trend': fields.List(fields.Raw, description='Monthly emissions trend'),
        'recent_measurements': fields.List(fields.Raw, description='Recent measurements'),
        'targets_summary': fields.List(fields.Raw, description='ESG targets summary'),
        'year': fields.Integer(description='Report year', example=2024)
    })
    
    models['emissions_trend'] = api.model('EmissionsTrend', {
        'trend_data': fields.List(fields.Raw, description='Trend data points'),
        'period': fields.String(description='Time period', example='monthly'),
        'scope': fields.Integer(description='GHG scope filter', example=2),
        'years': fields.Integer(description='Number of years included', example=1)
    })
    
    models['intensity_metrics'] = api.model('IntensityMetrics', {
        'emissions_per_revenue': fields.Float(description='Emissions per revenue (tCO2e/USD)', example=0.000082),
        'emissions_per_employee': fields.Float(description='Emissions per employee (tCO2e/employee)', example=8.2),
        'emissions_per_sqft': fields.Float(description='Emissions per square foot (tCO2e/sqft)', example=0.041),
        'year': fields.Integer(description='Metrics year', example=2024)
    })
    
    # ============================================================================
    # 8. REPORTS MODELS
    # ============================================================================
    
    models['report_base'] = api.model('ReportBase', {
        'name': fields.String(required=True, description='Report name', example='Q4 2023 ESG Report'),
        'report_type': fields.String(required=True, description='Report type', 
                                   example='sustainability', enum=['sustainability', 'carbon_footprint', 'esg_scorecard']),
        'framework': fields.String(description='Reporting framework', 
                                 example='GRI', enum=['GRI', 'SASB', 'TCFD', 'CDP', 'CUSTOM']),
        'reporting_period_start': fields.Date(required=True, description='Reporting period start', example='2023-10-01'),
        'reporting_period_end': fields.Date(required=True, description='Reporting period end', example='2023-12-31'),
        'description': fields.String(description='Report description', example='Quarterly sustainability performance report'),
        'status': fields.String(description='Report status', example='draft', enum=['draft', 'in_review', 'approved', 'published'])
    })
    
    models['report_response'] = api.inherit('ReportResponse', models['report_base'], {
        'id': common_fields['id'],
        'created_at': common_fields['created_at'],
        'updated_at': common_fields['updated_at'],
        'generated_at': fields.DateTime(description='Report generation timestamp'),
        'file_path': fields.String(description='Generated report file path'),
        'metrics': fields.Raw(description='Report metrics and KPIs')
    })
    
    models['report_generation'] = api.model('ReportGeneration', {
        'report_id': fields.Integer(required=True, description='Report ID to generate', example=1),
        'format': fields.String(description='Output format', example='pdf', enum=['pdf', 'excel', 'json']),
        'include_charts': fields.Boolean(description='Include charts and visualizations', example=True)
    })
    
    # ============================================================================
    # 9. TARGETS MODELS
    # ============================================================================
    
    models['target_base'] = api.model('TargetBase', {
        'name': fields.String(required=True, description='Target name', example='Reduce Scope 1 Emissions by 30%'),
        'target_type': fields.String(required=True, description='Target type', 
                                   example='emissions_reduction', enum=['emissions_reduction', 'energy_efficiency', 'renewable_energy', 'waste_reduction', 'water_conservation', 'custom']),
        'scope': fields.Integer(description='GHG scope (for emission targets)', example=1),
        'baseline_year': fields.Integer(required=True, description='Baseline year', example=2020),
        'target_year': fields.Integer(required=True, description='Target achievement year', example=2030),
        'baseline_value': fields.Float(required=True, description='Baseline value', example=10000.0),
        'target_value': fields.Float(required=True, description='Target value', example=7000.0),
        'unit': fields.String(required=True, description='Target unit', example='tCO2e'),
        'description': fields.String(description='Target description', example='Reduce direct emissions through operational efficiency'),
        'status': fields.String(description='Target status', example='active', enum=['active', 'achieved', 'missed', 'cancelled'])
    })
    
    models['target_response'] = api.inherit('TargetResponse', models['target_base'], {
        'id': common_fields['id'],
        'created_at': common_fields['created_at'],
        'updated_at': common_fields['updated_at'],
        'current_value': fields.Float(description='Current progress value', example=8500.0),
        'progress_percentage': fields.Float(description='Progress percentage', example=50.0),
        'years_remaining': fields.Integer(description='Years remaining to target', example=6),
        'on_track': fields.Boolean(description='Whether target is on track', example=True)
    })
    
    # ============================================================================
    # 10. ASSETS MODELS
    # ============================================================================
    
    models['asset_base'] = api.model('AssetBase', {
        'name': fields.String(required=True, description='Asset name', example='New York Office Building'),
        'asset_type': fields.String(required=True, description='Asset type', 
                                  example='building', enum=['building', 'vehicle', 'equipment', 'land', 'other']),
        'location': fields.String(description='Asset location', example='123 Main St, New York, NY'),
        'description': fields.String(description='Asset description', example='10-story office building with 50,000 sq ft'),
        'acquisition_date': fields.Date(description='Acquisition date', example='2020-01-15'),
        'acquisition_cost': fields.Float(description='Acquisition cost in USD', example=5000000.00),
        'current_value': fields.Float(description='Current estimated value', example=5500000.00),
        'useful_life_years': fields.Integer(description='Useful life in years', example=30),
        'status': fields.String(description='Asset status', example='active', enum=['active', 'inactive', 'disposed', 'under_maintenance'])
    })
    
    models['asset_response'] = api.inherit('AssetResponse', models['asset_base'], {
        'id': common_fields['id'],
        'created_at': common_fields['created_at'],
        'updated_at': common_fields['updated_at'],
        'depreciation_rate': fields.Float(description='Annual depreciation rate', example=0.033),
        'environmental_metrics': fields.Raw(description='Environmental performance metrics')
    })
    
    models['asset_comparison'] = api.model('AssetComparison', {
        'asset1_id': fields.Integer(required=True, description='First asset ID', example=1),
        'asset2_id': fields.Integer(required=True, description='Second asset ID', example=2),
        'comparison_type': fields.String(description='Comparison type', example='environmental', enum=['financial', 'environmental', 'operational']),
        'metrics': fields.Raw(description='Comparison metrics')
    })
    
    # ============================================================================
    # 11. ASSET COMPARISONS MODELS (USER'S ADDITIONAL MODULE)
    # ============================================================================
    
    models['asset_comparison_proposal'] = api.model('AssetComparisonProposal', {
        'asset1_id': fields.Integer(required=True, description='First asset ID for comparison', example=1),
        'asset2_id': fields.Integer(required=True, description='Second asset ID for comparison', example=2),
        'comparison_criteria': fields.List(fields.String, description='Criteria for comparison', 
                                         example=['environmental_impact', 'financial_performance', 'operational_efficiency']),
        'notes': fields.String(description='Additional notes for the comparison', example='Quarterly performance comparison'),
        'requested_by': fields.String(description='User who requested the comparison', example='analyst@company.com')
    })
    
    models['asset_comparison_result'] = api.model('AssetComparisonResult', {
        'id': common_fields['id'],
        'asset1': fields.Raw(description='First asset details'),
        'asset2': fields.Raw(description='Second asset details'),
        'comparison_metrics': fields.Raw(description='Detailed comparison metrics'),
        'summary': fields.String(description='Comparison summary', example='Asset 1 performs 15% better in environmental metrics'),
        'recommendations': fields.List(fields.String, description='Recommendations based on comparison'),
        'created_at': common_fields['created_at'],
        'updated_at': common_fields['updated_at']
    })
    
    # ============================================================================
    # 12. PROJECTS MODELS
    # ============================================================================
    
    models['project_base'] = api.model('ProjectBase', {
        'name': fields.String(required=True, description='Project name', example='Solar Panel Installation'),
        'project_type': fields.String(required=True, description='Project type', 
                                    example='renewable_energy', enum=['renewable_energy', 'energy_efficiency', 'waste_reduction', 'water_conservation', 'carbon_offset', 'other']),
        'description': fields.String(description='Project description', example='Installation of 500kW solar panel system on office rooftop'),
        'start_date': fields.Date(required=True, description='Project start date', example='2024-03-01'),
        'end_date': fields.Date(description='Project end date', example='2024-06-30'),
        'budget': fields.Float(description='Project budget in USD', example=750000.00),
        'expected_savings': fields.Float(description='Expected annual savings', example=120000.00),
        'expected_emission_reduction': fields.Float(description='Expected annual emission reduction in tCO2e', example=250.5),
        'status': fields.String(description='Project status', example='planning', 
                              enum=['planning', 'in_progress', 'completed', 'on_hold', 'cancelled'])
    })
    
    models['project_response'] = api.inherit('ProjectResponse', models['project_base'], {
        'id': common_fields['id'],
        'created_at': common_fields['created_at'],
        'updated_at': common_fields['updated_at'],
        'actual_cost': fields.Float(description='Actual project cost', example=725000.00),
        'actual_savings': fields.Float(description='Actual annual savings achieved', example=115000.00),
        'actual_emission_reduction': fields.Float(description='Actual emission reduction achieved', example=245.2),
        'roi': fields.Float(description='Return on investment percentage', example=15.8),
        'completion_percentage': fields.Float(description='Project completion percentage', example=75.0)
    })
    
    # ============================================================================
    # 13. SUPPLIERS MODELS
    # ============================================================================
    
    models['supplier_base'] = api.model('SupplierBase', {
        'name': fields.String(required=True, description='Supplier name', example='Green Materials Corp'),
        'industry': fields.String(description='Supplier industry', example='Manufacturing'),
        'contact_email': fields.String(description='Contact email', example='contact@greenmaterials.com'),
        'contact_phone': fields.String(description='Contact phone', example='+1-555-0199'),
        'address': fields.String(description='Supplier address', example='456 Industrial Blvd, Detroit, MI'),
        'website': fields.String(description='Supplier website', example='https://greenmaterials.com'),
        'annual_spend': fields.Float(description='Annual spend with supplier', example=500000.00),
        'contract_start_date': fields.Date(description='Contract start date', example='2023-01-01'),
        'contract_end_date': fields.Date(description='Contract end date', example='2025-12-31'),
        'status': fields.String(description='Supplier status', example='active', enum=['active', 'inactive', 'under_review', 'terminated'])
    })
    
    models['supplier_response'] = api.inherit('SupplierResponse', models['supplier_base'], {
        'id': common_fields['id'],
        'created_at': common_fields['created_at'],
        'updated_at': common_fields['updated_at'],
        'esg_score': fields.Float(description='ESG assessment score (0-100)', example=78.5),
        'risk_level': fields.String(description='ESG risk level', example='medium', enum=['low', 'medium', 'high']),
        'last_assessment_date': fields.Date(description='Last ESG assessment date', example='2024-01-15'),
        'certifications': fields.List(fields.String, description='ESG certifications', example=['ISO 14001', 'B-Corp'])
    })
    
    models['supplier_assessment'] = api.model('SupplierAssessment', {
        'supplier_id': fields.Integer(required=True, description='Supplier ID', example=1),
        'assessment_date': fields.Date(required=True, description='Assessment date', example='2024-01-15'),
        'environmental_score': fields.Float(description='Environmental score (0-100)', example=85.0),
        'social_score': fields.Float(description='Social score (0-100)', example=75.0),
        'governance_score': fields.Float(description='Governance score (0-100)', example=80.0),
        'overall_score': fields.Float(description='Overall ESG score (0-100)', example=78.5),
        'notes': fields.String(description='Assessment notes', example='Strong environmental practices, needs improvement in social metrics')
    })
    
    # ============================================================================
    # 14. ESG STANDARDS MODELS
    # ============================================================================
    
    models['esg_standard_base'] = api.model('ESGStandardBase', {
        'name': fields.String(required=True, description='Standard name', example='GRI 305: Emissions'),
        'framework': fields.String(required=True, description='Framework', example='GRI', enum=['GRI', 'SASB', 'TCFD', 'CDP', 'CUSTOM']),
        'category': fields.String(description='Standard category', example='Environmental'),
        'description': fields.String(description='Standard description', example='Disclosure requirements for greenhouse gas emissions'),
        'requirements': fields.List(fields.String, description='List of requirements', example=['Direct GHG emissions', 'Indirect GHG emissions']),
        'is_mandatory': fields.Boolean(description='Mandatory compliance', example=False),
        'effective_date': fields.Date(description='Effective date', example='2024-01-01')
    })
    
    models['esg_standard_response'] = api.inherit('ESGStandardResponse', models['esg_standard_base'], {
        'id': common_fields['id'],
        'created_at': common_fields['created_at'],
        'updated_at': common_fields['updated_at'],
        'compliance_status': fields.String(description='Compliance status', example='compliant', enum=['compliant', 'non_compliant', 'in_progress', 'not_applicable'])
    })
    
    # ============================================================================
    # 15. API KEYS MODELS
    # ============================================================================
    
    models['api_key_base'] = api.model('ApiKeyBase', {
        'name': fields.String(required=True, description='API key name', example='Production Integration'),
        'description': fields.String(description='API key description', example='API key for production data integration'),
        'permissions': fields.List(fields.String, description='List of permissions', 
                                 example=['MEASUREMENTS_READ', 'REPORTS_READ']),
        'expires_at': fields.DateTime(description='Expiration date', example='2025-01-15T00:00:00Z'),
        'is_active': fields.Boolean(description='Active status', example=True)
    })
    
    models['api_key_response'] = api.inherit('ApiKeyResponse', models['api_key_base'], {
        'id': common_fields['id'],
        'key_prefix': fields.String(description='API key prefix (for identification)', example='esg_abc123'),
        'created_at': common_fields['created_at'],
        'updated_at': common_fields['updated_at'],
        'last_used_at': fields.DateTime(description='Last usage timestamp'),
        'usage_count': fields.Integer(description='Total usage count', example=1250),
        'created_by': fields.String(description='Created by user', example='admin')
    })
    
    models['api_key_create_response'] = api.inherit('ApiKeyCreateResponse', models['api_key_response'], {
        'api_key': fields.String(description='Full API key (only shown once)', example='esg_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz')
    })
    
    models['api_key_usage'] = api.model('ApiKeyUsage', {
        'api_key_id': fields.Integer(description='API key ID', example=1),
        'usage_count': fields.Integer(description='Usage count', example=1250),
        'last_used_at': fields.DateTime(description='Last usage timestamp'),
        'daily_usage': fields.List(fields.Raw, description='Daily usage statistics'),
        'endpoint_usage': fields.Raw(description='Usage by endpoint')
    })
    
    return models

if __name__ == '__main__':
    print("Comprehensive Flask-RESTX API Models for Complete ESG Platform")
    print("Covers all 15+ modules with detailed request/response models")
    print("Import and use create_all_models(api) in your Flask-RESTX setup")

