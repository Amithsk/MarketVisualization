//src/components/step1/Step1Context.tsx
"use client";

import { useEffect, useState } from "react";
import type { TradeDate } from "@/types/common.types";
import type { useStep1 } from "@/hooks/useStep1";
import {
  MarketBias,
  GapContext,
  MARKET_BIAS_VALUES,
  GAP_CONTEXT_VALUES,
} from "@/types/step1.types";

interface Step1ContextProps {
  tradeDate: TradeDate;
  step1: ReturnType<typeof useStep1>;
}

type SystemMarketData = {
  yesterdayClose?: number;
  yesterdayHigh?: number;
  yesterdayLow?: number;
  day2High?: number;
  day2Low?: number;
  preOpenPrice?: number;
  last5DayRanges?: number[];
};

export default function Step1Context({
  tradeDate,
  step1,
}: Step1ContextProps) {
  const {
    snapshot,
    mode,
    derivedContext,
    suggestedMarketContext,
    isFrozen,
    loading,
    error,
    computeStep1,
    freezeStep1,
  } = step1;

  const [marketBias, setMarketBias] =
    useState<MarketBias>("UNDEFINED");
  const [gapContext, setGapContext] =
    useState<GapContext>("UNKNOWN");
  const [notes, setNotes] = useState("");

  const [systemData, setSystemData] =
    useState<SystemMarketData>({});

  /* ------------------------------
     Sync snapshot → local state
  ------------------------------- */
  useEffect(() => {
    if (!snapshot) return;

    setSystemData({
      yesterdayClose: snapshot.yesterdayClose ?? undefined,
      yesterdayHigh: snapshot.yesterdayHigh ?? undefined,
      yesterdayLow: snapshot.yesterdayLow ?? undefined,
      day2High: snapshot.day2High ?? undefined,
      day2Low: snapshot.day2Low ?? undefined,
      preOpenPrice: undefined,
      last5DayRanges: snapshot.last5DayRanges ?? [],
    });
  }, [snapshot]);

  /* Apply system suggestion */
  useEffect(() => {
    if (suggestedMarketContext) {
      setMarketBias(suggestedMarketContext);
    }
  }, [suggestedMarketContext]);

  /* Apply derived gap context */
  useEffect(() => {
    if (derivedContext?.gap_context) {
      setGapContext(
        derivedContext.gap_context as GapContext
      );
    }
  }, [derivedContext]);

  /* ------------------------------
     Actions
  ------------------------------- */

  const handleCompute = () => {
    if (
      systemData.yesterdayClose == null ||
      systemData.yesterdayHigh == null ||
      systemData.yesterdayLow == null ||
      systemData.day2High == null ||
      systemData.day2Low == null ||
      systemData.preOpenPrice == null ||
      !systemData.last5DayRanges ||
      systemData.last5DayRanges.length < 3
    ) {
      return;
    }

    computeStep1({
      yesterdayClose: systemData.yesterdayClose,
      yesterdayHigh: systemData.yesterdayHigh,
      yesterdayLow: systemData.yesterdayLow,
      day2High: systemData.day2High,
      day2Low: systemData.day2Low,
      last5DayRanges: systemData.last5DayRanges,
      preOpenPrice: systemData.preOpenPrice,
    });
  };

  const handleFreeze = () => {
    if (!derivedContext) return;

    freezeStep1({
      marketBias,
      gapContext,
      premarketNotes: notes,
      systemMarketData: {
        yesterdayClose: systemData.yesterdayClose!,
        yesterdayHigh: systemData.yesterdayHigh!,
        yesterdayLow: systemData.yesterdayLow!,
        day2High: systemData.day2High!,
        day2Low: systemData.day2Low!,
        preOpenPrice: systemData.preOpenPrice!,
        last5DayRanges: systemData.last5DayRanges!,
      },
    });
  };

  if (loading) {
    return (
      <div className="text-sm text-gray-500">
        Loading STEP-1…
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="text-sm text-gray-500">
        Pre-Market Context for{" "}
        <span className="font-medium">
          {tradeDate}
        </span>
      </div>

      {/* System Market Data */}
      <Section title="System Market Data">
        <Grid>
          <Field
            label="Yesterday Close"
            value={systemData.yesterdayClose}
            editable={mode === "MANUAL"}
            onChange={(v) =>
              setSystemData((s) => ({
                ...s,
                yesterdayClose: v,
              }))
            }
          />

          <Field
            label="Yesterday High"
            value={systemData.yesterdayHigh}
            editable={mode === "MANUAL"}
            onChange={(v) =>
              setSystemData((s) => ({
                ...s,
                yesterdayHigh: v,
              }))
            }
          />

          <Field
            label="Yesterday Low"
            value={systemData.yesterdayLow}
            editable={mode === "MANUAL"}
            onChange={(v) =>
              setSystemData((s) => ({
                ...s,
                yesterdayLow: v,
              }))
            }
          />

          <Field
            label="Day-2 High"
            value={systemData.day2High}
            editable={mode === "MANUAL"}
            onChange={(v) =>
              setSystemData((s) => ({
                ...s,
                day2High: v,
              }))
            }
          />

          <Field
            label="Day-2 Low"
            value={systemData.day2Low}
            editable={mode === "MANUAL"}
            onChange={(v) =>
              setSystemData((s) => ({
                ...s,
                day2Low: v,
              }))
            }
          />

          <Field
            label="Pre-Open Price"
            value={systemData.preOpenPrice}
            editable={mode === "MANUAL"}
            onChange={(v) =>
              setSystemData((s) => ({
                ...s,
                preOpenPrice: v,
              }))
            }
          />
        </Grid>

        {/* 🔥 Last 5-Day Ranges (RESTORED) */}
        <div className="mt-4">
          <label className="text-xs font-semibold">
            Last 5-Day Ranges (comma separated)
          </label>

          {mode === "MANUAL" ? (
            <input
              type="text"
              value={
                systemData.last5DayRanges?.join(", ") ?? ""
              }
              onChange={(e) =>
                setSystemData((s) => ({
                  ...s,
                  last5DayRanges: e.target.value
                    .split(",")
                    .map((v) => Number(v.trim()))
                    .filter((v) => !Number.isNaN(v)),
                }))
              }
              className="mt-1 w-full rounded border px-2 py-1"
              placeholder="e.g. 120, 140, 95, 110, 130"
            />
          ) : (
            <Readonly
              value={
                systemData.last5DayRanges?.join(", ")
              }
            />
          )}
        </div>

        {mode === "MANUAL" && !derivedContext && (
          <button
            onClick={handleCompute}
            className="mt-4 rounded bg-indigo-600 px-4 py-2 text-sm text-white"
          >
            Compute Market Context
          </button>
        )}
      </Section>

      {/* Derived Context */}
      <Section title="Derived Context">
        {derivedContext ? (
          <Grid>
            {Object.entries(derivedContext).map(
              ([k, v]) => (
                <Readonly
                  key={k}
                  label={k}
                  value={String(v)}
                />
              )
            )}
          </Grid>
        ) : (
          <div className="text-sm text-gray-400">
            Not computed yet
          </div>
        )}
      </Section>

      {/* Final Context */}
      <Section title="Final Market Context">
        {!isFrozen ? (
          <Grid>
            <Select
              label="Market Bias"
              value={marketBias}
              onChange={setMarketBias}
              options={MARKET_BIAS_VALUES}
            />

            <Select
              label="Gap Context"
              value={gapContext}
              onChange={setGapContext}
              options={GAP_CONTEXT_VALUES}
            />

            <TextArea
              label="Notes"
              value={notes}
              onChange={setNotes}
            />
          </Grid>
        ) : (
          <Grid>
            <Readonly
              label="Market Bias"
              value={snapshot?.marketBias}
            />
            <Readonly
              label="Notes"
              value={snapshot?.premarketNotes}
            />
          </Grid>
        )}
      </Section>

      {!isFrozen && derivedContext && (
        <button
          onClick={handleFreeze}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white"
        >
          Freeze STEP-1 Context
        </button>
      )}

      {error && (
        <div className="text-xs text-gray-400">
          Backend unavailable — manual mode enabled
        </div>
      )}
    </div>
  );
}

/* ---------- UI Helpers ---------- */

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded border p-4">
      <h3 className="mb-3 text-sm font-semibold">
        {title}
      </h3>
      {children}
    </div>
  );
}

