//IntradayTradeNiftyAnalyser/frontend/components/analytics/LearningSection.tsx
"use client";

import { LearningResponse } from "@/types/analytics";

interface Props {
    data: LearningResponse | null;
}

export default function LearningSection({
    data,
}: Props) {

    if (!data) {
        return null;
    }

    return (
        <section className="rounded-xl border border-slate-700 bg-slate-900 p-6">

            <h2 className="mb-6 text-xl font-bold text-white uppercase">
                What Did I Learn Today?
            </h2>

            {/* Summary */}

            <div className="mb-6 rounded-lg border border-slate-700 bg-slate-800 p-4">

                <div className="mb-2 text-sm font-semibold text-slate-400 uppercase">
                    Daily Summary
                </div>

                <div className="text-sm text-slate-200 whitespace-pre-wrap">
                    {data.summary?.summary_text}
                </div>

            </div>

            {/* Suggestions */}

            <div className="grid gap-4 md:grid-cols-2">

                {data.suggestions.map((item) => (

                    <div
                        key={`${item.rule_name}-${item.priority}`}
                        className="rounded-lg border border-slate-700 bg-slate-800 p-4"
                    >

                        <div className="mb-2 flex items-center justify-between">

                            <div className="font-semibold text-white">
                                {item.rule_name}
                            </div>

                            <span
                                className={`rounded px-2 py-1 text-xs font-medium
                                ${
                                    item.priority === "HIGH"
                                        ? "bg-red-900 text-red-200"
                                        : "bg-yellow-900 text-yellow-200"
                                }`}
                            >
                                {item.priority}
                            </span>

                        </div>

                        <div className="space-y-1 text-sm text-slate-300">

                            <div>
                                Current Value:
                                {" "}
                                {item.current_value}
                            </div>

                            <div>
                                Suggested Value:
                                {" "}
                                {item.suggested_value}
                            </div>

                            <div>
                                Confidence:
                                {" "}
                                {item.confidence}
                            </div>

                            <div>
                                Impact:
                                {" "}
                                {item.impact}
                            </div>

                        </div>

                        <div className="mt-3 text-xs text-slate-400">
                            {item.support_metric}
                        </div>

                    </div>

                ))}

            </div>

        </section>
    );
}