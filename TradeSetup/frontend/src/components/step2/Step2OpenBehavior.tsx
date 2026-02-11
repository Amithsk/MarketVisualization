// src/components/step2/Step2OpenBehavior.tsx
"use client";

import { useEffect, useMemo, useState } from "react";
import type { TradeDate } from "@/types/common.types";
import type { useStep2 } from "@/hooks/useStep2";
import type {
  IndexOpenBehavior,
  EarlyVolatility,
  MarketParticipation,
} from "@/types/step2.types";

interface Step2OpenBehaviorProps {
  tradeDate: TradeDate;
  step2: ReturnType<typeof useStep2>;
}

export default function Step2OpenBehavior({
  tradeDate,
  step2,
}: Step2OpenBehaviorProps) {
  const {
    snapshot,
    isFrozen,
    tradeAllowed,
    loading,
    error,
    freezeStep2,
  } = step2;

  console.log(
    "[STEP-2] RENDER",
    { tradeDate, isFrozen, tradeAllowed }
  );

  const [indexOpenBehavior, setIndexOpenBehavior] =
    useState<IndexOpenBehavior>("UNKNOWN");

  const [earlyVolatility, setEarlyVolatility] =
    useState<EarlyVolatility>("UNKNOWN");

  const [marketParticipation, setMarketParticipation] =
    useState<MarketParticipation>("UNKNOWN");

  /**
   * Detect Manual Mode
   */
  const isManual = useMemo(() => {
    if (!snapshot) return true;

    return (
      snapshot.indexOpenBehavior === "UNKNOWN" ||
      snapshot.earlyVolatility === "UNKNOWN" ||
      snapshot.marketParticipation === "UNKNOWN"
    );
  }, [snapshot]);

  const handleFreeze = () => {
    freezeStep2({
      indexOpenBehavior,
      earlyVolatility,
      marketParticipation,
    });
  };

  return (
    <div className="space-y-6">
      <div className="text-sm text-gray-500">
        Market Open Behavior for{" "}
        <span className="font-medium">{tradeDate}</span>
      </div>

      {loading && (
        <div className="text-sm text-gray-500">
          Loading STEP-2…
        </div>
      )}

      {!isManual && snapshot && (
        <>
          <ReadonlyField
            label="Index Open"
            value={snapshot.indexOpenBehavior}
          />
          <ReadonlyField
            label="Early Volatility"
            value={snapshot.earlyVolatility}
          />
          <ReadonlyField
            label="Market Participation"
            value={snapshot.marketParticipation}
          />
          <TradePermissionBanner tradeAllowed={tradeAllowed} />
        </>
      )}

      {isManual && !isFrozen && (
        <>
          <SelectField
            label="Index Open"
            value={indexOpenBehavior}
            onChange={setIndexOpenBehavior}
            options={[
              "UNKNOWN",
              "STRONG_UP",
              "WEAK_UP",
              "FLAT",
              "WEAK_DOWN",
              "STRONG_DOWN",
            ]}
          />

          <SelectField
            label="Early Volatility"
            value={earlyVolatility}
            onChange={setEarlyVolatility}
            options={[
              "UNKNOWN",
              "EXPANDING",
              "CONTRACTING",
              "NORMAL",
              "CHAOTIC",
            ]}
          />

          <SelectField
            label="Market Participation"
            value={marketParticipation}
            onChange={setMarketParticipation}
            options={[
              "UNKNOWN",
              "BROAD",
              "NARROW",
              "MIXED",
              "THIN",
            ]}
          />

          <TradePermissionBanner tradeAllowed={tradeAllowed} />
        </>
      )}

      {!isFrozen ? (
        <button
          onClick={handleFreeze}
          disabled={loading}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          Freeze STEP-2 Behavior
        </button>
      ) : (
        <div className="rounded border border-green-300 bg-green-50 p-4 text-sm text-green-700">
          STEP-2 frozen at{" "}
          <span className="font-medium">
            {snapshot?.frozenAt}
          </span>
        </div>
      )}

      {error && (
        <div className="text-xs text-gray-400">
          Non-blocking backend warning
        </div>
      )}
    </div>
  );
}

/* ---------- Small UI helpers ---------- */

function ReadonlyField({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded border p-4">
      <label className="text-sm font-semibold text-gray-700">
        {label}
      </label>
      <input
        value={value}
        readOnly
        className="mt-2 w-full rounded border px-2 py-1 bg-gray-100 text-sm"
      />
    </div>
  );
}

function SelectField<T extends string>({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: T;
  onChange: (v: T) => void;
  options: T[];
}) {
  return (
    <div className="rounded border p-4">
      <label className="text-sm font-semibold text-gray-700">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as T)}
        className="mt-2 w-full rounded border px-2 py-1 text-sm"
      >
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt.replace("_", " ")}
          </option>
        ))}
      </select>
    </div>
  );
}

function TradePermissionBanner({
  tradeAllowed,
}: {
  tradeAllowed: boolean;
}) {
  return (
    <div
      className={`rounded border p-4 ${
        tradeAllowed
          ? "border-green-300 bg-green-50 text-green-700"
          : "border-red-300 bg-red-50 text-red-700"
      }`}
    >
      <div className="text-sm font-medium">
        Trade Permission
      </div>
      <div className="mt-2 text-sm">
        {tradeAllowed
          ? "Trading is permitted based on STEP-2 evaluation."
          : "Trading is NOT permitted for the day."}
      </div>
    </div>
  );
}
