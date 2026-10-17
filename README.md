# NSE Security Master & Historical Graveyard

Permanent **ISIN-keyed security master** for 2,600+ listed Indian equities, 1,000+ historical ticker mutations (1994–2026), and a historical registry of delisted, insolvent, or suspended companies with terminal salvage rates.

Companion repository to [`prathmeshgupta/nifty-pit-universe`](https://github.com/prathmeshgupta/nifty-pit-universe).

---

## 📊 Summary of Datasets

All processed datasets are saved in [`output/`](output/):

| Dataset | Records | Unique ISINs | Primary Key | Formats |
| :--- | :---: | :---: | :--- | :--- |
| **Security Master** | **2,606** | **2,606** | `isin` | [`security_master.parquet`](output/security_master.parquet), [`security_master.csv`](output/security_master.csv) |
| **Symbol History** | **1,067** | — | `(old_symbol, new_symbol, effective_date)` | [`symbol_history.parquet`](output/symbol_history.parquet), [`symbol_history.csv`](output/symbol_history.csv) |

---

## 💡 Why This Exists: The Identifier & Survivorship Trap

In quantitative backtesting of Indian equities, naive ticker-based systems fail in two catastrophic ways:
1. **Ticker Renaming Drift**: Companies frequently change their exchange ticker. For example, `MINDTREE` became `LTIM`, `CADILAHC` became `ZYDUSLIFE`, and `UTIBANK` became `AXISBANK`. If your backtest uses modern tickers, historical data before the rename date returns as missing or gets dropped.
2. **The Disappearing Bankruptcy Trap (Survivorship Bias)**: Bankrupt companies (e.g., *DHFL, Reliance Communications, Sintex Industries, Bhushan Steel*) vanish from current active ticker lists. If backtests only pull active tickers, historical portfolios never realize the $-100\%$ catastrophic drawdown of failed holdings.

This repository anchors every security to its permanent international identifier (**ISIN**) and provides an automated resolver that traverses ticker history to determine what symbol actually traded on date $T$.

---

## 🧱 Data Schema

### `security_master`
| Column | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `isin` | String (12 chars) | Primary Key: Permanent ISO 6166 identifier | `INE002A01018` |
| `current_symbol` | String | Current/Last active exchange ticker | `RELIANCE` |
| `company_name` | String | Full legal corporate name | `Reliance Industries Limited` |
| `series` | String | Exchange trading series | `EQ` |
| `listing_date` | Date | IPO / initial listing date | `1995-11-29` |
| `delisting_date` | Date | Date of suspension/delisting (`NULL` if active) | `2021-06-14` |
| `is_active` | Integer | `1` = Currently trading, `0` = Delisted / Insolvent | `1` |
| `delisting_reason`| String | Reason for removal | `CIRP_INSOLVENCY` |
| `terminal_salvage_rate`| Float | Terminal return/recovery rate | `0.0` ($-100\%$ loss) |

### `symbol_history`
| Column | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `old_symbol` | String | Former exchange ticker | `MINDTREE` |
| `new_symbol` | String | Successor exchange ticker | `LTIM` |
| `effective_date` | Date | Effective date of rename on exchange | `2022-11-24` |
| `source` | String | Regulatory archive source | `NSE_SYMBOL_CHANGE` |

---

## 🔍 How to Query

### 1. Using Python & Pandas
```python
import pandas as pd

# Load security master
df = pd.read_parquet("output/security_master.parquet")

# Inspect insolvent / delisted companies in the graveyard
graveyard = df[df["is_active"] == 0]
print(f"Total delisted securities tracked: {len(graveyard)}")
print(graveyard[["isin", "current_symbol", "company_name", "delisting_date", "terminal_salvage_rate"]])
```

### 2. Using the CLI Symbol Resolver
```bash
# Resolve what symbol LTIM traded under on 2021-05-01 (Output: MINDTREE)
python runner.py --resolve LTIM 2021-05-01
```

---

## 🧪 Quality Audit
```bash
python evaluate_quality.py
```
* **ISIN Integrity**: 0 null ISINs, 0 duplicate ISINs ([PASS]).
* **Graveyard Preservation**: Insolvent and suspended entities preserved with terminal recovery rates ([PASS]).
* **Historical Ticker Changes**: 1,067 verified historical ticker renames ([PASS]).

---

## 📄 License
MIT License. Copyright (c) 2026 Prathmesh Gupta.
