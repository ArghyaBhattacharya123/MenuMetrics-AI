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
# pyrefly: ignore [missing-import]
import sqlalchemy
# pyrefly: ignore [missing-import]
from src.ml_model import train_and_predict_optimal_price
# pyrefly: ignore [missing-import]
from src.variance_engine import calculate_variances
# pyrefly: ignore [missing-import]
from src.opex_engine import calculate_opex_metrics
# pyrefly: ignore [missing-import]
from src.tax_engine import calculate_taxes

st.set_page_config(page_title="MenuMetrics-AI", layout="wide", page_icon="assets/logo.png")

import streamlit.components.v1 as components
components.html("""
<script>
    const parentDoc = window.parent.document;
    
    // --- PWA Mobile App Injection ---
    if (!parentDoc.querySelector('link[rel="manifest"]')) {
        const manifest = {
            "name": "MenuMetrics-AI Executive Cockpit",
            "short_name": "MenuMetrics",
            "start_url": ".",
            "display": "standalone",
            "background_color": "#121212",
            "theme_color": "#121212",
            "icons": [{
                "src": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23121212'/><text y='50' x='50' font-family='Arial' font-size='40' fill='%23D4AF37' text-anchor='middle' dominant-baseline='middle'>M</text></svg>",
                "sizes": "192x192",
                "type": "image/svg+xml"
            }]
        };
        const manifestBlob = new Blob([JSON.stringify(manifest)], {type: 'application/json'});
        const manifestUrl = URL.createObjectURL(manifestBlob);
        
        const linkManifest = parentDoc.createElement('link');
        linkManifest.rel = 'manifest';
        linkManifest.href = manifestUrl;
        parentDoc.head.appendChild(linkManifest);
        
        const metaApple = parentDoc.createElement('meta');
        metaApple.name = 'apple-mobile-web-app-capable';
        metaApple.content = 'yes';
        parentDoc.head.appendChild(metaApple);
        
        const metaAppleStatus = parentDoc.createElement('meta');
        metaAppleStatus.name = 'apple-mobile-web-app-status-bar-style';
        metaAppleStatus.content = 'black-translucent';
        parentDoc.head.appendChild(metaAppleStatus);
    }
    // --- End PWA Injection ---

    if (!parentDoc.getElementById("custom-sidebar-toggle")) {
        const btn = parentDoc.createElement("button");
        btn.id = "custom-sidebar-toggle";
        btn.innerHTML = "☰ Menu";
        btn.style.cssText = "position: fixed; top: 15px; left: 15px; z-index: 999999; background-color: #1E293B; color: #F8FAFC; border: 1px solid #334155; padding: 6px 12px; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.3); font-family: sans-serif; transition: all 0.2s ease-in-out;";
        
        btn.onmouseover = () => { btn.style.backgroundColor = "#334155"; btn.style.borderColor = "#D4AF37"; };
        btn.onmouseout = () => { btn.style.backgroundColor = "#1E293B"; btn.style.borderColor = "#334155"; };
        
        btn.onclick = () => {
            // Find the collapsed control to open it
            const toggleOpen = parentDoc.querySelector('[data-testid="collapsedControl"]');
            if (toggleOpen) {
                toggleOpen.click();
            } else {
                // If it is already open, click the native close arrow inside the sidebar
                const sidebar = parentDoc.querySelector('[data-testid="stSidebar"]');
                if (sidebar) {
                    const buttons = sidebar.querySelectorAll('button');
                    if (buttons.length > 0) {
                        buttons[0].click();
                    }
                }
            }
        };
        parentDoc.body.appendChild(btn);


        // Monitor sidebar state dynamically to show/hide the custom button
        setInterval(() => {
            const sidebar = parentDoc.querySelector('[data-testid="stSidebar"]');
            if (sidebar) {
                const isExpanded = sidebar.getAttribute('aria-expanded') === 'true';
                if (isExpanded) {
                    btn.style.display = 'none';  // Sidebar is open, hide button
                } else {
                    btn.style.display = 'block'; // Sidebar is closed, show button
                }
            }
        }, 150);
    }
</script>
""", height=0, width=0)

