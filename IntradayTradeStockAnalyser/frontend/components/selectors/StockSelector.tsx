"use client";

type Props = {

    stocks: string[];

    selectedStock: string;

    onSelectStock: (
        stock: string
    ) => void;

    disabled?: boolean;

    loading?: boolean;
};

export default function StockSelector({

    stocks,

    selectedStock,

    onSelectStock,

    disabled = false,

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

                Stock

            </label>

            {/* ---------------------------- */}
            {/* SELECT */}
            {/* ---------------------------- */}

            <select

                value={selectedStock}

                onChange={(event) =>

                    onSelectStock(
                        event.target.value
                    )
                }

                disabled={
                    disabled ||
                    loading
                }

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

                    Select Stock

                </option>

                {/* Stocks */}

                {

                    stocks.map(
                        (stock) => (

                            <option

                                key={stock}

                                value={stock}

                            >

                                {stock}

                            </option>
                        )
                    )
                }

            </select>

        </div>
    );
}