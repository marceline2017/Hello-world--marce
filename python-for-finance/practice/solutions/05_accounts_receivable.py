"""
PRACTICE SET 5 - ACCOUNTS RECEIVABLE (20 tasks)
Files: data/customers.csv, data/ar_invoices.csv, data/ar_receipts.csv,
       data/ar_receipts_2026.csv, data/ar_credit_notes_2026.csv
Lesson needed first: 14
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
by_cust = sales25.groupby("customer_name")["amount"].sum().sort_values(ascending=False)
print(by_cust.head(5).round(0))

# TASK 2: Total 2025 sales per month.
print(sales25.groupby(sales25["invoice_date"].dt.month)["amount"].sum().round(0))

# TASK 3: CONCENTRATION. What % of 2025 sales comes from the biggest customer,
# and from the top 3 together?
print(f"Top 1: {by_cust.iloc[0] / by_cust.sum():.1%}   Top 3: {by_cust.head(3).sum() / by_cust.sum():.1%}")

# TASK 4: Average invoice size per customer, and the single largest invoice.
print(sales25.groupby("customer_name")["amount"].mean().round(0).sort_values())
print(sales25.loc[sales25["amount"].idxmax(), ["invoice_no", "customer_name", "amount"]])

# TASK 5: Invoice numbers should be a continuous sequence (INV-25001, INV-25002...).
# Are any numbers missing?
nums = inv["invoice_no"].str.replace("INV-", "").astype(int)
print("Missing:", sorted(set(range(nums.min(), nums.max() + 1)) - set(nums)) or "none")

# TASK 6: Which invoice numbers are used more than once?
print(inv[inv["invoice_no"].duplicated(keep=False)][["invoice_no", "customer_name", "amount"]])

# TASK 7: List invoices whose due date does not match the customer's payment terms.
gap = (inv["due_date"] - inv["invoice_date"]).dt.days
print(inv[gap != inv["payment_terms_days"]][["invoice_no", "customer_name", "payment_terms_days"]]
      .assign(days_given=gap))

# TASK 8: Were any invoices raised for BLOCKED customers?
print(inv[inv["status"] == "Blocked"][["invoice_no", "customer_name", "invoice_date", "amount"]])

# TASK 9: HOW FAST DO CUSTOMERS PAY? For each receipt, days between invoice date and
# receipt date. Show the average per customer next to their terms. Who is slowest?
r = rec[rec["invoice_no"] != ""].merge(inv.drop_duplicates("invoice_no")
                                       [["invoice_no", "invoice_date", "customer_name", "payment_terms_days"]],
                                       on="invoice_no")
r["days_to_pay"] = (r["date"] - r["invoice_date"]).dt.days
speed = r.groupby("customer_name").agg(avg_days=("days_to_pay", "mean"),
                                       terms=("payment_terms_days", "first")).round(0)
speed["late_by"] = speed["avg_days"] - speed["terms"]
print(speed.sort_values("late_by", ascending=False))

# TASK 10: Find receipts that are NOT linked to an invoice, and receipts linked
# to an invoice number that does not exist.
print("Unallocated:\n", rec[rec["invoice_no"] == ""])
print("Unknown invoice:\n", rec[(rec["invoice_no"] != "") & ~rec["invoice_no"].isin(inv["invoice_no"])])

# TASK 11: Balance per customer (invoices - receipts). Prove that the total equals
# total invoices minus total receipts.
bal = inv.groupby("customer_id")["amount"].sum().sub(rec.groupby("customer_id")["amount"].sum(),
                                                     fill_value=0).round(2)
print(bal)
print("Proof:", round(bal.sum(), 2) == round(inv["amount"].sum() - rec["amount"].sum(), 2))

# TASK 12: Open amount per invoice (amount - receipts for that invoice; give the
# cash to the FIRST invoice if a number is used twice). Then age by INVOICE DATE
# (0-30, 31-60, 61-90, 91-180, 181+ days old).
paid = rec[rec["invoice_no"] != ""].groupby("invoice_no")["amount"].sum()
inv["paid"] = inv["invoice_no"].map(paid).fillna(0).where(~inv["invoice_no"].duplicated(), 0)
inv["open"] = (inv["amount"] - inv["paid"]).round(2)
op = inv[inv["open"] > 0].copy()
op["age"] = (YEAR_END - op["invoice_date"]).dt.days
op["age_band"] = pd.cut(op["age"], [-1, 30, 60, 90, 180, 10_000],
                        labels=["0-30", "31-60", "61-90", "91-180", "181+"])
print(op.pivot_table(index="customer_name", columns="age_band", values="open",
                     aggfunc="sum", fill_value=0, observed=False).round(0))

# TASK 13: Which customers have ANY invoice more than 90 days OVERDUE (past the
# due date)? How much is that in total?
op["overdue"] = (YEAR_END - op["due_date"]).dt.days
late90 = op[op["overdue"] > 90]
print(late90.groupby("customer_name")["open"].sum().round(2), "\nTotal:", round(late90["open"].sum(), 2))

# TASK 14: PROVISION. 100% for invoices from 2024 still open (specific provision),
# plus the matrix for the rest: not overdue 1%, 1-90 days overdue 10%, >90 days 50%.
old = op["invoice_date"].dt.year == 2024
rate = pd.cut(op["overdue"], [-10_000, 0, 90, 10_000], labels=[0.01, 0.10, 0.50]).astype(float)
op["provision"] = op["open"] * rate.where(~old, 1.0)
print(f"Specific {op.loc[old, 'provision'].sum():,.2f}  General {op.loc[~old, 'provision'].sum():,.2f}"
      f"  Total {op['provision'].sum():,.2f}")

# TASK 15: DSO per customer = balance / 2025 sales x 365. Which customers are above 90?
dso = (bal / sales25.groupby("customer_id")["amount"].sum() * 365).round(0)
print(dso.sort_values(ascending=False))

# TASK 16: AFTER-DATE CASH. For each customer, what % of the year-end OPEN invoices
# was received in Jan-Feb 2026?
after = rec26.groupby("invoice_no")["amount"].sum()
op["after"] = op["invoice_no"].map(after).fillna(0).clip(upper=op["open"])
pct = op.groupby("customer_name")[["open", "after"]].sum()
pct["%_received"] = (pct["after"] / pct["open"] * 100).round(0)
print(pct.round(0))

# TASK 17: CUT-OFF. List invoices dated 27-31 December and show which were
# cancelled by a credit note in January 2026.
end = inv[inv["invoice_date"] >= "2025-12-27"][["invoice_no", "customer_name", "invoice_date", "amount"]]
end = end.merge(cn26[["invoice_no", "credit_note_no"]], on="invoice_no", how="left")
print(end)

# TASK 18: CONFIRMATION SAMPLE: the 3 customers with the largest balances plus 3
# others chosen at random (random_state=7). Write one letter per customer to
# output/p5_letters/.
b = customers.set_index("customer_id").assign(balance=bal).fillna({"balance": 0})
top3 = b.nlargest(3, "balance")
rand3 = b.drop(top3.index)[lambda x: x["balance"] != 0].sample(3, random_state=7)
sample = pd.concat([top3, rand3])
folder = OUTPUT / "p5_letters"
folder.mkdir(exist_ok=True)
for cid, row in sample.iterrows():
    (folder / f"{cid}.txt").write_text(
        f"To {row['customer_name']}: please confirm your balance at 31 Dec 2025 of "
        f"{row['balance']:,.2f} directly to our auditors.\n")
print(sample[["customer_name", "balance"]])

# TASK 19: The replies came back: C002 says it owes 3,793.40, C010 says 41,874.02,
# and C014 did not reply. Compare each reply with our balance. For a
# disagreement, could the cut-off credit notes explain it? For no reply, what
# would you do instead?
replies = {"C002": 3793.40, "C010": 41874.02, "C014": None}
for cid, said in replies.items():
    ours = b.loc[cid, "balance"]
    if said is None:
        print(f"{cid}: NO REPLY -> alternative procedure: check receipts after year end and invoices/delivery notes")
    else:
        print(f"{cid}: ours {ours:,.2f}  customer {said:,.2f}  difference {ours - said:,.2f}")
print("C002 difference = the 3 cut-off invoices:", cn26.loc[cn26["customer_id"] == "C002", "amount"].sum())

# TASK 20: Save output/p5_receivables.xlsx with your ageing (task 12), provision
# (task 14) and confirmation sample (task 18).
with pd.ExcelWriter(OUTPUT / "p5_receivables.xlsx") as w:
    op.to_excel(w, sheet_name="Open items", index=False)
    sample.to_excel(w, sheet_name="Confirmations")
    pct.to_excel(w, sheet_name="After-date cash")
print("Saved output/p5_receivables.xlsx")
