# src/price_engine/aggregator.py
from .data_sources.binance_api import BinanceAPI
from .data_sources.coingecko_api import CoinGeckoAPI
from .data_sources.coinbase_api import CoinbaseAPI
from .price_calculator import PriceCalculator
from .price_history import PriceHistory  # Import PriceHistory

class PriceAggregator:
    def __init__(self):
        self.sources = {
            "binance": {"handler": BinanceAPI(), "weight": 0.4},
            "coingecko": {"handler": CoinGeckoAPI(), "weight": 0.3},
            "coinbase": {"handler": CoinbaseAPI(), "weight": 0.3},
        }
        self.price_history = PriceHistory()  # Initialize PriceHistory

    def get_all_prices(self, symbol: str) -> dict:
        prices = {}
        for source_name, source_info in self.sources.items():
            try:
                if source_name == "coingecko":
                    coin_id = self._get_coin_id(symbol)
                    price = source_info["handler"].get_price(coin_id)
                else:
                    price = source_info["handler"].get_price(symbol)
                prices[source_name] = price
                # Add price to history
                self.price_history.add_price(symbol, source_name, price)
            except Exception as e:
                print(f"Error fetching data from {source_name}: {e}")
                prices[source_name] = None
        return prices

    def _get_coin_id(self, symbol: str) -> str:
        coin_id_map = {
            "BTCUSDT": "bitcoin",
            "ETHUSDT": "ethereum",
        }
        return coin_id_map.get(symbol, symbol.lower())

    def get_price_history(self) -> list:
        """Return the price history."""
        return self.price_history.get_history()