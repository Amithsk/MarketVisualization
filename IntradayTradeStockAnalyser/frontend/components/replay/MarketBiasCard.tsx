//IntradayTradeStockAnalyser/frontend/components/replay/MarketBiasCard.tsx

type Props = {

    marketContext: {

        final_market_context: string | null;

        final_reason: string | null;
    };
};

export default function MarketBiasCard({
    marketContext
}: Props) {

    const marketType =
        marketContext
            ?.final_market_context;

    const reason =
        marketContext
            ?.final_reason;

    let badgeColor =
        "bg-gray-700";

    if (
        marketType === "TREND_DAY"
    ) {

        badgeColor =
            "bg-green-700";
    }

    else if (
        marketType ===
        "RANGE_UNCERTAIN_DAY"
    ) {

        badgeColor =
            "bg-yellow-700";
    }

    else if (
        marketType ===
        "NO_TRADE_DAY"
    ) {

        badgeColor =
            "bg-red-700";
    }

    return (

        <div
            className="
                mb-6
                rounded-lg
                border
                border-gray-800
                bg-gray-900
                p-4
            "
        >

            <div
                className="
                    flex
                    items-center
                    gap-3
                    mb-3
                "
            >

                <div
                    className={`
                        px-3
                        py-1
                        rounded-md
                        text-sm
                        font-semibold
                        text-white
                        ${badgeColor}
                    `}
                >

                    {

                        marketType
                            ?.replaceAll(
                                "_",
                                " "
                            )
                    }

                </div>

            </div>

            <div
                className="
                    text-sm
                    text-gray-300
                    leading-relaxed
                "
            >

                {

                    reason ||

                    "No market context available."
                }

            </div>

        </div>
    );
}