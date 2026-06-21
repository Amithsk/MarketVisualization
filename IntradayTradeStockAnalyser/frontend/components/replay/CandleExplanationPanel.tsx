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

          <div
            className="
                grid
               grid-cols-1
               lg:grid-cols-2
                gap-6
                mb-6
                 ">
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
                        {/* STOCK MOVE */}
                        {/* --------------------- */}

                        <details
                            open
                            className="
        mb-4
        border-b
        border-slate-700
    "
                        >

                            <summary
                                className="
            cursor-pointer
            flex
            justify-between
            items-center
            py-3
            font-semibold
        "
                            >

                                <span>
                                    Stock Move
                                </span>

                                <span
                                    className={
                                        (
                                            selectedExplanation
                                                ?.stock_analysis
                                                ?.move
                                                ?.result ?? 0
                                        ) >= 0
                                            ? "text-green-400"
                                            : "text-red-400"
                                    }
                                >

                                    {
                                        selectedExplanation
                                            ?.stock_analysis
                                            ?.move
                                            ?.result
                                    }%

                                </span>

                            </summary>

                            <div className="pb-4">

                                <div
                                    className="
                text-cyan-300
                text-sm
                mb-2
            "
                                >
                                    Calculation
                                </div>

                                <div
                                    className="
                bg-slate-950
                border
                border-slate-700
                rounded
                p-3
                mb-3
                font-mono
                text-sm
            "
                                >

                                    Formula:
                                    {" "}
                                    {
                                        selectedExplanation
                                            ?.stock_analysis
                                            ?.move
                                            ?.formula
                                    }

                                    <br />

                                    Open:
                                    {" "}
                                    {
                                        selectedExplanation
                                            ?.stock_analysis
                                            ?.move
                                            ?.open
                                    }

                                    <br />

                                    Close:
                                    {" "}
                                    {
                                        selectedExplanation
                                            ?.stock_analysis
                                            ?.move
                                            ?.close
                                    }

                                    <br />

                                    Result:
                                    {" "}
                                    {
                                        selectedExplanation
                                            ?.stock_analysis
                                            ?.move
                                            ?.result
                                    }%

                                </div>

                                <div
                                    className="
                text-cyan-300
                text-sm
                mb-2
            "
                                >
                                    Meaning
                                </div>

                                <div className="text-gray-300">

                                    Direction:
                                    {" "}
                                    {
                                        selectedExplanation
                                            ?.stock_analysis
                                            ?.move
                                            ?.direction
                                    }

                                    <br />
                                    <br />

                                    {
                                        selectedExplanation
                                            ?.stock_analysis
                                            ?.move
                                            ?.interpretation
                                    }

                                </div>

                            </div>

                        </details>

                        {/* --------------------- */}
                        {/* VWAP POSITION */}
                        {/* --------------------- */}

                        <details
                            className="
        mb-4
        border-b
        border-slate-700
    "
                        >

                            <summary
                                className="
            cursor-pointer
            flex
            justify-between
            items-center
            py-3
            font-semibold
        "
                            >

                                <span>
                                    VWAP Position
                                </span>

                                <span
                                    className={
                                        (
                                            selectedExplanation
                                                ?.stock_analysis
                                                ?.vwap_position
                                                ?.result ?? 0
                                        ) >= 0
                                            ? "text-green-400"
                                            : "text-red-400"
                                    }
                                >

                                    {
                                        selectedExplanation
                                            ?.stock_analysis
                                            ?.vwap_position
                                            ?.result
                                    }

                                </span>

                            </summary>

                            <div className="pb-4">

                                <div
                                    className="
                text-cyan-300
                text-sm
                mb-2
            "
                                >
                                    Calculation
                                </div>

                                <div
                                    className="
                bg-slate-950
                border
                border-slate-700
                rounded
                p-3
                mb-3
                font-mono
                text-sm
            "
                                >

                                    Formula:
                                    {" "}
                                    {
                                        selectedExplanation
                                            ?.stock_analysis
                                            ?.vwap_position
                                            ?.formula
                                    }

                                    <br />

                                    Close:
                                    {" "}
                                    {
                                        selectedExplanation
                                            ?.stock_analysis
                                            ?.vwap_position
                                            ?.close
                                    }

                                    <br />

                                    VWAP:
                                    {" "}
                                    {
                                        selectedExplanation
                                            ?.stock_analysis
                                            ?.vwap_position
                                            ?.vwap
                                    }

                                    <br />

                                    Result:
                                    {" "}
                                    {
                                        selectedExplanation
                                            ?.stock_analysis
                                            ?.vwap_position
                                            ?.result
                                    }

                                </div>

                                <div
                                    className="
                text-cyan-300
                text-sm
                mb-2
            "
                                >
                                    Meaning
                                </div>

                                <div className="text-gray-300">

                                    Position:
                                    {" "}
                                    {
                                        selectedExplanation
                                            ?.stock_analysis
                                            ?.vwap_position
                                            ?.position
                                    }

                                    <br />
                                    <br />

                                    {
                                        selectedExplanation
                                            ?.stock_analysis
                                            ?.vwap_position
                                            ?.interpretation
                                    }

                                </div>

                            </div>

                        </details>
                      </div>  
                 )
            }
               </div>
             {/* ===================================== */}
             {/* NIFTY ANALYSIS */}
             {/* ===================================== */}
              <div>
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
               
           </div> 
             
           <div>
                        {/* ===================================== */}
                        {/* MARKET RELATIONSHIP ANALYSIS */}
                        {/* ===================================== */}

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
           </div> 
           <div>
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

           </div>    
           <div>
                                   {/* --------------------- */}
                        {/* LEARNING */}
                        {/* --------------------- */}
                        {
                            selectedExplanation?.learning && (

                                <div
                                    className="
                mb-6
                rounded-lg
                border
                border-yellow-700
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
                                        LEARNING
                                    </h3>

                                    {/* --------------------- */}
                                    {/* CONCEPT */}
                                    {/* --------------------- */}

                                    <div className="mb-4">

                                        <div
                                            className="
                        text-sm
                        font-semibold
                        text-cyan-300
                    "
                                        >
                                            Concept
                                        </div>

                                        <div className="text-gray-300">

                                            {
                                                selectedExplanation
                                                    ?.learning
                                                    ?.concept
                                            }

                                        </div>

                                    </div>

                                    {/* --------------------- */}
                                    {/* EVIDENCE */}
                                    {/* --------------------- */}

                                    <div className="mb-4">

                                        <div
                                            className="
                        text-sm
                        font-semibold
                        text-cyan-300
                    "
                                        >
                                            Evidence
                                        </div>

                                        <div className="text-gray-300">

                                            Stock Move:
                                            {" "}
                                            {
                                                selectedExplanation
                                                    ?.learning
                                                    ?.evidence
                                                    ?.stock_move_pct
                                            }%

                                        </div>

                                        <div className="text-gray-300">

                                            NIFTY Move:
                                            {" "}
                                            {
                                                selectedExplanation
                                                    ?.learning
                                                    ?.evidence
                                                    ?.nifty_move_pct
                                            }%

                                        </div>

                                        <div className="text-gray-300">

                                            Relative Strength:
                                            {" "}
                                            {
                                                selectedExplanation
                                                    ?.learning
                                                    ?.evidence
                                                    ?.relative_strength
                                            }x

                                        </div>

                                    </div>

                                    {/* --------------------- */}
                                    {/* LESSON */}
                                    {/* --------------------- */}

                                    <div className="mb-4">

                                        <div
                                            className="
                        text-sm
                        font-semibold
                        text-cyan-300
                    "
                                        >
                                            Lesson
                                        </div>

                                        <div className="text-gray-300">

                                            {
                                                selectedExplanation
                                                    ?.learning
                                                    ?.lesson
                                            }

                                        </div>

                                    </div>

                                    {/* --------------------- */}
                                    {/* REMEMBER */}
                                    {/* --------------------- */}

                                    <div
                                        className="
                    rounded
                    border-l-4
                    border-yellow-500
                    bg-slate-800
                    p-3
                "
                                    >

                                        <div
                                            className="
                        mb-2
                        font-semibold
                        text-yellow-400
                    "
                                        >
                                            Remember
                                        </div>

                                        <div className="text-gray-300">

                                            {
                                                selectedExplanation
                                                    ?.learning
                                                    ?.remember
                                            }

                                        </div>

                                    </div>

                                </div>
                            )
                        }

           </div>       


        </div>

    )
 
}