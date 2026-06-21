"use client";

import { Step2Response } from "@/types/analytics";

interface Props {
    data: Step2Response | null;
}

export default function Step2Validation({
    data,
}: Props) {

    if (!data) {
        return null;
    }

    const behavior = data.market_behavior;
    const openBehavior = data.market_open_behavior;
    const validation = data.market_validation;

    return (
        <section className="rounded-xl border border-slate-700 bg-slate-900 p-6">

            <h2 className="mb-6 text-xl font-bold text-white uppercase">
                STEP 2 Validation
            </h2>

            <div className="grid gap-4 md:grid-cols-4">

                {/* Raw Inputs */}

                <div className="rounded-lg border border-slate-700 bg-slate-800 p-4">

                    <h3 className="mb-3 font-semibold text-white">
                        Raw Inputs
                    </h3>

                    <div className="space-y-2 text-sm text-slate-300">

                        <div>
                            IR High: {openBehavior?.ir_high}
                        </div>

                        <div>
                            IR Low: {openBehavior?.ir_low}
                        </div>

                        <div>
                            IR Range: {openBehavior?.ir_range}
                        </div>

                        <div>
                            IR Ratio: {openBehavior?.ir_ratio}
                        </div>

                    </div>

                </div>

                {/* System Decision */}

                <div className="rounded-lg border border-slate-700 bg-slate-800 p-4">

                    <h3 className="mb-3 font-semibold text-white">
                        System Decision
                    </h3>

                    <div className="space-y-2 text-sm text-slate-300">

                        <div>
                            Trade Permission:
                            {" "}
                            {openBehavior?.trade_permission}
                        </div>

                        <div>
                            VWAP State:
                            {" "}
                            {openBehavior?.vwap_state}
                        </div>

                        <div>
                            Volatility:
                            {" "}
                            {openBehavior?.volatility_state}
                        </div>

                        <div>
                            Range Hold:
                            {" "}
                            {openBehavior?.range_hold_status}
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
                            Open Behavior:
                            {" "}
                            {behavior?.index_open_behavior}
                        </div>

                        <div>
                            Volatility:
                            {" "}
                            {behavior?.early_volatility}
                        </div>

                        <div>
                            Participation:
                            {" "}
                            {behavior?.market_participation}
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

                        {openBehavior?.reason}

                    </div>

                </div>

            </div>

        </section>
    );
}