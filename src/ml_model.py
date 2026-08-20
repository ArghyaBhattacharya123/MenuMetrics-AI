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
    # pyrefly: ignore
    predicted_quantities = model.predict(prices)
    # pyrefly: ignore
    predicted_quantities = np.maximum(0, predicted_quantities)
    profits = (prices.flatten() - current_cost) * predicted_quantities
    
    # pyrefly: ignore
    baseline_demand = model.predict(np.array([[current_price]]))[0]
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
