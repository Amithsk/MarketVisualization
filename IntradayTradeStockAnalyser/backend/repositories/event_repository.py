# backend/repositories/event_repository.py

import json
from typing import List

from sqlalchemy import text
from sqlalchemy.orm import Session

from models.market_event import MarketEvent


class EventRepository:

    @staticmethod
    def save_market_events(
        db: Session,
        events: List[MarketEvent],
    ) -> None:

        if not events:
            return

        query = text("""

            INSERT INTO
            stocktradesanalysis_detected_events (

                event_id,
                symbol,
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
                :symbol,
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

            values.append({

                "event_id": event.id,

                "symbol": event.symbol,

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
            })

        db.execute(query, values)

        db.commit()