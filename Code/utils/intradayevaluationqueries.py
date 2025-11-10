from typing import List, Dict, Any, Optional
from Code.utils.db import read_sql
import pandas as pd
import math

def get_signals_with_eval(engine_key: str, trade_date: str, eval_tag: str,
                          limit: Optional[int]=None, offset: Optional[int]=0,
                          filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Returns joined rows and meta aggregates.
    Uses the exact SQL provided in the spec.
    """
    base_sql = """
    SELECT
      s.id AS signal_id,
      s.symbol,
      s.trade_date,
      s.strategy,
      s.signal_type,
      s.signal_score,
      s.entry_model AS signal_entry_model,
      s.entry_price AS signal_entry_price,
      s.stop_price AS signal_stop_price,
      s.target_price AS signal_target_price,
      s.expected_hold_days,
      s.notes AS signal_notes,
      e.eval_run_tag,
      e.entry_time AS eval_entry_time,
      e.entry_price AS eval_entry_price,
      e.stop_price AS eval_stop_price,
      e.target_price AS eval_target_price,
      e.realized_high,
      e.realized_low,
      e.close_price,
      e.realized_return,
      e.exit_price,
      e.exit_reason,
      e.days_to_exit,
      e.label_outcome,
      e.ambiguous_flag,
      e.notes AS eval_notes,
      e.created_at AS eval_created_at
    FROM strategy_signals s
    LEFT JOIN signal_evaluation_results e
      ON e.signal_id = s.id AND e.eval_run_tag = :eval_tag
    WHERE s.trade_date = :trade_date
    -- optional filters appended by caller: strategy / label / min_score / symbol LIKE
    ORDER BY s.signal_score DESC
    LIMIT :limit OFFSET :offset;
    """
    if limit is None:
        limit = 1000
    if offset is None:
        offset = 0
    params = {"eval_tag": eval_tag, "trade_date": trade_date, "limit": limit, "offset": offset}

    extra_where = []
    if filters:
        if filters.get("strategy"):
            extra_where.append("s.strategy = :f_strategy"); params["f_strategy"] = filters["strategy"]
        if "label_outcome" in filters and filters["label_outcome"] is not None:
            if filters["label_outcome"].upper() == "NOT_EVALUATED":
                extra_where.append("e.label_outcome IS NULL")
            else:
                extra_where.append("e.label_outcome = :f_label"); params["f_label"] = filters["label_outcome"]
        if "min_signal_score" in filters and filters["min_signal_score"] is not None:
            extra_where.append("s.signal_score >= :f_min_score"); params["f_min_score"] = filters["min_signal_score"]
        if filters.get("symbol_search"):
            extra_where.append("s.symbol LIKE :f_symbol_search"); params["f_symbol_search"] = f"%{filters['symbol_search']}%"

    if extra_where:
        and_clause = " AND " + " AND ".join(extra_where)
        sql = base_sql.replace("-- optional filters appended by caller: strategy / label / min_score / symbol LIKE", and_clause)
    else:
        sql = base_sql.replace("-- optional filters appended by caller: strategy / label / min_score / symbol LIKE", "")

    df = read_sql(engine_key, sql, params=params)

    def _to_native(val):
        if isinstance(val, float) and math.isnan(val):
            return None
        return val

    rows = []
    for _, r in df.iterrows():
        row = {col: _to_native(r[col]) for col in df.columns}
        rows.append(row)

    # aggregates
    agg_sql = """
    SELECT
      COUNT(*) AS total_rows,
      SUM(CASE WHEN e.label_outcome = 'win' THEN 1 ELSE 0 END) AS wins,
      SUM(CASE WHEN e.label_outcome = 'loss' THEN 1 ELSE 0 END) AS losses,
      SUM(CASE WHEN e.label_outcome = 'neutral' THEN 1 ELSE 0 END) AS neutral,
      SUM(CASE WHEN e.ambiguous_flag = 1 THEN 1 ELSE 0 END) AS ambiguous,
      AVG(e.realized_return) AS avg_realized_return
    FROM strategy_signals s
    LEFT JOIN signal_evaluation_results e
      ON e.signal_id = s.id AND e.eval_run_tag = :eval_tag
    WHERE s.trade_date = :trade_date
    """
    if extra_where:
        agg_sql = agg_sql + and_clause + ";"
    else:
        agg_sql = agg_sql + ";"

    agg_df = read_sql(engine_key, agg_sql, params={k:v for k,v in params.items() if k in ("eval_tag","trade_date") or k.startswith("f_")})
    meta = {
        "trade_date": trade_date,
        "eval_run_tag": eval_tag,
        "total_rows": int(agg_df.at[0, "total_rows"]) if not agg_df.empty and agg_df.at[0, "total_rows"] is not None else 0,
        "wins": int(agg_df.at[0, "wins"]) if not agg_df.empty and agg_df.at[0, "wins"] is not None else 0,
        "losses": int(agg_df.at[0, "losses"]) if not agg_df.empty and agg_df.at[0, "losses"] is not None else 0,
        "neutral": int(agg_df.at[0, "neutral"]) if not agg_df.empty and agg_df.at[0, "neutral"] is not None else 0,
        "ambiguous": int(agg_df.at[0, "ambiguous"]) if not agg_df.empty and agg_df.at[0, "ambiguous"] is not None else 0,
        "avg_realized_return": None if agg_df.empty or agg_df.at[0, "avg_realized_return"] is None else float(agg_df.at[0, "avg_realized_return"])
    }
    return {"meta": meta, "rows": rows}


def list_eval_tags(engine_key: str) -> List[str]:
    q = "SELECT DISTINCT eval_run_tag FROM signal_evaluation_results ORDER BY eval_run_tag DESC;"
    df = read_sql(engine_key, q)
    if df.empty:
        return []
    return [str(x) for x in df["eval_run_tag"].tolist()]


def diff_tags_summary(engine_key: str, trade_date: str, base_tag: str, compare_tag: str) -> Dict[str, Any]:
    q = """
    SELECT
      s.id AS signal_id,
      s.symbol,
      e_base.label_outcome AS base_label,
      e_cmp.label_outcome AS cmp_label
    FROM strategy_signals s
    LEFT JOIN signal_evaluation_results e_base
      ON e_base.signal_id = s.id AND e_base.eval_run_tag = :base_tag
    LEFT JOIN signal_evaluation_results e_cmp
      ON e_cmp.signal_id = s.id AND e_cmp.eval_run_tag = :compare_tag
    WHERE s.trade_date = :trade_date;
    """
    df = read_sql(engine_key, q, params={"base_tag": base_tag, "compare_tag": compare_tag, "trade_date": trade_date})
    df = df.where(pd.notnull(df), None)

    total = int(len(df))
    changes = []
    changed_count = 0
    for _, r in df.iterrows():
        base = r["base_label"]
        cmp = r["cmp_label"]
        if base != cmp:
            changed_count += 1
            changes.append({
                "signal_id": int(r["signal_id"]),
                "symbol": r["symbol"],
                "base": base,
                "cmp": cmp
            })
    return {
        "trade_date": trade_date,
        "base_tag": base_tag,
        "compare_tag": compare_tag,
        "total": total,
        "changed": changed_count,
        "changes": changes
    }
