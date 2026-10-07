"""
make_data.py - creates the practice data files used in the lessons.

You do NOT need to understand this file yet. Just run it once:

    python data/make_data.py

It makes three fake (made-up) files inside the data folder:

  1. general_ledger.csv  - 1,200 accounting entries for one company in 2025.
                           Some "problems" are hidden inside on purpose so
                           you can find them in the audit lessons.
  2. vendors.csv         - the list of approved suppliers (vendors).
  3. messy_invoices.csv  - a dirty file full of mistakes, for the
                           data cleaning lesson.

The random "seed" makes sure everyone gets exactly the same data.
"""

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
HERE = Path(__file__).parent

ACCOUNTS = {
    "4000": "Sales Revenue",
    "5000": "Cost of Goods Sold",
    "6100": "Rent Expense",
    "6200": "Salaries Expense",
    "6300": "Utilities Expense",
    "6400": "Travel Expense",
    "6500": "Office Supplies",
    "6600": "Consulting Fees",
}

VENDORS = [
    ("V001", "Sunrise Office Supplies", "Approved"),
    ("V002", "Metro Power & Water", "Approved"),
    ("V003", "Skyline Properties", "Approved"),
    ("V004", "Global Travel Ltd", "Approved"),
    ("V005", "BrightPath Consulting", "Approved"),
    ("V006", "Prime Goods Wholesale", "Approved"),
    ("V007", "Quick Fix Services", "Blocked"),
]

# Which vendor is normally used for which account
ACCOUNT_VENDOR = {
    "5000": "V006",
    "6100": "V003",
    "6300": "V002",
    "6400": "V004",
    "6500": "V001",
    "6600": "V005",
}

USERS = ["amina", "brian", "chen", "diana"]


def random_day():
    start = date(2025, 1, 1)
    # Pick a weekday most of the time (real offices post on weekdays)
    while True:
        d = start + timedelta(days=random.randint(0, 364))
        if d.weekday() < 5:
            return d


def log_uniform(low, high):
    """A random amount where small amounts are more common than big ones,
    like real invoices. (This also makes the data follow Benford's Law.)"""
    return round(math.exp(random.uniform(math.log(low), math.log(high))), 2)


