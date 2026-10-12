"""
PRACTICE SET 2 - JOURNALS and TRIAL BALANCE (18 tasks)
Files: data/journal_lines.csv, data/client_trial_balance.csv
Lesson needed first: 13
"""

from pathlib import Path
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "data").is_dir())
DATA, OUTPUT = ROOT / "data", ROOT / "output"
OUTPUT.mkdir(exist_ok=True)
pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)

jl = pd.read_csv(DATA / "journal_lines.csv", parse_dates=["date"], dtype={"account": str})
jl[["debit", "credit"]] = jl[["debit", "credit"]].fillna(0)
jl["net"] = jl["debit"] - jl["credit"]
jl["month"] = jl["date"].dt.month

# TASK 1: (Warm-up) How many journals and lines are there? How many journals have
# 2 lines, 3 lines, 4 lines...?
print(jl["journal_id"].nunique(), len(jl))
print(jl.groupby("journal_id").size().value_counts().sort_index())

# TASK 2: Do total debits equal total credits for the WHOLE file?
print(f"Debits {jl['debit'].sum():,.2f}  Credits {jl['credit'].sum():,.2f}")

# TASK 3: List every journal that does not balance, with the difference.
diff = jl.groupby("journal_id")["net"].sum().round(2)
print(diff[diff != 0])

# TASK 4: Build the trial balance: one row per account with debit and credit columns.
tb = jl.groupby(["account", "account_name"], as_index=False)["net"].sum().round(2)
tb["debit"] = tb["net"].clip(lower=0)          # clip = cut off below 0
tb["credit"] = (-tb["net"]).clip(lower=0)
print(tb.to_string(index=False))

# TASK 5: Compare your TB with data/client_trial_balance.csv. Which accounts differ
# and by how much?
client = pd.read_csv(DATA / "client_trial_balance.csv", dtype={"account": str}).fillna(0)
client["net"] = client["debit"] - client["credit"]
cmp = tb.merge(client[["account", "net"]], on="account", how="left",
               suffixes=("_ours", "_client")).fillna({"net_client": 0})
cmp["difference"] = (cmp["net_ours"] - cmp["net_client"]).round(2)
print(cmp.loc[cmp["difference"] != 0, ["account_name", "net_ours", "net_client", "difference"]])

# TASK 6: Calculate revenue, cost of goods sold, gross profit and GROSS MARGIN %.
revenue = -tb.loc[tb["account"] == "4000", "net"].sum()
cogs = tb.loc[tb["account"] == "5000", "net"].sum()
print(f"Revenue {revenue:,.0f}  COGS {cogs:,.0f}  GP {revenue - cogs:,.0f}"
      f"  GM {(revenue - cogs) / revenue:.1%}")

# TASK 7: Monthly revenue from the journals (remember revenue is a CREDIT).
print((-jl[jl["account"] == "4000"].groupby("month")["net"].sum()).round(0))

# TASK 8: Cash account (1000): total money in, total money out, closing balance,
# and the LOWEST month-end balance during the year.
cash = jl[jl["account"] == "1000"].sort_values("date")
print(f"In {cash['debit'].sum():,.2f}  Out {cash['credit'].sum():,.2f}"
      f"  Closing {cash['net'].sum():,.2f}")
month_end_cash = cash.groupby("month")["net"].sum().cumsum()
print("Lowest month-end cash:", round(month_end_cash.min(), 2), "in month", month_end_cash.idxmin())

# TASK 9: INVENTORY roll-forward: purchases in, cost of sales out, closing balance.
# Then inventory days = closing inventory / COGS x 365.
inv = jl[jl["account"] == "1200"]
closing_inv = inv["net"].sum()
print(f"Purchases {inv['debit'].sum():,.0f}  Used {inv['credit'].sum():,.0f}"
      f"  Closing {closing_inv:,.0f}  Days {closing_inv / cogs * 365:.0f}")

# TASK 10: PAYABLES roll-forward and creditor days (closing AP / purchases x 365).
ap = jl[jl["account"] == "2000"]
closing_ap = -ap["net"].sum()
purchases = ap["credit"].sum()
print(f"Invoices {purchases:,.0f}  Paid {ap['debit'].sum():,.0f}  Closing {closing_ap:,.0f}"
      f"  Creditor days {closing_ap / purchases * 365:.0f}")

# TASK 11: How many journals are MANUAL? What % of all journals is that?
src = jl.drop_duplicates("journal_id")["source"].value_counts()
print(src, f"\nManual share: {src.get('manual', 0) / src.sum():.1%}")

# TASK 12: Count manual journals per user. Is one person doing most of them?
print(jl[jl["source"] == "manual"].drop_duplicates("journal_id")["posted_by"].value_counts())

# TASK 13: Find journals whose description contains a risky word:
# adjust, reclass, confidential, difference, unknown (any capitals).
words = "adjust|reclass|confidential|difference|unknown"
print(jl[jl["description"].str.contains(words, case=False)]
        .drop_duplicates("journal_id")[["journal_id", "date", "description", "posted_by"]])

# TASK 14: Which journals touch the Suspense account (9999)? What is its balance?
susp = jl[jl["account"] == "9999"]
print(susp[["journal_id", "date", "description", "debit", "credit"]], "\nBalance:", susp["net"].sum())

# TASK 15: REPERFORM DEPRECIATION. Equipment cost 200,000 with a 5-year life and no
# salvage value. Expected monthly charge = 200,000 / 60. Was it posted every month,
# and is the yearly total right?
expected_month = round(200000 / 60, 2)
dep = jl[jl["account"] == "6800"].groupby("month")["net"].sum()
print("Months posted:", len(dep), " All correct:", (dep.round(2) == expected_month).all())
print(f"Expected year {expected_month * 12:,.2f}  Actual {dep.sum():,.2f}")

# TASK 16: COMPLETENESS of recurring journals. Rent and salaries should be posted
# exactly ONCE every month. Check both.
for desc in ["Monthly rent", "Monthly salaries"]:
    per_month = jl[(jl["description"] == desc) & (jl["debit"] > 0)].groupby("month").size()
    print(desc, "-> months:", len(per_month), " any month twice:", (per_month > 1).any())

# TASK 17: Salaries expense per the TB is lower than 12 x monthly salaries. Find
# the journal(s) that CREDIT salaries and explain what they did.
print(jl[(jl["account"] == "6200") & (jl["credit"] > 0)]
        [["journal_id", "date", "description", "credit", "posted_by"]])
# Answer: J0245 moved 22,000 of salary cost to Equipment (an asset).
# That increases profit by 22,000 - possible profit manipulation.

# TASK 18: Save output/p2_journals.xlsx with your TB, the comparison and the
# unbalanced journals.
with pd.ExcelWriter(OUTPUT / "p2_journals.xlsx") as w:
    tb.to_excel(w, sheet_name="TB", index=False)
    cmp.to_excel(w, sheet_name="TB vs client", index=False)
    diff[diff != 0].to_excel(w, sheet_name="Unbalanced")
print("Saved output/p2_journals.xlsx")
