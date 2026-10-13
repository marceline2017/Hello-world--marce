"""
LESSON 6 - CLEANING MESSY DATA
==============================

Analysts say 80% of the work is cleaning data. Client files come with:
extra spaces, different spellings, "$" and "," inside numbers, blanks,
duplicates, and dates stored as text.

If you skip cleaning, your totals are WRONG. "acme corp" and "ACME CORP "
look like two customers to a computer!

Run:  python lessons/lesson06_cleaning_data.py
"""

from pathlib import Path
import pandas as pd

DATA = Path(__file__).parent.parent / "data"
OUTPUT = Path(__file__).parent.parent / "output"
OUTPUT.mkdir(exist_ok=True)
pd.set_option("display.width", 120)

# Read every column as text first, so nothing is changed by surprise.
df = pd.read_csv(DATA / "messy_invoices.csv", dtype=str)
print("RAW DATA:")
print(df)
rows_received = len(df)


# ---------------------------------------------------------------
# Step 1. Clean the column names
# ---------------------------------------------------------------
print("\nOld column names:", df.columns.tolist())
df.columns = (
    df.columns
    .str.strip()                  # remove outside spaces
    .str.lower()                  # small letters
    .str.replace(" ", "_")        # spaces -> underscores
)
print("New column names:", df.columns.tolist())


# ---------------------------------------------------------------
# Step 2. Clean text columns
# ---------------------------------------------------------------
# .str gives you all the text tools from Lesson 1, for a whole column.
df["customer"] = df["customer"].str.strip().str.title()
df["status"] = df["status"].str.strip().str.title()
print("\nCustomers now:", df["customer"].unique())
print("Statuses now:", df["status"].unique())


# ---------------------------------------------------------------
# Step 3. Clean the money column
# ---------------------------------------------------------------
df["amount"] = (
    df["amount"]
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.strip()
)
# errors="coerce" = if it can't be a number, make it NaN (= missing)
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")


# ---------------------------------------------------------------
# Step 4. Convert dates
# ---------------------------------------------------------------
df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")


# ---------------------------------------------------------------
# Step 5. Find missing values
# ---------------------------------------------------------------
# NaN means "Not a Number" - pandas' way of saying "empty / missing".
df["customer"] = df["customer"].replace("", pd.NA)
print("\nMissing values per column:")
print(df.isna().sum())

print("\nRows with a missing amount or customer:")
missing = df[df["amount"].isna() | df["customer"].isna()]
print(missing)

# Options for missing data:
#   df.dropna()                 remove the rows
#   df["amount"].fillna(0)      fill with a value
# In AUDIT, never silently delete or fill! Put problems in an
# exceptions list and ASK the client. That is what we do here.
missing.to_csv(OUTPUT / "invoices_to_query.csv", index=False)


# ---------------------------------------------------------------
# Step 6. Duplicates
# ---------------------------------------------------------------
dups = df[df.duplicated(keep=False)]     # keep=False shows ALL copies
print("\nDuplicate rows:")
print(dups)

df = df.drop_duplicates()
print("Rows after removing exact duplicates:", len(df))

# Also check the invoice number alone - should be unique!
print("Repeated invoice numbers:",
      df["invoice_no"][df["invoice_no"].duplicated()].tolist())


# ---------------------------------------------------------------
# Step 7. The clean table and a reconciliation
# ---------------------------------------------------------------
clean = df.dropna(subset=["amount", "customer"])
print("\nCLEAN DATA:")
print(clean)

# Good practice: show what happened to every row (a mini reconciliation)
print(f"\nRows received:          {rows_received}")
print(f"Duplicates removed:     {rows_received - len(df)}")
print(f"Sent to client query:   {len(missing)}")
print(f"Clean rows:             {len(clean)}")

print("\nTotal by customer (now correct!):")
print(clean.groupby("customer")["amount"].sum())

clean.to_csv(OUTPUT / "clean_invoices.csv", index=False)
print("\nSaved output/clean_invoices.csv")


# ===============================================================
# CLEANING CHECKLIST (use it on every new file)
#   [ ] df.head(), df.info()            look first
#   [ ] fix column names                strip, lower, underscores
#   [ ] strip and standardise text      .str.strip().str.title()
#   [ ] numbers: remove $ and ,         pd.to_numeric(errors="coerce")
#   [ ] dates                           pd.to_datetime(errors="coerce")
#   [ ] missing values                  df.isna().sum()
#   [ ] duplicates                      df.duplicated()
#   [ ] reconcile row counts and totals before vs after
#
# NEXT: exercises/exercise06.py
# ===============================================================
