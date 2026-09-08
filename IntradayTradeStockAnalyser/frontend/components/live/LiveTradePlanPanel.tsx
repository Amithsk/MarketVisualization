"use client";

import {
    useMemo,
    useState,
} from "react";

import type {
    ReactNode,
} from "react";

import { Candle } from "../../types/candle";

type Direction = "LONG" | "SHORT";
export type TradePlanStatus = "ACTIVE" | "CANCELLED" | "EXECUTED" | "EXITED";

type TradePlanDraft = {
    direction: Direction;
    strategy: string;
    entry: string;
    stopLoss: string;
    target1: string;
    target2: string;
    positionSize: string;
    why: string;
    invalidation: string;
    entryConfirmation: string;
};

export type LiveTradePlan = TradePlanDraft & {
    id: string;
    symbol: string;
    decisionTime: string;
    status: TradePlanStatus;
    cancelledAt?: string;
    executedAt?: string;
    exitedAt?: string;
};

type Props = {
    selectedCandle: Candle | null;
    stockName: string;
    plans: LiveTradePlan[];
    onPlansChange: (plans: LiveTradePlan[]) => void;
};

const STRATEGIES = [
    "ORB Breakout",
    "ORB Breakdown",
    "VWAP Bounce",
    "VWAP Rejection",
    "Pullback",
    "Support / Resistance",
];

function formatPrice(value: number): string {

    if (!Number.isFinite(value)) {
        return "";
    }

    return value.toFixed(2);
}

function createDraftFromCandle(candle: Candle): TradePlanDraft {

    const entry = Number(candle.close);
    const candleRange = Math.abs(
        Number(candle.high) - Number(candle.low)
    );
    const defaultRisk = Math.max(
        candleRange,
        Math.abs(entry) * 0.001,
        0.05
    );

    return {
        direction: "LONG",
        strategy: STRATEGIES[0],
        entry: formatPrice(entry),
        stopLoss: formatPrice(entry - defaultRisk),
        target1: formatPrice(entry + defaultRisk),
        target2: formatPrice(entry + defaultRisk * 2),
        positionSize: "1",
        why: "",
        invalidation: "",
        entryConfirmation: "",
    };
}

function parseNumber(value: string): number | null {

    if (!value.trim()) {
        return null;
    }

    const parsed = Number(value);

    return Number.isFinite(parsed) ? parsed : null;
}

function formatCalculation(value: number | null): string {

    if (value === null || !Number.isFinite(value)) {
        return "-";
    }

    return value.toFixed(2);
}

