"""
PRACTICE SET 3 - REPERFORMING THE BANK RECONCILIATION (18 tasks)
Files: data/cash_book_dec.csv, data/bank_statement_dec.csv,
       data/outstanding_nov.csv, data/client_bank_rec_dec.csv
Lesson needed first: 11  (try to do it WITHOUT looking at lesson 11!)
"""

from pathlib import Path
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "data").is_dir())
DATA, OUTPUT = ROOT / "data", ROOT / "output"
OUTPUT.mkdir(exist_ok=True)
pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)

book = pd.read_csv(DATA / "cash_book_dec.csv", parse_dates=["date"])
bank = pd.read_csv(DATA / "bank_statement_dec.csv", parse_dates=["date"])
nov = pd.read_csv(DATA / "outstanding_nov.csv", parse_dates=["date_written"])
client = pd.read_csv(DATA / "client_bank_rec_dec.csv")

# TASK 1: (Warm-up) In the cash book, fill blanks with 0 and make a signed "amount"
# column (receipts +, payments -). How many receipts and payments are there, and
# what are their totals?
book[["receipt", "payment"]] = book[["receipt", "payment"]].fillna(0)
book["amount"] = book["receipt"] - book["payment"]
print(f"Receipts {(book['receipt'] > 0).sum()} = {book['receipt'].sum():,.2f}")
print(f"Payments {(book['payment'] > 0).sum()} = {book['payment'].sum():,.2f}")

# TASK 2: Work out the cash book OPENING balance (first balance minus first amount).
# Then prove: opening + receipts - payments = closing balance.
opening_book = book["balance"].iloc[0] - book["amount"].iloc[0]
closing_book = book["balance"].iloc[-1]
print(f"Opening {opening_book:,.2f}  Closing {closing_book:,.2f}  Proof OK:",
      round(opening_book + book["amount"].sum(), 2) == closing_book)

# TASK 3: Do the same for the bank statement. Remember the first row is
# "BALANCE BROUGHT FORWARD". Make a signed amount (credit +, debit -).
opening_bank = bank["balance"].iloc[0]
bank = bank.iloc[1:].copy()
bank[["debit", "credit"]] = bank[["debit", "credit"]].fillna(0)
bank["amount"] = bank["credit"] - bank["debit"]
closing_bank = bank["balance"].iloc[-1]
print(f"Bank opening {opening_bank:,.2f}  closing {closing_bank:,.2f}  Proof OK:",
      round(opening_bank + bank["amount"].sum(), 2) == closing_bank)

# TASK 4: Recalculate EVERY running balance on the bank statement with .cumsum().
# Are any rows wrong?
bank["recalc"] = (opening_bank + bank["amount"].cumsum()).round(2)
print("Wrong rows:", (bank["recalc"] != bank["balance"]).sum())

# TASK 5: The opening balances differ. Use outstanding_nov.csv to explain the
# difference between the bank and cash book OPENING balances.
print(f"Opening difference {opening_bank - opening_book:,.2f} = Nov outstanding cheques "
      f"{nov['amount'].sum():,.2f}")

# TASK 6: Create a matching key in both files ("CHQ-1105" and "CHQ 1105" -> "CHQ1105").
book["key"] = book["ref"].str.replace("-", "", regex=False)
p = bank["description"].str.extract(r"^(CHQ|DEP|EFT) (\d+)")
bank["key"] = p[0] + p[1]
print(bank[["description", "key"]].head())

# TASK 7: Match cash book to bank (only bank rows that HAVE a key).
# How many matched, how many only in the book, how many only in the bank?
with_ref = bank[bank["key"].notna()]
m = book.merge(with_ref, on="key", how="outer", suffixes=("_book", "_bank"), indicator=True)
print(m["_merge"].value_counts())

# TASK 8: For matched items, find where the amounts are different. Is the
# difference divisible by 9 (a sign of a transposition error)?
both = m[m["_merge"] == "both"].copy()
both["diff"] = (both["amount_bank"] - both["amount_book"]).round(2)
errors = both[both["diff"] != 0]
print(errors[["key", "amount_book", "amount_bank", "diff"]], "\nDivisible by 9:",
      (errors["diff"] % 9 == 0).tolist())

# TASK 9: List the OUTSTANDING CHEQUES at 31 December (in the book, not the bank)
# and their total.
os_dec = m[(m["_merge"] == "left_only") & (m["amount_book"] < 0)]
print(os_dec[["key", "date_book", "details", "amount_book"]], os_dec["amount_book"].sum())

# TASK 10: List the DEPOSITS IN TRANSIT and their total.
dit = m[(m["_merge"] == "left_only") & (m["amount_book"] > 0)]
print(dit[["key", "date_book", "amount_book"]], dit["amount_book"].sum())

