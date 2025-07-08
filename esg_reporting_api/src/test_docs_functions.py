"""
Test specific docs functions to find the exact issue
"""

import sys
import traceback

print("🔍 Testing docs function imports...")

# Test 1: Import specific functions
try:
    from docs import create_api_documentation, create_common_models, create_all_models, create_all_namespaces
    print("✅ All docs functions imported successfully")
except ImportError as e:
    print(f"❌ Docs function import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Create Flask app
try:
    from flask import Flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key'
    print("✅ Flask app created")
except Exception as e:
    print(f"❌ Flask app creation failed: {e}")
    sys.exit(1)

# Test 3: Test create_api_documentation function
try:
    print("🔍 Testing create_api_documentation...")
    api = create_api_documentation(app)
    print(f"✅ API created successfully: {type(api)}")
    print(f"   API title: {getattr(api, 'title', 'Unknown')}")
    print(f"   API version: {getattr(api, 'version', 'Unknown')}")
except Exception as e:
    print(f"❌ create_api_documentation failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test create_common_models function
try:
    print("🔍 Testing create_common_models...")
    common_models = create_common_models(api)
    print(f"✅ Common models created: {type(common_models)}")
    print(f"   Models: {list(common_models.keys()) if isinstance(common_models, dict) else 'Not a dict'}")
except Exception as e:
    print(f"❌ create_common_models failed: {e}")
    traceback.print_exc()

# Test 5: Test create_all_models function
try:
    print("🔍 Testing create_all_models...")
    all_models = create_all_models(api)
    print(f"✅ All models created: {type(all_models)}")
    print(f"   Model count: {len(all_models) if isinstance(all_models, dict) else 'Not a dict'}")
except Exception as e:
    print(f"❌ create_all_models failed: {e}")
    traceback.print_exc()

# Test 6: Test create_all_namespaces function
try:
    print("🔍 Testing create_all_namespaces...")
    namespaces = create_all_namespaces(api)
    print(f"✅ All namespaces created: {type(namespaces)}")
    print(f"   Namespaces: {list(namespaces.keys()) if isinstance(namespaces, dict) else 'Not a dict'}")
except Exception as e:
    print(f"❌ create_all_namespaces failed: {e}")
    traceback.print_exc()

# Test 7: Check if swagger.json route exists
try:
    print("🔍 Checking Flask routes...")
    with app.app_context():
        rules = list(app.url_map.iter_rules())
        print(f"   Total routes: {len(rules)}")
        
        swagger_routes = [str(rule) for rule in rules if 'swagger' in str(rule).lower()]
        docs_routes = [str(rule) for rule in rules if 'docs' in str(rule).lower()]
        api_routes = [str(rule) for rule in rules if '/api/' in str(rule)]
        
        print(f"   Swagger routes: {swagger_routes}")
        print(f"   Docs routes: {docs_routes}")
        print(f"   API routes: {len(api_routes)}")
        
        if swagger_routes:
            print("✅ swagger.json route found!")
        else:
            print("❌ swagger.json route NOT found!")
            print("   All routes:")
            for rule in rules:
                print(f"     {rule}")
                
except Exception as e:
    print(f"❌ Route checking failed: {e}")
    traceback.print_exc()

# Test 8: Try to start the app briefly
try:
    print("🔍 Testing app startup...")
    
    # Add a simple test route
    @app.route('/test')
    def test():
        return {'status': 'test works'}
    
    print("✅ App setup complete")
    print("   Ready to test server startup")
    
except Exception as e:
    print(f"❌ App setup failed: {e}")
    traceback.print_exc()

print("\n🎯 Test complete! If all tests passed, the issue might be in your main.py structure.")

