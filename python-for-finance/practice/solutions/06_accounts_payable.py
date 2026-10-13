"""
PRACTICE SET 6 - ACCOUNTS PAYABLE (20 tasks)
Files: data/suppliers.csv, data/employees.csv, data/purchase_orders.csv,
       data/goods_received.csv, data/ap_invoices.csv, data/ap_payments.csv,
       data/ap_payments_2026.csv, data/supplier_statement_S006.csv
Lesson needed first: 15
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
print(inv.groupby("supplier_name")["amount"].sum().sort_values(ascending=False).round(0))

# TASK 2: Total purchases (invoices) per month.
print(inv.groupby(inv["invoice_date"].dt.month)["amount"].sum().round(0))

# TASK 3: How many POs, GRNs and invoices are there? Which POs have NO invoice?
print(len(po), len(grn), len(inv))
no_inv = po[~po["po_number"].isin(inv["po_number"])]
print(no_inv)

# TASK 4: GOODS RECEIVED NOT INVOICED (GRNI). Which goods arrived by 31 Dec with no
# invoice yet? Their total must be ACCRUED as a liability.
grni = grn[(grn["date_received"] <= YEAR_END) & ~grn["po_number"].isin(inv["po_number"])]
print(grni, "\nAccrual needed:", grni["amount_received"].sum())

# TASK 5: Average days from PO to goods received, and from goods received to
# invoice, per supplier.
flow = po.merge(grn, on="po_number").merge(inv[["po_number", "invoice_date"]], on="po_number")
flow["po_to_grn"] = (flow["date_received"] - flow["po_date"]).dt.days
flow["grn_to_inv"] = (flow["invoice_date"] - flow["date_received"]).dt.days
print(flow.groupby("supplier_id")[["po_to_grn", "grn_to_inv"]].mean().round(1))

# TASK 6: THREE-WAY MATCH with a stricter 2% tolerance. List invoices with no PO,
# no GRN, or more than 2% above the PO.
m = inv.merge(po[["po_number", "po_amount"]], on="po_number", how="left") \
       .merge(grn[["po_number", "amount_received"]], on="po_number", how="left")
m["issue"] = ""
m.loc[m["po_number"] == "", "issue"] = "no PO"
m.loc[(m["po_number"] != "") & m["amount_received"].isna(), "issue"] = "no GRN"
m.loc[m["amount"] > m["po_amount"] * 1.02, "issue"] = "above PO"
print(m[m["issue"] != ""][["invoice_no", "supplier_name", "po_amount", "amount", "issue"]])

# TASK 7: Any invoices dated BEFORE the goods arrived?
ig = inv.merge(grn[["po_number", "date_received"]], on="po_number")
before = ig[ig["invoice_date"] < ig["date_received"]]
print(before[["invoice_no", "supplier_name", "invoice_date", "date_received"]]
      if len(before) else "None - every invoice came after the goods. Good!")

# TASK 8: EXACT duplicate invoices: same supplier, same amount, same date.
print(inv[inv.duplicated(["supplier_id", "amount", "invoice_date"], keep=False)]
      [["invoice_no", "supplier_name", "invoice_date", "amount"]])

# TASK 9: Invoices PAID MORE THAN ONCE, and the money to recover.
paid = pay.groupby("invoice_no")["amount"].agg(["count", "sum"])
twice = paid[paid["count"] > 1]
amt = inv.drop_duplicates("invoice_no").set_index("invoice_no")["amount"]
print(twice.assign(to_recover=twice["sum"] - amt.reindex(twice.index)))

# TASK 10: Were invoices paid on time? For each payment, days paid compared with the
# due date (negative = early). Average per supplier. Which payments were more
# than 5 days EARLY (bad for our cash)?
pd_ = pay.merge(inv[["invoice_no", "due_date"]].drop_duplicates("invoice_no"), on="invoice_no")
pd_["days_vs_due"] = (pd_["date"] - pd_["due_date"]).dt.days
print(pd_.groupby("supplier_id")["days_vs_due"].mean().round(1))
print(pd_[pd_["days_vs_due"] < -5][["payment_id", "supplier_id", "date", "due_date", "amount"]])

# TASK 11: Payments to an account different from the supplier master, payments to
# BLOCKED suppliers and payments on weekends - put them in ONE table with a
# "test" column.
pm = pay.merge(suppliers, on="supplier_id")
tests = pd.concat([
    pm[pm["paid_to_account"] != pm["bank_account"]].assign(test="wrong bank account"),
    pm[pm["status"] == "Blocked"].assign(test="blocked supplier"),
    pm[pm["date"].dt.dayofweek >= 5].assign(test="weekend"),
])
print(tests[["payment_id", "supplier_name", "date", "amount", "test"]])

# TASK 12: SUPPLIER MASTER: find suppliers whose names start with the same word,
# suppliers sharing a bank account, and suppliers whose account is an employee's.
suppliers["first_word"] = suppliers["supplier_name"].str.split().str[0]
print(suppliers[suppliers["first_word"].duplicated(keep=False)][["supplier_id", "supplier_name"]])
print(suppliers[suppliers["bank_account"].duplicated(keep=False)][["supplier_id", "bank_account"]])
print(suppliers.merge(employees, on="bank_account")[["supplier_name", "employee_name"]])

# TASK 13: ROUND AMOUNTS. For each supplier, what % of its invoices are whole
# hundreds (e.g. 4,500.00)? Real invoices are rarely round.
inv["round"] = inv["amount"] % 100 == 0
print((inv.groupby("supplier_name")["round"].mean() * 100).round(0).sort_values(ascending=False))

# TASK 14: The approval limit for invoices is 20,000. List invoices between 19,000
# and 19,999.99, and count invoices above 20,000.
print(inv[inv["amount"].between(19000, 19999.99)][["invoice_no", "supplier_name", "amount"]])
print("Above 20,000:", (inv["amount"] > 20000).sum())

# TASK 15: YEAR-END PAYABLES LISTING per supplier (invoices - payments up to 31 Dec).
# Show suppliers with a DEBIT balance (we paid too much).
by_sup = (inv.groupby("supplier_id")["amount"].sum()
          .sub(pay.groupby("supplier_id")["amount"].sum(), fill_value=0).round(2))
print(by_sup, "\nTotal:", round(by_sup.sum(), 2))
print("Debit balances:", by_sup[by_sup < 0].to_dict() or "none")
# Tip: a supplier can look fine in total but hide an overpaid invoice inside
# (look at Coastal Packaging's invoice CO-71040 from task 9).

# TASK 16: Age the open INVOICES at year end by days past the due date
# (not due, 1-30, 31-60, 60+).
inv["paid"] = inv["invoice_no"].map(pay.groupby("invoice_no")["amount"].sum()).fillna(0)
open_inv = inv[(inv["amount"] - inv["paid"]).round(2) > 0].copy()
open_inv["open"] = open_inv["amount"] - open_inv["paid"]
open_inv["band"] = pd.cut((YEAR_END - open_inv["due_date"]).dt.days, [-10_000, 0, 30, 60, 10_000],
                          labels=["not due", "1-30", "31-60", "60+"])
print(open_inv.groupby("band", observed=False)["open"].sum().round(2))

# TASK 17: UNRECORDED LIABILITIES. From the 2026 payments, list those for 2025
# costs (invoice dated on/before 31 Dec) whose invoice is NOT in ap_invoices.
# Only report items over 1,000.
u = pay26[(pay26["invoice_date"] <= YEAR_END) & ~pay26["invoice_no"].isin(inv["invoice_no"])
          & (pay26["amount"] > 1000)]
print(u[["supplier_id", "invoice_no", "invoice_date", "amount", "description"]])
print("Total:", u["amount"].sum())

# TASK 18: TOTAL UNDERSTATEMENT of liabilities = GRNI (task 4) + unrecorded
# liabilities (task 17). Is it more than performance materiality of 30,000?
under = grni["amount_received"].sum() + u["amount"].sum()
print(f"Understatement {under:,.2f} ->", "MATERIAL - propose adjustment" if under > 30000 else "below threshold")

# TASK 19: SUPPLIER STATEMENT. Load supplier_statement_S006.csv. Find the
# statement invoices that are not in our books and the payments we made that are
# not on the statement.
stmt = pd.read_csv(DATA / "supplier_statement_S006.csv")
s_inv = stmt[stmt["invoice"].notna()]
print(s_inv[~s_inv["ref"].isin(inv["invoice_no"])][["date", "ref", "invoice"]])
ours = pay[(pay["supplier_id"] == "S006") & (pay["date"] >= "2025-10-01")]
print(ours[~ours["payment_id"].isin(stmt["ref"])][["payment_id", "date", "amount"]])

# TASK 20: Save output/p6_payables.xlsx with the three-way match issues, the
# payment test table, GRNI and unrecorded liabilities.
with pd.ExcelWriter(OUTPUT / "p6_payables.xlsx") as w:
    m[m["issue"] != ""].to_excel(w, sheet_name="3-way match", index=False)
    tests.to_excel(w, sheet_name="Payment tests", index=False)
    grni.to_excel(w, sheet_name="GRNI", index=False)
    u.to_excel(w, sheet_name="Unrecorded", index=False)
print("Saved output/p6_payables.xlsx")
