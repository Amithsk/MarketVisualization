//IntradayTradeStockAnalyser/frontend/hooks/useReplayData.ts

"use client";

import { useState, useRef } from "react";

import {
    ReplayData
} from "../types/replay";

import {
    fetchReplayData as fetchReplayApiData
} from "../services/replayApi";

type ReplayParams = {

    tradeDate: string;

    stock: string;
};

export function useReplayData() {
    const requestRef = useRef(0);

    const [replayData, setReplayData] =
        useState<ReplayData | null>(null);

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState<string | null>(null);

    // -----------------------------------
    // Fetch replay payload
    // -----------------------------------

    const fetchReplayData = async ({
        tradeDate,
        stock
    }: ReplayParams) => {

        const request = ++requestRef.current;
        try {

            setLoading(true);

            setError(null);

            const replayPayload =
                await fetchReplayApiData(
                    tradeDate,
                    stock
                );

            if (request !== requestRef.current) return null;
            setReplayData(
                replayPayload
            );

            return replayPayload;

        } catch (err: any) {

            if (request !== requestRef.current) return null;
            setError(

                err.message ||

                "Replay fetch failed"
            );
            throw err;

        } finally {

            if (request === requestRef.current) setLoading(false);
        }
    };

    return {

        replayData,

        loading,

        error,

        fetchReplayData,
        invalidate: () => { requestRef.current++; setReplayData(null); setError(null); setLoading(false); }
    };
}
