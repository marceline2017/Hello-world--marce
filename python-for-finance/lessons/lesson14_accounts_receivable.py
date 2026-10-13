"""
LESSON 14 - ACCOUNTS RECEIVABLE (money customers owe us)
========================================================

When we sell on credit we send an INVOICE. The customer pays later.
Until they pay, the money is a RECEIVABLE (also called "debtors") - an
asset on the balance sheet.

What can go wrong (and what auditors test):
  EXISTENCE     - is the customer real and do they really owe this?
                  -> confirmations (write to the customer), receipts after year end
  VALUATION     - will we actually get paid? Old debts may never be paid.
                  -> aged analysis, provision for bad debts (expected credit loss)
  CUT-OFF       - were sales put in the right year?
                  -> invoices near year end, credit notes after year end
  ACCURACY      - does the aged report the client gave us add up and is it right?
                  -> rebuild the ageing ourselves from invoices and receipts

Words:  "open" / "outstanding" invoice = not fully paid yet
        "overdue" = past its due date       "DSO" = days sales outstanding

Run:  python lessons/lesson14_accounts_receivable.py
"""

from pathlib import Path
import pandas as pd

DATA = Path(__file__).parent.parent / "data"
OUTPUT = Path(__file__).parent.parent / "output"
OUTPUT.mkdir(exist_ok=True)
pd.set_option("display.width", 150)
pd.set_option("display.max_columns", 20)
YEAR_END = pd.Timestamp("2025-12-31")

customers = pd.read_csv(DATA / "customers.csv")
inv = pd.read_csv(DATA / "ar_invoices.csv", parse_dates=["invoice_date", "due_date"])
rec = pd.read_csv(DATA / "ar_receipts.csv", parse_dates=["date"])
rec26 = pd.read_csv(DATA / "ar_receipts_2026.csv", parse_dates=["date"])
cn26 = pd.read_csv(DATA / "ar_credit_notes_2026.csv", parse_dates=["date"])
client_aging = pd.read_csv(DATA / "client_ar_aging.csv")
rec["invoice_no"] = rec["invoice_no"].fillna("")
print(f"{len(customers)} customers, {len(inv)} invoices, {len(rec)} receipts in 2025")


# ---------------------------------------------------------------
# STEP 1. Check the invoices themselves
# ---------------------------------------------------------------
print("\n--- Invoice checks ---")
dup_no = inv[inv["invoice_no"].duplicated(keep=False)]
print("Invoice numbers used twice:\n", dup_no)

inv = inv.merge(customers, on="customer_id", how="left")
print("\nInvoices to BLOCKED customers:\n",
      inv[inv["status"] == "Blocked"][["invoice_no", "customer_name", "invoice_date", "amount"]])

inv["terms_used"] = (inv["due_date"] - inv["invoice_date"]).dt.days
wrong_terms = inv[inv["terms_used"] != inv["payment_terms_days"]]
print("\nDue date does NOT match the customer's terms:\n",
      wrong_terms[["invoice_no", "customer_name", "payment_terms_days", "terms_used", "amount"]])
# Longer terms than agreed = a salesperson may be giving secret extra credit.


# ---------------------------------------------------------------
# STEP 2. Which invoices are still OPEN at year end?
# ---------------------------------------------------------------
# Because one invoice number is used twice, we give every invoice row its own
# key (row number) and share receipts only once per invoice number.
paid = rec[rec["invoice_no"] != ""].groupby("invoice_no")["amount"].sum()
inv["paid"] = inv["invoice_no"].map(paid).fillna(0)
first = ~inv["invoice_no"].duplicated()          # only the first copy gets the cash
inv.loc[~first, "paid"] = 0
inv["open"] = (inv["amount"] - inv["paid"]).round(2)

overpaid = inv[inv["open"] < 0]
print("\nInvoices paid MORE than once (customer overpaid):\n",
      overpaid[["invoice_no", "customer_name", "amount", "paid", "open"]])
unallocated = rec[rec["invoice_no"] == ""]
print("\nReceipts NOT linked to any invoice (unallocated cash):\n", unallocated)

open_inv = inv[inv["open"] > 0].copy()
print(f"\nOpen invoices at year end: {len(open_inv)}  total {open_inv['open'].sum():,.2f}")