export default function LiveTradePlanPanel({
    selectedCandle,
    stockName,
    plans,
    onPlansChange,
}: Props) {

    const [draft, setDraft] =
        useState<TradePlanDraft | null>(null);

    const [selectedPlanId, setSelectedPlanId] =
        useState<string | null>(null);

    const [isDrawerOpen, setIsDrawerOpen] =
        useState(false);

    const activePlan =
        plans.find((plan) =>
            plan.symbol === stockName &&
            (
                plan.status === "ACTIVE" ||
                plan.status === "EXECUTED"
            )
        ) || null;

    const selectedPlan =
        plans.find((plan) => plan.id === selectedPlanId) || null;

    const decisionTime =
        selectedPlan?.decisionTime ||
        selectedCandle?.time ||
        "";

    const visibleDraft =
        draft || selectedPlan;

    const calculations =
        useMemo(() => {
            if (!visibleDraft) {
                return {
                    riskPerPoint: null,
                    rewardT1: null,
                    riskReward: null,
                };
            }

            const entry = parseNumber(visibleDraft.entry);
            const stopLoss = parseNumber(visibleDraft.stopLoss);
            const target1 = parseNumber(visibleDraft.target1);

            if (
                entry === null ||
                stopLoss === null ||
                target1 === null
            ) {
                return {
                    riskPerPoint: null,
                    rewardT1: null,
                    riskReward: null,
                };
            }

            const riskPerPoint = Math.abs(entry - stopLoss);
            const rewardT1 = Math.abs(target1 - entry);

            return {
                riskPerPoint,
                rewardT1,
                riskReward:
                    riskPerPoint > 0
                        ? rewardT1 / riskPerPoint
                        : null,
            };
        }, [visibleDraft]);

    const updateDraft = (
        field: keyof TradePlanDraft,
        value: string
    ) => {
        if (!visibleDraft) {
            return;
        }

        const nextDraft = {
            ...visibleDraft,
            [field]: value,
        };

        if (draft) {
            setDraft(nextDraft);
        }

        if (selectedPlan) {
            onPlansChange(
                plans.map((plan) =>
                    plan.id === selectedPlan.id
                        ? {
                            ...plan,
                            ...nextDraft,
                        }
                        : plan
                )
            );
        }
    };

    const handleCreatePlan = () => {
        if (!selectedCandle || activePlan) {
            return;
        }

        setSelectedPlanId(null);
        setDraft(
            createDraftFromCandle(selectedCandle)
        );
        setIsDrawerOpen(true);
    };

    const handleSavePlan = () => {
        if (!selectedCandle || !draft || activePlan) {
            return;
        }

        const requiredNumbers = [
            draft.entry,
            draft.stopLoss,
            draft.target1,
            draft.target2,
            draft.positionSize,
        ];

        if (
            requiredNumbers.some(
                (value) => parseNumber(value) === null
            )
        ) {
            return;
        }

        const nextPlan: LiveTradePlan = {
            ...draft,
            id: `${Date.now()}`,
            symbol: stockName,
            decisionTime: selectedCandle.time,
            status: "ACTIVE",
        };

        onPlansChange([
            nextPlan,
            ...plans,
        ]);
        setSelectedPlanId(nextPlan.id);
        setDraft(null);
    };

    const updateStatus = (
        nextStatus: TradePlanStatus
    ) => {
        if (!selectedPlan) {
            return;
        }

        const actionTime =
            selectedCandle?.time ||
            new Date().toISOString();

        onPlansChange(
            plans.map((plan) => {
                if (plan.id !== selectedPlan.id) {
                    return plan;
                }

                if (
                    nextStatus === "CANCELLED" &&
                    plan.status !== "ACTIVE"
                ) {
                    return plan;
                }

                if (
                    nextStatus === "EXECUTED" &&
                    plan.status !== "ACTIVE"
                ) {
                    return plan;
                }

                if (
                    nextStatus === "EXITED" &&
                    plan.status !== "EXECUTED"
                ) {
                    return plan;
                }

                return {
                    ...plan,
                    status: nextStatus,
                    cancelledAt:
                        nextStatus === "CANCELLED"
                            ? actionTime
                            : plan.cancelledAt,
                    executedAt:
                        nextStatus === "EXECUTED"
                            ? actionTime
                            : plan.executedAt,
                    exitedAt:
                        nextStatus === "EXITED"
                            ? actionTime
                            : plan.exitedAt,
                };
            })
        );
    };

    return (
        <div
            className="
                mt-6
                rounded-md
                border
                border-gray-800
                bg-gray-900
                p-4
                text-sm
                text-gray-300
            "
        >
            <div
                className="
                    mb-4
                    flex
                    flex-wrap
                    items-center
                    justify-between
                    gap-3
                "
            >
                <div>
                    <div
                        className="
                            text-base
                            font-semibold
                            text-white
                        "
                    >
                        Trade Plan
                    </div>
                    <div className="text-xs text-gray-500">
                        Select a stock candle, then record the trade idea.
                    </div>
                </div>

                <button
                    type="button"
                    onClick={handleCreatePlan}
                    disabled={!selectedCandle || Boolean(activePlan)}
                    className="
                        rounded
                        bg-cyan-500
                        px-4
                        py-2
                        font-semibold
                        text-gray-950
                        disabled:cursor-not-allowed
                        disabled:opacity-40
                    "
                >
                    Create Trade Plan
                </button>
            </div>

            {!selectedCandle && (
                <div className="mb-4 text-xs text-gray-500">
                    Select a Stock candle to enable Trade Plan creation.
                </div>
            )}

            {activePlan && !draft && (
                <div className="mb-4 text-xs text-amber-300">
                    Resolve the current active/executed plan before creating another one.
                </div>
            )}

            {isDrawerOpen && visibleDraft && (
                <div
                    className="
                        fixed
                        bottom-4
                        right-4
                        top-24
                        z-50
                        flex
                        w-[min(28rem,calc(100vw-2rem))]
                        max-w-full
                        flex-col
                        overflow-y-auto
                        rounded-lg
                        border
                        border-gray-700
                        bg-gray-900
                        p-4
                        shadow-2xl
                    "
                >
                    <div
                        className="
                            mb-4
                            flex
                            items-start
                            justify-between
                            gap-3
                        "
                    >
                        <div>
                            <div
                                className="
                                    text-base
                                    font-semibold
                                    text-white
                                "
                            >
                                Trade Plan
                            </div>
                            <div className="text-xs text-gray-500">
                                Existing plan workflow for the selected stock candle.
                            </div>
                        </div>

                        <button
                            type="button"
                            onClick={() => setIsDrawerOpen(false)}
                            className="
                                rounded
                                border
                                border-gray-700
                                px-2
                                py-1
                                text-xs
                                text-gray-200
                            "
                        >
                            Close
                        </button>
                    </div>

                    <div className="grid gap-4">
                    <div className="space-y-3">
                        <Field label="Decision Time">
                            <div className="text-white">
                                {decisionTime || "-"}
                            </div>
                        </Field>

                        <label className="block">
                            <span className="text-xs text-gray-500">
                                Direction
                            </span>
                            <select
                                value={visibleDraft.direction}
                                onChange={(event) =>
                                    updateDraft(
                                        "direction",
                                        event.target.value as Direction
                                    )
                                }
                                className={inputClassName}
                            >
                                <option value="LONG">LONG</option>
                                <option value="SHORT">SHORT</option>
                            </select>
                        </label>

                        <label className="block">
                            <span className="text-xs text-gray-500">
                                Strategy
                            </span>
                            <select
                                value={visibleDraft.strategy}
                                onChange={(event) =>
                                    updateDraft(
                                        "strategy",
                                        event.target.value
                                    )
                                }
                                className={inputClassName}
                            >
                                {STRATEGIES.map((strategy) => (
                                    <option
                                        key={strategy}
                                        value={strategy}
                                    >
                                        {strategy}
                                    </option>
                                ))}
                            </select>
                        </label>

                        <div className="grid grid-cols-2 gap-3">
                            <NumberField
                                label="Entry"
                                value={visibleDraft.entry}
                                onChange={(value) =>
                                    updateDraft("entry", value)
                                }
                            />
                            <NumberField
                                label="Stop Loss"
                                value={visibleDraft.stopLoss}
                                onChange={(value) =>
                                    updateDraft("stopLoss", value)
                                }
                            />
                            <NumberField
                                label="Target 1"
                                value={visibleDraft.target1}
                                onChange={(value) =>
                                    updateDraft("target1", value)
                                }
                            />
                            <NumberField
                                label="Target 2"
                                value={visibleDraft.target2}
                                onChange={(value) =>
                                    updateDraft("target2", value)
                                }
                            />
                        </div>

                        <NumberField
                            label="Position Size"
                            value={visibleDraft.positionSize}
                            onChange={(value) =>
                                updateDraft("positionSize", value)
                            }
                        />
                    </div>

                    <div className="space-y-3">
                        <TextAreaField
                            label="Why am I selecting this trade?"
                            value={visibleDraft.why}
                            onChange={(value) =>
                                updateDraft("why", value)
                            }
                        />
                        <TextAreaField
                            label="What invalidates this trade?"
                            value={visibleDraft.invalidation}
                            onChange={(value) =>
                                updateDraft("invalidation", value)
                            }
                        />
                        <TextAreaField
                            label="Entry confirmation"
                            value={visibleDraft.entryConfirmation}
                            onChange={(value) =>
                                updateDraft("entryConfirmation", value)
                            }
                        />

                        <div
                            className="
                                grid
                                grid-cols-3
                                gap-3
                                rounded
                                border
                                border-gray-800
                                bg-gray-950
                                p-3
                            "
                        >
                            <Metric
                                label="Risk / point"
                                value={formatCalculation(
                                    calculations.riskPerPoint
                                )}
                            />
                            <Metric
                                label="Reward T1"
                                value={formatCalculation(
                                    calculations.rewardT1
                                )}
                            />
                            <Metric
                                label="Risk : Reward"
                                value={formatCalculation(
                                    calculations.riskReward
                                )}
                            />
                        </div>

                        {draft && (
                            <button
                                type="button"
                                onClick={handleSavePlan}
                                className="
                                    rounded
                                    bg-green-500
                                    px-4
                                    py-2
                                    font-semibold
                                    text-gray-950
                                "
                            >
                                Save Plan
                            </button>
                        )}

                        {selectedPlan && (
                            <div className="flex flex-wrap gap-2">
                                <StatusButton
                                    disabled={selectedPlan.status !== "ACTIVE"}
                                    onClick={() => updateStatus("CANCELLED")}
                                >
                                    Cancel Trade Plan
                                </StatusButton>
                                <StatusButton
                                    disabled={selectedPlan.status !== "ACTIVE"}
                                    onClick={() => updateStatus("EXECUTED")}
                                >
                                    Execute Trade
                                </StatusButton>
                                <StatusButton
                                    disabled={selectedPlan.status !== "EXECUTED"}
                                    onClick={() => updateStatus("EXITED")}
                                >
                                    Exit Trade
                                </StatusButton>
                            </div>
                        )}
                    </div>
                    </div>
                </div>
            )}

            {plans.length > 0 && (
                <div className="mt-5">
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
                        Plans
                    </div>
                    <div className="space-y-2">
                        {plans.map((plan) => (
                            <button
                                key={plan.id}
                                type="button"
                                onClick={() => {
                                    setDraft(null);
                                    setSelectedPlanId(plan.id);
                                    setIsDrawerOpen(true);
                                }}
                                className="
                                    grid
                                    w-full
                                    grid-cols-6
                                    gap-2
                                    rounded
                                    border
                                    border-gray-800
                                    bg-gray-950
                                    px-3
                                    py-2
                                    text-left
                                    text-xs
                                    text-gray-300
                                "
                            >
                                <span>{plan.decisionTime.slice(11, 16)}</span>
                                <span>{plan.direction}</span>
                                <span>{plan.strategy}</span>
                                <span>Entry {plan.entry}</span>
                                <span>Stop {plan.stopLoss}</span>
                                <span className="text-white">{plan.status}</span>
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

const inputClassName = `
    mt-1
    w-full
    rounded
    border
    border-gray-700
    bg-gray-950
    px-3
    py-2
    text-sm
    text-white
`;

function Field({
    label,
    children,
}: {
    label: string;
    children: ReactNode;
}) {
    return (
        <div>
            <div className="text-xs text-gray-500">
                {label}
            </div>
            {children}
        </div>
    );
}

function NumberField({
    label,
    value,
    onChange,
}: {
    label: string;
    value: string;
    onChange: (value: string) => void;
}) {
    return (
        <label className="block">
            <span className="text-xs text-gray-500">
                {label}
            </span>
            <input
                type="number"
                value={value}
                onChange={(event) => onChange(event.target.value)}
                className={inputClassName}
            />
        </label>
    );
}

function TextAreaField({
    label,
    value,
    onChange,
}: {
    label: string;
    value: string;
    onChange: (value: string) => void;
}) {
    return (
        <label className="block">
            <span className="text-xs text-gray-500">
                {label}
            </span>
            <textarea
                value={value}
                onChange={(event) => onChange(event.target.value)}
                rows={3}
                className={inputClassName}
            />
        </label>
    );
}

function Metric({
    label,
    value,
}: {
    label: string;
    value: string;
}) {
    return (
        <div>
            <div className="text-xs text-gray-500">
                {label}
            </div>
            <div className="text-sm font-semibold text-white">
                {value}
            </div>
        </div>
    );
}

function StatusButton({
    disabled,
    onClick,
    children,
}: {
    disabled: boolean;
    onClick: () => void;
    children: ReactNode;
}) {
    return (
        <button
            type="button"
            disabled={disabled}
            onClick={onClick}
            className="
                rounded
                border
                border-gray-700
                px-3
                py-2
                text-xs
                text-gray-200
                disabled:cursor-not-allowed
                disabled:opacity-40
            "
        >
            {children}
        </button>
    );
}
