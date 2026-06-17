//IntradayTradeStockAnalyser/frontend/app/replay/page.tsx

"use client";

import {
    useState,
    useEffect
} from "react";

import SynchronizedCharts from
    "../../components/charts/SynchronizedCharts";

import TradeDateSelector from
    "../../components/selectors/TradeDateSelector";

import StockSelector from
    "../../components/selectors/StockSelector";

import UploadPanel from
    "../../components/upload/UploadPanel";

import { useReplayData }
    from "../../hooks/useReplayData";

import { useTradeSelection }
    from "../../hooks/useTradeSelection";

import MarketBiasCard from
    "../../components/replay/MarketBiasCard";

import TradePermissionBanner from
    "../../components/replay/TradePermissionBanner";

import RelativeStrengthBadge from
    "../../components/replay/RelativeStrengthBadge";

import StrategyContextPanel from
    "../../components/replay/StrategyContextPanel";

import LearningInsightPanel from
    "../../components/replay/LearningInsightPanel";

import NIFTYRelationshipPanel from
    "../../components/replay/NIFTYRelationshipPanel";

import TimelineNarrationPanel from
    "../../components/replay/TimelineNarrationPanel";


import CandleExplanationPanel from
    "../../components/replay/CandleExplanationPanel";

import useReplayPlayback
    from "../../hooks/useReplayPlayback";


import ReplayControls
    from "../../components/replay/ReplayControls";

import IntradayPanel from
    "../../components/replay/IntradayPanel";


const FEATURES = {

    replayControls: false,

    intradayPanel: false,

    marketBias: false,

    tradePermission: false,

    relativeStrength: false,

    strategyPanel: false,

    learningPanel: false,

    timelinePanel: false,

    niftyRelationship: false,

};






