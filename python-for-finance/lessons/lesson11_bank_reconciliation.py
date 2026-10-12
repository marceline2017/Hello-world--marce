"""
LESSON 11 - REPERFORMING A BANK RECONCILIATION
==============================================

WHAT IS A BANK RECONCILIATION?
The company keeps its own record of the bank account (the CASH BOOK).
The bank sends its record (the BANK STATEMENT). At month end the two
balances are almost never the same. A bank reconciliation explains WHY.

Differences come in two kinds:
  1. TIMING  - both are right, one is just "late"
       - Outstanding cheques: we wrote the cheque, the bank hasn't paid it yet
       - Deposits in transit: we banked money on 31 Dec, the bank shows it in Jan
  2. NOT YET RECORDED IN THE CASH BOOK - the bank knows, we don't (yet)
       - bank charges, interest, direct debits, returned (bounced) cheques
  3. ERRORS - somebody made a mistake (e.g. wrote 1,245 instead of 1,425)

The layout:
   Balance per bank           Balance per cash book
   + deposits in transit      - bank charges, direct debits, bounced cheques
   - outstanding cheques      + interest received
                              +/- errors in the cash book
   = ADJUSTED BANK BALANCE  ==  ADJUSTED CASH BOOK BALANCE   (must agree!)

WHAT DOES "REPERFORM" MEAN?
The client gives us THEIR reconciliation. We do NOT just tick it.
We rebuild it ourselves from the raw cash book and bank statement,
then compare. Any difference is a finding.

Run:  python lessons/lesson11_bank_reconciliation.py
"""

from pathlib import Path
import pandas as pd

DATA = Path(__file__).parent.parent / "data"
OUTPUT = Path(__file__).parent.parent / "output"
OUTPUT.mkdir(exist_ok=True)
pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)


# ---------------------------------------------------------------
# STEP 1. Load both records
# ---------------------------------------------------------------
book = pd.read_csv(DATA / "cash_book_dec.csv", parse_dates=["date"])
bank = pd.read_csv(DATA / "bank_statement_dec.csv", parse_dates=["date"])
print(book.head(), "\n")
print(bank.head(), "\n")

# Blank cells mean 0. Then make ONE signed amount column in each:
#   money IN  = positive,  money OUT = negative
book[["receipt", "payment"]] = book[["receipt", "payment"]].fillna(0)
book["amount"] = book["receipt"] - book["payment"]

opening_bank = bank.loc[0, "balance"]               # the "brought forward" row
bank = bank.iloc[1:].copy()                          # remove that row
bank[["debit", "credit"]] = bank[["debit", "credit"]].fillna(0)
bank["amount"] = bank["credit"] - bank["debit"]


# ---------------------------------------------------------------
# STEP 2. Check the arithmetic (auditors call this "casting")
# ---------------------------------------------------------------
# Never trust a balance someone typed. Recalculate it.
opening_book = book.loc[0, "balance"] - book.loc[0, "amount"]
book["check"] = (opening_book + book["amount"].cumsum()).round(2)
bank["check"] = (opening_bank + bank["amount"].cumsum()).round(2)
# .cumsum() = running total, like a balance column in Excel

print("Cash book balances all correct? ", (book["check"] == book["balance"]).all())
print("Bank statement balances correct?", (bank["check"] == bank["balance"]).all())

closing_book = book["balance"].iloc[-1]
closing_bank = bank["balance"].iloc[-1]
print(f"\nCash book closing balance:      {closing_book:>12,.2f}")
print(f"Bank statement closing balance: {closing_bank:>12,.2f}")
print(f"Difference to explain:          {closing_bank - closing_book:>12,.2f}")


# ---------------------------------------------------------------
# STEP 3. Make a "matching key" that is the same in both files
# ---------------------------------------------------------------
# Cash book says "CHQ-1105", bank says "CHQ 1105". A computer sees two
# different texts. We clean both into "CHQ1105".
book["key"] = book["ref"].str.replace("-", "", regex=False)

