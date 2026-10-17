import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional

DEFAULT_DB = Path(__file__).resolve().parent.parent.parent / "output" / "security_master.db"


class SecurityMaster:
    """Manages permanent ISIN-based ticker resolutions and historical corporate graveyard."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB
        self._init_db()

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS security_master (
                isin TEXT PRIMARY KEY,
                current_symbol TEXT NOT NULL,
                company_name TEXT NOT NULL,
                series TEXT DEFAULT 'EQ',
                listing_date DATE,
                delisting_date DATE,
                is_active INTEGER DEFAULT 1,
                delisting_reason TEXT,
                terminal_salvage_rate REAL DEFAULT 0.0,
                face_value REAL,
                paid_up_value REAL,
                market_lot INTEGER,
                source TEXT
            );
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS symbol_history (
                old_symbol TEXT NOT NULL,
                new_symbol TEXT NOT NULL,
                effective_date DATE NOT NULL,
                source TEXT,
                PRIMARY KEY (old_symbol, new_symbol, effective_date)
            );
            """)
            conn.commit()

    def resolve_symbol_on_date(self, symbol: str, query_date: str) -> str:
        """
        Traverses symbol history in reverse to determine the active trading symbol on query_date.
        """
        with sqlite3.connect(str(self.db_path)) as conn:
            df = pd.read_sql_query(
                "SELECT old_symbol, new_symbol, effective_date FROM symbol_history WHERE old_symbol = ? OR new_symbol = ? ORDER BY effective_date DESC",
                conn,
                params=[symbol, symbol]
            )
        if df.empty:
            return symbol

        current = symbol
        for _, row in df.iterrows():
            eff_dt = str(row["effective_date"])
            if query_date < eff_dt and current == row["new_symbol"]:
                current = row["old_symbol"]
        return current
