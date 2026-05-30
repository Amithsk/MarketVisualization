#/IntrdayTradeStockAnalyser/backend/services/ai_explanation/explanation_engine.py

from typing import Dict, Any

from backend.services.ai_explanation.candle_explainer import (
    build_candle_explanations,
)

from backend.services.ai_explanation.strategy_explainer import (
    build_strategy_explanations,
)

from backend.services.ai_explanation.timeline_narrator import (
    build_timeline_narration,
)

from backend.services.ai_explanation.trade_coach import (
    build_trade_coaching,
)

from backend.services.ai_explanation.nifty_relationship_explainer import (
    build_nifty_relationship_analysis,
)


class ExplanationEngine:
    """
    Main orchestration layer for
    AI explanation generation.

    Responsibilities:
    - orchestrate explanation generation
    - centralize educational intelligence
    - enrich replay payload
    """

    def generate_explanations(
        self,
        replay_payload: Dict[str, Any]
    ) -> Dict[str, Any]:

        """
        Generate all AI explanation layers
        from replay payload.
        """

        # =====================================================
        # CANDLE EXPLANATIONS
        # =====================================================

        candle_explanations = (
            build_candle_explanations(
                replay_payload
            )
        )

        # =====================================================
        # STRATEGY EXPLANATIONS
        # =====================================================

        strategy_explanations = (
            build_strategy_explanations(
                replay_payload
            )
        )

        # =====================================================
        # TIMELINE NARRATION
        # =====================================================

        timeline_narration = (
            build_timeline_narration(
                replay_payload
            )
        )

        # =====================================================
        # TRADE COACHING
        # =====================================================

        trade_coaching = (
            build_trade_coaching(
                replay_payload
            )
        )

        # =====================================================
        # NIFTY RELATIONSHIP ANALYSIS
        # =====================================================

        nifty_relationship_analysis = (
            build_nifty_relationship_analysis(
                replay_payload
            )
        )

        # =====================================================
        # FINAL EXPLANATION CONTEXT
        # =====================================================

        explanation_context = {

            "candle_explanations":
                candle_explanations,

            "strategy_explanations":
                strategy_explanations,

            "timeline_narration":
                timeline_narration,

            "trade_coaching":
                trade_coaching,

            "nifty_relationship_analysis":
                nifty_relationship_analysis,
        }

        return explanation_context

