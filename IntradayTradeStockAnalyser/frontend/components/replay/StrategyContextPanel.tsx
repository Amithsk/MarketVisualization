//IntradayTradeStockAnalyser/frontend/components/replay/StrategyContextPanel.tsx

type Props = {

    strategyUsed: string | null;

    structureValid: boolean | null;

    reason: string | null;

    strategySummary: string | null;
};

export default function StrategyContextPanel({
    strategyUsed,
    structureValid,
    reason,
    strategySummary
}: Props) {

    let badgeColor =
        "bg-gray-700";

    if (
        strategyUsed === "MOMENTUM"
    ) {

        badgeColor =
            "bg-green-700";
    }

    else if (
        strategyUsed === "GAP_FOLLOW"
    ) {

        badgeColor =
            "bg-blue-700";
    }

    else if (
        strategyUsed === "NO_TRADE"
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
                    justify-between
                    mb-3
                "
            >

                <div
                    className={`
                        rounded-md
                        px-3
                        py-1
                        text-sm
                        font-semibold
                        text-white
                        ${badgeColor}
                    `}
                >

                    {

                        strategyUsed
                            ?.replaceAll(
                                "_",
                                " "
                            ) ||

                        "UNKNOWN"
                    }

                </div>

                <div
                    className={`
                        rounded-md
                        px-2
                        py-1
                        text-xs
                        font-semibold
                        text-white
                        ${
                            structureValid
                                ? "bg-green-800"
                                : "bg-red-800"
                        }
                    `}
                >

                    {

                        structureValid
                            ? "STRUCTURE VALID"
                            : "STRUCTURE WEAK"
                    }

                </div>

            </div>

            <div
                className="
                    mb-3
                    text-sm
                    leading-relaxed
                    text-gray-300
                "
            >

                {

                    strategySummary ||

                    "Strategy explanation unavailable."
                }

            </div>

            <div
                className="
                    rounded-md
                    border
                    border-gray-800
                    bg-gray-950
                    p-3
                    text-xs
                    leading-relaxed
                    text-gray-400
                "
            >

                {

                    reason ||

                    "No additional strategy notes available."
                }

            </div>

        </div>
    );
}