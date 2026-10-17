import io
import requests
import pandas as pd
from typing import Optional

NSE_EQUITY_L_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
NSE_SYMBOL_CHANGE_URL = "https://archives.nseindia.com/content/equities/symbolchange.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class SecurityMasterFetcher:
    """Fetches active securities and historical symbol change events from official NSE archives."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch_active_securities(self) -> pd.DataFrame:
        resp = self.session.get(NSE_EQUITY_L_URL, timeout=15)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text))
        df.columns = [c.strip().replace(" ", "_").upper() for c in df.columns]
        
        rename_map = {
            "SYMBOL": "current_symbol",
            "NAME_OF_COMPANY": "company_name",
            "SERIES": "series",
            "DATE_OF_LISTING": "listing_date",
            "PAID_UP_VALUE": "paid_up_value",
            "MARKET_LOT": "market_lot",
            "ISIN_NUMBER": "isin",
            "FACE_VALUE": "face_value"
        }
        df = df.rename(columns=rename_map)
        df["listing_date"] = pd.to_datetime(df["listing_date"], errors="coerce").dt.strftime("%Y-%m-%d").fillna(df["listing_date"])
        df["is_active"] = 1
        df["source"] = "NSE_EQUITY_L"
        return df

    def fetch_symbol_changes(self) -> pd.DataFrame:
        resp = self.session.get(NSE_SYMBOL_CHANGE_URL, timeout=15)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text))
        df.columns = [c.strip().replace(" ", "_").upper() for c in df.columns]

        rename_map = {
            "NAME_OF_THE_COMPANY": "company_name",
            "OLD_SYMBOL": "old_symbol",
            "NEW_SYMBOL": "new_symbol",
            "EFFECTIVE_DATE": "effective_date"
        }
        df = df.rename(columns=rename_map)
        df["effective_date"] = pd.to_datetime(df["effective_date"], errors="coerce").dt.strftime("%Y-%m-%d").fillna(df["effective_date"])
        df["source"] = "NSE_SYMBOL_CHANGE"
        return df
