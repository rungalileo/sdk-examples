from langchain_core.tools import tool
import datetime

@tool
def check_supplier_compliance(supplier_id: str) -> str:
    """
    Check a supplier's compliance status against key regulations and standards.
    
    Args:
        supplier_id: The unique identifier for the supplier to check
        
    Returns:
        A summary of the supplier's compliance status including:
        - ESG compliance score
        - Sanctions list status
        - Required certifications status
        - Recent compliance incidents
    """
    # In a real implementation, this would query a database or API
    # This is a mock implementation for demonstration
    
    # Mock data dictionary - would be a database in production
    compliance_data = {
        "SUP001": {
            "name": "Acme Manufacturing",
            "esg_score": 82,
            "sanctions_status": "Clear",
            "certifications": {
                "ISO9001": "Valid until 2025-12-31",
                "ISO14001": "Valid until 2024-09-15",
                "REACH": "Non-compliant"
            },
            "incidents": ["Minor environmental violation (2023-11-04)"]
        },
        "SUP002": {
            "name": "Global Parts Inc.",
            "esg_score": 64,
            "sanctions_status": "Clear",
            "certifications": {
                "ISO9001": "Valid until 2026-03-22",
                "ISO14001": "Missing",
                "REACH": "Valid until 2025-01-10"
            },
            "incidents": []
        }
    }
    
    if supplier_id not in compliance_data:
        return f"Supplier {supplier_id} not found in compliance database."
    
    supplier = compliance_data[supplier_id]
    report = f"Compliance Report for {supplier['name']} (ID: {supplier_id}):\n\n"
    
    # ESG Score with risk level
    esg_score = supplier['esg_score']
    if esg_score >= 80:
        esg_risk = "Low Risk"
    elif esg_score >= 60:
        esg_risk = "Medium Risk"
    else:
        esg_risk = "High Risk"
    report += f"ESG Compliance Score: {esg_score}/100 ({esg_risk})\n"
    
    # Sanctions status
    report += f"Sanctions Status: {supplier['sanctions_status']}\n\n"
    
    # Certifications
    report += "Required Certifications:\n"
    for cert, status in supplier['certifications'].items():
        report += f"- {cert}: {status}\n"
    
    # Compliance incidents
    report += "\nRecent Compliance Incidents:\n"
    if supplier['incidents']:
        for incident in supplier['incidents']:
            report += f"- {incident}\n"
    else:
        report += "No incidents reported in the last 12 months.\n"
    
    return report

@tool
def assess_disruption_risk(region: str = None, material: str = None, supplier_id: str = None) -> str:
    """
    Assess supply chain disruption risk for a specific region, material, or supplier.
    
    Args:
        region: Geographic region to assess (e.g., "Southeast Asia", "Eastern Europe")
        material: Specific material or component to assess (e.g., "semiconductors", "rare earth metals")
        supplier_id: Specific supplier ID to assess
        
    Note: At least one parameter must be provided.
    
    Returns:
        A risk assessment including:
        - Overall risk score (1-10)
        - Key risk factors
        - Recommended mitigation actions
    """
    # This would normally use real-time data from various sources
    # Mock implementation for demonstration
    
    if not any([region, material, supplier_id]):
        return "Error: At least one parameter (region, material, or supplier_id) must be provided."
    
    risk_data = {
        "regions": {
            "southeast asia": {"score": 6.2, "factors": ["Flooding risk", "Political instability"]},
            "eastern europe": {"score": 7.8, "factors": ["Ongoing conflict", "Energy supply issues"]},
            "north america": {"score": 3.5, "factors": ["Labor shortages", "Extreme weather events"]}
        },
        "materials": {
            "semiconductors": {"score": 8.1, "factors": ["Concentrated production", "High demand volatility"]},
            "rare earth metals": {"score": 7.5, "factors": ["Limited sources", "Geopolitical tensions"]},
            "aluminum": {"score": 4.2, "factors": ["Price volatility", "Energy costs"]}
        },
        "suppliers": {
            "SUP001": {"score": 3.8, "factors": ["Strong financial position", "Multiple facilities"]},
            "SUP002": {"score": 6.5, "factors": ["Single-facility production", "Financial instability"]}
        }
    }
    
    # Calculate combined risk score and gather factors
    risk_score = 0
    risk_factors = []
    count = 0
    
    if region:
        region_lower = region.lower()
        if region_lower in risk_data["regions"]:
            risk_score += risk_data["regions"][region_lower]["score"]
            risk_factors.extend(risk_data["regions"][region_lower]["factors"])
            count += 1
        else:
            return f"Error: Region '{region}' not found in risk database."
    
    if material:
        material_lower = material.lower()
        if material_lower in risk_data["materials"]:
            risk_score += risk_data["materials"][material_lower]["score"]
            risk_factors.extend(risk_data["materials"][material_lower]["factors"])
            count += 1
        else:
            return f"Error: Material '{material}' not found in risk database."
    
    if supplier_id:
        if supplier_id in risk_data["suppliers"]:
            risk_score += risk_data["suppliers"][supplier_id]["score"]
            risk_factors.extend(risk_data["suppliers"][supplier_id]["factors"])
            count += 1
        else:
            return f"Error: Supplier '{supplier_id}' not found in risk database."
    
    # Calculate average risk score
    if count > 0:
        avg_risk_score = round(risk_score / count, 1)
    else:
        avg_risk_score = 0
    
    # Generate mitigation recommendations based on risk score
    if avg_risk_score >= 7:
        mitigation = [
            "Immediately develop alternative sourcing options",
            "Increase safety stock levels",
            "Implement real-time monitoring systems",
            "Develop comprehensive contingency plans"
        ]
    elif avg_risk_score >= 5:
        mitigation = [
            "Identify backup suppliers",
            "Review and update risk management protocols",
            "Consider selective inventory increases for critical items"
        ]
    else:
        mitigation = [
            "Maintain regular risk monitoring",
            "Annual review of contingency plans",
            "Standard supplier diversification strategies"
        ]
    
    # Build report
    report = "Supply Chain Disruption Risk Assessment\n"
    report += f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    if region:
        report += f"Region: {region}\n"
    if material:
        report += f"Material: {material}\n"
    if supplier_id:
        report += f"Supplier ID: {supplier_id}\n"
    
    report += f"\nOverall Risk Score: {avg_risk_score}/10 "
    
    # Risk level description
    if avg_risk_score >= 7:
        report += "(HIGH RISK)\n"
    elif avg_risk_score >= 5:
        report += "(MEDIUM RISK)\n"
    else:
        report += "(LOW RISK)\n"
    
    # Risk factors
    report += "\nKey Risk Factors:\n"
    unique_factors = list(set(risk_factors))  # Remove duplicates
    for factor in unique_factors:
        report += f"- {factor}\n"
    
    # Mitigation recommendations
    report += "\nRecommended Mitigation Actions:\n"
    for action in mitigation:
        report += f"- {action}\n"
    
    return report
