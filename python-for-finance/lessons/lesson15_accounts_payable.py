"""
LESSON 15 - ACCOUNTS PAYABLE (money we owe suppliers)
=====================================================

The normal "purchase-to-pay" process:
   1. PURCHASE ORDER (PO)   - we ask a supplier for goods, at an agreed price
   2. GOODS RECEIVED (GRN)  - the goods arrive and the store signs for them
   3. SUPPLIER INVOICE      - the supplier bills us
   4. PAYMENT               - we pay the supplier's bank account
Until we pay, the amount is a PAYABLE (also "creditors") - a liability.

What can go wrong (and what auditors test):
  COMPLETENESS  - are ALL liabilities recorded? Companies like to hide
                  bills to look more profitable.
                  -> search for unrecorded liabilities, supplier statement recs
  OCCURRENCE    - did we really get the goods? Is the supplier real?
                  -> three-way match (PO = GRN = invoice), supplier master tests
  FRAUD         - fake suppliers, duplicate payments, changed bank details
                  -> bank account tests, duplicate tests, payment tests

Run:  python lessons/lesson15_accounts_payable.py
"""

from pathlib import Path
import pandas as pd

DATA = Path(__file__).parent.parent / "data"
OUTPUT = Path(__file__).parent.parent / "output"
OUTPUT.mkdir(exist_ok=True)
pd.set_option("display.width", 150)
pd.set_option("display.max_columns", 20)
YEAR_END = pd.Timestamp("2025-12-31")

suppliers = pd.read_csv(DATA / "suppliers.csv", parse_dates=["created_date"])
employees = pd.read_csv(DATA / "employees.csv")
po = pd.read_csv(DATA / "purchase_orders.csv", parse_dates=["po_date"])
grn = pd.read_csv(DATA / "goods_received.csv", parse_dates=["date_received"])
inv = pd.read_csv(DATA / "ap_invoices.csv", parse_dates=["invoice_date", "due_date"])
pay = pd.read_csv(DATA / "ap_payments.csv", parse_dates=["date"])
pay26 = pd.read_csv(DATA / "ap_payments_2026.csv", parse_dates=["date", "invoice_date"])
stmt = pd.read_csv(DATA / "supplier_statement_S006.csv", parse_dates=["date"])
inv["po_number"] = inv["po_number"].fillna("")
names = suppliers.set_index("supplier_id")["supplier_name"]


# ---------------------------------------------------------------
# STEP 1. SUPPLIER MASTER FILE tests (who can we pay?)
# ---------------------------------------------------------------
print("--- Supplier master file ---")
shared = suppliers[suppliers["bank_account"].duplicated(keep=False)]
print("Suppliers sharing a bank account:\n", shared[["supplier_id", "supplier_name", "bank_account"]])

staff_match = suppliers.merge(employees, on="bank_account")
print("\nSupplier bank account = an EMPLOYEE's account (ghost supplier?):\n",
      staff_match[["supplier_id", "supplier_name", "employee_name", "bank_account"]])

new = suppliers[suppliers["created_date"] >= "2025-07-01"]
print("\nSuppliers created in the last 6 months:\n", new[["supplier_id", "supplier_name", "created_date"]])


# ---------------------------------------------------------------
# STEP 2. THREE-WAY MATCH: PO vs goods received vs invoice
# ---------------------------------------------------------------
m3 = (inv.merge(po[["po_number", "po_amount"]], on="po_number", how="left")
         .merge(grn[["po_number", "amount_received"]], on="po_number", how="left"))
no_po = m3[m3["po_number"] == ""]
no_grn = m3[(m3["po_number"] != "") & m3["amount_received"].isna()]
TOLERANCE = 0.05     # we accept an invoice up to 5% above the PO
over_po = m3[m3["amount"] > m3["po_amount"] * (1 + TOLERANCE)]
print("\n--- Three-way match ---")
print("Invoices with NO purchase order:\n", no_po[["invoice_no", "supplier_id", "invoice_date", "amount"]])
print("\nInvoices with a PO but NO goods received:\n", no_grn[["invoice_no", "supplier_id", "po_number", "amount"]])
print("\nInvoices more than 5% ABOVE the PO:\n",
      over_po[["invoice_no", "supplier_id", "po_amount", "amount"]].assign(
          over_by=over_po["amount"] - over_po["po_amount"]).round(2))


