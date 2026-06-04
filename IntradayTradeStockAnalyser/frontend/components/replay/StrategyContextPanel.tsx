//IntradayTradeStockAnalyser/frontend/components/replay/StrategyContextPanel.tsx

type Props = {

    strategyUsed: string | null;

    structureValid: boolean | null;

    reason: string | null;

    strategySummary: string | null;

    strategyExplanation?: {

        strategy_name?: string;
        strategy_bias?: string;
        selection_reasons?: string[];
        market_alignment?: string;
        execution_expectation?: string;
        risk_notes?: string[];
        confidence_score?: number;

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

    console.log(
        "[StrategyContextPanel] strategyExplanation:",
        strategyExplanation
    );

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
                        ${structureValid
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
                        {

                            strategyExplanation
                                .strategy_name && (

                                <div
                                    className="
                                        mb-3
                                    "
                                >

                                    <div
                                        className="
                                            mb-1
                                            text-xs
                                            font-semibold
                                            uppercase
                                            tracking-wide
                                            text-blue-300
                                        "
                                    >

                                        Strategy Name

                                    </div>

                                    <div
                                        className="
                                            text-sm
                                            font-medium
                                            text-white
                                        "
                                    >

                                        {

                                            strategyExplanation
                                                .strategy_name
                                        }

                                    </div>

                                </div>
                            )
                        }

                        {

                            strategyExplanation
                                .strategy_bias && (

                                <div
                                    className="
                                            mb-3
                                        "
                                >

                                    <div
                                        className="
                                                mb-1
                                                text-xs
                                                font-semibold
                                                uppercase
                                                tracking-wide
                                                text-blue-300
                                            "
                                    >

                                        Strategy Bias

                                    </div>

                                    <div
                                        className="
                                                text-sm
                                                text-gray-300
                                            "
                                    >

                                        {

                                            strategyExplanation
                                                .strategy_bias
                                        }

                                    </div>

                                </div>
                            )
                        }
                                                {

                            strategyExplanation
                                .market_alignment && (

                                <div
                                    className="
                                        mb-3
                                    "
                                >

                                    <div
                                        className="
                                            mb-1
                                            text-xs
                                            font-semibold
                                            uppercase
                                            tracking-wide
                                            text-blue-300
                                        "
                                    >

                                        Market Alignment

                                    </div>

                                    <div
                                        className="
                                            text-sm
                                            leading-relaxed
                                            text-gray-300
                                        "
                                    >

                                        {

                                            strategyExplanation
                                                .market_alignment
                                        }

                                    </div>

                                </div>
                            )
                        }
                                                {

                            strategyExplanation
                                .execution_expectation && (

                                <div
                                    className="
                                        mb-3
                                    "
                                >

                                    <div
                                        className="
                                            mb-1
                                            text-xs
                                            font-semibold
                                            uppercase
                                            tracking-wide
                                            text-blue-300
                                        "
                                    >

                                        Execution Expectation

                                    </div>

                                    <div
                                        className="
                                            text-sm
                                            leading-relaxed
                                            text-gray-300
                                        "
                                    >

                                        {

                                            strategyExplanation
                                                .execution_expectation
                                        }

                                    </div>

                                </div>
                            )
                        }
                                                 {

                            strategyExplanation
                                .risk_notes &&
                            strategyExplanation
                                .risk_notes
                                .length > 0 && (

                                <div
                                    className="
                                        mb-3
                                    "
                                >

                                    <div
                                        className="
                                            mb-2
                                            text-xs
                                            font-semibold
                                            uppercase
                                            tracking-wide
                                            text-yellow-300
                                        "
                                    >

                                        Risk Notes

                                    </div>

                                    <ul
                                        className="
                                            list-disc
                                            space-y-1
                                            pl-4
                                            text-sm
                                            leading-relaxed
                                            text-gray-300
                                        "
                                    >

                                        {

                                            strategyExplanation
                                                .risk_notes
                                                .map(
                                                    (
                                                        risk,
                                                        index
                                                    ) => (

                                                        <li
                                                            key={index}
                                                        >

                                                            {
                                                                risk
                                                            }

                                                        </li>
                                                    )
                                                )
                                        }

                                    </ul>

                                </div>
                            )
                        }

                        {

                            strategyExplanation
                                .selection_reasons &&
                            strategyExplanation
                                .selection_reasons
                                .length > 0 && (

                                <div
                                    className="
                                            mb-3
                                        "
                                >

                                    <div
                                        className="
                                                mb-2
                                                text-xs
                                                font-semibold
                                                uppercase
                                                tracking-wide
                                                text-blue-300
                                            "
                                    >

                                        Selection Reasons

                                    </div>

                                    <ul
                                        className="
                                                list-disc
                                                space-y-1
                                                pl-4
                                                text-sm
                                                leading-relaxed
                                                text-gray-300
                                            "
                                    >

                                        {

                                            strategyExplanation
                                                .selection_reasons
                                                .map(
                                                    (
                                                        reason,
                                                        index
                                                    ) => (

                                                        <li
                                                            key={index}
                                                        >

                                                            {
                                                                reason
                                                            }

                                                        </li>
                                                    )
                                                )
                                        }

                                    </ul>

                                </div>
                            )
                        }

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

