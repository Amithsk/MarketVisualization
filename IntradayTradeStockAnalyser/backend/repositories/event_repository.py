# backend/repositories/event_repository.py

import json
from typing import List

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.models.market_event import MarketEvent

from backend.utils.debug_logger import (
    log_count,
    log_error,
    log_info,
    log_object,
    log_step,
)




class EventRepository:

    @staticmethod
    def save_market_events(
        db: Session,
        trade_date: str,
        events: List[MarketEvent],
    ) -> None:

        try:

            log_step(
                "SAVING MARKET EVENTS"
            )

            log_count(
                "Events To Save",
                events,
            )

            if not events:

                log_info(
                    "Save Status",
                    "No events available to save"
                )

                return

            query = text("""

                INSERT IGNORE  INTO
                stocktradeanalysis_detected_events(

                    event_id,
                    trade_date,
                    stock_symbol,
                    event_type,
                    candle_time,
                    candle_index,
                    price,
                    strength_score,

                    nifty_direction,
                    relative_strength_score,

                    above_vwap,
                    volume_expansion,
                    orb_valid,

                    explanation,
                    trading_implication,

                    event_metadata

                )
                VALUES (

                    :event_id,
                    :trade_date,
                    :stock_symbol,
                    :event_type,
                    :candle_time,
                    :candle_index,
                    :price,
                    :strength_score,

                    :nifty_direction,
                    :relative_strength_score,

                    :above_vwap,
                    :volume_expansion,
                    :orb_valid,

                    :explanation,
                    :trading_implication,

                    :event_metadata

                )

            """)

            values = []

            for event in events:

                event_payload = {

                    "event_id": event.id,
                    
                    "trade_date": trade_date,

                    "stock_symbol": event.symbol,

                    "event_type": event.event_type.value,

                    "candle_time": event.timestamp,

                    "candle_index": event.candle_index,

                    "price": event.price,

                    "strength_score": event.strength_score,

                    "nifty_direction": (
                        event.nifty_context.direction
                    ),

                    "relative_strength_score": (
                        event.nifty_context
                        .relative_strength_score
                    ),

                    "above_vwap": (
                        event.validation.above_vwap
                    ),

                    "volume_expansion": (
                        event.validation
                        .volume_expansion
                    ),

                    "orb_valid": (
                        event.validation.orb_valid
                    ),

                    "explanation": (
                        event.explanation
                    ),

                    "trading_implication": (
                        event.trading_implication
                    ),

                    "event_metadata": json.dumps(
                        event.event_metadata
                    ),
                }

                values.append(
                    event_payload
                )

            log_count(
                "Prepared DB Payload",
                values
            )

            if values:

                log_object(
                    "First Event Payload",
                    values[0]
                )

            db.execute(
                query,
                values
            )

            log_info(
                "DB Execute Status",
                "Insert query executed"
            )

            db.commit()

            log_info(
                "DB Commit Status",
                "Transaction committed successfully"
            )

            log_step(
                "MARKET EVENTS SAVED SUCCESSFULLY"
            )

        except Exception as error:

            db.rollback()

            log_step(
                "EVENT SAVE FAILED"
            )

            log_error(error)

            raise