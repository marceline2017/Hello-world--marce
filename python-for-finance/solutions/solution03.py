"""SOLUTION 3 - Functions

There is always more than one correct answer. Yours can look different!
"""


# TASK 1: Write a function variance(actual, budget) that returns the difference AND
# the % difference. Test it with actual=56000, budget=50000.
def variance(actual, budget):
    diff = actual - budget
    return diff, diff / budget

d, p = variance(56000, 50000)
print(f"{d:,} ({p:.1%})")

# TASK 2: Write reducing_balance(cost, rate, years) that prints the book value at the
# end of each year when depreciation = book value x rate. Try (40000, 0.25, 4).
def reducing_balance(cost, rate, years):
    value = cost
    for year in range(1, years + 1):
        value -= value * rate
        print(f"Year {year}: {value:,.2f}")

reducing_balance(40000, 0.25, 4)

# TASK 3: Write is_weekend(day_name) that returns True for "Saturday" or "Sunday"
# (any capitals, e.g. "sunday"). Test with 3 days.
def is_weekend(day_name):
    return day_name.strip().lower() in ["saturday", "sunday"]

print(is_weekend("Monday"), is_weekend("sunday"), is_weekend("SATURDAY"))
