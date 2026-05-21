#IntradayTradeStockAnalyser/backend/utils/replay_store.py
class ReplayStore:

    stock_candles = []

    @classmethod
    def set_stock_candles(
        cls,
        candles
    ):

        cls.stock_candles = candles

    @classmethod
    def get_stock_candles(cls):

        return cls.stock_candles