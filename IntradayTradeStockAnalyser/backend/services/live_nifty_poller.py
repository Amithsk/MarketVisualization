import asyncio
from copy import deepcopy
from datetime import datetime, time, timedelta
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from backend.services.live_service import LiveService


INDIAN_TIME_ZONE = ZoneInfo("Asia/Kolkata")
MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 15)
MARKET_OPEN_MINUTES = 9 * 60 + 15
MARKET_CLOSE_MINUTES = 15 * 60 + 15


class LiveNiftyPoller:

    _task: Optional[asyncio.Task] = None
    _stop_event: Optional[asyncio.Event] = None
    _refresh_lock: Optional[asyncio.Lock] = None
    _state_lock: Optional[asyncio.Lock] = None
    _state: Dict[str, Any] = {
        "initialized": False,
        "payload": None,
        "trade_date": None,
        "last_refresh_time": None,
        "latest_candle_timestamp": None,
        "interval": None,
        "contract": None,
        "last_error": None,
    }

    @classmethod
    def start(cls):

        if cls._task and not cls._task.done():
            print("LIVE_NIFTY_POLLER already running")
            return

        cls._stop_event = asyncio.Event()
        cls._refresh_lock = asyncio.Lock()
        cls._state_lock = asyncio.Lock()
        cls._task = asyncio.create_task(cls._run())

        print("LIVE_NIFTY_POLLER started")

    @classmethod
    async def stop(cls):

        if cls._stop_event:
            cls._stop_event.set()

        if cls._task:
            await cls._task

        cls._task = None
        cls._stop_event = None
        cls._refresh_lock = None
        cls._state_lock = None

        print("LIVE_NIFTY_POLLER stopped")

    @classmethod
    async def get_payload(cls) -> Dict[str, Any]:

        current_trade_date = cls._current_trade_date()

        if cls._state_lock:
            async with cls._state_lock:
                state = deepcopy(cls._state)
        else:
            state = deepcopy(cls._state)

        if (
            not state["initialized"]
            or state["trade_date"] != current_trade_date
            or not state["payload"]
        ):
            return {
                "status": "error",
                "message": "Live NIFTY data temporarily unavailable",
                "trade_date": current_trade_date,
                "last_error": state.get("last_error"),
            }

        return state["payload"]

    @classmethod
    def is_market_time(cls, moment: Optional[datetime] = None) -> bool:

        current = cls._to_indian_time(moment)

        if current.weekday() >= 5:
            return False

        current_minutes = current.hour * 60 + current.minute

        return (
            MARKET_OPEN_MINUTES
            <= current_minutes
            <= MARKET_CLOSE_MINUTES
        )

    @classmethod
    def seconds_until_next_market_open(
        cls,
        moment: Optional[datetime] = None
    ) -> float:

        current = cls._to_indian_time(moment)
        candidate = datetime.combine(
            current.date(),
            MARKET_OPEN,
            tzinfo=INDIAN_TIME_ZONE,
        )

        if current >= candidate:
            candidate += timedelta(days=1)

        while candidate.weekday() >= 5:
            candidate += timedelta(days=1)

        return max(1.0, (candidate - current).total_seconds())

    @classmethod
    def seconds_until_next_five_minute_boundary(
        cls,
        moment: Optional[datetime] = None
    ) -> float:

        current = cls._to_indian_time(moment)
        next_minute = ((current.minute + 1 + 4) // 5) * 5
        boundary = datetime(
            current.year,
            current.month,
            current.day,
            current.hour,
            0,
            5,
            tzinfo=INDIAN_TIME_ZONE,
        ) + timedelta(minutes=next_minute)

        if boundary <= current:
            boundary += timedelta(minutes=5)

        return max(1.0, (boundary - current).total_seconds())

    @classmethod
    async def _run(cls):

        while cls._stop_event and not cls._stop_event.is_set():
            if not cls.is_market_time():
                await cls._clear_stale_session()
                wait_seconds = cls.seconds_until_next_market_open()
                print(
                    "LIVE_NIFTY_POLLER outside market hours; "
                    f"waiting {round(wait_seconds)} seconds"
                )
                await cls._wait(wait_seconds)
                continue

            try:
                await cls._refresh()
            except Exception as error:
                await cls._record_error(str(error))
                print(
                    "LIVE_NIFTY_POLLER refresh crashed "
                    f"error={repr(error)}"
                )

            if cls._stop_event and not cls._stop_event.is_set():
                wait_seconds = cls.seconds_until_next_five_minute_boundary()
                await cls._wait(wait_seconds)

    @classmethod
    async def _refresh(cls):

        if not cls._refresh_lock:
            return

        async with cls._refresh_lock:
            if not cls.is_market_time():
                return

            trade_date = cls._current_trade_date()

            print(
                "LIVE_NIFTY_POLLER refresh started "
                f"trade_date={trade_date}"
            )

            result = await asyncio.to_thread(
                LiveService.get_nifty_candles
            )

            if result.get("status") != "success":
                message = result.get(
                    "message",
                    "Failed to refresh live NIFTY data",
                )
                await cls._record_error(message)
                print(
                    "LIVE_NIFTY_POLLER refresh failed "
                    f"trade_date={trade_date} error={message}"
                )
                return

            response_trade_date = result.get("trade_date")

            if response_trade_date and response_trade_date != trade_date:
                message = (
                    "Live NIFTY trade date mismatch: "
                    f"expected={trade_date} actual={response_trade_date}"
                )
                await cls._record_error(message)
                print(
                    "LIVE_NIFTY_POLLER refresh rejected "
                    f"{message}"
                )
                return

            latest_candle_timestamp = cls._latest_candle_timestamp(
                result
            )
            refresh_time = cls._to_indian_time().isoformat()
            payload = {
                **result,
                "trade_date": result.get("trade_date") or trade_date,
                "last_refresh_time": refresh_time,
                "latest_candle_timestamp": latest_candle_timestamp,
            }

            if cls._state_lock:
                async with cls._state_lock:
                    cls._state = {
                        "initialized": True,
                        "payload": payload,
                        "trade_date": trade_date,
                        "last_refresh_time": refresh_time,
                        "latest_candle_timestamp": latest_candle_timestamp,
                        "interval": payload.get("interval"),
                        "contract": payload.get("contract"),
                        "last_error": None,
                    }

            print(
                "LIVE_NIFTY_POLLER refresh succeeded "
                f"trade_date={trade_date} "
                f"latest_candle={latest_candle_timestamp}"
            )

    @classmethod
    async def _record_error(cls, message: str):

        if cls._state_lock:
            async with cls._state_lock:
                cls._state["last_error"] = message
        else:
            cls._state["last_error"] = message

    @classmethod
    async def _clear_stale_session(cls):

        current_trade_date = cls._current_trade_date()

        if cls._state_lock:
            async with cls._state_lock:
                if (
                    cls._state["initialized"]
                    and cls._state["trade_date"] != current_trade_date
                ):
                    cls._state = {
                        "initialized": False,
                        "payload": None,
                        "trade_date": None,
                        "last_refresh_time": None,
                        "latest_candle_timestamp": None,
                        "interval": None,
                        "contract": None,
                        "last_error": None,
                    }

    @classmethod
    async def _wait(cls, seconds: float):

        if not cls._stop_event:
            return

        try:
            await asyncio.wait_for(
                cls._stop_event.wait(),
                timeout=seconds,
            )
        except asyncio.TimeoutError:
            pass

    @classmethod
    def _to_indian_time(
        cls,
        moment: Optional[datetime] = None
    ) -> datetime:

        current = moment or datetime.now(tz=INDIAN_TIME_ZONE)

        if current.tzinfo is None:
            current = current.replace(tzinfo=INDIAN_TIME_ZONE)

        return current.astimezone(INDIAN_TIME_ZONE)

    @classmethod
    def _current_trade_date(cls) -> str:

        return cls._to_indian_time().date().isoformat()

    @staticmethod
    def _latest_candle_timestamp(
        payload: Dict[str, Any]
    ) -> Optional[str]:

        candles = payload.get("candles") or []

        if not candles:
            return None

        return candles[-1].get("time")
