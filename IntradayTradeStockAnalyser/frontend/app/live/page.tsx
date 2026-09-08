/*IntradayTradeStockAnalyser/frontend/app/live/page.tsx*/
"use client";

import { useState } from "react";

import StockSelector from "../../components/selectors/StockSelector";
import SynchronizedCharts from "../../components/charts/SynchronizedCharts";
import LiveTradePlanPanel from "../../components/live/LiveTradePlanPanel";
import type {
    LiveTradePlan,
} from "../../components/live/LiveTradePlanPanel";
import useLivePolling from "../../hooks/useLivePolling";
import { Candle } from "../../types/candle";

const DEFAULT_STOCKS = [
    "NSE:SBIN",
    "NSE:HDFCBANK",
    "NSE:ICICIBANK",
    "NSE:INFY",
    "NSE:RELIANCE",
    "NSE:BHARTIARTL"
];

export default function LivePage() {

    const [selectedStock, setSelectedStock] = useState<string>(
        DEFAULT_STOCKS[0]
    );

    const [selectedStockCandle, setSelectedStockCandle] =
        useState<Candle | null>(null);

    const [tradePlans, setTradePlans] =
        useState<LiveTradePlan[]>([]);

    const { nifty, stock } = useLivePolling(selectedStock);

    // -----------------------------------
    // NIFTY candles
    // -----------------------------------

    const niftyCandles: Candle[] = nifty.map((c: any) => ({
        time: c.time || c.Datetime,
        open: Number(c.open || c.Open),
        high: Number(c.high || c.High),
        low: Number(c.low || c.Low),
        close: Number(c.close || c.Close),
        volume: Number(c.volume || c.Volume || 0),
    }));

    // -----------------------------------
    // Stock candles
    // -----------------------------------

    const stockCandles: Candle[] = stock.map((c: any) => ({
        time: c.time || c.Datetime,
        open: Number(c.open || c.Open),
        high: Number(c.high || c.High),
        low: Number(c.low || c.Low),
        close: Number(c.close || c.Close),
        volume: Number(c.volume || c.Volume || 0),
    }));

    return (
        <div className="p-6">

            {/* -------------------------------- */}
            {/* LIVE HEADER */}
            {/* -------------------------------- */}

            <div className="mb-6">

                <h2 className="text-xl font-semibold">
                    Live Intraday Analysis
                </h2>

                <p className="mt-1 text-sm text-gray-500">
                    Monitor NIFTY and the selected stock using live market data.
                </p>

            </div>

            {/* -------------------------------- */}
            {/* STOCK SELECTION */}
            {/* -------------------------------- */}

            <div className="mb-6 flex items-center gap-4">

                <span className="text-sm font-medium">
                    Stock
                </span>

                <StockSelector
                    stocks={DEFAULT_STOCKS}
                    selectedStock={selectedStock}
                    onSelectStock={(s) => {
                        setSelectedStock(s);
                        setSelectedStockCandle(null);
                    }}
                />

            </div>

            {/* -------------------------------- */}
            {/* SYNCHRONIZED MARKET + STOCK */}
            {/* -------------------------------- */}

            <SynchronizedCharts
                niftyCandles={niftyCandles}
                stockCandles={stockCandles}
                marketEvents={[]}
                stockName={selectedStock}
                mode="live"
                tradePlans={tradePlans}
                onStockCandleSelect={
                    setSelectedStockCandle
                }
            />

            <LiveTradePlanPanel
                selectedCandle={selectedStockCandle}
                stockName={selectedStock}
                plans={tradePlans}
                onPlansChange={setTradePlans}
            />

        </div>
    );
}
