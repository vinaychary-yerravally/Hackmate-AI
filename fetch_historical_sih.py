import json
import pandas as pd
from curl_cffi import requests

# Direct DataTables / API endpoints used by the SIH portal
ENDPOINTS = {
    "2024": "https://sih.gov.in/sih2024PS",
    "2023": "https://sih.gov.in/sih2023PS"
}

# Verified community archives for fallback/comprehensive multi-year coverage
COMMUNITY_ARCHIVES = [
    {
        "year": "2024",
        "url": "https://raw.githubusercontent.com/vedantchalke36/sih-2026-problem-statements/main/sih2024.csv"
    },
    {
        "year": "2023",
        "url": "https://raw.githubusercontent.com/vedantchalke36/sih-2026-problem-statements/main/sih2023.csv"
    }
]

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {}
    for col in df.columns:
        c = str(col).lower().strip().replace(" ", "_")
        if any(k in c for k in ["id", "number", "code", "ps"]):
            mapping[col] = "problem_statement_id"
        elif any(k in c for k in ["title", "name", "statement"]):
            mapping[col] = "title"
        elif any(k in c for k in ["category", "bucket"]):
            mapping[col] = "category"
        elif any(k in c for k in ["theme", "domain"]):
            mapping[col] = "theme"
        elif any(k in c for k in ["org", "creator", "ministry"]):
            mapping[col] = "organization"
        elif any(k in c for k in ["desc", "detail"]):
            mapping[col] = "description"

    return df.rename(columns=mapping)

def fetch_from_github_archives() -> pd.DataFrame:
    """Fallback fetcher pulling verified SIH historical snapshot CSVs directly."""
    print("\nFetching official community historical archives (2023-2024)...")
    dfs = []
    
    session = requests.Session(impersonate="chrome120")
    for item in COMMUNITY_ARCHIVES:
        try:
            res = session.get(item["url"], timeout=15)
            if res.status_code == 200:
                from io import StringIO
                df = pd.read_csv(StringIO(res.text))
                df = clean_column_names(df)
                df["sih_year"] = item["year"]
                dfs.append(df)
                print(f"✅ Loaded {len(df)} records for SIH {item['year']} from archive!")
        except Exception as e:
            print(f"⚠️ Could not load archive for {item['year']}: {e}")
            
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def main():
    df_archive = fetch_from_github_archives()
    
    if not df_archive.empty:
        # Standardize columns
        for col in ["problem_statement_id", "title", "category", "theme", "organization", "description"]:
            if col not in df_archive.columns:
                df_archive[col] = ""
            else:
                df_archive[col] = df_archive[col].fillna("").astype(str)

        df_archive = df_archive.drop_duplicates(subset=["title"]).reset_index(drop=True)

        output_file = "sih_multiyear_dataset.csv"
        df_archive.to_csv(output_file, index=False)
        print(f"\n🎉 Successfully saved {len(df_archive)} multi-year problem statements to '{output_file}'!")
    else:
        print("\nFailed to retrieve historical dataset. Verify internet access.")

if __name__ == "__main__":
    main()