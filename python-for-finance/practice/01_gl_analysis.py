"""
PRACTICE SET 1 - GENERAL LEDGER ANALYSIS (25 tasks)
Files: data/general_ledger.csv, data/vendors.csv
Lessons needed first: 5, 6, 7, 8

HOW TO USE: write your code under each TODO, then run this file:
    python practice/01_gl_analysis.py
Stuck? Compare with practice/solutions/01_gl_analysis.py - but try first!
The setup code below is already done for you.
"""

from pathlib import Path
import pandas as pd

# Find the course folder (the one with "data" inside) - works from any sub-folder
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "data").is_dir())
DATA, OUTPUT = ROOT / "data", ROOT / "output"
OUTPUT.mkdir(exist_ok=True)
pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)

gl = pd.read_csv(DATA / "general_ledger.csv", parse_dates=["date"], dtype={"account": str})
vendors = pd.read_csv(DATA / "vendors.csv")
gl["approved_by"] = gl["approved_by"].fillna("")
gl["vendor_id"] = gl["vendor_id"].fillna("")
gl["month"] = gl["date"].dt.month

# TASK 1: (Warm-up) How many rows and columns does the ledger have? What are the
# first and last dates?
# TODO


# TASK 2: For each account_name show the number of entries and the total amount,
# sorted by total (largest first).
# TODO


# TASK 3: Which account has the largest AVERAGE entry size?
# TODO


# TASK 4: Show the 10 largest entries (entry_id, date, account_name, amount).
# TODO


# TASK 5: Monthly Sales Revenue. Which month was best and which was worst?
# TODO


# TASK 6: What % of total EXPENSES (every account except Sales Revenue) does
# each expense account make up?
# TODO


# TASK 7: Make a table of revenue and expenses per QUARTER, plus profit.
# TODO


# TASK 8: Pivot: number of entries per user (rows) per month (columns).
# TODO


# TASK 9: Which user posted the highest TOTAL value? Show total and average per user.
# TODO


# TASK 10: Spend per vendor NAME (merge with vendors). What % of all vendor spend
# goes to the biggest vendor? (This is called "supplier concentration".)
# TODO


# TASK 11: Which accounts are paid to MORE than one vendor? (A rent account paid
# to two landlords would be strange.)
# TODO


# TASK 12: How many entries were posted in the LAST 3 DAYS of each month?
# (Month-end rush = higher risk of errors.)
# TODO


# TASK 13: How many entries were posted on each day of the week? Put the days
# in order Monday -> Sunday.
# TODO


# TASK 14: How many entries have NO cents (e.g. 5000.00)? Show them per user.
# TODO


# TASK 15: Which exact amounts appear MORE THAN ONCE? Show the amount, how many
# times, and the entry_ids.
# TODO


# TASK 16: (Challenge) Near-duplicates: same vendor and same amount within 7 days,
# but NOT on the same day. Hint: sort by vendor, amount, date and use .diff().
# TODO


# TASK 17: What % of entries of 10,000 or more were approved by someone?
# TODO


# TASK 18: Who approves whom? Make a crosstab of posted_by (rows) vs approved_by
# (columns) for approved entries. The diagonal = self-approval.
# TODO


# TASK 19: List the missing numbers in the entry_id sequence.
# TODO


# TASK 20: STRATIFICATION. Put every entry in a size band:
# 0-1k, 1k-5k, 5k-10k, 10k-20k, 20k+ and show count, total value and % of value.
# TODO


# TASK 21: COVERAGE. If you test only the 50 largest entries, what % of the total
# value do you cover?
# TODO


# TASK 22: SAMPLE SELECTION. Pick ALL "key items" (amount >= 20,000) plus a random
# sample of 25 from the rest (use random_state=1 so it is repeatable).
# TODO


# TASK 23: CUT-OFF. List every entry dated in the last 5 days of the year.
# TODO


# TASK 24: (Challenge) RELATIVE SIZE FACTOR. For each vendor, divide the largest
# entry by the second largest. A factor above 2 means one entry is much bigger
# than normal for that vendor.
# TODO


# TASK 25: Save an Excel file output/p1_gl_analysis.xlsx with sheets for
# your stratification (task 20), approvals crosstab (task 18) and sample (task 22).
# TODO
