import argparse
import sys
from pathlib import Path
from nse_security_master.master import SecurityMaster
from nse_security_master.fetcher import SecurityMasterFetcher

def main():
    parser = argparse.ArgumentParser(description="NSE Security Master & Symbol Change Resolver")
    parser.add_argument("--resolve", nargs=2, metavar=("SYMBOL", "DATE"), help="Resolve active symbol on historical DATE (YYYY-MM-DD)")
    parser.add_argument("--sync", action="store_true", help="Sync latest active list and symbol changes from NSE")
    args = parser.parse_args()

    sm = SecurityMaster()
    if args.resolve:
        sym, dt = args.resolve
        resolved = sm.resolve_symbol_on_date(sym, dt)
        print(f"\n[RESOLVER] Symbol '{sym}' traded as '{resolved}' on {dt}.")
    else:
        print("\nNSE Security Master CLI. Use --resolve <SYMBOL> <DATE> or --sync")

if __name__ == "__main__":
    main()
