//IntradayTradeNiftyAnalyser/frontend/components/analytics/RuleEffectiveness.tsx
"use client";

import { LearningResponse } from "@/types/analytics";

interface Props {
    data: LearningResponse | null;
}

export default function RuleEffectiveness({
    data,
}: Props) {

    if (!data) {
        return null;
    }

    return (
        <section className="rounded-xl border border-slate-700 bg-slate-900 p-6">

            <h2 className="mb-6 text-xl font-bold text-white uppercase">
                Rule Effectiveness
            </h2>

            <div className="grid gap-4 md:grid-cols-2">

                {data.suggestions.map((rule) => (

                    <div
                        key={rule.rule_name}
                        className="rounded-lg border border-slate-700 bg-slate-800 p-4"
                    >

                        <div className="mb-3 flex items-center justify-between">

                            <div className="font-semibold text-white">

                                {rule.rule_name}

                            </div>

                            <span
                                className={`rounded px-2 py-1 text-xs font-medium
                                ${
                                    rule.priority === "HIGH"
                                        ? "bg-red-900 text-red-200"
                                        : "bg-yellow-900 text-yellow-200"
                                }`}
                            >
                                {rule.priority}
                            </span>

                        </div>

                        <div className="space-y-2 text-sm text-slate-300">

                            <div>
                                Current:
                                {" "}
                                {rule.current_value}
                            </div>

                            <div>
                                Suggested:
                                {" "}
                                {rule.suggested_value}
                            </div>

                            <div>
                                Impact:
                                {" "}
                                {rule.impact}
                            </div>

                            <div>
                                Confidence:
                                {" "}
                                {rule.confidence}
                            </div>

                        </div>

                        <div className="mt-3 text-xs text-slate-400">

                            {rule.support_metric}

                        </div>

                    </div>

                ))}

            </div>

        </section>
    );
}