import pandas as pd
import numpy as np

months = ['2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-06']

# Revenue and Headcount
rev_data = []
base_rev = 100000
base_hc = 10

for i, m in enumerate(months):
    if i < 4:
        # First 4 months: scaling normally
        rev = base_rev + (i * 10000)
        hc = base_hc + i
    else:
        # Last 2 months: flat revenue, headcount bloat
        rev = base_rev + 30000 # Flat
        hc = base_hc + 3 + (i - 3) * 3 # jumps by 3 each month
        
    rev_data.append({
        "Month": m,
        "Gross_Revenue": rev,
        "Headcount": hc
    })

pd.DataFrame(rev_data).to_csv("data/monthly_revenue.csv", index=False)

# OpEx Ledger
opex_data = []

for i, m in enumerate(months):
    hc = rev_data[i]["Headcount"]
    
    # Payroll: 4000 per headcount
    opex_data.append({
        "Month": m,
        "Expense_Category": "Payroll",
        "Expense_Type": "Variable",
        "Amount": hc * 4000
    })
    
    # Other expenses
    opex_data.append({"Month": m, "Expense_Category": "Rent", "Expense_Type": "Fixed", "Amount": 10000})
    opex_data.append({"Month": m, "Expense_Category": "Marketing", "Expense_Type": "Variable", "Amount": 5000 + i * 500})
    opex_data.append({"Month": m, "Expense_Category": "Software", "Expense_Type": "Fixed", "Amount": 1000})
    opex_data.append({"Month": m, "Expense_Category": "Utilities", "Expense_Type": "Variable", "Amount": 1500 + i * 100})

pd.DataFrame(opex_data).to_csv("data/opex_ledger.csv", index=False)
