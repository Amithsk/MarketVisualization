//IntradayTradeStockAnalyser/frontend/components/replay/LearningInsightPanel.tsx

type Props = {

    learningInsight: string | null;

    executionSummary: string | null;

    tradeConstructionSummary: string | null;

    tradeCoaching?: {

        improvement_suggestions?: string[];

        mistakes_detected?: string[];

        coaching_summary?: string;

    } | null;
};

export default function LearningInsightPanel({

    learningInsight,

    executionSummary,

    tradeConstructionSummary,

    tradeCoaching

}: Props) {

    return (

        <div
            className="
                mb-6
                rounded-lg
                border
                border-blue-900
                bg-blue-950/30
                p-5
            "
        >

            {/* ===================================== */}
            {/* HEADER */}
            {/* ===================================== */}

            <div
                className="
                    mb-4
                    text-sm
                    font-bold
                    uppercase
                    tracking-wide
                    text-blue-300
                "
            >

                Learning Insight

            </div>

            {/* ===================================== */}
            {/* PRIMARY LEARNING INSIGHT */}
            {/* ===================================== */}

            <div
                className="
                    mb-4
                    text-sm
                    leading-relaxed
                    text-gray-200
                "
            >

                {

                    learningInsight ||

                    "No learning insight available."
                }

            </div>

            {/* ===================================== */}
            {/* AI TRADE COACHING */}
            {/* ===================================== */}

            {

                tradeCoaching && (

                    <div
                        className="
                            mb-4
                            rounded-md
                            border
                            border-yellow-900
                            bg-yellow-950/20
                            p-4
                        "
                    >

                        <div
                            className="
                                mb-3
                                text-xs
                                font-semibold
                                uppercase
                                tracking-wide
                                text-yellow-400
                            "
                        >

                            AI Trade Coaching

                        </div>

                        {

                            tradeCoaching
                                .coaching_summary && (

                                <div
                                    className="
                                        mb-3
                                        text-sm
                                        leading-relaxed
                                        text-gray-300
                                    "
                                >

                                    {

                                        tradeCoaching
                                            .coaching_summary
                                    }

                                </div>
                            )
                        }

                        {

                            tradeCoaching
                                .mistakes_detected &&
                            tradeCoaching
                                .mistakes_detected
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
                                            text-red-400
                                        "
                                    >

                                        Mistakes Detected

                                    </div>

                                    <ul
                                        className="
                                            list-disc
                                            space-y-1
                                            pl-4
                                            text-xs
                                            leading-relaxed
                                            text-gray-400
                                        "
                                    >

                                        {

                                            tradeCoaching
                                                .mistakes_detected
                                                .map(
                                                    (
                                                        mistake,
                                                        index
                                                    ) => (

                                                        <li
                                                            key={index}
                                                        >

                                                            {
                                                                mistake
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

                            tradeCoaching
                                .improvement_suggestions &&
                            tradeCoaching
                                .improvement_suggestions
                                .length > 0 && (

                                <div>

                                    <div
                                        className="
                                            mb-2
                                            text-xs
                                            font-semibold
                                            uppercase
                                            tracking-wide
                                            text-green-400
                                        "
                                    >

                                        Improvement Suggestions

                                    </div>

                                    <ul
                                        className="
                                            list-disc
                                            space-y-1
                                            pl-4
                                            text-xs
                                            leading-relaxed
                                            text-gray-400
                                        "
                                    >

                                        {

                                            tradeCoaching
                                                .improvement_suggestions
                                                .map(
                                                    (
                                                        suggestion,
                                                        index
                                                    ) => (

                                                        <li
                                                            key={index}
                                                        >

                                                            {
                                                                suggestion
                                                            }

                                                        </li>
                                                    )
                                                )
                                        }

                                    </ul>

                                </div>
                            )
                        }

                    </div>
                )
            }

            {/* ===================================== */}
            {/* EXECUTION CONTEXT */}
            {/* ===================================== */}

            <div
                className="
                    mb-3
                    rounded-md
                    border
                    border-gray-800
                    bg-gray-950
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
                        text-gray-500
                    "
                >

                    Execution Context

                </div>

                <div
                    className="
                        text-xs
                        leading-relaxed
                        text-gray-400
                    "
                >

                    {

                        executionSummary ||

                        "Execution summary unavailable."
                    }

                </div>

            </div>

            {/* ===================================== */}
            {/* TRADE CONSTRUCTION */}
            {/* ===================================== */}

            <div
                className="
                    rounded-md
                    border
                    border-gray-800
                    bg-gray-950
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
                        text-gray-500
                    "
                >

                    Trade Construction

                </div>

                <div
                    className="
                        text-xs
                        leading-relaxed
                        text-gray-400
                    "
                >

                    {

                        tradeConstructionSummary ||

                        "Trade construction summary unavailable."
                    }

                </div>

            </div>

        </div>
    );
}

