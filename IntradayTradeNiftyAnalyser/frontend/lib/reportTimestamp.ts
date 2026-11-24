const ISO_TIMESTAMP = /\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d{1,3})?)?(?:Z|[+-]\d{2}:?\d{2})\b/g;

const kolkataParts = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;

  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Kolkata",
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(date).reduce<Record<string, string>>((result, part) => {
    result[part.type] = part.value;
    return result;
  }, {});

  return parts;
};

/** Formats ISO timestamps only for display; the saved report text remains unchanged. */
export function formatNarrativeTimestamps(narrative?: string | null): string {
  if (narrative == null) return "";

  const timestamps = [...narrative.matchAll(ISO_TIMESTAMP)].map((match) => ({
    source: match[0],
    parts: kolkataParts(match[0]),
  }));
  const valid = timestamps.filter((timestamp): timestamp is { source: string; parts: Record<string, string> } => timestamp.parts !== null);
  const days = new Set(valid.map(({ parts }) => `${parts.year}-${parts.month}-${parts.day}`));
  const years = new Set(valid.map(({ parts }) => parts.year));
  const includeDate = days.size > 1;
  const includeYear = years.size > 1;

  return narrative.replace(ISO_TIMESTAMP, (source) => {
    const parts = valid.find((timestamp) => timestamp.source === source)?.parts;
    if (!parts) return source;
    const clock = `${parts.hour}:${parts.minute}`;
    if (!includeDate) return clock;
    return `${parts.day} ${parts.month}${includeYear ? ` ${parts.year}` : ""}, ${clock}`;
  });
}
