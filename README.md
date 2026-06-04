# Stock Price Tracker

Automated daily scraper that collects stock prices from Yahoo Finance and saves them to CSV. Runs on GitHub Actions every weekday — no manual input required.

## What it does

- Fetches closing prices for 7 major stocks (AAPL, TSLA, GOOGL, MSFT, AMZN, NVDA, META)
- Calculates daily % change vs previous close
- Appends results to `prices.csv`
- Runs automatically Monday–Friday at 21:00 UTC via GitHub Actions

## Stack

Python · yfinance · GitHub Actions · CSV

## Output format

| date | symbol | price | prev_close | change_pct |
|------|--------|-------|------------|------------|
| 2026-06-04 | AAPL | 201.45 | 199.30 | +1.08 |
| 2026-06-04 | TSLA | 178.90 | 181.20 | -1.27 |

## Run locally

```bash
pip install yfinance
python scraper.py
```
