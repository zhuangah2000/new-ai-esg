from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class EmissionFactor(db.Model):
    """Model for storing emission factors used in calculations"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    scope = db.Column(db.Integer, nullable=False)  # 1, 2, or 3
    category = db.Column(db.String(100), nullable=False)  # e.g., 'electricity', 'fuel', 'transportation'
    sub_category = db.Column(db.String(100))  # e.g., 'natural_gas', 'diesel', 'air_travel'
    factor_value = db.Column(db.Float, nullable=False)  # emission factor value
    unit = db.Column(db.String(50), nullable=False)  # e.g., 'kg CO2e/kWh', 'kg CO2e/liter'
    source = db.Column(db.String(100), nullable=False)  # e.g., 'EPA', 'DEFRA', 'Custom'
    effective_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    link = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'scope': self.scope,
            'category': self.category,
            'sub_category': self.sub_category,
            'factor_value': self.factor_value,
            'unit': self.unit,
            'source': self.source,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Measurement(db.Model):
    """Model for storing activity measurements"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200))  # facility or location name
    category = db.Column(db.String(100), nullable=False)  # e.g., 'electricity', 'fuel', 'transportation'
    sub_category = db.Column(db.String(100))  # specific type within category
    amount = db.Column(db.Float, nullable=False)  # measurement value
    unit = db.Column(db.String(50), nullable=False)  # measurement unit
    emission_factor_id = db.Column(db.Integer, db.ForeignKey('emission_factor.id'), nullable=False)
    calculated_emissions = db.Column(db.Float)  # calculated CO2e emissions
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    emission_factor = db.relationship('EmissionFactor', backref='measurements')

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'location': self.location,
            'category': self.category,
            'sub_category': self.sub_category,
            'amount': self.amount,
            'unit': self.unit,
            'emission_factor_id': self.emission_factor_id,
            'calculated_emissions': self.calculated_emissions,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'emission_factor': self.emission_factor.to_dict() if self.emission_factor else None
        }

class Supplier(db.Model):
    """Model for managing suppliers for Scope 3 emissions"""
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100))
    contact_person = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    esg_rating = db.Column(db.String(10))  # A, B, C, D, F rating
    data_completeness = db.Column(db.Float, default=0.0)  # percentage 0-100
    last_updated = db.Column(db.Date)
    status = db.Column(db.String(50), default='pending')  # pending, complete, overdue
    priority_level = db.Column(db.String(20), default='medium')  # low, medium, high
    scope3_categories = db.Column(db.Text)  # JSON string of applicable Scope 3 categories
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    annual_spend = db.Column(db.Float, default=0.0)  # Add this line

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'industry': self.industry,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'esg_rating': self.esg_rating,
            'data_completeness': self.data_completeness,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'status': self.status,
            'priority_level': self.priority_level,
            'scope3_categories': self.scope3_categories,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'annual_spend' : self.annual_spend
        }

class SupplierData(db.Model):
    """Model for storing ESG data from suppliers"""
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    data_type = db.Column(db.String(100), nullable=False)  # e.g., 'emissions', 'energy', 'waste'
    scope3_category = db.Column(db.String(100))  # specific Scope 3 category
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    reporting_period = db.Column(db.String(50))  # e.g., '2023', 'Q1 2023'
    data_quality = db.Column(db.String(20), default='estimated')  # measured, estimated, calculated
    verification_status = db.Column(db.String(20), default='unverified')  # verified, unverified
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    supplier = db.relationship('Supplier', backref='data_entries')

    def to_dict(self):
        # Safely get supplier information
        supplier_dict = None
        try:
            if self.supplier:
                supplier_dict = self.supplier.to_dict()
        except Exception:
            supplier_dict = None
        
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'data_type': self.data_type,
            'scope3_category': self.scope3_category,
            'value': self.value,
            'unit': self.unit,
            'reporting_period': self.reporting_period,
            'data_quality': self.data_quality,
            'verification_status': self.verification_status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'supplier': supplier_dict
        }

