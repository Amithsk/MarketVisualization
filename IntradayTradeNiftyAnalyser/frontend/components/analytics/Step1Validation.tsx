//IntradayTradeNiftyAnalyser/frontend/components/analytics/Step1Validation.tsx
"use client";

import { Step1Response } from "@/types/analytics";

interface Props {
    data: Step1Response | null;
}

export default function Step1Validation({
    data,
}: Props) {

    if (!data) {
        return null;
    }

    const context = data.step1_context;
    const validation = data.market_validation;

    return (
        <section className="rounded-xl border border-slate-700 bg-slate-900 p-6">

            <h2 className="mb-6 text-xl font-bold text-white uppercase">
                STEP 1 Validation
            </h2>

            <div className="grid gap-4 md:grid-cols-4">

                {/* Raw Inputs */}

                <div className="rounded-lg border border-slate-700 bg-slate-800 p-4">

                    <h3 className="mb-3 font-semibold text-white">
                        Raw Inputs
                    </h3>

                    <div className="space-y-2 text-sm text-slate-300">

                        <div>
                            Gap %: {context?.gap_pct}
                        </div>

                        <div>
                            Gap Class: {context?.gap_class}
                        </div>

                        <div>
                            Prior Range: {context?.prior_range_size}
                        </div>

                        <div>
                            Overlap: {context?.prior_day_overlap}
                        </div>

                        <div>
                            Structure: {context?.prior_structure_state}
                        </div>

                    </div>

                </div>

                {/* System Decision */}

                <div className="rounded-lg border border-slate-700 bg-slate-800 p-4">

                    <h3 className="mb-3 font-semibold text-white">
                        System Decision
                    </h3>

                    <div className="text-lg font-bold text-green-400">

                        {context?.final_market_context}

                    </div>

                </div>

                {/* Market Reality */}

                <div className="rounded-lg border border-slate-700 bg-slate-800 p-4">

                    <h3 className="mb-3 font-semibold text-white">
                        Market Reality
                    </h3>

                    <div className="space-y-2 text-sm text-slate-300">

                        <div>
                            Trend Strength:
                            {" "}
                            {validation?.trend_strength}
                        </div>

                        <div>
                            Range:
                            {" "}
                            {validation?.total_range}
                        </div>

                        <div>
                            Net Move:
                            {" "}
                            {validation?.net_move}
                        </div>

                        <div>
                            VWAP Hold:
                            {" "}
                            {validation?.vwap_hold_percentage}
                        </div>

                    </div>

                </div>

                {/* Learning */}

                <div className="rounded-lg border border-slate-700 bg-slate-800 p-4">

                    <h3 className="mb-3 font-semibold text-white">
                        Learning
                    </h3>

                    <div className="text-sm text-slate-300 whitespace-pre-wrap">

                        {context?.final_reason}

                    </div>

                </div>

            </div>

        </section>
    );
}