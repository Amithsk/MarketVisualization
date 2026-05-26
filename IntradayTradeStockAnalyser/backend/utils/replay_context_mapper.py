#IntradayTradeStockAnalyser/backend/utils/replay_context_mapper.py


class ReplayContextMapper:

    @staticmethod
    def map_market_context(
        final_market_context: str
    ):

        mapping = {

            "TREND_DAY": {
                "label": "Trend Day",
                "badge": "TREND",
                "color": "green"
            },

            "RANGE_UNCERTAIN_DAY": {
                "label": "Range / Uncertain Day",
                "badge": "RANGE",
                "color": "yellow"
            },

            "NO_TRADE_DAY": {
                "label": "No Trade Day",
                "badge": "NO TRADE",
                "color": "red"
            }

        }

        return mapping.get(
            final_market_context,
            {
                "label": "Unknown",
                "badge": "UNKNOWN",
                "color": "gray"
            }
        )

    @staticmethod
    def map_trade_permission(
        trade_permission: str
    ):

        mapping = {

            "YES": {
                "label": "Trade Allowed",
                "badge": "TRADE ALLOWED",
                "color": "green"
            },

            "LIMITED": {
                "label": "Limited Trading",
                "badge": "LIMITED",
                "color": "yellow"
            },

            "NO": {
                "label": "Trade Restricted",
                "badge": "NO TRADE",
                "color": "red"
            }

        }

        return mapping.get(
            trade_permission,
            {
                "label": "Unknown",
                "badge": "UNKNOWN",
                "color": "gray"
            }
        )

    @staticmethod
    def map_vwap_state(
        vwap_state: str
    ):

        mapping = {

            "CLEAN": {
                "label": "VWAP Clean",
                "description":
                    "Price respected VWAP with "
                    "stable directional movement.",
                "color": "green"
            },

            "CAUTION": {
                "label": "VWAP Caution",
                "description":
                    "VWAP behavior showed mixed "
                    "directional conviction.",
                "color": "yellow"
            },

            "CHOPPY": {
                "label": "VWAP Choppy",
                "description":
                    "Frequent VWAP crosses indicated "
                    "unstable market structure.",
                "color": "red"
            }

        }

        return mapping.get(
            vwap_state,
            {
                "label": "Unknown VWAP State",
                "description":
                    "VWAP interpretation unavailable.",
                "color": "gray"
            }
        )

    @staticmethod
    def map_relative_strength(
        rs_value: float
    ):

        if rs_value is None:

            return {

                "label": "RS Unknown",

                "strength": "UNKNOWN",

                "color": "gray"
            }

        if rs_value > 0:

            return {

                "label": "RS Strong",

                "strength": "STRONG",

                "color": "green"
            }

        if rs_value < 0:

            return {

                "label": "RS Weak",

                "strength": "WEAK",

                "color": "red"
            }

        return {

            "label": "RS Neutral",

            "strength": "NEUTRAL",

            "color": "yellow"
        }

    @staticmethod
    def map_strategy(
        strategy_used: str
    ):

        mapping = {

            "MOMENTUM": {
                "label": "Momentum",
                "description":
                    "Momentum strategy selected due "
                    "to directional strength and "
                    "market participation."
            },

            "GAP_FOLLOW": {
                "label": "Gap Follow",
                "description":
                    "Gap follow strategy selected "
                    "because opening structure "
                    "supported continuation."
            },

            "NO_TRADE": {
                "label": "No Trade",
                "description":
                    "No valid trading setup was "
                    "identified."
            }

        }

        return mapping.get(
            strategy_used,
            {
                "label": "Unknown Strategy",
                "description":
                    "Strategy interpretation unavailable."
            }
        )

    @staticmethod
    def map_volatility_state(
        volatility_state: str
    ):

        mapping = {

            "LOW": {
                "label": "Low Volatility",
                "description":
                    "Market movement remained compressed.",
                "color": "yellow"
            },

            "NORMAL": {
                "label": "Normal Volatility",
                "description":
                    "Volatility supported stable "
                    "intraday execution.",
                "color": "green"
            },

            "EXCESSIVE": {
                "label": "Excessive Volatility",
                "description":
                    "Market movement was aggressive "
                    "and required caution.",
                "color": "red"
            }

        }

        return mapping.get(
            volatility_state,
            {
                "label": "Unknown Volatility",
                "description":
                    "Volatility interpretation unavailable.",
                "color": "gray"
            }
        )

    @staticmethod
    def map_structure_validity(
        structure_valid: bool
    ):

        if structure_valid:

            return {

                "label": "Structure Valid",

                "description":
                    "Price structure supported "
                    "trade continuation.",

                "color": "green"
            }

        return {

            "label": "Structure Weak",

            "description":
                "Price structure lacked confirmation.",

            "color": "red"
        }

    @staticmethod
    def map_trade_status(
        trade_status: str
    ):

        mapping = {

            "READY": {
                "label": "Trade Ready",
                "description":
                    "Trade setup passed validation "
                    "checks and was executable.",
                "color": "green"
            },

            "BLOCKED": {
                "label": "Trade Blocked",
                "description":
                    "Trade setup failed validation "
                    "or market filters.",
                "color": "red"
            }

        }

        return mapping.get(
            trade_status,
            {
                "label": "Unknown Trade Status",
                "description":
                    "Trade status interpretation unavailable.",
                "color": "gray"
            }
        )