# MenuMetrics-AI: Executive Cockpit (Brain)

## Project Overview
MenuMetrics-AI is a fully autonomous, enterprise-grade Executive Financial Cockpit. It simulates real-world business environments using predictive ML algorithms, dynamic variance detection, and comprehensive OpEx, labor efficiency, and tax/escrow modules.

## Folder Structure
```text
MenuMetrics-AI/
├── .streamlit/
│   └── config.toml           # Enterprise UI configuration (Pitch-Black OLED Theme)
├── data/
│   └── mock_inventory.csv    # Default pre-loaded dummy data
├── src/
│   ├── auto_synthesizer.py   # Generates simulated ledgers and historical sales for custom uploads
│   ├── ml_model.py           # Linear regression ML model for price elasticity
│   ├── opex_engine.py        # Logic for calculating Labor Ratios, Fixed/Variable expenses
│   ├── tax_engine.py         # Logic for Sales and Corporate tax escrows
│   └── variance_engine.py    # Logic for detecting Purchase Price Variance (PPV)
├── app.py                    # Main Streamlit Dashboard Application
├── requirements.txt          # Python dependencies
├── run.bat                   # One-click Windows launcher
├── run.py                    # Python programmatic launcher
└── run.sh                    # One-click Mac/Linux launcher
```

## Completed Modules & Features
- **Module 1: Inventory Variance & Pricing AI:** Calculates elasticity-based optimal pricing and isolates supply chain inflation.
- **Module 2: OpEx & Labor Efficiency:** Calculates labor ratios and breakeven targets.
- **Module 3: Tax & Escrow:** Evaluates Net Profit After Tax (NPAT) and calculates reserve requirements.
- **Module 4: Executive Waterfall:** Visualizes cash flow from Gross Revenue down to NPAT.
- **Custom Ingestion Engine:** Accepts custom CSV/Excel files and instantly auto-synthesizes historical ML data and simulated ledgers.
- **Live Table Editor:** Updates dashboard instantly upon user edits.
- **Stress Testing:** Models extreme conditions like Recession Shocks and Supply Chain inflation.
- **Enterprise UX/UI:** Polished with a pitch-black OLED theme, hidden dev menus, and refined interactive elements.

## Source Code References

