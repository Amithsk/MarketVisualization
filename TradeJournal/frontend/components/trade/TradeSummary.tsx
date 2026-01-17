export default function TradeSummary({ trade }: { trade: any }) {
  if (!trade) return null;

  return (
    <div className="bg-gray-50 border rounded-xl p-4 space-y-2">
      <h3 className="font-semibold text-gray-700">Trade Summary</h3>

      <div className="grid grid-cols-2 text-sm gap-y-1">
        <span className="text-gray-500">Symbol</span>
        <span>{trade.symbol}</span>

        <span className="text-gray-500">Side</span>
        <span>{trade.side}</span>

        <span className="text-gray-500">Quantity</span>
        <span>{trade.quantity}</span>

        <span className="text-gray-500">Entry</span>
        <span>{trade.entry_price}</span>

        {trade.exit_price && (
          <>
            <span className="text-gray-500">Exit</span>
            <span>{trade.exit_price}</span>
          </>
        )}
      </div>
    </div>
  );
}