# ---------------------------------------------------------------
# STEP 3. Customer balances = all invoices - all receipts
# ---------------------------------------------------------------
bal = (inv.groupby("customer_id")["amount"].sum()
       .sub(rec.groupby("customer_id")["amount"].sum(), fill_value=0)
       .round(2).rename("balance"))
balances = customers.merge(bal, on="customer_id", how="left").fillna({"balance": 0})
print("\nCUSTOMER BALANCES")
print(balances[["customer_id", "customer_name", "credit_limit", "balance"]].to_string(index=False))
print(f"Total receivables: {balances['balance'].sum():,.2f}")
print("Credit balances (we owe the customer!):",
      balances.loc[balances["balance"] < 0, "customer_name"].tolist())


# ---------------------------------------------------------------
# STEP 4. Credit limit test
# ---------------------------------------------------------------
over = balances[balances["balance"] > balances["credit_limit"]].copy()
over["over_by"] = over["balance"] - over["credit_limit"]
print("\nCUSTOMERS OVER THEIR CREDIT LIMIT:")
print(over[["customer_name", "credit_limit", "balance", "over_by"]].round(0).to_string(index=False))
# Why does this matter? Someone kept selling to a customer who wasn't paying.


# ---------------------------------------------------------------
# STEP 5. AGED ANALYSIS - how late is the money?
# ---------------------------------------------------------------
open_inv["days_overdue"] = (YEAR_END - open_inv["due_date"]).dt.days
open_inv["bucket"] = pd.cut(open_inv["days_overdue"],
                            bins=[-10_000, 0, 30, 60, 90, 10_000],
                            labels=["current", "1_30", "31_60", "61_90", "over_90"])
aging = open_inv.pivot_table(index=["customer_id", "customer_name"], columns="bucket",
                             values="open", aggfunc="sum", fill_value=0, observed=False)
aging["total"] = aging.sum(axis=1)
print("\nOUR AGED DEBTORS REPORT")
print(aging.round(0).to_string())
print("\nBy bucket, % of total:")
print((aging.drop(columns="total").sum() / aging["total"].sum() * 100).round(1))


# ---------------------------------------------------------------
# STEP 6. Compare with the CLIENT'S aged report
# ---------------------------------------------------------------
# Turn both reports into a "long" list: one row per customer per bucket.
# .melt() does this (it is the opposite of a pivot table).
ours = aging.reset_index().drop(columns="customer_name")
ours.columns = [str(c) for c in ours.columns]
ours_long = ours.melt(id_vars="customer_id", var_name="bucket", value_name="ours")
client_long = client_aging.drop(columns="customer_name").melt(
    id_vars="customer_id", var_name="bucket", value_name="client")
cmp = ours_long.merge(client_long, on=["customer_id", "bucket"], how="outer").fillna(0)
cmp["diff"] = (cmp["ours"] - cmp["client"]).round(2)
diffs = cmp[cmp["diff"] != 0]
print("\nDIFFERENCES vs CLIENT AGED REPORT:")
print(diffs.to_string(index=False))
print("""Read this as:
 - Polar Logistics: totals agree but the client moved OVER-90 debt into
   'current'. That hides a bad debt - a VALUATION problem.
 - The client's report shows only unpaid invoices, so the overpaid customer
   (a credit balance) and the unallocated receipt are missing from it.""")


# ---------------------------------------------------------------
# STEP 7. Days Sales Outstanding (DSO)
# ---------------------------------------------------------------
sales_2025 = inv.loc[inv["invoice_date"].dt.year == 2025, "amount"].sum()
dso = balances["balance"].sum() / sales_2025 * 365
print(f"\nSales 2025 {sales_2025:,.0f}   DSO {dso:.0f} days "
      f"(customers take about {dso:.0f} days to pay on average)")


# ---------------------------------------------------------------
# STEP 8. Expected credit loss - a provision matrix
# ---------------------------------------------------------------
# IFRS 9 lets companies use a simple "matrix": the older the debt, the
# higher the % we expect never to collect. (These % are examples.)
rates = {"current": 0.01, "1_30": 0.03, "31_60": 0.10, "61_90": 0.25, "over_90": 0.60}
open_inv["ecl_rate"] = open_inv["bucket"].astype(str).map(rates)
open_inv["ecl"] = open_inv["open"] * open_inv["ecl_rate"]
matrix = open_inv.groupby("bucket", observed=False).agg(gross=("open", "sum"), provision=("ecl", "sum"))
matrix["rate"] = [rates[b] for b in matrix.index]
print("\nPROVISION MATRIX")
print(matrix.round({"gross": 0, "provision": 0, "rate": 2}))
print(f"Total provision needed: {matrix['provision'].sum():,.0f}")


