import type { LiveTradePlan } from "../components/live/LiveTradePlanPanel";

const BASE_URL = "http://127.0.0.1:8003/api/v1/live-trade-plans";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
    const response = await fetch(url, {
        ...options,
        headers: { "Content-Type": "application/json", ...options?.headers },
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.detail || "Trade-plan request failed");
    return body as T;
}

export function fetchLiveTradePlans(symbol: string): Promise<{ plans: LiveTradePlan[] }> {
    return request(`${BASE_URL}?symbol=${encodeURIComponent(symbol)}`);
}

export function createLiveTradePlan(plan: Omit<LiveTradePlan, "id" | "status"> & { planDate: string }): Promise<{ plan: LiveTradePlan }> {
    return request(BASE_URL, { method: "POST", body: JSON.stringify(plan) });
}

export function updateLiveTradePlan(plan: LiveTradePlan & { planDate: string }): Promise<{ status: string }> {
    return request(`${BASE_URL}/${encodeURIComponent(plan.id)}`, { method: "PUT", body: JSON.stringify(plan) });
}

export function transitionLiveTradePlan(id: string, status: LiveTradePlan["status"], actionTime: string, cancellationReason?: string): Promise<{ status: string }> {
    return request(`${BASE_URL}/${encodeURIComponent(id)}/transition`, { method: "POST", body: JSON.stringify({ status, actionTime, cancellationReason }) });
}
