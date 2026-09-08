//IntradayTradeStockAnalyser/frontend/components/charts/SynchronizedCharts.tsx

"use client";

import type {
    ChangeEvent,
} from "react";

import {
    useEffect,
    useMemo,
    useRef,
    useState,
} from "react";

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

    mode?: "live" | "replay";
};

const LIVE_VIEWPORT_DURATION_MS = 2 * 60 * 60 * 1000;
const LIVE_NAVIGATION_STEP_MS = 60 * 60 * 1000;
const FIVE_MINUTE_STEP_MS = 5 * 60 * 1000;

type LiveViewportMode = "live" | "historical";

type TimeBounds = {
    first: number;
    latest: number;
};

function createTimestamp(dateTime: string): number {

    const match = dateTime
        .trim()
        .match(
            /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?/
        );

    if (!match) {
        return Number.NaN;
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

    return Date.UTC(
        Number(year),
        Number(month) - 1,
        Number(day),
        Number(hours),
        Number(minutes),
        Number(seconds)
    );
}

function formatTime(timestamp: number): string {

    const date = new Date(timestamp);

    return `${String(date.getUTCHours()).padStart(2, "0")}:${String(date.getUTCMinutes()).padStart(2, "0")}`;
}

function getTimeBounds(
    niftyCandles: Candle[],
    stockCandles: Candle[]
): TimeBounds | null {

    const timestamps = [
        ...niftyCandles,
        ...stockCandles,
    ]
        .map((candle) => createTimestamp(candle.time))
        .filter((timestamp) => Number.isFinite(timestamp));

    if (!timestamps.length) {
        return null;
    }

    return {
        first: Math.min(...timestamps),
        latest: Math.max(...timestamps),
    };
}

function clampVisibleEnd(
    requestedEnd: number,
    bounds: TimeBounds
): number {

    const sessionDuration =
        bounds.latest - bounds.first;

    if (sessionDuration <= LIVE_VIEWPORT_DURATION_MS) {
        return bounds.latest;
    }

    const earliestEnd =
        bounds.first + LIVE_VIEWPORT_DURATION_MS;

    return Math.min(
        Math.max(requestedEnd, earliestEnd),
        bounds.latest
    );
}

function getVisibleRange(
    bounds: TimeBounds,
    requestedEnd: number
) {

    const visibleEnd =
        clampVisibleEnd(requestedEnd, bounds);

    const visibleStart =
        bounds.latest - bounds.first <= LIVE_VIEWPORT_DURATION_MS
            ? bounds.first
            : visibleEnd - LIVE_VIEWPORT_DURATION_MS;

    return {
        start: visibleStart,
        end: visibleEnd,
    };
}

function filterCandlesByRange(
    candles: Candle[],
    start: number,
    end: number
) {

    return candles.filter((candle) => {
        const timestamp = createTimestamp(candle.time);

        return (
            Number.isFinite(timestamp) &&
            timestamp >= start &&
            timestamp <= end
        );
    });
}

export default function SynchronizedCharts({


    niftyCandles,

    stockCandles,

    marketEvents,

    stockName,

    currentCandleIndex,

    onCandleSelect,

    mode = "replay",

}: Props) {

    // -----------------------------------
    // Shared Crosshair Timestamp
    // -----------------------------------

    const synchronizedTimestampRef =
        useRef<number | null>(
            null
        );

    const [
        liveViewportMode,
        setLiveViewportMode,
    ] = useState<LiveViewportMode>("live");

    const [
        historicalVisibleEnd,
        setHistoricalVisibleEnd,
    ] = useState<number | null>(null);

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

    const replayVisibleNiftyCandles =
        currentCandleIndex !== undefined
            ? niftyCandles.slice(
                0,
                currentCandleIndex + 1
            )
            : niftyCandles;

    const replayVisibleStockCandles =
        currentCandleIndex !== undefined
            ? stockCandles.slice(
                0,
                currentCandleIndex + 1
            )
            : stockCandles;

    const liveTimeBounds =
        useMemo(
            () => getTimeBounds(
                replayVisibleNiftyCandles,
                replayVisibleStockCandles
            ),
            [
                replayVisibleNiftyCandles,
                replayVisibleStockCandles,
            ]
        );

    useEffect(() => {
        if (
            mode !== "live" ||
            liveViewportMode !== "historical" ||
            !liveTimeBounds ||
            historicalVisibleEnd === null
        ) {
            return;
        }

        const clampedEnd =
            clampVisibleEnd(
                historicalVisibleEnd,
                liveTimeBounds
            );

        if (clampedEnd !== historicalVisibleEnd) {
            setHistoricalVisibleEnd(clampedEnd);
        }
    }, [
        mode,
        liveViewportMode,
        liveTimeBounds,
        historicalVisibleEnd,
    ]);

    const liveVisibleEnd =
        liveTimeBounds
            ? liveViewportMode === "live"
                ? liveTimeBounds.latest
                : historicalVisibleEnd ?? liveTimeBounds.latest
            : null;

    const liveVisibleRange =
        mode === "live" &&
        liveTimeBounds &&
        liveVisibleEnd !== null
            ? getVisibleRange(
                liveTimeBounds,
                liveVisibleEnd
            )
            : null;

    const visibleNiftyCandles =
        liveVisibleRange
            ? filterCandlesByRange(
                replayVisibleNiftyCandles,
                liveVisibleRange.start,
                liveVisibleRange.end
            )
            : replayVisibleNiftyCandles;

    const visibleStockCandles =
        liveVisibleRange
            ? filterCandlesByRange(
                replayVisibleStockCandles,
                liveVisibleRange.start,
                liveVisibleRange.end
            )
            : replayVisibleStockCandles;

    const canNavigateLiveViewport =
        mode === "live" &&
        liveTimeBounds !== null &&
        liveTimeBounds.latest - liveTimeBounds.first >
        LIVE_VIEWPORT_DURATION_MS;

    const sliderMin =
        liveTimeBounds
            ? canNavigateLiveViewport
                ? liveTimeBounds.first + LIVE_VIEWPORT_DURATION_MS
                : liveTimeBounds.first
            : 0;

    const sliderMax =
        liveTimeBounds
            ? liveTimeBounds.latest
            : 0;

    const sliderValue =
        liveVisibleRange
            ? liveVisibleRange.end
            : sliderMax;

    const handlePreviousHour = () => {
        if (!liveTimeBounds || !liveVisibleRange) {
            return;
        }

        setLiveViewportMode("historical");
        setHistoricalVisibleEnd(
            clampVisibleEnd(
                liveVisibleRange.end - LIVE_NAVIGATION_STEP_MS,
                liveTimeBounds
            )
        );
    };

    const handleNextHour = () => {
        if (!liveTimeBounds || !liveVisibleRange) {
            return;
        }

        const nextEnd =
            clampVisibleEnd(
                liveVisibleRange.end + LIVE_NAVIGATION_STEP_MS,
                liveTimeBounds
            );

        setHistoricalVisibleEnd(nextEnd);

        if (nextEnd >= liveTimeBounds.latest) {
            setLiveViewportMode("live");
            return;
        }

        setLiveViewportMode("historical");
    };

    const handleReturnToLive = () => {
        setLiveViewportMode("live");
        setHistoricalVisibleEnd(null);
    };

    const handleSliderChange = (
        event: ChangeEvent<HTMLInputElement>
    ) => {
        if (!liveTimeBounds) {
            return;
        }

        const nextEnd =
            clampVisibleEnd(
                Number(event.target.value),
                liveTimeBounds
            );

        setHistoricalVisibleEnd(nextEnd);

        if (nextEnd >= liveTimeBounds.latest) {
            setLiveViewportMode("live");
            return;
        }

        setLiveViewportMode("historical");
    };

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

            {mode === "live" && liveVisibleRange && (
                <div
                    className="
                        flex
                        flex-wrap
                        items-center
                        gap-3
                        rounded-md
                        border
                        border-gray-800
                        bg-gray-900
                        px-4
                        py-3
                        text-xs
                        text-gray-300
                    "
                >
                    <button
                        type="button"
                        onClick={handlePreviousHour}
                        disabled={!canNavigateLiveViewport}
                        className="
                            rounded
                            border
                            border-gray-700
                            px-3
                            py-1.5
                            text-gray-200
                            disabled:cursor-not-allowed
                            disabled:opacity-40
                        "
                    >
                        Previous hour
                    </button>

                    <div
                        className="
                            min-w-36
                            text-center
                            font-medium
                            text-white
                        "
                    >
                        {formatTime(liveVisibleRange.start)}
                        {" - "}
                        {formatTime(liveVisibleRange.end)}
                    </div>

                    <input
                        type="range"
                        min={sliderMin}
                        max={sliderMax}
                        step={FIVE_MINUTE_STEP_MS}
                        value={sliderValue}
                        disabled={!canNavigateLiveViewport}
                        onChange={handleSliderChange}
                        className="
                            h-2
                            min-w-64
                            flex-1
                            accent-cyan-400
                            disabled:opacity-40
                        "
                    />

                    <button
                        type="button"
                        onClick={handleNextHour}
                        disabled={!canNavigateLiveViewport}
                        className="
                            rounded
                            border
                            border-gray-700
                            px-3
                            py-1.5
                            text-gray-200
                            disabled:cursor-not-allowed
                            disabled:opacity-40
                        "
                    >
                        Next hour
                    </button>

                    <button
                        type="button"
                        onClick={handleReturnToLive}
                        disabled={liveViewportMode === "live"}
                        className="
                            rounded
                            bg-cyan-500
                            px-3
                            py-1.5
                            font-semibold
                            text-gray-950
                            disabled:cursor-not-allowed
                            disabled:opacity-40
                        "
                    >
                        Return to Live
                    </button>
                </div>
            )}

            {/* -------------------------------- */}
            {/* NIFTY CHART */}
            {/* -------------------------------- */}

            <CandlestickChart

                candles={
                    visibleNiftyCandles
                }

                title="NIFTY 50"

                mode={mode}

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
                mode={mode}
                
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