# TASK 11: Write a function classify(description) that returns "Bank charges",
# "Interest", "Direct debit", "Returned cheque" or "Other". Use it on the bank
# rows with NO key.
def classify(text):
    t = text.upper()
    if "CHARGES" in t:
        return "Bank charges"
    if "INTEREST" in t:
        return "Interest"
    if t.startswith("DD"):
        return "Direct debit"
    if "RETURNED" in t:
        return "Returned cheque"
    return "Other"

no_ref = bank[bank["key"].isna()].copy()
no_ref["category"] = no_ref["description"].apply(classify)
print(no_ref[["date", "description", "amount", "category"]])

# TASK 12: Which of last month's outstanding cheques cleared in December, on what
# date, and how many days after they were written?
nov["key"] = nov["ref"].str.replace("-", "", regex=False)
cleared = nov.merge(bank[["key", "date"]], on="key")
cleared["days_to_clear"] = (cleared["date"] - cleared["date_written"]).dt.days
print(cleared[["ref", "date_written", "date", "days_to_clear"]])

# TASK 13: Which of last month's cheques are STILL outstanding? Are any stale
# (older than 6 months at 31 Dec 2025)?
still = nov[~nov["key"].isin(bank["key"])].copy()
still["age_days"] = (pd.Timestamp("2025-12-31") - still["date_written"]).dt.days
still["stale"] = still["age_days"] > 182
print(still[["ref", "payee", "amount", "age_days", "stale"]])

# TASK 14: For December cheques that DID clear, how many days did each take?
# What is the average, and which took the longest?
chq = both[both["key"].str.startswith("CHQ")].copy()
chq["days"] = (chq["date_bank"] - chq["date_book"]).dt.days
print(f"Average {chq['days'].mean():.1f} days; slowest {chq.loc[chq['days'].idxmax(), 'key']}"
      f" ({chq['days'].max()} days)")

# TASK 15: Build your reconciliation and prove adjusted bank == adjusted book.
adj_bank = closing_bank + dit["amount_book"].sum() + os_dec["amount_book"].sum() - still["amount"].sum()
adj_book = closing_book + no_ref["amount"].sum() + errors["diff"].sum()
print(f"Adjusted bank {adj_bank:,.2f}   Adjusted book {adj_book:,.2f}"
      f"   Difference {adj_bank - adj_book:,.2f}")

# TASK 16: Compare with the client's rec. Show that the client's "unreconciled
# difference" = missed outstanding cheque(s) + the uncorrected transposition error.
plug = client.loc[client["description"].str.contains("Unreconciled"), "amount"].iloc[0]
listed = set(client["description"].str.extract(r"(CHQ-\d+)")[0].dropna().str.replace("-", ""))
missed = os_dec[~os_dec["key"].isin(listed)]
explained = -missed["amount_book"].sum() + errors["diff"].sum()
print(f"Plug {plug:,.2f} = missed cheques {-missed['amount_book'].sum():,.2f}"
      f" + transposition {errors['diff'].sum():,.2f} = {explained:,.2f}")

# TASK 17: Prepare the ADJUSTING ENTRIES the client must post in the cash book
# (account, debit, credit, reason). Make sure total debits = total credits.
adj = []
for _, r in no_ref.iterrows():
    other = {"Bank charges": "Bank charges expense", "Interest": "Interest income",
             "Direct debit": "Insurance expense", "Returned cheque": "Accounts receivable - Beta Ltd"}
    if r["amount"] < 0:
        adj += [(other[r["category"]], -r["amount"], 0, r["description"]),
                ("Cash at bank", 0, -r["amount"], r["description"])]
    else:
        adj += [("Cash at bank", r["amount"], 0, r["description"]),
                (other[r["category"]], 0, r["amount"], r["description"])]
for _, r in errors.iterrows():
    adj += [("Accounts payable", -r["diff"], 0, f"Correct {r['key']} transposition"),
            ("Cash at bank", 0, -r["diff"], f"Correct {r['key']} transposition")]
for _, r in still[still["stale"]].iterrows():
    adj += [("Cash at bank", r["amount"], 0, f"Write back stale {r['ref']}"),
            ("Accounts payable - " + r["payee"], 0, r["amount"], f"Write back stale {r['ref']}")]
adj = pd.DataFrame(adj, columns=["account", "debit", "credit", "reason"])
print(adj.to_string(index=False))
print("Balanced:", round(adj["debit"].sum(), 2) == round(adj["credit"].sum(), 2))

# TASK 18: Save output/p3_bank_rec.xlsx with sheets: Outstanding cheques, Deposits
# in transit, Bank only, Errors, Adjusting entries.
with pd.ExcelWriter(OUTPUT / "p3_bank_rec.xlsx") as w:
    os_dec.to_excel(w, sheet_name="Outstanding cheques", index=False)
    dit.to_excel(w, sheet_name="Deposits in transit", index=False)
    no_ref.to_excel(w, sheet_name="Bank only", index=False)
    errors.to_excel(w, sheet_name="Errors", index=False)
    adj.to_excel(w, sheet_name="Adjusting entries", index=False)
print("Saved output/p3_bank_rec.xlsx")