class ESGTarget(db.Model):
    """Model for storing ESG targets and goals"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_type = db.Column(db.String(50), nullable=False)  # e.g., 'emissions_reduction', 'energy_efficiency'
    scope = db.Column(db.Integer)  # 1, 2, 3, or null for non-emission targets
    baseline_value = db.Column(db.Float, nullable=False)
    baseline_year = db.Column(db.Integer, nullable=False)
    target_value = db.Column(db.Float, nullable=False)
    target_year = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    current_value = db.Column(db.Float)
    progress_percentage = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')  # active, achieved, at_risk, missed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'target_type': self.target_type,
            'scope': self.scope,
            'baseline_value': self.baseline_value,
            'baseline_year': self.baseline_year,
            'target_value': self.target_value,
            'target_year': self.target_year,
            'unit': self.unit,
            'current_value': self.current_value,
            'progress_percentage': self.progress_percentage,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Project(db.Model):
    """Enhanced model for managing ESG projects with target reduction"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    year = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='active') # active, completed, on_hold, cancelled
    
    # Target Reduction Fields
    target_reduction_percentage = db.Column(db.Float)  # e.g., 20.5 for 20.5% reduction
    target_reduction_absolute = db.Column(db.Float)    # e.g., 1000 for 1000 tCO2e reduction
    target_reduction_unit = db.Column(db.String(50))   # e.g., 'tCO2e', 'kWh', '%'
    baseline_value = db.Column(db.Float)               # Starting point for reduction calculation
    baseline_year = db.Column(db.Integer)              # Year of baseline measurement
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        # Safely get activities
        activities_list = []
        try:
            if hasattr(self, 'activities'):
                activities_list = [activity.to_dict() for activity in self.activities]
        except Exception:
            activities_list = []
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'year': self.year,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'target_reduction_percentage': self.target_reduction_percentage,
            'target_reduction_absolute': self.target_reduction_absolute,
            'target_reduction_unit': self.target_reduction_unit,
            'baseline_value': self.baseline_value,
            'baseline_year': self.baseline_year,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'activities': activities_list
        }

class ProjectActivity(db.Model):
    """Enhanced model for project activities with multiple emission factor categories"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='pending') # pending, in_progress, completed
    measurement_id = db.Column(db.Integer, db.ForeignKey('measurement.id'), nullable=True) # Keep for backward compatibility
    
    # Enhanced date tracking for timeline visualization
    start_date = db.Column(db.Date)                    # When activity actually starts
    end_date = db.Column(db.Date)                      # When activity was actually completed

    # Progress tracking
    completion_percentage = db.Column(db.Float, default=0.0)  # 0-100% completion
    estimated_hours = db.Column(db.Float)              # Estimated effort in hours
    actual_hours = db.Column(db.Float)                 # Actual effort spent in hours

    # Dependencies and blocking
    depends_on = db.Column(db.Text)                    # JSON array of activity IDs this depends on
    blocks = db.Column(db.Text)                        # JSON array of activity IDs this blocks

    # Additional tracking fields
    risk_level = db.Column(db.String(20), default='low')  # low, medium, high, critical
    budget_allocated = db.Column(db.Float)             # Budget allocated for this activity
    budget_spent = db.Column(db.Float, default=0.0)   # Budget actually spent
    
    # Multiple emission factor categories support
    emission_categories = db.Column(db.Text)  # JSON string of categories: ["electricity", "fuel", "water"]
    measurement_ids = db.Column(db.Text)      # JSON string of measurement IDs: [1, 2, 3]
    
    # Additional fields
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    assigned_to = db.Column(db.String(100))                # Person responsible
    notes = db.Column(db.Text)                             # Additional notes
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = db.relationship('Project', backref='activities')
    measurement = db.relationship('Measurement', backref='project_activities')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'measurement_id': self.measurement_id,  # Keep for backward compatibility
            'emission_categories': json.loads(self.emission_categories) if self.emission_categories else [],
            'measurement_ids': json.loads(self.measurement_ids) if self.measurement_ids else [],
            'priority': self.priority,
            'assigned_to': self.assigned_to,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'completion_percentage': self.completion_percentage,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'depends_on': json.loads(self.depends_on) if self.depends_on else [],
            'blocks': json.loads(self.blocks) if self.blocks else [],
            'risk_level': self.risk_level,
            'budget_allocated': self.budget_allocated,
            'budget_spent': self.budget_spent
        }

# Enhanced User Model for Settings functionality
class User(db.Model):
    """Enhanced model for user management with profile fields"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))  # For storing hashed passwords
    
    # Enhanced profile fields
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    job_title = db.Column(db.String(100))
    profile_picture = db.Column(db.String(500))  # URL to profile picture
    
    # Role and status
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False, default=4)  # Default to Viewer role
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationship
    role = db.relationship('Role', backref='users')

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        # Safely get role information with error handling
        role_name = None
        role_color = None
        
        try:
            if self.role:
                role_name = self.role.name
                role_color = self.role.color
        except Exception:
            # If there's any issue accessing the role, use defaults
            role_name = None
            role_color = None
        
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'department': self.department,
            'job_title': self.job_title,
            'profile_picture': self.profile_picture,
            'role_id': self.role_id,
            'role_name': role_name,
            'role_color': role_color,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

