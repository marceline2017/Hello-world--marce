"""
LESSON 9 - FINANCE CALCULATIONS: time value of money, loans, ratios, returns
============================================================================

Python can do everything your financial calculator does - and show
the working. We build these by hand so you understand the maths,
then use pandas for tables.

Run:  python lessons/lesson09_finance_calculations.py
"""

import pandas as pd

pd.set_option("display.width", 120)


# ---------------------------------------------------------------
# 1. Present Value and Future Value
# ---------------------------------------------------------------
# Money today is worth more than money tomorrow (you could invest it).
#   FV = PV * (1 + r) ** n       grow money forward
#   PV = FV / (1 + r) ** n       bring future money back to today

def future_value(pv, rate, years):
    return pv * (1 + rate) ** years

def present_value(fv, rate, years):
    return fv / (1 + rate) ** years

print(f"10,000 today at 8% for 5 years = {future_value(10000, 0.08, 5):,.2f}")
print(f"10,000 in 5 years is worth today = {present_value(10000, 0.08, 5):,.2f}")


# ---------------------------------------------------------------
# 2. NPV - Net Present Value (should we invest?)
# ---------------------------------------------------------------
# Add up the present value of every cash flow. Year 0 = today.
# NPV > 0  -> the project earns more than our required return. Accept.

def npv(rate, cash_flows):
    total = 0
    for year, cf in enumerate(cash_flows):
        total += cf / (1 + rate) ** year
    return total

project = [-50000, 15000, 18000, 20000, 12000]   # spend 50k, receive 4 years
print(f"\nNPV at 10%: {npv(0.10, project):,.2f}")


# ---------------------------------------------------------------
# 3. IRR - Internal Rate of Return
# ---------------------------------------------------------------
# IRR = the rate where NPV is exactly 0. There is no simple formula,
# so we "guess and improve" (bisection: halve the range each time).

def irr(cash_flows, low=-0.99, high=1.0, tolerance=0.000001):
    for _ in range(1000):
        mid = (low + high) / 2
        if npv(mid, cash_flows) > 0:
            low = mid        # NPV still positive -> rate must be higher
        else:
            high = mid
        if high - low < tolerance:
            break
    return mid

print(f"IRR: {irr(project):.2%}")


# ---------------------------------------------------------------
# 4. Payback period
# ---------------------------------------------------------------
def payback_period(cash_flows):
    cumulative = 0
    for year, cf in enumerate(cash_flows):
        previous = cumulative
        cumulative += cf
        if cumulative >= 0 and year > 0:
            # part of the year needed = what was still missing / this year's cash
            return year - 1 + (-previous / cf)
    return None   # never paid back

print(f"Payback: {payback_period(project):.2f} years")


# ---------------------------------------------------------------
# 5. Loan payment and amortization schedule
# ---------------------------------------------------------------
# Same as Excel =PMT(). Payment = P * r / (1 - (1 + r) ** -n)

def loan_payment(principal, annual_rate, years, per_year=12):
    r = annual_rate / per_year
    n = years * per_year
    return principal * r / (1 - (1 + r) ** -n)

def amortization_schedule(principal, annual_rate, years, per_year=12):
    payment = loan_payment(principal, annual_rate, years, per_year)
    r = annual_rate / per_year
    balance = principal
    rows = []
    for period in range(1, years * per_year + 1):
        interest = balance * r
        capital = payment - interest
        balance -= capital
        rows.append({"period": period, "payment": payment,
                     "interest": interest, "principal": capital,
                     "balance": max(balance, 0)})
    return pd.DataFrame(rows)       # a list of dicts -> DataFrame!

pay = loan_payment(100000, 0.12, 3)
print(f"\nLoan 100,000 at 12% for 3 years: monthly payment {pay:,.2f}")
sched = amortization_schedule(100000, 0.12, 3)
print(sched.head().round(2).to_string(index=False))
print("...")
print(sched.tail(2).round(2).to_string(index=False))
print(f"Total interest paid: {sched['interest'].sum():,.2f}")
# Audit idea: re-calculate a client's loan schedule and compare with theirs.


