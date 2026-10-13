# Capstone Project – Year-End Ledger Review

Do this after Lesson 10. It puts everything together, like a real audit job.

## Your role

You are the junior auditor at **Sunrise Trading Ltd**. The audit manager says:

> "Here is the 2025 general ledger (`data/general_ledger.csv`) and the vendor
> master file (`data/vendors.csv`). Test **100%** of the entries, tell me what
> looks wrong, and give me one Excel file and a short memo by Friday."

## What to do (write it all in `capstone/my_capstone.py`)

1. **Load and check completeness**
   - Load both files. Print the number of rows, the total amount, and the first and last dates.
   - Is any `entry_id` repeated? Are any numbers missing from the sequence?

2. **Clean**
   - Change the date column to a date type. Fill blank `approved_by` and `vendor_id` with `""`.

3. **Understand the business** (analytical review)
   - Total revenue, total expenses, profit and margin for the year.
   - A monthly pivot of revenue and expenses. Which month looks odd?
   - Materiality = 5% of profit. Print it.

4. **Run at least 6 audit tests** (from Lesson 8)
   - Duplicates, weekend postings, approval limit, self-approval,
     just below the limit, blocked vendors, round amounts, outliers.
   - Put a `test` column on every exception and combine them into one table.

5. **Rank the risk**
   - Some entries fail more than one test. Count the tests failed per `entry_id`
     and sort so the riskiest entries are at the top.
   - Mark which exceptions are above materiality.

6. **Report**
   - Save `output/capstone_report.xlsx` with sheets: *Summary*, *Exceptions*, *Top risks*, *Monthly*.
   - Save one chart (for example: monthly trend, or exceptions per test).
   - Write `output/capstone_memo.txt`: 5–10 lines in plain English. What you tested,
     what you found, what you recommend.

## Marking yourself

| ✔ | Check |
|---|---|
| ☐ | Row count and total agree before and after cleaning |
| ☐ | At least 6 tests, each with a one-line "why" comment |
| ☐ | One combined exceptions table with a `test` column |
| ☐ | Entries failing several tests are ranked first |
| ☐ | Excel file opens and is easy to read |
| ☐ | The memo could be understood by someone who can't code |

Stuck? Compare with `capstone/capstone_solution.py` – but finish your own version first.
