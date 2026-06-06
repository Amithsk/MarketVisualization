//IntradayTradeStockAnalyser/frontend/components/replay/TimelineNarrationPanel.tsx

type TimelineNarration = {

    timestamp?: string;

    title?: string;

    narration?: string;

    interpretation?: string;

    event_type?: string;

    market_phase?: string;

};

type Props = {

    timelineNarration?: TimelineNarration[];


    currentCandleIndex?: number;

    compact?: boolean;

    onJumpToCandle?: (
        candleIndex: number
    ) => void;

};

export default function TimelineNarrationPanel({

    timelineNarration,

    currentCandleIndex,

    compact = false,

    onJumpToCandle,

}: Props) {

    // =====================================
    // COMPACT REPLAY MODE
    // =====================================

    if (

        compact &&

        timelineNarration
    ) {

        const visibleNarration =

            timelineNarration.filter(

                (
                    _,
                    index
                ) => {

                    if (
                        currentCandleIndex === undefined
                    ) {

                        return false;
                    }

                    return (

                        index >=
                        currentCandleIndex - 1 &&

                        index <=
                        currentCandleIndex + 1
                    );
                }
            );

        return (

            <div
                className="
                mb-6
                rounded-lg
                border
                border-orange-900
                bg-orange-950/20
                p-5
            "
            >

                {/* ========================= */}
                {/* HEADER */}
                {/* ========================= */}

                <div
                    className="
                    mb-4
                    text-sm
                    font-bold
                    uppercase
                    tracking-wide
                    text-orange-300
                "
                >

                    Current Market Story

                </div>

                {/* ========================= */}
                {/* COMPACT TIMELINE */}
                {/* ========================= */}

                <div
                    className="
                    space-y-3
                "
                >

                    {

                        visibleNarration.map(

                            (
                                item,
                                index
                            ) => {

                                const actualIndex =

                                    timelineNarration.indexOf(
                                        item
                                    );

                                const isActive =

                                    actualIndex ===
                                    currentCandleIndex;

                                return (

                                    <div

                                        key={actualIndex}

                                        onClick={() => {

                                            if (
                                                onJumpToCandle
                                            ) {

                                                onJumpToCandle(
                                                    actualIndex
                                                );
                                            }
                                        }}

                                        className={`
                                        rounded-md
                                        border
                                        p-3
                                        cursor-pointer
                                        transition-all

                                        ${isActive

                                                ? `
                                                border-cyan-500
                                                bg-cyan-950/40
                                            `

                                                : `
                                                border-gray-800
                                                bg-gray-950
                                            `
                                            }
                                    `}
                                    >

                                        <div
                                            className="
                                            mb-1
                                            text-sm
                                            font-semibold
                                            text-orange-300
                                        "
                                        >

                                            {

                                                item.title ||

                                                "Market Event"
                                            }

                                        </div>

                                        <div
                                            className="
                                            text-xs
                                            text-gray-400
                                        "
                                        >

                                            {

                                                item.narration ||

                                                "Narration unavailable."
                                            }

                                        </div>

                                    </div>
                                );
                            }
                        )
                    }

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
                border-orange-900
                bg-orange-950/20
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
                    text-orange-300
                "
            >

                Market Story Timeline

            </div>

            {/* ===================================== */}
            {/* EMPTY STATE */}
            {/* ===================================== */}

            {

                (
                    !timelineNarration ||

                    timelineNarration.length === 0
                ) && (

                    <div
                        className="
                            text-sm
                            text-gray-400
                        "
                    >

                        No market narration available.

                    </div>
                )
            }

            {/* ===================================== */}
            {/* TIMELINE */}
            {/* ===================================== */}

            <div
                className="
                    space-y-4
                "
            >

                {

                    timelineNarration?.map(

                        (
                            item,
                            index
                        ) => (
                            <div

                                key={index}

                                onClick={() => {

                                    if (
                                        onJumpToCandle
                                    ) {

                                        onJumpToCandle(index);
                                    }
                                }}

                                className={`
        rounded-md
        border
        p-4
        transition-all
        duration-300
        cursor-pointer

        ${currentCandleIndex === index

                                        ? `
                    border-cyan-500
                    bg-cyan-950/30
                    shadow-lg
                    shadow-cyan-500/20
                  `

                                        : `
                    border-gray-800
                    bg-gray-950
                    hover:border-gray-700
                  `
                                    }
    `}
                            >

                                {/* ========================= */}
                                {/* HEADER */}
                                {/* ========================= */}

                                <div
                                    className="
                                        mb-3
                                        flex
                                        items-center
                                        justify-between
                                        gap-3
                                    "
                                >

                                    <div
                                        className="
                                            text-sm
                                            font-semibold
                                            text-orange-300
                                        "
                                    >

                                        {

                                            item.title ||

                                            "Market Event"
                                        }

                                    </div>

                                    <div
                                        className="
                                            text-xs
                                            text-gray-500
                                        "
                                    >

                                        {

                                            item.timestamp ||

                                            "Timestamp unavailable"
                                        }

                                    </div>

                                </div>

                                {/* ========================= */}
                                {/* EVENT TAGS */}
                                {/* ========================= */}

                                <div
                                    className="
                                        mb-3
                                        flex
                                        flex-wrap
                                        gap-2
                                    "
                                >

                                    {

                                        item.event_type && (

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

                                                    item.event_type
                                                }

                                            </div>
                                        )
                                    }

                                    {

                                        item.market_phase && (

                                            <div
                                                className="
                                                    rounded
                                                    bg-purple-900
                                                    px-2
                                                    py-1
                                                    text-xs
                                                    text-purple-200
                                                "
                                            >

                                                {

                                                    item.market_phase
                                                }

                                            </div>
                                        )
                                    }

                                </div>

                                {/* ========================= */}
                                {/* NARRATION */}
                                {/* ========================= */}

                                <div
                                    className="
                                        mb-3
                                        text-sm
                                        leading-relaxed
                                        text-gray-300
                                    "
                                >

                                    {

                                        item.narration ||

                                        "Narration unavailable."
                                    }

                                </div>

                                {/* ========================= */}
                                {/* INTERPRETATION */}
                                {/* ========================= */}

                                <div
                                    className="
                                        rounded-md
                                        border
                                        border-gray-800
                                        bg-black/30
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

                                        Interpretation

                                    </div>

                                    <div
                                        className="
                                            text-xs
                                            leading-relaxed
                                            text-gray-400
                                        "
                                    >

                                        {

                                            item.interpretation ||

                                            "No interpretation available."
                                        }

                                    </div>

                                </div>

                            </div>
                        )
                    )
                }

            </div>

        </div>
    );
}

