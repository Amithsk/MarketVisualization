"use client";

import { useState } from "react";

import { useAnalytics } from "@/hooks/useAnalytics";

import LearningSection from "@/components/analytics/LearningSection";
import Step1Validation from "@/components/analytics/Step1Validation";
import Step2Validation from "@/components/analytics/Step2Validation";
import SystemVsMarketReality from "@/components/analytics/SystemVsMarketReality";
import Step3Performance from "@/components/analytics/Step3Performance";

import MissedOpportunities from "@/components/analytics/MissedOpportunities";
import RuleEffectiveness from "@/components/analytics/RuleEffectiveness";
import ImprovementTracker from "@/components/analytics/ImprovementTracker";
import TradeDateSelector from "@/components/analytics/TradeDateSelector";

export default function AnalyticsPage() {
    
    const [tradeDate, setTradeDate] =
    useState(
        new Date()
            .toISOString()
            .split("T")[0]
    );

    const {
        loading,
        error,
        learning,
        step1,
        step2,
        performance
    } = useAnalytics(
        tradeDate
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

            <TradeDateSelector
            value={tradeDate}
            onChange={setTradeDate}
            />

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
            <RuleEffectiveness
              data={learning}
            />

            <ImprovementTracker
            data={learning}
            />

        </div>
    );
}