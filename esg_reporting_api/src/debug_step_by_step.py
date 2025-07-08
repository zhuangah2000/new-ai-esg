"""
Step-by-step debug script to identify what broke the Swagger documentation
"""

import sys
import traceback

print("🔍 DEBUGGING: What broke the Swagger documentation?")
print("=" * 60)

# Step 1: Test basic Flask-RESTX
print("\n1️⃣ Testing basic Flask-RESTX...")
try:
    from flask import Flask
    from flask_restx import Api
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test'
    
    # Create minimal API
    api = Api(app, title='Test API', doc='/docs/')
    
    print("✅ Basic Flask-RESTX works")
    
    # Test if swagger.json route exists
    with app.app_context():
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        swagger_routes = [rule for rule in rules if 'swagger' in rule.lower()]
        print(f"   Swagger routes found: {swagger_routes}")
        
        if swagger_routes:
            print("✅ swagger.json route created successfully")
        else:
            print("❌ swagger.json route NOT created")
            
except Exception as e:
    print(f"❌ Basic Flask-RESTX failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 2: Test docs imports
print("\n2️⃣ Testing docs imports...")
try:
    from docs.api_documentation import create_api_documentation, create_common_models
    print("✅ api_documentation imports work")
except Exception as e:
    print(f"❌ api_documentation import failed: {e}")
    traceback.print_exc()

try:
    from docs.api_models import create_all_models
    print("✅ api_models imports work")
except Exception as e:
    print(f"❌ api_models import failed: {e}")
    traceback.print_exc()

try:
    from docs.api_namespaces import create_all_namespaces
    print("✅ api_namespaces imports work")
except Exception as e:
    print(f"❌ api_namespaces import failed: {e}")
    traceback.print_exc()

# Step 3: Test API creation
print("\n3️⃣ Testing API creation...")
try:
    app2 = Flask(__name__)
    app2.config['SECRET_KEY'] = 'test'
    
    api2 = create_api_documentation(app2)
    print(f"✅ API created: {type(api2)}")
    
    # Check routes
    with app2.app_context():
        rules = [str(rule) for rule in app2.url_map.iter_rules()]
        swagger_routes = [rule for rule in rules if 'swagger' in rule.lower()]
        docs_routes = [rule for rule in rules if 'docs' in rule.lower()]
        
        print(f"   Total routes: {len(rules)}")
        print(f"   Swagger routes: {swagger_routes}")
        print(f"   Docs routes: {docs_routes}")
        
        if swagger_routes:
            print("✅ API creation preserves swagger.json route")
        else:
            print("❌ API creation breaks swagger.json route")
            
except Exception as e:
    print(f"❌ API creation failed: {e}")
    traceback.print_exc()

# Step 4: Test models creation
print("\n4️⃣ Testing models creation...")
try:
    models = create_common_models(api2)
    print(f"✅ Common models created: {list(models.keys())}")
except Exception as e:
    print(f"❌ Common models creation failed: {e}")
    traceback.print_exc()

try:
    all_models = create_all_models(api2)
    print(f"✅ All models created: {len(all_models)} models")
except Exception as e:
    print(f"❌ All models creation failed: {e}")
    traceback.print_exc()

# Step 5: Test namespaces creation (this is likely where it breaks)
print("\n5️⃣ Testing namespaces creation...")
try:
    namespaces = create_all_namespaces(api2)
    print(f"✅ Namespaces created: {list(namespaces.keys())}")
    
    # Check routes after namespace creation
    with app2.app_context():
        rules = [str(rule) for rule in app2.url_map.iter_rules()]
        swagger_routes = [rule for rule in rules if 'swagger' in rule.lower()]
        
        print(f"   Routes after namespaces: {len(rules)}")
        print(f"   Swagger routes after namespaces: {swagger_routes}")
        
        if swagger_routes:
            print("✅ Namespaces preserve swagger.json route")
        else:
            print("❌ Namespaces break swagger.json route")
            
except Exception as e:
    print(f"❌ Namespaces creation failed: {e}")
    traceback.print_exc()

# Step 6: Test minimal working version
print("\n6️⃣ Testing minimal working version...")
try:
    app3 = Flask(__name__)
    app3.config['SECRET_KEY'] = 'test'
    
    # Create API with minimal setup
    api3 = Api(app3, title='Minimal ESG API', doc='/docs/')
    
    # Add just one simple namespace
    ns = api3.namespace('test', description='Test namespace')
    
    @ns.route('/hello')
    class TestHello(api3.Resource):
        def get(self):
            return {'message': 'hello'}
    
    with app3.app_context():
        rules = [str(rule) for rule in app3.url_map.iter_rules()]
        swagger_routes = [rule for rule in rules if 'swagger' in rule.lower()]
        
        print(f"✅ Minimal version works")
        print(f"   Routes: {len(rules)}")
        print(f"   Swagger routes: {swagger_routes}")
        
except Exception as e:
    print(f"❌ Minimal version failed: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("🎯 DIAGNOSIS COMPLETE!")
print("\nLook for the step where swagger routes disappear.")
print("That's where the problem is!")
print("\nIf step 5 (namespaces) fails, the issue is in api_namespaces.py")
print("If step 4 (models) fails, the issue is in api_models.py")
print("If step 3 (API creation) fails, the issue is in api_documentation.py")

