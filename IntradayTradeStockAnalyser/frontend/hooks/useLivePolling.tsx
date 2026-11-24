/*intradayTradeStockAnalyser/frontend/hooks/useLivePolling.tsx*/


"use client";

import { useEffect, useRef, useState } from "react";

import {
    fetchNiftyCandles,
    fetchSymbolCandles,
} from "../services/liveApi";
import {
    isIndianMarketOpen,
    millisecondsUntilIndianMarketOpen,
} from "../lib/marketHours";

import { Candle } from "../types/candle";

export type NiftyLiveStatus = {
    refresh_status: "refreshing" | "ready" | "failed" | "waiting_for_data";
    refresh_started_at: string | null;
    last_successful_fetch_time: string | null;
    latest_candle_timestamp: string | null;
    last_error: string | null;
};

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
                        refresh_status: current.last_successful_fetch_time
                            ? "failed"
                            : "waiting_for_data",
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
                                refresh_status: current.last_successful_fetch_time
                                    ? "failed"
                                    : "waiting_for_data",
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


    return {
        nifty,
        stock,
        niftyContext,
        stockContext,
        niftyStatus,
    };
}
