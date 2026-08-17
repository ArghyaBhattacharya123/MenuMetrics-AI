import json
import os

def calculate_taxes(gross_cash, total_cogs, total_opex, region_code):
    tax_rates_path = "data/tax_rates.json"
    
    if not os.path.exists(tax_rates_path):
        return None
        
    with open(tax_rates_path, "r") as f:
        tax_config = json.load(f)
        
    # Default to US if region code not found
    config = tax_config.get(region_code, tax_config.get("US", {"transaction_tax_pct": 8.0, "corporate_tax_pct": 21.0}))
    
    transaction_tax_pct = config["transaction_tax_pct"]
    corporate_tax_pct = config["corporate_tax_pct"]
    
    # Net Sales Revenue (Extract transaction tax from Gross Cash)
    # Gross Cash = Net Sales + (Net Sales * transaction_tax_pct / 100)
    # Gross Cash = Net Sales * (1 + transaction_tax_pct / 100)
    net_sales_revenue = gross_cash / (1 + (transaction_tax_pct / 100))
    transaction_tax = gross_cash - net_sales_revenue
    
    # EBT
    ebt = net_sales_revenue - total_cogs - total_opex
    
    # Corporate Tax Liability (Only if EBT > 0)
    corporate_tax_liability = max(0, ebt * (corporate_tax_pct / 100))
    
    # NPAT
    npat = ebt - corporate_tax_liability
    
    # Total Tax Escrow
    total_tax_escrow = transaction_tax + corporate_tax_liability
    
    return {
        "gross_cash": gross_cash,
        "net_sales_revenue": net_sales_revenue,
        "transaction_tax": transaction_tax,
        "total_cogs": total_cogs,
        "total_opex": total_opex,
        "ebt": ebt,
        "corporate_tax_liability": corporate_tax_liability,
        "npat": npat,
        "total_tax_escrow": total_tax_escrow
    }
