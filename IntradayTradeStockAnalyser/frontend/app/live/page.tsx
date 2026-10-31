/*IntradayTradeStockAnalyser/frontend/app/live/page.tsx*/
"use client";

import { useEffect, useState } from "react";

import StockSelector from "../../components/selectors/StockSelector";
import SynchronizedCharts from "../../components/charts/SynchronizedCharts";
import LiveTradePlanPanel from "../../components/live/LiveTradePlanPanel";
import type {
    LiveTradePlan,
} from "../../components/live/LiveTradePlanPanel";
import useLivePolling from "../../hooks/useLivePolling";
import { Candle } from "../../types/candle";
import { fetchLiveTradePlans } from "../../services/liveTradePlanApi";

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

    const { nifty, stock, niftyContext, stockContext } = useLivePolling(selectedStock);

    useEffect(() => {
        let cancelled = false;
        void fetchLiveTradePlans(selectedStock)
            .then(({ plans }) => { if (!cancelled) setTradePlans(plans); })
            .catch(() => { if (!cancelled) setTradePlans([]); });
        return () => { cancelled = true; };
    }, [selectedStock]);

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

    // A draft belongs to a particular selected candle.  Retaining just that
    // identifier lets the panel hydrate the matching local draft after reload.
    useEffect(() => {
        try {
            const time = window.localStorage.getItem(`intraday.live-selected-candle.v1:${selectedStock}`);
            const candle = stockCandles.find((item) => item.time === time);
            if (candle) setSelectedStockCandle((current) => current?.time === candle.time ? current : candle);
        } catch { /* selection restoration is optional */ }
    }, [selectedStock, stockCandles]);

    const selectStockCandle = (candle: Candle | null) => {
        setSelectedStockCandle(candle);
        try {
            const key = `intraday.live-selected-candle.v1:${selectedStock}`;
            if (candle) window.localStorage.setItem(key, candle.time);
            else window.localStorage.removeItem(key);
        } catch { /* storage is optional */ }
    };

    return (
        <div className="p-6">

            {/* -------------------------------- */}
            {/* LIVE HEADER */}
            {/* -------------------------------- */}

            <div className="mb-6">

                <div className="flex flex-wrap items-center gap-6">

                    <h2 className="text-xl font-semibold">
                        Live Intraday Analysis
                    </h2>

                    <div className="flex items-center gap-4 [&>div>label]:hidden">

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

                </div>

                <p className="mt-1 text-sm text-gray-500">
                    Monitor NIFTY and the selected stock using live market data.
                </p>

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
                niftyContext={niftyContext}
                stockContext={stockContext}
                tradePlans={tradePlans}
                onStockCandleSelect={
                    selectStockCandle
                }
            />

            <LiveTradePlanPanel
                selectedCandle={selectedStockCandle}
                stockName={selectedStock}
                stockCandles={stockCandles}
                niftyCandles={niftyCandles}
                plans={tradePlans}
                onPlansChange={setTradePlans}
            />

        </div>
    );
}
