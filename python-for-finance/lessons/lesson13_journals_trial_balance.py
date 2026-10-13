"""
LESSON 13 - DOUBLE-ENTRY JOURNALS, TRIAL BALANCE and MANUAL JOURNAL TESTING
===========================================================================

Every accounting transaction is a JOURNAL with at least two LINES:
    DEBIT one account  and  CREDIT another account, for the SAME total.
    e.g. a sale on credit:   Dr Accounts Receivable 1,000
                             Cr Sales Revenue       1,000

Rules you must know:
  - In every journal:  total debits == total credits
  - Assets and expenses normally have DEBIT balances
  - Liabilities, equity and revenue normally have CREDIT balances
  - The TRIAL BALANCE (TB) lists every account's balance. Total debits on
    the TB must equal total credits. If not, something is broken.

Auditors also test MANUAL journals closely. Systems post routine entries
automatically; a person typing a journal by hand can override controls
("management override" - a fraud risk that auditing standards say we must
ALWAYS respond to).

Run:  python lessons/lesson13_journals_trial_balance.py
"""

from pathlib import Path
import pandas as pd

DATA = Path(__file__).parent.parent / "data"
OUTPUT = Path(__file__).parent.parent / "output"
OUTPUT.mkdir(exist_ok=True)
pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)

jl = pd.read_csv(DATA / "journal_lines.csv", parse_dates=["date"], dtype={"account": str})
jl[["debit", "credit"]] = jl[["debit", "credit"]].fillna(0)
jl["net"] = jl["debit"] - jl["credit"]          # debit = +, credit = -
print(jl.head(8).to_string(index=False))
print(f"\n{jl['journal_id'].nunique()} journals, {len(jl)} lines")


# ---------------------------------------------------------------
# STEP 1. Does every journal balance?
# ---------------------------------------------------------------
per_journal = jl.groupby("journal_id").agg(
    date=("date", "first"), description=("description", "first"),
    posted_by=("posted_by", "first"), source=("source", "first"),
    debits=("debit", "sum"), credits=("credit", "sum"))
per_journal["out_of_balance"] = (per_journal["debits"] - per_journal["credits"]).round(2)
unbalanced = per_journal[per_journal["out_of_balance"] != 0]
print("\nJOURNALS THAT DO NOT BALANCE:")
print(unbalanced.to_string())
# A good system should make this impossible. If you find one, the
# system control is not working - report it!


# ---------------------------------------------------------------
# STEP 2. Build the trial balance yourself
# ---------------------------------------------------------------
tb = jl.groupby(["account", "account_name"], as_index=False)["net"].sum()
tb["net"] = tb["net"].round(2)
tb["debit"] = tb["net"].where(tb["net"] > 0, 0)     # keep if > 0, else 0
tb["credit"] = (-tb["net"]).where(tb["net"] < 0, 0)
print("\nOUR TRIAL BALANCE")
print(tb[["account", "account_name", "debit", "credit"]].to_string(index=False))
print(f"Total debits  {tb['debit'].sum():,.2f}")
print(f"Total credits {tb['credit'].sum():,.2f}")
print(f"Difference    {tb['debit'].sum() - tb['credit'].sum():,.2f}"
      f"  (= sum of unbalanced journals {unbalanced['out_of_balance'].sum():,.2f})")


# ---------------------------------------------------------------
# STEP 3. Compare with the client's trial balance
# ---------------------------------------------------------------
client = pd.read_csv(DATA / "client_trial_balance.csv", dtype={"account": str})
client[["debit", "credit"]] = client[["debit", "credit"]].fillna(0)
client["net"] = client["debit"] - client["credit"]

cmp = tb[["account", "account_name", "net"]].merge(
    client[["account", "net"]], on="account", how="outer",
    suffixes=("_ours", "_client"), indicator=True)
cmp[["net_ours", "net_client"]] = cmp[["net_ours", "net_client"]].fillna(0)
cmp["difference"] = (cmp["net_ours"] - cmp["net_client"]).round(2)
print("\nOUR TB vs CLIENT TB - only the differences:")
print(cmp[cmp["difference"] != 0].to_string(index=False))


# ---------------------------------------------------------------
# STEP 4. From TB to financial statements
# ---------------------------------------------------------------
# The first digit of the account tells us the type (a "chart of accounts")
types = {"1": "Asset", "2": "Liability", "3": "Equity", "4": "Revenue",
         "5": "Expense", "6": "Expense", "7": "Expense", "9": "Suspense"}
tb["type"] = tb["account"].str[0].map(types)

revenue = -tb.loc[tb["type"] == "Revenue", "net"].sum()
expenses = tb.loc[tb["type"] == "Expense", "net"].sum()
profit = revenue - expenses
assets = tb.loc[tb["type"] == "Asset", "net"].sum()
liabilities = -tb.loc[tb["type"] == "Liability", "net"].sum()
equity = -tb.loc[tb["type"] == "Equity", "net"].sum()
suspense = tb.loc[tb["type"] == "Suspense", "net"].sum()

print(f"\nINCOME STATEMENT   Revenue {revenue:,.2f}   Expenses {expenses:,.2f}"
      f"   Profit {profit:,.2f}")
