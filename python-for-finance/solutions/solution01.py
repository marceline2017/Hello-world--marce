"""SOLUTION 1 - Python basics

There is always more than one correct answer. Yours can look different!
"""


# TASK 1: Create variables for a company: name = "Kilimo Foods", revenue = 845000,
# cost_of_sales = 507000. Print them.
name = "Kilimo Foods"
revenue = 845000
cost_of_sales = 507000
print(name, revenue, cost_of_sales)

# TASK 2: Calculate gross profit and gross margin. Print them with an f-string:
#   "Gross profit: 338,000.00"   and   "Gross margin: 40.0%" 
gross_profit = revenue - cost_of_sales
gross_margin = gross_profit / revenue
print(f"Gross profit: {gross_profit:,.2f}")
print(f"Gross margin: {gross_margin:.1%}")

# TASK 3: The text "  1,250.75 " came from a bank file. Clean it, turn it into a
# number, and add 16% VAT. Print the result with 2 decimals.
raw = "  1,250.75 "
amount = float(raw.strip().replace(",", ""))
print(f"With VAT: {amount * 1.16:,.2f}")

# TASK 4: The vendor name "  quick FIX services " is messy. Make it "Quick Fix Services".
vendor = "  quick FIX services "
print(vendor.strip().title())
