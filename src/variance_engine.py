import pandas as pd

def calculate_variances(sku_df=None, ledger_df=None):
    if sku_df is None:
        sku_df = pd.read_csv("data/sku_master.csv")
    if ledger_df is None:
        ledger_df = pd.read_csv("data/purchase_ledger.csv")
    
    # Calculate Unit_Cost
    ledger_df['Unit_Cost'] = ledger_df['Total_Paid'] / ledger_df['Quantity_Bought']
    ledger_df['Date'] = pd.to_datetime(ledger_df['Date'])
    
    # Sort by date
    ledger_df = ledger_df.sort_values(by=['SKU_ID', 'Date'])
    
    # Join with SKU info
    df = pd.merge(ledger_df, sku_df, on='SKU_ID')
    
    variance_results = []
    
    for sku in df['SKU_ID'].unique():
        sku_data = df[df['SKU_ID'] == sku].tail(2).reset_index(drop=True)
        if len(sku_data) < 2:
            continue
            
        prev = sku_data.iloc[0]
        curr = sku_data.iloc[1]
        
        ppv = (curr['Unit_Cost'] - prev['Unit_Cost']) * curr['Quantity_Bought']
        vol_var = (curr['Quantity_Bought'] - prev['Quantity_Bought']) * prev['Unit_Cost']
        
        variance_results.append({
            'SKU_ID': sku,
            'Item_Name': curr['Item_Name'],
            'Unit_of_Measure': curr['Unit_of_Measure'],
            'Prev_Unit_Cost': prev['Unit_Cost'],
            'Curr_Unit_Cost': curr['Unit_Cost'],
            'Prev_Qty': prev['Quantity_Bought'],
            'Curr_Qty': curr['Quantity_Bought'],
            'PPV': ppv,
            'Volume_Variance': vol_var,
            'Total_Variance': curr['Total_Paid'] - prev['Total_Paid']
        })
        
    return df, pd.DataFrame(variance_results)
