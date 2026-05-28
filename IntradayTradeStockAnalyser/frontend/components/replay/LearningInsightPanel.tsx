//IntradayTradeStockAnalyser/frontend/components/replay/LearningInsightPanel.tsx

type Props = {

    learningInsight: string | null;

    executionSummary: string | null;

    tradeConstructionSummary: string | null;
};

export default function LearningInsightPanel({
    learningInsight,
    executionSummary,
    tradeConstructionSummary
}: Props) {

    return (

        <div
            className="
                mb-6
                rounded-lg
                border
                border-blue-900
                bg-blue-950/30
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
                    text-blue-300
                "
            >

                Learning Insight

            </div>

            <div
                className="
                    mb-4
                    text-sm
                    leading-relaxed
                    text-gray-200
                "
            >

                {

                    learningInsight ||

                    "No learning insight available."
                }

            </div>

            <div
                className="
                    mb-3
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

                    Execution Context

                </div>

                <div
                    className="
                        text-xs
                        leading-relaxed
                        text-gray-400
                    "
                >

                    {

                        executionSummary ||

                        "Execution summary unavailable."
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

                    Trade Construction

                </div>

                <div
                    className="
                        text-xs
                        leading-relaxed
                        text-gray-400
                    "
                >

                    {

                        tradeConstructionSummary ||

                        "Trade construction summary unavailable."
                    }

                </div>

            </div>

        </div>
    );
}