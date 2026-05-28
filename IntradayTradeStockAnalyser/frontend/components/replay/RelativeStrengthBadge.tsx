//IntradayTradeStockAnalyser/frontend/components/replay/RelativeStrengthBadge.tsx

type Props = {

    rsValue: number | null;

    tradable: boolean | null;
};

export default function RelativeStrengthBadge({
    rsValue,
    tradable
}: Props) {

    let title =
        "RS NEUTRAL";

    let badgeColor =
        "bg-gray-700";

    let description =
        "Stock moved in line with market strength.";

    if (
        rsValue !== null
    ) {

        if (rsValue > 0) {

            title =
                "RS STRONG";

            badgeColor =
                "bg-green-700";

            description =
                "Stock showed stronger movement compared to NIFTY.";
        }

        else if (rsValue < 0) {

            title =
                "RS WEAK";

            badgeColor =
                "bg-red-700";

            description =
                "Stock underperformed compared to NIFTY.";
        }
    }

    return (

        <div
            className="
                mb-6
                rounded-lg
                border
                border-gray-800
                bg-gray-900
                p-4
            "
        >

            <div
                className="
                    flex
                    items-center
                    justify-between
                    mb-3
                "
            >

                <div
                    className={`
                        rounded-md
                        px-3
                        py-1
                        text-sm
                        font-semibold
                        text-white
                        ${badgeColor}
                    `}
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
                            tradable
                                ? "bg-green-800"
                                : "bg-red-800"
                        }
                    `}
                >

                    {

                        tradable
                            ? "TRADABLE"
                            : "REJECTED"
                    }

                </div>

            </div>

            <div
                className="
                    mb-2
                    text-sm
                    text-gray-300
                "
            >

                {description}

            </div>

            <div
                className="
                    text-xs
                    text-gray-500
                "
            >

                Relative Strength Value:

                {" "}

                {

                    rsValue !== null

                        ? rsValue.toFixed(2)

                        : "N/A"
                }

            </div>

        </div>
    );
}