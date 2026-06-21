"use client";

import { useAnalytics } from "@/hooks/useAnalytics";

export default function AnalyticsPage() {

    const {
        loading,
        error,
        learning,
        step1,
        step2,
        performance,
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

            <h1>
                Analytics Test Page
            </h1>

            <h2>Learning</h2>
            <pre>
                {JSON.stringify(
                    learning,
                    null,
                    2
                )}
            </pre>

            <h2>STEP1</h2>
            <pre>
                {JSON.stringify(
                    step1,
                    null,
                    2
                )}
            </pre>

            <h2>STEP2</h2>
            <pre>
                {JSON.stringify(
                    step2,
                    null,
                    2
                )}
            </pre>

            <h2>Performance</h2>
            <pre>
                {JSON.stringify(
                    performance,
                    null,
                    2
                )}
            </pre>

        </div>
    );
}