# For the bank, take the letters + number at the START of the description.
# r"^(CHQ|DEP|EFT) (\d+)" is a "regular expression" (a text pattern):
#   ^ = start of the text,  (CHQ|DEP|EFT) = one of these words,
#   \d+ = one or more digits.   The ( ) parts are what we extract.
parts = bank["description"].str.extract(r"^(CHQ|DEP|EFT) (\d+)")
bank["key"] = parts[0] + parts[1]       # NaN where there is no reference
print("\n", bank[["description", "key"]].head(8))


# ---------------------------------------------------------------
# STEP 4. Match the two files
# ---------------------------------------------------------------
# Bank lines with NO reference (charges, interest...) can't be matched by
# key, so we split them off first and look at them on their own.
bank_no_ref = bank[bank["key"].isna()]
bank_with_ref = bank[bank["key"].notna()]

m = book.merge(bank_with_ref, on="key", how="outer", suffixes=("_book", "_bank"),
               indicator=True)

matched = m[m["_merge"] == "both"].copy()
book_only = m[m["_merge"] == "left_only"]
bank_only_with_ref = m[m["_merge"] == "right_only"]

# Matched by reference, but is the AMOUNT the same?
matched["difference"] = (matched["amount_bank"] - matched["amount_book"]).round(2)
amount_errors = matched[matched["difference"] != 0]

print(f"\nMatched items:            {len(matched)}")
print(f"Matched, wrong amount:    {len(amount_errors)}")
print(f"In cash book only:        {len(book_only)}")
print(f"In bank only (with ref):  {len(bank_only_with_ref)}")
print(f"In bank only (no ref):    {len(bank_no_ref)}")


# ---------------------------------------------------------------
# STEP 5. Explain every unmatched item
# ---------------------------------------------------------------
print("\n--- Amount errors (bank is usually right) ---")
print(amount_errors[["key", "amount_book", "amount_bank", "difference"]].to_string(index=False))
# 1,245 vs 1,425: the digits 4 and 2 swapped = a TRANSPOSITION error.
# Tip: a difference that divides exactly by 9 is often a transposition!
for d in amount_errors["difference"]:
    print(f"  {d} / 9 = {d / 9}  -> whole number, so probably a transposition")

print("\n--- In cash book only = timing items ---")
outstanding_cheques = book_only[book_only["amount_book"] < 0]
deposits_in_transit = book_only[book_only["amount_book"] > 0]
print("Outstanding cheques:\n", outstanding_cheques[["key", "date_book", "amount_book"]].to_string(index=False))
print("Deposits in transit:\n", deposits_in_transit[["key", "date_book", "amount_book"]].to_string(index=False))

print("\n--- In bank only, with a reference ---")
print(bank_only_with_ref[["key", "date_bank", "amount_bank"]].to_string(index=False))
# CHQ1088 is not in December's cash book... check last month's list!
nov = pd.read_csv(DATA / "outstanding_nov.csv", parse_dates=["date_written"])
nov["key"] = nov["ref"].str.replace("-", "", regex=False)
print("\nLast month's outstanding cheques:\n", nov)
cleared_now = nov[nov["key"].isin(bank["key"])]
still_out = nov[~nov["key"].isin(bank["key"])]
print("Cleared in December:", cleared_now["key"].tolist(), " <- fine, timing")
print("STILL outstanding:  ", still_out["key"].tolist())

print("\n--- In bank only, no reference = not yet in the cash book ---")
print(bank_no_ref[["date", "description", "amount"]].to_string(index=False))


# ---------------------------------------------------------------
# STEP 6. Stale cheques
# ---------------------------------------------------------------
# A cheque older than 6 months usually can't be cashed any more ("stale").
# It should be written back to the cash book, not kept on the rec forever.
year_end = pd.Timestamp("2025-12-31")
still_out = still_out.assign(age_days=(year_end - still_out["date_written"]).dt.days)
stale = still_out[still_out["age_days"] > 180]
print("\nStale cheques (older than 180 days):\n", stale[["ref", "payee", "amount", "age_days"]])


# ---------------------------------------------------------------
# STEP 7. Build OUR reconciliation
# ---------------------------------------------------------------
dit = deposits_in_transit["amount_book"].sum()
oc = -outstanding_cheques["amount_book"].sum() + still_out["amount"].sum()
adjusted_bank = closing_bank + dit - oc