st.markdown("""
<style>
    /* Hide Streamlit default UI elements for a clean product look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {visibility: hidden;}
    
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
    
    /* Bulletproof Tab Styling */
    div[data-testid="stTabs"] button {
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stTabs"] button:hover p {
        color: #D4AF37 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] p {
        color: #D4AF37 !important;
        font-weight: 800 !important;
    }
    /* Streamlit uses an animated div for the bottom highlight */
    div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {
        background-color: #D4AF37 !important;
    }
    /* Fallback if Streamlit version uses border-bottom instead of animated div */
    div[data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom: 2px solid #D4AF37 !important;
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
    
    /* Gold Title Container Base Styles */
    .gold-title-container {
        text-align: center;
        padding: 18px 30px;
        margin: 10px auto 25px auto;
        border: 2px solid #D4AF37;
        border-radius: 12px;
        background-color: #121212;
        box-shadow: 0 4px 20px rgba(212, 175, 55, 0.15);
        max-width: 500px;
        width: 100%;
    }
    .gold-title-text {
        color: #D4AF37;
        margin: 0;
        font-size: 3.2rem;
        font-weight: 700;
        letter-spacing: 1px;
    }

    /* Fully Responsive Media Queries for Mobile/Tablet */
    @media (max-width: 768px) {
        .gold-title-container {
            width: 90% !important;
            padding: 12px 15px !important;
            margin: 5px auto 15px auto !important;
        }
        .gold-title-text {
            font-size: 2.2rem !important;
        }
        
        /* Scale down Fluffy's popup window */
        div[data-testid="stPopoverBody"] {
            width: 90vw !important;
            right: 5vw !important;
            height: 60vh !important;
        }
        
        /* Shrink the persistent sidebar toggle to avoid clutter */
        #custom-sidebar-toggle {
            padding: 6px 10px !important;
            font-size: 12px !important;
            top: 10px !important;
            left: 10px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="gold-title-container">
        <h1 class="gold-title-text">MenuMetrics-AI</h1>
    </div>
""", unsafe_allow_html=True)
st.markdown("<h1 style='color: #38BDF8; text-shadow: 0 0 10px rgba(56, 189, 248, 0.4); margin-bottom: 0.5rem;'>Executive Cockpit</h1>", unsafe_allow_html=True)

import os
if os.path.exists("assets/logo.png"):
    try:
        st.logo("assets/logo.png")
    except AttributeError:
        pass  # Fallback for older Streamlit versions
elif os.path.exists("assets/logo.jpg"):
    try:
        st.logo("assets/logo.jpg")
    except AttributeError:
        pass

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
                    
                    # pyrefly: ignore [missing-import]
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
                    # pyrefly: ignore [missing-import]
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
    db_url = st.text_input("PostgreSQL Connection String", type="password", placeholder="postgresql://user:pass@host/dbname")
    if st.button("Sync Data to Cloud", use_container_width=True):
        if not db_url:
            st.warning("Please enter a connection string first.")
        else:
            try:
                import pandas as pd
                engine = sqlalchemy.create_engine(db_url)
                
                # Fetch active data
                df_to_push = None
                if profile_selection == "Demo Mode (Pre-Loaded)":
                    df_to_push = pd.read_csv("data/inventory.csv")
                else:
                    if f"sku_df_{profile_selection}" in st.session_state:
                        df_to_push = st.session_state[f"sku_df_{profile_selection}"]
                
                if df_to_push is not None and not df_to_push.empty:
                    # pyrefly: ignore
                    df_to_push.to_sql("menumetrics_export", con=engine, if_exists='replace', index=False)
                    st.success("✅ Data successfully synced to Enterprise Database!")
                else:
                    st.warning("No active data found to sync. Please load data first.")
            except Exception as e:
                st.error(f"Connection Failed: {e}")

