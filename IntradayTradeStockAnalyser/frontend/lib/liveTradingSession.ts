const IST_TIME_ZONE = "Asia/Kolkata";
const SESSION_START_MINUTES = 9 * 60 + 15;
const SESSION_END_MINUTES = 15 * 60 + 30;

type SessionPlan = {
    planDate?: string;
    decisionTime?: string;
};

export type LiveTradingSession = {
    date: string;
    isOpen: boolean;
};

function istParts(date: Date): Record<string, string> {
    return Object.fromEntries(
        new Intl.DateTimeFormat("en-GB", {
            timeZone: IST_TIME_ZONE,
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            hourCycle: "h23",
        }).formatToParts(date)
            .filter((part) => part.type !== "literal")
            .map((part) => [part.type, part.value])
    );
}

export function istTradingDate(now = new Date()): string {
    const parts = istParts(now);
    return `${parts.year}-${parts.month}-${parts.day}`;
}

export function getLiveTradingSession(now = new Date()): LiveTradingSession {
    const parts = istParts(now);
    const minutes = Number(parts.hour) * 60 + Number(parts.minute);

    return {
        date: `${parts.year}-${parts.month}-${parts.day}`,
        isOpen: minutes >= SESSION_START_MINUTES && minutes < SESSION_END_MINUTES,
    };
}

export function millisecondsUntilLiveTradingSessionBoundary(now = new Date()): number {
    const parts = istParts(now);
    const year = Number(parts.year);
    const month = Number(parts.month);
    const day = Number(parts.day);
    const minutes = Number(parts.hour) * 60 + Number(parts.minute);
    const boundary = minutes < SESSION_START_MINUTES
        ? { dayOffset: 0, minutes: SESSION_START_MINUTES }
        : minutes < SESSION_END_MINUTES
            ? { dayOffset: 0, minutes: SESSION_END_MINUTES }
            : { dayOffset: 1, minutes: SESSION_START_MINUTES };
    const boundaryTimestamp = Date.UTC(
        year,
        month - 1,
        day + boundary.dayOffset,
        Math.floor(boundary.minutes / 60),
        boundary.minutes % 60
    ) - (5.5 * 60 * 60 * 1000);

    return Math.max(0, boundaryTimestamp - now.getTime());
}

function dateFromDecisionTime(decisionTime?: string): string | null {
    if (!decisionTime) return null;

    const datePrefix = decisionTime.match(/^(\d{4}-\d{2}-\d{2})/);
    if (!datePrefix) return null;

    // Candle timestamps without an offset are already expressed in IST.
    if (!/(Z|[+-]\d{2}:?\d{2})$/i.test(decisionTime)) {
        return datePrefix[1];
    }

    const timestamp = new Date(decisionTime);
    return Number.isNaN(timestamp.getTime()) ? null : istTradingDate(timestamp);
}

export function belongsToLiveTradingSession(
    plan: SessionPlan,
    sessionDate: string
): boolean {
    const planDate = plan.planDate || dateFromDecisionTime(plan.decisionTime);
    return planDate === sessionDate;
}
