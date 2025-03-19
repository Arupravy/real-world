# src/main.py
import argparse
from datetime import datetime, timedelta
from tabulate import tabulate
from price_engine.aggregator import PriceAggregator
from price_engine.price_calculator import PriceCalculator
from price_engine.data_sources.coingecko_api import CoinGeckoAPI

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Fetch and display cryptocurrency prices.")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["live", "historical"],
        required=True,
        help="Mode to run the script in: 'live' or 'historical'.",
    )
    parser.add_argument(
        "--from",
        dest="from_date",
        type=str,
        help="Start date for historical prices (format: YYYY-MM-DD). Required for historical mode.",
    )
    parser.add_argument(
        "--to",
        dest="to_date",
        type=str,
        help="End date for historical prices (format: YYYY-MM-DD). Required for historical mode.",
    )
    return parser.parse_args()

def fetch_historical_prices(symbol: str, from_date: str, to_date: str) -> list:
    """Fetch historical prices for the specified date range."""
    coingecko = CoinGeckoAPI()
    coin_id = "bitcoin" if symbol == "BTCUSDT" else "ethereum"  # Map symbol to CoinGecko ID
    historical_prices = []

    # Convert date strings to datetime objects
    start_date = datetime.strptime(from_date, "%Y-%m-%d")
    end_date = datetime.strptime(to_date, "%Y-%m-%d")

    # Fetch prices for each date in the range
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%d-%m-%Y")  # CoinGecko format
        try:
            price = coingecko.get_historical_price(coin_id, date_str)
            historical_prices.append({
                "timestamp": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "source": "coingecko",
                "price": price,
            })
        except Exception as e:
            print(f"Failed to fetch historical price for {date_str}: {e}")
        current_date += timedelta(days=1)  # Move to the next day

    return historical_prices

def run_live_mode():
    """Fetch and display live prices from all sources."""
    aggregator = PriceAggregator()
    symbol = "BTCUSDT"

    # Fetch prices and calculate weighted average
    prices = aggregator.get_all_prices(symbol)
    prices = PriceCalculator.handle_outliers(prices)
    weights = {source: info["weight"] for source, info in aggregator.sources.items()}
    weighted_avg_price = PriceCalculator.calculate_weighted_average(prices, weights)

    # Display current prices
    print("Live Prices from all sources:")
    for source, price in prices.items():
        print(f"{source}: {price}")
    print(f"Weighted Average Price: {weighted_avg_price}")

def run_historical_mode(from_date: str, to_date: str):
    """Fetch and display historical prices for the specified date range."""
    symbol = "BTCUSDT"
    historical_prices = fetch_historical_prices(symbol, from_date, to_date)

    # Display historical prices in a table
    if historical_prices:
        print("\nHistorical Prices:")
        print(tabulate(historical_prices, headers="keys", tablefmt="pretty"))
    else:
        print("\nNo historical prices available for the specified date range.")

if __name__ == "__main__":
    args = parse_args()

    if args.mode == "live":
        run_live_mode()
    elif args.mode == "historical":
        if not args.from_date or not args.to_date:
            print("Error: --from and --to dates are required for historical mode.")
        else:
            run_historical_mode(args.from_date, args.to_date)