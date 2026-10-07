"""SOLUTION 6 - Cleaning data

There is always more than one correct answer. Yours can look different!
"""

from pathlib import Path
import pandas as pd
DATA = Path(__file__).parent.parent / "data"

# TASK 1: Load data/messy_invoices.csv with dtype=str. Clean the column names (strip,
# lower, spaces to _).
df = pd.read_csv(DATA / "messy_invoices.csv", dtype=str)
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
print(df.columns.tolist())

# TASK 2: Clean "amount" into numbers. How many amounts could NOT be converted?
# "[$,]" means "any $ or comma" (a tiny pattern called a regular expression)
df["amount"] = pd.to_numeric(df["amount"].str.replace("[$,]", "", regex=True),
                             errors="coerce")
print("Not converted:", df["amount"].isna().sum())

# TASK 3: Standardise "status" and calculate the total of UNPAID invoices
# (after removing duplicates).
df["status"] = df["status"].str.strip().str.title()
df = df.drop_duplicates()
print("Unpaid total:", df.loc[df["status"] == "Unpaid", "amount"].sum())
