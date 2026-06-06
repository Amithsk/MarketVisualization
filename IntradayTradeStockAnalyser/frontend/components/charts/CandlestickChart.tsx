//IntradayTradeStockAnalyser/frontend/components/charts/CandlestickChart.tsx
"use client";

import {
    createChart,
    UTCTimestamp,
    ColorType,
    CandlestickSeries,
    createSeriesMarkers,
    HistogramSeries,
} from "lightweight-charts";
import { useEffect, useRef, useState } from "react";

import { Candle } from "../../types/candle";
import { MarketEvent } from "../../types/replay";

type Props = {
    candles: Candle[];
    marketEvents?: MarketEvent[];
    title: string;
    onCrosshairMove?: (timestamp: number | null) => void;
    synchronizedTimestamp?: number | null;
    currentCandleIndex?: number;
    onCandleSelect?: (index: number) => void;
};

// -----------------------------------
// IST SAFE TIMESTAMP
// -----------------------------------

function createISTTimestamp(dateTime: string): number {
    const [datePart, timePart] = dateTime.split(" ");
    const [year, month, day] = datePart.split("-").map(Number);
    const [hours, minutes, seconds] = timePart.split(":").map(Number);

    return Math.floor(
        Date.UTC(year, month - 1, day, hours, minutes, seconds) / 1000
    );
}