# Enhanced Role Model for granular permissions
class Role(db.Model):
    """Enhanced model for user roles with granular permissions"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)  # e.g., 'Administrator', 'Manager', 'Analyst', 'Viewer'
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#6b7280')  # Hex color for UI display
    
    # Granular permissions stored as JSON
    permissions = db.Column(db.Text)  # JSON string of module permissions
    
    # System role protection
    is_system_role = db.Column(db.Boolean, default=False)  # Prevents deletion of default roles
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        permissions_dict = {}
        if self.permissions:
            try:
                permissions_dict = json.loads(self.permissions)
            except (json.JSONDecodeError, TypeError):
                permissions_dict = {}
        
        # Safely get user count
        user_count = 0
        try:
            if hasattr(self, 'users'):
                user_count = len(self.users)
        except Exception:
            user_count = 0
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'permissions': permissions_dict,
            'is_system_role': self.is_system_role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_count': user_count
        }

# New Company Model for organization settings
class Company(db.Model):
    """Model for company profile and settings"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic company information
    name = db.Column(db.String(200), nullable=False)
    legal_name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100))
    description = db.Column(db.Text)
    website = db.Column(db.String(200))
    
    # Contact information
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    
    # Address
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Legal and registration
    tax_id = db.Column(db.String(50))
    registration_number = db.Column(db.String(50))
    
    # ESG reporting settings
    reporting_year = db.Column(db.Integer, default=datetime.now().year)
    fiscal_year_start = db.Column(db.String(5), default='01-01')  # MM-DD format
    fiscal_year_end = db.Column(db.String(5), default='12-31')    # MM-DD format
    currency = db.Column(db.String(3), default='USD')
    timezone = db.Column(db.String(50), default='UTC')
    
    # ESG frameworks and topics (stored as JSON)
    reporting_frameworks = db.Column(db.Text)  # JSON array of framework IDs
    materiality_topics = db.Column(db.Text)    # JSON array of topic IDs
    
    # Branding
    logo_url = db.Column(db.String(500))
    primary_color = db.Column(db.String(7), default='#10b981')    # Hex color
    secondary_color = db.Column(db.String(7), default='#3b82f6')  # Hex color
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        frameworks = []
        topics = []
        
        if self.reporting_frameworks:
            try:
                frameworks = json.loads(self.reporting_frameworks)
            except (json.JSONDecodeError, TypeError):
                frameworks = []
        
        if self.materiality_topics:
            try:
                topics = json.loads(self.materiality_topics)
            except (json.JSONDecodeError, TypeError):
                topics = []
        
        return {
            'id': self.id,
            'name': self.name,
            'legal_name': self.legal_name,
            'industry': self.industry,
            'description': self.description,
            'website': self.website,
            'email': self.email,
            'phone': self.phone,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'tax_id': self.tax_id,
            'registration_number': self.registration_number,
            'reporting_year': self.reporting_year,
            'fiscal_year_start': self.fiscal_year_start,
            'fiscal_year_end': self.fiscal_year_end,
            'currency': self.currency,
            'timezone': self.timezone,
            'reporting_frameworks': frameworks,
            'materiality_topics': topics,
            'logo_url': self.logo_url,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# New APIKey Model for API authentication
class APIKey(db.Model):
    """Model for API key management and authentication"""
    __tablename__ = 'api_key'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Key identification
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Key data (hashed for security)
    key_hash = db.Column(db.String(128), nullable=False, unique=True)
    key_prefix = db.Column(db.String(20), nullable=False)  # First few characters for display
    
    # Permissions and restrictions - FIXED: use correct column names
    permissions = db.Column(db.Text)  # JSON string of API permissions
    ip_whitelist = db.Column(db.Text)  # FIXED: use ip_whitelist instead of allowed_ips
    rate_limit = db.Column(db.Integer, default=1000)  # Requests per hour
    
    # Expiration and status
    expires_at = db.Column(db.DateTime)  # NULL means never expires
    is_active = db.Column(db.Boolean, default=True)
    
    # Usage tracking - FIXED: use correct column names
    usage_count = db.Column(db.Integer, default=0)
    last_used = db.Column(db.DateTime)  # FIXED: use last_used instead of last_used_at
    
    # Audit trail - FIXED: use correct column names
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # FIXED: use user_id instead of created_by
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships - FIXED: use correct foreign key
    creator = db.relationship('User', backref='api_keys', foreign_keys=[user_id])

    def to_dict(self):
        permissions_dict = {}
        allowed_ips_list = []
        
        if self.permissions:
            try:
                permissions_dict = json.loads(self.permissions)
            except (json.JSONDecodeError, TypeError):
                permissions_dict = {}
        
        # FIXED: use ip_whitelist instead of allowed_ips
        if self.ip_whitelist:
            try:
                allowed_ips_list = json.loads(self.ip_whitelist)
            except (json.JSONDecodeError, TypeError):
                allowed_ips_list = []
        
        # Safely get creator username
        creator_username = None
        try:
            if self.creator:
                creator_username = self.creator.username
        except Exception:
            creator_username = None
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'key_prefix': self.key_prefix,
            'permissions': permissions_dict,
            'allowed_ips': allowed_ips_list,  # Return as allowed_ips for frontend compatibility
            'rate_limit': self.rate_limit,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'usage_count': self.usage_count,
            'last_used_at': self.last_used.isoformat() if self.last_used else None,  # Return as last_used_at for frontend compatibility
            'created_by': self.user_id,  # Return as created_by for frontend compatibility
            'created_by_username': creator_username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Asset Management Models

class Asset(db.Model):
    """Model for managing physical assets like aircons, chillers, compressors, pumps etc."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    asset_type = db.Column(db.String(100), nullable=False)  # e.g., 'aircon', 'chiller', 'compressor', 'pump'
    model = db.Column(db.String(200))
    manufacturer = db.Column(db.String(200))
    serial_number = db.Column(db.String(100))
    location = db.Column(db.String(200))
    installation_date = db.Column(db.Date)
    capacity = db.Column(db.Float)  # e.g., cooling capacity in kW
    capacity_unit = db.Column(db.String(50))  # e.g., 'kW', 'TR', 'HP'
    power_rating = db.Column(db.Float)  # power consumption in kW
    efficiency_rating = db.Column(db.Float)  # e.g., COP, EER
    annual_kwh = db.Column(db.Float)  # estimated annual energy consumption
    annual_co2e = db.Column(db.Float)  # estimated annual CO2e emissions
    maintenance_schedule = db.Column(db.String(100))  # e.g., 'monthly', 'quarterly', 'annually'
    last_maintenance = db.Column(db.Date)
    next_maintenance = db.Column(db.Date)
    status = db.Column(db.String(50), default='active')  # active, inactive, maintenance, retired
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'asset_type': self.asset_type,
            'model': self.model,
            'manufacturer': self.manufacturer,
            'serial_number': self.serial_number,
            'location': self.location,
            'installation_date': self.installation_date.isoformat() if self.installation_date else None,
            'capacity': self.capacity,
            'capacity_unit': self.capacity_unit,
            'power_rating': self.power_rating,
            'efficiency_rating': self.efficiency_rating,
            'annual_kwh': self.annual_kwh,
            'annual_co2e': self.annual_co2e,
            'maintenance_schedule': self.maintenance_schedule,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'next_maintenance': self.next_maintenance.isoformat() if self.next_maintenance else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AssetComparison(db.Model):
    """Model for storing asset comparison scenarios"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    current_asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=True)
    created_by = db.Column(db.String(100))  # user who created the comparison
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    current_asset = db.relationship('Asset', backref='comparisons')

    def to_dict(self):
        # Safely get current asset
        current_asset_dict = None
        try:
            if self.current_asset:
                current_asset_dict = self.current_asset.to_dict()
        except Exception:
            current_asset_dict = None
        
        # Safely get proposals
        proposals_list = []
        try:
            if hasattr(self, 'proposals'):
                proposals_list = [proposal.to_dict() for proposal in self.proposals]
        except Exception:
            proposals_list = []
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'current_asset_id': self.current_asset_id,
            'current_asset': current_asset_dict,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'proposals': proposals_list
        }

