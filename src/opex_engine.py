import pandas as pd

def calculate_opex_metrics(opex_df=None, rev_df=None):
    if opex_df is None:
        opex_df = pd.read_csv("data/opex_ledger.csv")
    if rev_df is None:
        rev_df = pd.read_csv("data/monthly_revenue.csv")
    
    # Calculate Payroll per month
    payroll_df = opex_df[opex_df['Expense_Category'] == 'Payroll'].groupby('Month')['Amount'].sum().reset_index()
    payroll_df.rename(columns={'Amount': 'Payroll_Amount'}, inplace=True)
    
    # Total OpEx per month
    total_opex = opex_df.groupby('Month')['Amount'].sum().reset_index()
    total_opex.rename(columns={'Amount': 'Total_OpEx'}, inplace=True)
    
    # Fixed vs Variable
    type_split = opex_df.groupby(['Month', 'Expense_Type'])['Amount'].sum().unstack(fill_value=0).reset_index()
    
    # Merge everything
    df = pd.merge(rev_df, payroll_df, on='Month')
    df = pd.merge(df, total_opex, on='Month')
    df = pd.merge(df, type_split, on='Month')
    
    # Metrics
    df['Labor_Cost_Ratio'] = (df['Payroll_Amount'] / df['Gross_Revenue']) * 100
    df['Revenue_Per_Employee'] = df['Gross_Revenue'] / df['Headcount']
    
    return opex_df, df
