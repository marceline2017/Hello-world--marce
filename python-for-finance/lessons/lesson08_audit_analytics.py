"""
LESSON 8 - AUDIT ANALYTICS: finding red flags in a ledger
=========================================================

This is where Python becomes a super-power for an auditor.
Instead of checking a SAMPLE of 25 entries, you test 100% of them.

Our general ledger has some problems hidden inside on purpose.
Each test below is a real test used by internal and external auditors
(often called "journal entry testing" or "JET").

IMPORTANT: a red flag is NOT proof of fraud. It is a question to ask.
Every exception needs follow-up: look at the invoice, ask the person.

Run:  python lessons/lesson08_audit_analytics.py
"""

from pathlib import Path
import pandas as pd

DATA = Path(__file__).parent.parent / "data"
OUTPUT = Path(__file__).parent.parent / "output"
OUTPUT.mkdir(exist_ok=True)
pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)

gl = pd.read_csv(DATA / "general_ledger.csv", parse_dates=["date"],
                 dtype={"account": str})
vendors = pd.read_csv(DATA / "vendors.csv")
gl["approved_by"] = gl["approved_by"].fillna("")
gl["vendor_id"] = gl["vendor_id"].fillna("")

APPROVAL_LIMIT = 10000
COLS = ["entry_id", "date", "account_name", "vendor_id", "amount",
        "posted_by", "approved_by"]

# We collect every exception in one list, then save one report.
all_exceptions = []

def report(test_name, rows, why):
    """Print a test result and remember the exceptions."""
    print(f"\n{'=' * 70}\nTEST: {test_name}\nWHY:  {why}")
    print(f"RESULT: {len(rows)} exception(s)")
    if len(rows):
        print(rows[COLS].to_string(index=False))
        flagged = rows[COLS].copy()
        flagged["test"] = test_name
        all_exceptions.append(flagged)


# ---------------------------------------------------------------
# STEP 0. Completeness - does our data agree with the client's total?
# ---------------------------------------------------------------
# Before ANY testing, confirm you have ALL the data. Compare row count
# and total with the client's report (here we just print them).
print(f"Rows: {len(gl)}   Total amount: {gl['amount'].sum():,.2f}")
print(f"Period: {gl['date'].min().date()} to {gl['date'].max().date()}")


# ---------------------------------------------------------------
# TEST 1. Duplicate payments
# ---------------------------------------------------------------
dup_keys = ["vendor_id", "amount", "date"]
paid = gl[gl["vendor_id"] != ""]
dups = paid[paid.duplicated(subset=dup_keys, keep=False)].sort_values(dup_keys)
report("Duplicate payments", dups,
       "Same vendor, same amount, same day may mean we paid twice.")


# ---------------------------------------------------------------
# TEST 2. Weekend postings
# ---------------------------------------------------------------
# .dt.dayofweek: Monday=0 ... Saturday=5, Sunday=6
weekend = gl[gl["date"].dt.dayofweek >= 5]
report("Weekend postings", weekend,
       "Entries made when the office is closed are unusual.")


# ---------------------------------------------------------------
# TEST 3. Large entries without approval
# ---------------------------------------------------------------
no_approval = gl[(gl["amount"] >= APPROVAL_LIMIT) & (gl["approved_by"] == "")]
report("Above limit, not approved", no_approval,
       f"Policy: every entry of {APPROVAL_LIMIT:,} or more needs approval.")


# ---------------------------------------------------------------
# TEST 4. Self-approval (segregation of duties)
# ---------------------------------------------------------------
self_approved = gl[(gl["approved_by"] != "") & (gl["approved_by"] == gl["posted_by"])]
report("Self-approved entries", self_approved,
       "The same person should not both post and approve.")


# ---------------------------------------------------------------
# TEST 5. Just below the approval limit (split transactions)
# ---------------------------------------------------------------
just_below = gl[gl["amount"].between(APPROVAL_LIMIT * 0.95, APPROVAL_LIMIT - 0.01)]
report("Just below approval limit", just_below,
       "Amounts slightly under the limit may be split to avoid approval.")


