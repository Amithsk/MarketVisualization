"use client";

import { useAnalytics } from "@/hooks/useAnalytics";

import LearningSection from "@/components/analytics/LearningSection";

export default function AnalyticsPage() {

    const {
        loading,
        error,
        learning,
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

        </div>
    );
}