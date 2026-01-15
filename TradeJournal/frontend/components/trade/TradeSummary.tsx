"use client"

type Props = {
  planStatus?: string
  tradeId?: number
  onExecute: () => void
  onExit: () => void
}

export default function TradeSummary({
  planStatus,
  tradeId,
  onExecute,
  onExit,
}: Props) {
  return (
    <div className="bg-white rounded-xl border shadow-sm">
      <div className="px-6 py-4 border-b text-lg font-semibold">
        Trade Actions
      </div>

      <div className="px-6 py-6 flex gap-4">
        {planStatus === "PLANNED" && (
          <button
            onClick={onExecute}
            className="px-4 py-2 bg-green-600 text-white rounded"
          >
            Execute Trade
          </button>
        )}

        {tradeId && (
          <button
            onClick={onExit}
            className="px-4 py-2 bg-red-600 text-white rounded"
          >
            Exit Trade
          </button>
        )}
      </div>
    </div>
  )
}
