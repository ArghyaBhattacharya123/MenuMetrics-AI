import pandas as pd
import numpy as np
import datetime
import os

dishes = [
    {"name": "Chocolate Ice Cream Tub", "base_price": 8.00, "cost": 3.00, "elasticity": -50, "volume": 1200},
    {"name": "Cold Brew Coffee", "base_price": 5.00, "cost": 1.50, "elasticity": -80, "volume": 3000},
    {"name": "Gourmet Burger", "base_price": 18.00, "cost": 6.50, "elasticity": -30, "volume": 800},
    {"name": "Artisan Pizza", "base_price": 22.00, "cost": 7.00, "elasticity": -20, "volume": 1000},
    {"name": "Fruit Parfait", "base_price": 7.00, "cost": 2.50, "elasticity": -40, "volume": 1500},
]

records = []
start_date = datetime.date.today() - datetime.timedelta(days=100)
np.random.seed(42)

for i in range(100):
    date = start_date + datetime.timedelta(days=i)
    for dish in dishes:
        price_variation = np.random.uniform(-0.2, 0.2)
        price_sold = round(float(dish["base_price"]) * (1 + price_variation), 2)
        base_demand = float(dish["volume"]) / 30
        quantity_sold = int(base_demand + (price_sold - float(dish["base_price"])) * float(dish["elasticity"]))
        quantity_sold += np.random.randint(-int(max(1, base_demand*0.1)), int(max(1, base_demand*0.1)) + 1)
        quantity_sold = max(1, quantity_sold)
        records.append({
            "Date": date,
            "Dish_Name": dish["name"],
            "Price_Sold_USD": price_sold,
            "Quantity_Sold": quantity_sold,
            "Cost_USD": dish["cost"]
        })

df_hist = pd.DataFrame(records)
df_hist.to_csv("data/historical_sales.csv", index=False)

inv = pd.DataFrame([{
    "Dish_Name": d["name"],
    "Base_Cost_USD": d["cost"],
    "Base_Price_USD": d["base_price"],
    "Monthly_Volume": d["volume"]
} for d in dishes])
inv.to_csv("data/inventory.csv", index=False)

# cleanup old files
for f in ["inventory_us.csv", "inventory_in.csv", "historical_sales_us.csv", "historical_sales_in.csv"]:
    if os.path.exists(f"data/{f}"): os.remove(f"data/{f}")
