"use client";

import { useAnalytics } from "@/hooks/useAnalytics";

import LearningSection from "@/components/analytics/LearningSection";
import Step1Validation from "@/components/analytics/Step1Validation";
import Step2Validation from "@/components/analytics/Step2Validation";
import SystemVsMarketReality from "@/components/analytics/SystemVsMarketReality";
import Step3Performance from "@/components/analytics/Step3Performance";

import MissedOpportunities from "@/components/analytics/MissedOpportunities";

export default function AnalyticsPage() {

    const {
        loading,
        error,
        learning,
        step1,
        step2,
        performance
    } = useAnalytics(
        "2026-06-11"
    );

    if (loading) {
        return (
            <div style={{ padding: "20px" }}>
                Loading...
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ padding: "20px" }}>
                Error: {error}
            </div>
        );
    }

    return (
        <div style={{ padding: "20px" }}>

            <LearningSection
                data={learning}
            />

            <Step1Validation
            data={step1}
            />

            <Step2Validation
            data={step2}
            />

            <SystemVsMarketReality
             step1={step1}
             step2={step2}
            />

            <Step3Performance
            data={performance}
            />
            <MissedOpportunities
           data={performance}
            />

        </div>
    );
}