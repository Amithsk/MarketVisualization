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

    console.log(
        "[Stock Analysis]",
        selectedExplanation?.stock_analysis
    );

    console.log(
        "[NIFTY Analysis]",
        selectedExplanation?.nifty_analysis
    );

    console.log(
        "[Relationship Analysis]",
        selectedExplanation?.relationship_analysis
    );

    console.log(
        "[Action]",
        selectedExplanation?.action
    );

    console.log(
        "[Learning]",
        selectedExplanation?.learning
    );


    return (
        <div>
            {/* ===================================== */}
            {/* STOCK ANALYSIS */}
            {/* ===================================== */}

            {
                selectedExplanation?.stock_analysis && (

                    <div
                        className="
                mb-6
                rounded-lg
                border
                border-slate-700
                bg-slate-900
                p-4
            "
                    >

                        <h3
                            className="
                    mb-4
                    text-lg
                    font-semibold
                    text-cyan-400
                "
                        >
                            STOCK ANALYSIS
                        </h3>

                        {/* --------------------- */}
                        {/* MOVE */}
                        {/* --------------------- */}

                        <div className="mb-4">

                            <div
                                className="
                        text-sm
                        font-semibold
                        text-cyan-300
                    "
                            >
                                Move %
                            </div>

                            <div className="text-sm text-gray-300">

                                Formula:
                                {" "}
                                {
                                    selectedExplanation
                                        ?.stock_analysis
                                        ?.move
                                        ?.formula
                                }

                            </div>

                            <div className="text-sm text-gray-300">

                                Open:
                                {" "}
                                {
                                    selectedExplanation
                                        ?.stock_analysis
                                        ?.move
                                        ?.open
                                }

                            </div>

                            <div className="text-sm text-gray-300">

                                Close:
                                {" "}
                                {
                                    selectedExplanation
                                        ?.stock_analysis
                                        ?.move
                                        ?.close
                                }

                            </div>

                            <div
                                className="
                        mt-2
                        text-base
                        font-semibold
                        text-green-400
                    "
                            >

                                Result:
                                {" "}
                                {
                                    selectedExplanation
                                        ?.stock_analysis
                                        ?.move
                                        ?.result
                                }%

                            </div>

                            <div className="text-sm text-gray-400">

                                Direction:
                                {" "}
                                {
                                    selectedExplanation
                                        ?.stock_analysis
                                        ?.move
                                        ?.direction
                                }

                            </div>

                            <div className="text-sm text-gray-400">

                                {
                                    selectedExplanation
                                        ?.stock_analysis
                                        ?.move
                                        ?.interpretation
                                }

                            </div>

                        </div>

                        {/* --------------------- */}
                        {/* VWAP */}
                        {/* --------------------- */}

                        <div>

                            <div
                                className="
                        text-sm
                        font-semibold
                        text-cyan-300
                    "
                            >
                                VWAP Position
                            </div>

                            <div className="text-sm text-gray-300">

                                Formula:
                                {" "}
                                {
                                    selectedExplanation
                                        ?.stock_analysis
                                        ?.vwap_position
                                        ?.formula
                                }

                            </div>

                            <div className="text-sm text-gray-300">

                                Close:
                                {" "}
                                {
                                    selectedExplanation
                                        ?.stock_analysis
                                        ?.vwap_position
                                        ?.close
                                }

                            </div>

                            <div className="text-sm text-gray-300">

                                VWAP:
                                {" "}
                                {
                                    selectedExplanation
                                        ?.stock_analysis
                                        ?.vwap_position
                                        ?.vwap
                                }

                            </div>

                            <div
                                className="
                        mt-2
                        text-base
                        font-semibold
                        text-green-400
                    "
                            >

                                Result:
                                {" "}
                                {
                                    selectedExplanation
                                        ?.stock_analysis
                                        ?.vwap_position
                                        ?.result
                                }

                            </div>

                            <div className="text-sm text-gray-400">

                                Position:
                                {" "}
                                {
                                    selectedExplanation
                                        ?.stock_analysis
                                        ?.vwap_position
                                        ?.position
                                }

                            </div>

                            <div className="text-sm text-gray-400">

                                {
                                    selectedExplanation
                                        ?.stock_analysis
                                        ?.vwap_position
                                        ?.interpretation
                                }

                            </div>

                        </div>
                        {/* ===================================== */}
                        {/* NIFTY ANALYSIS */}
                        {/* ===================================== */}

                        {
                            selectedExplanation?.nifty_analysis && (

                                <div
                                    className="
                mb-6
                rounded-lg
                border
                border-slate-700
                bg-slate-900
                p-4
            "
                                >

                                    <h3
                                        className="
                    mb-4
                    text-lg
                    font-semibold
                    text-cyan-400
                "
                                    >
                                        NIFTY ANALYSIS
                                    </h3>

                                    {/* --------------------- */}
                                    {/* NIFTY MOVE */}
                                    {/* --------------------- */}

                                    <div>

                                        <div
                                            className="
                        text-sm
                        font-semibold
                        text-cyan-300
                    "
                                        >
                                            Market Move %
                                        </div>

                                        <div className="text-sm text-gray-300">

                                            Formula:
                                            {" "}
                                            {
                                                selectedExplanation
                                                    ?.nifty_analysis
                                                    ?.move
                                                    ?.formula
                                            }

                                        </div>

                                        <div className="text-sm text-gray-300">

                                            Open:
                                            {" "}
                                            {
                                                selectedExplanation
                                                    ?.nifty_analysis
                                                    ?.move
                                                    ?.open
                                            }

                                        </div>

                                        <div className="text-sm text-gray-300">

                                            Close:
                                            {" "}
                                            {
                                                selectedExplanation
                                                    ?.nifty_analysis
                                                    ?.move
                                                    ?.close
                                            }

                                        </div>

                                        <div
                                            className="
                        mt-2
                        text-base
                        font-semibold
                        text-green-400
                    "
                                        >

                                            Result:
                                            {" "}
                                            {
                                                selectedExplanation
                                                    ?.nifty_analysis
                                                    ?.move
                                                    ?.result
                                            }%

                                        </div>

                                        <div className="text-sm text-gray-400">

                                            Direction:
                                            {" "}
                                            {
                                                selectedExplanation
                                                    ?.nifty_analysis
                                                    ?.move
                                                    ?.direction
                                            }

                                        </div>

                                        <div className="text-sm text-gray-400">

                                            {
                                                selectedExplanation
                                                    ?.nifty_analysis
                                                    ?.move
                                                    ?.interpretation
                                            }

                                        </div>

                                    </div>

                                </div>
                            )
                        }

                        {
                            selectedExplanation?.relationship_analysis && (

                                <div
                                    className="
                mb-6
                rounded-lg
                border
                border-slate-700
                bg-slate-900
                p-4
            "
                                >

                                    <h3
                                        className="
                    mb-4
                    text-lg
                    font-semibold
                    text-yellow-400
                "
                                    >
                                        MARKET RELATIONSHIP ANALYSIS
                                    </h3>

                                    <div className="mb-4">

                                        <div
                                            className="
                        text-sm
                        font-semibold
                        text-cyan-300
                    "
                                        >
                                            Market Condition
                                        </div>

                                        <div className="text-gray-300">

                                            {
                                                selectedExplanation
                                                    ?.relationship_analysis
                                                    ?.market_condition
                                            }

                                        </div>

                                    </div>

                                    <div className="mb-4">

                                        <div
                                            className="
                        text-sm
                        font-semibold
                        text-cyan-300
                    "
                                        >
                                            Stock Move %
                                        </div>

                                        <div className="text-gray-300">

                                            {
                                                selectedExplanation
                                                    ?.relationship_analysis
                                                    ?.stock_move_pct
                                            }%

                                        </div>

                                    </div>

                                    <div className="mb-4">

                                        <div
                                            className="
                        text-sm
                        font-semibold
                        text-cyan-300
                    "
                                        >
                                            NIFTY Move %
                                        </div>

                                        <div className="text-gray-300">

                                            {
                                                selectedExplanation
                                                    ?.relationship_analysis
                                                    ?.nifty_move_pct
                                            }%

                                        </div>

                                    </div>

                                    <div>

                                        <div
                                            className="
                        text-sm
                        font-semibold
                        text-cyan-300
                    "
                                        >
                                            Relative Strength
                                        </div>

                                        <div className="text-gray-300">

                                            Formula:
                                            {" "}
                                            {
                                                selectedExplanation
                                                    ?.relationship_analysis
                                                    ?.relative_strength
                                                    ?.formula
                                            }

                                        </div>

                                        <div className="text-gray-300">

                                            Calculation:
                                            {" "}
                                            {
                                                selectedExplanation
                                                    ?.relationship_analysis
                                                    ?.relative_strength
                                                    ?.calculation
                                            }

                                        </div>

                                        <div
                                            className="
                        mt-2
                        text-green-400
                        font-semibold
                    "
                                        >

                                            Result:
                                            {" "}
                                            {
                                                selectedExplanation
                                                    ?.relationship_analysis
                                                    ?.relative_strength
                                                    ?.result
                                            }

                                        </div>

                                        <div className="text-gray-400">

                                            {
                                                selectedExplanation
                                                    ?.relationship_analysis
                                                    ?.relative_strength
                                                    ?.interpretation
                                            }

                                        </div>

                                    </div>

                                </div>
                            )
                        }

                        {/* --------------------- */}
                        {/* ACTION  */}
                        {/* --------------------- */}

                        {
                            selectedExplanation?.action && (

                                <div
                                    className="
                mb-6
                rounded-lg
                border
                border-slate-700
                bg-slate-900
                p-4
            "
                                >

                                    <h3
                                        className="
                    mb-4
                    text-lg
                    font-semibold
                    text-green-400
                "
                                    >
                                        TRADE ACTION
                                    </h3>

                                    {/* --------------------- */}
                                    {/* WOULD TRADE */}
                                    {/* --------------------- */}

                                    <div className="mb-4">

                                        <div
                                            className="
                        text-sm
                        font-semibold
                        text-cyan-300
                    "
                                        >
                                            Would Trade
                                        </div>

                                        <div
                                            className={`
                        text-lg
                        font-bold
                        ${selectedExplanation
                                                    ?.action
                                                    ?.would_trade
                                                    ? "text-green-400"
                                                    : "text-red-400"
                                                }
                    `}
                                        >

                                            {
                                                selectedExplanation
                                                    ?.action
                                                    ?.would_trade
                                                    ? "YES"
                                                    : "NO"
                                            }

                                        </div>

                                    </div>

                                    {/* --------------------- */}
                                    {/* TRADE BIAS */}
                                    {/* --------------------- */}

                                    <div className="mb-4">

                                        <div
                                            className="
                        text-sm
                        font-semibold
                        text-cyan-300
                    "
                                        >
                                            Trade Bias
                                        </div>

                                        <div className="text-gray-300">

                                            {
                                                selectedExplanation
                                                    ?.action
                                                    ?.trade_bias
                                            }

                                        </div>

                                    </div>

                                    {/* --------------------- */}
                                    {/* CONFIDENCE */}
                                    {/* --------------------- */}

                                    <div className="mb-4">

                                        <div
                                            className="
                        text-sm
                        font-semibold
                        text-cyan-300
                    "
                                        >
                                            Confidence
                                        </div>

                                        <div className="text-gray-300">

                                            {
                                                selectedExplanation
                                                    ?.action
                                                    ?.confidence
                                            }

                                        </div>

                                    </div>

                                    {/* --------------------- */}
                                    {/* REASONS */}
                                    {/* --------------------- */}

                                    <div className="mb-4">

                                        <div
                                            className="
                        text-sm
                        font-semibold
                        text-cyan-300
                    "
                                        >
                                            Why Trade?
                                        </div>

                                        <ul
                                            className="
                        mt-2
                        list-disc
                        list-inside
                        text-gray-300
                    "
                                        >

                                            {
                                                selectedExplanation
                                                    ?.action
                                                    ?.reason
                                                    ?.map(

                                                        (
                                                            item: string,
                                                            index: number
                                                        ) => (

                                                            <li key={index}>
                                                                {item}
                                                            </li>
                                                        )
                                                    )
                                            }

                                        </ul>

                                    </div>

                                    {/* --------------------- */}
                                    {/* WHY NOT */}
                                    {/* --------------------- */}

                                    {

                                        selectedExplanation
                                            ?.action
                                            ?.why_not
                                            ?.length > 0 && (

                                            <div>

                                                <div
                                                    className="
                                text-sm
                                font-semibold
                                text-red-300
                            "
                                                >
                                                    Why Not?
                                                </div>

                                                <ul
                                                    className="
                                mt-2
                                list-disc
                                list-inside
                                text-gray-300
                            "
                                                >

                                                    {
                                                        selectedExplanation
                                                            ?.action
                                                            ?.why_not
                                                            ?.map(

                                                                (
                                                                    item: string,
                                                                    index: number
                                                                ) => (

                                                                    <li key={index}>
                                                                        {item}
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

                        <div className="mb-4 text-yellow-400">
                            LEARNING (Coming Next)
                        </div>

                    </div>
                )
            }




        </div>

    );
}