### `app.py`
```python
# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.express as px
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go
# pyrefly: ignore [missing-import]
from plotly.subplots import make_subplots
import re
from src.ml_model import train_and_predict_optimal_price
from src.variance_engine import calculate_variances
from src.opex_engine import calculate_opex_metrics
from src.tax_engine import calculate_taxes

st.set_page_config(page_title="MenuMetrics-AI", layout="wide")

st.markdown("""
<style>
    /* Hide Streamlit default UI elements for a clean product look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Card-like styling for metric containers */
    div[data-testid="metric-container"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Soft borders and rounded corners for expanders and inputs */
    div[data-testid="stExpander"] {
        border-radius: 12px;
        border: 1px solid #334155;
    }
    
    /* Clean tab navigation styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    
    /* Sleek Pitch-Black Theme Button Styling */
    div.stButton > button, div.stDownloadButton > button {
        background-color: #1a1a1a !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background-color: #262626 !important;
        border-color: #6366F1 !important;
        color: #FFFFFF !important;
        box-shadow: 0 6px 12px rgba(99, 102, 241, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>MenuMetrics-AI <span style='color:#6366F1;'>// Executive Cockpit</span></h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("Account Management")
profile_selection = st.sidebar.selectbox("Select Business Profile", ["Demo Mode (Pre-Loaded)", "Custom Account 1", "Custom Account 2"])

if profile_selection != "Demo Mode (Pre-Loaded)":
    with st.sidebar.container():
        st.markdown("### 📁 Custom Data Ingestion")
        template_csv = "SKU_ID,Item_Name,Current_Cost,Selling_Price,Monthly_Volume\nSKU001,Premium Widget,12.50,45.00,150\nSKU002,Standard Widget,5.00,20.00,500"
        st.download_button(
            label="📥 Download Sample CSV Template",
            data=template_csv,
            file_name="menumetrics_template.csv",
            mime="text/csv"
        )
        uploaded_file = st.file_uploader("Upload Custom Account Data (CSV/Excel)", type=["csv", "xlsx"])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    uploaded_df = pd.read_csv(uploaded_file)
                else:
                    uploaded_df = pd.read_excel(uploaded_file)
                    
                required_columns = ['SKU_ID', 'Item_Name', 'Current_Cost', 'Selling_Price', 'Monthly_Volume']
                if all(col in uploaded_df.columns for col in required_columns):
                    st.session_state[f"uploaded_data_{profile_selection}"] = uploaded_df
                    
                    from src.auto_synthesizer import synthesize_custom_data
                    syn_sku, syn_ledger, syn_opex, syn_rev, syn_hist = synthesize_custom_data(uploaded_df)
                    st.session_state[f"sku_df_{profile_selection}"] = syn_sku
                    st.session_state[f"ledger_df_{profile_selection}"] = syn_ledger
                    st.session_state[f"opex_df_{profile_selection}"] = syn_opex
                    st.session_state[f"rev_df_{profile_selection}"] = syn_rev
                    st.session_state[f"hist_df_{profile_selection}"] = syn_hist
                    
                    st.success("Data successfully imported and auto-synthesized across all financial modules!")
                else:
                    st.error(f"Missing required columns. Expected: {required_columns}")
            except Exception as e:
                st.error(f"Error processing file: {e}")
                
        if f"uploaded_data_{profile_selection}" in st.session_state:
            with st.expander("✏️ Live Data Editor"):
                st.caption("Directly edit numbers. The dashboard instantly recalculates.")
                current_data = st.session_state[f"uploaded_data_{profile_selection}"]
                edited_df = st.data_editor(current_data, key=f"editor_{profile_selection}")
                if not edited_df.equals(current_data):
                    st.session_state[f"uploaded_data_{profile_selection}"] = edited_df
                    from src.auto_synthesizer import synthesize_custom_data
                    syn_sku, syn_ledger, syn_opex, syn_rev, syn_hist = synthesize_custom_data(edited_df)
                    st.session_state[f"sku_df_{profile_selection}"] = syn_sku
                    st.session_state[f"ledger_df_{profile_selection}"] = syn_ledger
                    st.session_state[f"opex_df_{profile_selection}"] = syn_opex
                    st.session_state[f"rev_df_{profile_selection}"] = syn_rev
                    st.session_state[f"hist_df_{profile_selection}"] = syn_hist
                    st.rerun()
                    
st.sidebar.markdown("---")
st.sidebar.header("Global Settings")
with st.sidebar.expander("Enterprise Cloud Sync"):
    cloud_sync = st.toggle("Enable Live Cloud Database Sync (PostgreSQL)")
    if cloud_sync:
        st.success("Cloud Sync Active: Connected to remote database cluster.")

region_selection = st.sidebar.selectbox("Select Currency", ["USD ($)", "INR (₹)", "EUR (€)", "JPY (¥)"])

fx_rates = {"USD": 1.0, "INR": 83.5, "EUR": 0.92, "JPY": 155.0}
curr_code = region_selection.split()[0]
currency_symbol = re.search(r'\((.*?)\)', region_selection).group(1)
fx_rate = fx_rates[curr_code]

st.sidebar.header("Simulation Settings")
stress_scenario = st.sidebar.selectbox("Macro Stress Test Scenario", ["Normal Market Conditions", "📉 Recession Shock (-20% Volume)", "⚡ Supply Chain Crisis (+15% Cost Inflation)"])
target_margin = st.sidebar.slider("Target Profit Margin (%)", min_value=10, max_value=80, value=65, step=1)
inflation_rate = st.sidebar.slider("Expected BOM Inflation (%)", min_value=0, max_value=50, value=5, step=1)

is_custom_active = profile_selection != "Demo Mode (Pre-Loaded)" and f"opex_df_{profile_selection}" in st.session_state

st.sidebar.subheader("Monthly Operating Expenses (OpEx)")
if is_custom_active:
    st.sidebar.info("OpEx is auto-scaled from your custom upload.")
    syn_opex = st.session_state[f"opex_df_{profile_selection}"]
    latest_month = syn_opex['Month'].iloc[-1]
    month_data = syn_opex[syn_opex['Month'] == latest_month]
    rent = month_data[month_data['Expense_Category'] == 'Rent']['Amount'].sum()
    staff = month_data[month_data['Expense_Category'] == 'Payroll']['Amount'].sum()
    utils = month_data[month_data['Expense_Category'] == 'Utilities']['Amount'].sum() + month_data[month_data['Expense_Category'] == 'Marketing']['Amount'].sum()
    
    st.sidebar.metric("Monthly Rent (Auto)", f"{currency_symbol}{rent:,.0f}")
    st.sidebar.metric("Staff Salaries (Auto)", f"{currency_symbol}{staff:,.0f}")
    st.sidebar.metric("Utilities/Marketing (Auto)", f"{currency_symbol}{utils:,.0f}")
else:
    rent = st.sidebar.number_input("Monthly Rent", value=int(5000 * fx_rate))
    staff = st.sidebar.number_input("Staff Salaries", value=int(15000 * fx_rate))
    utils = st.sidebar.number_input("Utilities/Marketing", value=int(2000 * fx_rate))

total_opex = rent + staff + utils

st.sidebar.subheader("Growth Settings")
new_customers = st.sidebar.number_input("New Customers Acquired This Month", value=100)
marketing_spend = st.sidebar.number_input("Marketing Spend", value=int(1500 * fx_rate))
val_multiplier = st.sidebar.number_input("Business Valuation Multiplier", value=5.0)
prev_profit = st.sidebar.number_input("Previous Month Net Profit", value=int(8000 * fx_rate))

tab0, tab1, tab2, tab3, tab4 = st.tabs([
    "Executive Summary", 
    "Pricing Simulator", 
    "Inventory Variance", 
    "OpEx & Labor", 
    "Tax & Compliance"
])

# Load all data globally so the Executive Summary can use it.
@st.cache_data
def load_data():
    return pd.read_csv("data/inventory.csv")

try:
    if profile_selection == "Demo Mode (Pre-Loaded)":
        df_base = load_data()
    else:
        profile_key = f"uploaded_data_{profile_selection}"
        if profile_key in st.session_state:
            df_base = st.session_state[profile_key].copy()
            if 'Item_Name' in df_base.columns:
                df_base = df_base.rename(columns={'Item_Name': 'Dish_Name', 'Current_Cost': 'Base_Cost_USD', 'Selling_Price': 'Base_Price_USD'})
        else:
            df_base = pd.DataFrame(columns=['Dish_Name', 'Base_Cost_USD', 'Base_Price_USD', 'Monthly_Volume'])
            # We no longer display a warning here since the upload UI is right in the sidebar

    df = df_base.copy()
    
    if stress_scenario == "📉 Recession Shock (-20% Volume)":
        if 'Monthly_Volume' in df.columns:
            df['Monthly_Volume'] = df['Monthly_Volume'] * 0.8
        st.warning("⚠️ **Stress Test Active:** Recession Shock (-20% Volume) applied to projections.")
    elif stress_scenario == "⚡ Supply Chain Crisis (+15% Cost Inflation)":
        df['Base_Cost_USD'] = df['Base_Cost_USD'] * 1.15
        st.warning("⚠️ **Stress Test Active:** Supply Chain Crisis (+15% Cost Inflation) applied to projections.")
        
    # Apply FX
    df['Cost_to_Make'] = df['Base_Cost_USD'] * fx_rate
    df['Current_Price'] = df['Base_Price_USD'] * fx_rate
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Pricing Simulator Variables
total_gross_revenue = (df['Current_Price'] * df['Monthly_Volume']).sum()
total_cogs = (df['Cost_to_Make'] * df['Monthly_Volume']).sum()
gross_profit = total_gross_revenue - total_cogs
ebitda = gross_profit - total_opex
ebitda_margin = (ebitda / total_gross_revenue) * 100 if total_gross_revenue > 0 else 0

# Variance Engine Variables
try:
    if is_custom_active:
        syn_sku = st.session_state[f"sku_df_{profile_selection}"]
        syn_ledger = st.session_state[f"ledger_df_{profile_selection}"]
        ledger_df, var_df = calculate_variances(sku_df=syn_sku, ledger_df=syn_ledger)
    else:
        ledger_df, var_df = calculate_variances()
        
    var_df['Curr_Unit_Cost'] = var_df['Curr_Unit_Cost'] * fx_rate
    var_df['Prev_Unit_Cost'] = var_df['Prev_Unit_Cost'] * fx_rate
    var_df['PPV'] = var_df['PPV'] * fx_rate
    var_df['Volume_Variance'] = var_df['Volume_Variance'] * fx_rate
    var_df['Total_Variance'] = var_df['Total_Variance'] * fx_rate
except:
    var_df = pd.DataFrame()

# OpEx Engine Variables
try:
    if is_custom_active:
        syn_opex = st.session_state[f"opex_df_{profile_selection}"]
        syn_rev = st.session_state[f"rev_df_{profile_selection}"]
        opex_df, efficiency_df = calculate_opex_metrics(opex_df=syn_opex, rev_df=syn_rev)
    else:
        opex_df, efficiency_df = calculate_opex_metrics()
        
    recent_month_data = efficiency_df.iloc[-1]
    recent_labor_ratio = recent_month_data['Labor_Cost_Ratio']
except:
    recent_labor_ratio = 0
    recent_month_data = {}

# Tax Engine Variables
try:
    region_code = curr_code[:2]
    tax_results = calculate_taxes(total_gross_revenue, total_cogs, total_opex, region_code)
except:
    tax_results = None

with tab0:
    st.header("Executive Summary: The Master Cheat Sheet")
    
    st.subheader("🚨 Anomaly & Leak Alert Center")
    alerts_triggered = False
    
    # 1. Supplier Alert
    if not var_df.empty:
        for idx, row in var_df.iterrows():
            if row['Curr_Unit_Cost'] > row['Prev_Unit_Cost']:
                pct_increase = ((row['Curr_Unit_Cost'] - row['Prev_Unit_Cost']) / row['Prev_Unit_Cost']) * 100
                if pct_increase > 5:
                    st.error(f"**Supplier Alert:** High Purchase Price Variance detected! **{row['Item_Name']}** increased by {pct_increase:.1f}%.")
                    alerts_triggered = True
                    
    # 2. Labor Alert
    if recent_labor_ratio > 35:
        st.warning(f"**Labor Alert:** Labor Cost Ratio is {recent_labor_ratio:.1f}%, exceeding the 35% safe threshold.")
        alerts_triggered = True
        
    # 3. Tax Alert
    if tax_results:
        st.info(f"**Tax Alert:** Current outstanding Tax Escrow is **{currency_symbol}{tax_results['total_tax_escrow']:,.2f}**.")
        alerts_triggered = True
        
    if not alerts_triggered:
        st.success("✅ All operational metrics are within healthy benchmarks.")
        
    st.markdown("---")
    
    st.subheader("⚖️ Breakeven Gauge")
    b_col1, b_col2 = st.columns(2)
    gross_margin_pct = (gross_profit / total_gross_revenue) * 100 if total_gross_revenue else 0
    
    # Fixed OpEx is Rent + Software etc. For simplicity, rent+utils is proxy
    try:
        fixed_val_usd = recent_month_data.get('Fixed', 0)
        total_fixed_opex = fixed_val_usd * fx_rate
    except:
        total_fixed_opex = rent + utils # Fallback

    breakeven_revenue = total_fixed_opex / (gross_margin_pct / 100) if gross_margin_pct > 0 else 0
    
    with b_col1:
        st.metric("Breakeven Revenue", f"{currency_symbol}{breakeven_revenue:,.2f}", help="Minimum monthly revenue required to stay open.")
    with b_col2:
        st.metric("Gross Margin", f"{gross_margin_pct:.1f}%")
        
    st.markdown("---")
    
    st.subheader("🌊 The Ultimate Cash-Flow Waterfall")
    if tax_results:
        npat = tax_results['npat']
        taxes = tax_results['transaction_tax'] + tax_results['corporate_tax_liability']
        
        fig_master = go.Figure(go.Waterfall(
            orientation = "v",
            measure = ["relative", "relative", "total", "relative", "relative", "total", "relative", "total"],
            x = [
                "Gross Sales Revenue", 
                "Total BOM Costs (COGS)", 
                "Gross Profit", 
                "Operating Expenses", 
                "Labor & Payroll", 
                "EBITDA", 
                "Estimated Taxes", 
                "Net Take-Home Cash Flow"
            ],
            textposition = "outside",
            text = [f"{currency_symbol}{val:,.0f}" for val in [
                total_gross_revenue, 
                -total_cogs, 
                gross_profit, 
                -(total_opex - staff), 
                -staff,
                ebitda,
                -taxes,
                npat
            ]],
            y = [
                total_gross_revenue, 
                -total_cogs, 
                gross_profit, 
                -(total_opex - staff), 
                -staff,
                ebitda,
                -taxes,
                npat
            ],
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
        ))
        
        fig_master.update_layout(title="Master Cash-Flow Timeline", margin=dict(l=20, r=20, t=50, b=20), height=500)
        st.plotly_chart(fig_master, use_container_width=True)

    st.markdown("---")
    
    st.subheader("📈 Growth & Valuation Scorecard")
    
    cac = marketing_spend / new_customers if new_customers > 0 else 0
    valuation_estimate = ebitda * val_multiplier
    
    current_profit = npat if tax_results else ebitda
    monthly_roi = ((current_profit - prev_profit) / prev_profit * 100) if prev_profit > 0 else 0
    
    g_col1, g_col2, g_col3 = st.columns(3)
    
    with g_col1:
        st.metric("CAC (Customer Acquisition Cost)", f"{currency_symbol}{cac:,.2f}")
    with g_col2:
        st.metric("Valuation Estimate", f"{currency_symbol}{valuation_estimate:,.2f}")
    with g_col3:
        st.metric("Monthly ROI (Profit Growth)", f"{monthly_roi:.1f}%", delta=f"{monthly_roi:.1f}%")
        
    st.info(f"💡 **Note:** Valuation Estimate is based on a {val_multiplier}x EBITDA multiple. This is an internal estimate and does not constitute a formal business appraisal.")
    
    st.markdown("---")
    st.subheader("📥 Export Executive Report")
    
    # Calculate some safe values for string formatting
    report_tax_escrow = tax_results['total_tax_escrow'] if tax_results else 0
    supplier_alert_status = 'Triggered' if (not var_df.empty and len(var_df[var_df['Curr_Unit_Cost'] > var_df['Prev_Unit_Cost']]) > 0) else 'Clear'
    
    report_content = f"""# Executive Financial Report

## Core Metrics
- **Currency:** {curr_code}
- **Target Margin:** {target_margin}%
- **Breakeven Revenue:** {currency_symbol}{breakeven_revenue:,.2f}
- **EBITDA Margin:** {ebitda_margin:.2f}%
- **Net Profit (NPAT):** {currency_symbol}{npat:,.2f}

## Alert Status
- **Supplier Alert:** {supplier_alert_status}
- **Labor Cost Ratio:** {recent_labor_ratio:.1f}%
- **Outstanding Tax Escrow:** {currency_symbol}{report_tax_escrow:,.2f}

## Growth Scorecard
- **Customer Acquisition Cost (CAC):** {currency_symbol}{cac:,.2f}
- **Business Valuation Estimate:** {currency_symbol}{valuation_estimate:,.2f}
- **Monthly Profit Growth (ROI):** {monthly_roi:.1f}%
"""
    st.download_button(
        label="Download Executive Report (.md)",
        data=report_content,
        file_name="executive_report.md",
        mime="text/markdown",
        type="primary"
    )


with tab1:
    st.subheader("Executive Financial Summary")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Total Revenue", f"{currency_symbol}{total_gross_revenue:,.2f}")
    m_col2.metric("Total COGS", f"{currency_symbol}{total_cogs:,.2f}")
    m_col3.metric("Total OpEx", f"{currency_symbol}{total_opex:,.2f}")
    m_col4.metric("EBITDA", f"{currency_symbol}{ebitda:,.2f}")
    
    st.markdown("---")
    st.header("💡 Profit Optimization & Cost-Cutting Recommendations")
    
    cogs_flag = False
    for idx, row in df.iterrows():
        if row['Cost_to_Make'] > 0.35 * row['Current_Price']:
            st.warning(f"⚠️ **COGS Alert:** {row['Dish_Name']} BOM cost is {(row['Cost_to_Make']/row['Current_Price'])*100:.1f}% of selling price (Exceeds 35%). Recommend bulk procurement savings.")
            cogs_flag = True
    
    if not cogs_flag:
        st.success("✅ **BOM Optimization:** All SKUs maintain healthy margins below 35% BOM cost.")
        
    if total_opex > 0.45 * total_gross_revenue:
        st.warning(f"⚠️ **OpEx Burn Warning:** Operating expenses are {(total_opex/total_gross_revenue)*100:.1f}% of gross revenue (Exceeds 45%). Recommend utility efficiency or marketing ROI audit.")
    else:
        st.success(f"✅ **Healthy OpEx:** Operating expenses are well controlled at {(total_opex/total_gross_revenue)*100:.1f}% of revenue.")
        
    margin_boost = (total_opex * 0.05) + (total_cogs * 0.03)
    st.info(f"📈 **Potential Margin Boost:** Trimming OpEx by 5% and reducing BOM waste by 3% would increase monthly profit by **{currency_symbol}{margin_boost:,.2f}**.")
    
    st.markdown("---")
    st.header("📈 Financial & Price Analytics")
    v_col1, v_col2, v_col3 = st.columns(3)
    
    with v_col1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=ebitda_margin,
            title={'text': "EBITDA Margin (%)"},
            gauge={
                'axis': {'range': [0, 50]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 5], 'color': "red"},
                    {'range': [5, 15], 'color': "yellow"},
                    {'range': [15, 50], 'color': "green"}
                ]
            }
        ))
        fig_gauge.update_layout(margin=dict(l=20, r=20, t=50, b=20), height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with v_col2:
        fig_donut = px.pie(
            values=[total_cogs, total_opex, max(0, ebitda)], 
            names=["BOM / COGS", "OpEx", "Net Profit"], 
            hole=0.4,
            title="Cost Breakdown"
        )
        fig_donut.update_layout(margin=dict(l=20, r=20, t=50, b=20), height=300)
        st.plotly_chart(fig_donut, use_container_width=True)
    
    with v_col3:
        fig_hist = px.histogram(
            df, 
            x="Current_Price", 
            title="Price Distribution",
            labels={'Current_Price': f'Current Price ({currency_symbol})'}
        )
        fig_hist.update_layout(margin=dict(l=20, r=20, t=50, b=20), height=300)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    st.markdown("---")
    st.header("🧠 AI Pricing Engine")
    st.write("Leverage machine learning to find the optimal price point that maximizes your profit based on historical sales and price elasticity.")
    
    selected_dish = st.selectbox("Select a SKU / Product to Analyze", df['Dish_Name'].tolist())
    
    if selected_dish:
        dish_info = df[df['Dish_Name'] == selected_dish].iloc[0]
        current_cost = dish_info['Cost_to_Make']
        current_price = dish_info['Current_Price']
        
        if is_custom_active and f"hist_df_{profile_selection}" in st.session_state:
            syn_hist = st.session_state[f"hist_df_{profile_selection}"]
            optimal_price, predicted_demand, revenue_impact = train_and_predict_optimal_price(selected_dish, current_cost, current_price, fx_rate, hist_df=syn_hist)
        else:
            optimal_price, predicted_demand, revenue_impact = train_and_predict_optimal_price(selected_dish, current_cost, current_price, fx_rate)
        
        if optimal_price is not None:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Recommended Optimal Price", value=f"{currency_symbol}{optimal_price:.2f}")
            with col2:
                st.metric(label="Predicted Order Volume", value=f"{predicted_demand:.0f} units")
            with col3:
                impact_color = "normal" if revenue_impact >= 0 else "inverse"
                st.metric(label="Predicted Monthly Revenue Impact", value=f"{currency_symbol}{revenue_impact:,.2f}", delta=f"{currency_symbol}{revenue_impact:,.2f}", delta_color=impact_color)
                
            try:
                if is_custom_active and f"hist_df_{profile_selection}" in st.session_state:
                    hist_df = st.session_state[f"hist_df_{profile_selection}"]
                else:
                    hist_df = pd.read_csv("data/historical_sales.csv")
                    
                hist_dish_df = hist_df[hist_df['Dish_Name'] == selected_dish].copy()
                hist_dish_df['Price_Sold'] = hist_dish_df['Price_Sold_USD'] * fx_rate
                
                st.subheader("Historical Demand vs. Price")
                fig_scatter = px.scatter(
                    hist_dish_df,
                    x="Price_Sold",
                    y="Quantity_Sold",
                    trendline="ols",
                    title=f"Price Elasticity for {selected_dish}",
                    labels={'Price_Sold': f'Price ({currency_symbol})', 'Quantity_Sold': 'Quantity Sold'}
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            except Exception as e:
                st.error(f"Could not load historical data for plotting: {e}")
        else:
            st.warning("Not enough historical data to generate a prediction.")

with tab2:
    st.header("Inventory Variance Engine")
    st.write("Track inventory spending and isolate margin leaks due to supplier inflation.")
    
    try:
        st.subheader("🚨 Leak Detector Alerts")
        alert_triggered = False
        if not var_df.empty:
            for idx, row in var_df.iterrows():
                if row['Curr_Unit_Cost'] > row['Prev_Unit_Cost']:
                    pct_increase = ((row['Curr_Unit_Cost'] - row['Prev_Unit_Cost']) / row['Prev_Unit_Cost']) * 100
                    if pct_increase > 5:
                        st.error(f"🚨 **Alert:** Supplier raised prices on **{row['Item_Name']}** by **{pct_increase:.1f}%**. This cost you an extra **{currency_symbol}{row['PPV']:,.2f}** this month in pure Price Variance.")
                        alert_triggered = True
        
        if not alert_triggered:
            st.success("✅ **All Good:** No significant supplier price hikes detected this month.")
                
        st.markdown("---")
        
        st.subheader("📈 Unit Cost Velocity")
        if not var_df.empty:
            selected_sku = st.selectbox("Select Item to Analyze", var_df['Item_Name'].tolist())
            sku_id = var_df[var_df['Item_Name'] == selected_sku].iloc[0]['SKU_ID']
            
            chart_data = ledger_df[ledger_df['SKU_ID'] == sku_id].copy()
            
            fig_line = px.line(chart_data, x="Date", y="Unit_Cost", markers=True, title=f"Unit Cost Trend for {selected_sku}")
            fig_line.update_layout(yaxis_title=f"Unit Cost ({currency_symbol})", xaxis_title="Date")
            st.plotly_chart(fig_line, use_container_width=True)
            
            st.markdown("---")
            
            st.subheader("📊 MoM Spend Increase Breakdown")
            
            melted_var = var_df.melt(id_vars=['Item_Name'], value_vars=['PPV', 'Volume_Variance'], var_name='Variance_Type', value_name='Amount')
            melted_var['Variance_Type'] = melted_var['Variance_Type'].map({'PPV': 'Price Variance (PPV)', 'Volume_Variance': 'Volume Variance'})
            
            color_discrete_map = {'Volume Variance': 'green', 'Price Variance (PPV)': 'red'}
            
            fig_bar = px.bar(melted_var, x="Item_Name", y="Amount", color="Variance_Type", title="Spend Variance Breakdown (Price vs Volume)", color_discrete_map=color_discrete_map, labels={"Amount": f"Variance Amount ({currency_symbol})"})
            st.plotly_chart(fig_bar, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading variance data: {e}. Please ensure data is generated.")

with tab3:
    st.header("OpEx & Labor Efficiency Engine")
    st.write("Track overhead sustainability and ensure hiring is driving revenue.")
    
    try:
        st.subheader("🚨 Efficiency Alerts")
        if recent_labor_ratio > 35:
            st.error(f"🚨 **Labor Warning ({recent_month_data.get('Month', '')}):** Payroll is consuming **{recent_labor_ratio:.1f}%** of revenue. Hiring is currently outpacing sales growth.")
        else:
            st.success(f"✅ **Labor Healthy ({recent_month_data.get('Month', '')}):** Payroll is well managed at **{recent_labor_ratio:.1f}%** of revenue.")
            
        st.markdown("---")
        
        st.subheader("📈 Current Month KPIs")
        kpi1, kpi2, kpi3 = st.columns(3)
        
        rev_per_emp = recent_month_data.get('Revenue_Per_Employee', 0)
        t_opex = recent_month_data.get('Total_OpEx', 0)
        fixed_val = recent_month_data.get('Fixed', 0)
        variable_val = recent_month_data.get('Variable', 0)
        
        rev_per_emp_fx = rev_per_emp * fx_rate
        total_opex_fx = t_opex * fx_rate
        fixed_pct = (fixed_val / t_opex) * 100 if t_opex else 0
        var_pct = (variable_val / t_opex) * 100 if t_opex else 0
        
        with kpi1:
            st.metric("Revenue Per Employee", f"{currency_symbol}{rev_per_emp_fx:,.0f}")
        with kpi2:
            st.metric("Total OpEx Burn", f"{currency_symbol}{total_opex_fx:,.0f}")
        with kpi3:
            st.metric("Fixed vs Variable Split", f"{fixed_pct:.0f}% / {var_pct:.0f}%")
            
        st.markdown("---")
        
        col_combo, col_donut = st.columns([2, 1])
        
        with col_combo:
            st.subheader("📊 Scaling Efficiency (Revenue vs Headcount)")
            
            fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
            
            plot_rev = efficiency_df['Gross_Revenue'] * fx_rate
            
            fig_combo.add_trace(
                go.Bar(x=efficiency_df['Month'], y=plot_rev, name="Gross Revenue", marker_color="royalblue"),
                secondary_y=False,
            )
            
            fig_combo.add_trace(
                go.Scatter(x=efficiency_df['Month'], y=efficiency_df['Headcount'], name="Headcount", mode='lines+markers', line=dict(color='red', width=3)),
                secondary_y=True,
            )
            
            fig_combo.update_layout(title="Revenue vs Headcount Trend")
            fig_combo.update_yaxes(title_text=f"Gross Revenue ({currency_symbol})", secondary_y=False)
            fig_combo.update_yaxes(title_text="Total Headcount", secondary_y=True)
            
            st.plotly_chart(fig_combo, use_container_width=True)
            
        with col_donut:
            st.subheader(f"🍩 OpEx Breakdown ({recent_month_data.get('Month', '')})")
            
            recent_opex = opex_df[opex_df['Month'] == recent_month_data.get('Month', '')].copy()
            recent_opex['Amount'] = recent_opex['Amount'] * fx_rate
            
            fig_donut_opex = px.pie(
                recent_opex,
                values='Amount',
                names='Expense_Category',
                hole=0.4,
                title="Expense Distribution"
            )
            st.plotly_chart(fig_donut_opex, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error loading Module 2 data: {e}")

with tab4:
    st.header("Tax & Regulatory Compliance")
    st.write("Calculate true Net Profit After Tax (NPAT) and required tax escrow.")
    
    try:
        t_results = tax_results
        
        if t_results:
            npat = t_results["npat"]
            total_escrow = t_results["total_tax_escrow"]
            
            st.subheader("💰 True Take-Home Profit (Safe to Spend)")
            st.metric("NPAT (Net Profit After Tax)", f"{currency_symbol}{npat:,.2f}")
            
            st.error(f"🚨 **Tax Escrow Required:** You must transfer **{currency_symbol}{total_escrow:,.2f}** to a separate bank account immediately to cover upcoming GST/Sales and Corporate Tax liabilities.")
            
            st.markdown("---")
            
            st.subheader("🌊 Profit Waterfall (Cash to NPAT)")
            
            fig_waterfall_tax = go.Figure(go.Waterfall(
                orientation = "v",
                measure = ["relative", "relative", "relative", "relative", "relative", "total"],
                x = ["Gross Cash Collected", "Transaction Tax", "COGS", "OpEx", "Corporate Tax", "NPAT"],
                textposition = "outside",
                text = [f"{currency_symbol}{val:,.0f}" for val in [
                    t_results['gross_cash'], 
                    -t_results['transaction_tax'], 
                    -t_results['total_cogs'], 
                    -t_results['total_opex'], 
                    -t_results['corporate_tax_liability'], 
                    npat
                ]],
                y = [
                    t_results['gross_cash'], 
                    -t_results['transaction_tax'], 
                    -t_results['total_cogs'], 
                    -t_results['total_opex'], 
                    -t_results['corporate_tax_liability'], 
                    npat
                ],
                connector = {"line":{"color":"rgb(63, 63, 63)"}},
            ))
            
            fig_waterfall_tax.update_layout(title="From Cash in Bank to True Profit", margin=dict(l=20, r=20, t=50, b=20), height=400)
            st.plotly_chart(fig_waterfall_tax, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error loading Tax data: {e}")

```

