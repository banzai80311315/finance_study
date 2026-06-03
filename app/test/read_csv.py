import pandas as pd
import os

# print(os.getcwd())
df = pd.read_csv("data/stock_master.csv")
print(df)
print(df.columns)
