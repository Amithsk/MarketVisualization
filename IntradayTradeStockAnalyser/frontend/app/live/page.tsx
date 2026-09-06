"use client";

import { useState } from "react";
import StockSelector from "../../components/selectors/StockSelector";
import SynchronizedCharts from "../../components/charts/SynchronizedCharts";
import useLivePolling from "../../hooks/useLivePolling";
import { Candle } from "../../types/candle";

const DEFAULT_STOCKS = [
    "NSE:SBIN",
    "NSE:RELIANCE",
    "NSE:HDFCBANK",
    "NSE:INFY",
    "NSE:CGPOWER",
];

export default function LivePage() {

    const [selectedStock, setSelectedStock] = useState<string>(DEFAULT_STOCKS[0]);

    const { nifty, stock } = useLivePolling(selectedStock);

    // Map incoming candles to the Candle type if needed
    const niftyCandles: Candle[] = nifty.map((c: any) => ({
        time: c.time || c.Datetime,
        open: Number(c.open || c.Open),
        high: Number(c.high || c.High),
        low: Number(c.low || c.Low),
        close: Number(c.close || c.Close),
        volume: Number(c.volume || c.Volume || 0),
    }));

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

            <div className="flex items-center gap-6 mb-6">
                <h2 className="text-xl font-semibold">Live Intraday Analysis</h2>

                <StockSelector
                    stocks={DEFAULT_STOCKS}
                    selectedStock={selectedStock}
                    onSelectStock={(s) => setSelectedStock(s)}
                />
            </div>

            <SynchronizedCharts
                niftyCandles={niftyCandles}
                stockCandles={stockCandles}
                marketEvents={[]}
                stockName={selectedStock}
            />

        </div>
    );
}
