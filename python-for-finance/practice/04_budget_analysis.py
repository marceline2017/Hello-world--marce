"""
PRACTICE SET 4 - BUDGET TESTING and ANALYTICAL REVIEW (18 tasks)
Files: data/budget_2025.csv, data/general_ledger.csv, data/prior_year_2024.csv
Lesson needed first: 12

HOW TO USE: write your code under each TODO, then run this file:
    python practice/04_budget_analysis.py
Stuck? Compare with practice/solutions/04_budget_analysis.py - but try first!
The setup code below is already done for you.
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "data").is_dir())
DATA, OUTPUT = ROOT / "data", ROOT / "output"
OUTPUT.mkdir(exist_ok=True)
pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)

budget = pd.read_csv(DATA / "budget_2025.csv", dtype={"account": str})
gl = pd.read_csv(DATA / "general_ledger.csv", parse_dates=["date"], dtype={"account": str})
prior = pd.read_csv(DATA / "prior_year_2024.csv", dtype={"account": str})
gl["month"] = gl["date"].dt.month
gl["approved_by"] = gl["approved_by"].fillna("")

# TASK 1: (Warm-up) What is the total budgeted revenue, total budgeted expenses,
# and budgeted profit for the year?
# TODO


# TASK 2: TEST THE BUDGET: does every account have exactly 12 months, are there
# duplicates, blanks or negative numbers?
# TODO


# TASK 3: Show the budget per QUARTER per account (pivot table).
# TODO


# TASK 4: Build an actual-vs-budget table per account per month (merge on
# month + account). Missing values = 0.
# TODO


# TASK 5: ANNUAL variance per account: variance, variance % and F/A.
# (Revenue: actual above budget = F. Costs: actual above budget = A.)
# TODO


# TASK 6: Which 3 accounts have the biggest ADVERSE variance in money terms?
# TODO


# TASK 7: Use YOUR thresholds: flag accounts where |variance %| > 5 AND
# |variance| > 20,000. How many are flagged?
# TODO


# TASK 8: CUMULATIVE (year-to-date) Sales Revenue variance by month. In which
# month did the year-to-date position first turn adverse?
# TODO


# TASK 9: Find the month with the biggest Consulting Fees variance, then list the
# GL entries for Consulting Fees in that month. What do you notice?
# TODO


# TASK 10: FLEXED BUDGET for Cost of Goods Sold per month: budget COGS % of budget
# sales x ACTUAL sales. Compare with actual COGS each month.
# TODO


# TASK 11: SEASONALITY. What % of the yearly sales budget falls in each month,
# and what % of actual sales did?
# TODO


# TASK 12: Was the budget REALISTIC? Compare budget with last year's actual:
# budget growth % = budget / actual_2024 - 1, next to actual growth %.
# TODO


# TASK 13: YOUR OWN EXPECTATION for salaries: last year x 1.04 (a 4% pay rise).
# Is the actual within 5% of your expectation?
# TODO


# TASK 14: FORECAST ACCURACY. At the end of June, forecast the full year for each
# account as (Jan-Jun actual / 6 x 12). How far was that from the real full year?
# TODO


# TASK 15: GROSS MARGIN %: budget vs actual.
# TODO


# TASK 16: Line chart of monthly Sales Revenue: budget vs actual. Save it as
# output/p4_sales_bva.png
# TODO


# TASK 17: Make a VARIANCE EXPLANATION template for the client: the flagged
# accounts from task 7 with empty "client_explanation" and "evidence_seen"
# columns, saved to Excel.
# TODO


# TASK 18: Save everything to output/p4_budget.xlsx (annual BvA, flex table,
# realism table, the explanation template).
# TODO