class AssetComparisonProposal(db.Model):
    """Model for storing individual proposals in asset comparisons"""
    id = db.Column(db.Integer, primary_key=True)
    comparison_id = db.Column(db.Integer, db.ForeignKey('asset_comparison.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)  # e.g., 'High-Efficiency Centrifugal Chiller'
    manufacturer = db.Column(db.String(200))
    model = db.Column(db.String(200))
    power_rating = db.Column(db.Float)
    efficiency_rating = db.Column(db.Float)
    annual_kwh = db.Column(db.Float)
    annual_co2e = db.Column(db.Float)
    purchase_cost = db.Column(db.Float)
    installation_cost = db.Column(db.Float)
    annual_maintenance_cost = db.Column(db.Float)
    expected_lifespan = db.Column(db.Integer)  # in years
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    comparison = db.relationship('AssetComparison', backref='proposals')

    def to_dict(self):
        return {
            'id': self.id,
            'comparison_id': self.comparison_id,
            'name': self.name,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'power_rating': self.power_rating,
            'efficiency_rating': self.efficiency_rating,
            'annual_kwh': self.annual_kwh,
            'annual_co2e': self.annual_co2e,
            'purchase_cost': self.purchase_cost,
            'installation_cost': self.installation_cost,
            'annual_maintenance_cost': self.annual_maintenance_cost,
            'expected_lifespan': self.expected_lifespan,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SupplierESGStandard(db.Model):
    """Model for tracking ESG standards, frameworks, and assessments for suppliers"""
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    
    # Type of ESG standard/framework
    standard_type = db.Column(db.String(50), nullable=False)  # 'standard', 'framework', 'assessment'
    
    # Standard/Framework/Assessment name
    name = db.Column(db.String(100), nullable=False)
    
    # Submission details
    submission_year = db.Column(db.Integer)
    document_link = db.Column(db.String(500))
    status = db.Column(db.String(50), default='active')  # active, expired, pending, in_progress
    
    # Additional details
    score_rating = db.Column(db.String(20))  # For assessments that have scores
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    supplier = db.relationship('Supplier', backref='esg_standards')
    
    def to_dict(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'standard_type': self.standard_type,
            'name': self.name,
            'submission_year': self.submission_year,
            'document_link': self.document_link,
            'status': self.status,
            'score_rating': self.score_rating,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EmissionFactorRevision(db.Model):
    """Model for storing emission factor revision history"""
    __tablename__ = 'emission_factor_revision'
    
    id = db.Column(db.Integer, primary_key=True)
    parent_factor_id = db.Column(db.Integer, db.ForeignKey('emission_factor.id'), nullable=False)
    
    # Revision data (snapshot of the factor at this revision)
    name = db.Column(db.String(255), nullable=False)
    scope = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    sub_category = db.Column(db.String(100))
    factor_value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    source = db.Column(db.String(255), nullable=False)
    effective_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    link = db.Column(db.Text, nullable=True)
    
    # Revision metadata
    revision_notes = db.Column(db.Text)  # What changed in this revision
    version = db.Column(db.Integer, nullable=False)  # Version number (1, 2, 3, etc.)
    is_active = db.Column(db.Boolean, default=False)  # Only one revision can be active
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100))  # Optional: track who made the revision
    
    # Relationship
    parent_factor = db.relationship('EmissionFactor', backref='revisions')
    
    def __repr__(self):
        return f'<EmissionFactorRevision {self.name} v{self.version}>'

    def to_dict(self):
        return {
            'id': self.id,
            'parent_factor_id': self.parent_factor_id,
            'name': self.name,
            'scope': self.scope,
            'category': self.category,
            'sub_category': self.sub_category,
            'factor_value': self.factor_value,
            'unit': self.unit,
            'source': self.source,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'description': self.description,
            'link': self.link,
            'revision_notes': self.revision_notes,
            'version': self.version,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }

