"""
make_arap_data.py - creates the files for Lessons 14-15 (receivables and
payables) and practice sets 5-6. It runs automatically at the end of
make_data.py, or alone:   python data/make_arap_data.py

ACCOUNTS RECEIVABLE (money customers owe us)
  customers.csv               - customer master file (credit limit, terms)
  ar_invoices.csv             - sales invoices (some from 2024 still unpaid)
  ar_receipts.csv             - money received from customers in 2025
  ar_receipts_2026.csv        - money received in Jan-Feb 2026 (after year end)
  ar_credit_notes_2026.csv    - credit notes issued in January 2026
  client_ar_aging.csv         - the aged debtors report the client gave us

ACCOUNTS PAYABLE (money we owe suppliers)
  suppliers.csv               - supplier master file (bank account, terms)
  employees.csv               - staff list with bank accounts (for fraud tests)
  purchase_orders.csv         - what we ordered
  goods_received.csv          - what actually arrived
  ap_invoices.csv             - supplier invoices
  ap_payments.csv             - payments made in 2025
  ap_payments_2026.csv        - payments made in Jan-Feb 2026
  supplier_statement_S006.csv - a statement sent to us by one supplier

All made up. Problems are hidden on purpose.
"""

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
rng = random.Random(1414)
YEAR_END = date(2025, 12, 31)


