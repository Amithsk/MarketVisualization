//IntradayTradeNiftyAnalyser/frontend/hooks/useAnalytics.ts
"use client";

import { useEffect, useState } from "react";

import {
    getLearning,
    getPerformance,
    getStep1,
    getStep2,
} from "@/services/analyticsService";

import {
    LearningResponse,
    PerformanceResponse,
    Step1Response,
    Step2Response,
} from "@/types/analytics";


export function useAnalytics(
    tradeDate: string
) {
    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState<string | null>(null);

    const [learning, setLearning] =
        useState<LearningResponse | null>(null);

    const [step1, setStep1] =
        useState<Step1Response | null>(null);

    const [step2, setStep2] =
        useState<Step2Response | null>(null);

    const [performance, setPerformance] =
        useState<PerformanceResponse | null>(null);

    useEffect(() => {

        if (!tradeDate) {
            return;
        }

        async function loadData() {

            try {

                setLoading(true);

                const [
                    learningData,
                    step1Data,
                    step2Data,
                    performanceData,
                ] = await Promise.all([
                    getLearning(tradeDate),
                    getStep1(tradeDate),
                    getStep2(tradeDate),
                    getPerformance(tradeDate),
                ]);

                setLearning(
                    learningData
                );

                setStep1(
                    step1Data
                );

                setStep2(
                    step2Data
                );

                setPerformance(
                    performanceData
                );

                setError(null);

            } catch (err) {

                console.error(err);

                setError(
                    "Failed to load analytics data"
                );

            } finally {

                setLoading(false);

            }
        }

        loadData();

    }, [tradeDate]);

    return {

        loading,

        error,

        learning,

        step1,

        step2,

        performance,
    };
}