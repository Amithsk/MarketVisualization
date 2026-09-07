const INDIAN_TIME_ZONE = "Asia/Kolkata";
const MARKET_OPEN_MINUTES = 9 * 60 + 15;
const MARKET_CLOSE_MINUTES = 15 * 60 + 15;

function getIndianTimeParts(date: Date) {
    const parts = new Intl.DateTimeFormat("en-GB", {
        timeZone: INDIAN_TIME_ZONE,
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hourCycle: "h23",
    }).formatToParts(date);

    const valueFor = (type: Intl.DateTimeFormatPartTypes) =>
        Number(parts.find((part) => part.type === type)?.value ?? 0);

    return {
        hour: valueFor("hour"),
        minute: valueFor("minute"),
        second: valueFor("second"),
    };
}

/** Whether an instant falls within the inclusive 09:15–15:15 IST window. */
export function isIndianMarketOpen(date = new Date()) {
    const { hour, minute } = getIndianTimeParts(date);
    const currentMinutes = hour * 60 + minute;

    return currentMinutes >= MARKET_OPEN_MINUTES &&
        currentMinutes <= MARKET_CLOSE_MINUTES;
}

/** Delay until the next 09:15 IST; intended for use while the market is closed. */
export function millisecondsUntilIndianMarketOpen(date = new Date()) {
    const { hour, minute, second } = getIndianTimeParts(date);
    const currentMinutes = hour * 60 + minute;
    const minutesUntilOpen = currentMinutes < MARKET_OPEN_MINUTES
        ? MARKET_OPEN_MINUTES - currentMinutes
        : 24 * 60 - currentMinutes + MARKET_OPEN_MINUTES;

    return Math.max(1000, minutesUntilOpen * 60_000 - second * 1000 - date.getMilliseconds());
}
