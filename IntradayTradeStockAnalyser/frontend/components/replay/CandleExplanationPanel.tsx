//IntradayTradeStockAnalyser/frontend/components/replay/CandleExplanationPanel.tsx

type CandleExplanation = {

    title?: string;

    summary?: string;

    explanation?: string;

    trading_implication?: string;

    event_type?: string;

    confidence_score?: number;

    market_context?: string;

    candle_time?: string;
};

type Props = {

    selectedExplanation?: CandleExplanation | null;

    compact?: boolean;
};

export default function CandleExplanationPanel({

    selectedExplanation,
    compact = false

}: Props) {
    
    // =====================================
    // COMPACT REPLAY MODE
    // =====================================

    if (

        compact &&

        selectedExplanation
    ) {

        return (

            <div
                className="
                mb-6
                rounded-lg
                border
                border-cyan-700
                bg-cyan-950/30
                p-5
            "
            >

                {/* ========================= */}
                {/* TITLE */}
                {/* ========================= */}

                <div
                    className="
                    mb-2
                    text-lg
                    font-bold
                    text-cyan-300
                "
                >

                    {

                        selectedExplanation.title ||

                        "Current Market Moment"
                    }

                </div>

                {/* ========================= */}
                {/* SUMMARY */}
                {/* ========================= */}

                <div
                    className="
                    mb-4
                    text-sm
                    leading-relaxed
                    text-gray-200
                "
                >

                    {

                        selectedExplanation.summary ||

                        "No summary available."
                    }

                </div>

                {/* ========================= */}
                {/* TRADE IMPLICATION */}
                {/* ========================= */}

                <div
                    className="
                    rounded-md
                    border
                    border-yellow-900
                    bg-yellow-950/20
                    p-3
                "
                >

                    <div
                        className="
                        mb-1
                        text-xs
                        font-semibold
                        uppercase
                        tracking-wide
                        text-yellow-400
                    "
                    >

                        Trade Implication

                    </div>

                    <div
                        className="
                        text-sm
                        text-gray-300
                    "
                    >

                        {

                            selectedExplanation
                                .trading_implication ||

                            "No trading implication available."
                        }

                    </div>

                </div>

            </div>
        );
    }

    return (

        <div
            className="
                mb-6
                rounded-lg
                border
                border-cyan-900
                bg-cyan-950/20
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
                    text-cyan-300
                "
            >

                Candle Explanation

            </div>

            {/* ===================================== */}
            {/* EMPTY STATE */}
            {/* ===================================== */}

            {

                !selectedExplanation && (

                    <div
                        className="
                            text-sm
                            text-gray-400
                        "
                    >

                        Hover or select a candle
                        to view explanation.

                    </div>
                )
            }

            {/* ===================================== */}
            {/* EXPLANATION CONTENT */}
            {/* ===================================== */}

            {

                selectedExplanation && (

                    <>

                        {/* ========================= */}
                        {/* TITLE + TIMESTAMP */}
                        {/* ========================= */}

                        <div
                            className="
                                mb-4
                                flex
                                items-center
                                justify-between
                                gap-3
                            "
                        >

                            <div
                                className="
                                    text-base
                                    font-semibold
                                    text-cyan-200
                                "
                            >

                                {

                                    selectedExplanation
                                        .title ||

                                    "Market Candle"
                                }

                            </div>

                            <div
                                className="
                                    text-xs
                                    text-gray-500
                                "
                            >

                                {

                                    selectedExplanation
                                        .candle_time ||

                                    "Time unavailable"
                                }

                            </div>

                        </div>

                        {/* ========================= */}
                        {/* EVENT TAGS */}
                        {/* ========================= */}

                        <div
                            className="
                                mb-4
                                flex
                                flex-wrap
                                gap-2
                            "
                        >

                            {

                                selectedExplanation
                                    .event_type && (

                                    <div
                                        className="
                                            rounded
                                            bg-blue-900
                                            px-2
                                            py-1
                                            text-xs
                                            text-blue-200
                                        "
                                    >

                                        {

                                            selectedExplanation
                                                .event_type
                                        }

                                    </div>
                                )
                            }

                            {

                                selectedExplanation
                                    .confidence_score !==
                                undefined && (

                                    <div
                                        className="
                                            rounded
                                            bg-green-900
                                            px-2
                                            py-1
                                            text-xs
                                            text-green-200
                                        "
                                    >

                                        Confidence:
                                        {" "}

                                        {

                                            selectedExplanation
                                                .confidence_score
                                        }

                                    </div>
                                )
                            }

                        </div>

                        {/* ========================= */}
                        {/* SUMMARY */}
                        {/* ========================= */}

                        <div
                            className="
                                mb-4
                                text-sm
                                leading-relaxed
                                text-gray-200
                            "
                        >

                            {

                                selectedExplanation
                                    .summary ||

                                "No summary available."
                            }

                        </div>

                        {/* ========================= */}
                        {/* DETAILED EXPLANATION */}
                        {/* ========================= */}

                        <div
                            className="
                                mb-4
                                rounded-md
                                border
                                border-gray-800
                                bg-gray-950
                                p-4
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

                                Market Interpretation

                            </div>

                            <div
                                className="
                                    text-sm
                                    leading-relaxed
                                    text-gray-300
                                "
                            >

                                {

                                    selectedExplanation
                                        .explanation ||

                                    "No detailed explanation available."
                                }

                            </div>

                        </div>

                        {/* ========================= */}
                        {/* TRADING IMPLICATION */}
                        {/* ========================= */}

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
                                    mb-2
                                    text-xs
                                    font-semibold
                                    uppercase
                                    tracking-wide
                                    text-yellow-400
                                "
                            >

                                Trading Implication

                            </div>

                            <div
                                className="
                                    text-sm
                                    leading-relaxed
                                    text-gray-300
                                "
                            >

                                {

                                    selectedExplanation
                                        .trading_implication ||

                                    "No trading implication available."
                                }

                            </div>

                        </div>

                        {/* ========================= */}
                        {/* MARKET CONTEXT */}
                        {/* ========================= */}

                        {

                            selectedExplanation
                                .market_context && (

                                <div
                                    className="
                                        rounded-md
                                        border
                                        border-purple-900
                                        bg-purple-950/20
                                        p-4
                                    "
                                >

                                    <div
                                        className="
                                            mb-2
                                            text-xs
                                            font-semibold
                                            uppercase
                                            tracking-wide
                                            text-purple-400
                                        "
                                    >

                                        Market Context

                                    </div>

                                    <div
                                        className="
                                            text-sm
                                            leading-relaxed
                                            text-gray-300
                                        "
                                    >

                                        {

                                            selectedExplanation
                                                .market_context
                                        }

                                    </div>

                                </div>
                            )
                        }

                    </>
                )
            }

        </div>
    );
}