# ---------------------------------------------------------------
# STEP 9. Receipts AFTER year end (the best evidence of existence)
# ---------------------------------------------------------------
# If the customer paid in January, the debt was real at 31 December.
paid_after = rec26.groupby("invoice_no")["amount"].sum()
open_inv["paid_after_ye"] = open_inv["invoice_no"].map(paid_after).fillna(0).clip(upper=open_inv["open"])
cover = open_inv["paid_after_ye"].sum() / open_inv["open"].sum()
print(f"\nReceived in Jan-Feb 2026: {open_inv['paid_after_ye'].sum():,.0f} "
      f"= {cover:.0%} of open invoices")
not_paid = open_inv.groupby("customer_name")[["open", "paid_after_ye"]].sum()
not_paid["still_unpaid"] = not_paid["open"] - not_paid["paid_after_ye"]
print(not_paid.sort_values("still_unpaid", ascending=False).round(0).head(6))


# ---------------------------------------------------------------
# STEP 10. CUT-OFF - credit notes after year end
# ---------------------------------------------------------------
cut = cn26.merge(inv[["invoice_no", "invoice_date", "customer_name"]], on="invoice_no", how="left")
reversing = cut[cut["invoice_date"].notna() & (cut["invoice_date"] <= YEAR_END)]
print("\nJanuary credit notes that CANCEL 2025 invoices:")
print(reversing[["credit_note_no", "date", "invoice_no", "invoice_date", "amount", "reason"]]
      .to_string(index=False))
print(f"2025 sales and receivables are overstated by {reversing['amount'].sum():,.2f}")


# ---------------------------------------------------------------
# STEP 11. Choose customers to CONFIRM and write the letters
# ---------------------------------------------------------------
# Rule: confirm every customer above 30,000 + every customer with a problem.
problem = set(over["customer_id"]) | set(overpaid["customer_id"]) | {"C013"}
balances["confirm"] = (balances["balance"].abs() > 30000) | balances["customer_id"].isin(problem)
selected = balances[balances["confirm"]]
coverage = selected["balance"].abs().sum() / balances["balance"].abs().sum()
print(f"\nConfirming {len(selected)} customers covering {coverage:.0%} of the balance")

letters = OUTPUT / "confirmations"
letters.mkdir(exist_ok=True)
for _, c in selected.iterrows():
    text = f"""Sunrise Trading Ltd
To: {c['customer_name']} ({c['customer_id']})

Dear Sir/Madam,

As part of the audit of our financial statements, please confirm directly
to our auditors the balance you owed us at 31 December 2025.

Our records show a balance of: {c['balance']:,.2f}

[ ] This balance is correct
[ ] This balance is NOT correct - the correct balance is: ____________

Signed: ______________________   Date: ____________
"""
    (letters / f"confirmation_{c['customer_id']}.txt").write_text(text)
print(f"Wrote {len(selected)} confirmation letters to output/confirmations/")

with pd.ExcelWriter(OUTPUT / "ar_workpaper.xlsx") as w:
    balances.to_excel(w, sheet_name="Balances", index=False)
    aging.to_excel(w, sheet_name="Aged analysis")
    matrix.to_excel(w, sheet_name="Provision matrix")
    diffs.to_excel(w, sheet_name="vs client ageing", index=False)
    reversing.to_excel(w, sheet_name="Cut-off", index=False)
    selected.to_excel(w, sheet_name="Confirmations", index=False)
print("Saved output/ar_workpaper.xlsx")


# ===============================================================
# SUMMARY - receivables audit programme in Python
#   1. Invoice checks: duplicates, blocked customers, wrong terms
#   2. Open items: invoices minus receipts per invoice; overpaid; unallocated
#   3. Balances per customer; credit balances; credit limit breaches
#   4. Age the open items with pd.cut -> pivot; compare with client's report
#   5. DSO;  provision matrix (expected credit loss)
#   6. Receipts after year end = existence evidence
#   7. Credit notes after year end = cut-off problem
#   8. Select and write confirmation letters with f-strings
#
# PRACTICE: practice/05_accounts_receivable.py
# ===============================================================
