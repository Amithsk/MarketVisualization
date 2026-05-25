"use client";

import {

    useEffect,

    useState

} from "react";

import {

    fetchTradeDates,

    fetchTradeStocks

} from "../services/tradeApi";

export function useTradeSelection() {

    // -----------------------------------
    // Trade dates
    // -----------------------------------

    const [tradeDates, setTradeDates] =
        useState<string[]>([]);

    const [selectedDate, setSelectedDate] =
        useState("");

    // -----------------------------------
    // Stocks
    // -----------------------------------

    const [stocks, setStocks] =
        useState<string[]>([]);

    const [selectedStock, setSelectedStock] =
        useState("");

    // -----------------------------------
    // Loading
    // -----------------------------------

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState<string | null>(null);

    // -----------------------------------
    // Load trade dates
    // -----------------------------------

    useEffect(() => {

        loadTradeDates();

    }, []);

    const loadTradeDates = async () => {

        try {

            setLoading(true);

            setError(null);

            const dates =
                await fetchTradeDates();

            setTradeDates(dates);

        } catch (err: any) {

            console.error(err);

            setError(
                err.message ||
                "Failed to load trade dates"
            );

        } finally {

            setLoading(false);
        }
    };

    // -----------------------------------
    // Load stocks for selected date
    // -----------------------------------

    const selectTradeDate = async (
        tradeDate: string
    ) => {

        try {

            setSelectedDate(tradeDate);

            setSelectedStock("");

            setStocks([]);

            setLoading(true);

            setError(null);

            const fetchedStocks =
                await fetchTradeStocks(
                    tradeDate
                );

            setStocks(
                fetchedStocks
            );

        } catch (err: any) {

            console.error(err);

            setError(
                err.message ||
                "Failed to load stocks"
            );

        } finally {

            setLoading(false);
        }
    };

    return {

        // Dates

        tradeDates,

        selectedDate,

        selectTradeDate,

        // Stocks

        stocks,

        selectedStock,

        setSelectedStock,

        // State

        loading,

        error
    };
}