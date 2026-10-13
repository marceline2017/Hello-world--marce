"""EXERCISE 5 - pandas intro

Write your code under each TODO, then run:
    python exercises/exercise05.py
Stuck? Peek at solutions/solution05.py - but try first!
"""

from pathlib import Path
import pandas as pd
DATA = Path(__file__).parent.parent / "data"

# TASK 1: Load data/general_ledger.csv into a DataFrame called gl. Print its shape and
# the first 3 rows.
# TODO


# TASK 2: What is the total, average and largest amount in the ledger?
# TODO


# TASK 3: Which user posted the most entries? (hint: value_counts)
# TODO


# TASK 4: Add a column "quarter" using gl["date"].dt.quarter and show how many entries
# fall in each quarter.
# TODO
