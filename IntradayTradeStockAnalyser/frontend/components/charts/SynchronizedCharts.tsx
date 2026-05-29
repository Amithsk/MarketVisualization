//IntradayTradeStockAnalyser/frontend/components/charts/SynchronizedCharts.tsx

"use client";

import { useState } from "react";

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

    const [

        synchronizedTimestamp,

        setSynchronizedTimestamp

    ] = useState<number | null>(
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

        setSynchronizedTimestamp(
            timestamp
        );
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
                    synchronizedTimestamp
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
                    synchronizedTimestamp
                }

            />

        </div>
    );
}