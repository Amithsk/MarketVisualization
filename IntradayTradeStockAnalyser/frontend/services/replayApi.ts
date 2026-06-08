//IntradayTradeStockAnalyser/frontend/services/replayApi.ts

import {
    ReplayData
} from "../types/replay";

const BASE_URL =
    "http://127.0.0.1:8003";

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

    console.log(
        "[Replay API] Fetch URL:",
        url
    );

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

    console.log(
        "[Replay API] Raw Response:",
        data
    );

    if (
        data.status !== "success"
    ) {

        throw new Error(
            "Replay API returned error status"
        );
    }

    console.log(
        "[Replay API] Replay Data Keys:",
        Object.keys(
            data.replay_data
        )
    );

    console.log(
        "[Replay API] Market Events Count:",
        data.replay_data
            .market_events?.length || 0
    );

    console.log(
        "[Replay API] First Market Event:",
        data.replay_data
            .market_events?.[0]
    );

    return data.replay_data;
}