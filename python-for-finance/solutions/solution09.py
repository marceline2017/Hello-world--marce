"""SOLUTION 9 - Finance calculations

There is always more than one correct answer. Yours can look different!
"""

from pathlib import Path
import pandas as pd
DATA = Path(__file__).parent.parent / "data"

# TASK 1: Write npv(rate, cash_flows). A machine costs 80,000 and saves 25,000 a year
# for 4 years. Is NPV positive at 9%?
def npv(rate, cfs):
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cfs))

value = npv(0.09, [-80000, 25000, 25000, 25000, 25000])
print(f"NPV {value:,.2f} ->", "accept" if value > 0 else "reject")

# TASK 2: Monthly payment on a 250,000 mortgage at 9% for 20 years.
r, n = 0.09 / 12, 20 * 12
print(f"{250000 * r / (1 - (1 + r) ** -n):,.2f}")

# TASK 3: Current assets 420,000, inventory 150,000, current liabilities 300,000.
# Calculate the current ratio and the quick ratio.
print(f"Current {420000 / 300000:.2f}, Quick {(420000 - 150000) / 300000:.2f}")
