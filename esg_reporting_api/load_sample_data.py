"""
Sample data loader for ESG Reporting API
This script populates the database with sample emission factors, measurements, suppliers, ESG targets, assets, and asset comparisons.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import date, datetime, timedelta
from src.models.esg_models import db, EmissionFactor, Measurement, Supplier, ESGTarget, Asset, AssetComparison, AssetComparisonProposal
from src.main import app

def load_sample_emission_factors():
    """Load sample emission factors"""
    sample_factors = [
        # Scope 1 - Direct emissions
        {
            'name': 'Natural Gas Combustion',
            'scope': 1,
            'category': 'fuel',
            'sub_category': 'natural_gas',
            'factor_value': 0.0531,
            'unit': 'kg CO2e/kWh',
            'source': 'EPA',
            'effective_date': date(2024, 1, 1),
            'description': 'Emission factor for natural gas combustion in stationary sources'
        },
        {
            'name': 'Diesel Fuel Combustion',
            'scope': 1,
            'category': 'fuel',
            'sub_category': 'diesel',
            'factor_value': 2.68,
            'unit': 'kg CO2e/liter',
            'source': 'EPA',
            'effective_date': date(2024, 1, 1),
            'description': 'Emission factor for diesel fuel combustion in mobile sources'
        },
        {
            'name': 'Gasoline Combustion',
            'scope': 1,
            'category': 'fuel',
            'sub_category': 'gasoline',
            'factor_value': 2.31,
            'unit': 'kg CO2e/liter',
            'source': 'EPA',
            'effective_date': date(2024, 1, 1),
            'description': 'Emission factor for gasoline combustion in mobile sources'
        },
        
        # Scope 2 - Indirect emissions from purchased energy
        {
            'name': 'Grid Electricity - US Average',
            'scope': 2,
            'category': 'electricity',
            'sub_category': 'grid_average',
            'factor_value': 0.386,
            'unit': 'kg CO2e/kWh',
            'source': 'EPA eGRID',
            'effective_date': date(2024, 1, 1),
            'description': 'US national average grid electricity emission factor'
        },
        {
            'name': 'Steam Purchase',
            'scope': 2,
            'category': 'steam',
            'sub_category': 'purchased_steam',
            'factor_value': 0.2,
            'unit': 'kg CO2e/kWh',
            'source': 'EPA',
            'effective_date': date(2024, 1, 1),
            'description': 'Emission factor for purchased steam'
        },
        
        # Scope 3 - Other indirect emissions
        {
            'name': 'Air Travel - Domestic',
            'scope': 3,
            'category': 'transportation',
            'sub_category': 'air_travel_domestic',
            'factor_value': 0.18,
            'unit': 'kg CO2e/km',
            'source': 'DEFRA',
            'effective_date': date(2024, 1, 1),
            'description': 'Emission factor for domestic air travel per passenger-km'
        },
        {
            'name': 'Air Travel - International',
            'scope': 3,
            'category': 'transportation',
            'sub_category': 'air_travel_international',
            'factor_value': 0.15,
            'unit': 'kg CO2e/km',
            'source': 'DEFRA',
            'effective_date': date(2024, 1, 1),
            'description': 'Emission factor for international air travel per passenger-km'
        },
        {
            'name': 'Employee Commuting - Car',
            'scope': 3,
            'category': 'transportation',
            'sub_category': 'employee_commuting',
            'factor_value': 0.17,
            'unit': 'kg CO2e/km',
            'source': 'DEFRA',
            'effective_date': date(2024, 1, 1),
            'description': 'Emission factor for employee commuting by car'
        },
        {
            'name': 'Waste to Landfill',
            'scope': 3,
            'category': 'waste',
            'sub_category': 'landfill',
            'factor_value': 0.5,
            'unit': 'kg CO2e/kg',
            'source': 'EPA',
            'effective_date': date(2024, 1, 1),
            'description': 'Emission factor for waste sent to landfill'
        }
    ]
    
    for factor_data in sample_factors:
        factor = EmissionFactor(**factor_data)
        db.session.add(factor)
    
    print(f"Added {len(sample_factors)} emission factors")

def load_sample_measurements():
    """Load sample measurements"""
    # Get some emission factors to use
    electricity_factor = EmissionFactor.query.filter_by(category='electricity').first()
    natural_gas_factor = EmissionFactor.query.filter_by(sub_category='natural_gas').first()
    air_travel_factor = EmissionFactor.query.filter_by(sub_category='air_travel_domestic').first()
    
    if not all([electricity_factor, natural_gas_factor, air_travel_factor]):
        print("Error: Required emission factors not found")
        return
    
    # Generate sample measurements for the last 12 months
    base_date = date.today() - timedelta(days=365)
    sample_measurements = []
    
    # Monthly electricity consumption
    for i in range(12):
        measurement_date = base_date + timedelta(days=i*30)
        amount = 15000 + (i * 500)  # Increasing consumption
        
        measurement = Measurement(
            date=measurement_date,
            location='Main Office',
            category='electricity',
            sub_category='grid_average',
            amount=amount,
            unit='kWh',
            emission_factor_id=electricity_factor.id,
            calculated_emissions=amount * electricity_factor.factor_value,
            notes=f'Monthly electricity consumption for {measurement_date.strftime("%B %Y")}'
        )
        sample_measurements.append(measurement)
    
    # Monthly natural gas consumption
    for i in range(12):
        measurement_date = base_date + timedelta(days=i*30)
        amount = 8000 + (i * 200)  # Increasing consumption
        
        measurement = Measurement(
            date=measurement_date,
            location='Main Office',
            category='fuel',
            sub_category='natural_gas',
            amount=amount,
            unit='kWh',
            emission_factor_id=natural_gas_factor.id,
            calculated_emissions=amount * natural_gas_factor.factor_value,
            notes=f'Monthly natural gas consumption for {measurement_date.strftime("%B %Y")}'
        )
        sample_measurements.append(measurement)
    
    # Quarterly business travel
    for i in range(4):
        measurement_date = base_date + timedelta(days=i*90)
        amount = 25000 + (i * 5000)  # Increasing travel
        
        measurement = Measurement(
            date=measurement_date,
            location='Various',
            category='transportation',
            sub_category='air_travel_domestic',
            amount=amount,
            unit='km',
            emission_factor_id=air_travel_factor.id,
            calculated_emissions=amount * air_travel_factor.factor_value,
            notes=f'Quarterly business travel for Q{i+1}'
        )
        sample_measurements.append(measurement)
    
    for measurement in sample_measurements:
        db.session.add(measurement)
    
    print(f"Added {len(sample_measurements)} measurements")

def load_sample_suppliers():
    """Load sample suppliers"""
    sample_suppliers = [
        {
            'company_name': 'Green Energy Solutions Inc.',
            'industry': 'Energy',
            'contact_person': 'John Smith',
            'email': 'john.smith@greenenergy.com',
            'phone': '+1-555-0123',
            'esg_rating': 'A',
            'data_completeness': 85.0,
            'status': 'complete',
            'priority_level': 'high',
            'scope3_categories': '["Purchased goods and services", "Capital goods"]',
            'notes': 'Key renewable energy supplier with excellent ESG performance'
        },
        {
            'company_name': 'Sustainable Logistics Corp.',
            'industry': 'Transportation',
            'contact_person': 'Sarah Johnson',
            'email': 'sarah.j@sustainablelogistics.com',
            'phone': '+1-555-0456',
            'esg_rating': 'B',
            'data_completeness': 60.0,
            'status': 'pending',
            'priority_level': 'medium',
            'scope3_categories': '["Upstream transportation and distribution"]',
            'notes': 'Working on improving data collection processes'
        },
        {
            'company_name': 'EcoMaterials Ltd.',
            'industry': 'Manufacturing',
            'contact_person': 'Michael Chen',
            'email': 'm.chen@ecomaterials.com',
            'phone': '+1-555-0789',
            'esg_rating': 'C',
            'data_completeness': 30.0,
            'status': 'overdue',
            'priority_level': 'high',
            'scope3_categories': '["Purchased goods and services"]',
            'notes': 'Need to follow up on data submission'
        }
    ]
    
    for supplier_data in sample_suppliers:
        supplier = Supplier(**supplier_data)
        db.session.add(supplier)
    
    print(f"Added {len(sample_suppliers)} suppliers")

def load_sample_targets():
    """Load sample ESG targets"""
    sample_targets = [
        {
            'name': 'Reduce Scope 1 Emissions by 30%',
            'description': 'Reduce direct emissions from fuel combustion by 30% by 2030',
            'target_type': 'emissions_reduction',
            'scope': 1,
            'baseline_value': 1000.0,
            'baseline_year': 2020,
            'target_value': 700.0,
            'target_year': 2030,
            'unit': 'tCO2e',
            'current_value': 850.0,
            'progress_percentage': 50.0,
            'status': 'active'
        },
        {
            'name': 'Achieve Carbon Neutrality',
            'description': 'Achieve net-zero carbon emissions across all scopes by 2050',
            'target_type': 'emissions_reduction',
            'scope': None,
            'baseline_value': 5000.0,
            'baseline_year': 2020,
            'target_value': 0.0,
            'target_year': 2050,
            'unit': 'tCO2e',
            'current_value': 4200.0,
            'progress_percentage': 16.0,
            'status': 'active'
        },
        {
            'name': 'Increase Renewable Energy to 80%',
            'description': 'Source 80% of electricity from renewable sources by 2028',
            'target_type': 'energy_efficiency',
            'scope': 2,
            'baseline_value': 20.0,
            'baseline_year': 2022,
            'target_value': 80.0,
            'target_year': 2028,
            'unit': '%',
            'current_value': 35.0,
            'progress_percentage': 25.0,
            'status': 'active'
        }
    ]
    
    for target_data in sample_targets:
        target = ESGTarget(**target_data)
        db.session.add(target)
    
    print(f"Added {len(sample_targets)} ESG targets")

def load_sample_assets():
    """Load sample assets"""
    sample_assets = [
        {
            'name': 'Main Office Chiller 1',
            'asset_type': 'chiller',
            'model': 'Centrifugal 500',
            'manufacturer': 'Carrier',
            'serial_number': 'CHL-MO-001',
            'location': 'Main Office - Basement',
            'installation_date': date(2018, 5, 10),
            'capacity': 500.0,
            'capacity_unit': 'TR',
            'power_rating': 350.0, # kW
            'efficiency_rating': 3.5, # COP
            'annual_kwh': 1500000.0, # kWh
            'annual_co2e': 579.0, # tCO2e (using 0.386 kg CO2e/kWh)
            'maintenance_schedule': 'Quarterly',
            'last_maintenance': date(2024, 4, 1),
            'next_maintenance': date(2024, 7, 1),
            'status': 'active',
            'notes': 'Primary chiller for main office building'
        },
        {
            'name': 'Server Room AC Unit',
            'asset_type': 'aircon',
            'model': 'PrecisionCool 100',
            'manufacturer': 'Liebert',
            'serial_number': 'AC-SR-001',
            'location': 'Main Office - Server Room',
            'installation_date': date(2022, 1, 15),
            'capacity': 10.0,
            'capacity_unit': 'TR',
            'power_rating': 7.5, # kW
            'efficiency_rating': 4.0, # EER
            'annual_kwh': 65700.0, # kWh (7.5kW * 24h * 365d)
            'annual_co2e': 25.36, # tCO2e
            'maintenance_schedule': 'Monthly',
            'last_maintenance': date(2024, 5, 1),
            'next_maintenance': date(2024, 6, 1),
            'status': 'active',
            'notes': 'Dedicated cooling for critical server infrastructure'
        },
        {
            'name': 'Warehouse Pump 1',
            'asset_type': 'pump',
            'model': 'HydroFlow 50',
            'manufacturer': 'Grundfos',
            'serial_number': 'PMP-WH-001',
            'location': 'Warehouse - Water Treatment',
            'installation_date': date(2019, 9, 1),
            'capacity': 50.0,
            'capacity_unit': 'HP',
            'power_rating': 37.3, # kW (50HP * 0.746)
            'efficiency_rating': 0.85,
            'annual_kwh': 326748.0, # kWh (37.3kW * 24h * 365d * 0.85 utilization)
            'annual_co2e': 126.2, # tCO2e
            'maintenance_schedule': 'Annually',
            'last_maintenance': date(2024, 1, 10),
            'next_maintenance': date(2025, 1, 10),
            'status': 'active',
            'notes': 'Used for water circulation in warehouse'
        }
    ]

    for asset_data in sample_assets:
        asset = Asset(**asset_data)
        db.session.add(asset)

    print(f"Added {len(sample_assets)} assets")

def load_sample_asset_comparisons():
    """Load sample asset comparisons"""
    current_chiller = Asset.query.filter_by(name='Main Office Chiller 1').first()

    if not current_chiller:
        print("Error: 'Main Office Chiller 1' asset not found for comparison.")
        return

    # Comparison 1: Chiller Upgrade
    comparison1 = AssetComparison(
        name='Chiller Upgrade Project',
        description='Comparison of existing chiller with high-efficiency alternatives',
        current_asset_id=current_chiller.id,
        created_by='admin'
    )
    db.session.add(comparison1)
    db.session.flush() # Flush to get comparison1.id

    # Proposals for Chiller Upgrade
    proposals1 = [
        {
            'comparison_id': comparison1.id,
            'name': 'High-Efficiency Centrifugal Chiller',
            'manufacturer': 'Trane',
            'model': 'CenTraVac 450',
            'power_rating': 300.0, # kW
            'efficiency_rating': 4.2, # COP
            'annual_kwh': 1200000.0, # kWh
            'annual_co2e': 463.2, # tCO2e
            'purchase_cost': 250000.0,
            'installation_cost': 50000.0,
            'annual_maintenance_cost': 10000.0,
            'expected_lifespan': 20,
            'notes': 'New generation chiller with improved COP'
        },
        {
            'comparison_id': comparison1.id,
            'name': 'Magnetic Bearing Chiller',
            'manufacturer': 'Danfoss',
            'model': 'Turbocor TT400',
            'power_rating': 280.0, # kW
            'efficiency_rating': 4.8, # COP
            'annual_kwh': 1100000.0, # kWh
            'annual_co2e': 424.6, # tCO2e
            'purchase_cost': 350000.0,
            'installation_cost': 70000.0,
            'annual_maintenance_cost': 8000.0,
            'expected_lifespan': 25,
            'notes': 'Oil-free design, very high efficiency at part load'
        }
    ]

    for proposal_data in proposals1:
        proposal = AssetComparisonProposal(**proposal_data)
        db.session.add(proposal)

    print(f"Added {len(proposals1)} proposals for '{comparison1.name}'")

    db.session.commit()

def main():
    """Load all sample data"""
    with app.app_context():
        print("Loading sample data for ESG Reporting API...")
        
        # Clear existing data (optional)
        # db.drop_all()
        # db.create_all()
        
        load_sample_emission_factors()
        db.session.commit()
        
        load_sample_measurements()
        db.session.commit()
        
        load_sample_suppliers()
        db.session.commit()
        
        load_sample_targets()
        db.session.commit()

        load_sample_assets()
        db.session.commit()

        load_sample_asset_comparisons()
        db.session.commit()
        
        print("Sample data loaded successfully!")

if __name__ == '__main__':
    main()



