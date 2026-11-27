/*intradayTradeStockAnalyser/frontend/hooks/useLivePolling.tsx*/


"use client";

import { useEffect, useRef, useState } from "react";

import {
    fetchNiftyCandles,
    fetchSymbolCandles,
} from "../services/liveApi";
import {
    isIndianMarketOpen,
    MARKET_CLOSE_MINUTES,
    MARKET_OPEN_MINUTES,
    millisecondsUntilIndianMarketOpen,
} from "../lib/marketHours";

import { Candle } from "../types/candle";

export type NiftyLiveStatus = {
    refresh_status: "refreshing" | "ready" | "failed" | "waiting_for_data";
    refresh_started_at: string | null;
    last_successful_fetch_time: string | null;
    latest_candle_timestamp: string | null;
    last_error: string | null;
    display_status?: "ready" | "updating" | "delayed" | "fetch_failed" | "market_closed" | "waiting_for_first_candle";
    expected_candle_timestamp?: string | null;
    current_time?: string;
    candle_delay_minutes?: number | null;
};

// The existing stale-cache retry waits 20 seconds when the poller does not
// provide a next refresh time.  Use that same normal refresh window for UI
// freshness rather than changing the polling cadence.
export const NIFTY_FRESHNESS_GRACE_MS = 20_000;

const EMPTY_NIFTY_STATUS: NiftyLiveStatus = {
    refresh_status: "waiting_for_data",
    refresh_started_at: null,
    last_successful_fetch_time: null,
    latest_candle_timestamp: null,
    last_error: null,
};

function toNiftyStatus(response: any): NiftyLiveStatus {
    return {
        refresh_status: response?.refresh_status || "waiting_for_data",
        refresh_started_at: response?.refresh_started_at || null,
        last_successful_fetch_time: response?.last_successful_fetch_time || null,
        latest_candle_timestamp: response?.latest_candle_timestamp || null,
        last_error: response?.last_error || response?.message || null,
    };
}

function indianDateParts(date: Date) {
    const parts = new Intl.DateTimeFormat("en-US", {
        timeZone: "Asia/Kolkata", year: "numeric", month: "numeric",
        day: "numeric", hour: "numeric", minute: "numeric", second: "numeric",
        hourCycle: "h23",
    }).formatToParts(date);
    const value = (type: string) => Number(parts.find((part) => part.type === type)?.value);
    return { year: value("year"), month: value("month"), day: value("day"), hour: value("hour"), minute: value("minute"), second: value("second") };
}

function expectedCompletedCandle(now: Date): number | null {
    const ist = indianDateParts(now);
    const minutes = ist.hour * 60 + ist.minute;
    if (minutes < MARKET_OPEN_MINUTES + 5 || minutes > MARKET_CLOSE_MINUTES) return null;

    const expectedMinutes = Math.floor((minutes - 5) / 5) * 5;
    return Date.UTC(ist.year, ist.month - 1, ist.day, 0, expectedMinutes) - 5.5 * 60 * 60 * 1000;
}

export function getNiftyFreshnessStatus(status: NiftyLiveStatus, now = new Date()): NiftyLiveStatus {
    if (!isIndianMarketOpen(now)) {
        return { ...status, display_status: "market_closed", current_time: now.toISOString(), expected_candle_timestamp: null, candle_delay_minutes: null };
    }

    const expected = expectedCompletedCandle(now);
    if (expected === null) {
        return { ...status, display_status: "waiting_for_first_candle", current_time: now.toISOString(), expected_candle_timestamp: null, candle_delay_minutes: null };
    }

    const latest = status.latest_candle_timestamp ? new Date(status.latest_candle_timestamp).getTime() : Number.NaN;
    const current = latest === expected;
    const delay = Number.isFinite(latest) ? Math.max(0, Math.round((expected - latest) / 60_000)) : null;
    if (current) {
        return { ...status, display_status: "ready", current_time: now.toISOString(), expected_candle_timestamp: new Date(expected).toISOString(), candle_delay_minutes: 0 };
    }
    if (status.refresh_status === "failed") {
        return { ...status, display_status: "fetch_failed", current_time: now.toISOString(), expected_candle_timestamp: new Date(expected).toISOString(), candle_delay_minutes: delay };
    }
    const expectedAvailableAt = expected + 5 * 60_000;
    return {
        ...status,
        display_status: now.getTime() < expectedAvailableAt + NIFTY_FRESHNESS_GRACE_MS ? "updating" : "delayed",
        current_time: now.toISOString(),
        expected_candle_timestamp: new Date(expected).toISOString(),
        candle_delay_minutes: delay,
    };
}


