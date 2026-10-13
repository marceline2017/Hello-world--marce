"""
LESSON 1 - PYTHON BASICS: printing, variables, numbers and text
================================================================

How to use every lesson:
  1. Open this file and READ it from top to bottom.
  2. Run it:   python lessons/lesson01_basics.py
  3. Compare what you read with what appears on the screen.
  4. Change numbers, run again, see what changes. Breaking things is OK!

A line that starts with  #  is a "comment". Python ignores it.
Comments are notes for humans. I use them to explain everything.
"""

# ---------------------------------------------------------------
# 1. print() - show something on the screen
# ---------------------------------------------------------------
# print() is a "function": a ready-made tool. You give it something
# inside the brackets ( ) and it shows it on the screen.

print("Hello, future auditor!")
print("=" * 40)   # "=" repeated 40 times makes a nice line


# ---------------------------------------------------------------
# 2. Variables - a labelled box that holds a value
# ---------------------------------------------------------------
# Think of a variable like a cell in Excel with a name.
#   name  =  value
# The = sign means "put this value in the box". It is NOT "equals"
# like in maths.

company = "Sunrise Trading Ltd"     # text   (called a "string", str)
year = 2025                          # whole number (called "int")
revenue = 1_250_000.50               # decimal number (called "float")
is_audited = True                    # yes/no value (called "bool")
# Tip: the _ in 1_250_000 is only to make it easy to read, like a comma.

print(company)
print(year)
print(revenue)
print(is_audited)

# type() tells you what kind of value is inside the box
print(type(company), type(year), type(revenue), type(is_audited))


# ---------------------------------------------------------------
# 3. Maths - Python is a calculator
# ---------------------------------------------------------------
expenses = 980_000.25

profit = revenue - expenses          # minus
margin = profit / revenue            # divide
double_profit = profit * 2           # multiply
total = revenue + expenses           # plus

print("Profit:", profit)
print("Margin:", margin)

# Other useful maths signs:
print(10 ** 2)     # power: 10 to the power of 2 = 100
print(17 // 5)     # whole-number division = 3
print(17 % 5)      # remainder (called "modulo") = 2
print(round(margin, 4))   # round to 4 decimal places


# ---------------------------------------------------------------
# 4. f-strings - the BEST way to show numbers nicely
# ---------------------------------------------------------------
# Put the letter f before the quotes, then put variables inside { }.
# After a colon : you can tell Python how to format the number.
#   :,      -> add thousand separators        1,250,000.5
#   :.2f    -> 2 decimal places                1250000.50
#   :,.2f   -> both                            1,250,000.50
#   :.1%    -> show as a percentage            21.6%

print(f"Company: {company}")
print(f"Revenue: {revenue:,.2f}")
print(f"Profit:  {profit:,.2f}")
print(f"Margin:  {margin:.1%}")


# ---------------------------------------------------------------
# 5. Working with text (strings)
# ---------------------------------------------------------------
vendor = "  acme CORP  "

print(vendor.strip())          # remove spaces at both ends -> "acme CORP"
print(vendor.upper())          # ALL CAPITALS
print(vendor.lower())          # all small letters
print(vendor.strip().title())  # Each Word Capital -> "Acme Corp"
print(len("INV-001"))          # length = number of characters = 7
print("INV" in "INV-001")      # is "INV" inside? -> True
print("INV-001".replace("INV", "INVOICE"))

# Joining text together with +
first = "Amina"
last = "Otieno"
print(first + " " + last)


# ---------------------------------------------------------------
# 6. Converting between types
# ---------------------------------------------------------------
# Data from files often arrives as TEXT, even when it looks like a
# number. You must convert it before you can do maths.

amount_text = "1500.75"
# amount_text + 100  -> this would give an ERROR (text + number)
amount = float(amount_text)        # text -> decimal number
print(amount + 100)                # 1600.75 - works now

print(int("42"))                   # text -> whole number
print(str(2025) + " audit")        # number -> text

# Removing a comma before converting (very common in finance files!)
print(float("1,200.50".replace(",", "")))


# ---------------------------------------------------------------
# 7. A WARNING about money and decimals
# ---------------------------------------------------------------
# Computers store decimals in binary, so tiny errors can appear:
print(0.1 + 0.2)               # 0.30000000000000004 - not exactly 0.3!

# For normal analysis this does not matter - just round when showing.
# When you need EXACT cents (e.g. reconciling to the penny), use Decimal:
from decimal import Decimal
print(Decimal("0.10") + Decimal("0.20"))   # exactly 0.30


# ---------------------------------------------------------------
# 8. Getting input from the user (optional, try it!)
# ---------------------------------------------------------------
# Remove the # from the next 2 lines to try it:
# price = float(input("Enter a price: "))
# print(f"Price with 16% VAT: {price * 1.16:,.2f}")


# ===============================================================
# SUMMARY - what you learned
#   print()         show things
#   x = 5           store a value in a variable
#   str, int, float, bool   the 4 basic types
#   + - * / ** // %         maths
#   f"{x:,.2f}"     format money nicely
#   .strip() .upper() .lower() .title() .replace()   clean text
#   float("12.5")   convert text to a number
#
# NEXT: open exercises/exercise01.py and try it yourself.
# ===============================================================
