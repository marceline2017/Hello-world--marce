"""SOLUTION 4 - Files and errors

There is always more than one correct answer. Yours can look different!
"""

from pathlib import Path
DATA = Path(__file__).parent.parent / "data"

# TASK 1: Open data/vendors.csv with the csv module and print only the BLOCKED vendors.
import csv
with open(DATA / "vendors.csv") as f:
    for row in csv.DictReader(f):
        if row["status"] == "Blocked":
            print(row["vendor_name"])

# TASK 2: Read data/general_ledger.csv and count how many entries each user (posted_by) made.
# Use a dictionary as a counter.
with open(DATA / "general_ledger.csv") as f:
    counts = {}
    for row in csv.DictReader(f):
        counts[row["posted_by"]] = counts.get(row["posted_by"], 0) + 1
print(counts)

# TASK 3: Write safe_divide(a, b) that uses try/except ZeroDivisionError and returns None
# when b is 0.
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None

print(safe_divide(10, 2), safe_divide(10, 0))