region_selection = st.sidebar.selectbox("Select Currency", [
    "USD ($)", "INR (₹)", "EUR (€)", "GBP (£)", "CAD ($)", "GIP (£)", 
    "CNY (¥)", "KWD (د.ك)", "IRR (﷼)", "JPY (¥)", "RUB (₽)", 
    "KRW (₩)", "CHF (Fr)", "VND (₫)", "RMB (¥)"
])

fx_rates = {
    "USD": 1.0, "EUR": 0.92, "GBP": 0.79, "CAD": 1.36, "GIP": 0.79, 
    "CNY": 7.23, "KWD": 0.31, "IRR": 42000.0, "JPY": 155.0, "RUB": 92.0, 
    "KRW": 1360.0, "CHF": 0.90, "VND": 25400.0, "RMB": 7.23, "INR": 83.5
}
region_to_country = {
    "USD": "US", "INR": "IN", "EUR": "EU", "GBP": "GB", "CAD": "CA",
    "GIP": "GI", "CNY": "CN", "KWD": "KW", "IRR": "IR", "JPY": "JP",
    "RUB": "RU", "KRW": "KR", "CHF": "CH", "VND": "VN", "RMB": "CN"
}
curr_code = region_selection.split()[0]
match = re.search(r'\((.*?)\)', region_selection)
currency_symbol = match.group(1) if match else "$"
fx_rate = fx_rates.get(curr_code, 1.0)
region_code = region_to_country.get(curr_code, "US")

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
except Exception as e:
    st.error(f"Variance Engine Error: {e}")
    var_df = pd.DataFrame()
    ledger_df = pd.DataFrame()

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
except Exception as e:
    st.error(f"OpEx Engine Error: {e}")
    recent_labor_ratio = 0
    recent_month_data = {}
    opex_df = pd.DataFrame()
    efficiency_df = pd.DataFrame()

# Tax Engine Variables
try:
    tax_results = calculate_taxes(total_gross_revenue, total_cogs, total_opex, region_code)
except Exception as e:
    st.error(f"Tax Engine Error: {e}")
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
    
    # Fixed OpEx is Rent + Payroll. Marketing/Utilities is Variable.
    try:
        fixed_val_usd = recent_month_data.get('Fixed', 0)
        total_fixed_opex = fixed_val_usd * fx_rate
    except:
        total_fixed_opex = rent + staff # Fallback

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
    else:
        npat = ebitda
        st.warning("Tax engine failed. Cash-flow waterfall could not be generated.")

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

