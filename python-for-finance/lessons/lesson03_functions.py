"""
LESSON 3 - FUNCTIONS: build your own reusable tools
===================================================

A function is a recipe. You write it once, then use it again and again.
In Excel you use =SUM() or =PMT(). In Python you can MAKE your own.

Run:  python lessons/lesson03_functions.py
"""

# ---------------------------------------------------------------
# 1. Making a function
# ---------------------------------------------------------------
#   def  name(inputs):
#       do something
#       return answer
#
# "def" means define. The inputs are called "parameters".
# "return" sends the answer back.

def add_vat(price, rate):
    """Return the price including VAT."""   # a "docstring": explains it
    return price * (1 + rate)

print(add_vat(100, 0.16))      # 116.0
print(add_vat(250, 0.20))      # 300.0


# ---------------------------------------------------------------
# 2. Default values - inputs that are optional
# ---------------------------------------------------------------
def add_vat2(price, rate=0.16):
    return round(price * (1 + rate), 2)

print(add_vat2(100))            # uses 0.16 automatically
print(add_vat2(100, rate=0.0))  # you can still change it


# ---------------------------------------------------------------
# 3. FINANCE TOOLBOX - functions you will really use
# ---------------------------------------------------------------

def percent_change(old, new):
    """Growth from old to new. 100 -> 120 = 0.20 (20%)."""
    if old == 0:
        return None          # avoid dividing by zero
    return (new - old) / old


def simple_interest(principal, rate, years):
    return principal * rate * years


def compound_interest(principal, rate, years, times_per_year=1):
    """Future value with compounding. FV = P * (1 + r/n) ** (n*t)"""
    n = times_per_year
    return principal * (1 + rate / n) ** (n * years)


def straight_line_depreciation(cost, salvage, life_years):
    """Same depreciation every year."""
    return (cost - salvage) / life_years


def depreciation_schedule(cost, salvage, life_years):
    """Print a year-by-year table of book value."""
    yearly = straight_line_depreciation(cost, salvage, life_years)
    book_value = cost
    print(f"{'Year':<6}{'Depreciation':>15}{'Book value':>15}")
    for year in range(1, life_years + 1):
        book_value -= yearly
        print(f"{year:<6}{yearly:>15,.2f}{book_value:>15,.2f}")
    # Formatting tip:  :<6 = left-align in 6 spaces,  :>15 = right-align


def materiality(benchmark, percent=0.05):
    """Audit materiality, e.g. 5% of profit before tax."""
    return benchmark * percent


print(f"Growth: {percent_change(80000, 96000):.1%}")
print(f"Simple interest: {simple_interest(10000, 0.10, 3):,.2f}")
print(f"Compound (yearly):  {compound_interest(10000, 0.10, 3):,.2f}")
print(f"Compound (monthly): {compound_interest(10000, 0.10, 3, 12):,.2f}")
print(f"Materiality: {materiality(2_400_000):,.0f}")
print()
depreciation_schedule(cost=50000, salvage=5000, life_years=5)


# ---------------------------------------------------------------
# 4. Returning more than one value
# ---------------------------------------------------------------
def summary(numbers):
    total = sum(numbers)
    average = total / len(numbers)
    return total, average, max(numbers)   # returns 3 values

t, avg, biggest = summary([1200, 3400, 560, 7800])
print(f"\nTotal {t:,}, average {avg:,.2f}, biggest {biggest:,}")


# ---------------------------------------------------------------
# 5. A function that does an audit check
# ---------------------------------------------------------------
def check_payment(amount, posted_by, approved_by, limit=10000):
    """Return a list of problems found with one payment."""
    problems = []
    if amount <= 0:
        problems.append("amount is zero or negative")
    if amount >= limit and not approved_by:
        problems.append("missing approval")
    if approved_by and approved_by == posted_by:
        problems.append("self-approved")
    if amount % 1000 == 0:
        problems.append("round amount - check support")
    return problems

print("\n--- Payment checks ---")
print(check_payment(450.75, "amina", ""))          # []  = no problems
print(check_payment(15000, "brian", ""))
print(check_payment(12000, "chen", "chen"))


# ---------------------------------------------------------------
# 6. Scope - variables inside a function stay inside
# ---------------------------------------------------------------
def demo():
    secret = 123       # only exists while demo() runs
    return secret

demo()
# print(secret)   <- this would be an ERROR: secret only lives inside demo


# ---------------------------------------------------------------
# 7. lambda - a tiny one-line function (you will see these in pandas)
# ---------------------------------------------------------------
double = lambda x: x * 2
print(double(21))   # 42

# Very useful for sorting:
vendors = [("Skyline", 15000), ("Metro", 980), ("Global", 22000)]
print(sorted(vendors, key=lambda v: v[1], reverse=True))  # by amount


# ===============================================================
# SUMMARY
#   def name(a, b=default):    create a function
#       return answer          give the answer back
#   Functions = write once, use many times. Fewer mistakes.
#   lambda x: x * 2            tiny function on one line
#
# GOOD HABIT: if you copy-paste the same code 3 times, make a function.
#
# NEXT: exercises/exercise03.py
# ===============================================================
