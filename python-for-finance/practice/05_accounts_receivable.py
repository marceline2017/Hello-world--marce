"""
PRACTICE SET 5 - ACCOUNTS RECEIVABLE (20 tasks)
Files: data/customers.csv, data/ar_invoices.csv, data/ar_receipts.csv,
       data/ar_receipts_2026.csv, data/ar_credit_notes_2026.csv
Lesson needed first: 14

HOW TO USE: write your code under each TODO, then run this file:
    python practice/05_accounts_receivable.py
Stuck? Compare with practice/solutions/05_accounts_receivable.py - but try first!
The setup code below is already done for you.
"""

from pathlib import Path
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "data").is_dir())
DATA, OUTPUT = ROOT / "data", ROOT / "output"
OUTPUT.mkdir(exist_ok=True)
pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)
YEAR_END = pd.Timestamp("2025-12-31")

customers = pd.read_csv(DATA / "customers.csv")
inv = pd.read_csv(DATA / "ar_invoices.csv", parse_dates=["invoice_date", "due_date"])
rec = pd.read_csv(DATA / "ar_receipts.csv", parse_dates=["date"])
rec26 = pd.read_csv(DATA / "ar_receipts_2026.csv", parse_dates=["date"])
cn26 = pd.read_csv(DATA / "ar_credit_notes_2026.csv", parse_dates=["date"])
rec["invoice_no"] = rec["invoice_no"].fillna("")
inv = inv.merge(customers, on="customer_id", how="left")
sales25 = inv[inv["invoice_date"].dt.year == 2025]

# TASK 1: (Warm-up) Total 2025 sales per customer name. Show the top 5.
# TODO


# TASK 2: Total 2025 sales per month.
# TODO


# TASK 3: CONCENTRATION. What % of 2025 sales comes from the biggest customer,
# and from the top 3 together?
# TODO


# TASK 4: Average invoice size per customer, and the single largest invoice.
# TODO


# TASK 5: Invoice numbers should be a continuous sequence (INV-25001, INV-25002...).
# Are any numbers missing?
# TODO


# TASK 6: Which invoice numbers are used more than once?
# TODO


# TASK 7: List invoices whose due date does not match the customer's payment terms.
# TODO


# TASK 8: Were any invoices raised for BLOCKED customers?
# TODO


# TASK 9: HOW FAST DO CUSTOMERS PAY? For each receipt, days between invoice date and
# receipt date. Show the average per customer next to their terms. Who is slowest?
# TODO


# TASK 10: Find receipts that are NOT linked to an invoice, and receipts linked
# to an invoice number that does not exist.
# TODO


# TASK 11: Balance per customer (invoices - receipts). Prove that the total equals
# total invoices minus total receipts.
# TODO


# TASK 12: Open amount per invoice (amount - receipts for that invoice; give the
# cash to the FIRST invoice if a number is used twice). Then age by INVOICE DATE
# (0-30, 31-60, 61-90, 91-180, 181+ days old).
# TODO


# TASK 13: Which customers have ANY invoice more than 90 days OVERDUE (past the
# due date)? How much is that in total?
# TODO


# TASK 14: PROVISION. 100% for invoices from 2024 still open (specific provision),
# plus the matrix for the rest: not overdue 1%, 1-90 days overdue 10%, >90 days 50%.
# TODO


# TASK 15: DSO per customer = balance / 2025 sales x 365. Which customers are above 90?
# TODO


# TASK 16: AFTER-DATE CASH. For each customer, what % of the year-end OPEN invoices
# was received in Jan-Feb 2026?
# TODO


# TASK 17: CUT-OFF. List invoices dated 27-31 December and show which were
# cancelled by a credit note in January 2026.
# TODO


# TASK 18: CONFIRMATION SAMPLE: the 3 customers with the largest balances plus 3
# others chosen at random (random_state=7). Write one letter per customer to
# output/p5_letters/.
# TODO


# TASK 19: The replies came back: C002 says it owes 3,793.40, C010 says 41,874.02,
# and C014 did not reply. Compare each reply with our balance. For a
# disagreement, could the cut-off credit notes explain it? For no reply, what
# would you do instead?
# TODO


# TASK 20: Save output/p5_receivables.xlsx with your ageing (task 12), provision
# (task 14) and confirmation sample (task 18).
# TODO
