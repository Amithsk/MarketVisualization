//IntradayTradeStockAnalyser/frontend/components/replay/IntradayPanel.tsx

import { ReplayTradeData }
    from "../../types/replay";

type Props = {

    tradeData: ReplayTradeData;
};

export default function IntradayPanel({

    tradeData

}: Props) {

    console.log(
        "[IntradayPanel] tradeData:",
        tradeData
    );

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

                Intraday Trade Plan

            </div>

            <div
                className="
                    mb-4
                    grid
                    grid-cols-2
                    gap-3
                "
            >

                <div>
                    <div className="text-xs text-gray-500">
                        Strategy
                    </div>

                    <div className="text-sm text-white">
                        {tradeData.strategy}
                    </div>
                </div>

                <div>
                    <div className="text-xs text-gray-500">
                        Position Type
                    </div>

                    <div className="text-sm text-white">
                        {tradeData.position_type}
                    </div>
                </div>

                <div>
                    <div className="text-xs text-gray-500">
                        Trade Mode
                    </div>

                    <div className="text-sm text-white">
                        {tradeData.trade_mode}
                    </div>
                </div>

                <div>
                    <div className="text-xs text-gray-500">
                        Status
                    </div>

                    <div className="text-sm text-white">
                        {tradeData.plan_status}
                    </div>
                </div>

            </div>

            <div
                className="
                    mb-4
                    grid
                    grid-cols-3
                    gap-3
                "
            >

                <div>
                    <div className="text-xs text-gray-500">
                        Planned Entry
                    </div>

                    <div className="text-sm text-white">
                        {tradeData.planned_entry_price}
                    </div>
                </div>

                <div>
                    <div className="text-xs text-gray-500">
                        Planned Stop
                    </div>

                    <div className="text-sm text-white">
                        {tradeData.planned_stop_price}
                    </div>
                </div>

                <div>
                    <div className="text-xs text-gray-500">
                        Planned Target
                    </div>

                    <div className="text-sm text-white">
                        {tradeData.planned_target_price}
                    </div>
                </div>

            </div>

            <div>

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

                    Setup Description

                </div>

                <div
                    className="
                        text-sm
                        text-gray-300
                    "
                >

                    {tradeData.setup_description}

                </div>

            </div>

        </div>
    );
}