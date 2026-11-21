const IST_TIME_ZONE = "Asia/Kolkata";
const ISO_TIMESTAMP = /(?<![A-Za-z0-9_])\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})(?![A-Za-z0-9_])/g;

type TimestampParts = { day: string; month: string; hour: string; minute: string; dayPeriod: string };

function parts(value: string): TimestampParts | null {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return null;
    const values = new Intl.DateTimeFormat("en-GB", { timeZone: IST_TIME_ZONE, day: "numeric", month: "short", hour: "numeric", minute: "2-digit", hour12: true }).formatToParts(date);
    const get = (type: Intl.DateTimeFormatPartTypes) => values.find((part) => part.type === type)?.value;
    const day = get("day"), month = get("month"), hour = get("hour"), minute = get("minute"), dayPeriod = get("dayPeriod");
    return day && month && hour && minute && dayPeriod ? { day, month, hour, minute, dayPeriod } : null;
}

/** Format an authoritative instant for Coach UI without changing the source value. */
export function formatCoachTimestamp(value: string, includeDate = true): string {
    const valueParts = parts(value);
    if (!valueParts) return value;
    const clock = `${valueParts.hour}:${valueParts.minute} ${valueParts.dayPeriod}`;
    return includeDate ? `${valueParts.day} ${valueParts.month}, ${clock}` : clock;
}

/** Replace ISO instants in stored Coach prose while preserving its surrounding Markdown. */
export function formatCoachTimestampText(text: string): string {
    let establishedDate: string | null = null;
    return text.replace(ISO_TIMESTAMP, (raw) => {
        const valueParts = parts(raw);
        if (!valueParts) return raw;
        const date = `${valueParts.day} ${valueParts.month}`;
        const formatted = formatCoachTimestamp(raw, establishedDate !== date);
        establishedDate = date;
        return formatted;
    });
}

export function formatCoachTimestampList(values: string[]): string[] {
    let establishedDate: string | null = null;
    return values.map((value) => {
        const valueParts = parts(value);
        if (!valueParts) return value;
        const date = `${valueParts.day} ${valueParts.month}`;
        const formatted = formatCoachTimestamp(value, establishedDate !== date);
        establishedDate = date;
        return formatted;
    });
}
