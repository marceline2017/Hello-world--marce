"""
LESSON 10 - CHARTS and EXCEL REPORTS
====================================

Your analysis is only useful if someone understands it. Managers and
audit partners want: one clear chart + a tidy Excel file.

  matplotlib  = the standard Python charting library
  ExcelWriter = save several tables into one Excel workbook

Run:  python lessons/lesson10_charts_and_reports.py
Charts are saved as PNG pictures in the "output" folder.
"""

from pathlib import Path
import math
import matplotlib
matplotlib.use("Agg")            # save to files (works without a screen)
import matplotlib.pyplot as plt  # "plt" is the usual nickname
import pandas as pd

DATA = Path(__file__).parent.parent / "data"
OUTPUT = Path(__file__).parent.parent / "output"
OUTPUT.mkdir(exist_ok=True)

gl = pd.read_csv(DATA / "general_ledger.csv", parse_dates=["date"],
                 dtype={"account": str})
gl["month"] = gl["date"].dt.month
gl["type"] = gl["account"].str[0].map({"4": "Revenue"}).fillna("Expense")

# A small, calm colour set. Use the SAME colour for the same thing
# in every chart (revenue is always blue, expenses always orange).
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED = "#0b0b0b", "#898781"

# Good chart habits, set once for all charts:
plt.rcParams.update({
    "axes.spines.top": False,      # remove the box lines on top/right
    "axes.spines.right": False,
    "axes.edgecolor": MUTED,
    "axes.grid": True,
    "grid.color": "#e6e5e1",       # light grid that stays in the background
    "axes.axisbelow": True,
    "font.size": 10,
})


# ---------------------------------------------------------------
# CHART 1. Line chart - change over time
# ---------------------------------------------------------------
# Rule of thumb: time on the bottom (x-axis) -> use a LINE chart.
monthly = gl.pivot_table(index="month", columns="type", values="amount", aggfunc="sum")

fig, ax = plt.subplots(figsize=(9, 4.5))   # fig = the page, ax = the chart
ax.plot(monthly.index, monthly["Revenue"], color=BLUE, linewidth=2, marker="o",
        label="Revenue")
ax.plot(monthly.index, monthly["Expense"], color=ORANGE, linewidth=2, marker="o",
        label="Expenses")

# Write the name at the end of each line (easier than looking at a legend)
for col, name in [("Revenue", "Revenue"), ("Expense", "Expenses")]:
    ax.annotate(name, (12, monthly.loc[12, col]), xytext=(8, 0),
                textcoords="offset points", va="center", color=INK)

ax.set_title("Monthly revenue and expenses, 2025", loc="left", color=INK)
ax.set_xlabel("Month")
ax.set_ylabel("Amount")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
ax.set_ylim(bottom=0)                      # money charts should start at 0
ax.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")   # 1,000 separators
# Legend under the chart so it never covers the data
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2)
fig.tight_layout()
fig.savefig(OUTPUT / "chart1_monthly_trend.png", dpi=150)
plt.close(fig)
print("Saved chart1_monthly_trend.png")


# ---------------------------------------------------------------
# CHART 2. Horizontal bar chart - compare categories
# ---------------------------------------------------------------
# Categories with long names -> HORIZONTAL bars, sorted biggest first.
expenses = (gl[gl["type"] == "Expense"]
            .groupby("account_name")["amount"].sum()
            .sort_values())                 # smallest at bottom... flipped below

fig, ax = plt.subplots(figsize=(9, 4.5))
bars = ax.barh(expenses.index, expenses.values, color=ORANGE, height=0.6)
ax.bar_label(bars, labels=[f"{v:,.0f}" for v in expenses.values],
             padding=4, color=INK)          # value at the end of each bar
