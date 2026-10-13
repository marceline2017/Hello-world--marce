"""
PRACTICE SET 1 - GENERAL LEDGER ANALYSIS (25 tasks)
Files: data/general_ledger.csv, data/vendors.csv
Lessons needed first: 5, 6, 7, 8
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
print(gl.shape, gl["date"].min().date(), gl["date"].max().date())

# TASK 2: For each account_name show the number of entries and the total amount,
# sorted by total (largest first).
print(gl.groupby("account_name")["amount"].agg(["count", "sum"])
        .sort_values("sum", ascending=False).round(2))

# TASK 3: Which account has the largest AVERAGE entry size?
avg = gl.groupby("account_name")["amount"].mean()
print(avg.idxmax(), round(avg.max(), 2))

# TASK 4: Show the 10 largest entries (entry_id, date, account_name, amount).
print(gl.nlargest(10, "amount")[["entry_id", "date", "account_name", "amount"]])

# TASK 5: Monthly Sales Revenue. Which month was best and which was worst?
sales = gl[gl["account_name"] == "Sales Revenue"].groupby("month")["amount"].sum()
print(sales.round(0))
print("Best month:", sales.idxmax(), " Worst month:", sales.idxmin())

# TASK 6: What % of total EXPENSES (every account except Sales Revenue) does
# each expense account make up?
exp = gl[gl["account_name"] != "Sales Revenue"].groupby("account_name")["amount"].sum()
print((exp / exp.sum() * 100).round(1).sort_values(ascending=False))

# TASK 7: Make a table of revenue and expenses per QUARTER, plus profit.
gl["quarter"] = gl["date"].dt.quarter
gl["type"] = gl["account"].str.startswith("4").map({True: "Revenue", False: "Expense"})
q = gl.pivot_table(index="quarter", columns="type", values="amount", aggfunc="sum")
q["Profit"] = q["Revenue"] - q["Expense"]
print(q.round(0))

# TASK 8: Pivot: number of entries per user (rows) per month (columns).
print(gl.pivot_table(index="posted_by", columns="month", values="entry_id",
                     aggfunc="count", fill_value=0))

# TASK 9: Which user posted the highest TOTAL value? Show total and average per user.
print(gl.groupby("posted_by")["amount"].agg(["sum", "mean"]).sort_values("sum").round(2))

# TASK 10: Spend per vendor NAME (merge with vendors). What % of all vendor spend
# goes to the biggest vendor? (This is called "supplier concentration".)
spend = gl.merge(vendors, on="vendor_id").groupby("vendor_name")["amount"].sum() \
          .sort_values(ascending=False)
print(spend.round(2))
print(f"Biggest vendor share: {spend.iloc[0] / spend.sum():.1%}")

# TASK 11: Which accounts are paid to MORE than one vendor? (A rent account paid
# to two landlords would be strange.)
n_vendors = gl[gl["vendor_id"] != ""].groupby("account_name")["vendor_id"].nunique()
print(n_vendors[n_vendors > 1] if (n_vendors > 1).any() else "Each account has one vendor")

# TASK 12: How many entries were posted in the LAST 3 DAYS of each month?
# (Month-end rush = higher risk of errors.)
gl["days_to_month_end"] = gl["date"].dt.days_in_month - gl["date"].dt.day
month_end = gl[gl["days_to_month_end"] < 3]
print(month_end.groupby("month").size())

# TASK 13: How many entries were posted on each day of the week? Put the days
# in order Monday -> Sunday.
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
print(gl["date"].dt.day_name().value_counts().reindex(order, fill_value=0))

# TASK 14: How many entries have NO cents (e.g. 5000.00)? Show them per user.
no_cents = gl[(gl["amount"] * 100).round() % 100 == 0]
print(len(no_cents), no_cents["posted_by"].value_counts().to_dict())

# TASK 15: Which exact amounts appear MORE THAN ONCE? Show the amount, how many
# times, and the entry_ids.
rep = gl[gl.duplicated("amount", keep=False)].groupby("amount")["entry_id"].agg(["count", list])
print(rep)

# TASK 16: (Challenge) Near-duplicates: same vendor and same amount within 7 days,
# but NOT on the same day. Hint: sort by vendor, amount, date and use .diff().
v = gl[gl["vendor_id"] != ""].sort_values(["vendor_id", "amount", "date"]).copy()
v["days_since_same"] = v.groupby(["vendor_id", "amount"])["date"].diff().dt.days
near = v[(v["days_since_same"] > 0) & (v["days_since_same"] <= 7)]
print(near[["entry_id", "date", "vendor_id", "amount", "days_since_same"]])
# These are the SECOND payments. Find the first one: same vendor and amount.

# TASK 17: What % of entries of 10,000 or more were approved by someone?
big = gl[gl["amount"] >= 10000]
print(f"Approval coverage: {(big['approved_by'] != '').mean():.1%} of {len(big)} entries")

# TASK 18: Who approves whom? Make a crosstab of posted_by (rows) vs approved_by
# (columns) for approved entries. The diagonal = self-approval.
appr = gl[gl["approved_by"] != ""]
print(pd.crosstab(appr["posted_by"], appr["approved_by"]))

# TASK 19: List the missing numbers in the entry_id sequence.
ids = gl["entry_id"]
print(sorted(set(range(ids.min(), ids.max() + 1)) - set(ids)))

# TASK 20: STRATIFICATION. Put every entry in a size band:
# 0-1k, 1k-5k, 5k-10k, 10k-20k, 20k+ and show count, total value and % of value.
bands = pd.cut(gl["amount"], bins=[0, 1000, 5000, 10000, 20000, float("inf")],
               labels=["0-1k", "1k-5k", "5k-10k", "10k-20k", "20k+"])
strat = gl.groupby(bands, observed=False)["amount"].agg(["count", "sum"])
strat["%_of_value"] = (strat["sum"] / strat["sum"].sum() * 100).round(1)
print(strat.round(0))

# TASK 21: COVERAGE. If you test only the 50 largest entries, what % of the total
# value do you cover?
print(f"{gl.nlargest(50, 'amount')['amount'].sum() / gl['amount'].sum():.1%}")

# TASK 22: SAMPLE SELECTION. Pick ALL "key items" (amount >= 20,000) plus a random
# sample of 25 from the rest (use random_state=1 so it is repeatable).
key_items = gl[gl["amount"] >= 20000]
random_items = gl[gl["amount"] < 20000].sample(25, random_state=1)
sample = pd.concat([key_items.assign(reason="key item"),
                    random_items.assign(reason="random")])
print(sample["reason"].value_counts())
sample.to_csv(OUTPUT / "p1_sample.csv", index=False)

# TASK 23: CUT-OFF. List every entry dated in the last 5 days of the year.
print(gl[gl["date"] >= "2025-12-27"][["entry_id", "date", "account_name", "amount",
                                       "posted_by"]].to_string(index=False))

# TASK 24: (Challenge) RELATIVE SIZE FACTOR. For each vendor, divide the largest
# entry by the second largest. A factor above 2 means one entry is much bigger
# than normal for that vendor.
def rsf(amounts):
    top2 = amounts.nlargest(2)
    return top2.iloc[0] / top2.iloc[1] if len(top2) == 2 else None

factor = gl[gl["vendor_id"] != ""].groupby("vendor_id")["amount"].apply(rsf)
print(factor.round(2).sort_values(ascending=False))

# TASK 25: Save an Excel file output/p1_gl_analysis.xlsx with sheets for
# your stratification (task 20), approvals crosstab (task 18) and sample (task 22).
with pd.ExcelWriter(OUTPUT / "p1_gl_analysis.xlsx") as w:
    strat.to_excel(w, sheet_name="Stratification")
    pd.crosstab(appr["posted_by"], appr["approved_by"]).to_excel(w, sheet_name="Approvals")
    sample.to_excel(w, sheet_name="Sample", index=False)
print("Saved output/p1_gl_analysis.xlsx")
