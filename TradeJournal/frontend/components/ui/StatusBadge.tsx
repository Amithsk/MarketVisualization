export function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    PLANNED: "bg-gray-200 text-gray-700",
    EXECUTED: "bg-blue-200 text-blue-800",
    EXITED: "bg-orange-200 text-orange-800",
    REVIEWED: "bg-green-200 text-green-800",
    NOT_TAKEN: "bg-red-200 text-red-800",
  };

  return (
    <span
      className={`px-3 py-1 rounded-full text-xs font-semibold ${
        colors[status] ?? "bg-gray-100 text-gray-600"
      }`}
    >
      {status}
    </span>
  );
}
