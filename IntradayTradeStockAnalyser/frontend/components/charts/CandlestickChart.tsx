//IntradayTradeStockAnalyser/frontend/components/charts/CandlestickChart.tsx
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
    useRef,
    useState
} from "react";

import { Candle } from "../../types/candle";

type Props = {

    candles: Candle[];

    title: string;

    onCrosshairMove?: (
        timestamp: number | null
    ) => void;

    synchronizedTimestamp?: (
        number | null
    );
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

    title,

    onCrosshairMove,

    synchronizedTimestamp

}: Props) {

    const chartContainerRef =
        useRef<HTMLDivElement | null>(null);

    // -----------------------------------
    // Hover State
    // -----------------------------------

    const [hoverData, setHoverData] =
        useState<any>(null);

    // -----------------------------------
    // Synchronized Hover Effect
    // -----------------------------------

    useEffect(() => {

        if (
            synchronizedTimestamp === null
        ) {
            return;
        }

        const matchedCandle =
            candles.find(

                (candle) => {

                    const convertedTimestamp =
                        createISTTimestamp(
                            candle.time
                        );

                    return (

                        convertedTimestamp ===
                        synchronizedTimestamp
                    );
                }
            );

        if (!matchedCandle) {
            return;
        }

        setHoverData({

            time:
                matchedCandle.time,

            open:
                matchedCandle.open,

            high:
                matchedCandle.high,

            low:
                matchedCandle.low,

            close:
                matchedCandle.close,

            volume:
                matchedCandle.volume
        });

    }, [

        synchronizedTimestamp,

        candles
    ]);

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
        // Crosshair Hover
        // -----------------------------------

        chart.subscribeCrosshairMove(

            (param) => {

                // -----------------------------------
                // Invalid hover state
                // -----------------------------------

                if (
                    !param.point ||
                    !param.time
                ) {

                    if (onCrosshairMove) {

                        onCrosshairMove(null);
                    }

                    setHoverData(null);

                    return;
                }

                // -----------------------------------
                // Emit timestamp
                // -----------------------------------

                if (onCrosshairMove) {

                    onCrosshairMove(
                        Number(param.time)
                    );
                }

                // -----------------------------------
                // Get candle data
                // -----------------------------------

                const data =
                    param.seriesData.get(
                        candleSeries
                    );

                if (!data) {

                    setHoverData(null);

                    return;
                }

                const candleData: any =
                    data;

                // -----------------------------------
                // Match candle
                // -----------------------------------

                const matchedCandle =
                    candles.find(

                        (candle) =>

                            createISTTimestamp(
                                candle.time
                            ) === param.time
                    );

                // -----------------------------------
                // Update hover
                // -----------------------------------

                setHoverData({

                    time:
                        matchedCandle?.time ||

                        "",

                    open:
                        candleData.open,

                    high:
                        candleData.high,

                    low:
                        candleData.low,

                    close:
                        candleData.close,

                    volume:
                        matchedCandle?.volume || 0
                });
            }
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

    }, [

        candles,

        onCrosshairMove,

        synchronizedTimestamp
    ]);

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
            {/* Hover OHLC */}
            {/* -------------------------------- */}

            {

                hoverData && (

                    <div
                        className="
                            mb-2
                            text-xs
                            text-gray-300
                            flex
                            gap-4
                            flex-wrap
                        "
                    >

                        <div>

                            Time:

                            <span
                                className="
                                    ml-1
                                    text-white
                                "
                            >

                                {hoverData.time}

                            </span>

                        </div>

                        <div>

                            O:

                            <span
                                className="
                                    ml-1
                                    text-green-400
                                "
                            >

                                {hoverData.open}

                            </span>

                        </div>

                        <div>

                            H:

                            <span
                                className="
                                    ml-1
                                    text-green-400
                                "
                            >

                                {hoverData.high}

                            </span>

                        </div>

                        <div>

                            L:

                            <span
                                className="
                                    ml-1
                                    text-red-400
                                "
                            >

                                {hoverData.low}

                            </span>

                        </div>

                        <div>

                            C:

                            <span
                                className="
                                    ml-1
                                    text-white
                                "
                            >

                                {hoverData.close}

                            </span>

                        </div>

                        <div>

                            Vol:

                            <span
                                className="
                                    ml-1
                                    text-cyan-400
                                "
                            >

                                {hoverData.volume}

                            </span>

                        </div>

                    </div>
                )
            }

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