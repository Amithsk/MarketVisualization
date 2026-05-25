//IntradayTradeStockAnalyser/frontend/hooks/useReplayData.ts
"use client";

import { useState } from "react";

import { ReplayData } from "../types/replay";

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

            console.log(
                "Fetching replay data..."
            );

            const response = await fetch(

                `http://127.0.0.1:8000/api/v1/replay?trade_date=${tradeDate}&stock=${stock}`

            );

            if (!response.ok) {

                throw new Error(
                    "Failed to fetch replay data"
                );
            }

            const result =
                await response.json();

            console.log(
                "Replay payload:",
                result
            );

            setReplayData(
                result.replay_data
            );

        } catch (err: any) {

            console.error(err);

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