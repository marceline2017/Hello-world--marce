"""SOLUTION 2 - Lists, dicts, if, loops

There is always more than one correct answer. Yours can look different!
"""


# TASK 1: Here are quarterly expenses: expenses = [45200, 51800, 38900, 60100]
# Print the total, the average and the largest quarter.
expenses = [45200, 51800, 38900, 60100]
print(sum(expenses), sum(expenses) / len(expenses), max(expenses))

# TASK 2: Budget is 50,000 per quarter. Loop through expenses and print "Over budget"
# or "Within budget" for each quarter, e.g. "Q1: 45,200 Within budget".
# start=1 makes enumerate count 1,2,3,4 instead of 0,1,2,3
for i, e in enumerate(expenses, start=1):
    status = "Over budget" if e > 50000 else "Within budget"
    print(f"Q{i}: {e:,} {status}")

# TASK 3: Make a dictionary of exchange rates: {"USD": 1.0, "EUR": 1.08, "GBP": 1.27}.
# Convert 2,500 EUR to USD using the dictionary.
rates = {"USD": 1.0, "EUR": 1.08, "GBP": 1.27}
print(f"2,500 EUR = {2500 * rates['EUR']:,.2f} USD")

# TASK 4: AUDIT: invoices = [("INV-1", 900), ("INV-2", 0), ("INV-3", -150), ("INV-4", 1200)]
# Make a list of invoice numbers whose amount is zero or negative.
invoices = [("INV-1", 900), ("INV-2", 0), ("INV-3", -150), ("INV-4", 1200)]
bad = [no for no, amt in invoices if amt <= 0]
print(bad)
