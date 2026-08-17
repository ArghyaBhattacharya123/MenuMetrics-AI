import streamlit as st
import pandas as pd
import plotly.express as px
from src.ml_model import train_and_predict_optimal_price

st.set_page_config(page_title="MenuMetrics-AI", layout="wide")
st.title("MenuMetrics-AI: Dynamic Pricing Simulator")

# Sidebar
st.sidebar.header("Simulation Settings")
target_margin = st.sidebar.slider("Target Profit Margin (%)", min_value=10, max_value=80, value=65, step=1)
inflation_rate = st.sidebar.slider("Expected Ingredient Inflation (%)", min_value=0, max_value=50, value=5, step=1)

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("data/mock_inventory.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Calculate current margin
df['Original_Margin_Amount'] = df['Current_Price'] - df['Cost_to_Make']
df['Original_Margin_Pct'] = (df['Original_Margin_Amount'] / df['Current_Price']) * 100

# Calculate simulated cost and margin based on inflation
df['Simulated_Cost'] = df['Cost_to_Make'] * (1 + inflation_rate / 100)
df['Simulated_Margin_Amount'] = df['Current_Price'] - df['Simulated_Cost']
df['Simulated_Margin_Pct'] = (df['Simulated_Margin_Amount'] / df['Current_Price']) * 100

# Margin Drop
df['Margin_Drop'] = df['Original_Margin_Pct'] - df['Simulated_Margin_Pct']

# Required Price to maintain target margin
df['Required_Price'] = df['Simulated_Cost'] / (1 - target_margin / 100)

st.subheader("Inventory Metrics (Simulated)")
st.dataframe(df.style.format({
    "Cost_to_Make": "${:.2f}",
    "Current_Price": "${:.2f}",
    "Original_Margin_Pct": "{:.1f}%",
    "Simulated_Cost": "${:.2f}",
    "Simulated_Margin_Amount": "${:.2f}",
    "Simulated_Margin_Pct": "{:.1f}%",
    "Margin_Drop": "{:.1f}%",
    "Required_Price": "${:.2f}"
}), use_container_width=True)

# Plot Margin Drop
st.subheader("Margin Drop After Inflation")
fig = px.bar(
    df, 
    x="Dish_Name", 
    y="Margin_Drop", 
    title="Margin Drop per Dish", 
    labels={'Margin_Drop': 'Margin Drop (%)', 'Dish_Name': 'Dish Name'},
    text_auto='.1f'
)
fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.header("🧠 AI Pricing Engine")
st.write("Leverage machine learning to find the optimal price point that maximizes your profit based on historical sales and price elasticity.")

# Select a dish
selected_dish = st.selectbox("Select a Dish to Analyze", df['Dish_Name'].tolist())

if selected_dish:
    # Get current cost for the selected dish
    dish_info = df[df['Dish_Name'] == selected_dish].iloc[0]
    current_cost = dish_info['Cost_to_Make']
    
    # Run ML prediction
    optimal_price, predicted_demand = train_and_predict_optimal_price(selected_dish, current_cost)
    
    if optimal_price is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Recommended Optimal Price", value=f"${optimal_price:.2f}")
        with col2:
            st.metric(label="Predicted Order Volume", value=f"{predicted_demand:.0f} units")
            
        # Load historical data for plotting
        try:
            hist_df = pd.read_csv("data/historical_sales.csv")
            hist_dish_df = hist_df[hist_df['Dish_Name'] == selected_dish]
            
            # Scatter plot with trendline
            st.subheader("Historical Demand vs. Price")
            fig_scatter = px.scatter(
                hist_dish_df,
                x="Price_Sold",
                y="Quantity_Sold",
                trendline="ols",
                title=f"Price Elasticity for {selected_dish}",
                labels={'Price_Sold': 'Price ($)', 'Quantity_Sold': 'Quantity Sold'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        except Exception as e:
            st.error(f"Could not load historical data for plotting: {e}")
    else:
        st.warning("Not enough historical data to generate a prediction.")
