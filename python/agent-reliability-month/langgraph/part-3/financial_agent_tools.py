import datetime

from langchain_core.tools import tool


@tool
def calculate_tco(supplier_id: str, annual_volume: float, unit_price: float,
                  transportation_cost: float = 0, quality_cost: float = 0,
                  risk_cost: float = 0) -> str:
    """
    Calculate Total Cost of Ownership for a supplier.

    Args:
        supplier_id: Unique identifier for the supplier
        annual_volume: Expected annual purchase volume
        unit_price: Price per unit
        transportation_cost: Annual transportation costs
        quality_cost: Annual quality-related costs (defects, returns)
        risk_cost: Annual risk-related costs (disruptions, delays)

    Returns:
        Detailed TCO analysis including breakdown by cost category
    """
    base_cost = annual_volume * unit_price
    total_cost = base_cost + transportation_cost + quality_cost + risk_cost

    report = f"Total Cost of Ownership Analysis for Supplier {supplier_id}\n"
    report += f"Analysis Date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n"

    report += f"Cost Breakdown:\n"
    report += f"- Base Purchase Cost: ${base_cost:,.2f} ({base_cost / total_cost * 100:.1f}%)\n"
    report += f"- Transportation Cost: ${transportation_cost:,.2f} ({transportation_cost / total_cost * 100:.1f}%)\n"
    report += f"- Quality Cost: ${quality_cost:,.2f} ({quality_cost / total_cost * 100:.1f}%)\n"
    report += f"- Risk Cost: ${risk_cost:,.2f} ({risk_cost / total_cost * 100:.1f}%)\n"
    report += f"\nTotal Annual Cost: ${total_cost:,.2f}\n"
    report += f"Cost per Unit (including all factors): ${total_cost / annual_volume:.2f}\n"

    return report


@tool
def analyze_financial_risk(supplier_id: str) -> str:
    """
    Analyze the financial health and stability of a supplier.

    Args:
        supplier_id: Unique identifier for the supplier

    Returns:
        Financial risk assessment including credit rating, liquidity, and stability metrics
    """
    # Mock financial data - would connect to financial APIs in production
    financial_data = {
        "SUP001": {
            "name": "Acme Manufacturing",
            "credit_rating": "BBB+",
            "debt_to_equity": 0.45,
            "current_ratio": 2.1,
            "revenue_growth": 0.08,
            "profit_margin": 0.12,
            "days_sales_outstanding": 45
        },
        "SUP002": {
            "name": "Global Parts Inc.",
            "credit_rating": "BB-",
            "debt_to_equity": 0.78,
            "current_ratio": 1.3,
            "revenue_growth": -0.02,
            "profit_margin": 0.05,
            "days_sales_outstanding": 62
        }
    }

    if supplier_id not in financial_data:
        return f"Financial data for supplier {supplier_id} not available."

    supplier = financial_data[supplier_id]

    report = f"Financial Risk Analysis for {supplier['name']} (ID: {supplier_id})\n"
    report += f"Analysis Date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n"

    # Credit assessment
    credit_rating = supplier['credit_rating']
    if credit_rating.startswith('A'):
        credit_risk = "Low"
    elif credit_rating.startswith('BB'):
        credit_risk = "Medium"
    else:
        credit_risk = "High"

    report += f"Credit Rating: {credit_rating} ({credit_risk} Risk)\n\n"

    # Liquidity analysis
    current_ratio = supplier['current_ratio']
    if current_ratio >= 2.0:
        liquidity_health = "Strong"
    elif current_ratio >= 1.5:
        liquidity_health = "Adequate"
    else:
        liquidity_health = "Weak"

    report += f"Liquidity Analysis:\n"
    report += f"- Current Ratio: {current_ratio:.2f} ({liquidity_health})\n"
    report += f"- Days Sales Outstanding: {supplier['days_sales_outstanding']} days\n\n"

    # Profitability and growth
    report += f"Financial Performance:\n"
    report += f"- Revenue Growth: {supplier['revenue_growth'] * 100:+.1f}%\n"
    report += f"- Profit Margin: {supplier['profit_margin'] * 100:.1f}%\n"
    report += f"- Debt-to-Equity Ratio: {supplier['debt_to_equity']:.2f}\n\n"

    # Risk summary
    risk_factors = []
    if credit_risk == "High":
        risk_factors.append("Poor credit rating")
    if current_ratio < 1.5:
        risk_factors.append("Weak liquidity position")
    if supplier['revenue_growth'] < 0:
        risk_factors.append("Declining revenue")
    if supplier['debt_to_equity'] > 0.6:
        risk_factors.append("High leverage")

    if risk_factors:
        report += "Key Risk Factors:\n"
        for factor in risk_factors:
            report += f"- {factor}\n"
    else:
        report += "Overall Assessment: Low financial risk\n"

    return report


@tool
def compare_supplier_costs(supplier_ids: list, scenario_data: dict) -> str:
    """
    Compare total costs across multiple suppliers under different scenarios.

    Args:
        supplier_ids: List of supplier IDs to compare
        scenario_data: Dictionary with cost assumptions for each supplier

    Returns:
        Comparative cost analysis across suppliers and scenarios
    """
    # This would be implemented with actual cost modeling
    # Mock implementation for demonstration
    report = "Supplier Cost Comparison Analysis\n"
    report += f"Analysis Date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n"

    # This would contain actual comparison logic
    report += "Comparative analysis would be performed here with:\n"
    report += "- Base costs vs. total costs\n"
    report += "- Risk-adjusted costs\n"
    report += "- Scenario modeling (best case, worst case, most likely)\n"
    report += "- Sensitivity analysis\n"

    return report