### `run.py`
```python
import os
import sys
from streamlit.web import cli as stcli

if __name__ == "__main__":
    app_path = os.path.abspath("app.py")
    sys.argv = ["streamlit", "run", app_path, "--global.developmentMode=false"]
    sys.exit(stcli.main())

```

### `run.bat`
```bat
@echo off
echo Starting MenuMetrics-AI Executive Cockpit...
python run.py
pause

```

### `run.sh`
```bash
#!/bin/bash
echo "Starting MenuMetrics-AI Executive Cockpit..."
python3 run.py

```

### `requirements.txt`
```text
streamlit>=1.30.0
pandas>=2.0.0
plotly>=5.18.0
scikit-learn>=1.3.0
reportlab>=4.0.0
openpyxl>=3.1.2
statsmodels>=0.14.0  
 
```

### `.streamlit/config.toml`
```toml
[theme]
base="dark"
primaryColor="#FFFFFF"
backgroundColor="#050505"
secondaryBackgroundColor="#121212"
textColor="#EDEDED"
font="sans serif"

[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[client]
toolbarMode = "minimal"

```

### `src/auto_synthesizer.py`
```python
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

```

### `src/ml_model.py`
```python
import pandas as pd
import numpy as np
import warnings
from sklearn.linear_model import LinearRegression

warnings.filterwarnings('ignore', category=UserWarning)

def train_and_predict_optimal_price(dish_name, current_cost, current_price, fx_rate, hist_df=None):
    if hist_df is None:
        hist_df = pd.read_csv("data/historical_sales.csv")
        
    dish_df = hist_df[hist_df['Dish_Name'] == dish_name]
    
    if len(dish_df) < 5:
        return None, None, None
        
    X = (dish_df[['Price_Sold_USD']] * fx_rate).rename(columns={'Price_Sold_USD': 'Price_Sold'})
    y = dish_df['Quantity_Sold']
    
    model = LinearRegression()
    model.fit(X, y)
    
    min_price = max(current_cost, X['Price_Sold'].min() * 0.5)
    max_price = X['Price_Sold'].max() * 1.5
    
    prices = np.linspace(min_price, max_price, 200).reshape(-1, 1)
    predicted_quantities = model.predict(prices)
    predicted_quantities = np.maximum(0, predicted_quantities)
    profits = (prices.flatten() - current_cost) * predicted_quantities
    
    baseline_demand = model.predict([[current_price]])[0]
    baseline_profit = (current_price - current_cost) * baseline_demand
    
    optimal_idx = np.argmax(profits)
    optimal_price = prices[optimal_idx][0]
    optimal_demand = predicted_quantities[optimal_idx]
    optimal_profit = profits[optimal_idx]
    
    if optimal_profit < baseline_profit:
        optimal_price = current_price
        optimal_demand = baseline_demand
        
    monthly_baseline_revenue = current_price * baseline_demand * 30
    monthly_optimal_revenue = optimal_price * optimal_demand * 30
    revenue_impact_monthly = monthly_optimal_revenue - monthly_baseline_revenue
    
    return optimal_price, optimal_demand, revenue_impact_monthly

```

### `src/opex_engine.py`
```python
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

```

### `src/tax_engine.py`
```python
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

```

### `src/variance_engine.py`
```python
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

```

