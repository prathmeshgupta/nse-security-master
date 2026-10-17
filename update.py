"""
Automated Weekly Dataset Updater for nse-security-master
Can be executed locally or via GitHub Actions.
Zero credentials required.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
from nse_security_master.fetcher import SecurityMasterFetcher

OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SM_CSV = OUTPUT_DIR / "security_master.csv"
SM_PARQUET = OUTPUT_DIR / "security_master.parquet"
SH_CSV = OUTPUT_DIR / "symbol_history.csv"
SH_PARQUET = OUTPUT_DIR / "symbol_history.parquet"


def update():
    print("[1/4] Fetching latest active securities and symbol changes from NSE archives...")
    fetcher = SecurityMasterFetcher()
    
    active_df = fetcher.fetch_active_securities()
    changes_df = fetcher.fetch_symbol_changes()
    print(f"      Retrieved {len(active_df)} listed scrips and {len(changes_df)} symbol changes.")

    # 1. Update Security Master
    print("[2/4] Merging with existing security master and preserving historical graveyard...")
    if SM_CSV.exists():
        existing_sm = pd.read_csv(SM_CSV)
        graveyard = existing_sm[existing_sm["is_active"] == 0]
    else:
        graveyard = pd.DataFrame()

    merged_sm = pd.concat([active_df, graveyard], ignore_index=True)
    merged_sm = merged_sm.drop_duplicates(subset=["isin"], keep="last")
    merged_sm = merged_sm.sort_values(by=["is_active", "current_symbol"], ascending=[False, True])

    merged_sm.to_csv(SM_CSV, index=False)
    merged_sm.to_parquet(SM_PARQUET, index=False)
    print(f"      Saved {len(merged_sm)} securities to {SM_CSV.name} and {SM_PARQUET.name}.")

    # 2. Update Symbol History
    print("[3/4] Updating symbol history...")
    isin_map = dict(zip(merged_sm["current_symbol"], merged_sm["isin"]))
    changes_df["isin"] = changes_df["new_symbol"].map(isin_map)

    # Order columns consistently
    cols = ["isin", "company_name", "old_symbol", "new_symbol", "effective_date", "source"]
    for c in cols:
        if c not in changes_df.columns:
            changes_df[c] = None
    changes_df = changes_df[cols]

    if SH_CSV.exists():
        existing_sh = pd.read_csv(SH_CSV)
        # Ensure older rows without company_name get backfilled from changes_df
        combined_sh = pd.concat([changes_df, existing_sh], ignore_index=True)
    else:
        combined_sh = changes_df.copy()

    combined_sh = combined_sh.dropna(subset=["old_symbol", "new_symbol", "effective_date"])
    # Drop duplicates keeping the one with company_name
    combined_sh = combined_sh.sort_values(by=["effective_date", "company_name"], ascending=[False, False])
    combined_sh = combined_sh.drop_duplicates(subset=["old_symbol", "new_symbol", "effective_date"], keep="first")
    combined_sh = combined_sh[cols]

    combined_sh.to_csv(SH_CSV, index=False)
    combined_sh.to_parquet(SH_PARQUET, index=False)
    print(f"      Saved {len(combined_sh)} symbol renames to {SH_CSV.name} and {SH_PARQUET.name}.")

    # 3. Quality Audit Verification
    print("[4/4] Running automated quality audit...")
    from evaluate_quality import audit_quality
    audit_quality()
    print("Update complete successfully.")


if __name__ == "__main__":
    update()
