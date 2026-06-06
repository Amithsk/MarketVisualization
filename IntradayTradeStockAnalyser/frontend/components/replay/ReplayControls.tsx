// IntradayTradeStockAnalyser/frontend/components/replay/ReplayControls.tsx

"use client";

type Props = {

    isPlaying: boolean;

    playbackSpeed: number;

    replayProgress: number;

    currentCandleIndex: number;

    totalCandles: number;

    onPlay: () => void;

    onPause: () => void;

    onReset: () => void;

    onNext: () => void;

    onPrevious: () => void;

    onSpeedChange: (
        speed: 0.5 | 1 | 2 | 4
    ) => void;
};

export default function ReplayControls({

    isPlaying,

    playbackSpeed,

    replayProgress,

    currentCandleIndex,

    totalCandles,

    onPlay,

    onPause,

    onReset,

    onNext,

    onPrevious,

    onSpeedChange,

}: Props) {

    return (

        <div
            className="
                w-full
                rounded-xl
                border
                border-zinc-800
                bg-zinc-950
                p-4
                flex
                flex-col
                gap-4
            "
        >

            {/* ================================= */}
            {/* TOP SECTION */}
            {/* ================================= */}

            <div
                className="
                    flex
                    flex-wrap
                    items-center
                    justify-between
                    gap-4
                "
            >

                {/* ============================= */}
                {/* PLAYBACK BUTTONS */}
                {/* ============================= */}

                <div
                    className="
                        flex
                        items-center
                        gap-2
                    "
                >

                    {/* PLAY / PAUSE */}

                    {
                        isPlaying ? (

                            <button
                                onClick={onPause}
                                className="
                                    px-4
                                    py-2
                                    rounded-lg
                                    bg-red-600
                                    hover:bg-red-500
                                    text-white
                                    font-medium
                                    transition
                                "
                            >
                                Pause
                            </button>

                        ) : (

                            <button
                                onClick={onPlay}
                                className="
                                    px-4
                                    py-2
                                    rounded-lg
                                    bg-green-600
                                    hover:bg-green-500
                                    text-white
                                    font-medium
                                    transition
                                "
                            >
                                Play
                            </button>
                        )
                    }

                    {/* PREVIOUS */}

                    <button
                        onClick={onPrevious}
                        className="
                            px-4
                            py-2
                            rounded-lg
                            bg-zinc-800
                            hover:bg-zinc-700
                            text-white
                            transition
                        "
                    >
                        ◀ Prev
                    </button>

                    {/* NEXT */}

                    <button
                        onClick={onNext}
                        className="
                            px-4
                            py-2
                            rounded-lg
                            bg-zinc-800
                            hover:bg-zinc-700
                            text-white
                            transition
                        "
                    >
                        Next ▶
                    </button>

                    {/* RESET */}

                    <button
                        onClick={onReset}
                        className="
                            px-4
                            py-2
                            rounded-lg
                            bg-zinc-800
                            hover:bg-zinc-700
                            text-white
                            transition
                        "
                    >
                        Reset
                    </button>

                </div>

                {/* ============================= */}
                {/* SPEED CONTROLS */}
                {/* ============================= */}

                <div
                    className="
                        flex
                        items-center
                        gap-2
                    "
                >

                    <div
                        className="
                            text-sm
                            text-zinc-400
                        "
                    >
                        Speed
                    </div>

                    {
                        [0.5, 1, 2, 4].map((speed) => (

                            <button
                                key={speed}
                                onClick={() =>
                                    onSpeedChange(
                                        speed as
                                        0.5 | 1 | 2 | 4
                                    )
                                }
                                className={`
                                    px-3
                                    py-1
                                    rounded-md
                                    text-sm
                                    transition

                                    ${
                                        playbackSpeed === speed
                                            ? `
                                                bg-cyan-600
                                                text-white
                                            `
                                            : `
                                                bg-zinc-800
                                                text-zinc-300
                                                hover:bg-zinc-700
                                            `
                                    }
                                `}
                            >
                                {speed}x
                            </button>
                        ))
                    }

                </div>

            </div>

            {/* ================================= */}
            {/* PROGRESS SECTION */}
            {/* ================================= */}

            <div
                className="
                    flex
                    flex-col
                    gap-2
                "
            >

                {/* ============================= */}
                {/* REPLAY INFO */}
                {/* ============================= */}

                <div
                    className="
                        flex
                        justify-between
                        text-sm
                        text-zinc-400
                    "
                >

                    <div>

                        Candle:

                        {" "}

                        <span className="text-white">

                            {currentCandleIndex + 1}

                        </span>

                        {" / "}

                        <span className="text-white">

                            {totalCandles}

                        </span>

                    </div>

                    <div>

                        {replayProgress.toFixed(1)}%

                    </div>

                </div>

                {/* ============================= */}
                {/* PROGRESS BAR */}
                {/* ============================= */}

                <div
                    className="
                        w-full
                        h-3
                        rounded-full
                        bg-zinc-800
                        overflow-hidden
                    "
                >

                    <div
                        className="
                            h-full
                            bg-cyan-500
                            transition-all
                            duration-200
                        "
                        style={{
                            width:
                                `${replayProgress}%`
                        }}
                    />

                </div>

            </div>

        </div>
    );
}