export default function ReplayPage() {

    // -----------------------------------
    // Trade Selection
    // -----------------------------------

    const {

        tradeDates,

        selectedDate,

        selectTradeDate,

        stocks,

        selectedStock,

        setSelectedStock,

        loading: tradeLoading,

        error: tradeError

    } = useTradeSelection();

    // -----------------------------------
    // Replay Hook
    // -----------------------------------

    const {

        replayData,

        loading: replayLoading,

        error: replayError,

        fetchReplayData

    } = useReplayData();
    // -----------------------------------
    // Replay Playback Engine
    // -----------------------------------

    const {

        currentCandleIndex,

        isPlaying,

        playbackSpeed,

        replayProgress,

        play,

        pause,

        reset,

        nextCandle,

        previousCandle,

        jumpToCandle,

        setPlaybackSpeed,

    } = useReplayPlayback({

        totalCandles:
            replayData?.stock_candles?.length || 0

    });

    // -----------------------------------
    // Upload Status
    // -----------------------------------

    const [uploadSuccess, setUploadSuccess] =
        useState(false);

    const [

        selectedCandleIndex,

        setSelectedCandleIndex

    ] = useState<number>(0);

    // -----------------------------------
    // Reset Upload State
    // On Stock Change
    // -----------------------------------

    useEffect(() => {

        setUploadSuccess(false);

    }, [selectedStock]);

    // -----------------------------------
    // Upload Success
    // -----------------------------------

    const handleUploadSuccess = () => {

        setUploadSuccess(true);
    };

    // -----------------------------------
    // Load Replay
    // -----------------------------------

    const handleLoadReplay = async () => {

        if (
            !selectedDate ||
            !selectedStock
        ) {

            alert(
                "Select trade date and stock"
            );

            return;
        }

        await fetchReplayData({

            tradeDate:
                selectedDate,

            stock:
                selectedStock
        });
    };
    const selectedCandleEvents =

        replayData?.market_events?.filter(

            (event) =>

                event.candle_index ===
                selectedCandleIndex

        ) || [];

    console.log(
        "[SELECTED EVENTS]",
        selectedCandleIndex,
        selectedCandleEvents.length
    );

    return (

        <div
            className="
                min-h-screen
                bg-gray-950
                text-white
                p-6
            "
        >

            {/* -------------------------------- */}
            {/* PAGE HEADER */}
            {/* -------------------------------- */}

            <div
                className="
                    mb-6
                "
            >

                <h1
                    className="
                        text-2xl
                        font-bold
                    "
                >

                    Replay System

                </h1>

            </div>

            {/* -------------------------------- */}
            {/* CONTROLS */}
            {/* -------------------------------- */}

            <div
                className="
                    flex
                    gap-4
                    mb-6
                    items-end
                    flex-wrap
                "
            >

                {/* -------------------------------- */}
                {/* Trade Date Selector */}
                {/* -------------------------------- */}

                <TradeDateSelector

                    tradeDates={
                        tradeDates
                    }

                    selectedDate={
                        selectedDate
                    }

                    onSelectDate={
                        selectTradeDate
                    }

                    loading={
                        tradeLoading
                    }

                />

                {/* -------------------------------- */}
                {/* Stock Selector */}
                {/* -------------------------------- */}

                <StockSelector

                    stocks={
                        stocks
                    }

                    selectedStock={
                        selectedStock
                    }

                    onSelectStock={
                        setSelectedStock
                    }

                    disabled={
                        !selectedDate
                    }

                    loading={
                        tradeLoading
                    }

                />

                {/* -------------------------------- */}
                {/* Load Replay */}
                {/* -------------------------------- */}

                <button

                    onClick={
                        handleLoadReplay
                    }

                    disabled={
                        !selectedDate ||
                        !selectedStock ||
                        !uploadSuccess
                    }

                    className="
                        bg-blue-600
                        hover:bg-blue-700
                        disabled:bg-gray-700
                        disabled:cursor-not-allowed
                        px-4
                        py-2
                        rounded-md
                        text-sm
                        font-medium
                    "
                >

                    Load Replay

                </button>

            </div>

            {/* -------------------------------- */}
            {/* Upload Panel */}
            {/* -------------------------------- */}

            <div
                className="
                    mb-6
                "
            >

                <UploadPanel

                    selectedStock={
                        selectedStock
                    }

                    disabled={
                        !selectedDate ||
                        !selectedStock
                    }

                    onUploadSuccess={
                        handleUploadSuccess
                    }

                />

            </div>

            {/* -------------------------------- */}
            {/* Upload Helper */}
            {/* -------------------------------- */}

            {

                !uploadSuccess &&

                selectedDate &&

                selectedStock && (

                    <div
                        className="
                            mb-4
                            text-yellow-400
                            text-sm
                        "
                    >

                        Upload stock candle CSV
                        before loading replay.

                    </div>
                )
            }

            {/* -------------------------------- */}
            {/* LOADING */}
            {/* -------------------------------- */}

            {

                (tradeLoading || replayLoading) && (

                    <div
                        className="
                            mb-4
                            text-blue-400
                        "
                    >

                        Loading...

                    </div>
                )
            }

            {/* -------------------------------- */}
            {/* ERROR */}
            {/* -------------------------------- */}

            {

                (tradeError || replayError) && (

                    <div
                        className="
                            mb-4
                            text-red-400
                        "
                    >

                        {

                            tradeError ||
                            replayError
                        }

                    </div>
                )
            }
            {/* -------------------------------- */}
            {/* REPLAY CONTROLS */}
            {/* -------------------------------- */}

            {

                FEATURES.replayControls &&
                replayData && (

                    <div
                        className="
                            mb-6
                        "
                    >
                        <ReplayControls

                            isPlaying={
                                isPlaying
                            }

                            playbackSpeed={
                                playbackSpeed
                            }

                            replayProgress={
                                replayProgress
                            }

                            currentCandleIndex={
                                currentCandleIndex
                            }

                            totalCandles={
                                replayData
                                    .stock_candles
                                    .length
                            }

                            onPlay={
                                play
                            }

                            onPause={
                                pause
                            }

                            onReset={
                                reset
                            }

                            onNext={
                                nextCandle
                            }

                            onPrevious={
                                previousCandle
                            }

                            onSpeedChange={
                                setPlaybackSpeed
                            }

                        />

                        {
                            FEATURES.intradayPanel &&
                            replayData && (


                                <IntradayPanel

                                    tradeData={
                                        replayData.trade_data
                                    }

                                />
                            )
                        }

                    </div>
                )
            }

            {/* -------------------------------- */}
            {/* CHARTS */}
            {/* -------------------------------- */}

            {

                replayData && (

                    <div
                        className="
                            mb-6
                        "
                    >

                        <SynchronizedCharts

                            niftyCandles={
                                replayData
                                    .nifty_candles
                            }

                            stockCandles={
                                replayData
                                    .stock_candles
                            }

                            marketEvents={
                                replayData
                                    .market_events
                            }

                            stockName={
                                selectedStock
                            }

                            currentCandleIndex={
                                undefined
                            }
                            onCandleSelect={
                                setSelectedCandleIndex
                            }

                        />

                    </div>
                )
            }


            {/* -------------------------------- */}
            {/* CURRENT MARKET MOMENT */}
            {/* -------------------------------- */}

            {


                replayData && (


                    <CandleExplanationPanel

                        compact={
                            isPlaying
                        }

                        selectedEvents={
                            selectedCandleEvents
                        }


                        selectedExplanation={

                            Object.values(

                                replayData
                                    ?.explanation_context
                                    ?.candle_explanations || {}

                            )[selectedCandleIndex] ||

                            Object.values(

                                replayData
                                    ?.explanation_context
                                    ?.candle_explanations || {}

                            )[0]

                        }

                    />
                )
            }

            {/* -------------------------------- */}
            {/* LEARNING INSIGHT PANEL */}
            {/* -------------------------------- */}

            {

                FEATURES.learningPanel &&
                replayData && (

                    <LearningInsightPanel

                        learningInsight={
                            replayData
                                ?.narrative_context
                                ?.learning_insight
                        }

                        executionSummary={
                            replayData
                                ?.narrative_context
                                ?.execution_summary
                        }

                        tradeConstructionSummary={
                            replayData
                                ?.narrative_context
                                ?.trade_construction_summary
                        }

                        compact={
                            isPlaying
                        }

                        tradeCoaching={
                            replayData
                                ?.explanation_context
                                ?.trade_coaching
                        }

                    />
                )
            }

            {/* -------------------------------- */}
            {/* PAUSED MODE ANALYSIS */}
            {/* -------------------------------- */}

            {

                replayData &&

                !isPlaying && (

                    <>
                        {/* -------------------------------- */}
                        {/* MARKET CONTEXT */}
                        {/* -------------------------------- */}

                        {
                            FEATURES.marketBias && (

                                <MarketBiasCard
                                    marketContext={
                                        replayData.market_context
                                    }
                                />

                            )
                        }

                        {/* -------------------------------- */}
                        {/* TRADE PERMISSION */}
                        {/* -------------------------------- */}

                        {
                            FEATURES.tradePermission && (

                                <TradePermissionBanner
                                    tradePermission={
                                        replayData
                                            .execution_control
                                            .trade_permission
                                    }
                                    executionAllowed={
                                        replayData
                                            .execution_control
                                            .execution_allowed
                                    }
                                />

                            )
                        }

                        {/* -------------------------------- */}
                        {/* RELATIVE STRENGTH */}
                        {/* -------------------------------- */}

                        {
                            FEATURES.relativeStrength && (

                                <RelativeStrengthBadge
                                    rsValue={
                                        replayData
                                            .stock_selection_context
                                            .rs_value
                                    }
                                    tradable={
                                        replayData
                                            .stock_selection_context
                                            .tradable
                                    }
                                />

                            )
                        }

                        {/* -------------------------------- */}
                        {/* STRATEGY CONTEXT */}
                        {/* -------------------------------- */}

                        {
                            FEATURES.strategyPanel && (

                                <StrategyContextPanel
                                    strategyUsed={
                                        replayData
                                            .trade_construction
                                            .strategy_used
                                    }
                                    structureValid={
                                        replayData
                                            .trade_construction
                                            .structure_valid
                                    }
                                    reason={
                                        replayData
                                            .stock_selection_context
                                            .reason
                                    }
                                    strategySummary={
                                        replayData
                                            .narrative_context
                                            .strategy_summary
                                    }
                                    strategyExplanation={
                                        replayData
                                            .explanation_context
                                            .strategy_explanations
                                    }
                                />

                            )
                        }

                        {/* -------------------------------- */}
                        {/* NIFTY RELATIONSHIP PANEL */}
                        {/* -------------------------------- */}

                        {
                            FEATURES.niftyRelationship && (

                                <NIFTYRelationshipPanel
                                    niftyRelationshipAnalysis={
                                        replayData
                                            ?.explanation_context
                                            ?.nifty_relationship_analysis
                                    }
                                />

                            )
                        }

                        {/* -------------------------------- */}
                        {/* TIMELINE NARRATION PANEL */}
                        {/* -------------------------------- */}
                        {
                            FEATURES.timelinePanel && (

                                <TimelineNarrationPanel
                                    timelineNarration={
                                        replayData
                                            ?.explanation_context
                                            ?.timeline_narration
                                    }
                                    currentCandleIndex={
                                        currentCandleIndex
                                    }
                                    compact={false}
                                    onJumpToCandle={
                                        jumpToCandle
                                    }
                                />

                            )
                        }


                    </>
                )
            }


        </div>

    );

}