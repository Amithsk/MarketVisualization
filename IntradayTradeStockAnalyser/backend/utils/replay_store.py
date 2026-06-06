#IntradayTradeStockAnalyser/backend/utils/replay_store.py

class ReplayStore:

    stock_candles = []

    @classmethod
    def set_stock_candles(
        cls,
        candles
    ):

        cumulative_price_volume = 0.0

        cumulative_volume = 0.0

        processed_candles = []

        for candle in candles:

            high = float(candle.high)

            low = float(candle.low)

            close = float(candle.close)

            volume = float(candle.volume)

            typical_price = (
                high + low + close
            ) / 3

            cumulative_price_volume += (
                typical_price * volume
            )

            cumulative_volume += volume

            vwap = 0.0

            if cumulative_volume > 0:

                vwap = (
                    cumulative_price_volume
                    / cumulative_volume
                )

            candle.vwap = round(
                vwap,
                2
            )

            processed_candles.append(
                candle
            )

        cls.stock_candles = processed_candles

    @classmethod
    def get_stock_candles(cls):

        return cls.stock_candles