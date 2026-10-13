"""
LESSON 4 - READING FILES and HANDLING ERRORS
============================================

Real work starts with a file: a bank statement, a ledger export,
an invoice list. Here you learn to open files with plain Python
and to stop your program from crashing when data is bad.

(In Lesson 5 we use pandas, which makes this much easier. But knowing
the basics helps you understand what pandas does for you.)

First make sure the data exists:   python data/make_data.py
Then run:   python lessons/lesson04_files_and_errors.py
"""

import csv                 # "import" loads an extra toolbox
from pathlib import Path   # Path helps find files on any computer

# ---------------------------------------------------------------
# 1. Finding the data folder
# ---------------------------------------------------------------
# __file__ is "this file". .parent goes up one folder.
# So DATA = the "data" folder next to the "lessons" folder.
DATA = Path(__file__).parent.parent / "data"
OUTPUT = Path(__file__).parent.parent / "output"
OUTPUT.mkdir(exist_ok=True)   # make the folder if it is missing

print("Data folder:", DATA)


# ---------------------------------------------------------------
# 2. Reading a CSV file
# ---------------------------------------------------------------
# CSV = "comma separated values". Excel can save any sheet as CSV.
# "with open(...)" opens the file and closes it again automatically.

with open(DATA / "vendors.csv") as f:
    reader = csv.DictReader(f)     # each row becomes a dictionary
    vendors = list(reader)

for v in vendors:
    print(v["vendor_id"], v["vendor_name"], v["status"])


# ---------------------------------------------------------------
# 3. Reading the ledger and doing some sums
# ---------------------------------------------------------------
with open(DATA / "general_ledger.csv") as f:
    ledger = list(csv.DictReader(f))

print(f"\nThe ledger has {len(ledger)} entries")
print("First row:", ledger[0])

# Everything from a CSV is TEXT. Convert amount to float to add it up.
total_by_account = {}
for row in ledger:
    name = row["account_name"]
    amount = float(row["amount"])
    # .get(name, 0) = "current total, or 0 if this is the first time"
    total_by_account[name] = total_by_account.get(name, 0) + amount

print("\nTotal by account:")
for name, total in sorted(total_by_account.items()):
    print(f"  {name:<22}{total:>15,.2f}")


# ---------------------------------------------------------------
# 4. Writing a file
# ---------------------------------------------------------------
# Let's save all entries over 20,000 into a new file for review.
big_entries = [r for r in ledger if float(r["amount"]) > 20000]

with open(OUTPUT / "big_entries.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=ledger[0].keys())
    writer.writeheader()
    writer.writerows(big_entries)

print(f"\nSaved {len(big_entries)} big entries to output/big_entries.csv")

# Writing a simple text file (e.g. a short audit note)
with open(OUTPUT / "note.txt", "w") as f:
    f.write("Audit note\n")
    f.write(f"Entries reviewed: {len(ledger)}\n")
    f.write(f"Entries above 20,000: {len(big_entries)}\n")


# ---------------------------------------------------------------
# 5. ERRORS - and how to handle them with try / except
# ---------------------------------------------------------------
# When Python meets a problem it stops and shows an error message
# called a "traceback". READ THE LAST LINE - it tells you what went wrong:
#   ValueError        - wrong kind of value, e.g. float("abc")
#   KeyError          - dictionary key does not exist
#   ZeroDivisionError - divided by 0
#   FileNotFoundError - the file is not where you said
#   TypeError         - mixing types, e.g. "5" + 5
#   NameError         - you used a variable that does not exist (typo?)
#   IndentationError  - spaces at the start of a line are wrong
#
# try/except says: "TRY this. IF it fails, do this instead of crashing."

messy_amounts = ["1200.50", "850", "n/a", "", "4,000.00", "$2,750.00"]

def to_number(text):
    """Turn messy text into a number. Return None if impossible."""
    cleaned = text.replace(",", "").replace("$", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None

clean = []
bad = []
for value in messy_amounts:
    number = to_number(value)
    if number is None:
        bad.append(value)
    else:
        clean.append(number)

print("\nGood numbers:", clean)
print("Could not read:", bad)
print(f"Total of good numbers: {sum(clean):,.2f}")

# Handling a missing file politely
try:
    with open(DATA / "does_not_exist.csv") as f:
        pass
except FileNotFoundError:
    print("\nThat file was not found - check the name and folder.")


# ---------------------------------------------------------------
# 6. Reading a whole column of messy invoices
# ---------------------------------------------------------------
with open(DATA / "messy_invoices.csv") as f:
    invoices = list(csv.DictReader(f))

print("\nColumn names exactly as in the file:", list(invoices[0].keys()))
# Notice " Customer " has spaces! Real files are messy. Lesson 6 fixes this.


# ===============================================================
# SUMMARY
#   import csv / from pathlib import Path    load tools
#   with open(path) as f:                     open a file safely
#   csv.DictReader(f)                         rows as dictionaries
#   csv.DictWriter(f, fieldnames=...)         write rows
#   try: ... except ValueError: ...           handle errors
#   Always read the LAST line of an error message first.
#
# NEXT: exercises/exercise04.py
# ===============================================================
