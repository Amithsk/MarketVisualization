//IntradayTradeNiftyAnalyser/frontend/components/analytics/SystemVsMarketReality.tsx
"use client";

import {
    Step1Response,
    Step2Response,
} from "@/types/analytics";

interface Props {
    step1: Step1Response | null;
    step2: Step2Response | null;
}

export default function SystemVsMarketReality({
    step1,
    step2,
}: Props) {

    if (!step1 || !step2) {
        return null;
    }

    return (
        <section className="rounded-xl border border-slate-700 bg-slate-900 p-6">

            <h2 className="mb-6 text-xl font-bold text-white uppercase">
                System vs Market Reality
            </h2>

            <div className="grid gap-4 md:grid-cols-3">

                {/* System Prediction */}

                <div className="rounded-lg border border-slate-700 bg-slate-800 p-4">

                    <h3 className="mb-3 font-semibold text-white">
                        System Prediction
                    </h3>

                    <div className="space-y-2 text-sm text-slate-300">

                        <div>
                            Market Context:
                            {" "}
                            {step1.step1_context
                                ?.final_market_context}
                        </div>

                        <div>
                            Trade Permission:
                            {" "}
                            {step2.market_open_behavior
                                ?.trade_permission}
                        </div>

                        <div>
                            VWAP State:
                            {" "}
                            {step2.market_open_behavior
                                ?.vwap_state}
                        </div>

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
                            {step1.market_validation
                                ?.trend_strength}
                        </div>

                        <div>
                            Net Move:
                            {" "}
                            {step1.market_validation
                                ?.net_move}
                        </div>

                        <div>
                            VWAP Hold:
                            {" "}
                            {step1.market_validation
                                ?.vwap_hold_percentage}
                        </div>

                    </div>

                </div>

                {/* Learning */}

                <div className="rounded-lg border border-slate-700 bg-slate-800 p-4">

                    <h3 className="mb-3 font-semibold text-white">
                        Learning
                    </h3>

                    <div className="space-y-2 text-sm text-slate-300">

                        <div>
                            STEP1 Context:
                            {" "}
                            {step1.step1_context
                                ?.final_market_context}
                        </div>

                        <div>
                            STEP2 Permission:
                            {" "}
                            {step2.market_open_behavior
                                ?.trade_permission}
                        </div>

                        <div>
                            Actual Net Move:
                            {" "}
                            {step1.market_validation
                                ?.net_move}
                        </div>

                    </div>

                </div>

            </div>

        </section>
    );
}