function nextFiveMinuteBoundaryDelay() {

    const now = new Date();

    const minutes = now.getMinutes();

    const next =
        Math.ceil((minutes + 1) / 5) * 5;

    const boundary =
        new Date(
            now.getFullYear(),
            now.getMonth(),
            now.getDate(),
            now.getHours(),
            next,
            5
        );

    return Math.max(
        1000,
        boundary.getTime() - now.getTime()
    );
}


export default function useLivePolling(
    selectedSymbol: string | null
) {

    const [nifty, setNifty] =
        useState<Candle[]>([]);

    const [stock, setStock] =
        useState<Candle[]>([]);
    const [niftyContext, setNiftyContext] = useState<any>(null);
    const [stockContext, setStockContext] = useState<any>(null);
    const [niftyStatus, setNiftyStatus] =
        useState<NiftyLiveStatus>(EMPTY_NIFTY_STATUS);
    const [freshnessClock, setFreshnessClock] = useState(() => Date.now());
    const timerRef =
        useRef<number | null>(null);
    const niftyRetryTimerRef =
        useRef<number | null>(null);

    const requestIdRef =
        useRef(0);


    useEffect(() => {

        let cancelled = false;

        const requestId =
        ++requestIdRef.current;

        
        setStock([]);



        async function loadOnce() {

            // Guard every live API request, including an already-scheduled poll.
            if (!isIndianMarketOpen()) {
                return;
            }

            // -----------------------------------
            // NIFTY
            // -----------------------------------

            try {

                const nRes =
                    await fetchNiftyCandles();

                if (!cancelled) {
                    setNiftyStatus(toNiftyStatus(nRes));
                }

                if (
                    !cancelled &&
                    nRes?.candles
                ) {

                    setNifty(
                        nRes.candles.map(
                            (c: any) => ({
                                ...c,
                                time:
                                    c.time ||
                                    c.Datetime,
                            })
                        )
                    );
                    setNiftyContext(nRes.market_context || null);
                    scheduleNiftyRefreshRetry(nRes);
                }

            } catch (e) {

                if (!cancelled) {

                    console.error(
                        "Nifty load error",
                        e
                    );
                    setNiftyStatus((current) => ({
                        ...current,
                        refresh_status: "failed",
                        last_error: e instanceof Error
                            ? e.message
                            : "NIFTY request failed",
                    }));
                }
            }


            // -----------------------------------
            // SELECTED STOCK
            // -----------------------------------

            if (selectedSymbol) {

                try {

                    const sRes =
                        await fetchSymbolCandles(
                            selectedSymbol
                        );

                    if (
                        !cancelled && requestId === requestIdRef.current &&
                        sRes?.candles
                    ) {

                        setStock(
                            sRes.candles.map(
                                (c: any) => ({
                                    ...c,
                                    time:
                                        c.time ||
                                        c.Datetime,
                                })
                            )
                        );
                        setStockContext(sRes.market_context || null);
                    }

                } catch (e) {

                    if (!cancelled) {

                        console.error(
                            "Symbol load error",
                            e
                        );
                    }
                }
            }
        }

        function latestCompletedCandleStart() {

            const parts = new Intl.DateTimeFormat(
                "en-US",
                {
                    timeZone: "Asia/Kolkata",
                    year: "numeric",
                    month: "numeric",
                    day: "numeric",
                    hour: "numeric",
                    minute: "numeric",
                    hourCycle: "h23",
                }
            ).formatToParts(new Date());

            const part = (type: string) =>
                Number(parts.find((item) => item.type === type)?.value);
            const istNow = Date.UTC(
                part("year"),
                part("month") - 1,
                part("day"),
                part("hour"),
                part("minute")
            ) - 5.5 * 60 * 60 * 1000;

            return Math.floor(
                (istNow - 5 * 60 * 1000) / (5 * 60 * 1000)
            ) * 5 * 60 * 1000;
        }

        function scheduleNiftyRefreshRetry(response: any) {

            if (niftyRetryTimerRef.current !== null) {
                window.clearTimeout(niftyRetryTimerRef.current);
                niftyRetryTimerRef.current = null;
            }

            const latest = response?.latest_candle_timestamp ||
                response?.candles?.[response.candles.length - 1]?.time;
            const latestTimestamp = latest ? new Date(latest).getTime() : NaN;

            if (!Number.isFinite(latestTimestamp) ||
                latestTimestamp >= latestCompletedCandleStart()) {
                return;
            }

            const nextRefreshTimestamp = response?.next_refresh_time
                ? new Date(response.next_refresh_time).getTime()
                : NaN;
            const retryDelay = Number.isFinite(nextRefreshTimestamp)
                ? Math.max(1000, nextRefreshTimestamp - Date.now() + 20000)
                : 20000;

            niftyRetryTimerRef.current = window.setTimeout(
                async () => {
                    if (cancelled || !isIndianMarketOpen()) {
                        return;
                    }

                    try {
                        const refreshed = await fetchNiftyCandles();
                        if (!cancelled) {
                            setNiftyStatus(toNiftyStatus(refreshed));
                        }
                        if (!cancelled && refreshed?.candles) {
                            setNifty(refreshed.candles.map((c: any) => ({
                                ...c,
                                time: c.time || c.Datetime,
                            })));
                            setNiftyContext(refreshed.market_context || null);
                        }
                    } catch (e) {
                        if (!cancelled) {
                            console.error("Nifty refresh retry error", e);
                            setNiftyStatus((current) => ({
                                ...current,
                                refresh_status: "failed",
                                last_error: e instanceof Error
                                    ? e.message
                                    : "NIFTY request failed",
                            }));
                        }
                    }
                },
                retryDelay
            );
        }


        // -----------------------------------
        // INITIAL LOAD
        // -----------------------------------

        loadOnce();


        // -----------------------------------
        // NEXT 5-MINUTE POLL
        // -----------------------------------

        function scheduleNext() {

            // While closed, schedule one next-open wake-up rather than polling.
            if (!isIndianMarketOpen()) {
                timerRef.current = window.setTimeout(
                    async () => {
                        if (
                            !cancelled &&
                            requestId === requestIdRef.current
                        ) {
                            // loadOnce re-checks market hours before calling APIs.
                            await loadOnce();
                            scheduleNext();
                        }
                    },
                    millisecondsUntilIndianMarketOpen()
                );

                return;
            }

            const delay =
                nextFiveMinuteBoundaryDelay();

            timerRef.current =
                window.setTimeout(
                    async () => {

                        await loadOnce();

                        if (
                            !cancelled &&
                            requestId === requestIdRef.current
                        ) {
                            scheduleNext();
                        }

                    },
                    delay
                );
        }


        scheduleNext();


        // -----------------------------------
        // CLEANUP
        // -----------------------------------

        return () => {

            cancelled = true;

            if (
                timerRef.current !== null
            ) {

                window.clearTimeout(
                    timerRef.current
                );

                timerRef.current = null;
            }

            if (niftyRetryTimerRef.current !== null) {
                window.clearTimeout(niftyRetryTimerRef.current);
                niftyRetryTimerRef.current = null;
            }
        };

    }, [selectedSymbol]);

    // Freshness changes at a candle boundary even when the chart data has not
    // changed. This timer performs no network work.
    useEffect(() => {
        let timer: number | null = null;
        const reassess = () => {
            setFreshnessClock(Date.now());
            const now = new Date();
            const delay = 5 * 60_000 - (now.getTime() % (5 * 60_000));
            timer = window.setTimeout(reassess, Math.max(1000, delay));
        };
        const onVisibilityChange = () => {
            if (document.visibilityState === "visible") setFreshnessClock(Date.now());
        };
        reassess();
        document.addEventListener("visibilitychange", onVisibilityChange);
        return () => {
            if (timer !== null) window.clearTimeout(timer);
            document.removeEventListener("visibilitychange", onVisibilityChange);
        };
    }, []);


    return {
        nifty,
        stock,
        niftyContext,
        stockContext,
        niftyStatus: getNiftyFreshnessStatus(niftyStatus, new Date(freshnessClock)),
    };
}