def write_csv(name, rows):
    with open(HERE / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{name:<28}-> {len(rows)} rows")


def money(low, high):
    return round(math.exp(rng.uniform(math.log(low), math.log(high))), 2)


def weekday(d):
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


# =====================================================================
# ACCOUNTS RECEIVABLE
# =====================================================================
CUSTOMERS = [
    # id, name, credit limit, terms, status, payer type
    ("C001", "Acme Corp", 150000, 30, "Active", "good"),
    ("C002", "Beta Ltd", 120000, 30, "Active", "good"),
    ("C003", "Gamma Inc", 80000, 45, "Active", "good"),
    ("C004", "Delta Co", 60000, 30, "Active", "slow"),
    ("C005", "Omega Traders", 100000, 60, "Active", "good"),
    ("C006", "Zeta Retail", 50000, 30, "Active", "good"),
    ("C007", "Kappa Foods", 90000, 45, "Active", "good"),
    ("C008", "Lambda Stores", 70000, 30, "Active", "good"),
    ("C009", "Sigma Hardware", 40000, 30, "Active", "slow"),
    ("C010", "Theta Pharma", 130000, 60, "Active", "good"),
    ("C011", "Nova Builders", 40000, 30, "Active", "bad"),
    ("C012", "Orion Hotels", 60000, 45, "Active", "good"),
    ("C013", "Vega Motors", 30000, 30, "Blocked", "good"),
    ("C014", "Polar Logistics", 50000, 30, "Active", "bad"),
]


def make_ar():
    cust = {c[0]: c for c in CUSTOMERS}
    write_csv("customers.csv", [
        {"customer_id": c[0], "customer_name": c[1], "credit_limit": c[2],
         "payment_terms_days": c[3], "status": c[4]} for c in CUSTOMERS])

    invoices, receipts, receipts_2026 = [], [], []
    inv_no, rec_no = 25000, 7000

    def add_invoice(cid, d, amount, due_days=None):
        nonlocal inv_no
        inv_no += 1
        terms = cust[cid][3]
        inv = {"invoice_no": f"INV-{inv_no}", "customer_id": cid,
               "invoice_date": d.isoformat(),
               "due_date": (d + timedelta(days=due_days or terms)).isoformat(),
               "amount": amount}
        invoices.append(inv)
        return inv

    def add_receipt(cid, d, amount, invoice_no):
        nonlocal rec_no
        rec_no += 1
        row = {"receipt_id": f"RC-{rec_no}", "customer_id": cid, "date": d.isoformat(),
               "amount": amount, "invoice_no": invoice_no}
        (receipts if d <= YEAR_END else receipts_2026).append(row)

    # Old unpaid invoices from 2024 (opening balances)
    for cid, d, amt in [("C011", date(2024, 9, 14), 8650.00),
                        ("C014", date(2024, 11, 2), 12480.50),
                        ("C014", date(2024, 12, 10), 5310.75)]:
        add_invoice(cid, d, amt)

    active = [c for c in cust if cust[c][4] == "Active"]
    for m in range(1, 13):
        for _ in range(rng.randint(24, 30)):
            cid = rng.choice(active)
            d = weekday(date(2025, m, rng.randint(1, 28)))
            inv = add_invoice(cid, d, money(800, 28000))
            kind = cust[cid][5]
            due = date.fromisoformat(inv["due_date"])
            if kind == "bad" and m >= 6:
                continue                                   # stopped paying
            delay = {"good": rng.randint(-10, 8), "slow": rng.randint(20, 75),
                     "bad": rng.randint(30, 60)}[kind]
            pay_day = weekday(due + timedelta(days=delay))
            if pay_day > date(2026, 2, 27):
                continue                                   # not yet paid
            if rng.random() < 0.08:                        # paid in two halves
                part = round(inv["amount"] / 2, 2)
                add_receipt(cid, pay_day, part, inv["invoice_no"])
                later = weekday(pay_day + timedelta(days=30))
                add_receipt(cid, later, round(inv["amount"] - part, 2), inv["invoice_no"])
            else:
                add_receipt(cid, pay_day, inv["amount"], inv["invoice_no"])

    # ---- Hidden problems ----
    # a) Blocked customer still invoiced
    add_invoice("C013", date(2025, 11, 18), 14250.00)
    # b) Due date does not match terms (90 days instead of 30)
    for inv in [i for i in invoices if i["customer_id"] == "C008"][3:5]:
        inv["due_date"] = (date.fromisoformat(inv["invoice_date"]) + timedelta(days=90)).isoformat()
    # c) Customer paid one invoice twice -> credit balance
    paid_c006 = [r for r in receipts if r["customer_id"] == "C006"]
    dup = dict(paid_c006[len(paid_c006) // 2])          # a mid-year receipt
    add_receipt("C006", weekday(date.fromisoformat(dup["date"]) + timedelta(days=6)),
                dup["amount"], dup["invoice_no"])
    # d) Receipt that nobody allocated to an invoice
    add_receipt("C005", date(2025, 12, 19), 7420.00, "")
    # e) The same invoice number used twice
    twin = dict(invoices[120])
    twin.update(customer_id="C003", amount=6180.40)
    invoices.append(twin)
    # f) Cut-off: big invoices at year end, reversed by credit notes in January
    credit_notes = []
    for n, (d, amt) in enumerate([(date(2025, 12, 29), 38500.00),
                                  (date(2025, 12, 30), 42750.00),
                                  (date(2025, 12, 31), 27900.00)], start=1):
        inv = add_invoice("C002", d, amt)
        credit_notes.append({"credit_note_no": f"CN-26{n:03d}", "customer_id": "C002",
                             "date": date(2026, 1, 6 + n).isoformat(),
                             "invoice_no": inv["invoice_no"], "amount": amt,
                             "reason": "Goods not delivered - invoice raised in error"})
    credit_notes.append({"credit_note_no": "CN-26004", "customer_id": "C007",
                         "date": "2026-01-20", "invoice_no": "", "amount": 650.00,
                         "reason": "Price discount January order"})

    invoices.sort(key=lambda r: (r["invoice_date"], r["invoice_no"]))
    receipts.sort(key=lambda r: r["date"])
    receipts_2026.sort(key=lambda r: r["date"])
    write_csv("ar_invoices.csv", invoices)
    write_csv("ar_receipts.csv", receipts)
    write_csv("ar_receipts_2026.csv", receipts_2026)
    write_csv("ar_credit_notes_2026.csv", credit_notes)

    # ---- The client's aged debtors report (with mistakes) ----
    paid = {}
    for r in receipts:
        if r["invoice_no"]:
            paid[r["invoice_no"]] = paid.get(r["invoice_no"], 0) + r["amount"]
    buckets = ["current", "1_30", "31_60", "61_90", "over_90"]
    report = {c: dict.fromkeys(buckets, 0.0) for c in cust}
    for inv in invoices:
        open_amt = round(inv["amount"] - paid.get(inv["invoice_no"], 0), 2)
        paid[inv["invoice_no"]] = max(paid.get(inv["invoice_no"], 0) - inv["amount"], 0)
        if open_amt <= 0:
            continue
        overdue = (YEAR_END - date.fromisoformat(inv["due_date"])).days
        b = ("current" if overdue <= 0 else "1_30" if overdue <= 30 else
             "31_60" if overdue <= 60 else "61_90" if overdue <= 90 else "over_90")
        report[inv["customer_id"]][b] += open_amt
    # Mistake 1: Polar Logistics' old debt shown as current
    report["C014"]["current"] += report["C014"]["over_90"]
    report["C014"]["over_90"] = 0.0
    # Mistake 2: unallocated cash and credit balances simply left out
    rows = []
    for c in cust:
        r = {k: round(v, 2) for k, v in report[c].items()}
        r = {"customer_id": c, "customer_name": cust[c][1], **r, "total": round(sum(r.values()), 2)}
        if r["total"]:
            rows.append(r)
    write_csv("client_ar_aging.csv", rows)


# =====================================================================
# ACCOUNTS PAYABLE
# =====================================================================
SUPPLIERS = [
    # id, name, bank account, terms, status, created
    ("S001", "Prime Goods Wholesale", "01-2233-4455", 30, "Active", "2019-03-01"),
    ("S002", "Metro Power & Water", "02-7788-1100", 15, "Active", "2018-01-15"),
    ("S003", "Skyline Properties", "03-5566-7788", 30, "Active", "2017-06-30"),
    ("S004", "Sunrise Office Supplies", "01-9900-1122", 30, "Active", "2020-02-11"),
    ("S005", "Global Travel Ltd", "04-3344-5566", 30, "Active", "2021-08-19"),
    ("S006", "BrightPath Consulting", "05-6677-8899", 45, "Active", "2022-04-04"),
    ("S007", "Coastal Packaging", "02-1212-3434", 30, "Active", "2020-10-10"),
    ("S008", "Highland Logistics", "06-4545-6767", 30, "Active", "2019-12-01"),
    ("S009", "Quick Fix Services", "07-8989-0101", 30, "Blocked", "2023-05-05"),
    ("S010", "Apex Legal Advisors", "08-2323-4545", 30, "Active", "2016-09-09"),
    ("S011", "Fast Supplies Ltd", "09-1357-2468", 7, "Active", "2025-09-22"),
    ("S012", "Skyline Property Mgmt", "03-5566-7788", 30, "Active", "2025-10-03"),
]

EMPLOYEES = [("E01", "Amina Otieno"), ("E02", "Brian Mwangi"), ("E03", "Chen Wei"),
             ("E04", "Diana Njeri"), ("E05", "Elijah Kamau"), ("E06", "Fatma Ali"),
             ("E07", "George Ochieng"), ("E08", "Hellen Wanjiru")]


def make_ap():
    sup = {s[0]: s for s in SUPPLIERS}
    write_csv("suppliers.csv", [
        {"supplier_id": s[0], "supplier_name": s[1], "bank_account": s[2],
         "payment_terms_days": s[3], "status": s[4], "created_date": s[5]}
        for s in SUPPLIERS])
    emp_rows = []
    for i, (eid, name) in enumerate(EMPLOYEES):
        acct = f"1{i}-{rng.randint(1000, 9999)}-{rng.randint(1000, 9999)}"
        if eid == "E07":
            acct = "09-1357-2468"          # same bank account as supplier S011!
        emp_rows.append({"employee_id": eid, "employee_name": name, "bank_account": acct})
    write_csv("employees.csv", emp_rows)

    pos, grns, invs, pays, pays_2026 = [], [], [], [], []
    po_no, grn_no, pay_no = 5000, 8000, 3000

    def pay(sid, d, amount, invoice_no, account=None):
        nonlocal pay_no
        pay_no += 1
        row = {"payment_id": f"PY-{pay_no}", "supplier_id": sid, "date": d.isoformat(),
               "amount": amount, "invoice_no": invoice_no,
               "paid_to_account": account or sup[sid][2]}
        (pays if d <= YEAR_END else pays_2026).append(row)

    regular = ["S001", "S002", "S003", "S004", "S005", "S006", "S007", "S008", "S010"]
    for m in range(1, 13):
        for _ in range(rng.randint(16, 20)):
            sid = rng.choice(regular)
            d = weekday(date(2025, m, rng.randint(1, 26)))
            po_no += 1
            po_amt = money(500, 25000)
            po = f"PO-{po_no}"
            pos.append({"po_number": po, "supplier_id": sid, "po_date": d.isoformat(),
                        "po_amount": po_amt})
            recv = weekday(d + timedelta(days=rng.randint(2, 10)))
            grn_no += 1
            grns.append({"grn_number": f"GRN-{grn_no}", "po_number": po,
                         "date_received": recv.isoformat(), "amount_received": po_amt})
            inv_d = weekday(recv + timedelta(days=rng.randint(0, 5)))
            inv_no = f"{sup[sid][1][:2].upper()}-{rng.randint(10000, 99999)}"
            due = inv_d + timedelta(days=sup[sid][3])
            invs.append({"invoice_no": inv_no, "supplier_id": sid, "po_number": po,
                         "invoice_date": inv_d.isoformat(), "due_date": due.isoformat(),
                         "amount": po_amt})
            pay_day = weekday(due + timedelta(days=rng.randint(-5, 6)))
            if pay_day <= date(2026, 2, 27):
                pay(sid, pay_day, po_amt, inv_no)

    # ---- Hidden problems ----
    # a) Invoice more than the purchase order
    for inv in invs[30:32]:
        inv["amount"] = round(inv["amount"] * 1.15, 2)
    # b) Invoice with a PO but no goods received
    for inv in invs[60:62]:
        grns[:] = [g for g in grns if g["po_number"] != inv["po_number"]]
    # c) The same invoice entered twice ("A" added to the number)
    twin = dict(invs[90])
    twin["invoice_no"] += "A"
    invs.append(twin)
    pay(twin["supplier_id"], weekday(date.fromisoformat(twin["due_date"]) + timedelta(days=2)),
        twin["amount"], twin["invoice_no"])
    # d) One invoice paid twice
    p = pays[100]
    pay(p["supplier_id"], weekday(date.fromisoformat(p["date"]) + timedelta(days=9)),
        p["amount"], p["invoice_no"])
    # e) Payment to a bank account that is NOT the supplier's
    pays[140]["paid_to_account"] = "11-0000-9999"
    # f) Paid before the invoice date
    p = pays[160]
    inv = next(i for i in invs if i["invoice_no"] == p["invoice_no"])
    p["date"] = (date.fromisoformat(inv["invoice_date"]) - timedelta(days=3)).isoformat()
    # g) Ghost supplier S011 (bank account = an employee's): no POs, round amounts
    for d, amt in [(date(2025, 10, 6), 4500.00), (date(2025, 10, 27), 6000.00),
                   (date(2025, 11, 17), 5500.00), (date(2025, 12, 8), 7000.00)]:
        n = f"FS-{d.month:02d}{d.day:02d}"
        invs.append({"invoice_no": n, "supplier_id": "S011", "po_number": "",
                     "invoice_date": d.isoformat(),
                     "due_date": (d + timedelta(days=7)).isoformat(), "amount": amt})
        pay("S011", d + timedelta(days=2), amt, n)
    # h) Blocked supplier paid
    invs.append({"invoice_no": "QF-7781", "supplier_id": "S009", "po_number": "",
                 "invoice_date": "2025-12-05", "due_date": "2026-01-04", "amount": 3850.00})
    pay("S009", date(2025, 12, 7), 3850.00, "QF-7781")      # a Sunday!

    # i) Unrecorded liabilities: paid in January for 2025 costs, never recorded
    for d, sid, amt, inv_no, inv_date, desc in [
        (date(2026, 1, 12), "S002", 4380.60, "ME-88120", "2025-12-31", "Electricity December 2025"),
        (date(2026, 1, 19), "S010", 18500.00, "AP-2025-12", "2025-12-20", "Legal fees Oct-Dec 2025"),
        (date(2026, 1, 26), "S008", 2950.00, "HI-55102", "2025-12-29", "Transport of December stock"),
        (date(2026, 1, 15), "S005", 3120.00, "GL-60001", "2026-01-08", "Staff travel January 2026"),
        (date(2026, 2, 9), "S004", 860.40, "SU-61002", "2026-01-30", "Stationery January 2026")]:
        pay_no += 1
        pays_2026.append({"payment_id": f"PY-{pay_no}", "supplier_id": sid,
                          "date": d.isoformat(), "amount": amt, "invoice_no": inv_no,
                          "paid_to_account": sup[sid][2], "invoice_date": inv_date,
                          "description": desc})
    for p in pays_2026:
        if "description" not in p:
            inv = next(i for i in invs if i["invoice_no"] == p["invoice_no"])
            p["invoice_date"] = inv["invoice_date"]
            p["description"] = "Payment of recorded invoice"

    # k) Goods received in late December, no invoice yet (accrual needed)
    for d, sid, amt in [(date(2025, 12, 22), "S001", 15840.00),
                        (date(2025, 12, 23), "S007", 3275.50),
                        (date(2025, 12, 30), "S001", 9420.80)]:
        po_no += 1
        grn_no += 1
        pos.append({"po_number": f"PO-{po_no}", "supplier_id": sid,
                    "po_date": (d - timedelta(days=4)).isoformat(), "po_amount": amt})
        grns.append({"grn_number": f"GRN-{grn_no}", "po_number": f"PO-{po_no}",
                     "date_received": d.isoformat(), "amount_received": amt})

    # j) A BrightPath payment made on 30 Dec (it reaches them in January)
    move = next(p for p in pays_2026 if p["supplier_id"] == "S006")
    pays_2026.remove(move)
    move["date"] = "2025-12-30"
    for k in ("invoice_date", "description"):
        move.pop(k)
    pays.append(move)

    # ---- Statement from BrightPath Consulting (S006) ----
    ledger = sorted([i for i in invs if i["supplier_id"] == "S006"
                     and i["invoice_date"] >= "2025-10-01"], key=lambda i: i["invoice_date"])
    paid_s006 = [p for p in pays if p["supplier_id"] == "S006" and p["date"] >= "2025-10-01"]
    stmt = []
    for i in ledger:
        amt = i["amount"]
        if i is ledger[1]:
            amt = round(amt + 450.00, 2)                    # supplier charged more
        stmt.append((i["invoice_date"], i["invoice_no"], "Invoice", amt, 0.0))
    for p in paid_s006:
        if p["date"] >= "2025-12-29":
            continue                                        # payment in transit
        stmt.append((p["date"], p["payment_id"], "Payment received - thank you", 0.0, p["amount"]))
    stmt.append(("2025-12-30", "BP-99117", "Invoice - December advisory", 6200.00, 0.0))
    stmt.sort()
    # Opening = what we owed at 30 Sep (invoices before Oct not yet paid before Oct)
    opening = round(sum(i["amount"] for i in invs if i["supplier_id"] == "S006"
                        and i["invoice_date"] < "2025-10-01")
                    - sum(p["amount"] for p in pays if p["supplier_id"] == "S006"
                          and p["date"] < "2025-10-01"), 2)
    bal = opening
    rows = [{"date": "2025-10-01", "ref": "", "description": "Balance brought forward",
             "invoice": "", "payment": "", "balance": f"{opening:.2f}"}]
    for d, ref, desc, dr, cr in stmt:
        bal = round(bal + dr - cr, 2)
        rows.append({"date": d, "ref": ref, "description": desc,
                     "invoice": f"{dr:.2f}" if dr else "", "payment": f"{cr:.2f}" if cr else "",
                     "balance": f"{bal:.2f}"})
    write_csv("supplier_statement_S006.csv", rows)

    invs.sort(key=lambda r: r["invoice_date"])
    pays.sort(key=lambda r: r["date"])
    pays_2026.sort(key=lambda r: r["date"])
    write_csv("purchase_orders.csv", pos)
    write_csv("goods_received.csv", grns)
    write_csv("ap_invoices.csv", invs)
    write_csv("ap_payments.csv", pays)
    write_csv("ap_payments_2026.csv", pays_2026)


def main():
    make_ar()
    make_ap()


if __name__ == "__main__":
    main()
    print("Done! Receivables and payables data is ready.")
