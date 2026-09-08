//IntradayTradeStockAnalyser/frontend/components/charts/CandlestickChart.tsx
"use client";

import {
    createChart,
    UTCTimestamp,
    ColorType,
    CandlestickSeries,
    createSeriesMarkers,
    HistogramSeries,
    Coordinate,
} from "lightweight-charts";
import { useEffect, useRef, useState } from "react";

import { Candle } from "../../types/candle";
import { MarketEvent } from "../../types/replay";
import type {
    LiveTradePlan,
} from "../live/LiveTradePlanPanel";

type Props = {
    candles: Candle[];
    marketEvents?: MarketEvent[];
    title: string;
    onCrosshairMove?: (timestamp: number | null) => void;
    synchronizedTimestamp?: number | null;
    currentCandleIndex?: number;
    onCandleSelect?: (index: number) => void;
    showTimeline?: boolean;
    tradePlans?: LiveTradePlan[];

    // -----------------------------------
    // Chart Mode
    // -----------------------------------

    mode?: "live" | "replay";
};

const EMPTY_MARKET_EVENTS: MarketEvent[] = [];

// -----------------------------------
// LIVE CANDLE METADATA HELPERS
// -----------------------------------

function formatVolume(volume: number): string {

    if (!Number.isFinite(volume)) {
        return "0";
    }

    if (volume >= 1_000_000) {
        return `${(volume / 1_000_000).toFixed(2)}M`;
    }

    if (volume >= 1_000) {
        return `${(volume / 1_000).toFixed(0)}K`;
    }

    return volume.toString();
}


function calculateVolumeChange(
    candles: Candle[],
    index: number
): number | null {

    if (index === 0) {
        return null;
    }

    const currentVolume =
        Number(candles[index]?.volume);

    const previousVolume =
        Number(candles[index - 1]?.volume);

    if (
        !Number.isFinite(currentVolume) ||
        !Number.isFinite(previousVolume) ||
        previousVolume === 0
    ) {
        return null;
    }

    return (
        ((currentVolume - previousVolume) /
            previousVolume) *
        100
    );
}

type LiveMetadataItem = {

    key: string;

    x: Coordinate;

    top: number;

    high: number;

    low: number;

    close: number;

    range: number;

    bodyCenterY: number;

    volume: number;

    volumeChange: number | null;

    timeLabel: string;

    highY: Coordinate;

    lowY: Coordinate;
};

type LifecycleSegmentItem = {
    key: string;
    left: number;
    width: number;
    color: string;
};

