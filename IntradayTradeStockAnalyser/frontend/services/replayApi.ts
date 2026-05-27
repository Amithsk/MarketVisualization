//IntradayTradeStockAnalyser/frontend/services/replayApi.ts

import {
    ReplayData
} from "../types/replay";

const BASE_URL =
    "http://127.0.0.1:8000";

type ReplayApiResponse = {

    status: string;

    replay_data: ReplayData;
};

export async function fetchReplayData(
    tradeDate: string,
    stock: string
): Promise<ReplayData> {

    const url =
        `${BASE_URL}/api/v1/replay` +
        `?trade_date=${tradeDate}` +
        `&stock=${stock}`;

    const response = await fetch(
        url,
        {
            method: "GET",
            cache: "no-store"
        }
    );

    if (!response.ok) {

        throw new Error(
            "Failed to fetch replay data"
        );
    }

    const data:
        ReplayApiResponse =
        await response.json();

    if (
        data.status !== "success"
    ) {

        throw new Error(
            "Replay API returned error status"
        );
    }

    return data.replay_data;
}