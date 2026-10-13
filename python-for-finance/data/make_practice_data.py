"""
make_practice_data.py - creates the extra files for Lessons 11-13 and the
practice sets. It runs automatically at the end of make_data.py, but you
can also run it alone (after make_data.py has run once):

    python data/make_practice_data.py

Files it makes (all made-up):

  BANK RECONCILIATION (December 2025)
    cash_book_dec.csv         - the company's own record of the bank account
    bank_statement_dec.csv    - what the bank says happened
    outstanding_nov.csv       - cheques still outstanding on last month's rec
    client_bank_rec_dec.csv   - the reconciliation the client prepared
                                (it has mistakes - you will find them!)

  BUDGET
    budget_2025.csv           - monthly budget per account
    prior_year_2024.csv       - last year's actual totals per account

  DOUBLE-ENTRY JOURNALS
    journal_lines.csv         - every journal line (debit / credit) for 2025
    client_trial_balance.csv  - the trial balance the client gave us
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
rng = random.Random(2025)   # own random generator so other files don't change


def write_csv(name, rows, fields=None):
    fields = fields or list(rows[0])
    with open(HERE / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"{name:<26}-> {len(rows)} rows")


# =====================================================================
# 1. BANK RECONCILIATION DATA
# =====================================================================
def make_bank_data():
    d = lambda day: date(2025, 12, day)
    book_opening = 85_000.00
    stale_cheque = ("CHQ-0950", date(2025, 6, 12), "Quick Fix Services", 780.00)
    nov_cheque = ("CHQ-1088", date(2025, 11, 28), "Skyline Properties", 2300.00)
    bank_opening = book_opening + stale_cheque[3] + nov_cheque[3]

    # ---- Cash book: (date, ref, payee/payer, receipt, payment)
    book = []
    customers = ["Acme Corp", "Beta Ltd", "Gamma Inc", "Delta Co", "Omega Traders"]
    receipt_days = [1, 3, 4, 8, 10, 11, 15, 17, 19, 22, 24, 29, 31]
    for n, day in enumerate(receipt_days, start=1):
        amt = round(rng.uniform(2500, 18000), 2)
        who = rng.choice(customers)
        if day == 10:
            who, amt = "Beta Ltd", 3400.00          # this cheque will bounce
        book.append([d(day), f"DEP-{1200 + n}", who, amt, 0.0])

    payees = ["Skyline Properties", "Metro Power & Water", "Sunrise Office Supplies",
              "Global Travel Ltd", "Prime Goods Wholesale", "BrightPath Consulting"]
    cheque_days = [1, 2, 3, 5, 5, 8, 9, 10, 12, 15, 16, 17, 18, 19, 22, 23, 24, 29, 30, 31]
    for n, day in enumerate(cheque_days, start=1):
        amt = round(rng.uniform(300, 9000), 2)
        if n == 12:
            amt = 1245.00            # bank will clear 1,425.00 (transposition)
        if n == 20:
            amt = 2150.00            # the cheque the client "forgets"
        book.append([d(day), f"CHQ-{1100 + n}", rng.choice(payees), 0.0, amt])

    for day, ref, who, amt in [(5, "EFT-3001", "Kenya Revenue Authority", 6420.00),
                               (12, "EFT-3002", "Prime Goods Wholesale", 11875.40),
                               (26, "EFT-3003", "December salaries", 28450.00)]:
        book.append([d(day), ref, who, 0.0, amt])

    book.sort(key=lambda r: (r[0], r[1]))
    balance = book_opening
    book_rows = []
    for dt, ref, who, rec, pay in book:
        balance = round(balance + rec - pay, 2)
        book_rows.append({"date": dt.isoformat(), "ref": ref, "details": who,
                          "receipt": f"{rec:.2f}" if rec else "",
                          "payment": f"{pay:.2f}" if pay else "",
                          "balance": f"{balance:.2f}"})
    book_closing = balance

    # ---- Bank statement: what actually went through the bank
    bank = []   # (date, description, debit=money out, credit=money in)
    bank.append([d(3), "CHQ 1088", nov_cheque[3], 0.0])        # last month's cheque
    outstanding_dec, deposit_in_transit = [], []
    for dt, ref, who, rec, pay in book:
        kind, num = ref.split("-")
        if kind == "DEP":
            if dt.day == 31:
                deposit_in_transit.append((ref, rec))
                continue
            bank.append([dt + timedelta(days=rng.choice([0, 1])), f"DEP {num}", 0.0, rec])
        elif kind == "CHQ":
            if dt.day >= 29:
                outstanding_dec.append((ref, pay))
                continue
            clear = min(dt + timedelta(days=rng.randint(2, 5)), d(31))
            amount = 1425.00 if pay == 1245.00 else pay
            bank.append([clear, f"CHQ {num}", amount, 0.0])
        else:
            bank.append([dt, f"EFT {num} {who.upper()[:18]}", pay, 0.0])

    bank_only = [[d(15), "DD AFRICA INSURANCE", 1200.00, 0.0],
                 [d(18), "RETURNED CHQ BETA LTD", 3400.00, 0.0],
                 [d(31), "BANK CHARGES DEC", 145.50, 0.0],
                 [d(31), "INTEREST CREDIT", 0.0, 62.30]]
    bank += bank_only
    bank.sort(key=lambda r: (r[0], r[1]))
    balance = bank_opening
    bank_rows = [{"date": d(1).isoformat(), "description": "BALANCE BROUGHT FORWARD",
                  "debit": "", "credit": "", "balance": f"{bank_opening:.2f}"}]
    for dt, desc, dr, cr in bank:
        balance = round(balance - dr + cr, 2)
        bank_rows.append({"date": dt.isoformat(), "description": desc,
                          "debit": f"{dr:.2f}" if dr else "",
                          "credit": f"{cr:.2f}" if cr else "",
                          "balance": f"{balance:.2f}"})
    bank_closing = balance

    # ---- Check our own maths: the CORRECT reconciliation must agree
    dit = sum(a for _, a in deposit_in_transit)
    os_cheques = sum(a for _, a in outstanding_dec) + stale_cheque[3]
    adjusted_bank = round(bank_closing + dit - os_cheques, 2)
    adjusted_book = round(book_closing - 1200 - 3400 - 145.50 + 62.30 - 180.00, 2)
    assert adjusted_bank == adjusted_book, (adjusted_bank, adjusted_book)

    # ---- Last month's outstanding cheques
    write_csv("outstanding_nov.csv", [
        {"ref": r, "date_written": dt.isoformat(), "payee": p, "amount": f"{a:.2f}"}
        for r, dt, p, a in [stale_cheque, nov_cheque]])

    # ---- The client's reconciliation - with two mistakes and a "plug"
    client = [("Balance per bank statement 31 Dec 2025", bank_closing)]
    for ref, a in deposit_in_transit:
        client.append((f"Add: deposit in transit {ref}", a))
    for ref, a in outstanding_dec:
        if ref != "CHQ-1120":                        # mistake 1: one cheque left out
            client.append((f"Less: outstanding cheque {ref}", -a))
    client.append((f"Less: outstanding cheque {stale_cheque[0]}", -stale_cheque[3]))
    client_adj_bank = round(sum(a for _, a in client), 2)
    client.append(("ADJUSTED BANK BALANCE", client_adj_bank))
    book_side = [("Balance per cash book 31 Dec 2025", book_closing),
                 ("Less: direct debit - insurance", -1200.00),
                 ("Less: returned cheque - Beta Ltd", -3400.00),
                 ("Less: bank charges", -145.50),
                 ("Add: interest received", 62.30)]   # mistake 2: no transposition fix
    client_adj_book = round(sum(a for _, a in book_side), 2)
    client += book_side
    client.append(("ADJUSTED CASH BOOK BALANCE", client_adj_book))
    client.append(("Unreconciled difference - written off to sundry expenses",
                   round(client_adj_bank - client_adj_book, 2)))
    write_csv("client_bank_rec_dec.csv",
              [{"line": i, "description": t, "amount": f"{a:.2f}"}
               for i, (t, a) in enumerate(client, start=1)])
    write_csv("cash_book_dec.csv", book_rows)
    write_csv("bank_statement_dec.csv", bank_rows)


# =====================================================================
# 2. BUDGET DATA (built from the general ledger)
# =====================================================================
def make_budget_data():
    with open(HERE / "general_ledger.csv") as f:
        gl = list(csv.DictReader(f))
    names, annual = {}, {}
    for r in gl:
        names[r["account"]] = r["account_name"]
        annual[r["account"]] = annual.get(r["account"], 0) + float(r["amount"])

    # How the budget-setter planned each account compared with what happened.
    # (Under 1.0 = budget too low = actual will be OVER budget.)
    plan = {"4000": 1.08, "5000": 1.02, "6100": 1.00, "6200": 1.03,
            "6300": 0.97, "6400": 0.70, "6500": 0.85, "6600": 0.55}
    # Revenue is expected to be higher at year end (seasonality)
    season = [0.07, 0.07, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.09, 0.09, 0.10, 0.10]
    rows = []
    for acc in sorted(annual):
        yearly = annual[acc] * plan[acc]
        for m in range(1, 13):
            share = season[m - 1] if acc == "4000" else 1 / 12
            rows.append({"month": m, "account": acc, "account_name": names[acc],
                         "budget": round(yearly * share, -2)})   # round to 100
    write_csv("budget_2025.csv", rows)

    growth = {"4000": 0.88, "5000": 0.80, "6100": 1.00, "6200": 0.95,
              "6300": 0.93, "6400": 0.45, "6500": 0.90, "6600": 0.40}
    write_csv("prior_year_2024.csv", [
        {"account": a, "account_name": names[a],
         "actual_2024": round(annual[a] * growth[a], 2)} for a in sorted(annual)])


# =====================================================================
# 3. DOUBLE-ENTRY JOURNALS and the client's TRIAL BALANCE
# =====================================================================
CHART = {
    "1000": "Cash at Bank", "1100": "Accounts Receivable", "1200": "Inventory",
    "1500": "Equipment", "2000": "Accounts Payable", "2100": "Accrued Expenses",
    "2500": "Bank Loan", "3000": "Share Capital", "4000": "Sales Revenue",
    "5000": "Cost of Goods Sold", "6100": "Rent Expense", "6200": "Salaries Expense",
    "6300": "Utilities Expense", "6400": "Travel Expense",
    "6800": "Depreciation Expense", "7000": "Interest Expense", "9999": "Suspense",
}


def make_journals():
    lines, jid = [], 0

    def journal(dt, desc, entries, user="system", source="system"):
        """entries = list of (account, debit, credit)"""
        nonlocal jid
        jid += 1
        for n, (acc, dr, cr) in enumerate(entries, start=1):
            lines.append({"journal_id": f"J{jid:04d}", "line": n, "date": dt.isoformat(),
                          "account": acc, "account_name": CHART[acc],
                          "debit": f"{dr:.2f}" if dr else "",
                          "credit": f"{cr:.2f}" if cr else "",
                          "description": desc, "source": source, "posted_by": user})

    journal(date(2025, 1, 1), "Opening balances",
            [("1000", 200000, 0), ("1500", 200000, 0),
             ("3000", 0, 330000), ("2500", 0, 70000)], "amina", "manual")

    ar = ap = 0.0      # running totals, so customers only pay what they owe
    for m in range(1, 13):
        for _ in range(rng.randint(14, 18)):
            dt = date(2025, m, rng.randint(1, 28))
            kind = rng.choices(["sale", "receipt", "purchase", "payment", "travel",
                                "utilities"], [5, 5, 3, 3, 1, 1])[0]
            if kind == "sale":
                amt = round(rng.uniform(2000, 25000), 2)
                cost = round(amt * rng.uniform(0.55, 0.65), 2)
                ar += amt
                journal(dt, "Sales invoice", [("1100", amt, 0), ("4000", 0, amt),
                                              ("5000", cost, 0), ("1200", 0, cost)])
            elif kind == "receipt" and ar > 1000:
                amt = round(ar * rng.uniform(0.3, 0.6), 2)
                ar -= amt
                journal(dt, "Customer receipt", [("1000", amt, 0), ("1100", 0, amt)])
            elif kind == "purchase":
                amt = round(rng.uniform(4000, 30000), 2)
                ap += amt
                journal(dt, "Supplier invoice - stock", [("1200", amt, 0), ("2000", 0, amt)])
            elif kind == "payment" and ap > 1000:
                amt = round(ap * rng.uniform(0.3, 0.6), 2)
                ap -= amt
                journal(dt, "Supplier payment", [("2000", amt, 0), ("1000", 0, amt)])
            elif kind == "travel":
                amt = round(rng.uniform(200, 4000), 2)
                journal(dt, "Travel claim", [("6400", amt, 0), ("1000", 0, amt)])
            elif kind == "utilities":
                amt = round(rng.uniform(150, 3000), 2)
                journal(dt, "Utilities bill", [("6300", amt, 0), ("2000", 0, amt)])
        end = date(2025, m, 28)
        journal(end, "Monthly rent", [("6100", 4500, 0), ("1000", 0, 4500)])
        journal(end, "Monthly salaries", [("6200", 12800, 0), ("1000", 0, 12800)])
        journal(end, "Monthly depreciation", [("6800", 3333.33, 0), ("1500", 0, 3333.33)])
        journal(end, "Loan interest", [("7000", 580, 0), ("1000", 0, 580)])

    # --------- Hidden problems ---------
    # a) Journals that do not balance (debits are not equal to credits)
    journal(date(2025, 3, 14), "Supplier invoice - stock",
            [("1200", 4870.00, 0), ("2000", 0, 4780.00)], "brian", "manual")
    journal(date(2025, 7, 9), "Travel claim",
            [("6400", 1250.00, 0), ("1000", 0, 1150.00)], "chen", "manual")
    journal(date(2025, 10, 21), "Customer receipt",
            [("1000", 9300.00, 0), ("1100", 0, 3900.00)], "brian", "manual")
    # b) Amounts parked in the suspense account
    journal(date(2025, 8, 30), "Unknown receipt - to investigate",
            [("1000", 6250.00, 0), ("9999", 0, 6250.00)], "diana", "manual")
    journal(date(2025, 11, 30), "Difference - to clear later",
            [("9999", 1875.00, 0), ("6300", 0, 1875.00)], "diana", "manual")
    # c) Management override: big manual revenue on the last day of the year
    journal(date(2025, 12, 31), "Adjustment per CEO - confidential",
            [("1100", 85000.00, 0), ("4000", 0, 85000.00)], "ceo", "manual")
    # d) Weekend manual journal reducing expenses
    journal(date(2025, 12, 27), "Reclass expenses",
            [("1500", 22000.00, 0), ("6200", 0, 22000.00)], "brian", "manual")
    lines.sort(key=lambda r: (r["date"], r["journal_id"], r["line"]))
    write_csv("journal_lines.csv", lines)

    # --------- The client's trial balance (with mistakes) ---------
    tb = {}
    for r in lines:
        tb[r["account"]] = tb.get(r["account"], 0) + float(r["debit"] or 0) - float(r["credit"] or 0)
    tb["6400"] -= 5000.00        # travel understated by 5,000
    tb.pop("9999")               # suspense balance left off the TB
    rows = []
    for acc in sorted(tb):
        net = round(tb[acc], 2)
        rows.append({"account": acc, "account_name": CHART[acc],
                     "debit": f"{net:.2f}" if net > 0 else "",
                     "credit": f"{-net:.2f}" if net < 0 else ""})
    write_csv("client_trial_balance.csv", rows)


def main():
    make_bank_data()
    make_budget_data()
    make_journals()


if __name__ == "__main__":
    main()
    print("Done! Practice data for lessons 11-13 is ready.")