# ---------------------------------------------------------------
# TEST 6. Round amounts
# ---------------------------------------------------------------
round_amts = gl[(gl["amount"] % 1000 == 0) & (gl["amount"] > 0)]
report("Round thousand amounts", round_amts,
       "Real invoices rarely total exactly 5,000.00 - estimates or made-up?")


# ---------------------------------------------------------------
# TEST 7. Payments to blocked / unknown vendors
# ---------------------------------------------------------------
with_status = gl.merge(vendors, on="vendor_id", how="left")
blocked = with_status[with_status["status"] == "Blocked"]
report("Payments to blocked vendors", blocked,
       "A blocked supplier should never receive money.")


# ---------------------------------------------------------------
# TEST 8. Gaps in the entry number sequence (completeness)
# ---------------------------------------------------------------
ids = sorted(gl["entry_id"])
expected = set(range(ids[0], ids[-1] + 1))
missing_ids = sorted(expected - set(ids))
print(f"\n{'=' * 70}\nTEST: Gaps in entry numbers")
print("WHY:  Missing numbers may mean deleted entries.")
print(f"RESULT: missing entry IDs: {missing_ids}")


# ---------------------------------------------------------------
# TEST 9. Outliers - amounts far from normal FOR THAT ACCOUNT
# ---------------------------------------------------------------
# z-score = how many "standard deviations" away from the average.
# Above 3 is very unusual.
grp = gl.groupby("account_name")["amount"]
gl["z_score"] = (gl["amount"] - grp.transform("mean")) / grp.transform("std")
outliers = gl[gl["z_score"].abs() > 3]
report("Statistical outliers (z > 3)", outliers,
       "Amounts very different from the usual size for their account.")


# ---------------------------------------------------------------
# TEST 10. Benford's Law - the first-digit test
# ---------------------------------------------------------------
# In natural financial data, the FIRST digit is "1" about 30% of the time,
# "2" about 18%, ... "9" only about 5%. Made-up numbers often break this.
# Expected % for digit d = log10(1 + 1/d)
import math

first_digit = gl["amount"].astype(str).str.lstrip("0.").str[0].astype(int)
actual = first_digit.value_counts(normalize=True).sort_index()
benford = pd.DataFrame({
    "actual_%": (actual * 100).round(1),
    "expected_%": [round(math.log10(1 + 1 / d) * 100, 1) for d in actual.index],
})
benford["difference"] = benford["actual_%"] - benford["expected_%"]
print(f"\n{'=' * 70}\nTEST: Benford's Law first-digit analysis")
print(benford)
print("HOW TO READ IT: differences of 1-2 points are normal. A digit that is")
print("much too common (e.g. lots of 9s from amounts just under a limit)")
print("is a reason to look closer. Benford needs lots of data (500+ rows)")
print("and does not work for fixed-price items or amounts with a set range.")


# ---------------------------------------------------------------
# FINAL: one exceptions report for the audit file
# ---------------------------------------------------------------
exceptions = pd.concat(all_exceptions, ignore_index=True)
summary = exceptions.groupby("test").agg(count=("entry_id", "count"),
                                          value=("amount", "sum"))
print(f"\n{'=' * 70}\nEXCEPTIONS SUMMARY")
print(summary.round(2))

out_file = OUTPUT / "audit_exceptions.xlsx"
with pd.ExcelWriter(out_file) as writer:
    summary.to_excel(writer, sheet_name="Summary")
    exceptions.to_excel(writer, sheet_name="Detail", index=False)
    benford.to_excel(writer, sheet_name="Benford")
print(f"\nSaved {out_file.name} - open it in Excel!")


# ===============================================================
# THE AUDITOR'S JET CHECKLIST
#   1. Completeness: rows and totals agree to the client's report
#   2. Duplicates               6. Round amounts
#   3. Weekend / holiday dates  7. Blocked / unknown vendors
#   4. Approval over the limit  8. Sequence gaps
#   5. Self-approval / SoD      9. Outliers   10. Benford
#   Then: document, follow up, conclude.
#
# NEXT: exercises/exercise08.py
# ===============================================================
