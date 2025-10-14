- NIFTY OHLC & indicators:
  - Table: nifty_prices (Date, Open, High, Low, Close, Volume, SMA_5, SMA_20, RSI, ATR). Source: nifty_nifty_prices.sql. :contentReference[oaicite:20]{index=20}

- Predictions (forward/backtest):
  - Table: predictions (date, model_name, predicted_dir, predicted_price, is_forward). Source: nifty_predictions.sql. :contentReference[oaicite:21]{index=21}
  - Table: comparisons (date, model_name, actual_dir, predicted_dir, was_correct, error_mag). Source: nifty_comparisons.sql. :contentReference[oaicite:22]{index=22}
  - Table: model_daily_summary (summary_date, model_name, total_bars, correct, incorrect, accuracy_pct, avg_error_mag). Source: nifty_model_daily_summary.sql. :contentReference[oaicite:23]{index=23}
  - Table: forward_summary (summary_date, model_name, total_bars, bullish_count, bearish_count, bullish_pct, avg_pred_price). Source: nifty_forward_summary.sql. :contentReference[oaicite:24]{index=24}

- Intraday:
  - intraday_bhavcopy (trade_date, symbol, open, high, low, close, net_trdval, net_trdqty). Source: intradaytrading_intraday_bhavcopy.sql. :contentReference[oaicite:25]{index=25}
  - gainers_losers (trade_date, symbol, pct_change). Source: intradaytrading_gainers_losers.sql. :contentReference[oaicite:26]{index=26}
  - circuit_hits (trade_date, symbol, new_val, previous_val, circuit_status). Source: intradaytrading_circuit_hits.sql. :contentReference[oaicite:27]{index=27}
  - trade_log for trades. Source: intradaytrading_trade_log.sql. :contentReference[oaicite:28]{index=28}

- ETF:
  - etf (etf_id, etf_symbol, etf_name). Source: etf_etf.sql. :contentReference[oaicite:29]{index=29}
  - etf_daily_transaction (etf_trade_date, etf_last_traded_price, etf_prevclose_price etc.). Source: etf_etf_daily_transaction.sql. :contentReference[oaicite:30]{index=30}
  - etf_returns, etf_aum, etf_expenseratio etc. for KPIs. :contentReference[oaicite:31]{index=31}:contentReference[oaicite:32]{index=32}:contentReference[oaicite:33]{index=33}
