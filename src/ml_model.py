import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def train_and_predict_optimal_price(dish_name, current_cost):
    # Load historical sales
    df = pd.read_csv("data/historical_sales.csv")
    
    # Filter for the specific dish
    dish_df = df[df['Dish_Name'] == dish_name]
    
    if len(dish_df) < 5:
        # Not enough data
        return None, None
        
    X = dish_df[['Price_Sold']]
    y = dish_df['Quantity_Sold']
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Simulate a range of prices
    min_price = max(current_cost, dish_df['Price_Sold'].min() * 0.5)
    max_price = dish_df['Price_Sold'].max() * 1.5
    
    prices = np.linspace(min_price, max_price, 200).reshape(-1, 1)
    predicted_quantities = model.predict(prices)
    
    # Ensure predicted quantities are non-negative
    predicted_quantities = np.maximum(0, predicted_quantities)
    
    # Calculate profits
    profits = (prices.flatten() - current_cost) * predicted_quantities
    
    # Find the index of max profit
    optimal_idx = np.argmax(profits)
    optimal_price = prices[optimal_idx][0]
    optimal_demand = predicted_quantities[optimal_idx]
    
    return optimal_price, optimal_demand