# ---------------------------------------------------------------
# 6. Financial ratios from a simple balance sheet and income statement
# ---------------------------------------------------------------
fs = {
    "revenue": 2_500_000, "cost_of_sales": 1_500_000, "operating_expenses": 600_000,
    "interest_expense": 50_000, "net_income": 260_000,
    "current_assets": 800_000, "inventory": 300_000, "current_liabilities": 500_000,
    "total_assets": 2_000_000, "total_liabilities": 1_100_000, "equity": 900_000,
    "receivables": 350_000,
}

gross_profit = fs["revenue"] - fs["cost_of_sales"]
operating_profit = gross_profit - fs["operating_expenses"]

ratios = {
    # Profitability - is the business making money?
    "Gross margin":       gross_profit / fs["revenue"],
    "Operating margin":   operating_profit / fs["revenue"],
    "Net margin":         fs["net_income"] / fs["revenue"],
    "Return on assets":   fs["net_income"] / fs["total_assets"],
    "Return on equity":   fs["net_income"] / fs["equity"],
    # Liquidity - can it pay its bills soon?
    "Current ratio":      fs["current_assets"] / fs["current_liabilities"],
    "Quick ratio":        (fs["current_assets"] - fs["inventory"]) / fs["current_liabilities"],
    # Solvency - how much debt?
    "Debt to equity":     fs["total_liabilities"] / fs["equity"],
    "Interest cover":     operating_profit / fs["interest_expense"],
    # Efficiency
    "Receivable days":    fs["receivables"] / fs["revenue"] * 365,
    "Inventory days":     fs["inventory"] / fs["cost_of_sales"] * 365,
}

print("\nFINANCIAL RATIOS")
for name, value in ratios.items():
    if "margin" in name or "Return" in name:
        print(f"  {name:<20}{value:>10.1%}")
    else:
        print(f"  {name:<20}{value:>10.2f}")


# ---------------------------------------------------------------
# 7. Analytical review - compare this year with last year
# ---------------------------------------------------------------
# Auditors compare years and ask about big changes ("fluctuation analysis").
pl = pd.DataFrame({
    "line":      ["Revenue", "Cost of sales", "Salaries", "Rent", "Travel", "Consulting"],
    "last_year": [2_200_000, 1_320_000, 310_000, 120_000, 45_000, 30_000],
    "this_year": [2_500_000, 1_500_000, 325_000, 120_000, 88_000, 95_000],
})
pl["change"] = pl["this_year"] - pl["last_year"]
pl["change_%"] = (pl["change"] / pl["last_year"] * 100).round(1)

# Flag: change bigger than 10% AND bigger than 25,000 (a "threshold")
pl["investigate"] = (pl["change_%"].abs() > 10) & (pl["change"].abs() > 25000)
print("\nANALYTICAL REVIEW")
print(pl.to_string(index=False))


# ---------------------------------------------------------------
# 8. Investment returns and risk
# ---------------------------------------------------------------
prices = pd.Series([100, 102, 101, 105, 107, 104, 110, 112, 111, 115],
                   name="share_price")
daily_returns = prices.pct_change().dropna()    # % change from day before
print("\nDaily returns:", (daily_returns * 100).round(2).tolist())
print(f"Total return:      {prices.iloc[-1] / prices.iloc[0] - 1:.2%}")
print(f"Average daily:     {daily_returns.mean():.2%}")
print(f"Volatility (std):  {daily_returns.std():.2%}")   # higher = riskier
print(f"Annualised vol:    {daily_returns.std() * 252 ** 0.5:.2%}")  # 252 trading days

# Moving average - smooths the line (traders and analysts use this)
print("3-day moving average:", prices.rolling(3).mean().round(2).tolist())


# ===============================================================
# SUMMARY
#   FV = PV * (1+r)**n          PV = FV / (1+r)**n
#   NPV > 0 -> good project     IRR = rate where NPV = 0
#   loan_payment() = Excel PMT  amortization table -> DataFrame
#   Ratios: profitability, liquidity, solvency, efficiency
#   Analytical review: change and change %, then a threshold flag
#   .pct_change()  .rolling(n).mean()  .std()
#
# Tip: the "numpy-financial" package has ready-made npv/irr/pmt:
#   pip install numpy-financial    then   import numpy_financial as npf
#
# NEXT: exercises/exercise09.py
# ===============================================================
