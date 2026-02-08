//frontend/src/components/step1/Step1Context.tsx
"use client";

import { useEffect, useState } from "react";
import { useStep1 } from "@/hooks/useStep1";
import type { TradeDate } from "@/types/common.types";
import {
  MarketBias,
  GapContext,
  MARKET_BIAS_VALUES,
  GAP_CONTEXT_VALUES,
} from "@/types/step1.types";

interface Step1ContextProps {
  tradeDate: TradeDate;
}

type SystemMarketData = {
  yesterdayClose?: number;
  yesterdayHigh?: number;
  yesterdayLow?: number;
  day2High?: number;
  day2Low?: number;
  preOpenPrice?: number;
};

export default function Step1Context({ tradeDate }: Step1ContextProps) {
  const {
    snapshot,
    mode,
    isFrozen,
    loading,
    error,
    previewStep1,
    freezeStep1,
  } = useStep1(tradeDate);

  const [marketBias, setMarketBias] =
    useState<MarketBias>("UNDEFINED");
  const [gapContext, setGapContext] =
    useState<GapContext>("UNKNOWN");
  const [notes, setNotes] = useState("");

  // 🔒 System Market Data (captured in MANUAL mode)
  const [systemData, setSystemData] =
    useState<SystemMarketData>({});

  useEffect(() => {
    previewStep1();
  }, [previewStep1]);

  // Sync snapshot → local system data (AUTO or first MANUAL load)
  useEffect(() => {
    if (snapshot) {
      const next = {
        yesterdayClose: snapshot.yesterdayClose,
        yesterdayHigh: snapshot.yesterdayHigh,
        yesterdayLow: snapshot.yesterdayLow,
        day2High: snapshot.day2High,
        day2Low: snapshot.day2Low,
        preOpenPrice: snapshot.preOpenPrice,
      };

      console.log("[DEBUG][STEP-1][SYSTEM-DATA] sync from snapshot", next);
      setSystemData(next);
    }
  }, [snapshot]);

  const handleFreeze = () => {
    console.log("[DEBUG][STEP-1][FREEZE][UI] submitting", {
      marketBias,
      gapContext,
      notes,
      systemData,
    });

    freezeStep1({
      marketBias,
      gapContext,
      premarketNotes: notes,
      preOpenPrice: systemData.preOpenPrice,
      systemMarketData: {
        yesterdayClose: systemData.yesterdayClose,
        yesterdayHigh: systemData.yesterdayHigh,
        yesterdayLow: systemData.yesterdayLow,
        day2High: systemData.day2High,
        day2Low: systemData.day2Low,
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
        <span className="font-medium">{tradeDate}</span>
      </div>

      {/* ===================================================== */}
      {/* 1️⃣ SYSTEM MARKET DATA — EDITABLE IN MANUAL */}
      {/* ===================================================== */}
      <Section title="System Market Data">
        <Grid>
          <Field
            label="Yesterday Close"
            value={systemData.yesterdayClose}
            editable={mode === "MANUAL"}
            onBlur={(v) =>
              setSystemData((s) => ({ ...s, yesterdayClose: v }))
            }
          />
          <Field
            label="Yesterday High"
            value={systemData.yesterdayHigh}
            editable={mode === "MANUAL"}
            onBlur={(v) =>
              setSystemData((s) => ({ ...s, yesterdayHigh: v }))
            }
          />
          <Field
            label="Yesterday Low"
            value={systemData.yesterdayLow}
            editable={mode === "MANUAL"}
            onBlur={(v) =>
              setSystemData((s) => ({ ...s, yesterdayLow: v }))
            }
          />
          <Field
            label="Day-2 High"
            value={systemData.day2High}
            editable={mode === "MANUAL"}
            onBlur={(v) =>
              setSystemData((s) => ({ ...s, day2High: v }))
            }
          />
          <Field
            label="Day-2 Low"
            value={systemData.day2Low}
            editable={mode === "MANUAL"}
            onBlur={(v) =>
              setSystemData((s) => ({ ...s, day2Low: v }))
            }
          />
        </Grid>
      </Section>

      {/* ===================================================== */}
      {/* 2️⃣ PRE-OPEN INPUT */}
      {/* ===================================================== */}
      <Section title="Pre-Open Input">
        <Field
          label="Pre-Open Price"
          value={systemData.preOpenPrice}
          editable={mode === "MANUAL"}
          onBlur={(v) =>
            setSystemData((s) => ({ ...s, preOpenPrice: v }))
          }
        />
      </Section>

      {/* ===================================================== */}
      {/* 3️⃣ DERIVED CONTEXT (READ-ONLY) */}
      {/* ===================================================== */}
      <Section title="Derived Context (System)">
        <Grid>
          <Readonly label="Gap %" value={snapshot?.gapPct} />
          <Readonly label="Gap Class" value={snapshot?.gapClass} />
          <Readonly label="Range Ratio" value={snapshot?.rangeRatio} />
          <Readonly label="Range Size" value={snapshot?.rangeSize} />
          <Readonly label="Overlap Type" value={snapshot?.overlapType} />
          <Readonly label="DB2 State" value={snapshot?.db2State} />
        </Grid>
      </Section>

      {/* ===================================================== */}
      {/* 4️⃣ FINAL MARKET CONTEXT */}
      {/* ===================================================== */}
      <Section title="STEP-1 Final Market Context">
        {mode === "AUTO" && snapshot ? (
          <Grid>
            <Readonly label="Market Bias" value={snapshot.marketBias} />
            <Readonly label="Gap Context" value={snapshot.gapContext} />
            <Readonly
              label="Pre-Market Notes"
              value={snapshot.premarketNotes}
            />
          </Grid>
        ) : (
          !isFrozen && (
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
                label="Pre-Market Notes"
                value={notes}
                onChange={setNotes}
              />
            </Grid>
          )
        )}
      </Section>

      {/* ===================================================== */}
      {/* ACTIONS */}
      {/* ===================================================== */}
      {!isFrozen ? (
        <button
          onClick={handleFreeze}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white"
        >
          Freeze STEP-1 Context
        </button>
      ) : (
        <div className="rounded border border-green-300 bg-green-50 p-4 text-sm text-green-700">
          STEP-1 frozen at {snapshot?.frozenAt}
        </div>
      )}

      {error && (
        <div className="text-xs text-gray-400">
          Backend unavailable — manual mode enabled
        </div>
      )}
    </div>
  );
}

/* ===================================================== */
/* SHARED UI HELPERS                                     */
/* ===================================================== */

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded border p-4">
      <h3 className="mb-3 text-sm font-semibold">{title}</h3>
      {children}
    </div>
  );
}

function Grid({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      {children}
    </div>
  );
}

/**
 * Editable → uncontrolled + onBlur capture
 * Read-only → controlled
 */
function Field({
  label,
  value,
  editable = false,
  onBlur,
}: {
  label: string;
  value: any;
  editable?: boolean;
  onBlur?: (v: number | undefined) => void;
}) {
  return (
    <div>
      <label className="text-xs font-semibold">{label}</label>

      {editable ? (
        <input
          defaultValue={value ?? ""}
          onBlur={(e) => {
            const v =
              e.target.value === ""
                ? undefined
                : Number(e.target.value);
            console.log("[DEBUG][FIELD][BLUR]", label, v);
            onBlur?.(v);
          }}
          className="mt-1 w-full rounded border px-2 py-1"
        />
      ) : (
        <input
          value={value ?? ""}
          readOnly
          className="mt-1 w-full rounded border bg-gray-100 px-2 py-1"
        />
      )}
    </div>
  );
}

function Readonly({
  label,
  value,
}: {
  label: string;
  value: any;
}) {
  return (
    <div>
      <label className="text-xs font-semibold">{label}</label>
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
      <label className="text-xs font-semibold">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as T)}
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
      <label className="text-xs font-semibold">{label}</label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={3}
        className="mt-1 w-full rounded border px-2 py-1"
      />
    </div>
  );
}
