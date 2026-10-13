"""SOLUTION 7 - Filter, group, pivot, merge

There is always more than one correct answer. Yours can look different!
"""

from pathlib import Path
import pandas as pd
DATA = Path(__file__).parent.parent / "data"

# TASK 1: Load the ledger (gl) and vendors. How many Consulting Fees entries are above 5,000?
gl = pd.read_csv(DATA / "general_ledger.csv", parse_dates=["date"])
vendors = pd.read_csv(DATA / "vendors.csv")
print(len(gl[(gl["account_name"] == "Consulting Fees") & (gl["amount"] > 5000)]))

# TASK 2: Total amount posted by each user, largest first.
print(gl.groupby("posted_by")["amount"].sum().sort_values(ascending=False))

# TASK 3: Make a pivot table: rows = account_name, columns = quarter, values = amount (sum).
gl["quarter"] = gl["date"].dt.quarter
print(gl.pivot_table(index="account_name", columns="quarter", values="amount",
                     aggfunc="sum").round(0))

# TASK 4: Merge vendors into gl and show total spend per vendor_name.
m = gl.merge(vendors, on="vendor_id", how="inner")
print(m.groupby("vendor_name")["amount"].sum().round(2))
