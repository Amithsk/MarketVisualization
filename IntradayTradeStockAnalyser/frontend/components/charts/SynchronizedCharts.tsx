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

    currentCandleIndex?: number;

    onCandleSelect?: (
        index: number
    ) => void;
};

export default function SynchronizedCharts({

    niftyCandles,

    stockCandles,

    marketEvents,

    stockName,

    currentCandleIndex,

    onCandleSelect,

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
    // Replay Candle Slicing
    // -----------------------------------

    const visibleNiftyCandles =
        currentCandleIndex !== undefined
            ? niftyCandles.slice(
                0,
                currentCandleIndex + 1
            )
            : niftyCandles;

    const visibleStockCandles =
        currentCandleIndex !== undefined
            ? stockCandles.slice(
                0,
                currentCandleIndex + 1
            )
            : stockCandles;

    // -----------------------------------
    // Replay Event Filtering
    // -----------------------------------

    const visibleMarketEvents =
        currentCandleIndex !== undefined
            ? marketEvents.filter((event) => {

                if (
                    event.candle_index === undefined ||
                    event.candle_index === null
                ) {

                    return false;
                }

                return (
                    event.candle_index <=
                    currentCandleIndex
                );
            })
            : marketEvents;

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
                    visibleNiftyCandles
                }

                title="NIFTY 50"
                currentCandleIndex={
                    currentCandleIndex
                }

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
                    visibleStockCandles
                }

                marketEvents={
                    visibleMarketEvents
                }

                title={
                    stockName
                }

                currentCandleIndex={
                    currentCandleIndex
                }
                
                onCandleSelect={
                    onCandleSelect
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