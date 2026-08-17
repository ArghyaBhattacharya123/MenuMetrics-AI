import pandas as pd
import numpy as np
import datetime

dishes = [
    {"name": "Truffle Pasta", "base_price": 22.00, "cost": 8.50, "elasticity": -10},
    {"name": "Wagyu Burger", "base_price": 28.00, "cost": 12.00, "elasticity": -15},
    {"name": "Margherita Pizza", "base_price": 16.00, "cost": 4.00, "elasticity": -30},
    {"name": "Lobster Bisque", "base_price": 19.00, "cost": 7.50, "elasticity": -5},
    {"name": "Vegan Quinoa Bowl", "base_price": 18.00, "cost": 5.00, "elasticity": -20},
]

records = []
start_date = datetime.date.today() - datetime.timedelta(days=100)

np.random.seed(42)

for i in range(100):
    date = start_date + datetime.timedelta(days=i)
    for dish in dishes:
        price_variation = np.random.uniform(-0.2, 0.3)
        price_sold = round(dish["base_price"] * (1 + price_variation), 2)
        
        base_demand = 20
        quantity_sold = int(base_demand + (price_sold - dish["base_price"]) * dish["elasticity"])
        quantity_sold += np.random.randint(-4, 5)
        quantity_sold = max(1, quantity_sold)
        
        records.append({
            "Date": date,
            "Dish_Name": dish["name"],
            "Price_Sold": price_sold,
            "Quantity_Sold": quantity_sold,
            "Cost": dish["cost"]
        })

df = pd.DataFrame(records)
df.to_csv("data/historical_sales.csv", index=False)
