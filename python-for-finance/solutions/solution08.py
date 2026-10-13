"""SOLUTION 8 - Audit analytics

There is always more than one correct answer. Yours can look different!
"""

from pathlib import Path
import pandas as pd
DATA = Path(__file__).parent.parent / "data"

# TASK 1: Load gl. Find entries posted on a Sunday only.
gl = pd.read_csv(DATA / "general_ledger.csv", parse_dates=["date"])
gl["approved_by"] = gl["approved_by"].fillna("")
print(gl[gl["date"].dt.day_name() == "Sunday"][["entry_id", "date", "amount"]])

# TASK 2: Find entries posted in the LAST 3 days of the year (Dec 29-31). Cut-off
# testing looks at entries near year end.
print(gl[gl["date"] >= "2025-12-29"][["entry_id", "date", "account_name", "amount"]])

# TASK 3: For each user, count how many entries ended in .00 (whole numbers).
# Who has the most?
whole = gl[gl["amount"] % 1 == 0]
print(whole["posted_by"].value_counts())

# TASK 4: Find entries where the description contains "urgent" or "misc" (case-insensitive).
print(gl[gl["description"].str.contains("urgent|misc", case=False)]
      [["entry_id", "description", "amount"]])
