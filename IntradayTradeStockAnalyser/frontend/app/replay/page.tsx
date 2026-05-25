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
    // Upload Status
    // -----------------------------------

    const [uploadSuccess, setUploadSuccess] =
        useState(false);

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

                !uploadSuccess

                &&

                selectedDate

                &&

                selectedStock

                && (

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

                (tradeLoading || replayLoading)

                && (

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

                (tradeError || replayError)

                && (

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
            {/* CHARTS */}
            {/* -------------------------------- */}

            {

                replayData && (

                    <SynchronizedCharts

                        niftyCandles={
                            replayData
                                .nifty_candles
                        }

                        stockCandles={
                            replayData
                                .stock_candles
                        }

                        stockName={
                            selectedStock
                        }

                    />
                )
            }

        </div>
    );
}