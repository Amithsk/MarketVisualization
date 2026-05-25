//IntradayTradeStockAnalyser/frontend/app/replay/page.tsx
"use client";

import { useState } from "react";

import SynchronizedCharts from
    "../../components/charts/SynchronizedCharts";

import { useReplayData }
    from "../../hooks/useReplayData";

export default function ReplayPage() {

    // -----------------------------------
    // Local state
    // -----------------------------------

    const [tradeDate, setTradeDate] =
        useState("");

    const [stock, setStock] =
        useState("");

    // -----------------------------------
    // Replay hook
    // -----------------------------------

    const {

        replayData,

        loading,

        error,

        fetchReplayData

    } = useReplayData();

    // -----------------------------------
    // Load replay
    // -----------------------------------

    const handleLoadReplay = async () => {

        if (!tradeDate || !stock) {

            alert(
                "Select trade date and stock"
            );

            return;
        }

        await fetchReplayData({

            tradeDate,

            stock
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

                {/* Trade Date */}

                <div
                    className="
                        flex
                        flex-col
                    "
                >

                    <label
                        className="
                            text-sm
                            mb-1
                            text-gray-400
                        "
                    >
                        Trade Date
                    </label>

                    <input
                        type="text"

                        value={tradeDate}

                        onChange={(e) =>
                            setTradeDate(
                                e.target.value
                            )
                        }

                        placeholder="2026-05-18"

                        className="
                            bg-gray-900
                            border
                            border-gray-700
                            rounded-md
                            px-3
                            py-2
                            text-sm
                        "
                    />

                </div>

                {/* Stock */}

                <div
                    className="
                        flex
                        flex-col
                    "
                >

                    <label
                        className="
                            text-sm
                            mb-1
                            text-gray-400
                        "
                    >
                        Stock
                    </label>

                    <input
                        type="text"

                        value={stock}

                        onChange={(e) =>
                            setStock(
                                e.target.value
                            )
                        }

                        placeholder="POLYCAB"

                        className="
                            bg-gray-900
                            border
                            border-gray-700
                            rounded-md
                            px-3
                            py-2
                            text-sm
                        "
                    />

                </div>

                {/* Load Replay */}

                <button

                    onClick={handleLoadReplay}

                    className="
                        bg-blue-600
                        hover:bg-blue-700
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
            {/* LOADING */}
            {/* -------------------------------- */}

            {

                loading && (

                    <div
                        className="
                            mb-4
                            text-blue-400
                        "
                    >

                        Loading replay...

                    </div>
                )
            }

            {/* -------------------------------- */}
            {/* ERROR */}
            {/* -------------------------------- */}

            {

                error && (

                    <div
                        className="
                            mb-4
                            text-red-400
                        "
                    >

                        {error}

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

                        stockName={stock}

                    />
                )
            }

        </div>
    );
}