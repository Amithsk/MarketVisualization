//IntradayTradeNiftyAnalyser/frontend/components/analytics/Step3Performance.tsx
"use client";

import { PerformanceResponse } from "@/types/analytics";

interface Props {
    data: PerformanceResponse | null;
}

export default function Step3Performance({
    data,
}: Props) {

    if (!data) {
        return null;
    }

    return (
        <section className="rounded-xl border border-slate-700 bg-slate-900 p-6">

            <h2 className="mb-6 text-xl font-bold text-white uppercase">
                STEP 3 Performance
            </h2>

            <div className="grid gap-4 md:grid-cols-3">

                {/* Execution */}

                <div className="rounded-lg border border-slate-700 bg-slate-800 p-4">

                    <h3 className="mb-3 font-semibold text-white">
                        Execution Control
                    </h3>

                    <div className="space-y-2 text-sm text-slate-300">

                        <div>
                            Market Context:
                            {" "}
                            {data.execution_control?.market_context}
                        </div>

                        <div>
                            Trade Permission:
                            {" "}
                            {data.execution_control?.trade_permission}
                        </div>

                        <div>
                            Max Trades:
                            {" "}
                            {data.execution_control?.max_trades_allowed}
                        </div>

                        <div>
                            Execution Allowed:
                            {" "}
                            {String(
                                data.execution_control
                                    ?.execution_allowed
                            )}
                        </div>

                    </div>

                </div>

                {/* Selection */}

                <div className="rounded-lg border border-slate-700 bg-slate-800 p-4">

                    <h3 className="mb-3 font-semibold text-white">
                        Stock Selection
                    </h3>

                    <div className="text-sm text-slate-300">

                        Total Stocks:
                        {" "}
                        {data.stock_selection?.length}

                    </div>

                    <div className="mt-3 space-y-1 text-xs text-slate-400">

                        {data.stock_selection?.map(
                            (stock) => (
                                <div key={stock.symbol}>
                                    {stock.symbol}
                                    {" - "}
                                    {stock.rejection_tag}
                                </div>
                            )
                        )}

                    </div>

                </div>

                {/* Metrics */}

                <div className="rounded-lg border border-slate-700 bg-slate-800 p-4">

                    <h3 className="mb-3 font-semibold text-white">
                        Performance Metrics
                    </h3>

                    <div className="space-y-2 text-sm text-slate-300">

                        <div>
                            Candidates:
                            {" "}
                            {data.performance_metrics
                                ?.candidate_count}
                        </div>

                        <div>
                            Selected:
                            {" "}
                            {data.performance_metrics
                                ?.selected_count}
                        </div>

                        <div>
                            Success:
                            {" "}
                            {data.performance_metrics
                                ?.total_success}
                        </div>

                        <div>
                            Missed:
                            {" "}
                            {data.performance_metrics
                                ?.total_missed_opportunities}
                        </div>

                    </div>

                </div>

            </div>

        </section>
    );
}