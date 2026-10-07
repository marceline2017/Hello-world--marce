# Python for Finance & Auditing – a Beginner's Course

You don't need any coding experience. Every lesson uses **simple words** and
**real finance and audit examples**: invoices, ledgers, VAT, depreciation,
loans, ratios and audit tests.

At the end you will be able to take a client's ledger, test **every** entry
for red flags, and hand your manager a clean Excel report with charts and a
written memo.

---

## 1. Setup (one time, about 15 minutes)

1. **Install Python.** Go to <https://www.python.org/downloads/> and download
   the latest version. On Windows, **tick the box "Add Python to PATH"**
   during installation.
2. **Install a code editor.** I recommend **VS Code**
   (<https://code.visualstudio.com/>). Add the "Python" extension inside it.
3. **Open a terminal** (in VS Code: menu *Terminal → New Terminal*) and go to
   this folder:
   ```
   cd python-for-finance
   ```
4. **Install the tools** we use:
   ```
   pip install -r requirements.txt
   ```
   (If `pip` is not found, try `python -m pip install -r requirements.txt`.
   On Mac you may need `python3` instead of `python`.)
5. **Make the practice data:**
   ```
   python data/make_data.py
   ```
6. **Run your first lesson:**
   ```
   python lessons/lesson01_basics.py
   ```
   If text appears on screen, you're ready!

**No install option:** you can also paste any lesson into
[Google Colab](https://colab.research.google.com/) (free, works in the browser).
Upload the files from `data/` into Colab first.

---

## 2. How to study

For each lesson:

1. **Read** the lesson file from top to bottom. The comments (`#`) explain every line.
2. **Run** it, then compare what you read with what's on the screen.
3. **Change something** – a number, a name – and run it again. Breaking things is
   how you learn. You can't damage anything.
4. Do the **exercise** (`exercises/exerciseNN.py`). Write your code under each `TODO`.
5. Only then look at the **solution** (`solutions/solutionNN.py`).

Aim for **1 lesson per week** with about 30–45 minutes a day. Type the code
yourself – don't copy and paste. Your fingers learn too.

---

## 3. The lessons

| # | Lesson | You will learn | Finance / audit example |
|---|--------|----------------|-------------------------|
| 1 | [Basics](lessons/lesson01_basics.py) | variables, numbers, text, f-strings | profit, margin, cleaning a bank amount |
| 2 | [Lists, dicts, if, loops](lessons/lesson02_decisions_and_loops.py) | storing many values, decisions, repeating | approval-limit check, budget variance |
| 3 | [Functions](lessons/lesson03_functions.py) | building your own tools | VAT, interest, depreciation, materiality |
| 4 | [Files & errors](lessons/lesson04_files_and_errors.py) | reading/writing CSV, `try/except` | totals per account, messy amounts |
| 5 | [pandas intro](lessons/lesson05_pandas_intro.py) | DataFrames – "Excel in Python" | exploring a 1,200-row ledger |
| 6 | [Cleaning data](lessons/lesson06_cleaning_data.py) | spaces, `$` and `,`, blanks, duplicates | cleaning a client invoice list |
| 7 | [Filter, group, pivot, merge](lessons/lesson07_filter_group_merge.py) | SUMIF, pivot tables, VLOOKUP in Python | monthly profit report, vendor spend |
| 8 | [Audit analytics](lessons/lesson08_audit_analytics.py) | journal entry testing on 100% of data | duplicates, weekends, self-approval, Benford's Law |
| 9 | [Finance calculations](lessons/lesson09_finance_calculations.py) | time value of money | NPV, IRR, loan schedules, ratios, returns |
| 10 | [Charts & reports](lessons/lesson10_charts_and_reports.py) | matplotlib, Excel output | management report with charts |
| ★ | [Capstone project](capstone/PROJECT_BRIEF.md) | everything together | a full year-end ledger review + memo |

All outputs (Excel files, charts, CSVs) are saved in the `output/` folder.

---

## 4. The practice data

`python data/make_data.py` creates made-up data for "Sunrise Trading Ltd":

- `general_ledger.csv` – about 1,200 accounting entries for 2025.
  **Problems are hidden in it on purpose**: duplicate payments, weekend
  entries, missing approvals, self-approvals, amounts just under the
  approval limit, payments to a blocked vendor, round amounts, an
  unusually large purchase and missing entry numbers. Lesson 8 and the
  capstone teach you to find them all.
- `vendors.csv` – the approved supplier list (one supplier is blocked).
- `messy_invoices.csv` – a small, very dirty file for the cleaning lesson.

---

## 5. When you get an error (you will – everyone does!)

1. **Read the LAST line** of the red message first. It names the problem.
2. Common ones:

| Error | What it usually means |
|-------|------------------------|
| `NameError` | A typo in a variable name, or you used it before creating it |
| `SyntaxError` | A missing `:` `)` or `"` |
| `IndentationError` | The spaces at the start of a line are wrong (use 4 spaces) |
| `TypeError` | Mixing text and numbers, e.g. `"5" + 5` |
| `ValueError` | Converting something impossible, e.g. `float("n/a")` |
| `KeyError` | That column / dictionary key doesn't exist – check spelling and spaces |
| `FileNotFoundError` | Wrong folder – run commands from inside `python-for-finance` |
| `ModuleNotFoundError` | A library isn't installed – run `pip install -r requirements.txt` |

3. Still stuck? Copy the error message into a search engine or ask an AI
   assistant – include your code and the full message.

---

## 6. Excel → Python quick reference

| In Excel | In Python (pandas) |
|----------|--------------------|
| Open a file | `df = pd.read_excel("file.xlsx")` or `pd.read_csv("file.csv")` |
| Look at the top rows | `df.head()` |
| `=SUM(B:B)` | `df["amount"].sum()` |
| `=AVERAGE(B:B)` | `df["amount"].mean()` |
| `=COUNTIF(A:A, "x")` | `(df["col"] == "x").sum()` |
| `=SUMIF` / subtotals | `df.groupby("account")["amount"].sum()` |
| Filter | `df[df["amount"] > 10000]` |
| Sort | `df.sort_values("amount", ascending=False)` |
| Pivot table | `pd.pivot_table(df, index=..., columns=..., values=..., aggfunc="sum")` |
| `VLOOKUP` / `XLOOKUP` | `df.merge(other, on="key", how="left")` |
| Remove duplicates | `df.drop_duplicates()` |
| `=TRIM()` `=PROPER()` | `df["col"].str.strip().str.title()` |
| `=IF()` | `np.where(df["amount"] > 10000, "Big", "Small")` (needs `import numpy as np`) |
| `=PMT()` | see `loan_payment()` in Lesson 9 |
| Save as Excel | `df.to_excel("out.xlsx", index=False)` |

---

## 7. After this course – what to learn next

1. **Practise on real public data** – company annual reports, central bank
   exchange rates, stock prices (`pip install yfinance`), government
   spending data (data.gov, Kaggle).
2. **Jupyter Notebooks** – write code and notes together; great for audit
   working papers. Install with `pip install notebook`, start with
   `jupyter notebook`.
3. **SQL** – most company data lives in databases. Learn `SELECT`,
   `WHERE`, `GROUP BY`, `JOIN`. (You already know the ideas from Lesson 7!)
4. **Power BI or Tableau** – dashboards that managers love.
5. **Automation** – reconcile bank statements, merge 50 Excel files at once,
   send monthly reports automatically.
6. **Statistics for audit** – sampling, regression, and the `scipy` and
   `statsmodels` libraries.
7. **Certifications** that value these skills: CISA (IT audit),
   the ACCA / CPA data analytics modules, and Microsoft's PL-300 (Power BI).

Good luck – and remember the promise in the main README. You've got this! 💪
