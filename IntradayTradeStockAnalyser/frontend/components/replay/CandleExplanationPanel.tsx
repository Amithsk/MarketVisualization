//IntradayTradeStockAnalyser/frontend/components/replay/CandleExplanationPanel.tsx

import {
    MarketEvent,
    CandleExplanation
}
    from "../../types/replay";


type Props = {

    selectedExplanation?: CandleExplanation | null;

    selectedEvents?: MarketEvent[];

    compact?: boolean;
};

export default function CandleExplanationPanel({

    selectedExplanation,

    selectedEvents = [],

    compact = false

}: Props) {

    console.log(
        "[CandleExplanationPanel] selectedExplanation:",
        selectedExplanation
    );

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
                {

                    selectedExplanation
                        .reasons &&

                    selectedExplanation
                        .reasons
                        .length > 0 && (

                        <div
                            className="
                mb-4
            "
                        >

                            <div
                                className="
                    mb-2
                    text-xs
                    font-semibold
                    uppercase
                    tracking-wide
                    text-cyan-300
                "
                            >

                                Key Reasons

                            </div>

                            <ul
                                className="
                    list-disc
                    space-y-1
                    pl-5
                    text-sm
                    text-gray-300
                "
                            >

                                {

                                    selectedExplanation
                                        .reasons
                                        .map(

                                            (
                                                reason,
                                                index
                                            ) => (

                                                <li
                                                    key={index}
                                                >

                                                    {reason}

                                                </li>
                                            )
                                        )
                                }

                            </ul>

                        </div>
                    )
                }

 
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
                                .trade_implication ||

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
                        {/* EVENTS DETECTED */}
                        {/* ========================= */}

                        {
                            selectedEvents.length > 0 && (

                                <div
                                    className="
                mb-4
            "
                                >

                                    <div
                                        className="
                    mb-2
                    text-sm
                    font-semibold
                    text-yellow-300
                "
                                    >
                                        Events Detected
                                    </div>

                                    <ul
                                        className="
                    list-disc
                    ml-5
                    text-sm
                    text-gray-300
                "
                                    >

                                        {
                                            selectedEvents.map(

                                                (
                                                    event,
                                                    index
                                                ) => (

                                                    <li
                                                        key={index}
                                                    >
                                                        {event.event_type}
                                                    </li>
                                                )
                                            )
                                        }

                                    </ul>

                                </div>
                            )
                        }

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
                        {/* REASON EXPLANATION */}
                        {/* ========================= */}
                        {

                            selectedExplanation
                                .reasons &&

                            selectedExplanation
                                .reasons
                                .length > 0 && (

                                <div
                                    className="
                mb-4
            "
                                >

                                    <div
                                        className="
                    mb-2
                    text-xs
                    font-semibold
                    uppercase
                    tracking-wide
                    text-cyan-300
                "
                                    >

                                        Key Reasons

                                    </div>

                                    <ul
                                        className="
                    list-disc
                    space-y-1
                    pl-5
                    text-sm
                    text-gray-300
                "
                                    >

                                        {

                                            selectedExplanation
                                                .reasons
                                                .map(

                                                    (
                                                        reason,
                                                        index
                                                    ) => (

                                                        <li
                                                            key={index}
                                                        >

                                                            {reason}

                                                        </li>
                                                    )
                                                )
                                        }

                                    </ul>

                                </div>
                            )
                        }

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
                                        .market_interpretation ||

                                    "No detailed explanation available."
                                }

                            </div>

                        </div>

                        {/* ========================= */}
                        {/* NIFTY RELATIONSHIP */}
                        {/* ========================= */}

                        {

                            selectedExplanation
                                .nifty_relationship && (

                                <div
                                    className="
                                        mb-4
                                        rounded-md
                                        border
                                        border-blue-900
                                        bg-blue-950/20
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
                                            text-blue-400
                                        "
                                    >

                                        Nifty Relationship

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
                                                .nifty_relationship
                                        }

                                    </div>

                                </div>
                            )
                        }


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
                                        .trade_implication ||

                                    "No trading implication available."
                                }

                            </div>

                        </div>
                  


                    </>
                )
            }

        </div>
    );
}