print(f"BALANCE SHEET      Assets {assets:,.2f} = Liabilities {liabilities:,.2f}"
      f" + Equity {equity:,.2f} + Profit {profit:,.2f}")
gap = assets - (liabilities + equity + profit)
print(f"Accounting equation gap: {gap:,.2f}")
# Why? The gap = the unbalanced journals + the suspense balance (which is
# not an asset, liability, equity, revenue or expense):
print(f"  unbalanced journals {unbalanced['out_of_balance'].sum():,.2f}"
      f" + suspense credit {-suspense:,.2f} = {unbalanced['out_of_balance'].sum() - suspense:,.2f}")


# ---------------------------------------------------------------
# STEP 5. Accounts with the "wrong" side balance
# ---------------------------------------------------------------
# e.g. a CREDIT balance on an asset = money we owe ourselves?? Investigate.
normal_debit = tb["type"].isin(["Asset", "Expense"])
wrong_side = tb[(normal_debit & (tb["net"] < 0)) | (~normal_debit & (tb["net"] > 0)
                                                     & (tb["type"] != "Suspense"))]
print("\nAccounts with an unusual-side balance:", wrong_side["account_name"].tolist() or "none")
print("Suspense account balance:", f"{suspense:,.2f}",
      "-> must be cleared before year end!" if suspense else "")


# ---------------------------------------------------------------
# STEP 6. Roll-forward of receivables (does the movement make sense?)
# ---------------------------------------------------------------
ar = jl[jl["account"] == "1100"]
invoiced = ar["debit"].sum()
received = ar["credit"].sum()
print(f"\nRECEIVABLES ROLL-FORWARD:  opening 0 + invoiced {invoiced:,.2f}"
      f" - received {received:,.2f} = closing {invoiced - received:,.2f}")
print(f"Debtor days: {(invoiced - received) / revenue * 365:.0f} days")


# ---------------------------------------------------------------
# STEP 7. MANUAL JOURNAL TESTING (management override)
# ---------------------------------------------------------------
manual = per_journal[per_journal["source"] == "manual"].copy()
print(f"\nManual journals: {len(manual)} of {len(per_journal)}")

keywords = "adjust|reclass|confidential|per ceo|correction|difference|unknown"
suspense_ids = set(jl.loc[jl["account"] == "9999", "journal_id"])
manual["flag_year_end"] = manual["date"] >= "2025-12-24"
manual["flag_weekend"] = manual["date"].dt.dayofweek >= 5
manual["flag_keyword"] = manual["description"].str.contains(keywords, case=False)
manual["flag_senior"] = manual["posted_by"].isin(["ceo", "cfo"])
manual["flag_large"] = manual["debits"] >= 20000
manual["flag_suspense"] = manual.index.isin(suspense_ids)
manual["flag_unbalanced"] = manual["out_of_balance"] != 0
flag_cols = [c for c in manual.columns if c.startswith("flag_")]
manual["risk_score"] = manual[flag_cols].sum(axis=1)   # count of True flags
print(manual.sort_values("risk_score", ascending=False)
      [["date", "description", "posted_by", "debits", "risk_score"]].to_string())


# ---------------------------------------------------------------
# STEP 8. Unusual account combinations
# ---------------------------------------------------------------
# Which account is debited together with which account credited?
# Common pairs are normal. RARE pairs need a look.
# (We leave out the opening balances journal - it is a one-off set-up.)
normal = jl[jl["description"] != "Opening balances"]
dr = normal[normal["debit"] > 0][["journal_id", "account_name"]]
cr = normal[normal["credit"] > 0][["journal_id", "account_name"]]
pairs = dr.merge(cr, on="journal_id", suffixes=("_dr", "_cr"))
pair_counts = pairs.groupby(["account_name_dr", "account_name_cr"]).size() \
                   .sort_values().rename("times")
print("\nRAREST account pairs (debit -> credit):")
print(pair_counts.head(6).to_string())
# "Dr Equipment / Cr Salaries" = moving salary costs onto the balance
# sheet. That makes profit look better. A classic red flag!

with pd.ExcelWriter(OUTPUT / "journals_tb_workpaper.xlsx") as w:
    tb.to_excel(w, sheet_name="Our TB", index=False)
    cmp.to_excel(w, sheet_name="TB comparison", index=False)
    unbalanced.to_excel(w, sheet_name="Unbalanced journals")
    manual.sort_values("risk_score", ascending=False).to_excel(w, sheet_name="Manual journals")
    pair_counts.reset_index().to_excel(w, sheet_name="Account pairs", index=False)
print("\nSaved output/journals_tb_workpaper.xlsx")


# ===============================================================
# SUMMARY
#   jl.groupby("journal_id")[["debit","credit"]].sum()  -> every journal balances?
#   groupby account -> net -> debit / credit columns    -> your own TB
#   merge with the client's TB                          -> differences
#   first digit of account -> type -> IS and BS        -> A = L + E + profit
#   Suspense must be zero at year end
#   Manual journals: year end, weekend, keywords, senior people, large,
#   suspense, unbalanced -> add the flags to get a risk score
#   Rare debit/credit account pairs -> red flags
#
# PRACTICE: practice/02_journals_and_trial_balance.py
# ===============================================================