function Grid({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      {children}
    </div>
  );
}

function Field({
  label,
  value,
  editable,
  onChange,
}: {
  label: string;
  value?: number;
  editable: boolean;
  onChange: (v: number | undefined) => void;
}) {
  return (
    <div>
      <label className="text-xs font-semibold">
        {label}
      </label>
      {editable ? (
        <input
          type="number"
          value={value ?? ""}
          onChange={(e) =>
            onChange(
              e.target.value === ""
                ? undefined
                : Number(e.target.value)
            )
          }
          className="mt-1 w-full rounded border px-2 py-1"
        />
      ) : (
        <Readonly value={value} />
      )}
    </div>
  );
}

function Readonly({
  label,
  value,
}: {
  label?: string;
  value?: string | number | null;
}) {
  return (
    <div>
      {label && (
        <label className="text-xs font-semibold">
          {label}
        </label>
      )}
      <div className="mt-1 rounded border bg-gray-100 px-2 py-1 text-sm">
        {value ?? "--"}
      </div>
    </div>
  );
}

function Select<T extends string>({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: T;
  onChange: (v: T) => void;
  options: readonly T[];
}) {
  return (
    <div>
      <label className="text-xs font-semibold">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) =>
          onChange(e.target.value as T)
        }
        className="mt-1 w-full rounded border px-2 py-1"
      >
        {options.map((v) => (
          <option key={v} value={v}>
            {v}
          </option>
        ))}
      </select>
    </div>
  );
}

function TextArea({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <label className="text-xs font-semibold">
        {label}
      </label>
      <textarea
        value={value}
        onChange={(e) =>
          onChange(e.target.value)
        }
        rows={3}
        className="mt-1 w-full rounded border px-2 py-1"
      />
    </div>
  );
}
