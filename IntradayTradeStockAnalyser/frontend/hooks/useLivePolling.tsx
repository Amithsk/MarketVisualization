"use client";

import { useEffect, useRef, useState } from "react";
import { fetchNiftyCandles, fetchSymbolCandles } from "../services/liveApi";
import { Candle } from "../types/candle";

function nextFiveMinuteBoundaryDelay() {
    const now = new Date();
    const minutes = now.getMinutes();
    const next = Math.ceil((minutes + 1) / 5) * 5;
    const boundary = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours(), next, 5);
    return Math.max(1000, boundary.getTime() - now.getTime());
}

export default function useLivePolling(selectedSymbol: string | null) {

    const [nifty, setNifty] = useState<Candle[]>([]);
    const [stock, setStock] = useState<Candle[]>([]);
    const timerRef = useRef<number | null>(null);
    const mountedRef = useRef(true);

    useEffect(() => {
        mountedRef.current = true;

        async function loadOnce() {
            try {
                const nRes = await fetchNiftyCandles();
                if (mountedRef.current && nRes?.candles) {
                    setNifty(nRes.candles.map((c: any) => ({ ...c, time: c.time || c.Datetime })));
                }
            } catch (e) {
                console.error("Nifty load error", e);
            }

            if (selectedSymbol) {
                try {
                    const sRes = await fetchSymbolCandles(selectedSymbol);
                    if (mountedRef.current && sRes?.candles) {
                        setStock(sRes.candles.map((c: any) => ({ ...c, time: c.time || c.Datetime })));
                    }
                } catch (e) {
                    console.error("Symbol load error", e);
                }
            }
        }

        loadOnce();

        function scheduleNext() {
            const delay = nextFiveMinuteBoundaryDelay();
            timerRef.current = window.setTimeout(async () => {
                await loadOnce();
                scheduleNext();
            }, delay);
        }

        scheduleNext();

        return () => {
            mountedRef.current = false;
            if (timerRef.current) window.clearTimeout(timerRef.current);
        };
    }, [selectedSymbol]);

    return { nifty, stock };
}
