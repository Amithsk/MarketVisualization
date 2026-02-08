// src/components/step2/Step2OpenBehavior.tsx
"use client";

import { useEffect, useState, useMemo } from "react";
import { useStep2 } from "@/hooks/useStep2";
import type { TradeDate } from "@/types/common.types";
import type {
  IndexOpenBehavior,
  EarlyVolatility,
  MarketParticipation,
} from "@/types/step2.types";

interface Step2OpenBehaviorProps {
  tradeDate: TradeDate;
}

export default function Step2OpenBehavior({
  tradeDate,
}: Step2OpenBehaviorProps) {
  console.log(
    "[DEBUG][STEP-2] Component RENDERED for tradeDate:",
    tradeDate
  );

  const {
    snapshot,
    isFrozen,
    tradeAllowed,
    loading,
    error,
    previewStep2,
    freezeStep2,
  } = useStep2(tradeDate);

  // Manual entry state (used only when backend sends UNKNOWNs)
  const [indexOpenBehavior, setIndexOpenBehavior] =
    useState<IndexOpenBehavior>("UNKNOWN");
  const [earlyVolatility, setEarlyVolatility] =
    useState<EarlyVolatility>("UNKNOWN");
  const [marketParticipation, setMarketParticipation] =
    useState<MarketParticipation>("UNKNOWN");

  /**
   * STEP-2 PREVIEW (DEBUGGED)
   */
  useEffect(() => {
    console.log(
      "[DEBUG][STEP-2] previewStep2() CALLED for tradeDate:",
      tradeDate
    );

    previewStep2();
  }, [previewStep2, tradeDate]);

  /**
   * STEP-2 MODE DERIVATION (LOCKED)
   */
  const isManual = useMemo(() => {
    if (!snapshot) {
      console.log(
        "[DEBUG][STEP-2] snapshot is NULL → MANUAL mode"
      );
      return true;
    }

    const manual =
      snapshot.indexOpenBehavior === "UNKNOWN" ||
      snapshot.earlyVolatility === "UNKNOWN" ||
      snapshot.marketParticipation === "UNKNOWN";

    console.log(
      "[DEBUG][STEP-2] snapshot received",
      snapshot,
      "→ isManual =",
      manual
    );

    return manual;
  }, [snapshot]);

  const handleFreeze = () => {
    console.log(
      "[DEBUG][STEP-2] Freeze clicked with values:",
      {
        indexOpenBehavior,
        earlyVolatility,
        marketParticipation,
      }
    );

    if (!snapshot) return;

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
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
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
          </div>

          <TradePermissionBanner tradeAllowed={tradeAllowed} />
        </>
      )}

      {isManual && !isFrozen && (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
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
          </div>

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
