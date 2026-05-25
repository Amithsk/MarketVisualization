//IntradayTradeStockAnalyser/frontend/types/replay.ts
import { Candle } from "./candle";

export type ReplayTradeData = {

    strategy: string;

    position_type: string;

    trade_mode: string;

    setup_description: string;

    planned_entry_price: number;

    planned_stop_price: number;

    planned_target_price: number;

    plan_status: string;
};

export type ReplayData = {

    trade_data: ReplayTradeData;

    stock_candles: Candle[];

    nifty_candles: Candle[];
};