import yfinance as yf
import csv
import datetime
import os

STOCKS = ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN", "NVDA", "META"]
OUTPUT_FILE = "prices.csv"


def fetch_price(symbol: str) -> dict | None:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        return {
            "date": datetime.date.today().isoformat(),
            "symbol": symbol,
            "price": round(info["last_price"], 2),
            "prev_close": round(info["previous_close"], 2),
            "change_pct": round((info["last_price"] - info["previous_close"]) / info["previous_close"] * 100, 2),
        }
    except Exception as e:
        print(f"Failed to fetch {symbol}: {e}")
        return None


def save_to_csv(rows: list[dict]) -> None:
    fieldnames = ["date", "symbol", "price", "prev_close", "change_pct"]
    write_header = not os.path.exists(OUTPUT_FILE) or os.path.getsize(OUTPUT_FILE) == 0
    with open(OUTPUT_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def main():
    print(f"Starting scrape — {datetime.date.today()}")
    results = []

    for symbol in STOCKS:
        data = fetch_price(symbol)
        if data:
            results.append(data)
            print(f"  {symbol}: ${data['price']}  ({data['change_pct']:+.2f}%)")

    if results:
        save_to_csv(results)
        print(f"\nSaved {len(results)} records to {OUTPUT_FILE}")
    else:
        print("No data collected.")


if __name__ == "__main__":
    main()
