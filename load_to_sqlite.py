import pandas as pd
import sqlite3

deals     = pd.read_excel("data/Ethis Indonesia Deals.xlsx")
projects  = pd.read_excel("data/Project List EI.xlsx")
investors = pd.read_excel("data/All Investors Data - All Entity.xlsx")

# drop any duplicate-named columns so SQLite won’t choke
investors = investors.loc[:, ~investors.columns.duplicated()]

conn = sqlite3.connect("investor_lookup.db")
deals.to_sql("deals", conn, if_exists="replace", index=False)
projects.to_sql("projects", conn, if_exists="replace", index=False)
investors.to_sql("investors", conn, if_exists="replace", index=False)
conn.close()
print("✅ Data loaded into investor_lookup.db")