# ---------------------------------------------------------------
# STEP 3. DUPLICATE INVOICES
# ---------------------------------------------------------------
# Exact duplicates are easy to catch. Fraudsters and tired clerks create
# "near" duplicates: "PR-12345" and "PR-12345A". So we also compare the
# DIGITS only, plus supplier and amount.
inv["digits"] = inv["invoice_no"].str.replace(r"\D", "", regex=True)   # \D = not a digit
near_dup = inv[inv.duplicated(["supplier_id", "digits", "amount"], keep=False)]
print("\n--- Duplicate invoices (same supplier, same digits, same amount) ---\n",
      near_dup[["invoice_no", "supplier_id", "invoice_date", "amount"]])


# ---------------------------------------------------------------
# STEP 4. PAYMENT tests
# ---------------------------------------------------------------
print("\n--- Payment tests ---")
twice = pay[pay.duplicated("invoice_no", keep=False)].sort_values("invoice_no")
print("Invoices PAID TWICE:\n", twice)

pm = pay.merge(suppliers[["supplier_id", "bank_account", "status"]], on="supplier_id")
wrong_acct = pm[pm["paid_to_account"] != pm["bank_account"]]
print("\nPaid to a bank account that is NOT on the master file:\n",
      wrong_acct[["payment_id", "supplier_id", "date", "amount", "paid_to_account", "bank_account"]])

pi = pay.merge(inv[["invoice_no", "invoice_date"]], on="invoice_no", how="left")
early = pi[pi["date"] < pi["invoice_date"]]
print("\nPaid BEFORE the invoice date:\n", early[["payment_id", "invoice_no", "invoice_date", "date", "amount"]])

print("\nPayments to BLOCKED suppliers:\n", pm[pm["status"] == "Blocked"][["payment_id", "supplier_id", "date", "amount"]])
print("\nWeekend payments:\n", pay[pay["date"].dt.dayofweek >= 5][["payment_id", "supplier_id", "date", "amount"]])


# ---------------------------------------------------------------
# STEP 5. Profile the suspicious supplier
# ---------------------------------------------------------------
s11 = inv[inv["supplier_id"] == "S011"]
print("\nFast Supplies Ltd (S011) invoices:\n", s11[["invoice_no", "invoice_date", "amount", "po_number"]])
print("Red flags: new supplier, bank account = employee, no POs, round amounts,"
      " 7-day terms, paid within 2 days.")


# ---------------------------------------------------------------
# STEP 6. The year-end PAYABLES LISTING (and ageing)
# ---------------------------------------------------------------
paid_by_inv = pay.groupby("invoice_no")["amount"].sum()
inv["paid"] = inv["invoice_no"].map(paid_by_inv).fillna(0)
inv["open"] = (inv["amount"] - inv["paid"]).round(2)
ap_list = inv[inv["open"] != 0].copy()
ap_list["days_overdue"] = (YEAR_END - ap_list["due_date"]).dt.days
ap_list["bucket"] = pd.cut(ap_list["days_overdue"], [-10_000, 0, 30, 60, 10_000],
                           labels=["not due", "1_30", "31_60", "over_60"])
print(f"\nPayables at 31 Dec 2025: {ap_list['open'].sum():,.2f} on {len(ap_list)} invoices")
print(ap_list.groupby("bucket", observed=False)["open"].sum().round(0))
debit_bal = ap_list[ap_list["open"] < 0]
print("Negative items (we overpaid - should be recovered):\n",
      debit_bal[["invoice_no", "supplier_id", "amount", "paid", "open"]])

purchases = inv.loc[inv["invoice_date"].dt.year == 2025, "amount"].sum()
print(f"Creditor days: {ap_list['open'].sum() / purchases * 365:.0f}")


