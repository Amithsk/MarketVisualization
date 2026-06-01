//IntradayTradeStockAnalyser/frontend/components/replay/NIFTYRelationshipPanel.tsx

import { NiftyRelationshipAnalysis }
from "../../types/replay";

type Props = {
    niftyRelationshipAnalysis?:
        NiftyRelationshipAnalysis | null;
};

export default function NIFTYRelationshipPanel({

    niftyRelationshipAnalysis

}: Props) {

    const marketAlignment =
        niftyRelationshipAnalysis
            ?.market_alignment;

    const relativeStrengthAnalysis  =
        niftyRelationshipAnalysis
            ?.relative_strength_analysis;

    const marketDirection  =
        niftyRelationshipAnalysis
            ?.market_direction;

    const stockBehavior  =
        niftyRelationshipAnalysis
            ?.stock_behavior;

    const tradingImplication  =
        niftyRelationshipAnalysis
            ?.trading_implication;

    const relationshipStrength =
        niftyRelationshipAnalysis
            ?.relationship_strength;

    return (

        <div
            className="
                mb-6
                rounded-lg
                border
                border-purple-900
                bg-purple-950/20
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
                    text-purple-300
                "
            >

                NIFTY Relationship Analysis

            </div>

            {/* ===================================== */}
            {/* RELATIONSHIP SUMMARY */}
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

                    tradingImplication  ||

                    "No NIFTY relationship analysis available."
                }

            </div>

            {/* ===================================== */}
            {/* MARKET RELATIONSHIP GRID */}
            {/* ===================================== */}

            <div
                className="
                    mb-4
                    grid
                    grid-cols-2
                    gap-3
                "
            >

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

                        NIFTY Trend

                    </div>

                    <div
                        className="
                            text-sm
                            font-medium
                            text-gray-300
                        "
                    >

                        {

                            marketDirection   ||

                            "Unavailable"
                        }

                    </div>

                </div>

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

                        Stock Trend

                    </div>

                    <div
                        className="
                            text-sm
                            font-medium
                            text-gray-300
                        "
                    >

                        {

                            stockBehavior  ||

                            "Unavailable"
                        }

                    </div>

                </div>

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

                        Market Alignment

                    </div>

                    <div
                        className="
                            text-sm
                            font-medium
                            text-gray-300
                        "
                    >

                        {

                            marketAlignment ||

                            "Unavailable"
                        }

                    </div>

                </div>

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

                        Relative Strength

                    </div>

                    <div
                        className="
                            text-sm
                            font-medium
                            text-gray-300
                        "
                    >

                        {

                            relativeStrengthAnalysis  ||

                            "Unavailable"
                        }

                    </div>

                </div>

            </div>

            {/* ===================================== */}
            {/* MARKET INFLUENCE */}
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

                    NIFTY Influence

                </div>

                <div
                    className="
                        text-xs
                        leading-relaxed
                        text-gray-400
                    "
                >

                    {

                        relationshipStrength  ||

                        "No market influence explanation available."
                    }

                </div>

            </div>

        </div>
    );
}

