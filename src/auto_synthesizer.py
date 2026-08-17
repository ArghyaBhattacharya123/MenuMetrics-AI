import pandas as pd
import numpy as np

def synthesize_custom_data(uploaded_df):
    """
    Takes the uploaded custom CSV/Excel data and synthesizes realistic 
    purchase ledgers, opex ledgers, and revenue ledgers.
    """
    # 1. sku_df
    sku_df = pd.DataFrame({
        'SKU_ID': uploaded_df['SKU_ID'],
        'Item_Name': uploaded_df['Item_Name'],
        'Category': 'Custom',
        'Unit_of_Measure': 'Units'
    })
    
    # 2. ledger_df (Jan - June 2026)
    months = ['2026-01-01', '2026-02-01', '2026-03-01', '2026-04-01', '2026-05-01', '2026-06-01']
    ledger_records = []
    
    for _, row in uploaded_df.iterrows():
        sku = row['SKU_ID']
        vol = row['Monthly_Volume']
        base_cost = row['Current_Cost']
        
        # Start cost at 90% and increase to 100% (+ inflation/variance)
        for i, m in enumerate(months):
            cost_multiplier = 0.90 + (i * 0.02) # gradual increase
            unit_cost = base_cost * cost_multiplier
            # add slight random noise
            unit_cost = unit_cost * np.random.uniform(0.98, 1.05)
            
            qty = int(vol * np.random.uniform(0.9, 1.1))
            
            ledger_records.append({
                'Date': m,
                'SKU_ID': sku,
                'Quantity_Bought': qty,
                'Total_Paid': qty * unit_cost
            })
            
    ledger_df = pd.DataFrame(ledger_records)
    
    # 3. rev_df (Monthly Revenue & Headcount)
    rev_records = []
    total_rev_base = (uploaded_df['Selling_Price'] * uploaded_df['Monthly_Volume']).sum()
    
    # Headcount scales with volume
    base_headcount = max(2, int(uploaded_df['Monthly_Volume'].sum() / 1000))
    
    for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']):
        growth = 1.0 + (i * 0.05)
        monthly_rev = total_rev_base * growth * np.random.uniform(0.95, 1.05)
        hc = base_headcount + int(i / 2) # headcount grows slowly
        
        rev_records.append({
            'Month': m,
            'Gross_Revenue': monthly_rev,
            'Headcount': hc
        })
        
    rev_df = pd.DataFrame(rev_records)
    
    # 4. opex_df
    opex_records = []
    for i, row in rev_df.iterrows():
        m = row['Month']
        rev = row['Gross_Revenue']
        
        # Payroll ~ 30-35% of revenue
        payroll = rev * np.random.uniform(0.30, 0.35)
        # Rent ~ 10% (Fixed-ish)
        rent = total_rev_base * 0.10
        # Marketing ~ 5%
        marketing = rev * 0.05
        # Utilities ~ 2%
        utilities = total_rev_base * 0.02
        
        opex_records.extend([
            {'Month': m, 'Expense_Category': 'Payroll', 'Expense_Type': 'Variable', 'Amount': payroll},
            {'Month': m, 'Expense_Category': 'Rent', 'Expense_Type': 'Fixed', 'Amount': rent},
            {'Month': m, 'Expense_Category': 'Marketing', 'Expense_Type': 'Variable', 'Amount': marketing},
            {'Month': m, 'Expense_Category': 'Utilities', 'Expense_Type': 'Fixed', 'Amount': utilities}
        ])
        
    opex_df = pd.DataFrame(opex_records)
    
    # 5. hist_df (Historical Sales for ML Pricing Engine)
    hist_records = []
    for _, row in uploaded_df.iterrows():
        name = row['Item_Name']
        base_price = row['Selling_Price']
        base_vol = row['Monthly_Volume']
        
        # Generate ~15 historical data points for linear regression
        for _ in range(15):
            price_variation = np.random.uniform(-0.2, 0.2)
            historical_price = base_price * (1 + price_variation)
            
            # Inverse demand curve
            volume_variation = -price_variation * 1.5 
            historical_qty = base_vol * (1 + volume_variation) * np.random.uniform(0.9, 1.1)
            
            hist_records.append({
                'Dish_Name': name,
                'Price_Sold_USD': historical_price,
                'Quantity_Sold': int(historical_qty)
            })
            
    hist_df = pd.DataFrame(hist_records)
    
    return sku_df, ledger_df, opex_df, rev_df, hist_df
