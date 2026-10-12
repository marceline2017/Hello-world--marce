"""
PRACTICE SET 3 - REPERFORMING THE BANK RECONCILIATION (18 tasks)
Files: data/cash_book_dec.csv, data/bank_statement_dec.csv,
       data/outstanding_nov.csv, data/client_bank_rec_dec.csv
Lesson needed first: 11  (try to do it WITHOUT looking at lesson 11!)

HOW TO USE: write your code under each TODO, then run this file:
    python practice/03_bank_reconciliation.py
Stuck? Compare with practice/solutions/03_bank_reconciliation.py - but try first!
The setup code below is already done for you.
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
# TODO


# TASK 2: Work out the cash book OPENING balance (first balance minus first amount).
# Then prove: opening + receipts - payments = closing balance.
# TODO


# TASK 3: Do the same for the bank statement. Remember the first row is
# "BALANCE BROUGHT FORWARD". Make a signed amount (credit +, debit -).
# TODO


# TASK 4: Recalculate EVERY running balance on the bank statement with .cumsum().
# Are any rows wrong?
# TODO


# TASK 5: The opening balances differ. Use outstanding_nov.csv to explain the
# difference between the bank and cash book OPENING balances.
# TODO


# TASK 6: Create a matching key in both files ("CHQ-1105" and "CHQ 1105" -> "CHQ1105").
# TODO


# TASK 7: Match cash book to bank (only bank rows that HAVE a key).
# How many matched, how many only in the book, how many only in the bank?
# TODO


# TASK 8: For matched items, find where the amounts are different. Is the
# difference divisible by 9 (a sign of a transposition error)?
# TODO


# TASK 9: List the OUTSTANDING CHEQUES at 31 December (in the book, not the bank)
# and their total.
# TODO


# TASK 10: List the DEPOSITS IN TRANSIT and their total.
# TODO


# TASK 11: Write a function classify(description) that returns "Bank charges",
# "Interest", "Direct debit", "Returned cheque" or "Other". Use it on the bank
# rows with NO key.
# TODO


# TASK 12: Which of last month's outstanding cheques cleared in December, on what
# date, and how many days after they were written?
# TODO


# TASK 13: Which of last month's cheques are STILL outstanding? Are any stale
# (older than 6 months at 31 Dec 2025)?
# TODO


# TASK 14: For December cheques that DID clear, how many days did each take?
# What is the average, and which took the longest?
# TODO


# TASK 15: Build your reconciliation and prove adjusted bank == adjusted book.
# TODO


# TASK 16: Compare with the client's rec. Show that the client's "unreconciled
# difference" = missed outstanding cheque(s) + the uncorrected transposition error.
# TODO


# TASK 17: Prepare the ADJUSTING ENTRIES the client must post in the cash book
# (account, debit, credit, reason). Make sure total debits = total credits.
# TODO


# TASK 18: Save output/p3_bank_rec.xlsx with sheets: Outstanding cheques, Deposits
# in transit, Bank only, Errors, Adjusting entries.
# TODO
