//IntradayTradeStockAnalyser/frontend/components/replay/TradePermissionBanner.tsx

type Props = {

    tradePermission: string | null;

    executionAllowed: boolean | null;
};

export default function TradePermissionBanner({
    tradePermission,
    executionAllowed
}: Props) {

    let bgColor =
        "bg-gray-800";

    let borderColor =
        "border-gray-700";

    let title =
        "UNKNOWN MARKET STATE";

    let description =
        "Trade permission information unavailable.";

    if (
        tradePermission === "YES"
    ) {

        bgColor =
            "bg-green-950";

        borderColor =
            "border-green-700";

        title =
            "TRADE ALLOWED";

        description =
            "Market conditions supported active intraday execution.";
    }

    else if (
        tradePermission === "LIMITED"
    ) {

        bgColor =
            "bg-yellow-950";

        borderColor =
            "border-yellow-700";

        title =
            "LIMITED TRADING";

        description =
            "Market conditions required selective and cautious execution.";
    }

    else if (
        tradePermission === "NO"
    ) {

        bgColor =
            "bg-red-950";

        borderColor =
            "border-red-700";

        title =
            "NO TRADE";

        description =
            "Market structure did not support safe intraday execution.";
    }

    return (

        <div
            className={`
                mb-6
                rounded-lg
                border
                p-4
                ${bgColor}
                ${borderColor}
            `}
        >

            <div
                className="
                    flex
                    items-center
                    justify-between
                    mb-2
                "
            >

                <div
                    className="
                        text-sm
                        font-bold
                        tracking-wide
                        text-white
                    "
                >

                    {title}

                </div>

                <div
                    className={`
                        rounded-md
                        px-2
                        py-1
                        text-xs
                        font-semibold
                        text-white
                        ${
                            executionAllowed
                                ? "bg-green-700"
                                : "bg-red-700"
                        }
                    `}
                >

                    {

                        executionAllowed
                            ? "EXECUTION ENABLED"
                            : "EXECUTION BLOCKED"
                    }

                </div>

            </div>

            <div
                className="
                    text-sm
                    leading-relaxed
                    text-gray-300
                "
            >

                {description}

            </div>

        </div>
    );
}