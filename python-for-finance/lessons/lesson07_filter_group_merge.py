"""
LESSON 7 - FILTER, GROUP, PIVOT and MERGE
=========================================

These four skills answer almost every business question:
  FILTER  "Show me only the travel expenses over 5,000"      (Excel filter)
  GROUP   "What is the total per account?"                    (SUMIF)
  PIVOT   "Total per account per month"                       (Pivot table)
  MERGE   "Add the vendor name from the vendor list"          (VLOOKUP)

Run:  python lessons/lesson07_filter_group_merge.py
"""

from pathlib import Path
import pandas as pd

DATA = Path(__file__).parent.parent / "data"
pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)

gl = pd.read_csv(DATA / "general_ledger.csv", parse_dates=["date"],
                 dtype={"account": str})
vendors = pd.read_csv(DATA / "vendors.csv")
gl["month"] = gl["date"].dt.month


# ---------------------------------------------------------------
# 1. FILTER - keep only rows that match a condition
# ---------------------------------------------------------------
# Step A: a condition gives True/False for every row (a "mask")
is_travel = gl["account_name"] == "Travel Expense"
print(is_travel.head())

# Step B: put the mask inside [ ] to keep only the True rows
travel = gl[is_travel]
print(f"\nTravel entries: {len(travel)}")

# Several conditions: use  &  (and)   |  (or)   ~  (not)
# Each condition MUST be inside its own ( ) brackets.
big_travel = gl[(gl["account_name"] == "Travel Expense") & (gl["amount"] > 5000)]
print(f"Travel over 5,000: {len(big_travel)}")

# .isin() - is the value one of these?
rent_or_utilities = gl[gl["account"].isin(["6100", "6300"])]
print(f"Rent or utilities: {len(rent_or_utilities)}")

# .between() - in a range (both ends included)
q4 = gl[gl["date"].between("2025-10-01", "2025-12-31")]
print(f"Q4 entries: {len(q4)}")

# Text search
urgent = gl[gl["description"].str.contains("urgent", case=False)]
print(f"Entries described as 'urgent': {len(urgent)}")

# .query() - the same filter written like a sentence
print(len(gl.query("amount > 20000 and posted_by == 'amina'")))


# ---------------------------------------------------------------
# 2. GROUP BY - totals per category (like SUMIF / subtotals)
# ---------------------------------------------------------------
# Read it as: "group the rows by account_name, then sum the amount"
by_account = gl.groupby("account_name")["amount"].sum()
print("\nTotal per account:")
print(by_account.round(2))

# Several calculations at once with .agg()
summary = gl.groupby("account_name")["amount"].agg(["count", "sum", "mean", "max"])
print("\nSummary per account:")
print(summary.round(2))

# Group by two columns
by_user_account = gl.groupby(["posted_by", "account_name"])["amount"].sum()
print(by_user_account.head(10).round(2))

# Percentage of total
pct = (by_account / by_account.sum() * 100).round(1)
print("\n% of total activity per account:")
print(pct.sort_values(ascending=False))


# ---------------------------------------------------------------
# 3. PIVOT TABLE - rows x columns, just like Excel
# ---------------------------------------------------------------
pivot = pd.pivot_table(
    gl,
    index="account_name",   # rows
    columns="month",         # columns
    values="amount",         # what to calculate
    aggfunc="sum",           # how
    fill_value=0,
    margins=True,            # add a Total row and column
    margins_name="Total",
)
print("\nPivot: account x month")
print(pivot.round(0))


# ---------------------------------------------------------------
# 4. MERGE - join two tables (like VLOOKUP / XLOOKUP)
# ---------------------------------------------------------------
# Add vendor_name and status from the vendor list to each GL row.
merged = gl.merge(vendors, on="vendor_id", how="left")
#   how="left"  : keep every GL row, even if no vendor matches
#   how="inner" : keep only rows that match in both tables
print(merged[["entry_id", "vendor_id", "vendor_name", "status", "amount"]].head())

print("\nSpend per vendor:")
spend = (merged.dropna(subset=["vendor_name"])
               .groupby(["vendor_name", "status"])["amount"]
               .sum()
               .sort_values(ascending=False))
print(spend.round(2))

# indicator=True shows where each row came from - great for reconciliations
check = gl.merge(vendors, on="vendor_id", how="outer", indicator=True)
print("\nMatch result:")
print(check["_merge"].value_counts())
#   both       -> found in both tables
#   left_only  -> in GL but not in vendor list (here: rows with no vendor)
#   right_only -> in vendor list but never used


# ---------------------------------------------------------------
# 5. A TRIAL-BALANCE-STYLE monthly report
# ---------------------------------------------------------------
gl["type"] = gl["account"].apply(lambda a: "Revenue" if a.startswith("4") else "Expense")
monthly = gl.pivot_table(index="month", columns="type", values="amount", aggfunc="sum")
monthly["Profit"] = monthly["Revenue"] - monthly["Expense"]
monthly["Margin %"] = (monthly["Profit"] / monthly["Revenue"] * 100).round(1)
print("\nMonthly profit report:")
print(monthly.round(0))


# ===============================================================
# SUMMARY
#   df[df["col"] > 5]                          filter
#   df[(cond1) & (cond2)]                      AND filter (use brackets!)
#   df.groupby("col")["amount"].sum()          SUMIF
#   df.groupby("col")["amount"].agg([...])     many stats at once
#   pd.pivot_table(df, index, columns, values, aggfunc)
#   df.merge(other, on="key", how="left")      VLOOKUP
#
# NEXT: exercises/exercise07.py
# ===============================================================
