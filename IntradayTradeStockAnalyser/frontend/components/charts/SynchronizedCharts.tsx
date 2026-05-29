//IntradayTradeStockAnalyser/frontend/components/charts/SynchronizedCharts.tsx
"use client";

import { useState } from "react";

import CandlestickChart from
    "./CandlestickChart";

import { Candle }
    from "../../types/candle";



type Props = {

    niftyCandles: Candle[];

    stockCandles: Candle[];

    stockName: string;
};

export default function SynchronizedCharts({

    niftyCandles,

    stockCandles,

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