import os
import csv
import datetime

import requests
import yfinance as yf


STOCKS = ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN", "NVDA", "META"]
OUTPUT_FILE = "prices.csv"

# Only notify when a stock moves at least this much, in percent
ALERT_THRESHOLD = 3.0


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


def send_telegram(text: str) -> None:
    """Send a message if bot credentials are configured, stay quiet otherwise."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram credentials not set, skipping notification.")
        return

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        response.raise_for_status()
        print("Telegram alert sent.")
    except requests.RequestException as e:
        # A failed notification should never break the data collection run
        print(f"Failed to send Telegram alert: {e}")


def build_alert(rows: list[dict]) -> str | None:
    """Return an alert message for stocks that moved past the threshold."""
    movers = [r for r in rows if abs(r["change_pct"]) >= ALERT_THRESHOLD]
    if not movers:
        return None

    movers.sort(key=lambda r: abs(r["change_pct"]), reverse=True)

    lines = [f"<b>Market movers — {datetime.date.today().isoformat()}</b>", ""]
    for r in movers:
        arrow = "▲" if r["change_pct"] > 0 else "▼"
        lines.append(
            f"{arrow} <b>{r['symbol']}</b>  ${r['price']}  ({r['change_pct']:+.2f}%)"
        )

    return "\n".join(lines)


def main():
    print(f"Starting scrape — {datetime.date.today()}")

    results = []
    for symbol in STOCKS:
        data = fetch_price(symbol)
        if data:
            results.append(data)
            print(f"  {symbol}: ${data['price']}  ({data['change_pct']:+.2f}%)")

    if not results:
        print("No data collected.")
        return

    save_to_csv(results)
    print(f"\nSaved {len(results)} records to {OUTPUT_FILE}")

    alert = build_alert(results)
    if alert:
        send_telegram(alert)
    else:
        print(f"No stock moved more than {ALERT_THRESHOLD}%, no alert sent.")


if __name__ == "__main__":
    main()
