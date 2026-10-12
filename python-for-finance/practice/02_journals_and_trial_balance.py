"""
PRACTICE SET 2 - JOURNALS and TRIAL BALANCE (18 tasks)
Files: data/journal_lines.csv, data/client_trial_balance.csv
Lesson needed first: 13

HOW TO USE: write your code under each TODO, then run this file:
    python practice/02_journals_and_trial_balance.py
Stuck? Compare with practice/solutions/02_journals_and_trial_balance.py - but try first!
The setup code below is already done for you.
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
# TODO


# TASK 2: Do total debits equal total credits for the WHOLE file?
# TODO


# TASK 3: List every journal that does not balance, with the difference.
# TODO


# TASK 4: Build the trial balance: one row per account with debit and credit columns.
# TODO


# TASK 5: Compare your TB with data/client_trial_balance.csv. Which accounts differ
# and by how much?
# TODO


# TASK 6: Calculate revenue, cost of goods sold, gross profit and GROSS MARGIN %.
# TODO


# TASK 7: Monthly revenue from the journals (remember revenue is a CREDIT).
# TODO


# TASK 8: Cash account (1000): total money in, total money out, closing balance,
# and the LOWEST month-end balance during the year.
# TODO


# TASK 9: INVENTORY roll-forward: purchases in, cost of sales out, closing balance.
# Then inventory days = closing inventory / COGS x 365.
# TODO


# TASK 10: PAYABLES roll-forward and creditor days (closing AP / purchases x 365).
# TODO


# TASK 11: How many journals are MANUAL? What % of all journals is that?
# TODO


# TASK 12: Count manual journals per user. Is one person doing most of them?
# TODO


# TASK 13: Find journals whose description contains a risky word:
# adjust, reclass, confidential, difference, unknown (any capitals).
# TODO


# TASK 14: Which journals touch the Suspense account (9999)? What is its balance?
# TODO


# TASK 15: REPERFORM DEPRECIATION. Equipment cost 200,000 with a 5-year life and no
# salvage value. Expected monthly charge = 200,000 / 60. Was it posted every month,
# and is the yearly total right?
# TODO


# TASK 16: COMPLETENESS of recurring journals. Rent and salaries should be posted
# exactly ONCE every month. Check both.
# TODO


# TASK 17: Salaries expense per the TB is lower than 12 x monthly salaries. Find
# the journal(s) that CREDIT salaries and explain what they did.
# TODO


# TASK 18: Save output/p2_journals.xlsx with your TB, the comparison and the
# unbalanced journals.
# TODO
