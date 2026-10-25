
import pandas as pd

input_file = "sih_batch1_raw.csv"
output_file = "sih_batch1_clean.csv"

# Read the raw extraction without assuming a header
df = pd.read_csv(input_file, header=None, dtype=str)

# Remove completely empty rows and columns
df = df.dropna(how="all").dropna(axis=1, how="all")

# Remove whitespace and normalize empty cells
df = df.fillna("")
df = df.apply(
    lambda column: column.str.strip()
)

# Keep only rows whose first column looks like an SIH problem ID
df = df[
    df.iloc[:, 0].str.match(r"^SIH\d+$", na=False)
].copy()

# Remove duplicate rows
df = df.drop_duplicates()

df.to_csv(output_file, index=False, header=False)

print("Cleaning completed!")
print("Rows retained:", len(df))
print("Saved to:", output_file)
print("\nFirst 10 rows:")
print(df.head(10).to_string(index=False, header=False))
