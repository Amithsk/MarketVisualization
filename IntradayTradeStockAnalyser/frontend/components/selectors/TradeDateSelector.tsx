"use client";

type Props = {

    tradeDates: string[];

    selectedDate: string;

    onSelectDate: (
        tradeDate: string
    ) => void;

    loading?: boolean;
};

export default function TradeDateSelector({

    tradeDates,

    selectedDate,

    onSelectDate,

    loading = false

}: Props) {

    return (

        <div
            className="
                flex
                flex-col
                gap-2
            "
        >

            {/* ---------------------------- */}
            {/* LABEL */}
            {/* ---------------------------- */}

            <label
                className="
                    text-sm
                    text-gray-400
                    font-medium
                "
            >

                Trade Date

            </label>

            {/* ---------------------------- */}
            {/* SELECT */}
            {/* ---------------------------- */}

            <select

                value={selectedDate}

                onChange={(event) =>

                    onSelectDate(
                        event.target.value
                    )
                }

                disabled={loading}

                className="
                    bg-gray-900
                    border
                    border-gray-700
                    rounded-md
                    px-3
                    py-2
                    text-sm
                    text-white
                    min-w-[220px]
                "
            >

                {/* Placeholder */}

                <option value="">

                    Select Trade Date

                </option>

                {/* Trade Dates */}

                {

                    tradeDates.map(
                        (tradeDate) => (

                            <option

                                key={tradeDate}

                                value={tradeDate}

                            >

                                {tradeDate}

                            </option>
                        )
                    )
                }

            </select>

        </div>
    );
}