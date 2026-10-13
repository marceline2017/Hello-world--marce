"""
CAPSTONE SOLUTION - Year-end ledger review for Sunrise Trading Ltd.

One possible answer to capstone/PROJECT_BRIEF.md. Read the brief first!
Run:  python capstone/capstone_solution.py
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DATA = Path(__file__).parent.parent / "data"
OUTPUT = Path(__file__).parent.parent / "output"
OUTPUT.mkdir(exist_ok=True)
APPROVAL_LIMIT = 10000

# ---------------------------------------------------------------
# 1. Load and check completeness
# ---------------------------------------------------------------
gl = pd.read_csv(DATA / "general_ledger.csv", dtype={"account": str})
vendors = pd.read_csv(DATA / "vendors.csv")
rows_in, total_in = len(gl), gl["amount"].sum()
print(f"Loaded {rows_in} rows, total {total_in:,.2f}")

repeated_ids = gl["entry_id"][gl["entry_id"].duplicated()].tolist()
all_ids = set(range(gl["entry_id"].min(), gl["entry_id"].max() + 1))
missing_ids = sorted(all_ids - set(gl["entry_id"]))
print("Repeated IDs:", repeated_ids, "| Missing IDs:", missing_ids)

# ---------------------------------------------------------------
# 2. Clean
# ---------------------------------------------------------------
gl["date"] = pd.to_datetime(gl["date"])
gl["approved_by"] = gl["approved_by"].fillna("")
gl["vendor_id"] = gl["vendor_id"].fillna("")
gl = gl.merge(vendors, on="vendor_id", how="left")
assert len(gl) == rows_in and round(gl["amount"].sum(), 2) == round(total_in, 2), \
    "Cleaning changed the data!"   # assert = stop if this is not true
print(f"Period {gl['date'].min().date()} to {gl['date'].max().date()}")

# ---------------------------------------------------------------
# 3. Analytical review
# ---------------------------------------------------------------
gl["type"] = gl["account"].str[0].map({"4": "Revenue"}).fillna("Expense")
gl["month"] = gl["date"].dt.month
monthly = gl.pivot_table(index="month", columns="type", values="amount", aggfunc="sum")
monthly["Profit"] = monthly["Revenue"] - monthly["Expense"]

revenue = monthly["Revenue"].sum()
expenses = monthly["Expense"].sum()
profit = revenue - expenses
materiality = 0.05 * profit
print(f"Revenue {revenue:,.0f}  Expenses {expenses:,.0f}  "
      f"Profit {profit:,.0f}  Margin {profit / revenue:.1%}")
print(f"Materiality (5% of profit): {materiality:,.0f}")
worst = monthly["Profit"].idxmin()
print(f"Weakest month: {worst} (profit {monthly.loc[worst, 'Profit']:,.0f})")

# ---------------------------------------------------------------
# 4. Audit tests - each returns the rows that fail
# ---------------------------------------------------------------
grp = gl.groupby("account_name")["amount"]
z = (gl["amount"] - grp.transform("mean")) / grp.transform("std")
supplier = gl["vendor_id"] != ""

tests = {
    # Same vendor, amount and date -> may be paid twice
    "Duplicate payment": supplier & gl.duplicated(["vendor_id", "amount", "date"], keep=False),
    # Office is closed at weekends
    "Weekend posting": gl["date"].dt.dayofweek >= 5,
    # Policy: approval needed at or above the limit
    "No approval over limit": (gl["amount"] >= APPROVAL_LIMIT) & (gl["approved_by"] == ""),
    # Segregation of duties
    "Self-approved": (gl["approved_by"] != "") & (gl["approved_by"] == gl["posted_by"]),
    # Possible split to avoid approval
    "Just below limit": gl["amount"].between(APPROVAL_LIMIT * 0.95, APPROVAL_LIMIT - 0.01),
    # Supplier should not be paid at all
    "Blocked vendor": gl["status"] == "Blocked",
    # Real invoices are rarely round
    "Round amount": (gl["amount"] % 1000 == 0),
    # Unusual size for the account
    "Outlier (z>3)": z.abs() > 3,
}

pieces = []
for name, mask in tests.items():
    hits = gl.loc[mask, ["entry_id", "date", "account_name", "vendor_name",
                         "amount", "posted_by", "approved_by"]].copy()
    hits["test"] = name
    pieces.append(hits)
exceptions = pd.concat(pieces, ignore_index=True)

summary = (exceptions.groupby("test")
           .agg(exceptions=("entry_id", "count"), value=("amount", "sum"))
           .sort_values("exceptions", ascending=False))
print("\n", summary.round(2))

# ---------------------------------------------------------------
# 5. Rank the risk
# ---------------------------------------------------------------
top = (exceptions.groupby("entry_id")
       .agg(tests_failed=("test", "count"),
            which_tests=("test", ", ".join),
            amount=("amount", "first"),
            posted_by=("posted_by", "first"))
       .sort_values(["tests_failed", "amount"], ascending=False)
       .reset_index())
top["above_materiality"] = top["amount"] >= materiality
print("\nTop risks:\n", top.head(10).to_string(index=False))

# ---------------------------------------------------------------
# 6. Report
# ---------------------------------------------------------------
with pd.ExcelWriter(OUTPUT / "capstone_report.xlsx") as w:
    summary.to_excel(w, sheet_name="Summary")
    exceptions.to_excel(w, sheet_name="Exceptions", index=False)
    top.to_excel(w, sheet_name="Top risks", index=False)
    monthly.round(2).to_excel(w, sheet_name="Monthly")

fig, ax = plt.subplots(figsize=(8, 4))
s = summary["exceptions"].sort_values()
bars = ax.barh(s.index, s.values, color="#2a78d6", height=0.6)
ax.bar_label(bars, padding=4)
ax.set_title("Exceptions found per audit test, FY2025", loc="left")
for side in ["top", "right"]:
    ax.spines[side].set_visible(False)
fig.tight_layout()
fig.savefig(OUTPUT / "capstone_chart.png", dpi=150)
plt.close(fig)

multi = top[top["tests_failed"] > 1]
memo = f"""AUDIT MEMO - Sunrise Trading Ltd - General ledger review FY2025

Scope: all {rows_in:,} entries ({total_in:,.2f}) from {gl['date'].min().date()} to {gl['date'].max().date()}.
Materiality: {materiality:,.0f} (5% of profit of {profit:,.0f}).
Completeness: {len(missing_ids)} entry numbers missing from the sequence {missing_ids}.

We ran {len(tests)} automated tests and found {len(exceptions)} exceptions on {len(top)} entries.
Most common: {summary.index[0]} ({int(summary.iloc[0]['exceptions'])} entries).
{len(multi)} entries failed more than one test - these are the highest risk.
Payments to the blocked vendor: {int(tests['Blocked vendor'].sum())}.

Recommendations:
- Obtain support (invoice, approval) for every entry on the "Top risks" sheet.
- Ask management to explain the missing entry numbers and blocked-vendor payments.
- Enforce system approval for amounts >= {APPROVAL_LIMIT:,} and block self-approval.
"""
(OUTPUT / "capstone_memo.txt").write_text(memo)
print("\n" + memo)
print("Saved capstone_report.xlsx, capstone_chart.png and capstone_memo.txt")
