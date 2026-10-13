"""
PRACTICE SET 6 - ACCOUNTS PAYABLE (20 tasks)
Files: data/suppliers.csv, data/employees.csv, data/purchase_orders.csv,
       data/goods_received.csv, data/ap_invoices.csv, data/ap_payments.csv,
       data/ap_payments_2026.csv, data/supplier_statement_S006.csv
Lesson needed first: 15

HOW TO USE: write your code under each TODO, then run this file:
    python practice/06_accounts_payable.py
Stuck? Compare with practice/solutions/06_accounts_payable.py - but try first!
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

suppliers = pd.read_csv(DATA / "suppliers.csv", parse_dates=["created_date"])
employees = pd.read_csv(DATA / "employees.csv")
po = pd.read_csv(DATA / "purchase_orders.csv", parse_dates=["po_date"])
grn = pd.read_csv(DATA / "goods_received.csv", parse_dates=["date_received"])
inv = pd.read_csv(DATA / "ap_invoices.csv", parse_dates=["invoice_date", "due_date"])
pay = pd.read_csv(DATA / "ap_payments.csv", parse_dates=["date"])
pay26 = pd.read_csv(DATA / "ap_payments_2026.csv", parse_dates=["date", "invoice_date"])
inv["po_number"] = inv["po_number"].fillna("")
inv = inv.merge(suppliers[["supplier_id", "supplier_name"]], on="supplier_id")

# TASK 1: (Warm-up) Total invoiced per supplier name in 2025, largest first.
# TODO


# TASK 2: Total purchases (invoices) per month.
# TODO


# TASK 3: How many POs, GRNs and invoices are there? Which POs have NO invoice?
# TODO


# TASK 4: GOODS RECEIVED NOT INVOICED (GRNI). Which goods arrived by 31 Dec with no
# invoice yet? Their total must be ACCRUED as a liability.
# TODO


# TASK 5: Average days from PO to goods received, and from goods received to
# invoice, per supplier.
# TODO


# TASK 6: THREE-WAY MATCH with a stricter 2% tolerance. List invoices with no PO,
# no GRN, or more than 2% above the PO.
# TODO


# TASK 7: Any invoices dated BEFORE the goods arrived?
# TODO


# TASK 8: EXACT duplicate invoices: same supplier, same amount, same date.
# TODO


# TASK 9: Invoices PAID MORE THAN ONCE, and the money to recover.
# TODO


# TASK 10: Were invoices paid on time? For each payment, days paid compared with the
# due date (negative = early). Average per supplier. Which payments were more
# than 5 days EARLY (bad for our cash)?
# TODO


# TASK 11: Payments to an account different from the supplier master, payments to
# BLOCKED suppliers and payments on weekends - put them in ONE table with a
# "test" column.
# TODO


# TASK 12: SUPPLIER MASTER: find suppliers whose names start with the same word,
# suppliers sharing a bank account, and suppliers whose account is an employee's.
# TODO


# TASK 13: ROUND AMOUNTS. For each supplier, what % of its invoices are whole
# hundreds (e.g. 4,500.00)? Real invoices are rarely round.
# TODO


# TASK 14: The approval limit for invoices is 20,000. List invoices between 19,000
# and 19,999.99, and count invoices above 20,000.
# TODO


# TASK 15: YEAR-END PAYABLES LISTING per supplier (invoices - payments up to 31 Dec).
# Show suppliers with a DEBIT balance (we paid too much).
# TODO


# TASK 16: Age the open INVOICES at year end by days past the due date
# (not due, 1-30, 31-60, 60+).
# TODO


# TASK 17: UNRECORDED LIABILITIES. From the 2026 payments, list those for 2025
# costs (invoice dated on/before 31 Dec) whose invoice is NOT in ap_invoices.
# Only report items over 1,000.
# TODO


# TASK 18: TOTAL UNDERSTATEMENT of liabilities = GRNI (task 4) + unrecorded
# liabilities (task 17). Is it more than performance materiality of 30,000?
# TODO


# TASK 19: SUPPLIER STATEMENT. Load supplier_statement_S006.csv. Find the
# statement invoices that are not in our books and the payments we made that are
# not on the statement.
# TODO


# TASK 20: Save output/p6_payables.xlsx with the three-way match issues, the
# payment test table, GRNI and unrecorded liabilities.
# TODO