ax.set_title("Total expenses by account, 2025", loc="left", color=INK)
ax.xaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
ax.grid(axis="y", visible=False)
ax.set_xlim(0, expenses.max() * 1.18)       # room for the labels
fig.tight_layout()
fig.savefig(OUTPUT / "chart2_expenses_by_account.png", dpi=150)
plt.close(fig)
print("Saved chart2_expenses_by_account.png")


# ---------------------------------------------------------------
# CHART 3. Benford's Law - actual (bars) against expected (line)
# ---------------------------------------------------------------
first_digit = gl["amount"].astype(str).str.lstrip("0.").str[0].astype(int)
actual = first_digit.value_counts(normalize=True).sort_index() * 100
expected = [math.log10(1 + 1 / d) * 100 for d in range(1, 10)]

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.bar(actual.index, actual.values, color=BLUE, width=0.6, label="Actual %")
ax.plot(range(1, 10), expected, color=INK, linewidth=2, marker="o",
        label="Expected % (Benford)")
ax.set_title("First-digit test: does the ledger follow Benford's Law?",
             loc="left", color=INK)
ax.set_xlabel("First digit of the amount")
ax.set_ylabel("% of entries")
ax.set_xticks(range(1, 10))
ax.grid(axis="x", visible=False)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(OUTPUT / "chart3_benford.png", dpi=150)
plt.close(fig)
print("Saved chart3_benford.png")


# ---------------------------------------------------------------
# CHART 4. Histogram - how are the amounts spread out?
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.hist(gl.loc[gl["type"] == "Expense", "amount"], bins=40, color=ORANGE,
        edgecolor="white")
ax.axvline(10000, color=INK, linestyle="--", linewidth=1)
ax.text(10150, ax.get_ylim()[1] * 0.9, "approval limit 10,000", color=INK)
ax.set_title("How big are expense entries? (count per size band)",
             loc="left", color=INK)
ax.set_xlabel("Amount")
ax.set_ylabel("Number of entries")
ax.xaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
fig.tight_layout()
fig.savefig(OUTPUT / "chart4_histogram.png", dpi=150)
plt.close(fig)
print("Saved chart4_histogram.png")


# ---------------------------------------------------------------
# EXCEL REPORT - several sheets, nice column widths, number format
# ---------------------------------------------------------------
by_account = (gl.groupby(["type", "account_name"])["amount"]
                .agg(entries="count", total="sum").reset_index())
monthly_out = monthly.copy()
monthly_out["Profit"] = monthly_out["Revenue"] - monthly_out["Expense"]

report_file = OUTPUT / "management_report.xlsx"
with pd.ExcelWriter(report_file, engine="openpyxl") as writer:
    by_account.to_excel(writer, sheet_name="By account", index=False)
    monthly_out.to_excel(writer, sheet_name="Monthly")
    gl.head(500).to_excel(writer, sheet_name="Ledger sample", index=False)

    # Make it look professional: widen columns and format numbers
    for sheet in writer.sheets.values():
        for column in sheet.columns:
            width = max(len(str(cell.value or "")) for cell in column) + 2
            sheet.column_dimensions[column[0].column_letter].width = min(width, 30)
            for cell in column:
                if isinstance(cell.value, float):
                    cell.number_format = "#,##0.00"
        sheet.freeze_panes = "A2"          # header row stays visible

# Put a chart picture into the workbook too
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
wb = load_workbook(report_file)
ws = wb.create_sheet("Charts")
ws.add_image(Image(OUTPUT / "chart1_monthly_trend.png"), "A1")
wb.save(report_file)
print(f"Saved {report_file.name}")


# ===============================================================
# WHICH CHART SHOULD I USE?
#   Change over time .................. line chart
#   Compare categories ................ bar chart (horizontal if long names)
#   Spread / size of values ........... histogram
#   Actual vs expected ................ bars + a line
#   One important number .............. no chart - just show the number big!
#   AVOID: pie charts with many slices, 3D charts, two y-axes.
#
# NEXT: exercises/exercise10.py, then lessons 11-13 and the practice sets!
# ===============================================================