function LiveCandleMetadata({
    metadata,
    showStockCandleDetails,
}: {
    metadata: LiveMetadataItem[];
    showStockCandleDetails: boolean;
}) {
    if (!metadata.length) {
        return null;
    }

    return (
        <div
            className="
                pointer-events-none
                absolute
                inset-0
                z-10
            "
        >
            {metadata.map((item) => (
                <div
                    key={item.key}
                    className="
                        absolute
                        text-[11px]
                        leading-none
                        whitespace-nowrap
                        text-white
                        text-center
                    "
                    style={{
                        left: `${item.x}px`,
                        top: "0px",
                        height: "100%",
                        transform: "translateX(-50%)",
                    }}
                >
                    <div
                        className="absolute"
                        style={{
                            top: `${item.highY - 11 - Math.min(Math.max(Math.abs(item.lowY - item.highY) * 0.15, 4), 12)}px`,
                            left: "50%",
                            transform: "translateX(-50%)",
                        }}
                    >
                        {Number(item.high).toFixed(1)}
                    </div>

                    {showStockCandleDetails && (
                        <div
                            className="absolute"
                            style={{
                                top: `${item.bodyCenterY - 10}px`,
                                left: "50%",
                                transform: "translateX(-50%)",
                            }}
                        >
                            <div
                                className="
                                    min-w-10
                                    text-center
                                    font-medium
                                "
                            >
                                {item.range.toFixed(1)}
                            </div>

                            <div
                                className="
                                    mx-auto
                                    mt-1
                                    h-0.5
                                    w-5
                                    bg-white
                                "
                            />
                        </div>
                    )}

                    <div
                        className="absolute"
                        style={{
                            top: `${item.lowY + Math.min(Math.max(Math.abs(item.lowY - item.highY) * 0.15, 4), 12)}px`,
                            left: "50%",
                            transform: "translateX(-50%)",
                        }}
                    >
                        {Number(item.low).toFixed(1)}
                    </div>

                    <div
                        className="
                            absolute
                            font-medium
                        "
                        style={{
                            top: "calc(100% - 76px)",
                            left: "50%",
                            transform: "translateX(-50%)",
                        }}
                    >
                        {formatVolume(item.volume)}
                    </div>

                    {item.volumeChange !== null && (
                        <div
                            className={`
                                absolute
                                font-medium
                                ${item.volumeChange > 0
                                    ? "text-green-400"
                                    : item.volumeChange < 0
                                        ? "text-red-400"
                                        : "text-gray-300"}
                            `}
                            style={{
                                top: showStockCandleDetails
                                    ? "calc(100% - 58px)"
                                    : `calc(100% - ${76 - Math.min(Math.max(Math.abs(item.lowY - item.highY) * 0.15, 20), 26)}px)`,
                                left: "50%",
                                transform: "translateX(-50%)",
                            }}
                        >
                            {item.volumeChange > 0
                                ? `▲ ${Math.abs(item.volumeChange).toFixed(0)}%`
                                : item.volumeChange < 0
                                    ? `▼ ${Math.abs(item.volumeChange).toFixed(0)}%`
                                    : "— 0%"}
                        </div>
                    )}

                    {showStockCandleDetails && (
                        <div
                            className="
                                absolute
                                text-gray-300
                            "
                            style={{
                                top: "calc(100% - 38px)",
                                left: "50%",
                                transform: "translateX(-50%)",
                            }}
                        >
                            C {Number(item.close).toFixed(1)}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}
// -----------------------------------
// IST SAFE TIMESTAMP
// -----------------------------------

function createISTTimestamp(dateTime: string): number {

    const match = dateTime
        .trim()
        .match(
            /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?/
        );

    if (!match) {
        throw new Error(
            `Invalid candle timestamp format: ${dateTime}`
        );
    }

    const [
        ,
        year,
        month,
        day,
        hours,
        minutes,
        seconds = "0",
    ] = match;

    return Math.floor(
        Date.UTC(
            Number(year),
            Number(month) - 1,
            Number(day),
            Number(hours),
            Number(minutes),
            Number(seconds)
        ) / 1000
    );
}

export default function CandlestickChart({
    candles,
    marketEvents: providedMarketEvents,
    title,
    onCrosshairMove,
    synchronizedTimestamp,
    currentCandleIndex,
    onCandleSelect,
    showTimeline = true,
    tradePlans = [],
    mode = "replay",
}: Props) {
    const chartContainerRef = useRef<HTMLDivElement | null>(null);
    const marketEvents = providedMarketEvents ?? EMPTY_MARKET_EVENTS;
    const isStockChart = providedMarketEvents !== undefined;

    // -----------------------------------
    // Live Metadata Position State
    // -----------------------------------

    const [liveMetadata, setLiveMetadata] = useState<LiveMetadataItem[]>([]);
    const [lifecycleSegments, setLifecycleSegments] =
        useState<LifecycleSegmentItem[]>([]);

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
                visible: showTimeline,
                borderColor: "#374151",
                timeVisible: true,
                secondsVisible: false,
                rightOffset: mode === "live" ? 2 : 0,
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
        if (mode !== "live") {
            volumeSeries.setData(formattedVolume);
        }
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
                if (
                    typeof event.trade_date !== "string" ||
                    !event.trade_date.trim() ||
                    typeof event.candle_time !== "string" ||
                    !event.candle_time.trim()
                ) {
                    return false;
                }

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

        const updateLiveMetadata = () => {
            const nextLiveMetadata: LiveMetadataItem[] = candles
                .map((candle, index) => {
                    const timestamp = createISTTimestamp(candle.time) as UTCTimestamp;
                    const x = chart.timeScale().timeToCoordinate(timestamp);
                    const highY = candleSeries.priceToCoordinate(Number(candle.high));
                    const lowY = candleSeries.priceToCoordinate(Number(candle.low));
                    const openY = candleSeries.priceToCoordinate(Number(candle.open));
                    const closeY = candleSeries.priceToCoordinate(Number(candle.close));

                    if (
                        x === null ||
                        highY === null ||
                        lowY === null ||
                        openY === null ||
                        closeY === null
                    ) {
                        return null;
                    }

                    const range = Number(candle.high) - Number(candle.low);
                    const volumeChange = calculateVolumeChange(candles, index);
                    const bodyCenterY = (openY + closeY) / 2;

                    return {
                        key: `${candle.time}-${index}`,
                        x,
                        top: highY - 18,
                        high: Number(candle.high),
                        low: Number(candle.low),
                        close: Number(candle.close),
                        range,
                        bodyCenterY,
                        volume: Number(candle.volume),
                        volumeChange,
                        timeLabel: candle.time.slice(11, 16),
                        highY,
                        lowY,
                    };
                })
                .filter((item): item is LiveMetadataItem => item !== null);

            setLiveMetadata(nextLiveMetadata);
        };

        const updateLifecycleSegments = () => {
            if (
                mode !== "live" ||
                !isStockChart ||
                !candles.length ||
                !tradePlans.length
            ) {
                setLifecycleSegments([]);
                return;
            }

            const visibleStart =
                createISTTimestamp(candles[0].time);
            const visibleEnd =
                createISTTimestamp(candles[candles.length - 1].time);

            const createSegment = (
                key: string,
                startTime: string,
                endTime: string,
                color: string
            ): LifecycleSegmentItem | null => {
                let startTimestamp: number;
                let endTimestamp: number;

                try {
                    startTimestamp = createISTTimestamp(startTime);
                    endTimestamp = createISTTimestamp(endTime);
                } catch {
                    return null;
                }

                if (
                    endTimestamp < visibleStart ||
                    startTimestamp > visibleEnd
                ) {
                    return null;
                }

                const clippedStart =
                    Math.max(startTimestamp, visibleStart);
                const clippedEnd =
                    Math.min(endTimestamp, visibleEnd);

                const startX =
                    chart
                        .timeScale()
                        .timeToCoordinate(clippedStart as UTCTimestamp);
                const endX =
                    chart
                        .timeScale()
                        .timeToCoordinate(clippedEnd as UTCTimestamp);

                if (startX === null || endX === null) {
                    return null;
                }

                const left =
                    Math.min(startX, endX);
                const width =
                    Math.max(Math.abs(endX - startX), 3);

                return {
                    key,
                    left,
                    width,
                    color,
                };
            };

            const nextLifecycleSegments =
                tradePlans
                    .flatMap((plan) => {
                        const currentCandleTime =
                            candles[candles.length - 1].time;

                        if (plan.status === "ACTIVE") {
                            return [
                                createSegment(
                                    `${plan.id}-active`,
                                    plan.decisionTime,
                                    currentCandleTime,
                                    "#FACC15"
                                ),
                            ];
                        }

                        if (plan.status === "CANCELLED") {
                            if (!plan.cancelledAt) {
                                return [];
                            }

                            return [
                                createSegment(
                                    `${plan.id}-cancelled`,
                                    plan.decisionTime,
                                    plan.cancelledAt,
                                    "#EF4444"
                                ),
                            ];
                        }

                        if (plan.status === "EXECUTED") {
                            if (!plan.executedAt) {
                                return [];
                            }

                            return [
                                createSegment(
                                    `${plan.id}-planned`,
                                    plan.decisionTime,
                                    plan.executedAt,
                                    "#FACC15"
                                ),
                                createSegment(
                                    `${plan.id}-executed`,
                                    plan.executedAt,
                                    currentCandleTime,
                                    "#3B82F6"
                                ),
                            ];
                        }

                        if (plan.status === "EXITED") {
                            if (
                                !plan.executedAt ||
                                !plan.exitedAt
                            ) {
                                return [];
                            }

                            return [
                                createSegment(
                                    `${plan.id}-planned`,
                                    plan.decisionTime,
                                    plan.executedAt,
                                    "#FACC15"
                                ),
                                createSegment(
                                    `${plan.id}-exited`,
                                    plan.executedAt,
                                    plan.exitedAt,
                                    "#3B82F6"
                                ),
                            ];
                        }

                        return [];
                    })
                    .filter(
                        (segment): segment is LifecycleSegmentItem =>
                            segment !== null
                    );

            setLifecycleSegments(nextLifecycleSegments);
        };

        const updateLiveOverlays = () => {
            updateLiveMetadata();
            updateLifecycleSegments();
        };

        let metadataAnimationFrame =
            requestAnimationFrame(updateLiveOverlays);

        // -----------------------------------
        // Resize handling
        // -----------------------------------

        const handleResize = () => {
            if (!chartContainerRef.current) {
                return;
            }
            chart.applyOptions({ width: chartContainerRef.current.clientWidth });
            cancelAnimationFrame(metadataAnimationFrame);
            metadataAnimationFrame = requestAnimationFrame(updateLiveOverlays);
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

            cancelAnimationFrame(metadataAnimationFrame);

            chart.remove();
        };
    }, [candles, marketEvents, mode, onCrosshairMove, synchronizedTimestamp, tradePlans]);

    return (
        <div className="relative w-full h-full">
            <div className="text-sm font-semibold mb-2 text-gray-300">{title}</div>
            {hoverData && (
                <div className="w-full overflow-x-auto">
                    <div
                        className="
                            mb-3
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
                        "
                    >
                        <div className="font-semibold text-white">{title}</div>

                        <div>
                            O:
                            <span className="ml-1 text-green-400">{hoverData.open}</span>
                        </div>

                        <div>
                            H:
                            <span className="ml-1 text-green-400">{hoverData.high}</span>
                        </div>

                        <div>
                            L:
                            <span className="ml-1 text-red-400">{hoverData.low}</span>
                        </div>

                        <div>
                            C:
                            <span className="ml-1 text-white">{hoverData.close}</span>
                        </div>

                        <div>
                            Vol:
                            <span className="ml-1 text-cyan-400">{hoverData.volume}</span>
                        </div>
                    </div>
                </div>
            )}

            <div className="relative">
                <div ref={chartContainerRef} className="relative" />

                {mode === "live" && (
                    <LiveCandleMetadata
                        metadata={liveMetadata}
                        showStockCandleDetails={isStockChart}
                    />
                )}

                {mode === "live" && isStockChart && lifecycleSegments.length > 0 && (
                    <div
                        className="
                            pointer-events-none
                            absolute
                            inset-0
                            z-20
                        "
                    >
                        {lifecycleSegments.map((segment) => (
                            <div
                                key={segment.key}
                                className="
                                    absolute
                                    h-1
                                    rounded-full
                                "
                                style={{
                                    left: `${segment.left}px`,
                                    width: `${segment.width}px`,
                                    bottom: "22px",
                                    backgroundColor: segment.color,
                                    opacity: 0.9,
                                }}
                            />
                        ))}
                    </div>
                )}
            </div>

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
                            mb-2
                            text-sm
                            font-semibold
                            text-cyan-400
                        "
                    >
                        {hoveredEvent.event_type}
                    </div>

                    <div
                        className="
                            mb-2
                            leading-relaxed
                            text-zinc-200
                        "
                    >
                        {hoveredEvent.explanation}
                    </div>

                    <div
                        className="
                            mb-2
                            italic
                            text-amber-300
                        "
                    >
                        {hoveredEvent.trading_implication}
                    </div>

                    <div
                        className="
                            mt-2
                            flex
                            justify-between
                            text-zinc-400
                        "
                    >
                        <span>Strength</span>
                        <span>{hoveredEvent.strength_score}</span>
                    </div>

                    <div
                        className="
                            mt-1
                            flex
                            justify-between
                            text-zinc-400
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
