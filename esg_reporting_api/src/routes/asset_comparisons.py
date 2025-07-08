from flask import Blueprint, request, jsonify
from src.models.esg_models import db, AssetComparison, AssetComparisonProposal, Asset
from datetime import datetime

asset_comparisons_bp = Blueprint("asset_comparisons", __name__)

@asset_comparisons_bp.route("/asset-comparisons", methods=["POST"])
def create_asset_comparison():
    """Create a new asset comparison"""
    data = request.get_json()
    try:
        new_comparison = AssetComparison(
            name=data["name"],
            description=data.get("description"),
            current_asset_id=data.get("current_asset_id")
        )
        db.session.add(new_comparison)
        db.session.flush()  # Get the ID

        # Add proposals
        for proposal_data in data.get("proposals", []):
            proposal = AssetComparisonProposal(
                comparison_id=new_comparison.id,
                name=proposal_data["name"],
                manufacturer=proposal_data.get("manufacturer"),
                model=proposal_data.get("model"),
                power_rating=proposal_data.get("power_rating"),
                efficiency_rating=proposal_data.get("efficiency_rating"),
                annual_kwh=proposal_data.get("annual_kwh"),
                annual_co2e=proposal_data.get("annual_co2e"),
                purchase_cost=proposal_data.get("purchase_cost"),
                installation_cost=proposal_data.get("installation_cost"),
                annual_maintenance_cost=proposal_data.get("annual_maintenance_cost"),
                expected_lifespan=proposal_data.get("expected_lifespan"),
                notes=proposal_data.get("notes")
            )
            db.session.add(proposal)

        db.session.commit()
        return jsonify({"success": True, "data": new_comparison.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@asset_comparisons_bp.route("/asset-comparisons", methods=["GET"])
def get_asset_comparisons():
    """Get all asset comparisons"""
    try:
        comparisons = AssetComparison.query.all()
        return jsonify({"success": True, "data": [comp.to_dict() for comp in comparisons]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@asset_comparisons_bp.route("/asset-comparisons/<int:comparison_id>", methods=["GET"])
def get_asset_comparison(comparison_id):
    """Get a specific asset comparison"""
    try:
        comparison = AssetComparison.query.get(comparison_id)
        if not comparison:
            return jsonify({"success": False, "error": "Comparison not found"}), 404
        return jsonify({"success": True, "data": comparison.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@asset_comparisons_bp.route("/asset-comparisons/<int:comparison_id>", methods=["PUT"])
def update_asset_comparison(comparison_id):
    """Update an existing asset comparison"""
    data = request.get_json()
    try:
        comparison = AssetComparison.query.get(comparison_id)
        if not comparison:
            return jsonify({"success": False, "error": "Comparison not found"}), 404
        
        # Update basic fields
        comparison.name = data.get("name", comparison.name)
        comparison.description = data.get("description", comparison.description)
        comparison.current_asset_id = data.get("current_asset_id", comparison.current_asset_id)
        
        # Update proposals if provided
        if "proposals" in data:
            # Delete existing proposals
            AssetComparisonProposal.query.filter_by(comparison_id=comparison_id).delete()
            
            # Add new proposals
            for proposal_data in data["proposals"]:
                proposal = AssetComparisonProposal(
                    comparison_id=comparison_id,
                    name=proposal_data["name"],
                    manufacturer=proposal_data.get("manufacturer"),
                    model=proposal_data.get("model"),
                    power_rating=proposal_data.get("power_rating"),
                    efficiency_rating=proposal_data.get("efficiency_rating"),
                    annual_kwh=proposal_data.get("annual_kwh"),
                    annual_co2e=proposal_data.get("annual_co2e"),
                    purchase_cost=proposal_data.get("purchase_cost"),
                    installation_cost=proposal_data.get("installation_cost"),
                    annual_maintenance_cost=proposal_data.get("annual_maintenance_cost"),
                    expected_lifespan=proposal_data.get("expected_lifespan"),
                    notes=proposal_data.get("notes")
                )
                db.session.add(proposal)
        
        db.session.commit()
        return jsonify({"success": True, "data": comparison.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@asset_comparisons_bp.route("/asset-comparisons/<int:comparison_id>", methods=["DELETE"])
def delete_asset_comparison(comparison_id):
    """Delete an asset comparison"""
    try:
        comparison = AssetComparison.query.get(comparison_id)
        if not comparison:
            return jsonify({"success": False, "error": "Comparison not found"}), 404
        
        # Delete proposals first (cascade should handle this, but being explicit)
        AssetComparisonProposal.query.filter_by(comparison_id=comparison_id).delete()
        
        db.session.delete(comparison)
        db.session.commit()
        return jsonify({"success": True, "message": "Comparison deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@asset_comparisons_bp.route("/asset-comparisons/<int:comparison_id>/analysis", methods=["GET"])
def get_comparison_analysis(comparison_id):
    """Get analysis data for an asset comparison"""
    try:
        comparison = AssetComparison.query.get(comparison_id)
        if not comparison:
            return jsonify({"success": False, "error": "Comparison not found"}), 404
        
        current_asset = comparison.current_asset
        proposals = comparison.proposals
        
        analysis = {
            "comparison_id": comparison_id,
            "comparison_name": comparison.name,
            "current_asset": {
                "name": current_asset.name if current_asset else "N/A",
                "annual_kwh": current_asset.annual_kwh if current_asset else 0,
                "annual_co2e": current_asset.annual_co2e if current_asset else 0,
                "power_rating": current_asset.power_rating if current_asset else 0
            },
            "proposals": [],
            "savings_analysis": []
        }
        
        current_kwh = current_asset.annual_kwh if current_asset and current_asset.annual_kwh else 0
        current_co2e = current_asset.annual_co2e if current_asset and current_asset.annual_co2e else 0
        
        for proposal in proposals:
            proposal_data = {
                "name": proposal.name,
                "manufacturer": proposal.manufacturer,
                "model": proposal.model,
                "annual_kwh": proposal.annual_kwh or 0,
                "annual_co2e": proposal.annual_co2e or 0,
                "power_rating": proposal.power_rating or 0,
                "purchase_cost": proposal.purchase_cost or 0,
                "installation_cost": proposal.installation_cost or 0,
                "annual_maintenance_cost": proposal.annual_maintenance_cost or 0,
                "expected_lifespan": proposal.expected_lifespan or 0
            }
            analysis["proposals"].append(proposal_data)
            
            # Calculate savings
            kwh_savings = current_kwh - (proposal.annual_kwh or 0)
            co2e_savings = current_co2e - (proposal.annual_co2e or 0)
            
            # Estimate cost savings (assuming $0.12 per kWh)
            energy_cost_savings = kwh_savings * 0.12
            
            # Calculate total initial cost
            total_initial_cost = (proposal.purchase_cost or 0) + (proposal.installation_cost or 0)
            
            # Calculate payback period (years)
            annual_savings = energy_cost_savings - (proposal.annual_maintenance_cost or 0)
            payback_period = total_initial_cost / annual_savings if annual_savings > 0 else float('inf')
            
            savings_data = {
                "proposal_name": proposal.name,
                "kwh_savings_annual": round(kwh_savings, 2),
                "co2e_savings_annual": round(co2e_savings, 2),
                "energy_cost_savings_annual": round(energy_cost_savings, 2),
                "total_initial_cost": round(total_initial_cost, 2),
                "payback_period_years": round(payback_period, 2) if payback_period != float('inf') else None,
                "lifetime_savings": round(annual_savings * (proposal.expected_lifespan or 10), 2) if annual_savings > 0 else 0
            }
            analysis["savings_analysis"].append(savings_data)
        
        return jsonify({"success": True, "data": analysis})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@asset_comparisons_bp.route("/asset-comparisons/generate-sample", methods=["POST"])
def generate_sample_comparison():
    """Generate sample comparison data for demonstration"""
    try:
        # Create a sample comparison
        sample_comparison = AssetComparison(
            name="Chiller Replacement Analysis - Building A",
            description="Comparing current 20-year-old chiller with modern high-efficiency alternatives",
            current_asset_id=None  # Will be set if there's an existing asset
        )
        db.session.add(sample_comparison)
        db.session.flush()
        
        # Sample proposals with realistic data
        sample_proposals = [
            {
                "name": "High-Efficiency Centrifugal Chiller",
                "manufacturer": "Carrier",
                "model": "30XA-1002",
                "power_rating": 850.0,
                "efficiency_rating": 0.58,
                "annual_kwh": 425000.0,
                "annual_co2e": 191250.0,
                "purchase_cost": 180000.0,
                "installation_cost": 25000.0,
                "annual_maintenance_cost": 8500.0,
                "expected_lifespan": 20,
                "notes": "Variable speed drive, R-134a refrigerant, AHRI certified"
            },
            {
                "name": "Magnetic Bearing Chiller",
                "manufacturer": "Daikin",
                "model": "WME-C1000",
                "power_rating": 780.0,
                "efficiency_rating": 0.52,
                "annual_kwh": 390000.0,
                "annual_co2e": 175500.0,
                "purchase_cost": 220000.0,
                "installation_cost": 30000.0,
                "annual_maintenance_cost": 6000.0,
                "expected_lifespan": 25,
                "notes": "Oil-free magnetic bearings, reduced maintenance, R-1233zd refrigerant"
            },
            {
                "name": "Heat Recovery Chiller",
                "manufacturer": "Trane",
                "model": "RTWD-400",
                "power_rating": 820.0,
                "efficiency_rating": 0.55,
                "annual_kwh": 410000.0,
                "annual_co2e": 184500.0,
                "purchase_cost": 195000.0,
                "installation_cost": 35000.0,
                "annual_maintenance_cost": 7500.0,
                "expected_lifespan": 22,
                "notes": "Integrated heat recovery, dual compressor design, smart controls"
            }
        ]
        
        for proposal_data in sample_proposals:
            proposal = AssetComparisonProposal(
                comparison_id=sample_comparison.id,
                **proposal_data
            )
            db.session.add(proposal)
        
        db.session.commit()
        return jsonify({"success": True, "data": sample_comparison.to_dict(), "message": "Sample comparison created successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

