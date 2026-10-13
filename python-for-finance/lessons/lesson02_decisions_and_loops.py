"""
LESSON 2 - LISTS, DICTIONARIES, DECISIONS (if) and LOOPS (for)
==============================================================

These four ideas are the heart of all programming.
  - list  = many values in one box, in order (like one Excel column)
  - dict  = values with labels (like one Excel row with headers)
  - if    = make a decision
  - for   = repeat something for every item

Run:  python lessons/lesson02_decisions_and_loops.py
"""

# ---------------------------------------------------------------
# 1. LISTS - an ordered collection, written with [ ]
# ---------------------------------------------------------------
monthly_sales = [12000, 15500, 9800, 17250, 14100, 16800]

print(monthly_sales)
print(monthly_sales[0])      # first item. Python counts from 0 (!)
print(monthly_sales[1])      # second item
print(monthly_sales[-1])     # last item
print(monthly_sales[0:3])    # items 0,1,2 (first quarter) - stops BEFORE 3

print(len(monthly_sales))    # how many items -> 6
print(sum(monthly_sales))    # total
print(max(monthly_sales))    # biggest
print(min(monthly_sales))    # smallest
print(sum(monthly_sales) / len(monthly_sales))   # average

monthly_sales.append(18000)  # add a new item at the end
print(monthly_sales)

print(sorted(monthly_sales))                 # smallest to largest
print(sorted(monthly_sales, reverse=True))   # largest to smallest


# ---------------------------------------------------------------
# 2. DICTIONARIES - labels and values, written with { }
# ---------------------------------------------------------------
# Format:  {"label": value, "label": value}
# The label is called a "key".

invoice = {
    "invoice_no": "INV-001",
    "customer": "Acme Corp",
    "amount": 1200.50,
    "paid": False,
}

print(invoice["customer"])        # get a value by its key
print(invoice["amount"])

invoice["paid"] = True            # change a value
invoice["currency"] = "USD"       # add a new key
print(invoice)

# .get() is safer: it does not crash if the key is missing
print(invoice.get("due_date", "no due date"))

# A dictionary is great for lookups, like VLOOKUP in Excel:
account_names = {
    "4000": "Sales Revenue",
    "6100": "Rent Expense",
    "6200": "Salaries Expense",
}
print(account_names["6100"])      # -> Rent Expense


# ---------------------------------------------------------------
# 3. IF - making decisions
# ---------------------------------------------------------------
# Comparison signs:
#   ==  equal (two = signs!)    !=  not equal
#   >   greater                 <   less
#   >=  greater or equal        <=  less or equal
#
# IMPORTANT: the lines "inside" the if must be INDENTED (4 spaces).
# Indentation is how Python knows what belongs together.

amount = 12500
approval_limit = 10000

if amount >= approval_limit:
    print(f"{amount:,} needs manager approval")
else:
    print(f"{amount:,} can be paid directly")

# elif = "else if" - check more conditions in order
variance_pct = 0.07   # actual is 7% above budget

if variance_pct > 0.10:
    print("RED: investigate immediately")
elif variance_pct > 0.05:
    print("AMBER: ask for explanation")
else:
    print("GREEN: within tolerance")

# Combine conditions with  and / or / not
posted_by = "brian"
approved_by = "brian"
if amount >= approval_limit and posted_by == approved_by:
    print("CONTROL FAILURE: person approved their own entry!")


# ---------------------------------------------------------------
# 4. FOR LOOPS - do something for each item
# ---------------------------------------------------------------
# Read it like English: "for each sale in monthly_sales, do this..."

for sale in monthly_sales:
    print(f"Sale: {sale:,}")

# Keep a running total (the "accumulator" pattern - used ALL the time)
total = 0
for sale in monthly_sales:
    total = total + sale        # same as: total += sale
print(f"Total sales: {total:,}")

# enumerate() gives you the position number too
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
for i, sale in enumerate(monthly_sales):
    print(f"{months[i]}: {sale:,}")

# zip() walks through two lists side by side (cleaner than above)
for month, sale in zip(months, monthly_sales):
    print(month, sale)

# range() makes a list of numbers: range(1, 6) -> 1,2,3,4,5
for year in range(1, 6):
    print("Year", year)


# ---------------------------------------------------------------
# 5. LOOP + IF together = an audit test!
# ---------------------------------------------------------------
# A list of dictionaries is like a small table (each dict = a row).
payments = [
    {"id": 1, "vendor": "Sunrise", "amount": 450.00,   "approved_by": "diana"},
    {"id": 2, "vendor": "Skyline", "amount": 15000.00, "approved_by": ""},
    {"id": 3, "vendor": "Metro",   "amount": 980.25,   "approved_by": ""},
    {"id": 4, "vendor": "Global",  "amount": 22000.00, "approved_by": "chen"},
    {"id": 5, "vendor": "Quick",   "amount": 11250.00, "approved_by": ""},
]

print("\n--- Payments over 10,000 with NO approval ---")   # \n = new line
exceptions = []
for p in payments:
    if p["amount"] >= 10000 and p["approved_by"] == "":
        exceptions.append(p)
        print(f"Payment {p['id']} to {p['vendor']}: {p['amount']:,.2f}")

print(f"Found {len(exceptions)} exceptions out of {len(payments)} payments")


# ---------------------------------------------------------------
# 6. List comprehension - a short way to build a list
# ---------------------------------------------------------------
# Long way:
big = []
for p in payments:
    if p["amount"] > 10000:
        big.append(p["id"])
# Short way (same result, one line):
big = [p["id"] for p in payments if p["amount"] > 10000]
print("Big payment IDs:", big)

# Add 16% VAT to every price:
prices = [100, 250, 80]
with_vat = [round(x * 1.16, 2) for x in prices]
print(with_vat)


# ---------------------------------------------------------------
# 7. WHILE loop - repeat until a condition becomes false
# ---------------------------------------------------------------
# How many years until 10,000 grows to 20,000 at 8% interest?
balance = 10000
years = 0
while balance < 20000:
    balance = balance * 1.08
    years += 1
print(f"It takes {years} years to double. Final balance {balance:,.2f}")


# ===============================================================
# SUMMARY
#   [1, 2, 3]            list    -> x[0], len(), sum(), .append()
#   {"key": value}       dict    -> d["key"], d.get("key")
#   if / elif / else     decisions (remember the colon : and indent)
#   for x in items:      repeat for each item
#   while condition:     repeat until condition is False
#   [x for x in items if ...]   quick filtered list
#
# NEXT: exercises/exercise02.py
# ===============================================================
