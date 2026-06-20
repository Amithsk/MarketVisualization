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
                        <div className="mb-4 text-yellow-400">
                            NIFTY ANALYSIS (Coming Next)
                        </div>

                        <div className="mb-4 text-yellow-400">
                            RELATIONSHIP ANALYSIS (Coming Next)
                        </div>

                        <div className="mb-4 text-yellow-400">
                            ACTION (Coming Next)
                        </div>

                        <div className="mb-4 text-yellow-400">
                            LEARNING (Coming Next)
                        </div>

                    </div>
                )
            }




        </div>

    );
}

