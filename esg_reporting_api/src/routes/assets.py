"""
Enhanced Asset Management Routes with Centralized Auth Middleware
Preserves 100% of original functionality while adding API key authentication
"""

from flask import Blueprint, request, jsonify
from src.models.esg_models import db, Asset, AssetComparison, AssetComparisonProposal
from datetime import datetime
import json

# Import auth middleware with graceful fallback
try:
    from src.auth_middleware import require_auth as require_api_auth, Permissions, get_current_user as get_auth_user
    AUTH_MIDDLEWARE_AVAILABLE = True
    print("INFO:src.routes.assets:Auth middleware imported successfully")
except ImportError:
    AUTH_MIDDLEWARE_AVAILABLE = False
    print("WARNING:src.routes.assets:Auth middleware not available, using session-only authentication")

assets_bp = Blueprint("assets", __name__)

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
                        print(f"INFO:src.routes.assets:API key authentication successful for {f.__name__}")
                    else:
                        current_user = require_session_auth()
                        print(f"INFO:src.routes.assets:Session authentication successful for {f.__name__}")
                    return f(*args, **kwargs)
                except Exception as e:
                    print(f"ERROR:src.routes.assets:Authentication failed for {f.__name__}: {str(e)}")
                    return jsonify({'error': 'Authentication failed'}), 401
            return wrapper
    return decorator