def make_general_ledger():
    rows = []
    entry_no = 10000
    for _ in range(1200):
        entry_no += 1
        # Sales entries are more common than any single expense account
        account = random.choices(list(ACCOUNTS), weights=[6, 2, 1, 2, 1, 1, 1, 1])[0]
        if account == "4000":
            amount = log_uniform(1000, 30000)
            vendor = ""
        elif account == "6200":
            amount = log_uniform(3000, 9000)
            vendor = ""
        else:
            amount = log_uniform(50, 8000)
            vendor = ACCOUNT_VENDOR[account]
        rows.append({
            "entry_id": entry_no,
            "date": random_day().isoformat(),
            "account": account,
            "account_name": ACCOUNTS[account],
            "vendor_id": vendor,
            "description": f"{ACCOUNTS[account]} - routine",
            "amount": amount,
            "posted_by": random.choice(USERS),
            "approved_by": "",
        })

    # Every entry of 10,000 or more needs an approver.
    for r in rows:
        if r["amount"] >= 10000:
            others = [u for u in USERS if u != r["posted_by"]]
            r["approved_by"] = random.choice(others)

    # ---------------- Hidden problems for the audit lessons ----------------
    # 1) Exact duplicate payments (same vendor, same amount, same date)
    supplier_rows = [r for r in rows if r["vendor_id"]]
    for r in random.sample(supplier_rows, 6):
        dup = dict(r)
        entry_no += 1
        dup["entry_id"] = entry_no
        rows.append(dup)

    # 2) Entries posted on weekends
    for i in random.sample(range(len(rows)), 8):
        d = date.fromisoformat(rows[i]["date"])
        while d.weekday() < 5:
            d += timedelta(days=1)
        rows[i]["date"] = d.isoformat()

    # 3) Amounts just under the 10,000 approval limit (split to avoid approval)
    for amt in [9950.00, 9990.00, 9875.50, 9999.00, 9920.00]:
        entry_no += 1
        rows.append({
            "entry_id": entry_no, "date": "2025-11-28", "account": "6600",
            "account_name": ACCOUNTS["6600"], "vendor_id": "V005",
            "description": "Consulting Fees - urgent", "amount": amt,
            "posted_by": "diana", "approved_by": "",
        })

    # 4) Big entries where the poster approved their own work
    approved = [r for r in rows if r["approved_by"]]
    for r in random.sample(approved, 4):
        r["approved_by"] = r["posted_by"]

    # 5) Payments to a blocked vendor
    for amt in [4500.00, 3200.00, 7800.00]:
        entry_no += 1
        rows.append({
            "entry_id": entry_no, "date": "2025-12-30", "account": "6600",
            "account_name": ACCOUNTS["6600"], "vendor_id": "V007",
            "description": "Consulting Fees - misc", "amount": amt,
            "posted_by": "brian", "approved_by": "",
        })

    # 6) Suspiciously round amounts
    for amt in [5000.00, 8000.00, 3000.00, 6000.00]:
        entry_no += 1
        rows.append({
            "entry_id": entry_no, "date": random_day().isoformat(),
            "account": "6400", "account_name": ACCOUNTS["6400"],
            "vendor_id": "V004", "description": "Travel Expense - advance",
            "amount": amt, "posted_by": "chen", "approved_by": "",
        })

    # 7) Large entries with NO approval at all
    for acc, amt in [("6100", 18500.00), ("5000", 12740.35), ("6600", 26300.00)]:
        entry_no += 1
        rows.append({
            "entry_id": entry_no, "date": random_day().isoformat(),
            "account": acc, "account_name": ACCOUNTS[acc],
            "vendor_id": ACCOUNT_VENDOR[acc],
            "description": f"{ACCOUNTS[acc]} - adjustment",
            "amount": amt, "posted_by": "brian", "approved_by": "",
        })

    # 8) An unusually large office supplies purchase (an outlier)
    entry_no += 1
    rows.append({
        "entry_id": entry_no, "date": "2025-08-14", "account": "6500",
        "account_name": ACCOUNTS["6500"], "vendor_id": "V001",
        "description": "Office Supplies - laptops", "amount": 24815.60,
        "posted_by": "chen", "approved_by": "amina",
    })

    # 9) Remove a few entry numbers to create gaps in the sequence
    removed = set(random.sample([r["entry_id"] for r in rows[:1200]], 3))
    rows = [r for r in rows if r["entry_id"] not in removed]

    rows.sort(key=lambda r: (r["date"], r["entry_id"]))
    with open(HERE / "general_ledger.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"general_ledger.csv  -> {len(rows)} rows")


def make_vendors():
    with open(HERE / "vendors.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["vendor_id", "vendor_name", "status"])
        writer.writerows(VENDORS)
    print(f"vendors.csv         -> {len(VENDORS)} rows")


def make_messy_invoices():
    rows = [
        ["Invoice No", " Customer ", "Invoice Date", "Amount", "Status"],
        ["INV-001", "acme corp", "2025-01-15", "1,200.50", "Paid"],
        ["INV-002", "  Beta Ltd", "2025-01-20", "$850.00", "paid"],
        ["INV-003", "ACME CORP ", "2025-02-03", "2300", "UNPAID"],
        ["INV-004", "Gamma Inc", "2025-02-10", "", "Unpaid"],
        ["INV-005", "beta ltd", "2025-02-28", "4,000.00", "Paid "],
        ["INV-005", "beta ltd", "2025-02-28", "4,000.00", "Paid "],
        ["INV-006", "Delta Co", "2025-03-05", "1500.75", "unpaid"],
        ["INV-007", "Gamma Inc", "2025-03-18", "n/a", "Paid"],
        ["INV-008", "delta co", "2025-03-30", "$2,750.00", "Unpaid"],
        ["INV-009", "Acme Corp", "2025-04-02", "980", "PAID"],
        ["INV-010", "", "2025-04-15", "640.00", "Unpaid"],
    ]
    with open(HERE / "messy_invoices.csv", "w", newline="") as f:
        csv.writer(f).writerows(rows)
    print(f"messy_invoices.csv  -> {len(rows) - 1} rows")


if __name__ == "__main__":
    make_general_ledger()
    make_vendors()
    make_messy_invoices()
    print("Done! Your practice data is ready.")
