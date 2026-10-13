"""SOLUTION 5 - pandas intro

There is always more than one correct answer. Yours can look different!
"""

from pathlib import Path
import pandas as pd
DATA = Path(__file__).parent.parent / "data"

# TASK 1: Load data/general_ledger.csv into a DataFrame called gl. Print its shape and
# the first 3 rows.
gl = pd.read_csv(DATA / "general_ledger.csv", parse_dates=["date"])
print(gl.shape)
print(gl.head(3))

# TASK 2: What is the total, average and largest amount in the ledger?
print(gl["amount"].sum(), gl["amount"].mean(), gl["amount"].max())

# TASK 3: Which user posted the most entries? (hint: value_counts)
print(gl["posted_by"].value_counts().head(1))

# TASK 4: Add a column "quarter" using gl["date"].dt.quarter and show how many entries
# fall in each quarter.
gl["quarter"] = gl["date"].dt.quarter
print(gl["quarter"].value_counts().sort_index())