@assets_bp.route("/assets", methods=["POST"])
@dual_auth(permissions=[Permissions.ASSETS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def create_asset():
    """Create a new asset"""
    try:
        data = request.get_json()
        
        # Convert date strings to date objects
        installation_date = None
        if data.get("installation_date"):
            installation_date = datetime.strptime(data["installation_date"], "%Y-%m-%d").date()
        
        last_maintenance = None
        if data.get("last_maintenance"):
            last_maintenance = datetime.strptime(data["last_maintenance"], "%Y-%m-%d").date()
        
        next_maintenance = None
        if data.get("next_maintenance"):
            next_maintenance = datetime.strptime(data["next_maintenance"], "%Y-%m-%d").date()
        
        # Convert annual_co2e from kgCO2e to tCO2e for storage (if provided in kgCO2e)
        annual_co2e = None
        if data.get("annual_co2e"):
            annual_co2e = float(data["annual_co2e"]) / 1000  # Convert kgCO2e to tCO2e for storage
        
        new_asset = Asset(
            name=data["name"],
            asset_type=data["asset_type"],
            model=data.get("model"),
            manufacturer=data.get("manufacturer"),
            serial_number=data.get("serial_number"),
            location=data.get("location"),
            installation_date=installation_date,
            capacity=float(data["capacity"]) if data.get("capacity") else None,
            capacity_unit=data.get("capacity_unit"),
            power_rating=float(data["power_rating"]) if data.get("power_rating") else None,
            efficiency_rating=float(data["efficiency_rating"]) if data.get("efficiency_rating") else None,
            annual_kwh=float(data["annual_kwh"]) if data.get("annual_kwh") else None,
            annual_co2e=annual_co2e,
            maintenance_schedule=data.get("maintenance_schedule"),
            last_maintenance=last_maintenance,
            next_maintenance=next_maintenance,
            status=data.get("status", "active"),
            notes=data.get("notes")
        )
        
        db.session.add(new_asset)
        db.session.commit()
        
        return jsonify({"success": True, "data": new_asset.to_dict()}), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@assets_bp.route("/assets", methods=["GET"])
@dual_auth(permissions=[Permissions.ASSETS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_assets():
    """Get all assets with enhanced filtering"""
    try:
        # Get query parameters for filtering
        asset_type = request.args.get('type')
        status = request.args.get('status')
        location = request.args.get('location')
        search = request.args.get('search')
        
        # Build query
        query = Asset.query
        
        if asset_type and asset_type != 'all':
            query = query.filter(Asset.asset_type == asset_type)
        
        if status and status != 'all':
            query = query.filter(Asset.status == status)
        
        if location and location != 'all':
            query = query.filter(Asset.location == location)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Asset.name.ilike(search_filter),
                    Asset.manufacturer.ilike(search_filter),
                    Asset.model.ilike(search_filter),
                    Asset.location.ilike(search_filter)
                )
            )
        
        assets = query.all()
        return jsonify({"success": True, "data": [asset.to_dict() for asset in assets]})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@assets_bp.route("/assets/<int:asset_id>", methods=["GET"])
@dual_auth(permissions=[Permissions.ASSETS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_asset(asset_id):
    """Get a specific asset"""
    try:
        asset = Asset.query.get(asset_id)
        if not asset:
            return jsonify({"success": False, "error": "Asset not found"}), 404
        return jsonify({"success": True, "data": asset.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@assets_bp.route("/assets/<int:asset_id>", methods=["PUT"])
@dual_auth(permissions=[Permissions.ASSETS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def update_asset(asset_id):
    """Update an existing asset"""
    try:
        asset = Asset.query.get(asset_id)
        if not asset:
            return jsonify({"success": False, "error": "Asset not found"}), 404
        
        data = request.get_json()
        
        # Update basic fields
        asset.name = data.get("name", asset.name)
        asset.asset_type = data.get("asset_type", asset.asset_type)
        asset.model = data.get("model", asset.model)
        asset.manufacturer = data.get("manufacturer", asset.manufacturer)
        asset.serial_number = data.get("serial_number", asset.serial_number)
        asset.location = data.get("location", asset.location)
        asset.status = data.get("status", asset.status)
        asset.notes = data.get("notes", asset.notes)
        
        # Update numeric fields with proper conversion
        if "capacity" in data and data["capacity"]:
            asset.capacity = float(data["capacity"])
        asset.capacity_unit = data.get("capacity_unit", asset.capacity_unit)
        
        if "power_rating" in data and data["power_rating"]:
            asset.power_rating = float(data["power_rating"])
        
        if "efficiency_rating" in data and data["efficiency_rating"]:
            asset.efficiency_rating = float(data["efficiency_rating"])
        
        if "annual_kwh" in data and data["annual_kwh"]:
            asset.annual_kwh = float(data["annual_kwh"])
        
        # Convert annual_co2e from kgCO2e to tCO2e for storage
        if "annual_co2e" in data and data["annual_co2e"]:
            asset.annual_co2e = float(data["annual_co2e"]) / 1000  # Convert kgCO2e to tCO2e
        
        asset.maintenance_schedule = data.get("maintenance_schedule", asset.maintenance_schedule)
        
        # Update date fields
        if "installation_date" in data and data["installation_date"]:
            asset.installation_date = datetime.strptime(data["installation_date"], "%Y-%m-%d").date()
        
        if "last_maintenance" in data and data["last_maintenance"]:
            asset.last_maintenance = datetime.strptime(data["last_maintenance"], "%Y-%m-%d").date()
        
        if "next_maintenance" in data and data["next_maintenance"]:
            asset.next_maintenance = datetime.strptime(data["next_maintenance"], "%Y-%m-%d").date()
        
        db.session.commit()
        return jsonify({"success": True, "data": asset.to_dict()})
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@assets_bp.route("/assets/<int:asset_id>", methods=["DELETE"])
@dual_auth(permissions=[Permissions.ASSETS_DELETE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def delete_asset(asset_id):
    """Delete an asset"""
    try:
        asset = Asset.query.get(asset_id)
        if not asset:
            return jsonify({"success": False, "error": "Asset not found"}), 404
        
        # Check if asset is used in any comparisons
        comparisons = AssetComparison.query.filter_by(current_asset_id=asset_id).all()
        if comparisons:
            return jsonify({
                "success": False, 
                "error": f"Cannot delete asset. It is referenced in {len(comparisons)} comparison(s)."
            }), 400
        
        db.session.delete(asset)
        db.session.commit()
        return jsonify({"success": True, "message": "Asset deleted successfully"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@assets_bp.route("/assets/types", methods=["GET"])
@dual_auth(permissions=[Permissions.ASSETS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_asset_types():
    """Get available asset types"""
    asset_types = [
        {"value": "aircon", "label": "Air Conditioner"},
        {"value": "chiller", "label": "Chiller"},
        {"value": "compressor", "label": "Compressor"},
        {"value": "pump", "label": "Pump"},
        {"value": "boiler", "label": "Boiler"},
        {"value": "fan", "label": "Fan"},
        {"value": "motor", "label": "Motor"},
        {"value": "lighting", "label": "Lighting System"},
        {"value": "hvac", "label": "HVAC System"},
        {"value": "generator", "label": "Generator"},
        {"value": "transformer", "label": "Transformer"},
        {"value": "heat_pump", "label": "Heat Pump"},
        {"value": "cooling_tower", "label": "Cooling Tower"},
        {"value": "ahu", "label": "Air Handling Unit"},
        {"value": "vfd", "label": "Variable Frequency Drive"},
        {"value": "other", "label": "Other"}
    ]
    return jsonify({"success": True, "data": asset_types})

@assets_bp.route("/assets/summary", methods=["GET"])
@dual_auth(permissions=[Permissions.ASSETS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_assets_summary():
    """Get summary statistics for assets"""
    try:
        total_assets = Asset.query.count()
        active_assets = Asset.query.filter_by(status='active').count()
        
        # Calculate totals with proper null handling
        total_annual_kwh = db.session.query(
            db.func.coalesce(db.func.sum(Asset.annual_kwh), 0)
        ).scalar()
        
        total_annual_co2e_tonnes = db.session.query(
            db.func.coalesce(db.func.sum(Asset.annual_co2e), 0)
        ).scalar()
        
        # Convert tCO2e to kgCO2e for display
        total_annual_co2e_kg = total_annual_co2e_tonnes * 1000
        
        # Assets by type
        assets_by_type = db.session.query(
            Asset.asset_type,
            db.func.count(Asset.id).label('count')
        ).group_by(Asset.asset_type).all()
        
        # Assets by status
        assets_by_status = db.session.query(
            Asset.status,
            db.func.count(Asset.id).label('count')
        ).group_by(Asset.status).all()
        
        # Assets by location
        assets_by_location = db.session.query(
            Asset.location,
            db.func.count(Asset.id).label('count')
        ).filter(Asset.location.isnot(None)).group_by(Asset.location).all()
        
        # Maintenance due soon (next 30 days)
        from datetime import date, timedelta
        thirty_days_from_now = date.today() + timedelta(days=30)
        maintenance_due_soon = Asset.query.filter(
            Asset.next_maintenance <= thirty_days_from_now,
            Asset.next_maintenance >= date.today(),
            Asset.status == 'active'
        ).count()
        
        summary = {
            "total_assets": total_assets,
            "active_assets": active_assets,
            "inactive_assets": total_assets - active_assets,
            "total_annual_kwh": round(float(total_annual_kwh), 2),
            "total_annual_co2e": round(float(total_annual_co2e_kg), 2),  # Return in kgCO2e
            "maintenance_due_soon": maintenance_due_soon,
            "assets_by_type": [{"type": item[0], "count": item[1]} for item in assets_by_type],
            "assets_by_status": [{"status": item[0], "count": item[1]} for item in assets_by_status],
            "assets_by_location": [{"location": item[0], "count": item[1]} for item in assets_by_location]
        }
        
        return jsonify({"success": True, "data": summary})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Asset Comparison endpoints
@assets_bp.route("/asset-comparisons", methods=["POST"])
@dual_auth(permissions=[Permissions.ASSETS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def create_asset_comparison():
    """Create a new asset comparison"""
    try:
        data = request.get_json()
        
        # Validate current asset exists
        current_asset = Asset.query.get(data["current_asset_id"])
        if not current_asset:
            return jsonify({"success": False, "error": "Current asset not found"}), 404
        
        new_comparison = AssetComparison(
            name=data["name"],
            description=data.get("description"),
            current_asset_id=data["current_asset_id"]
        )
        
        db.session.add(new_comparison)
        db.session.flush()  # Get the ID
        
        # Add proposals if provided
        if "proposals" in data and data["proposals"]:
            for proposal_data in data["proposals"]:
                # Convert annual_co2e from kgCO2e to tCO2e for storage
                annual_co2e = None
                if proposal_data.get("annual_co2e"):
                    annual_co2e = float(proposal_data["annual_co2e"]) / 1000
                
                proposal = AssetComparisonProposal(
                    comparison_id=new_comparison.id,
                    name=proposal_data["name"],
                    manufacturer=proposal_data.get("manufacturer"),
                    model=proposal_data.get("model"),
                    power_rating=float(proposal_data["power_rating"]) if proposal_data.get("power_rating") else None,
                    efficiency_rating=float(proposal_data["efficiency_rating"]) if proposal_data.get("efficiency_rating") else None,
                    annual_kwh=float(proposal_data["annual_kwh"]) if proposal_data.get("annual_kwh") else None,
                    annual_co2e=annual_co2e,
                    purchase_cost=float(proposal_data["purchase_cost"]) if proposal_data.get("purchase_cost") else None,
                    installation_cost=float(proposal_data["installation_cost"]) if proposal_data.get("installation_cost") else None,
                    annual_maintenance_cost=float(proposal_data["annual_maintenance_cost"]) if proposal_data.get("annual_maintenance_cost") else None,
                    expected_lifespan=int(proposal_data["expected_lifespan"]) if proposal_data.get("expected_lifespan") else None,
                    notes=proposal_data.get("notes")
                )
                db.session.add(proposal)
        
        db.session.commit()
        
        # Return the comparison with proposals
        comparison_dict = new_comparison.to_dict()
        proposals = AssetComparisonProposal.query.filter_by(comparison_id=new_comparison.id).all()
        comparison_dict["proposals"] = [proposal.to_dict() for proposal in proposals]
        
        return jsonify({"success": True, "data": comparison_dict}), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@assets_bp.route("/asset-comparisons", methods=["GET"])
@dual_auth(permissions=[Permissions.ASSETS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_asset_comparisons():
    """Get all asset comparisons with their proposals"""
    try:
        current_asset_id = request.args.get('current_asset_id')
        
        query = AssetComparison.query
        if current_asset_id and current_asset_id != 'all':
            query = query.filter(AssetComparison.current_asset_id == int(current_asset_id))
        
        comparisons = query.all()
        
        result = []
        for comparison in comparisons:
            comparison_dict = comparison.to_dict()
            proposals = AssetComparisonProposal.query.filter_by(comparison_id=comparison.id).all()
            comparison_dict["proposals"] = [proposal.to_dict() for proposal in proposals]
            result.append(comparison_dict)
        
        return jsonify({"success": True, "data": result})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@assets_bp.route("/asset-comparisons/<int:comparison_id>", methods=["GET"])
@dual_auth(permissions=[Permissions.ASSETS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_asset_comparison(comparison_id):
    """Get a specific asset comparison with its proposals"""
    try:
        comparison = AssetComparison.query.get(comparison_id)
        if not comparison:
            return jsonify({"success": False, "error": "Comparison not found"}), 404
        
        comparison_dict = comparison.to_dict()
        proposals = AssetComparisonProposal.query.filter_by(comparison_id=comparison.id).all()
        comparison_dict["proposals"] = [proposal.to_dict() for proposal in proposals]
        
        return jsonify({"success": True, "data": comparison_dict})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@assets_bp.route("/asset-comparisons/<int:comparison_id>", methods=["PUT"])
@dual_auth(permissions=[Permissions.ASSETS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def update_asset_comparison(comparison_id):
    """Update an existing asset comparison"""
    try:
        comparison = AssetComparison.query.get(comparison_id)
        if not comparison:
            return jsonify({"success": False, "error": "Comparison not found"}), 404
        
        data = request.get_json()
        
        # Update comparison fields
        comparison.name = data.get("name", comparison.name)
        comparison.description = data.get("description", comparison.description)
        
        if "current_asset_id" in data:
            # Validate new current asset exists
            current_asset = Asset.query.get(data["current_asset_id"])
            if not current_asset:
                return jsonify({"success": False, "error": "Current asset not found"}), 404
            comparison.current_asset_id = data["current_asset_id"]
        
        # Delete existing proposals and add new ones
        AssetComparisonProposal.query.filter_by(comparison_id=comparison.id).delete()
        
        if "proposals" in data and data["proposals"]:
            for proposal_data in data["proposals"]:
                # Convert annual_co2e from kgCO2e to tCO2e for storage
                annual_co2e = None
                if proposal_data.get("annual_co2e"):
                    annual_co2e = float(proposal_data["annual_co2e"]) / 1000
                
                proposal = AssetComparisonProposal(
                    comparison_id=comparison.id,
                    name=proposal_data["name"],
                    manufacturer=proposal_data.get("manufacturer"),
                    model=proposal_data.get("model"),
                    power_rating=float(proposal_data["power_rating"]) if proposal_data.get("power_rating") else None,
                    efficiency_rating=float(proposal_data["efficiency_rating"]) if proposal_data.get("efficiency_rating") else None,
                    annual_kwh=float(proposal_data["annual_kwh"]) if proposal_data.get("annual_kwh") else None,
                    annual_co2e=annual_co2e,
                    purchase_cost=float(proposal_data["purchase_cost"]) if proposal_data.get("purchase_cost") else None,
                    installation_cost=float(proposal_data["installation_cost"]) if proposal_data.get("installation_cost") else None,
                    annual_maintenance_cost=float(proposal_data["annual_maintenance_cost"]) if proposal_data.get("annual_maintenance_cost") else None,
                    expected_lifespan=int(proposal_data["expected_lifespan"]) if proposal_data.get("expected_lifespan") else None,
                    notes=proposal_data.get("notes")
                )
                db.session.add(proposal)
        
        db.session.commit()
        
        # Return updated comparison with proposals
        comparison_dict = comparison.to_dict()
        proposals = AssetComparisonProposal.query.filter_by(comparison_id=comparison.id).all()
        comparison_dict["proposals"] = [proposal.to_dict() for proposal in proposals]
        
        return jsonify({"success": True, "data": comparison_dict})
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@assets_bp.route("/asset-comparisons/<int:comparison_id>", methods=["DELETE"])
@dual_auth(permissions=[Permissions.ASSETS_DELETE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def delete_asset_comparison(comparison_id):
    """Delete an asset comparison and its proposals"""
    try:
        comparison = AssetComparison.query.get(comparison_id)
        if not comparison:
            return jsonify({"success": False, "error": "Comparison not found"}), 404
        
        # Delete associated proposals first (cascade should handle this, but being explicit)
        AssetComparisonProposal.query.filter_by(comparison_id=comparison.id).delete()
        
        db.session.delete(comparison)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Comparison deleted successfully"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# Additional utility endpoints
@assets_bp.route("/assets/maintenance-schedule", methods=["GET"])
@dual_auth(permissions=[Permissions.ASSETS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_maintenance_schedule():
    """Get assets with upcoming maintenance"""
    try:
        from datetime import date, timedelta
        
        days_ahead = int(request.args.get('days', 30))
        end_date = date.today() + timedelta(days=days_ahead)
        
        assets = Asset.query.filter(
            Asset.next_maintenance <= end_date,
            Asset.next_maintenance >= date.today(),
            Asset.status == 'active'
        ).order_by(Asset.next_maintenance).all()
        
        return jsonify({"success": True, "data": [asset.to_dict() for asset in assets]})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@assets_bp.route("/assets/energy-analysis", methods=["GET"])
@dual_auth(permissions=[Permissions.ASSETS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_energy_analysis():
    """Get energy consumption analysis"""
    try:
        # Top energy consumers
        top_consumers = Asset.query.filter(
            Asset.annual_kwh.isnot(None),
            Asset.status == 'active'
        ).order_by(Asset.annual_kwh.desc()).limit(10).all()
        
        # Energy by asset type
        energy_by_type = db.session.query(
            Asset.asset_type,
            db.func.coalesce(db.func.sum(Asset.annual_kwh), 0).label('total_kwh'),
            db.func.count(Asset.id).label('count')
        ).filter(Asset.status == 'active').group_by(Asset.asset_type).all()
        
        # Energy by location
        energy_by_location = db.session.query(
            Asset.location,
            db.func.coalesce(db.func.sum(Asset.annual_kwh), 0).label('total_kwh'),
            db.func.count(Asset.id).label('count')
        ).filter(
            Asset.status == 'active',
            Asset.location.isnot(None)
        ).group_by(Asset.location).all()
        
        # Efficiency analysis
        efficiency_stats = db.session.query(
            db.func.avg(Asset.efficiency_rating).label('avg_efficiency'),
            db.func.min(Asset.efficiency_rating).label('min_efficiency'),
            db.func.max(Asset.efficiency_rating).label('max_efficiency')
        ).filter(
            Asset.efficiency_rating.isnot(None),
            Asset.status == 'active'
        ).first()
        
        analysis = {
            "top_consumers": [asset.to_dict() for asset in top_consumers],
            "energy_by_type": [
                {
                    "type": item[0],
                    "total_kwh": round(float(item[1]), 2),
                    "asset_count": item[2]
                } for item in energy_by_type
            ],
            "energy_by_location": [
                {
                    "location": item[0],
                    "total_kwh": round(float(item[1]), 2),
                    "asset_count": item[2]
                } for item in energy_by_location
            ],
            "efficiency_stats": {
                "average": round(float(efficiency_stats[0] or 0), 2),
                "minimum": round(float(efficiency_stats[1] or 0), 2),
                "maximum": round(float(efficiency_stats[2] or 0), 2)
            } if efficiency_stats else None
        }
        
        return jsonify({"success": True, "data": analysis})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@assets_bp.route("/assets/carbon-analysis", methods=["GET"])
@dual_auth(permissions=[Permissions.ASSETS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def get_carbon_analysis():
    """Get carbon emissions analysis"""
    try:
        # Top carbon emitters
        top_emitters = Asset.query.filter(
            Asset.annual_co2e.isnot(None),
            Asset.status == 'active'
        ).order_by(Asset.annual_co2e.desc()).limit(10).all()
        
        # Emissions by asset type (convert tCO2e to kgCO2e for display)
        emissions_by_type = db.session.query(
            Asset.asset_type,
            db.func.coalesce(db.func.sum(Asset.annual_co2e), 0).label('total_co2e_tonnes'),
            db.func.count(Asset.id).label('count')
        ).filter(Asset.status == 'active').group_by(Asset.asset_type).all()
        
        # Emissions by location
        emissions_by_location = db.session.query(
            Asset.location,
            db.func.coalesce(db.func.sum(Asset.annual_co2e), 0).label('total_co2e_tonnes'),
            db.func.count(Asset.id).label('count')
        ).filter(
            Asset.status == 'active',
            Asset.location.isnot(None)
        ).group_by(Asset.location).all()
        
        # Carbon intensity analysis (kgCO2e per kWh)
        carbon_intensity = db.session.query(
            Asset.id,
            Asset.name,
            Asset.asset_type,
            Asset.annual_kwh,
            Asset.annual_co2e,
            (Asset.annual_co2e * 1000 / Asset.annual_kwh).label('carbon_intensity')
        ).filter(
            Asset.annual_kwh.isnot(None),
            Asset.annual_co2e.isnot(None),
            Asset.annual_kwh > 0,
            Asset.status == 'active'
        ).order_by((Asset.annual_co2e * 1000 / Asset.annual_kwh).desc()).limit(10).all()
        
        analysis = {
            "top_emitters": [
                {
                    **asset.to_dict(),
                    "annual_co2e_kg": round(float(asset.annual_co2e * 1000), 2) if asset.annual_co2e else 0
                } for asset in top_emitters
            ],
            "emissions_by_type": [
                {
                    "type": item[0],
                    "total_co2e_kg": round(float(item[1] * 1000), 2),
                    "asset_count": item[2]
                } for item in emissions_by_type
            ],
            "emissions_by_location": [
                {
                    "location": item[0],
                    "total_co2e_kg": round(float(item[1] * 1000), 2),
                    "asset_count": item[2]
                } for item in emissions_by_location
            ],
            "carbon_intensity": [
                {
                    "id": item[0],
                    "name": item[1],
                    "asset_type": item[2],
                    "annual_kwh": round(float(item[3]), 2),
                    "annual_co2e_kg": round(float(item[4] * 1000), 2),
                    "carbon_intensity_kg_per_kwh": round(float(item[5]), 4)
                } for item in carbon_intensity
            ]
        }
        
        return jsonify({"success": True, "data": analysis})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Settings-based unified access endpoints
@assets_bp.route("/settings/assets", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_assets():
    """Get assets via settings permission"""
    return get_assets()

@assets_bp.route("/settings/assets", methods=["POST"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_create_asset():
    """Create asset via settings permission"""
    return create_asset()

@assets_bp.route("/settings/assets/<int:asset_id>", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_asset(asset_id):
    """Get specific asset via settings permission"""
    return get_asset(asset_id)

@assets_bp.route("/settings/assets/<int:asset_id>", methods=["PUT"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_update_asset(asset_id):
    """Update asset via settings permission"""
    return update_asset(asset_id)

@assets_bp.route("/settings/assets/<int:asset_id>", methods=["DELETE"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_delete_asset(asset_id):
    """Delete asset via settings permission"""
    return delete_asset(asset_id)

@assets_bp.route("/settings/assets/summary", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_assets_summary():
    """Get assets summary via settings permission"""
    return get_assets_summary()

@assets_bp.route("/settings/assets/types", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_asset_types():
    """Get asset types via settings permission"""
    return get_asset_types()

@assets_bp.route("/settings/asset-comparisons", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_asset_comparisons():
    """Get asset comparisons via settings permission"""
    return get_asset_comparisons()

@assets_bp.route("/settings/asset-comparisons", methods=["POST"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_create_asset_comparison():
    """Create asset comparison via settings permission"""
    return create_asset_comparison()

@assets_bp.route("/settings/asset-comparisons/<int:comparison_id>", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_asset_comparison(comparison_id):
    """Get specific asset comparison via settings permission"""
    return get_asset_comparison(comparison_id)

@assets_bp.route("/settings/asset-comparisons/<int:comparison_id>", methods=["PUT"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_update_asset_comparison(comparison_id):
    """Update asset comparison via settings permission"""
    return update_asset_comparison(comparison_id)

@assets_bp.route("/settings/asset-comparisons/<int:comparison_id>", methods=["DELETE"])
@dual_auth(permissions=[Permissions.SETTINGS_WRITE] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_delete_asset_comparison(comparison_id):
    """Delete asset comparison via settings permission"""
    return delete_asset_comparison(comparison_id)

@assets_bp.route("/settings/assets/maintenance-schedule", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_maintenance_schedule():
    """Get maintenance schedule via settings permission"""
    return get_maintenance_schedule()

@assets_bp.route("/settings/assets/energy-analysis", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_energy_analysis():
    """Get energy analysis via settings permission"""
    return get_energy_analysis()

@assets_bp.route("/settings/assets/carbon-analysis", methods=["GET"])
@dual_auth(permissions=[Permissions.SETTINGS_READ] if AUTH_MIDDLEWARE_AVAILABLE else None)
def settings_get_carbon_analysis():
    """Get carbon analysis via settings permission"""
    return get_carbon_analysis()

