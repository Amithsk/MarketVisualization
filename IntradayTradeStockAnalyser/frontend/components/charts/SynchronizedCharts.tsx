//IntradayTradeStockAnalyser/frontend/components/charts/SynchronizedCharts.tsx

"use client";

import { useRef } from "react";

import CandlestickChart from
    "./CandlestickChart";

import { Candle }
    from "../../types/candle";

import {
    MarketEvent
}
    from "../../types/replay";


type Props = {

    niftyCandles: Candle[];

    stockCandles: Candle[];

    marketEvents: MarketEvent[];

    stockName: string;
};

export default function SynchronizedCharts({

    niftyCandles,

    stockCandles,

    marketEvents,

    stockName

}: Props) {

    // -----------------------------------
    // Shared Crosshair Timestamp
    // -----------------------------------
    const synchronizedTimestampRef =
        useRef<number | null>(
            null
        );
    console.log(
        "[SynchronizedCharts] Market Events:",
        marketEvents
    );

    console.log(
        "[SynchronizedCharts] Market Events Count:",
        marketEvents?.length || 0
    );

    // -----------------------------------
    // Crosshair Handler
    // -----------------------------------

    const handleCrosshairMove = (
        timestamp: number | null
    ) => {

        synchronizedTimestampRef.current = timestamp;
    };

    return (

        <div
            className="
                flex
                flex-col
                gap-6
                w-full
            "
        >

            {/* -------------------------------- */}
            {/* NIFTY CHART */}
            {/* -------------------------------- */}

            <CandlestickChart

                candles={
                    niftyCandles
                }

                title="NIFTY 50"

                onCrosshairMove={
                    handleCrosshairMove
                }

                synchronizedTimestamp={
                     synchronizedTimestampRef.current
                }

            />

            {/* -------------------------------- */}
            {/* STOCK CHART */}
            {/* -------------------------------- */}

            <CandlestickChart

                candles={
                    stockCandles
                }

                marketEvents={
                    marketEvents
                }

                title={
                    stockName
                }

                onCrosshairMove={
                    handleCrosshairMove
                }

                synchronizedTimestamp={
                    synchronizedTimestampRef.current
                }

            />

        </div>
    );
}