# ---------------------------------------------------------------
# STEP 7. SEARCH FOR UNRECORDED LIABILITIES
# ---------------------------------------------------------------
# Look at payments made AFTER year end. If the cost belongs to 2025
# (invoice dated 2025, or the service was in 2025) it should be in the
# year-end payables. If it isn't - it is UNRECORDED.
after = pay26.copy()
after["for_2025"] = after["invoice_date"] <= YEAR_END
after["recorded"] = after["invoice_no"].isin(inv["invoice_no"])
unrecorded = after[after["for_2025"] & ~after["recorded"]]
print("\n--- Search for unrecorded liabilities ---")
print(f"Payments Jan-Feb 2026 checked: {len(after)} = {after['amount'].sum():,.2f}")
print("UNRECORDED 2025 liabilities:\n",
      unrecorded[["payment_id", "supplier_id", "invoice_no", "invoice_date", "amount", "description"]])
print(f"Total understatement of payables: {unrecorded['amount'].sum():,.2f}")


# ---------------------------------------------------------------
# STEP 8. SUPPLIER STATEMENT RECONCILIATION (BrightPath, S006)
# ---------------------------------------------------------------
# A supplier statement is strong evidence: it comes from outside.
# It works like a bank reconciliation: match items, explain differences.
stmt_bal = stmt["balance"].iloc[-1]
our_bal = inv.loc[inv["supplier_id"] == "S006", "amount"].sum() - pay.loc[pay["supplier_id"] == "S006", "amount"].sum()
print(f"\n--- Supplier statement S006 ---\nTheir balance {stmt_bal:,.2f}   Our balance {our_bal:,.2f}"
      f"   Difference {stmt_bal - our_bal:,.2f}")

s_inv = stmt[stmt["invoice"].notna()][["ref", "invoice"]]
our_inv = inv.loc[inv["supplier_id"] == "S006", ["invoice_no", "amount"]]
mi = s_inv.merge(our_inv, left_on="ref", right_on="invoice_no", how="left")
missing_inv = mi[mi["invoice_no"].isna()]
price_diff = mi[mi["invoice_no"].notna() & (mi["invoice"] != mi["amount"])]
s_pay = set(stmt["ref"].dropna())
our_pay = pay[(pay["supplier_id"] == "S006") & (pay["date"] >= "2025-10-01")]
in_transit = our_pay[~our_pay["payment_id"].isin(s_pay)]
print("On their statement, NOT in our books:\n", missing_inv[["ref", "invoice"]])
print("Same invoice, different amount:\n", price_diff[["ref", "invoice", "amount"]])
print("Our payments they haven't received yet (in transit):\n", in_transit[["payment_id", "date", "amount"]])
# All three make THEIR balance higher than OURS, so we add them up:
#   their invoice we don't have + extra they charged + money still on its way
explained = (missing_inv["invoice"].sum() + (price_diff["invoice"] - price_diff["amount"]).sum()
             + in_transit["amount"].sum())
print(f"Explained difference: {explained:,.2f}  ->  unexplained "
      f"{stmt_bal - our_bal - explained:,.2f}")

with pd.ExcelWriter(OUTPUT / "ap_workpaper.xlsx") as w:
    pd.concat([no_po.assign(issue="No PO"), no_grn.assign(issue="No GRN"),
               over_po.assign(issue="Above PO")]).to_excel(w, sheet_name="3-way match", index=False)
    near_dup.to_excel(w, sheet_name="Duplicate invoices", index=False)
    twice.to_excel(w, sheet_name="Duplicate payments", index=False)
    wrong_acct.to_excel(w, sheet_name="Wrong bank account", index=False)
    ap_list.to_excel(w, sheet_name="AP listing", index=False)
    unrecorded.to_excel(w, sheet_name="Unrecorded liabilities", index=False)
print("\nSaved output/ap_workpaper.xlsx")


# ===============================================================
# SUMMARY - payables audit programme in Python
#   1. Supplier master: shared bank accounts, employee bank accounts, new suppliers
#   2. Three-way match: no PO, no GRN, invoice above PO (+ tolerance)
#   3. Duplicate invoices: exact AND "digits only" near-duplicates
#   4. Payments: paid twice, wrong bank account, before invoice, blocked, weekends
#   5. Year-end AP listing, ageing, debit balances, creditor days
#   6. Search for unrecorded liabilities using payments after year end
#   7. Supplier statement reconciliation
#
# PRACTICE: practice/06_accounts_payable.py
# ===============================================================
