//IntradayTradeNiftyAnalyser/frontend/components/analytics/MissedOpportunities.tsx

"use client";

import { PerformanceResponse } from "@/types/analytics";

interface Props {
    data: PerformanceResponse | null;
}

export default function MissedOpportunities({
    data,
}: Props) {

    if (!data) {
        return null;
    }

    const missedStocks =
        data.stock_selection?.filter(
            (stock) =>
                stock.rejection_tag
        ) || [];

    return (
        <section className="rounded-xl border border-slate-700 bg-slate-900 p-6">

            <h2 className="mb-6 text-xl font-bold text-white uppercase">
                Missed Opportunities
            </h2>

            <div className="space-y-4">

                {missedStocks.length === 0 && (

                    <div className="rounded-lg border border-slate-700 bg-slate-800 p-4 text-slate-300">

                        No missed opportunities found.

                    </div>

                )}

                {missedStocks.map((stock) => (

                    <div
                        key={stock.symbol}
                        className="rounded-lg border border-slate-700 bg-slate-800 p-4"
                    >

                        <div className="mb-2 flex items-center justify-between">

                            <div className="font-semibold text-white">

                                {stock.symbol}

                            </div>

                            <span className="rounded bg-red-900 px-2 py-1 text-xs text-red-200">

                                {stock.rejection_tag}

                            </span>

                        </div>

                        <div className="text-sm text-slate-300">

                            {stock.reason}

                        </div>

                    </div>

                ))}

            </div>

        </section>
    );
}