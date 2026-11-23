import { SavedDate, StockIdentity, StockReview } from "@/types/stockReview";

const API_BASE = "/stock-review/api/analytics/stock-reviews";

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  let timeoutId: ReturnType<typeof setTimeout> | undefined;
  const timeout = new Promise<never>((_, reject) => {
    timeoutId = setTimeout(() => reject(new Error("Request timed out. Please retry.")), 10000);
  });

  try {
    const response = await Promise.race([fetch(path, { signal }), timeout]);
    if (!response.ok) throw new Error(`Request failed (${response.status})`);
    return response.json();
  } finally {
    if (timeoutId) clearTimeout(timeoutId);
  }
}

export const getReviewStocks = (signal?: AbortSignal) => request<StockIdentity[]>(`${API_BASE}/stocks?exchange=NSE`, signal);
export const getReviewDates = (exchange: string, symbol: string, signal?: AbortSignal) => request<SavedDate[]>(`${API_BASE}/${encodeURIComponent(exchange)}/${encodeURIComponent(symbol)}/dates`, signal);
export const getStockReview = (exchange: string, symbol: string, tradeDate: string, signal?: AbortSignal) => request<StockReview>(`${API_BASE}/${encodeURIComponent(exchange)}/${encodeURIComponent(symbol)}/${tradeDate}`, signal);
