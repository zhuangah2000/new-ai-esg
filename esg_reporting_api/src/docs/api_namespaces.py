"""
Flask-RESTX Namespaces with Proper Security Decorators
COMPLETE VERSION - Includes ALL endpoints: Assets, Emission Factors, Suppliers, Targets, Projects
"""

from flask_restx import Namespace, Resource
from flask import request, jsonify, current_app
import json

def create_namespace(api, name, description, path):
    """Helper function to create a namespace with consistent styling"""
    return api.namespace(name, description=description, path=path)

def create_all_namespaces(api):
    """Create comprehensive namespaces that proxy to actual business endpoints"""
    
    # Import models
    try:
        from .api_models import create_all_models
        models = create_all_models(api)
    except ImportError:
        # Fallback if models not available
        models = {}
    
    namespaces = {}
    
    def proxy_request(endpoint_path, method='GET'):
        """Proxy a request to the actual API endpoint using Flask's test client"""
        try:
            # Use Flask's test client to make internal requests
            with current_app.test_client() as client:
                # Prepare headers - ENHANCED to capture all relevant headers
                headers = {}
                
                # Copy ALL headers from the original request
                for header_name, header_value in request.headers:
                    # Skip headers that might cause conflicts
                    if header_name.lower() not in ['host', 'content-length']:
                        headers[header_name] = header_value
                
                # DEBUG: Log headers being forwarded
                print(f"🔄 DEBUG: Proxying {method} {endpoint_path}")
                for header_name, header_value in headers.items():
                    if header_name.lower() == 'authorization':
                        print(f"   ✅ Authorization: {header_value[:20]}...")
                    else:
                        print(f"   📋 {header_name}: {header_value}")
                
                # Prepare the actual API path
                actual_path = f"/api{endpoint_path}"
                
                # Add query parameters if any
                if request.args:
                    query_string = '&'.join([f"{k}={v}" for k, v in request.args.items()])
                    actual_path += f"?{query_string}"
                
                # Make the internal request
                if method == 'GET':
                    response = client.get(actual_path, headers=headers)
                elif method == 'POST':
                    data = request.get_json() if request.is_json else None
                    response = client.post(actual_path, headers=headers, 
                                         data=json.dumps(data) if data else None,
                                         content_type='application/json' if data else None)
                elif method == 'PUT':
                    data = request.get_json() if request.is_json else None
                    response = client.put(actual_path, headers=headers,
                                        data=json.dumps(data) if data else None,
                                        content_type='application/json' if data else None)
                elif method == 'DELETE':
                    response = client.delete(actual_path, headers=headers)
                else:
                    return jsonify({'error': 'Unsupported method'}), 405
                
                # DEBUG: Log response
                print(f"📤 DEBUG: Response status: {response.status_code}")
                
                # Return the response
                try:
                    if response.data:
                        return json.loads(response.data), response.status_code
                    else:
                        return {}, response.status_code
                except json.JSONDecodeError:
                    return {'message': response.data.decode('utf-8')}, response.status_code
                    
        except Exception as e:
            print(f"❌ DEBUG: Proxy error: {str(e)}")
            return {'error': f'Proxy error: {str(e)}'}, 500
    
    # ============================================================================
    # 1. AUTHENTICATION NAMESPACE
    # ============================================================================
    
    auth_ns = create_namespace(api, 'Authentication', 
                              'User authentication and session management', '/auth')
    
    @auth_ns.route('/login')
    class AuthLogin(Resource):
        @auth_ns.doc('login_user', security='apikey')
        @auth_ns.response(200, 'Login successful')
        @auth_ns.response(401, 'Invalid credentials')
        def post(self):
            """Authenticate user and create session"""
            return proxy_request('/auth/login', 'POST')
    
    @auth_ns.route('/logout')
    class AuthLogout(Resource):
        @auth_ns.doc('logout_user', security='apikey')
        @auth_ns.response(200, 'Logout successful')
        def post(self):
            """Logout user and clear session"""
            return proxy_request('/auth/logout', 'POST')
    
    @auth_ns.route('/status')
    class AuthStatus(Resource):
        @auth_ns.doc('auth_status', security='apikey')
        @auth_ns.response(200, 'Authentication status retrieved')
        def get(self):
            """Get current authentication status"""
            return proxy_request('/auth/status', 'GET')
    
    namespaces['auth'] = auth_ns
    
    # ============================================================================
    # 2. USERS NAMESPACE
    # ============================================================================
    
    users_ns = create_namespace(api, 'Users', 
                               'User management and profiles', '/users')
    
    @users_ns.route('')
    class UsersList(Resource):
        @users_ns.doc('list_users', security='apikey')
        @users_ns.response(200, 'Users retrieved successfully')
        @users_ns.response(403, 'Insufficient permissions')
        def get(self):
            """Get list of all users"""
            print("🚀 DEBUG: UsersList.get() called via Swagger UI")
            return proxy_request('/users', 'GET')
        
        @users_ns.doc('create_user', security='apikey')
        @users_ns.response(201, 'User created successfully')
        @users_ns.response(400, 'Invalid user data')
        @users_ns.response(409, 'User already exists')
        def post(self):
            """Create a new user"""
            print("🚀 DEBUG: UsersList.post() called via Swagger UI")
            return proxy_request('/users', 'POST')
    
    @users_ns.route('/<int:user_id>')
    class UsersDetail(Resource):
        @users_ns.doc('get_user', security='apikey')
        @users_ns.response(200, 'User retrieved successfully')
        @users_ns.response(404, 'User not found')
        def get(self, user_id):
            """Get user by ID"""
            print(f"🚀 DEBUG: UsersDetail.get({user_id}) called via Swagger UI")
            return proxy_request(f'/users/{user_id}', 'GET')
        
        @users_ns.doc('update_user', security='apikey')
        @users_ns.response(200, 'User updated successfully')
        @users_ns.response(404, 'User not found')
        def put(self, user_id):
            """Update user information"""
            print(f"🚀 DEBUG: UsersDetail.put({user_id}) called via Swagger UI")
            return proxy_request(f'/users/{user_id}', 'PUT')
        
        @users_ns.doc('delete_user', security='apikey')
        @users_ns.response(200, 'User deleted successfully')
        @users_ns.response(404, 'User not found')
        def delete(self, user_id):
            """Delete user"""
            print(f"🚀 DEBUG: UsersDetail.delete({user_id}) called via Swagger UI")
            return proxy_request(f'/users/{user_id}', 'DELETE')
    
    namespaces['users'] = users_ns
    
    # ============================================================================
    # 3. ROLES NAMESPACE
    # ============================================================================
    
    roles_ns = create_namespace(api, 'Roles', 
                               'Role and permission management', '/roles')
    
    @roles_ns.route('')
    class RolesList(Resource):
        @roles_ns.doc('list_roles', security='apikey')
        @roles_ns.response(200, 'Roles retrieved successfully')
        def get(self):
            """Get list of all roles"""
            return proxy_request('/roles', 'GET')
        
        @roles_ns.doc('create_role', security='apikey')
        @roles_ns.response(201, 'Role created successfully')
        @roles_ns.response(400, 'Invalid role data')
        def post(self):
            """Create a new role"""
            return proxy_request('/roles', 'POST')
    
    @roles_ns.route('/<int:role_id>')
    class RolesDetail(Resource):
        @roles_ns.doc('get_role', security='apikey')
        @roles_ns.response(200, 'Role retrieved successfully')
        @roles_ns.response(404, 'Role not found')
        def get(self, role_id):
            """Get role by ID"""
            return proxy_request(f'/roles/{role_id}', 'GET')
        
        @roles_ns.doc('update_role', security='apikey')
        @roles_ns.response(200, 'Role updated successfully')
        @roles_ns.response(404, 'Role not found')
        def put(self, role_id):
            """Update role information"""
            return proxy_request(f'/roles/{role_id}', 'PUT')
        
        @roles_ns.doc('delete_role', security='apikey')
        @roles_ns.response(200, 'Role deleted successfully')
        @roles_ns.response(404, 'Role not found')
        def delete(self, role_id):
            """Delete role"""
            return proxy_request(f'/roles/{role_id}', 'DELETE')
    
    @roles_ns.route('/permissions')
    class RolePermissions(Resource):
        @roles_ns.doc('list_permissions', security='apikey')
        @roles_ns.response(200, 'Permissions retrieved successfully')
        def get(self):
            """Get list of all available permissions"""
            return proxy_request('/roles/permissions', 'GET')
    
    namespaces['roles'] = roles_ns
    
    # ============================================================================
    # 4. COMPANIES NAMESPACE
    # ============================================================================
    
    companies_ns = create_namespace(api, 'Companies', 
                                   'Company information and settings', '/companies')
    
    @companies_ns.route('')
    class CompaniesList(Resource):
        @companies_ns.doc('list_companies', security='apikey')
        @companies_ns.response(200, 'Companies retrieved successfully')
        def get(self):
            """Get list of all companies"""
            return proxy_request('/companies', 'GET')
        
        @companies_ns.doc('create_company', security='apikey')
        @companies_ns.response(201, 'Company created successfully')
        @companies_ns.response(400, 'Invalid company data')
        def post(self):
            """Create a new company"""
            return proxy_request('/companies', 'POST')
    
    @companies_ns.route('/<int:company_id>')
    class CompaniesDetail(Resource):
        @companies_ns.doc('get_company', security='apikey')
        @companies_ns.response(200, 'Company retrieved successfully')
        @companies_ns.response(404, 'Company not found')
        def get(self, company_id):
            """Get company by ID"""
            return proxy_request(f'/companies/{company_id}', 'GET')
        
        @companies_ns.doc('update_company', security='apikey')
        @companies_ns.response(200, 'Company updated successfully')
        @companies_ns.response(404, 'Company not found')
        def put(self, company_id):
            """Update company information"""
            return proxy_request(f'/companies/{company_id}', 'PUT')
        
        @companies_ns.doc('delete_company', security='apikey')
        @companies_ns.response(200, 'Company deleted successfully')
        @companies_ns.response(404, 'Company not found')
        def delete(self, company_id):
            """Delete company"""
            return proxy_request(f'/companies/{company_id}', 'DELETE')
    
    namespaces['companies'] = companies_ns
    
    # ============================================================================
    # 5. MEASUREMENTS NAMESPACE
    # ============================================================================
    
    measurements_ns = create_namespace(api, 'Measurements', 
                                     'Emission measurements and tracking', '/measurements')
    
    @measurements_ns.route('')
    class MeasurementsList(Resource):
        @measurements_ns.doc('list_measurements', security='apikey')
        @measurements_ns.response(200, 'Measurements retrieved successfully')
        def get(self):
            """Get list of all measurements"""
            return proxy_request('/measurements', 'GET')
        
        @measurements_ns.doc('create_measurement', security='apikey')
        @measurements_ns.response(201, 'Measurement created successfully')
        @measurements_ns.response(400, 'Invalid measurement data')
        def post(self):
            """Create a new measurement"""
            return proxy_request('/measurements', 'POST')
    
    @measurements_ns.route('/<int:measurement_id>')
    class MeasurementsDetail(Resource):
        @measurements_ns.doc('get_measurement', security='apikey')
        @measurements_ns.response(200, 'Measurement retrieved successfully')
        @measurements_ns.response(404, 'Measurement not found')
        def get(self, measurement_id):
            """Get measurement by ID"""
            return proxy_request(f'/measurements/{measurement_id}', 'GET')
        
        @measurements_ns.doc('update_measurement', security='apikey')
        @measurements_ns.response(200, 'Measurement updated successfully')
        @measurements_ns.response(404, 'Measurement not found')
        def put(self, measurement_id):
            """Update measurement information"""
            return proxy_request(f'/measurements/{measurement_id}', 'PUT')
        
        @measurements_ns.doc('delete_measurement', security='apikey')
        @measurements_ns.response(200, 'Measurement deleted successfully')
        @measurements_ns.response(404, 'Measurement not found')
        def delete(self, measurement_id):
            """Delete measurement"""
            return proxy_request(f'/measurements/{measurement_id}', 'DELETE')
    
    @measurements_ns.route('/summary')
    class MeasurementsSummary(Resource):
        @measurements_ns.doc('measurements_summary', security='apikey')
        @measurements_ns.response(200, 'Summary retrieved successfully')
        def get(self):
            """Get measurements summary and statistics"""
            return proxy_request('/measurements/summary', 'GET')
    
    namespaces['measurements'] = measurements_ns
    
    # ============================================================================
    # 6. DASHBOARD NAMESPACE
    # ============================================================================
    
    dashboard_ns = create_namespace(api, 'Dashboard', 
                                   'Analytics and reporting dashboard', '/dashboard')
    
    @dashboard_ns.route('/overview')
    class DashboardOverview(Resource):
        @dashboard_ns.doc('dashboard_overview', security='apikey')
        @dashboard_ns.response(200, 'Dashboard overview retrieved successfully')
        def get(self):
            """Get dashboard overview with key metrics"""
            return proxy_request('/dashboard/overview', 'GET')
    
    @dashboard_ns.route('/emissions-trend')
    class DashboardEmissionsTrend(Resource):
        @dashboard_ns.doc('emissions_trend', security='apikey')
        @dashboard_ns.response(200, 'Emissions trend data retrieved successfully')
        def get(self):
            """Get emissions trend analysis"""
            return proxy_request('/dashboard/emissions-trend', 'GET')
    
    @dashboard_ns.route('/intensity-metrics')
    class DashboardIntensityMetrics(Resource):
        @dashboard_ns.doc('intensity_metrics', security='apikey')
        @dashboard_ns.response(200, 'Intensity metrics retrieved successfully')
        def get(self):
            """Get emissions intensity metrics"""
            return proxy_request('/dashboard/intensity-metrics', 'GET')
    
    @dashboard_ns.route('/targets-progress')
    class DashboardTargetsProgress(Resource):
        @dashboard_ns.doc('targets_progress', security='apikey')
        @dashboard_ns.response(200, 'Targets progress retrieved successfully')
        def get(self):
            """Get ESG targets progress tracking"""
            return proxy_request('/dashboard/targets-progress', 'GET')
    
    namespaces['dashboard'] = dashboard_ns
    
    # ============================================================================
    # 7. API KEYS NAMESPACE
    # ============================================================================
    
    api_keys_ns = create_namespace(api, 'API Keys', 
                                  'API key management and authentication', '/api-keys')
    
    @api_keys_ns.route('')
    class ApiKeysList(Resource):
        @api_keys_ns.doc('list_api_keys', security='apikey')
        @api_keys_ns.response(200, 'API keys retrieved successfully')
        def get(self):
            """Get list of API keys"""
            return proxy_request('/api-keys', 'GET')
        
        @api_keys_ns.doc('create_api_key', security='apikey')
        @api_keys_ns.response(201, 'API key created successfully')
        @api_keys_ns.response(400, 'Invalid API key data')
        def post(self):
            """Create a new API key"""
            return proxy_request('/api-keys', 'POST')
    
    @api_keys_ns.route('/<int:key_id>')
    class ApiKeysDetail(Resource):
        @api_keys_ns.doc('get_api_key', security='apikey')
        @api_keys_ns.response(200, 'API key retrieved successfully')
        @api_keys_ns.response(404, 'API key not found')
        def get(self, key_id):
            """Get API key by ID"""
            return proxy_request(f'/api-keys/{key_id}', 'GET')
        
        @api_keys_ns.doc('update_api_key', security='apikey')
        @api_keys_ns.response(200, 'API key updated successfully')
        @api_keys_ns.response(404, 'API key not found')
        def put(self, key_id):
            """Update API key information"""
            return proxy_request(f'/api-keys/{key_id}', 'PUT')
        
        @api_keys_ns.doc('delete_api_key', security='apikey')
        @api_keys_ns.response(200, 'API key deleted successfully')
        @api_keys_ns.response(404, 'API key not found')
        def delete(self, key_id):
            """Delete API key"""
            return proxy_request(f'/api-keys/{key_id}', 'DELETE')
    
    namespaces['api_keys'] = api_keys_ns
    
    # ============================================================================
    # 8. ASSETS NAMESPACE - NEW!
    # ============================================================================
    
    assets_ns = create_namespace(api, 'Assets', 
                                'Asset management and environmental tracking', '/assets')
    
    @assets_ns.route('')
    class AssetsList(Resource):
        @assets_ns.doc('list_assets', security='apikey')
        @assets_ns.response(200, 'Assets retrieved successfully')
        def get(self):
            """Get list of all assets"""
            return proxy_request('/assets', 'GET')
        
        @assets_ns.doc('create_asset', security='apikey')
        @assets_ns.response(201, 'Asset created successfully')
        @assets_ns.response(400, 'Invalid asset data')
        def post(self):
            """Create a new asset"""
            return proxy_request('/assets', 'POST')
    
    @assets_ns.route('/<int:asset_id>')
    class AssetsDetail(Resource):
        @assets_ns.doc('get_asset', security='apikey')
        @assets_ns.response(200, 'Asset retrieved successfully')
        @assets_ns.response(404, 'Asset not found')
        def get(self, asset_id):
            """Get asset by ID"""
            return proxy_request(f'/assets/{asset_id}', 'GET')
        
        @assets_ns.doc('update_asset', security='apikey')
        @assets_ns.response(200, 'Asset updated successfully')
        @assets_ns.response(404, 'Asset not found')
        def put(self, asset_id):
            """Update asset information"""
            return proxy_request(f'/assets/{asset_id}', 'PUT')
        
        @assets_ns.doc('delete_asset', security='apikey')
        @assets_ns.response(200, 'Asset deleted successfully')
        @assets_ns.response(404, 'Asset not found')
        def delete(self, asset_id):
            """Delete asset"""
            return proxy_request(f'/assets/{asset_id}', 'DELETE')
    
    @assets_ns.route('/comparisons')
    class AssetComparisons(Resource):
        @assets_ns.doc('asset_comparisons', security='apikey')
        @assets_ns.response(200, 'Asset comparisons retrieved successfully')
        def get(self):
            """Get asset performance comparisons"""
            return proxy_request('/assets/comparisons', 'GET')
    
    namespaces['assets'] = assets_ns
    
    # ============================================================================
    # 9. EMISSION FACTORS NAMESPACE - NEW!
    # ============================================================================
    
    emission_factors_ns = create_namespace(api, 'Emission Factors', 
                                         'Emission factor management and calculations', '/emission-factors')
    
    @emission_factors_ns.route('')
    class EmissionFactorsList(Resource):
        @emission_factors_ns.doc('list_emission_factors', security='apikey')
        @emission_factors_ns.response(200, 'Emission factors retrieved successfully')
        def get(self):
            """Get list of all emission factors"""
            return proxy_request('/emission-factors', 'GET')
        
        @emission_factors_ns.doc('create_emission_factor', security='apikey')
        @emission_factors_ns.response(201, 'Emission factor created successfully')
        @emission_factors_ns.response(400, 'Invalid emission factor data')
        def post(self):
            """Create a new emission factor"""
            return proxy_request('/emission-factors', 'POST')
    
    @emission_factors_ns.route('/<int:factor_id>')
    class EmissionFactorsDetail(Resource):
        @emission_factors_ns.doc('get_emission_factor', security='apikey')
        @emission_factors_ns.response(200, 'Emission factor retrieved successfully')
        @emission_factors_ns.response(404, 'Emission factor not found')
        def get(self, factor_id):
            """Get emission factor by ID"""
            return proxy_request(f'/emission-factors/{factor_id}', 'GET')
        
        @emission_factors_ns.doc('update_emission_factor', security='apikey')
        @emission_factors_ns.response(200, 'Emission factor updated successfully')
        @emission_factors_ns.response(404, 'Emission factor not found')
        def put(self, factor_id):
            """Update emission factor information"""
            return proxy_request(f'/emission-factors/{factor_id}', 'PUT')
        
        @emission_factors_ns.doc('delete_emission_factor', security='apikey')
        @emission_factors_ns.response(200, 'Emission factor deleted successfully')
        @emission_factors_ns.response(404, 'Emission factor not found')
        def delete(self, factor_id):
            """Delete emission factor"""
            return proxy_request(f'/emission-factors/{factor_id}', 'DELETE')
    
    @emission_factors_ns.route('/active')
    class ActiveEmissionFactors(Resource):
        @emission_factors_ns.doc('active_emission_factors', security='apikey')
        @emission_factors_ns.response(200, 'Active emission factors retrieved successfully')
        def get(self):
            """Get list of active emission factors"""
            return proxy_request('/emission-factors/active', 'GET')
    
    @emission_factors_ns.route('/recalculate')
    class RecalculateEmissions(Resource):
        @emission_factors_ns.doc('recalculate_emissions', security='apikey')
        @emission_factors_ns.response(200, 'Recalculation completed successfully')
        def post(self):
            """Recalculate emissions with updated factors"""
            return proxy_request('/emission-factors/recalculate', 'POST')
    
    namespaces['emission_factors'] = emission_factors_ns
    
    # ============================================================================
    # 10. SUPPLIERS NAMESPACE - NEW!
    # ============================================================================
    
    suppliers_ns = create_namespace(api, 'Suppliers', 
                                   'Supplier management and ESG assessment', '/suppliers')
    
    @suppliers_ns.route('')
    class SuppliersList(Resource):
        @suppliers_ns.doc('list_suppliers', security='apikey')
        @suppliers_ns.response(200, 'Suppliers retrieved successfully')
        def get(self):
            """Get list of all suppliers"""
            return proxy_request('/suppliers', 'GET')
        
        @suppliers_ns.doc('create_supplier', security='apikey')
        @suppliers_ns.response(201, 'Supplier created successfully')
        @suppliers_ns.response(400, 'Invalid supplier data')
        def post(self):
            """Create a new supplier"""
            return proxy_request('/suppliers', 'POST')
    
    @suppliers_ns.route('/<int:supplier_id>')
    class SuppliersDetail(Resource):
        @suppliers_ns.doc('get_supplier', security='apikey')
        @suppliers_ns.response(200, 'Supplier retrieved successfully')
        @suppliers_ns.response(404, 'Supplier not found')
        def get(self, supplier_id):
            """Get supplier by ID"""
            return proxy_request(f'/suppliers/{supplier_id}', 'GET')
        
        @suppliers_ns.doc('update_supplier', security='apikey')
        @suppliers_ns.response(200, 'Supplier updated successfully')
        @suppliers_ns.response(404, 'Supplier not found')
        def put(self, supplier_id):
            """Update supplier information"""
            return proxy_request(f'/suppliers/{supplier_id}', 'PUT')
        
        @suppliers_ns.doc('delete_supplier', security='apikey')
        @suppliers_ns.response(200, 'Supplier deleted successfully')
        @suppliers_ns.response(404, 'Supplier not found')
        def delete(self, supplier_id):
            """Delete supplier"""
            return proxy_request(f'/suppliers/{supplier_id}', 'DELETE')
    
    @suppliers_ns.route('/<int:supplier_id>/assessment')
    class SupplierAssessment(Resource):
        @suppliers_ns.doc('supplier_assessment', security='apikey')
        @suppliers_ns.response(200, 'Supplier assessment retrieved successfully')
        def get(self, supplier_id):
            """Get supplier ESG assessment"""
            return proxy_request(f'/suppliers/{supplier_id}/assessment', 'GET')
        
        @suppliers_ns.doc('update_supplier_assessment', security='apikey')
        @suppliers_ns.response(200, 'Supplier assessment updated successfully')
        def put(self, supplier_id):
            """Update supplier ESG assessment"""
            return proxy_request(f'/suppliers/{supplier_id}/assessment', 'PUT')
    
    namespaces['suppliers'] = suppliers_ns
    
    # ============================================================================
    # 11. TARGETS NAMESPACE - NEW!
    # ============================================================================
    
    targets_ns = create_namespace(api, 'Targets', 
                                 'ESG targets and goal management', '/targets')
    
    @targets_ns.route('')
    class TargetsList(Resource):
        @targets_ns.doc('list_targets', security='apikey')
        @targets_ns.response(200, 'Targets retrieved successfully')
        def get(self):
            """Get list of all ESG targets"""
            return proxy_request('/targets', 'GET')
        
        @targets_ns.doc('create_target', security='apikey')
        @targets_ns.response(201, 'Target created successfully')
        @targets_ns.response(400, 'Invalid target data')
        def post(self):
            """Create a new ESG target"""
            return proxy_request('/targets', 'POST')
    
    @targets_ns.route('/<int:target_id>')
    class TargetsDetail(Resource):
        @targets_ns.doc('get_target', security='apikey')
        @targets_ns.response(200, 'Target retrieved successfully')
        @targets_ns.response(404, 'Target not found')
        def get(self, target_id):
            """Get target by ID"""
            return proxy_request(f'/targets/{target_id}', 'GET')
        
        @targets_ns.doc('update_target', security='apikey')
        @targets_ns.response(200, 'Target updated successfully')
        @targets_ns.response(404, 'Target not found')
        def put(self, target_id):
            """Update target information"""
            return proxy_request(f'/targets/{target_id}', 'PUT')
        
        @targets_ns.doc('delete_target', security='apikey')
        @targets_ns.response(200, 'Target deleted successfully')
        @targets_ns.response(404, 'Target not found')
        def delete(self, target_id):
            """Delete target"""
            return proxy_request(f'/targets/{target_id}', 'DELETE')
    
    @targets_ns.route('/progress')
    class TargetsProgress(Resource):
        @targets_ns.doc('targets_progress', security='apikey')
        @targets_ns.response(200, 'Targets progress retrieved successfully')
        def get(self):
            """Get progress tracking for all targets"""
            return proxy_request('/targets/progress', 'GET')
    
    namespaces['targets'] = targets_ns
    
    # ============================================================================
    # 12. PROJECTS NAMESPACE - NEW!
    # ============================================================================
    
    projects_ns = create_namespace(api, 'Projects', 
                                  'Sustainability project management', '/projects')
    
    @projects_ns.route('')
    class ProjectsList(Resource):
        @projects_ns.doc('list_projects', security='apikey')
        @projects_ns.response(200, 'Projects retrieved successfully')
        def get(self):
            """Get list of all sustainability projects"""
            return proxy_request('/projects', 'GET')
        
        @projects_ns.doc('create_project', security='apikey')
        @projects_ns.response(201, 'Project created successfully')
        @projects_ns.response(400, 'Invalid project data')
        def post(self):
            """Create a new sustainability project"""
            return proxy_request('/projects', 'POST')
    
    @projects_ns.route('/<int:project_id>')
    class ProjectsDetail(Resource):
        @projects_ns.doc('get_project', security='apikey')
        @projects_ns.response(200, 'Project retrieved successfully')
        @projects_ns.response(404, 'Project not found')
        def get(self, project_id):
            """Get project by ID"""
            return proxy_request(f'/projects/{project_id}', 'GET')
        
        @projects_ns.doc('update_project', security='apikey')
        @projects_ns.response(200, 'Project updated successfully')
        @projects_ns.response(404, 'Project not found')
        def put(self, project_id):
            """Update project information"""
            return proxy_request(f'/projects/{project_id}', 'PUT')
        
        @projects_ns.doc('delete_project', security='apikey')
        @projects_ns.response(200, 'Project deleted successfully')
        @projects_ns.response(404, 'Project not found')
        def delete(self, project_id):
            """Delete project"""
            return proxy_request(f'/projects/{project_id}', 'DELETE')
    
    @projects_ns.route('/<int:project_id>/impact')
    class ProjectImpact(Resource):
        @projects_ns.doc('project_impact', security='apikey')
        @projects_ns.response(200, 'Project impact retrieved successfully')
        def get(self, project_id):
            """Get project environmental impact analysis"""
            return proxy_request(f'/projects/{project_id}/impact', 'GET')
    
    namespaces['projects'] = projects_ns
    
    return namespaces