st.markdown("""
<style>
    /* Absolute Floating Button Fix */
    div[data-testid="stPopover"] {
        position: fixed !important;
        bottom: 25px !important;
        right: 25px !important;
        z-index: 999999 !important;
        width: auto !important;
        display: inline-block !important;
    }
    div[data-testid="stPopover"] > button {
        background-color: #6366F1 !important;
        color: white !important;
        border-radius: 50px !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4) !important;
        border: none !important;
        transition: transform 0.2s ease !important;
        width: auto !important;
    }
    div[data-testid="stPopover"] > button:hover {
        transform: scale(1.05) !important;
    }
    /* Fix for popup width */
    div[data-testid="stPopoverBody"] {
        width: 350px !important;
        background-color: #121212 !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

with st.popover("🤖 Fluffy", use_container_width=False):
    st.markdown("**Fluffy // AI Financial Companion**")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": "Hello! I am Fluffy 🤖. Ask me about **net profit**, **tax escrows**, **revenue**, **labor**, or **items**."})
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Ask Fluffy..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Parse query
        prompt_lower = prompt.lower()
        
        user_text = prompt_lower.strip()
        if user_text in ['?', '??'] or re.search(r'\b(help|options|menu)\b', user_text):
            response = "I can help you with:\n- Revenue & Profit (NPAT)\n- Margins (Gross & EBITDA)\n- Operating Expenses & Labor\n- Best/Worst Selling Items\n- Tax Escrows\n- Breakeven Analysis"
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
            
        responses = []
        historical_flag = False
        skip_global_revenue = False
        skip_global_profit = False
        
        try:
            # 1. Product & Inventory NLP Matching
            item_match = None
            if not df.empty and 'Dish_Name' in df.columns:
                prompt_words = re.findall(r'\b\w{4,}\b', prompt_lower)
                ignore_words = {'revenue', 'profit', 'margin', 'sales', 'item', 'items', 'inventory', 'best', 'worst', 'sold', 'made', 'what', 'much', 'from'}
                valid_words = [w for w in prompt_words if w not in ignore_words]
                
                for item in df['Dish_Name'].unique():
                    item_lower = str(item).lower()
                    if item_lower in prompt_lower or any(w in item_lower for w in valid_words):
                        item_match = item
                        break
                        
            if item_match:
                item_data = df[df['Dish_Name'] == item_match].iloc[0]
                item_qty = int(item_data['Monthly_Volume'])
                item_price = float(item_data['Current_Price'])
                item_cost = float(item_data['Cost_to_Make'])
                
                if re.search(r'\b(revenue|earn|earned|made|sales)\b', prompt_lower, re.IGNORECASE):
                    item_rev = item_price * item_qty
                    responses.append(f"• **{item_match}** generated **\\{currency_symbol}{item_rev:,.2f}** in sales.")
                    skip_global_revenue = True
                    
                if re.search(r'\b(profit|margin)\b', prompt_lower, re.IGNORECASE):
                    item_profit = (item_price - item_cost) * item_qty
                    responses.append(f"• **{item_match}** generated **\\{currency_symbol}{item_profit:,.2f}** in gross profit.")
                    skip_global_profit = True
                    
                if not skip_global_revenue and not skip_global_profit:
                    responses.append(f"• **{item_match}** sells for **\\{currency_symbol}{item_price:,.2f}** with a cost of **\\{currency_symbol}{item_cost:,.2f}**. You move approximately **{item_qty:,} units** per month.")
                
            if re.search(r'\b(best|top)\b.*\b(item|product|seller)\b|\bmost\b.*\b(sold|selling)\b', prompt_lower, re.IGNORECASE) or 'sold the most' in prompt_lower:
                if not df.empty and 'Monthly_Volume' in df.columns:
                    top_item = df.sort_values(by='Monthly_Volume', ascending=False).iloc[0]
                    responses.append(f"• Your best selling item is **{str(top_item['Dish_Name'])}** with **{int(float(top_item['Monthly_Volume']))} units**.")
                else:
                    responses.append("• I don't have enough data to determine the top seller.")
                    
            if re.search(r'\b(worst|bottom)\b.*\b(item|product|seller)\b|\bleast\b.*\b(sold|selling)\b', prompt_lower, re.IGNORECASE) or 'sold the least' in prompt_lower:
                if not df.empty and 'Monthly_Volume' in df.columns:
                    bottom_item = df.sort_values(by='Monthly_Volume', ascending=True).iloc[0]
                    responses.append(f"• Your worst selling item is **{str(bottom_item['Dish_Name'])}** with **{int(float(bottom_item['Monthly_Volume']))} units**.")
                else:
                    responses.append("• I don't have enough data to determine the worst seller.")
                    
            esc_currency = "\\$" if currency_symbol == "$" else currency_symbol
            
            if re.search(r'\b(costliest|highest cost|highest cp|highest cost price|most to make)\b|\bmost expensive\b.*\b(make|cost|bom|cp)\b', prompt_lower, re.IGNORECASE):
                if not df.empty and 'Cost_to_Make' in df.columns:
                    expensive_item = df.sort_values(by='Cost_to_Make', ascending=False).iloc[0]
                    responses.append(f"• The costliest item to make is {str(expensive_item['Dish_Name'])}, which costs {esc_currency}{float(expensive_item['Cost_to_Make']):.2f} per unit.")
                else:
                    responses.append("• I don't have enough data to determine the costliest item.")
                    
            if re.search(r'\b(least to make|lowest cost|lowest cp|lowest cost price)\b|\b(cheapest|least expensive)\b.*\b(make|cost|bom|cp)\b', prompt_lower, re.IGNORECASE):
                if not df.empty and 'Cost_to_Make' in df.columns:
                    cheap_item = df.sort_values(by='Cost_to_Make', ascending=True).iloc[0]
                    responses.append(f"• The cheapest item to make is {str(cheap_item['Dish_Name'])}, costing only {esc_currency}{float(cheap_item['Cost_to_Make']):.2f} per unit.")
                else:
                    responses.append("• I don't have enough data to determine the cheapest item.")
                    
            if re.search(r'\b(highest|highest priced|most expensive)\b.*\b(price|priced|selling|sold for|sp)\b', prompt_lower, re.IGNORECASE) and not re.search(r'\b(cost|cp|bom)\b', prompt_lower, re.IGNORECASE):
                if not df.empty and 'Current_Price' in df.columns:
                    high_price_item = df.sort_values(by='Current_Price', ascending=False).iloc[0]
                    responses.append(f"• The highest priced item on your menu is {str(high_price_item['Dish_Name'])}, selling for {esc_currency}{float(high_price_item['Current_Price']):.2f} (Cost to make: {esc_currency}{float(high_price_item['Cost_to_Make']):.2f}).")
                else:
                    responses.append("• I don't have enough data to determine the highest priced item.")
                    
            if re.search(r'\b(lowest|cheapest|least expensive)\b.*\b(price|priced|selling|sold for|sp)\b', prompt_lower, re.IGNORECASE) and not re.search(r'\b(cost|cp|bom)\b', prompt_lower, re.IGNORECASE):
                if not df.empty and 'Current_Price' in df.columns:
                    low_price_item = df.sort_values(by='Current_Price', ascending=True).iloc[0]
                    responses.append(f"• The lowest priced item on your menu is {str(low_price_item['Dish_Name'])}, selling for {esc_currency}{float(low_price_item['Current_Price']):.2f} (Cost to make: {esc_currency}{float(low_price_item['Cost_to_Make']):.2f}).")
                else:
                    responses.append("• I don't have enough data to determine the lowest priced item.")
                    
            if re.search(r'\b(order|sort|sorted|list)\b', prompt_lower, re.IGNORECASE) and re.search(r'\b(sp|cp|price|cost)\b', prompt_lower, re.IGNORECASE):
                sort_col = 'Cost_to_Make' if re.search(r'\b(cp|cost|make)\b', prompt_lower, re.IGNORECASE) else 'Current_Price'
                sort_label = 'BOM Cost' if sort_col == 'Cost_to_Make' else 'Selling Price'
                
                if not df.empty and sort_col in df.columns:
                    is_asc = False if re.search(r'\b(highest to lowest|descending|reverse)\b', prompt_lower, re.IGNORECASE) else True
                    sorted_df = df.sort_values(by=sort_col, ascending=is_asc)
                    menu_list = [f"{row['Dish_Name']} ({esc_currency}{float(row[sort_col]):.2f})" for _, row in sorted_df.iterrows()]
                    menu_str = ", ".join(menu_list)
                    responses.append(f"• Here are your items ordered by {sort_label}: {menu_str}")
                else:
                    responses.append(f"• I don't have enough data to sort by {sort_label}.")
                    
            if re.search(r'\b(what|list|show|all)\b.*\b(items|inventory|catalog|products)\b', prompt_lower, re.IGNORECASE):
                if not df.empty and 'Dish_Name' in df.columns:
                    total_items = len(df)
                    items_list = ", ".join(df['Dish_Name'].astype(str).tolist()[:5])
                    responses.append(f"• You currently have **{total_items} items** in your active inventory catalog. Some examples include: {items_list}...")
                else:
                    responses.append("• Your inventory is currently empty.")
            
            # 2. Financial KPI NLP Matching
            if re.search(r'\b(last month|yesterday|previous)\b', prompt_lower, re.IGNORECASE):
                historical_flag = True
                
            time_prefix = "Current Month's " if historical_flag else ""
            
            if re.search(r'\b(breakeven|break even)\b', prompt_lower, re.IGNORECASE):
                responses.append(f"• **{time_prefix}Breakeven Revenue:** \\{currency_symbol}{breakeven_revenue:,.2f}")
                
            if re.search(r'\b(tax|taxes|escrow)\b', prompt_lower, re.IGNORECASE):
                if tax_results:
                    responses.append(f"• **{time_prefix}Tax Escrow:** \\{currency_symbol}{tax_results['total_tax_escrow']:,.2f} (Includes \\{currency_symbol}{tax_results['transaction_tax']:,.2f} sales, \\{currency_symbol}{tax_results['corporate_tax_liability']:,.2f} corp)")
                else:
                    responses.append("• Tax calculations are currently unavailable.")
                    
            if not skip_global_profit and re.search(r'\b(profit|net|take home|pocket)\b', prompt_lower, re.IGNORECASE):
                profit_val = npat if tax_results else ebitda
                responses.append(f"• **{time_prefix}Net Profit (NPAT):** \\{currency_symbol}{profit_val:,.2f}")
                
            if not skip_global_revenue and re.search(r'\b(revenue|earn|earned|made|sales|overall)\b', prompt_lower, re.IGNORECASE):
                responses.append(f"• **{time_prefix}Gross Revenue:** \\{currency_symbol}{total_gross_revenue:,.2f}")
                
            if re.search(r'\b(margin|magrin|margn|profitability)\b', prompt_lower, re.IGNORECASE):
                responses.append(f"• **{time_prefix}Gross Margin:** {gross_margin_pct:.1f}% | **EBITDA Margin:** {ebitda_margin:.2f}%")
                
            if re.search(r'\b(labor|staff)\b', prompt_lower, re.IGNORECASE):
                responses.append(f"• **{time_prefix}Labor Cost:** \\{currency_symbol}{staff:,.0f} ({recent_labor_ratio:.1f}%)")
                
            if re.search(r'\b(ebitda)\b', prompt_lower, re.IGNORECASE):
                responses.append(f"• **{time_prefix}EBITDA:** \\{currency_symbol}{ebitda:,.2f}")
                
            if re.search(r'\b(opex|operating expenses?)\b', prompt_lower, re.IGNORECASE):
                responses.append(f"• **{time_prefix}Total OpEx:** \\{currency_symbol}{total_opex:,.2f}")
                
            if re.search(r'\b(cac|customer acquisition)\b', prompt_lower, re.IGNORECASE):
                responses.append(f"• **{time_prefix}CAC:** \\{currency_symbol}{cac:,.2f}")
                
            if re.search(r'\b(valuation|worth|value)\b', prompt_lower, re.IGNORECASE):
                responses.append(f"• **{time_prefix}Valuation Estimate:** \\{currency_symbol}{valuation_estimate:,.2f}")
                
            if re.search(r'\b(fixed vs variable|split)\b', prompt_lower, re.IGNORECASE):
                responses.append(f"• **{time_prefix}Fixed OpEx:** \\{currency_symbol}{total_fixed_opex:,.2f} vs **Variable OpEx:** \\{currency_symbol}{(total_opex - total_fixed_opex):,.2f}")
                
        except NameError:
            responses.append("• Some data is not fully loaded yet to answer that specific query.")
            
        if historical_flag and not responses:
            response = "• *Note: I currently only have access to this month's real-time data. Historical comparisons are coming soon!*"
        elif historical_flag and responses:
            response = "• *Note: I only have access to current real-time data. Here are your current metrics:*\n\n" + "\n\n".join(responses)
        elif not historical_flag and responses:
            response = "\n\n".join(responses)
        else:
            response = "I'm sorry, I couldn't understand that query. Try asking about 'tax', 'net profit', 'revenue', 'margin', 'labor', or specific inventory items."
            
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
