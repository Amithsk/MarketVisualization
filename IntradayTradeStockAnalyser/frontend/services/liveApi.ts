export async function fetchNiftyCandles() {
    const res = await fetch('/api/v1/live/nifty-candles');
    const payload = await res.json();

    // A 503 before the first completed fetch still carries poller state.
    if (!res.ok && !payload?.refresh_status) {
        throw new Error(`Nifty fetch failed: ${res.status}`);
    }

    return payload;
}

export async function fetchSymbolCandles(symbol: string) {
    const normalizedSymbol = symbol.includes(":")
        ? symbol
        : `NSE:${symbol}`;

    const url =
        `/api/v1/live/symbol-candles?symbol=${encodeURIComponent(normalizedSymbol)}`;

    const res = await fetch(url);

    if (!res.ok) {
        throw new Error(`Symbol fetch failed: ${res.status}`);
    }

    return res.json();
}
