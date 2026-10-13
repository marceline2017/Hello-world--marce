"""SOLUTION 10 - Charts and reports

There is always more than one correct answer. Yours can look different!
"""

from pathlib import Path
import pandas as pd
DATA = Path(__file__).parent.parent / "data"

# TASK 1: Make a bar chart of the number of entries per user and save it as
# output/ex10_users.png
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
gl = pd.read_csv(DATA / "general_ledger.csv", parse_dates=["date"])
OUTPUT = Path(__file__).parent.parent / "output"
OUTPUT.mkdir(exist_ok=True)
counts = gl["posted_by"].value_counts()
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(counts.index, counts.values, color="#2a78d6")
ax.set_title("Entries posted per user", loc="left")
fig.tight_layout()
fig.savefig(OUTPUT / "ex10_users.png", dpi=120)
plt.close(fig)

# TASK 2: Save an Excel file output/ex10_report.xlsx with two sheets: "By user" (total
# amount per user) and "Top 20" (20 biggest entries).
with pd.ExcelWriter(OUTPUT / "ex10_report.xlsx") as w:
    gl.groupby("posted_by")["amount"].sum().to_excel(w, sheet_name="By user")
    gl.nlargest(20, "amount").to_excel(w, sheet_name="Top 20", index=False)
print("Saved ex10_users.png and ex10_report.xlsx")
