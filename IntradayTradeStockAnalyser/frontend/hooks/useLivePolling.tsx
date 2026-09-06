/*intradayTradeStockAnalyser/frontend/hooks/useLivePolling.tsx*/


"use client";

import { useEffect, useRef, useState } from "react";

import {
    fetchNiftyCandles,
    fetchSymbolCandles,
} from "../services/liveApi";

import { Candle } from "../types/candle";


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

    const timerRef =
        useRef<number | null>(null);


    useEffect(() => {

        let cancelled = false;


        async function loadOnce() {

            // -----------------------------------
            // NIFTY
            // -----------------------------------

            try {

                const nRes =
                    await fetchNiftyCandles();

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
                }

            } catch (e) {

                if (!cancelled) {

                    console.error(
                        "Nifty load error",
                        e
                    );
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
                        !cancelled &&
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


        // -----------------------------------
        // INITIAL LOAD
        // -----------------------------------

        loadOnce();


        // -----------------------------------
        // NEXT 5-MINUTE POLL
        // -----------------------------------

        function scheduleNext() {

            const delay =
                nextFiveMinuteBoundaryDelay();

            timerRef.current =
                window.setTimeout(
                    async () => {

                        await loadOnce();

                        if (!cancelled) {
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
        };

    }, [selectedSymbol]);


    return {
        nifty,
        stock,
    };
}