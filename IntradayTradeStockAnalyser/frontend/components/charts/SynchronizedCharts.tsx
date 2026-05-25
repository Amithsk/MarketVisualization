"use client";

import CandlestickChart from "./CandlestickChart";

import { Candle } from "../../types/candle";

type Props = {

    niftyCandles: Candle[];

    stockCandles: Candle[];

    stockName: string;
};

export default function SynchronizedCharts({

    niftyCandles,

    stockCandles,

    stockName

}: Props) {

    return (

        <div
            className="
                flex
                flex-col
                gap-6
                w-full
            "
        >

            {/* -------------------------------- */}
            {/* NIFTY CHART */}
            {/* -------------------------------- */}

            <CandlestickChart
                candles={niftyCandles}
                title="NIFTY 50"
            />

            {/* -------------------------------- */}
            {/* STOCK CHART */}
            {/* -------------------------------- */}

            <CandlestickChart
                candles={stockCandles}
                title={stockName}
            />

        </div>
    );
}