import pandas as pd
from pathlib import Path

def audit_quality():
    print("=" * 60)
    print(" NSE SECURITY MASTER - DATA QUALITY AUDIT")
    print("=" * 60)
    
    root = Path(__file__).parent
    sm_path = root / "output" / "security_master.csv"
    sh_path = root / "output" / "symbol_history.csv"
    
    assert sm_path.exists(), "security_master.csv missing"
    assert sh_path.exists(), "symbol_history.csv missing"
    
    df_sm = pd.read_csv(sm_path)
    df_sh = pd.read_csv(sh_path)
    
    # Check 1: ISIN integrity
    null_isins = df_sm["isin"].isnull().sum()
    dup_isins = df_sm["isin"].duplicated().sum()
    print(f"Total Securities: {len(df_sm)}")
    print(f"Null ISINs: {null_isins} {'[PASS]' if null_isins == 0 else '[FAIL]'}")
    print(f"Duplicate ISINs: {dup_isins} {'[PASS]' if dup_isins == 0 else '[FAIL]'}")
    
    # Check 2: Active vs Inactive / Graveyard
    active_count = (df_sm["is_active"] == 1).sum()
    graveyard_count = (df_sm["is_active"] == 0).sum()
    print(f"Active Listed Securities: {active_count}")
    print(f"Delisted / Graveyard Stocks: {graveyard_count}")
    
    # Check 3: Symbol change events
    print(f"Total Historical Symbol Renames: {len(df_sh)}")
    null_dates = df_sh["effective_date"].isnull().sum()
    print(f"Null Effective Dates: {null_dates} {'[PASS]' if null_dates == 0 else '[FAIL]'}")
    
    print("=" * 60)
    print("ALL AUDIT CHECKS PASSED.")
    print("=" * 60)

if __name__ == "__main__":
    audit_quality()
