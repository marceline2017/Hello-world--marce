"""
LESSON 5 - PANDAS: Excel inside Python
======================================

pandas is THE tool for data analysis in Python. Banks, audit firms and
finance teams all use it.

  - A DataFrame = a whole table (like an Excel sheet)
  - A Series    = one column of that table

Why not just use Excel?
  - Excel slows down or stops at ~1 million rows. pandas handles millions.
  - Every step is written down, so a reviewer can re-perform your work
    (very important in audit - this is your "audit trail").
  - Run the same analysis next month in 1 second.

Install once (in your terminal):   pip install pandas matplotlib openpyxl
Run:   python lessons/lesson05_pandas_intro.py
"""

from pathlib import Path
import pandas as pd       # "pd" is the nickname everyone uses

DATA = Path(__file__).parent.parent / "data"

# Show more columns when printing (just for nicer output)
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)


# ---------------------------------------------------------------
# 1. Load a file into a DataFrame
# ---------------------------------------------------------------
gl = pd.read_csv(DATA / "general_ledger.csv")
# For Excel files you would use:  pd.read_excel("file.xlsx", sheet_name="Sheet1")

# ---------------------------------------------------------------
# 2. First look at the data - ALWAYS do this first
# ---------------------------------------------------------------
print(gl.head())          # first 5 rows   (gl.head(10) for 10)
print(gl.tail(3))         # last 3 rows
print(gl.shape)           # (rows, columns)
print(gl.columns.tolist())  # column names

print("\n--- info(): column types and missing values ---")
gl.info()

print("\n--- describe(): quick statistics of number columns ---")
print(gl["amount"].describe())


# ---------------------------------------------------------------
# 3. Choosing columns
# ---------------------------------------------------------------
amounts = gl["amount"]                       # one column -> Series
print(amounts.head())

small = gl[["entry_id", "date", "amount"]]   # several columns -> DataFrame
print(small.head())                          # (note the DOUBLE brackets)


# ---------------------------------------------------------------
# 4. Column maths - works on the whole column at once!
# ---------------------------------------------------------------
# No loop needed. This is what makes pandas so fast and simple.
print("Total:", round(gl["amount"].sum(), 2))
print("Average:", round(gl["amount"].mean(), 2))
print("Median:", gl["amount"].median())
print("Largest:", gl["amount"].max())
print("Count:", gl["amount"].count())

# Make a new column (like adding a formula column in Excel)
gl["amount_with_vat"] = (gl["amount"] * 1.16).round(2)
gl["is_large"] = gl["amount"] >= 10000
print(gl[["amount", "amount_with_vat", "is_large"]].head())


# ---------------------------------------------------------------
# 5. Counting values
# ---------------------------------------------------------------
print("\nEntries per account:")
print(gl["account_name"].value_counts())

print("\nEntries per user:")
print(gl["posted_by"].value_counts())

print("\nUnique vendors:", gl["vendor_id"].nunique())


# ---------------------------------------------------------------
# 6. Sorting
# ---------------------------------------------------------------
top10 = gl.sort_values("amount", ascending=False).head(10)
print("\nTop 10 entries by amount:")
print(top10[["entry_id", "date", "account_name", "amount"]])


# ---------------------------------------------------------------
# 7. Selecting rows by position and by label
# ---------------------------------------------------------------
print(gl.iloc[0])          # row at position 0 (iloc = integer location)
print(gl.iloc[0:3])        # rows 0,1,2
print(gl.loc[5, "amount"]) # row with label 5, column "amount"


# ---------------------------------------------------------------
# 8. Dates - tell pandas the column is a date
# ---------------------------------------------------------------
gl["date"] = pd.to_datetime(gl["date"])
gl["month"] = gl["date"].dt.month         # 1..12
gl["day_name"] = gl["date"].dt.day_name() # Monday, Tuesday...
print(gl[["date", "month", "day_name"]].head())
print("First date:", gl["date"].min().date(), " Last date:", gl["date"].max().date())


# ===============================================================
# EXCEL  ->  PANDAS cheat sheet
#   Open file              pd.read_csv() / pd.read_excel()
#   Look at the top        df.head()
#   Count rows             len(df)  or  df.shape
#   =SUM(B:B)              df["col"].sum()
#   =AVERAGE(B:B)          df["col"].mean()
#   =COUNTIF               df["col"].value_counts()
#   Add formula column     df["new"] = df["a"] * df["b"]
#   Sort                   df.sort_values("col")
#
# NEXT: exercises/exercise05.py
# ===============================================================
