//IntradayTradeStockAnalyser/frontend/components/replay/StrategyContextPanel.tsx

type Props = {

    strategyUsed: string | null;

    structureValid: boolean | null;

    reason: string | null;

    strategySummary: string | null;

    strategyExplanation?: {

        strategy_name?: string;

        explanation?: string;

        confidence_score?: number;

        tradable?: boolean;

        direction?: string;

    } | null;
};

export default function StrategyContextPanel({

    strategyUsed,

    structureValid,

    reason,

    strategySummary,

    strategyExplanation

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

            {/* ===================================== */}
            {/* HEADER */}
            {/* ===================================== */}

            <div
                className="
                    mb-3
                    flex
                    items-center
                    justify-between
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

            {/* ===================================== */}
            {/* STRATEGY SUMMARY */}
            {/* ===================================== */}

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

            {/* ===================================== */}
            {/* AI STRATEGY EXPLANATION */}
            {/* ===================================== */}

            {

                strategyExplanation && (

                    <div
                        className="
                            mb-3
                            rounded-md
                            border
                            border-blue-900
                            bg-blue-950/30
                            p-3
                        "
                    >

                        <div
                            className="
                                mb-2
                                text-xs
                                font-semibold
                                uppercase
                                tracking-wide
                                text-blue-400
                            "
                        >

                            AI STRATEGY ANALYSIS

                        </div>

                        <div
                            className="
                                mb-2
                                text-sm
                                leading-relaxed
                                text-gray-300
                            "
                        >

                            {

                                strategyExplanation
                                    .explanation ||

                                "No AI explanation available."
                            }

                        </div>

                        <div
                            className="
                                flex
                                flex-wrap
                                gap-2
                                text-xs
                            "
                        >

                            {

                                strategyExplanation
                                    .direction && (

                                    <div
                                        className="
                                            rounded
                                            bg-gray-800
                                            px-2
                                            py-1
                                            text-gray-300
                                        "
                                    >

                                        Direction:
                                        {" "}

                                        {

                                            strategyExplanation
                                                .direction
                                        }

                                    </div>
                                )
                            }

                            {

                                strategyExplanation
                                    .confidence_score !==
                                undefined && (

                                    <div
                                        className="
                                            rounded
                                            bg-gray-800
                                            px-2
                                            py-1
                                            text-gray-300
                                        "
                                    >

                                        Confidence:
                                        {" "}

                                        {

                                            strategyExplanation
                                                .confidence_score
                                        }

                                    </div>
                                )
                            }

                            {

                                strategyExplanation
                                    .tradable !==
                                undefined && (

                                    <div
                                        className={`
                                            rounded
                                            px-2
                                            py-1
                                            ${
                                                strategyExplanation
                                                    .tradable
                                                    ? "bg-green-900 text-green-300"
                                                    : "bg-red-900 text-red-300"
                                            }
                                        `}
                                    >

                                        {

                                            strategyExplanation
                                                .tradable
                                                ? "TRADABLE"
                                                : "NON TRADABLE"
                                        }

                                    </div>
                                )
                            }

                        </div>

                    </div>
                )
            }

            {/* ===================================== */}
            {/* STRATEGY NOTES */}
            {/* ===================================== */}

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

