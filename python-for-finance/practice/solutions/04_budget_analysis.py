"""
PRACTICE SET 4 - BUDGET TESTING and ANALYTICAL REVIEW (18 tasks)
Files: data/budget_2025.csv, data/general_ledger.csv, data/prior_year_2024.csv
Lesson needed first: 12
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "data").is_dir())
DATA, OUTPUT = ROOT / "data", ROOT / "output"
OUTPUT.mkdir(exist_ok=True)
pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)

budget = pd.read_csv(DATA / "budget_2025.csv", dtype={"account": str})
gl = pd.read_csv(DATA / "general_ledger.csv", parse_dates=["date"], dtype={"account": str})
prior = pd.read_csv(DATA / "prior_year_2024.csv", dtype={"account": str})
gl["month"] = gl["date"].dt.month
gl["approved_by"] = gl["approved_by"].fillna("")

# TASK 1: (Warm-up) What is the total budgeted revenue, total budgeted expenses,
# and budgeted profit for the year?
is_rev = budget["account"].str.startswith("4")
b_rev, b_exp = budget.loc[is_rev, "budget"].sum(), budget.loc[~is_rev, "budget"].sum()
print(f"Budget revenue {b_rev:,.0f}  expenses {b_exp:,.0f}  profit {b_rev - b_exp:,.0f}")

# TASK 2: TEST THE BUDGET: does every account have exactly 12 months, are there
# duplicates, blanks or negative numbers?
print("12 months each:", (budget.groupby("account").size() == 12).all())
print("Duplicates:", budget.duplicated(["account", "month"]).sum(),
      " Blanks:", budget["budget"].isna().sum(), " Negatives:", (budget["budget"] < 0).sum())

# TASK 3: Show the budget per QUARTER per account (pivot table).
budget["quarter"] = (budget["month"] - 1) // 3 + 1
print(budget.pivot_table(index="account_name", columns="quarter", values="budget",
                         aggfunc="sum").round(0))

# TASK 4: Build an actual-vs-budget table per account per month (merge on
# month + account). Missing values = 0.
actual = gl.groupby(["month", "account"], as_index=False)["amount"].sum() \
           .rename(columns={"amount": "actual"})
bva = budget.merge(actual, on=["month", "account"], how="outer").fillna({"actual": 0, "budget": 0})
print(bva.head())

# TASK 5: ANNUAL variance per account: variance, variance % and F/A.
# (Revenue: actual above budget = F. Costs: actual above budget = A.)
ann = bva.groupby(["account", "account_name"], as_index=False)[["budget", "actual"]].sum()
ann["variance"] = ann["actual"] - ann["budget"]
ann["variance_%"] = (ann["variance"] / ann["budget"] * 100).round(1)
rev = ann["account"].str.startswith("4")
ann["F/A"] = ((rev & (ann["variance"] >= 0)) | (~rev & (ann["variance"] <= 0))).map({True: "F", False: "A"})
print(ann.round(0).to_string(index=False))

# TASK 6: Which 3 accounts have the biggest ADVERSE variance in money terms?
adverse = ann[ann["F/A"] == "A"].copy()
adverse["size"] = adverse["variance"].abs()
print(adverse.nlargest(3, "size")[["account_name", "variance", "variance_%"]])

# TASK 7: Use YOUR thresholds: flag accounts where |variance %| > 5 AND
# |variance| > 20,000. How many are flagged?
ann["flag"] = (ann["variance_%"].abs() > 5) & (ann["variance"].abs() > 20000)
print(ann.loc[ann["flag"], ["account_name", "variance", "variance_%", "F/A"]])

# TASK 8: CUMULATIVE (year-to-date) Sales Revenue variance by month. In which
# month did the year-to-date position first turn adverse?
s = bva[bva["account"] == "4000"].sort_values("month").copy()
s["ytd_variance"] = (s["actual"] - s["budget"]).cumsum()
print(s[["month", "budget", "actual", "ytd_variance"]].round(0).to_string(index=False))
neg = s[s["ytd_variance"] < 0]
print("First adverse month:", neg["month"].iloc[0] if len(neg) else "never")

# TASK 9: Find the month with the biggest Consulting Fees variance, then list the
# GL entries for Consulting Fees in that month. What do you notice?
c = bva[bva["account"] == "6600"].copy()
c["variance"] = c["actual"] - c["budget"]
worst = c.loc[c["variance"].idxmax(), "month"]
print("Worst month:", worst)
print(gl[(gl["account"] == "6600") & (gl["month"] == worst)]
        [["entry_id", "date", "vendor_id", "description", "amount", "posted_by", "approved_by"]])
# Notice: several "urgent" entries just under 10,000 on the same day by the same
# person, none approved = possible split transactions to avoid approval.

# TASK 10: FLEXED BUDGET for Cost of Goods Sold per month: budget COGS % of budget
# sales x ACTUAL sales. Compare with actual COGS each month.
pivot = bva.pivot_table(index="month", columns="account", values=["budget", "actual"], aggfunc="sum")
cogs_pct = pivot[("budget", "5000")].sum() / pivot[("budget", "4000")].sum()
flex = pd.DataFrame({"actual_sales": pivot[("actual", "4000")],
                     "flexed_cogs": pivot[("actual", "4000")] * cogs_pct,
                     "actual_cogs": pivot[("actual", "5000")]})
flex["variance"] = flex["actual_cogs"] - flex["flexed_cogs"]
print(f"Budget COGS % = {cogs_pct:.1%}")
print(flex.round(0))

# TASK 11: SEASONALITY. What % of the yearly sales budget falls in each month,
# and what % of actual sales did?
season = pd.DataFrame({
    "budget_%": pivot[("budget", "4000")] / pivot[("budget", "4000")].sum() * 100,
    "actual_%": pivot[("actual", "4000")] / pivot[("actual", "4000")].sum() * 100}).round(1)
print(season)

# TASK 12: Was the budget REALISTIC? Compare budget with last year's actual:
# budget growth % = budget / actual_2024 - 1, next to actual growth %.
real = ann.merge(prior, on=["account", "account_name"])
real["budget_growth_%"] = ((real["budget"] / real["actual_2024"] - 1) * 100).round(1)
real["actual_growth_%"] = ((real["actual"] / real["actual_2024"] - 1) * 100).round(1)
print(real[["account_name", "actual_2024", "budget", "actual", "budget_growth_%",
            "actual_growth_%"]].round(0).to_string(index=False))

# TASK 13: YOUR OWN EXPECTATION for salaries: last year x 1.04 (a 4% pay rise).
# Is the actual within 5% of your expectation?
py_sal = prior.loc[prior["account"] == "6200", "actual_2024"].iloc[0]
exp_sal = py_sal * 1.04
act_sal = ann.loc[ann["account"] == "6200", "actual"].iloc[0]
d = act_sal / exp_sal - 1
print(f"Expected {exp_sal:,.0f}  Actual {act_sal:,.0f}  Difference {d:.1%}"
      f" -> {'OK' if abs(d) <= 0.05 else 'INVESTIGATE'}")

# TASK 14: FORECAST ACCURACY. At the end of June, forecast the full year for each
# account as (Jan-Jun actual / 6 x 12). How far was that from the real full year?
h1 = bva[bva["month"] <= 6].groupby("account_name")["actual"].sum() / 6 * 12
full = bva.groupby("account_name")["actual"].sum()
acc = pd.DataFrame({"june_forecast": h1, "actual": full})
acc["error_%"] = ((acc["june_forecast"] / acc["actual"] - 1) * 100).round(1)
print(acc.round(0))

# TASK 15: GROSS MARGIN %: budget vs actual.
gm = lambda rev, cogs: (rev - cogs) / rev
b = ann.set_index("account")
print(f"Budget GM {gm(b.loc['4000', 'budget'], b.loc['5000', 'budget']):.1%}  "
      f"Actual GM {gm(b.loc['4000', 'actual'], b.loc['5000', 'actual']):.1%}")

# TASK 16: Line chart of monthly Sales Revenue: budget vs actual. Save it as
# output/p4_sales_bva.png
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(pivot.index, pivot[("budget", "4000")], color="#898781", linestyle="--",
        linewidth=2, label="Budget")
ax.plot(pivot.index, pivot[("actual", "4000")], color="#2a78d6", linewidth=2,
        marker="o", label="Actual")
ax.set_title("Sales revenue 2025, actual vs budget", loc="left")
ax.set_ylim(bottom=0)
ax.set_xticks(range(1, 13))
ax.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
ax.legend(frameon=False)
for side in ["top", "right"]:
    ax.spines[side].set_visible(False)
fig.tight_layout()
fig.savefig(OUTPUT / "p4_sales_bva.png", dpi=150)
plt.close(fig)

# TASK 17: Make a VARIANCE EXPLANATION template for the client: the flagged
# accounts from task 7 with empty "client_explanation" and "evidence_seen"
# columns, saved to Excel.
template = ann.loc[ann["flag"], ["account_name", "budget", "actual", "variance", "variance_%", "F/A"]].copy()
template["client_explanation"] = ""
template["evidence_seen"] = ""
template["auditor_conclusion"] = ""

# TASK 18: Save everything to output/p4_budget.xlsx (annual BvA, flex table,
# realism table, the explanation template).
with pd.ExcelWriter(OUTPUT / "p4_budget.xlsx") as w:
    ann.to_excel(w, sheet_name="Annual BvA", index=False)
    flex.to_excel(w, sheet_name="Flexed COGS")
    real.to_excel(w, sheet_name="Budget realism", index=False)
    template.to_excel(w, sheet_name="Explanations", index=False)
print("Saved output/p4_sales_bva.png and output/p4_budget.xlsx")
