//IntradayTradeNiftyAnalyser/frontend/components/analytics/TradeDateSelector.tsx
"use client";

interface Props {
    value: string;
    onChange: (value: string) => void;
}

export default function TradeDateSelector({
    value,
    onChange,
}: Props) {

    return (
        <section className="rounded-xl border border-slate-700 bg-slate-900 p-6">

            <h2 className="mb-4 text-xl font-bold text-white">
                Trade Date
            </h2>

            <input
                type="date"
                value={value}
                onChange={(e) =>
                    onChange(e.target.value)
                }
                className="rounded border border-slate-600 bg-slate-800 px-3 py-2 text-white"
            />

        </section>
    );
}