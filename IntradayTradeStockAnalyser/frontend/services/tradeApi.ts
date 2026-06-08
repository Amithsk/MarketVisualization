//IntradayTradeStockAnalyser/frontend/services/tradeApi.ts
const BASE_URL =
    "http://127.0.0.1:8003/api/v1";


// -------------------------------------
// Fetch trade dates
// -------------------------------------

export async function fetchTradeDates():

    Promise<string[]> {

    const response = await fetch(

        `${BASE_URL}/trades/dates`

    );

    if (!response.ok) {

        throw new Error(
            "Failed to fetch trade dates"
        );
    }

    const result =
        await response.json();

    return result.trade_dates;
}


// -------------------------------------
// Fetch traded stocks
// -------------------------------------

export async function fetchTradeStocks(

    tradeDate: string

): Promise<string[]> {

    const response = await fetch(

        `${BASE_URL}/trades/stocks?trade_date=${tradeDate}`

    );

    if (!response.ok) {

        throw new Error(
            "Failed to fetch trade stocks"
        );
    }

    const result =
        await response.json();

    return result.stocks;
}