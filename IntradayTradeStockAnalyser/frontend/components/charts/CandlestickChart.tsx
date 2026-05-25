//IntradayTradeStockAnalyser/frontend/components/charts/CandlestickChart.tsx
"use client";

import {
    createChart,
    UTCTimestamp,
    ColorType,
    CandlestickSeries,
    HistogramSeries
} from "lightweight-charts";

import {
    useEffect,
    useRef
} from "react";

import { Candle } from "../../types/candle";

type Props = {
    candles: Candle[];
    title: string;
};

// -----------------------------------
// IST SAFE TIMESTAMP
// -----------------------------------

function createISTTimestamp(
    dateTime: string
): number {

    const [
        datePart,
        timePart
    ] = dateTime.split(" ");

    const [
        year,
        month,
        day
    ] = datePart
        .split("-")
        .map(Number);

    const [
        hours,
        minutes,
        seconds
    ] = timePart
        .split(":")
        .map(Number);

    return Math.floor(

        Date.UTC(
            year,
            month - 1,
            day,
            hours,
            minutes,
            seconds
        ) / 1000
    );
}

export default function CandlestickChart({
    candles,
    title
}: Props) {

    const chartContainerRef =
        useRef<HTMLDivElement | null>(null);

    useEffect(() => {

        if (!chartContainerRef.current) {
            return;
        }

        // -----------------------------------
        // Create chart
        // -----------------------------------

        const chart = createChart(
            chartContainerRef.current,
            {
                width:
                    chartContainerRef.current
                        .clientWidth,

                height: 400,

                layout: {
                    background: {
                        type: ColorType.Solid,
                        color: "#111827",
                    },

                    textColor: "#D1D5DB",
                },

                grid: {
                    vertLines: {
                        color: "#1F2937",
                    },

                    horzLines: {
                        color: "#1F2937",
                    },
                },

                crosshair: {
                    mode: 1,
                },

                rightPriceScale: {
                    borderColor: "#374151",
                },

                timeScale: {

                    borderColor: "#374151",

                    timeVisible: true,

                    secondsVisible: false,
                },
            }
        );

        // -----------------------------------
        // Candlestick series
        // -----------------------------------

        const candleSeries =
            chart.addSeries(
                CandlestickSeries,
                {
                    upColor: "#22C55E",

                    downColor: "#EF4444",

                    borderVisible: false,

                    wickUpColor: "#22C55E",

                    wickDownColor: "#EF4444",
                }
            );

        // -----------------------------------
        // Volume series
        // -----------------------------------

        const volumeSeries =
            chart.addSeries(
                HistogramSeries,
                {
                    priceFormat: {
                        type: "volume",
                    },

                    priceScaleId: "",

                    color: "#3B82F6",
                }
            );

        // -----------------------------------
        // Format candle data
        // -----------------------------------

        const formattedCandles = candles.map(

            (candle) => ({

                time:
                    createISTTimestamp(
                        candle.time
                    ) as UTCTimestamp,

                open: candle.open,

                high: candle.high,

                low: candle.low,

                close: candle.close,
            })
        );

        // -----------------------------------
        // Format volume data
        // -----------------------------------

        const formattedVolume = candles.map(

            (candle) => ({

                time:
                    createISTTimestamp(
                        candle.time
                    ) as UTCTimestamp,

                value: candle.volume,

                color:
                    candle.close >= candle.open

                        ? "#26a69a"

                        : "#ef5350",
            })
        );

        // -----------------------------------
        // Set chart data
        // -----------------------------------

        candleSeries.setData(
            formattedCandles
        );

        volumeSeries.setData(
            formattedVolume
        );

        // -----------------------------------
        // Fit content
        // -----------------------------------

        chart.timeScale().fitContent();

        // -----------------------------------
        // Resize handling
        // -----------------------------------

        const handleResize = () => {

            if (
                !chartContainerRef.current
            ) {
                return;
            }

            chart.applyOptions({
                width:
                    chartContainerRef.current
                        .clientWidth,
            });
        };

        window.addEventListener(
            "resize",
            handleResize
        );

        // -----------------------------------
        // Cleanup
        // -----------------------------------

        return () => {

            window.removeEventListener(
                "resize",
                handleResize
            );

            chart.remove();
        };

    }, [candles]);

    return (

        <div
            className="
                w-full
            "
        >

            {/* -------------------------------- */}
            {/* Title */}
            {/* -------------------------------- */}

            <div
                className="
                    text-sm
                    font-semibold
                    mb-2
                    text-gray-300
                "
            >

                {title}

            </div>

            {/* -------------------------------- */}
            {/* Chart */}
            {/* -------------------------------- */}

            <div
                ref={chartContainerRef}
                className="
                    w-full
                "
            />

        </div>
    );
}