
import pdfplumber
import pandas as pd

pdf_path = "../sih-2k25batch1.pdf"
output_path = "sih_batch1_clean.csv"

records = []

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()

        for table in tables:
            for row in table:
                # Actual data rows have SIH IDs in column 2
                if not row or len(row) < 10:
                    continue

                if not row[2] or not row[2].strip().startswith("SIH"):
                    continue

                records.append({
                    "problem_statement_id": row[2].strip(),
                    "organization": (row[3] or "").replace("\n", " ").strip(),
                    "department": (row[4] or "").replace("\n", " ").strip(),
                    "serial_number": row[5],
                    "idea_id": row[6],
                    "team_id": row[7],
                    "team_name": (row[8] or "").replace("\n", " ").strip(),
                    "team_leader": (row[9] or "").replace("\n", " ").strip(),
                })

df = pd.DataFrame(records)
df = df.drop_duplicates()
df.to_csv(output_path, index=False)

print("Records extracted:", len(df))
print("\nMissing values:")
print(df.isnull().sum())
print("\nFirst 10 records:")
print(df.head(10).to_string(index=False))
print("\nSaved to:", output_path)
