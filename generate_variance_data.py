import pandas as pd
import numpy as np

sku_data = [
    {"SKU_ID": "SKU001", "Item_Name": "Coffee Beans", "Unit_of_Measure": "kg"},
    {"SKU_ID": "SKU002", "Item_Name": "T-Shirts", "Unit_of_Measure": "pcs"},
    {"SKU_ID": "SKU003", "Item_Name": "Packaging Boxes", "Unit_of_Measure": "100-pack"},
    {"SKU_ID": "SKU004", "Item_Name": "Premium Flour", "Unit_of_Measure": "kg"},
    {"SKU_ID": "SKU005", "Item_Name": "Software Licenses", "Unit_of_Measure": "users"},
]
pd.DataFrame(sku_data).to_csv("data/sku_master.csv", index=False)

months = ['2023-01', '2023-02', '2023-03', '2023-04']
ledger = []

base_metrics = {
    "SKU001": {"qty": 100, "price": 15.0}, 
    "SKU002": {"qty": 500, "price": 8.0},  
    "SKU003": {"qty": 200, "price": 10.0}, 
    "SKU004": {"qty": 300, "price": 2.0},  
    "SKU005": {"qty": 50,  "price": 100.0} 
}

np.random.seed(42)

for i, month in enumerate(months):
    for sku, metrics in base_metrics.items():
        qty = metrics["qty"]
        price = metrics["price"]
        
        if sku == "SKU002": # Massive price inflation
            price = price * (1 + 0.15 * i)
            
        if sku == "SKU003": # Massive volume growth
            qty = int(qty * (1 + 0.5 * i))
            
        qty = max(1, int(qty * np.random.uniform(0.95, 1.05)))
        
        if sku != "SKU002":
            price = round(price * np.random.uniform(0.98, 1.02), 2)
        else:
            price = round(price, 2)
            
        ledger.append({
            "Date": f"{month}-01",
            "SKU_ID": sku,
            "Quantity_Bought": qty,
            "Total_Paid": round(qty * price, 2)
        })

pd.DataFrame(ledger).to_csv("data/purchase_ledger.csv", index=False)