bank_items = bank_no_ref["amount"].sum()            # charges, DD, interest, bounced
errors = amount_errors["difference"].sum()
adjusted_book = closing_book + bank_items + errors

rec = pd.DataFrame([
    ("Balance per bank statement", closing_bank),
    ("Add: deposits in transit", dit),
    ("Less: outstanding cheques (incl. prior months)", -oc),
    ("ADJUSTED BANK BALANCE", adjusted_bank),
    ("Balance per cash book", closing_book),
    ("Add/(less): items on bank statement not in cash book", bank_items),
    ("Add/(less): cash book errors (transposition)", errors),
    ("ADJUSTED CASH BOOK BALANCE", adjusted_book),
    ("DIFFERENCE (should be zero)", round(adjusted_bank - adjusted_book, 2)),
], columns=["item", "amount"])
print("\nOUR BANK RECONCILIATION AT 31 DEC 2025")
print(rec.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))


# ---------------------------------------------------------------
# STEP 8. Compare with the CLIENT'S reconciliation
# ---------------------------------------------------------------
client = pd.read_csv(DATA / "client_bank_rec_dec.csv")
print("\nCLIENT'S RECONCILIATION")
print(client.to_string(index=False))

client_adj_bank = client.loc[client["description"] == "ADJUSTED BANK BALANCE", "amount"].iloc[0]
client_adj_book = client.loc[client["description"] == "ADJUSTED CASH BOOK BALANCE", "amount"].iloc[0]
print(f"\nAdjusted bank:  client {client_adj_bank:,.2f}  vs ours {adjusted_bank:,.2f}"
      f"  -> difference {client_adj_bank - adjusted_bank:,.2f}")
print(f"Adjusted book:  client {client_adj_book:,.2f}  vs ours {adjusted_book:,.2f}"
      f"  -> difference {client_adj_book - adjusted_book:,.2f}")

# Which outstanding cheques did the client list?
client_os = client["description"].str.extract(r"(CHQ-\d+)")[0].dropna()
client_os = set(client_os.str.replace("-", "", regex=False))
ours = set(outstanding_cheques["key"]) | set(still_out["key"])
print("Outstanding cheques the client MISSED:", sorted(ours - client_os))

plug = client[client["description"].str.contains("Unreconciled", case=False)]
print("\nCLIENT 'PLUG' FIGURE:\n", plug.to_string(index=False))
print("""
FINDINGS for the audit file:
 1. The client left one outstanding cheque off the reconciliation.
 2. The client did not correct the transposition error in the cash book.
 3. Instead of finding these, they wrote off the difference to sundry
    expenses. A "plug" like this hides errors - and sometimes fraud.
 4. A stale cheque is still on the rec and should be written back.
 5. The cash book needs entries for charges, interest, the direct debit
    and the bounced cheque.
""")

with pd.ExcelWriter(OUTPUT / "bank_rec_workpaper.xlsx") as w:
    rec.to_excel(w, sheet_name="Our reconciliation", index=False)
    client.to_excel(w, sheet_name="Client reconciliation", index=False)
    matched.to_excel(w, sheet_name="Matched", index=False)
    book_only.to_excel(w, sheet_name="Cash book only", index=False)
    bank_only_with_ref.to_excel(w, sheet_name="Bank only - ref", index=False)
    bank_no_ref.to_excel(w, sheet_name="Bank only - no ref", index=False)
print("Saved output/bank_rec_workpaper.xlsx")


# ===============================================================
# SUMMARY - the bank rec audit programme in Python
#   1. Load cash book + bank statement, make one signed amount column
#   2. Recalculate (cast) running balances
#   3. Clean references into one matching key  (.str.replace, .str.extract)
#   4. merge(how="outer", indicator=True) to match
#   5. Matched but different amount -> errors   (difference / 9 trick)
#   6. Book only -> outstanding cheques / deposits in transit
#      Bank only -> charges, interest, DDs, bounced cheques, last month's items
#   7. Look for stale cheques (> 6 months)
#   8. Build your own rec, prove the difference is ZERO
#   9. Compare with the client's rec, report every difference and any plug
#
# PRACTICE: practice/03_bank_reconciliation.py
# ===============================================================
