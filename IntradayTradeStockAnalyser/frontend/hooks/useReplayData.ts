//IntradayTradeStockAnalyser/frontend/hooks/useReplayData.ts

"use client";

import { useState } from "react";

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

        try {

            setLoading(true);

            setError(null);

            const replayPayload =
                await fetchReplayApiData(
                    tradeDate,
                    stock
                );

            setReplayData(
                replayPayload
            );

        } catch (err: any) {

            setError(

                err.message ||

                "Replay fetch failed"
            );

        } finally {

            setLoading(false);
        }
    };

    return {

        replayData,

        loading,

        error,

        fetchReplayData
    };
}