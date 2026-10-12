"""
LESSON 12 - BUDGET vs ACTUAL and ANALYTICAL REVIEW
==================================================

Managers compare ACTUAL results with the BUDGET (the plan) every month.
Auditors use the same comparison as an "analytical procedure":
  1. set an EXPECTATION (budget, last year, or your own calculation)
  2. compare it with the actual figure
  3. if the difference is bigger than a THRESHOLD, investigate
  4. get an explanation AND evidence. "Prices went up" is not enough -
     ask to see the new price list.

Words you need:
  Variance       = actual - budget
  Favourable (F) = good for profit: revenue ABOVE budget, or cost BELOW budget
  Adverse (A)    = bad for profit:  revenue BELOW budget, or cost ABOVE budget
  Flexed budget  = the budget re-calculated for the ACTUAL level of sales

Run:  python lessons/lesson12_budget_analysis.py
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DATA = Path(__file__).parent.parent / "data"
OUTPUT = Path(__file__).parent.parent / "output"
OUTPUT.mkdir(exist_ok=True)
pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)

gl = pd.read_csv(DATA / "general_ledger.csv", parse_dates=["date"], dtype={"account": str})
budget = pd.read_csv(DATA / "budget_2025.csv", dtype={"account": str})
prior = pd.read_csv(DATA / "prior_year_2024.csv", dtype={"account": str})
gl["month"] = gl["date"].dt.month


# ---------------------------------------------------------------
# STEP 1. Test the budget itself (is it complete and sensible?)
# ---------------------------------------------------------------
print(budget.head())
months_per_account = budget.groupby("account_name")["month"].nunique()
print("\nEvery account has 12 months?", (months_per_account == 12).all())
print("Any negative budget lines?   ", (budget["budget"] < 0).any())
print("Any repeated month+account?  ", budget.duplicated(["month", "account"]).any())
missing = set(gl["account"]) - set(budget["account"])
print("GL accounts with NO budget:  ", missing or "none")


# ---------------------------------------------------------------
# STEP 2. Put actual and budget side by side (per month, per account)
# ---------------------------------------------------------------
actual = (gl.groupby(["month", "account", "account_name"], as_index=False)["amount"]
            .sum().rename(columns={"amount": "actual"}))
bva = budget.merge(actual, on=["month", "account", "account_name"], how="outer")
bva[["budget", "actual"]] = bva[["budget", "actual"]].fillna(0)
bva["is_revenue"] = bva["account"].str.startswith("4")


# ---------------------------------------------------------------
# STEP 3. Variance, %, and Favourable / Adverse
# ---------------------------------------------------------------
def add_variance(df):
    df["variance"] = df["actual"] - df["budget"]
    df["variance_%"] = (df["variance"] / df["budget"] * 100).round(1)
    # Revenue: more is good. Costs: more is bad.
    good = (df["is_revenue"] & (df["variance"] >= 0)) | (~df["is_revenue"] & (df["variance"] <= 0))
    df["F/A"] = good.map({True: "F", False: "A"})
    return df

bva = add_variance(bva)

annual = (bva.groupby(["account", "account_name", "is_revenue"], as_index=False)
             [["budget", "actual"]].sum())
annual = add_variance(annual)
print("\nANNUAL BUDGET vs ACTUAL")
print(annual.drop(columns="is_revenue").round(0).to_string(index=False))


# ---------------------------------------------------------------
# STEP 4. The profit line
# ---------------------------------------------------------------
rev = annual[annual["is_revenue"]][["budget", "actual"]].sum()
cost = annual[~annual["is_revenue"]][["budget", "actual"]].sum()
profit = rev - cost
print(f"\nProfit:  budget {profit['budget']:,.0f}   actual {profit['actual']:,.0f}"
      f"   variance {profit['actual'] - profit['budget']:,.0f}")


# ---------------------------------------------------------------
# STEP 5. Which variances need investigating? (the audit threshold)
# ---------------------------------------------------------------
# A common rule: investigate if the variance is bigger than a % AND bigger
# than an amount (so tiny accounts with big % don't waste your time).
# The amount is often "performance materiality" (e.g. 75% of materiality).
materiality = 0.05 * profit["actual"]
performance_materiality = 0.75 * materiality
PCT = 10
print(f"\nMateriality {materiality:,.0f}  ->  performance materiality {performance_materiality:,.0f}")

annual["investigate"] = (annual["variance_%"].abs() > PCT) & \
                        (annual["variance"].abs() > performance_materiality)
to_investigate = annual[annual["investigate"]]
print(f"\nAccounts to investigate (> {PCT}% AND > {performance_materiality:,.0f}):")
print(to_investigate[["account_name", "budget", "actual", "variance", "variance_%", "F/A"]]
      .round(0).to_string(index=False))

# For monthly lines use a lower amount (a month is 1/12 of a year)
bva["investigate"] = (bva["variance_%"].abs() > 25) & \
                     (bva["variance"].abs() > performance_materiality / 4)


# ---------------------------------------------------------------
# STEP 6. Monthly variance % table - WHEN did it go wrong?
# ---------------------------------------------------------------
heat = bva.pivot_table(index="account_name", columns="month", values="variance_%")
print("\nMONTHLY VARIANCE % (actual vs budget)")
print(heat.round(0).to_string())
# (Our practice ledger is random, so months jump around more than in a
# real company. In real life even rent would be almost flat every month.)
# Look for the month where a cost suddenly jumps - then drill down to
# the GL entries of that month (Lesson 8 tests are a great next step).
worst = bva.loc[bva["variance"].abs().idxmax()]
print(f"\nBiggest single monthly variance: {worst['account_name']} in month "
      f"{worst['month']}: {worst['variance']:,.0f}")
drill = gl[(gl["account_name"] == worst["account_name"]) & (gl["month"] == worst["month"])]
print("Largest entries behind it:")
print(drill.nlargest(5, "amount")[["entry_id", "date", "description", "amount", "posted_by"]]
      .to_string(index=False))


# ---------------------------------------------------------------
# STEP 7. Flexed budget - separate "we sold more" from "we spent badly"
# ---------------------------------------------------------------
# Cost of goods sold SHOULD go up when sales go up. So compare actual COGS
# with what the budget would have been at the ACTUAL sales level.
budget_cogs_pct = (annual.loc[annual["account"] == "5000", "budget"].iloc[0] /
                   annual.loc[annual["account"] == "4000", "budget"].iloc[0])
actual_sales = annual.loc[annual["account"] == "4000", "actual"].iloc[0]
actual_cogs = annual.loc[annual["account"] == "5000", "actual"].iloc[0]
flexed_cogs = budget_cogs_pct * actual_sales
print(f"\nBudget COGS as % of sales: {budget_cogs_pct:.1%}")
print(f"Flexed COGS budget: {flexed_cogs:,.0f}   Actual COGS: {actual_cogs:,.0f}")
print(f"Variance after flexing: {actual_cogs - flexed_cogs:,.0f} "
      f"({'A' if actual_cogs > flexed_cogs else 'F'})")


# ---------------------------------------------------------------
# STEP 8. Three-way comparison: last year, budget, this year
# ---------------------------------------------------------------
three = annual.merge(prior, on=["account", "account_name"])
three["vs_PY_%"] = ((three["actual"] / three["actual_2024"] - 1) * 100).round(1)
three["vs_budget_%"] = three["variance_%"]
print("\nPRIOR YEAR vs BUDGET vs ACTUAL")
print(three[["account_name", "actual_2024", "budget", "actual", "vs_PY_%", "vs_budget_%"]]
      .round(0).to_string(index=False))
# When an account is up a lot vs last year AND over budget, that is a
# strong signal. Ask: what changed in the business?


# ---------------------------------------------------------------
# STEP 9. Your OWN expectation (a "substantive analytical procedure")
# ---------------------------------------------------------------
# Rent is usually a fixed contract. Expectation = last year's rent
# (if the lease didn't change). Compare.
rent_expected = prior.loc[prior["account"] == "6100", "actual_2024"].iloc[0]
rent_actual = annual.loc[annual["account"] == "6100", "actual"].iloc[0]
diff = rent_actual - rent_expected
print(f"\nRent - expected {rent_expected:,.0f}, actual {rent_actual:,.0f}, "
      f"difference {diff:,.0f} ({diff / rent_expected:.1%})")
print("Within threshold - no further work" if abs(diff) < performance_materiality
      else "Above threshold - investigate")


# ---------------------------------------------------------------
# STEP 10. Year-to-date and a full-year forecast
# ---------------------------------------------------------------
# Imagine it is the end of September. How are we doing so far?
ytd = bva[bva["month"] <= 9].groupby("account_name")[["budget", "actual"]].sum()
ytd["forecast_full_year"] = (ytd["actual"] / 9 * 12).round(0)   # "run-rate"
ytd["full_year_budget"] = bva.groupby("account_name")["budget"].sum()
print("\nYTD (Jan-Sep) and run-rate forecast:")
print(ytd.round(0))


# ---------------------------------------------------------------
# STEP 11. A chart and the workpaper
# ---------------------------------------------------------------
chart = annual.sort_values("variance_%")
# Adverse = red-orange, Favourable = blue. Labels say A/F too, so colour
# is never the only way to read the chart.
colors = chart["F/A"].map({"A": "#d03b3b", "F": "#2a78d6"})
fig, ax = plt.subplots(figsize=(9, 4.5))
bars = ax.barh(chart["account_name"], chart["variance_%"], color=colors, height=0.6)
ax.bar_label(bars, labels=[f"{v:+.0f}% {fa}" for v, fa in zip(chart["variance_%"], chart["F/A"])],
             padding=4)
ax.axvline(0, color="#898781", linewidth=1)
ax.set_title("Actual vs budget 2025, % variance by account (A = adverse, F = favourable)",
             loc="left")
for side in ["top", "right"]:
    ax.spines[side].set_visible(False)
lo, hi = chart["variance_%"].min(), chart["variance_%"].max()
ax.set_xlim(min(lo * 1.35, -10), max(hi * 1.35, 10))
fig.tight_layout()
fig.savefig(OUTPUT / "budget_variance.png", dpi=150)
plt.close(fig)

with pd.ExcelWriter(OUTPUT / "budget_workpaper.xlsx") as w:
    annual.to_excel(w, sheet_name="Annual BvA", index=False)
    bva.to_excel(w, sheet_name="Monthly BvA", index=False)
    heat.round(1).to_excel(w, sheet_name="Variance % by month")
    three.to_excel(w, sheet_name="PY vs Budget vs Actual", index=False)
print("\nSaved output/budget_variance.png and output/budget_workpaper.xlsx")


# ===============================================================
# SUMMARY - budget and analytical review audit programme
#   1. Test the budget: complete, no duplicates, every GL account covered
#   2. Merge actual and budget on month + account
#   3. variance, variance %, F/A (opposite rule for revenue vs costs)
#   4. Threshold: % AND amount (performance materiality)
#   5. Monthly pivot to find WHEN, then drill into GL entries to find WHAT
#   6. Flex variable costs to actual sales
#   7. Compare with prior year too
#   8. Build your own expectation for stable accounts (rent, salaries)
#   9. Get explanations AND evidence for every investigated item
#
# PRACTICE: practice/04_budget_analysis.py
# ===============================================================
