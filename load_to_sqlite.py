import pandas as pd
import sqlite3

deals     = pd.read_excel("data/Ethis Indonesia Deals.xlsx")
projects  = pd.read_excel("data/Project List EI.xlsx")
investors = pd.read_excel("data/All Investors Data - All Entity.xlsx")

# Clean up column names
investors.columns = investors.columns.str.strip().str.replace('\u00A0', ' ').str.replace('\n', ' ').str.lower()

# Ensure all column names are unique
seen = {}
new_cols = []
for col in investors.columns:
    if col not in seen:
        seen[col] = 0
        new_cols.append(col)
    else:
        seen[col] += 1
        new_cols.append(f"{col}_{seen[col]}")
investors.columns = new_cols

# Print columns for debugging
print("Investor columns:")
for i, col in enumerate(investors.columns):
    print(f"{i}: '{col}'")

conn = sqlite3.connect("investor_lookup.db")
deals.to_sql("deals", conn, if_exists="replace", index=False)
projects.to_sql("projects", conn, if_exists="replace", index=False)
investors.to_sql("investors", conn, if_exists="replace", index=False)
conn.close()
print("✅ Data loaded into investor_lookup.db") 