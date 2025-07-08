"""
Integration Guide: Adding Flask-RESTX Documentation to Existing ESG Platform
Step-by-step guide to integrate API documentation with your current Flask application
"""

integration_steps = """
# 🚀 Flask-RESTX Integration Guide for ESG Platform

## 📋 Overview
This guide shows how to integrate the comprehensive API documentation with your existing Flask application.

## 🔧 Step 1: Install Dependencies
```bash
pip install flask-restx
```

## 📁 Step 2: File Placement
Place these files in your project structure:

```
your_esg_project/
├── src/
│   ├── routes/           # Your existing route files
│   ├── models/           # Your existing models
│   ├── docs/             # NEW: API documentation files
│   │   ├── __init__.py
│   │   ├── api_documentation.py
│   │   ├── api_models.py
│   │   └── api_namespaces.py
│   └── main.py           # Your existing main file
```

## 🔗 Step 3: Modify Your Main Flask App

### Option A: Minimal Integration (Recommended)
Add to your existing `main.py`:

```python
from flask import Flask
from flask_restx import Api

# Import documentation components
from docs.api_documentation import create_api_documentation
from docs.api_namespaces import create_all_namespaces

def create_app():
    app = Flask(__name__)
    
    # Your existing configuration
    # ... existing code ...
    
    # Add API documentation
    api = create_api_documentation(app)
    namespaces = create_all_namespaces(api)
    
    # Your existing blueprints
    # ... existing blueprint registrations ...
    
    return app
```

### Option B: Full Integration with Route Documentation
For each of your existing route files, add documentation decorators:

```python
# Example: measurements.py
from flask import Blueprint
from flask_restx import Namespace, Resource

# Create namespace for this module
measurements_ns = Namespace('measurements', description='Emission measurements')

@measurements_ns.route('')
class MeasurementsList(Resource):
    @measurements_ns.doc('get_measurements')
    def get(self):
        # Your existing get_measurements() function code
        pass
    
    @measurements_ns.doc('create_measurement')
    def post(self):
        # Your existing create_measurement() function code
        pass
```

## 🎯 Step 4: Quick Start (Standalone)
For immediate testing, use the standalone version:

```bash
python main_with_docs.py
```

Then visit: http://localhost:5000/docs/

## 🔐 Step 5: Authentication Integration
The documentation automatically supports your existing authentication:

### Session Authentication
- Users login via `/api/auth/login`
- Session cookies work automatically with Swagger UI

### API Key Authentication
- Add `Authorization: Bearer esg_your_key` header
- Swagger UI has built-in authorization button

## 📊 Step 6: Customize Documentation
Edit `api_documentation.py` to customize:

```python
api_config = {
    'title': 'Your Company ESG API',
    'description': 'Your custom description...',
    'contact': 'your-team@company.com',
    # ... other customizations
}
```

## 🧪 Step 7: Test the Integration

### 1. Start your application
```bash
python main.py  # or your startup command
```

### 2. Access documentation
- **Swagger UI**: http://localhost:5000/docs/
- **API Spec**: http://localhost:5000/swagger.json
- **Welcome**: http://localhost:5000/

### 3. Test authentication
- Click "Authorize" button in Swagger UI
- Enter your API key: `esg_your_key`
- Test endpoints directly in the browser

## 🎨 Step 8: Customization Options

### Custom Styling
Add custom CSS to Swagger UI:

```python
# In api_documentation.py
api = Api(
    app,
    # ... existing config ...
    doc='/docs/',
    # Add custom CSS
    css_url='/static/swagger-custom.css'
)
```

### Custom Models
Add your specific models in `api_models.py`:

```python
custom_model = api.model('CustomModel', {
    'field1': fields.String(description='Your field'),
    'field2': fields.Integer(description='Your integer field')
})
```

### Additional Namespaces
Add company-specific namespaces in `api_namespaces.py`:

```python
custom_ns = create_namespace(
    api,
    'Custom Module',
    'Your custom module description',
    '/custom'
)
```

## 🚨 Troubleshooting

### Common Issues:

1. **Import Errors**
   - Ensure all files are in the correct directory
   - Check Python path includes your project root

2. **Authentication Not Working**
   - Verify your auth middleware is properly imported
   - Check API key format: `Bearer esg_your_key`

3. **Documentation Not Loading**
   - Check Flask-RESTX is installed: `pip install flask-restx`
   - Verify no port conflicts on 5000

4. **CORS Issues**
   - Ensure CORS is enabled: `CORS(app, supports_credentials=True)`
   - Check browser console for CORS errors

### Debug Mode:
```python
app.run(debug=True)  # Enable detailed error messages
```

## 📈 Benefits You'll Get:

✅ **Professional API Documentation** - Auto-generated from your code
✅ **Interactive Testing** - Test all endpoints in the browser
✅ **Authentication Support** - Works with your existing auth system
✅ **Organized Structure** - Clean separation by module
✅ **Industry Standard** - Swagger/OpenAPI compliance
✅ **Mobile Friendly** - Responsive design for any device
✅ **Zero Maintenance** - Updates automatically with code changes

## 🎯 Next Steps:

1. **Integrate with CI/CD** - Auto-deploy documentation
2. **Add Examples** - Include request/response examples
3. **Custom Themes** - Brand the documentation
4. **API Versioning** - Support multiple API versions
5. **Rate Limiting** - Add usage quotas and monitoring

## 📞 Support:
If you encounter any issues during integration, the documentation is designed to be:
- **Non-invasive**: Won't break existing functionality
- **Incremental**: Can be added gradually
- **Flexible**: Customize to your needs

Happy documenting! 🚀
"""

def print_integration_guide():
    """Print the complete integration guide"""
    print(integration_steps)

def create_init_file():
    """Create __init__.py for docs package"""
    return '''"""
ESG Platform API Documentation Package
"""

from .api_documentation import create_api_documentation, create_common_models
from .api_models import create_all_models
from .api_namespaces import create_all_namespaces

__all__ = [
    'create_api_documentation',
    'create_common_models', 
    'create_all_models',
    'create_all_namespaces'
]
'''

def create_requirements_addition():
    """Additional requirements for the documentation"""
    return """
# Additional requirements for API documentation
flask-restx==1.3.0
aniso8601>=0.82
jsonschema
"""

if __name__ == '__main__':
    print("📚 Flask-RESTX Integration Guide for ESG Platform")
    print("=" * 60)
    print_integration_guide()
    
    print("\n" + "=" * 60)
    print("📁 Additional Files Needed:")
    print("- docs/__init__.py")
    print("- requirements.txt (add flask-restx)")
    
    print("\n🔧 __init__.py content:")
    print(create_init_file())
    
    print("\n📦 Requirements addition:")
    print(create_requirements_addition())