export default function CandlestickChart({
    candles,
    marketEvents = [],
    title,
    onCrosshairMove,
    synchronizedTimestamp,
    currentCandleIndex,
    onCandleSelect,
}: Props) {
    const chartContainerRef = useRef<HTMLDivElement | null>(null);

    // -----------------------------------
    // Hover State
    // -----------------------------------

    const [hoverData, setHoverData] = useState<any>(null);
    const [hoveredEvent, setHoveredEvent] = useState<MarketEvent | null>(null);
    const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });

    // -----------------------------------
    // Event Hover Debug
    // -----------------------------------

    useEffect(() => {
        console.log("[EVENT HOVER STATE]", hoveredEvent);
    }, [hoveredEvent]);

    // -----------------------------------
    // Synchronized Hover Effect
    // -----------------------------------

    useEffect(() => {
        if (synchronizedTimestamp === null) {
            return;
        }

        const matchedCandle = candles.find((candle) => {
            const convertedTimestamp = createISTTimestamp(candle.time);
            return convertedTimestamp === synchronizedTimestamp;
        });

        if (!matchedCandle) {
            return;
        }

        setHoverData({
            time: matchedCandle.time,
            open: matchedCandle.open,
            high: matchedCandle.high,
            low: matchedCandle.low,
            close: matchedCandle.close,
            volume: matchedCandle.volume,
        });
    }, [synchronizedTimestamp, candles]);

    useEffect(() => {
        if (!chartContainerRef.current) {
            return;
        }

        // -----------------------------------
        // Create chart
        // -----------------------------------

        const chart = createChart(chartContainerRef.current, {
            width: chartContainerRef.current.clientWidth,
            height: 400,
            layout: {
                background: { type: ColorType.Solid, color: "#111827" },
                textColor: "#D1D5DB",
            },
            grid: {
                vertLines: { color: "#1F2937" },
                horzLines: { color: "#1F2937" },
            },
            crosshair: { mode: 1 },
            rightPriceScale: { borderColor: "#374151" },
            timeScale: {
                borderColor: "#374151",
                timeVisible: true,
                secondsVisible: false,
            },
        });

        // -----------------------------------
        // Candlestick series
        // -----------------------------------

        const candleSeries = chart.addSeries(CandlestickSeries, {
            upColor: "#22C55E",
            downColor: "#EF4444",
            borderVisible: false,
            wickUpColor: "#22C55E",
            wickDownColor: "#EF4444",
        });

        // -----------------------------------
        // Volume series
        // -----------------------------------

        const volumeSeries = chart.addSeries(HistogramSeries, {
            priceFormat: { type: "volume" },
            priceScaleId: "",
            color: "#3B82F6",
        });
        volumeSeries.priceScale().applyOptions({

            scaleMargins: {

                top: 0.78,

                bottom: 0,
            },
        });

        // -----------------------------------
        // Format candle data
        // -----------------------------------

        const formattedCandles = candles.map((candle) => ({
            time: createISTTimestamp(
                candle.time
            ) as UTCTimestamp,

            open: candle.open,

            high: candle.high,

            low: candle.low,

            close: candle.close,
        }));

        // -----------------------------------
        // Format volume data
        // -----------------------------------

        const formattedVolume = candles.map((candle) => ({
            time: createISTTimestamp(candle.time) as UTCTimestamp,
            value: candle.volume,
            color: candle.close >= candle.open ? "#26a69a" : "#ef5350",
        }));

        // -----------------------------------
        // Set chart data
        // -----------------------------------

        candleSeries.setData(formattedCandles);
        volumeSeries.setData(formattedVolume);
        // -----------------------------------
        // Replay Auto Follow
        // -----------------------------------

        chart.timeScale().scrollToRealTime();
        // -----------------------------------
        // Create Event Markers
        // -----------------------------------

        if (
            marketEvents &&
            marketEvents.length > 0
        ) {
            // -----------------------------------
            // Group Events By Candle
            // -----------------------------------

            const eventsByCandle =
                new Map<
                    number,
                    MarketEvent[]
                >();

            marketEvents.forEach(
                (event) => {

                    if (
                        event.candle_index === undefined ||
                        event.candle_index === null
                    ) {
                        return;
                    }

                    const existingEvents =
                        eventsByCandle.get(
                            event.candle_index
                        ) || [];

                    existingEvents.push(
                        event
                    );

                    eventsByCandle.set(
                        event.candle_index,
                        existingEvents
                    );
                }
            );

            const markers =

                Array.from(
                    eventsByCandle.entries()
                )

                    .map(

                        ([

                            candleIndex,

                            candleEvents

                        ]) => {

                            const matchingCandle =
                                formattedCandles[
                                candleIndex
                                ];

                            if (
                                !matchingCandle
                            ) {

                                return null;
                            }

                            const eventCount =
                                candleEvents.length;

                            const isActiveReplayEvent =

                                currentCandleIndex !== undefined &&

                                candleIndex ===
                                currentCandleIndex;

                            return {

                                time:
                                    matchingCandle.time,

                                position:
                                    "aboveBar" as const,

                                color:

                                    isActiveReplayEvent

                                        ? "#00E5FF"

                                        : "#f59e0b",

                                shape:
                                    "square" as const,

                                text:

                                    eventCount > 1

                                        ? `★${eventCount}`

                                        : "★",
                            };
                        }
                    )

                    .filter(Boolean);

            console.log(
                "[FIRST CANDLE TIME]",
                formattedCandles[0]
            );


            console.log(
                "[FIRST MARKER TIME]",
                markers[0]
            );

            console.log(
                "[MARKERS APPLIED]",
                markers
            );
            const matchingCandleCheck =
                formattedCandles.find(
                    (
                        candle
                    ) =>
                        candle.time ===
                        markers[0]?.time
                );

            console.log(
                "[MATCHING CANDLE]",
                matchingCandleCheck
            );
            createSeriesMarkers(
                candleSeries,
                markers as any
            );
        }

        // -----------------------------------
        // Crosshair Hover (named handler for proper cleanup)
        // -----------------------------------

        const handleCrosshairMove = (param) => {
            if (!param || !param.time || !param.point) {
                setHoverData(null);
                setHoveredEvent(null);
                return;
            }

            const candleData = param.seriesData.get(candleSeries) as any;
            if (!candleData) {
                setHoverData(null);
                setHoveredEvent(null);
                return;
            }
            // -----------------------------------
            // Selected Candle Index
            // -----------------------------------

            const candleIndex = candles.findIndex((c) => {

                return (
                    createISTTimestamp(c.time) ===
                    Number(param.time)
                );
            });


            const matchedCandle = candles.find((c) => {

                return (
                    createISTTimestamp(c.time) ===
                    Number(param.time)
                );
            });

            setHoverData({
                ttime: matchedCandle?.time,
                open: candleData.open,
                high: candleData.high,
                low: candleData.low,
                close: candleData.close,
                volume: matchedCandle?.volume
            });

            if (onCrosshairMove) {
                onCrosshairMove(Number(param.time));
            }

            const mouseX = param.point.x;
            const mouseY = param.point.y;

            const matchedEvent = marketEvents.find((event) => {
                const eventTimestamp = createISTTimestamp(
                    `${event.trade_date} ${event.candle_time}`
                );

                const markerX = chart.timeScale().timeToCoordinate(eventTimestamp as any);
                if (markerX === null) {
                    return false;
                }

                const candle = candles.find((c) => {
                    const candleTimestamp = createISTTimestamp(c.time);
                    return candleTimestamp === eventTimestamp;
                });

                if (!candle) {
                    return false;
                }

                const markerY = candleSeries.priceToCoordinate(candle.high);
                if (markerY === null) {
                    return false;
                }

                const distanceX = Math.abs(mouseX - markerX);
                const distanceY = Math.abs(mouseY - markerY);

                return distanceX < 12 && distanceY < 12;
            });

            if (matchedEvent) {
                console.log("[EVENT DETECTED]", matchedEvent);
                setHoveredEvent(matchedEvent);
                setTooltipPosition({ x: param.point.x, y: param.point.y });
            } else {
                setHoveredEvent(null);
            }
        };

        chart.subscribeCrosshairMove(handleCrosshairMove);
        // -----------------------------------
        // Candle Click Selection
        // -----------------------------------

        const handleChartClick = (
            param: any
        ) => {

            if (
                !param.time ||
                !onCandleSelect
            ) {
                return;
            }

            const candleIndex =
                candles.findIndex(

                    (candle) =>

                        createISTTimestamp(
                            candle.time
                        ) ===
                        Number(param.time)
                );

            if (
                candleIndex !== -1
            ) {

                console.log(
                    "[CLICKED CANDLE]",
                    candleIndex
                );

                onCandleSelect(
                    candleIndex
                );
            }
        };

        chart.subscribeClick(
            handleChartClick
        );

        // -----------------------------------
        // Fit content
        // -----------------------------------

        chart.timeScale().fitContent();

        // -----------------------------------
        // Resize handling
        // -----------------------------------

        const handleResize = () => {
            if (!chartContainerRef.current) {
                return;
            }
            chart.applyOptions({ width: chartContainerRef.current.clientWidth });
        };

        window.addEventListener("resize", handleResize);

        // -----------------------------------
        // Cleanup
        // -----------------------------------

        return () => {

            window.removeEventListener(
                "resize",
                handleResize
            );

            chart.unsubscribeCrosshairMove(
                handleCrosshairMove
            );

            chart.unsubscribeClick(
                handleChartClick
            );

            chart.remove();
        };
    }, [candles, marketEvents, onCrosshairMove, synchronizedTimestamp]);

    return (
        <div className="relative w-full h-full">
            <div className="text-sm font-semibold mb-2 text-gray-300">{title}</div>
            {hoverData && (

                <div
                    className="
        w-full
        overflow-x-auto
    "
                >

                    {

                        hoverData && (

                            <div
                                className="
                    flex
                    min-w-max
                    items-center
                    gap-6
                    rounded-md
                    border
                    border-gray-800
                    bg-gray-900
                    px-4
                    py-2
                    text-xs
                    text-gray-300
                    mb-3
                "
                            >

                                <div
                                    className="
                        font-semibold
                        text-white
                    "
                                >

                                    {title}

                                </div>

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

                </div>

            )}

            <div ref={chartContainerRef} className="w-full" />

            {hoveredEvent && tooltipPosition && (
                <div
                    className="
                        absolute
                        z-50
                        pointer-events-none
                        bg-zinc-900
                        border
                        border-zinc-700
                        rounded-lg
                        shadow-2xl
                        px-4
                        py-3
                        text-white
                        text-xs
                        min-w-65
                    "
                    style={{
                        left: tooltipPosition.x + 15,
                        top: tooltipPosition.y - 20,
                    }}
                >
                    <div
                        className="
                            text-cyan-400
                            font-semibold
                            text-sm
                            mb-2
                        "
                    >
                        {hoveredEvent.event_type}
                    </div>

                    <div
                        className="
                            text-zinc-200
                            leading-relaxed
                            mb-2
                        "
                    >
                        {hoveredEvent.explanation}
                    </div>

                    <div
                        className="
                            text-amber-300
                            italic
                            mb-2
                        "
                    >
                        {hoveredEvent.trading_implication}
                    </div>

                    <div
                        className="
                            flex
                            justify-between
                            text-zinc-400
                            mt-2
                        "
                    >
                        <span>Strength</span>
                        <span>{hoveredEvent.strength_score}</span>
                    </div>

                    <div
                        className="
                            flex
                            justify-between
                            text-zinc-400
                            mt-1
                        "
                    >
                        <span>NIFTY</span>
                        <span>{hoveredEvent.nifty_context_data?.direction}</span>
                    </div>
                </div>
            )}
        </div>
    );
}