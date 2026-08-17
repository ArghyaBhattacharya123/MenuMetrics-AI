import pandas as pd
import numpy as np
import datetime
import os

# US Data
us_dishes = [
    {"name": "Wagyu Burger", "base_price": 28.00, "cost": 12.00, "elasticity": -15, "volume": 600},
    {"name": "Lobster Bisque", "base_price": 19.00, "cost": 7.50, "elasticity": -10, "volume": 300},
    {"name": "Truffle Pasta", "base_price": 22.00, "cost": 8.50, "elasticity": -15, "volume": 450},
    {"name": "Margherita Pizza", "base_price": 16.00, "cost": 4.00, "elasticity": -40, "volume": 800},
    {"name": "Vegan Quinoa Bowl", "base_price": 18.00, "cost": 5.00, "elasticity": -25, "volume": 500},
]

# India Data
in_dishes = [
    {"name": "Vada Pav", "base_price": 15.00, "cost": 5.00, "elasticity": -30, "volume": 5000},
    {"name": "Masala Dosa", "base_price": 120.00, "cost": 40.00, "elasticity": -5, "volume": 2000},
    {"name": "Paneer Tikka", "base_price": 250.00, "cost": 90.00, "elasticity": -2, "volume": 1200},
    {"name": "Butter Chicken", "base_price": 350.00, "cost": 150.00, "elasticity": -1.5, "volume": 1500},
    {"name": "Biryani", "base_price": 300.00, "cost": 120.00, "elasticity": -2.5, "volume": 2500},
]

def generate_hist(dishes, suffix):
    records = []
    start_date = datetime.date.today() - datetime.timedelta(days=100)
    np.random.seed(42)
    for i in range(100):
        date = start_date + datetime.timedelta(days=i)
        for dish in dishes:
            price_variation = np.random.uniform(-0.15, 0.25)
            price_sold = round(dish["base_price"] * (1 + price_variation), 2)
            base_demand = dish["volume"] / 30
            quantity_sold = int(base_demand + (price_sold - dish["base_price"]) * dish["elasticity"])
            quantity_sold += np.random.randint(-int(max(1, base_demand*0.1)), int(max(1, base_demand*0.1)) + 1)
            quantity_sold = max(1, quantity_sold)
            records.append({
                "Date": date,
                "Dish_Name": dish["name"],
                "Price_Sold": price_sold,
                "Quantity_Sold": quantity_sold,
                "Cost": dish["cost"]
            })
    df = pd.DataFrame(records)
    df.to_csv(f"data/historical_sales_{suffix}.csv", index=False)
    
    # Inventory
    inv = pd.DataFrame([{
        "Dish_Name": d["name"],
        "Cost_to_Make": d["cost"],
        "Current_Price": d["base_price"],
        "Monthly_Volume": d["volume"]
    } for d in dishes])
    inv.to_csv(f"data/inventory_{suffix}.csv", index=False)

generate_hist(us_dishes, "us")
generate_hist(in_dishes, "in")

# Delete old files
if os.path.exists("data/mock_inventory.csv"): os.remove("data/mock_inventory.csv")
if os.path.exists("data/historical_sales.csv"): os.remove("data/historical_sales.csv")
