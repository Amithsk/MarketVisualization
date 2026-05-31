// IntradayTradeStockAnalyser/frontend/hooks/useReplayPlayback.ts

"use client";

import {
    useCallback,
    useEffect,
    useMemo,
    useRef,
    useState,
} from "react";

type UseReplayPlaybackProps = {

    totalCandles: number;
};

type ReplaySpeed = 0.5 | 1 | 2 | 4;

export default function useReplayPlayback({
    totalCandles,
}: UseReplayPlaybackProps) {

    // ============================================
    // CORE REPLAY STATE
    // ============================================

    const [
        currentCandleIndex,
        setCurrentCandleIndex,
    ] = useState(0);

    const [
        isPlaying,
        setIsPlaying,
    ] = useState(false);

    const [
        playbackSpeed,
        setPlaybackSpeed,
    ] = useState<ReplaySpeed>(1);

    // ============================================
    // INTERNAL TIMER REF
    // ============================================

    const playbackIntervalRef =
        useRef<NodeJS.Timeout | null>(null);

    // ============================================
    // PLAYBACK INTERVAL
    // ============================================

    const playbackIntervalMs = useMemo(() => {

        switch (playbackSpeed) {

            case 0.5:
                return 1200;

            case 1:
                return 700;

            case 2:
                return 350;

            case 4:
                return 180;

            default:
                return 700;
        }

    }, [playbackSpeed]);

    // ============================================
    // PLAY
    // ============================================

    const play = useCallback(() => {

        if (totalCandles <= 0) {
            return;
        }

        setIsPlaying(true);

    }, [totalCandles]);

    // ============================================
    // PAUSE
    // ============================================

    const pause = useCallback(() => {

        setIsPlaying(false);

    }, []);

    // ============================================
    // RESET
    // ============================================

    const reset = useCallback(() => {

        setIsPlaying(false);

        setCurrentCandleIndex(0);

    }, []);

    // ============================================
    // NEXT CANDLE
    // ============================================

    const nextCandle = useCallback(() => {

        setCurrentCandleIndex((prev) => {

            if (prev >= totalCandles - 1) {

                return prev;
            }

            return prev + 1;
        });

    }, [totalCandles]);

    // ============================================
    // PREVIOUS CANDLE
    // ============================================

    const previousCandle = useCallback(() => {

        setCurrentCandleIndex((prev) => {

            if (prev <= 0) {

                return 0;
            }

            return prev - 1;
        });

    }, []);

    // ============================================
    // JUMP TO CANDLE
    // ============================================

    const jumpToCandle = useCallback((
        candleIndex: number
    ) => {

        if (candleIndex < 0) {

            setCurrentCandleIndex(0);

            return;
        }

        if (candleIndex >= totalCandles) {

            setCurrentCandleIndex(
                totalCandles - 1
            );

            return;
        }

        setCurrentCandleIndex(candleIndex);

    }, [totalCandles]);

    // ============================================
    // PLAYBACK LOOP
    // ============================================

    useEffect(() => {

        if (!isPlaying) {

            if (playbackIntervalRef.current) {

                clearInterval(
                    playbackIntervalRef.current
                );

                playbackIntervalRef.current = null;
            }

            return;
        }

        playbackIntervalRef.current = setInterval(() => {

            setCurrentCandleIndex((prev) => {

                // ====================================
                // STOP AT FINAL CANDLE
                // ====================================

                if (prev >= totalCandles - 1) {

                    setIsPlaying(false);

                    return prev;
                }

                return prev + 1;
            });

        }, playbackIntervalMs);

        return () => {

            if (playbackIntervalRef.current) {

                clearInterval(
                    playbackIntervalRef.current
                );

                playbackIntervalRef.current = null;
            }
        };

    }, [
        isPlaying,
        playbackIntervalMs,
        totalCandles,
    ]);

    // ============================================
    // CLEANUP ON UNMOUNT
    // ============================================

    useEffect(() => {

        return () => {

            if (playbackIntervalRef.current) {

                clearInterval(
                    playbackIntervalRef.current
                );
            }
        };

    }, []);

    // ============================================
    // REPLAY COMPLETION
    // ============================================

    const isReplayComplete =
        currentCandleIndex >= totalCandles - 1;

    // ============================================
    // PROGRESS %
    // ============================================

    const replayProgress = useMemo(() => {

        if (totalCandles <= 0) {

            return 0;
        }

        return (
            (
                currentCandleIndex /
                (totalCandles - 1)
            ) * 100
        );

    }, [
        currentCandleIndex,
        totalCandles,
    ]);

    // ============================================
    // EXPOSE PUBLIC API
    // ============================================

    return {

        // replay state
        currentCandleIndex,
        isPlaying,
        playbackSpeed,
        isReplayComplete,
        replayProgress,

        // state setters
        setPlaybackSpeed,

        // controls
        play,
        pause,
        reset,
        nextCandle,
        previousCandle,
        jumpToCandle,
    };
}