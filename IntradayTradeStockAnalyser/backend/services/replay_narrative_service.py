#IntradayTradeStockAnalyser/backend/services/replay_narrative_service.py


class ReplayNarrativeService:

    @staticmethod
    def build_replay_narrative(
        market_context: dict,
        market_behavior: dict,
        market_open_behavior: dict,
        execution_control: dict,
        stock_selection_context: dict,
        trade_construction: dict
    ):

        market_summary = (
            ReplayNarrativeService
            ._build_market_summary(
                market_context,
                market_open_behavior
            )
        )

        strategy_summary = (
            ReplayNarrativeService
            ._build_strategy_summary(
                stock_selection_context,
                execution_control
            )
        )

        execution_summary = (
            ReplayNarrativeService
            ._build_execution_summary(
                execution_control,
                market_open_behavior
            )
        )

        relative_strength_summary = (
            ReplayNarrativeService
            ._build_relative_strength_summary(
                stock_selection_context
            )
        )

        trade_construction_summary = (
            ReplayNarrativeService
            ._build_trade_construction_summary(
                trade_construction
            )
        )

        learning_insight = (
            ReplayNarrativeService
            ._build_learning_insight(
                market_context,
                stock_selection_context,
                trade_construction
            )
        )

        return {

            "market_summary": market_summary,

            "strategy_summary": strategy_summary,

            "execution_summary": execution_summary,

            "relative_strength_summary":
                relative_strength_summary,

            "trade_construction_summary":
                trade_construction_summary,

            "learning_insight": learning_insight

        }

    @staticmethod
    def _build_market_summary(
        market_context: dict,
        market_open_behavior: dict
    ):

        final_market_context = (
            market_context
            .get("final_market_context")
        )

        vwap_state = (
            market_open_behavior
            .get("vwap_state")
        )

        volatility_state = (
            market_open_behavior
            .get("volatility_state")
        )

        if final_market_context == "TREND_DAY":

            return (
                "Market conditions favored "
                "directional momentum trading. "
                f"VWAP behavior remained "
                f"{vwap_state} with "
                f"{volatility_state} volatility."
            )

        if final_market_context == "RANGE_UNCERTAIN_DAY":

            return (
                "Market conditions were uncertain "
                "with mixed directional structure. "
                "Selective trade execution was preferred."
            )

        if final_market_context == "NO_TRADE_DAY":

            return (
                "Market conditions were not suitable "
                "for aggressive intraday execution."
            )

        return (
            "Market context information unavailable."
        )

    @staticmethod
    def _build_strategy_summary(
        stock_selection_context: dict,
        execution_control: dict
    ):
        strategy_used = (
            stock_selection_context
            .get("strategy_used")
        )

        allowed_strategies = (
            execution_control
            .get("allowed_strategies", [])
        )

        structure_valid = (
            stock_selection_context
            .get("structure_valid")
        )

        rs_value = (
            stock_selection_context
            .get("rs_value")
        )

        rejection_reason = (
            stock_selection_context
            .get("reason")
        )

        if not strategy_used:
            return (
                "No active strategy context available."
            )

        if strategy_used == "NO_TRADE":
            return (
                "No valid trading setup passed the "
                "strategy selection filters. "
                f"Reason: {rejection_reason}."
            )

        return (
            f"{strategy_used} strategy was selected "
            f"because market conditions supported "
            f"{', '.join(allowed_strategies)} setups. "
            f"Structure validity was "
            f"{'confirmed' if structure_valid else 'weak'} "
            f"with relative strength value of {rs_value}."
        )

    @staticmethod
    def _build_execution_summary(
        execution_control: dict,
        market_open_behavior: dict
    ):

        trade_permission = (
            execution_control
            .get("trade_permission")
        )

        vwap_state = (
            market_open_behavior
            .get("vwap_state")
        )

        range_hold_status = (
            market_open_behavior
            .get("range_hold_status")
        )

        if trade_permission == "YES":

            return (
                "Trade execution was permitted because "
                f"VWAP behavior remained {vwap_state} "
                f"and range structure stayed "
                f"{range_hold_status}."
            )

        if trade_permission == "LIMITED":

            return (
                "Trade execution required caution due "
                "to unstable market conditions."
            )

        if trade_permission == "NO":

            return (
                "Trade execution was restricted due "
                "to unfavorable market structure."
            )

        return (
            "Execution context unavailable."
        )

    @staticmethod
    def _build_relative_strength_summary(
        stock_selection_context: dict
    ):

        rs_value = (
            stock_selection_context
            .get("rs_value")
        )

        tradable = (
            stock_selection_context
            .get("tradable")
        )

        if rs_value is None:

            return (
                "Relative strength information unavailable."
            )

        if rs_value > 0:

            return (
                f"Stock showed positive relative "
                f"strength against NIFTY with "
                f"RS value of {rs_value}. "
                f"Tradable status remained "
                f"{'active' if tradable else 'inactive'}."
            )

        if rs_value < 0:

            return (
                f"Stock showed relative weakness "
                f"against NIFTY with RS value "
                f"of {rs_value}."
            )

        return (
            "Stock moved in line with overall "
            "market strength."
        )

    @staticmethod
    def _build_trade_construction_summary(
        trade_construction: dict
    ):

        entry_price = (
            trade_construction
            .get("entry_price")
        )

        stop_loss = (
            trade_construction
            .get("stop_loss")
        )

        target_price = (
            trade_construction
            .get("target_price")
        )

        trade_status = (
            trade_construction
            .get("trade_status")
        )

        if not entry_price:

            return (
                "Trade construction information unavailable."
            )

        return (
            f"Trade setup prepared with entry "
            f"near {entry_price}, stop loss "
            f"near {stop_loss}, and target "
            f"near {target_price}. "
            f"Trade status remained "
            f"{trade_status}."
        )

    @staticmethod
    def _build_learning_insight(
        market_context: dict,
        stock_selection_context: dict,
        trade_construction: dict
    ):

        final_market_context = (
            market_context
            .get("final_market_context")
        )

        strategy_used = (
            stock_selection_context
            .get("strategy_used")
        )

        structure_valid = (
            stock_selection_context
            .get("structure_valid")
        )

        trade_status = (
            trade_construction
            .get("trade_status")
        )

        if (
            final_market_context == "TREND_DAY"
            and structure_valid
            and trade_status == "READY"
        ):

            return (
                "This setup aligned market direction, "
                "relative strength, and trade structure, "
                "which improved the probability of "
                "successful execution."
            )

        if trade_status == "BLOCKED":

            return (
                "Trade was blocked because market "
                "conditions or structure quality "
                "did not support safe execution."
            )

        if strategy_used == "NO_TRADE":

            return (
                "Avoiding low-quality setups is an "
                "important part of disciplined "
                "intraday trading."
            )

        return (
            "Market replay should be used to study "
            "how price structure interacted with "
            "market context throughout the session."
        )