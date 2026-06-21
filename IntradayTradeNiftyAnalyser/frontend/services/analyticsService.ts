//IntradayTradeNiftyAnalyser/frontend/services/analyticsService.ts

import {
    LearningResponse,
    Step1Response,
    Step2Response,
    PerformanceResponse,
} from "@/types/analytics";


// =====================================================
// STEP 1
// =====================================================

export async function getStep1(
    tradeDate: string
): Promise<Step1Response> {

    const response = await fetch(
        `/api/analytics/step1/${tradeDate}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to load STEP1 data"
        );
    }

    return response.json();
}


// =====================================================
// STEP 2
// =====================================================

export async function getStep2(
    tradeDate: string
): Promise<Step2Response> {

    const response = await fetch(
        `/api/analytics/step2/${tradeDate}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to load STEP2 data"
        );
    }

    return response.json();
}


// =====================================================
// PERFORMANCE
// =====================================================

export async function getPerformance(
    tradeDate: string
): Promise<PerformanceResponse> {

    const response = await fetch(
        `/api/analytics/performance/${tradeDate}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to load performance data"
        );
    }

    return response.json();
}


// =====================================================
// LEARNING
// =====================================================

export async function getLearning(
    tradeDate: string
): Promise<LearningResponse> {

    const response = await fetch(
        `/api/analytics/learning/${tradeDate}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to load learning data"
        );
    }

    return response.json();
}
export {};