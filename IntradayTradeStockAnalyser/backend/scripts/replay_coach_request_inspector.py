"""Manual dry-run: write the exact Replay Coach request without calling OpenAI."""
import argparse
import hashlib
import json
from pathlib import Path

from backend.services.replay_coach_config import replay_coach_max_output_tokens
from backend.services.replay_coach_context_service import ReplayCoachContextService
from backend.services.replay_coach_openai_service import ReplayCoachOpenAIService
from backend.services.replay_service import ReplayService
from backend.utils.database import SessionLocal
from sqlalchemy import text

EXPECTED_KEYS = {"model", "input", "text", "max_output_tokens"}


def validate(context, request, trade_date, symbol):
    """Return paths only; never repair evidence or request data."""
    errors = []
    if not request.get("model"): errors.append("model")
    if request.get("max_output_tokens") != 16000: errors.append("max_output_tokens")
    if set(request) != EXPECTED_KEYS: errors.append("$")
    inputs = request.get("input")
    if not isinstance(inputs, list) or not inputs: errors.append("input")
    elif len(inputs) < 2 or not inputs[0].get("content"): errors.append("input.0.content")
    elif not inputs[1].get("content"): errors.append("input.1.content")
    if context.get("trade_date") != trade_date: errors.append("context.trade_date")
    if context.get("stock", {}).get("symbol", "").upper().removeprefix("NSE:") != symbol.upper().removeprefix("NSE:"): errors.append("context.stock.symbol")
    trade = context.get("executed_trade", {})
    for field in ("trade_id", "side", "entry_timestamp", "exit_timestamp"):
        if not trade.get(field): errors.append(f"context.executed_trade.{field}")
    if trade.get("side") != "SELL": errors.append("context.executed_trade.side")
    if len(context.get("stock", {}).get("candles", [])) != 72: errors.append("context.stock.candles")
    if len(context.get("market", {}).get("candles", [])) != 73: errors.append("context.market.candles")
    try:
        evidence = inputs[1]["content"]; json.loads(evidence)
        if evidence.count('"candles"') != 2: errors.append("input.1.content.evidence_duplicate")
    except (TypeError, ValueError, IndexError): errors.append("input.1.content")
    format_ = request.get("text", {}).get("format", {})
    if format_.get("name") != ReplayCoachOpenAIService.SCHEMA_NAME: errors.append("text.format.name")
    if format_.get("strict") is not True: errors.append("text.format.strict")
    try:
        schema = format_["schema"]; rendered = json.dumps(schema)
        if "oneOf" in rendered: errors.append("text.format.schema.oneOf")
        if "discriminator" in rendered: errors.append("text.format.schema.discriminator")
    except (KeyError, TypeError, ValueError): errors.append("text.format.schema")
    return errors


def build_request(trade_date, symbol):
    db = SessionLocal()
    try:
        replay = ReplayService.get_replay_data(db, trade_date, symbol)
        context = ReplayCoachContextService.build_context(replay, trade_date)
    finally:
        db.close()
    cap, _ = replay_coach_max_output_tokens()
    evidence = json.dumps(context, default=str)
    return context, ReplayCoachOpenAIService.request_kwargs(ReplayCoachOpenAIService.requested_model(), evidence, cap)


def build_persisted_request(analysis_id):
    """Read only the persisted evidence; never touches ReplayStore or OpenAI."""
    db = SessionLocal()
    try:
        row = db.execute(text("""SELECT id, trade_date, symbol, normalized_symbol, trade_id,
            context_version, evidence_hash, evidence_json, prompt_version,
            coach_schema_version, requested_model FROM replay_coach_analysis WHERE id=:id"""), {"id": analysis_id}).mappings().first()
    finally:
        db.close()
    if not row: raise SystemExit("INSPECTOR_ANALYSIS_NOT_FOUND")
    try: context = json.loads(row["evidence_json"] if isinstance(row["evidence_json"], str) else json.dumps(row["evidence_json"]))
    except (TypeError, ValueError): raise SystemExit("INSPECTOR_EVIDENCE_JSON_INVALID")
    canonical = json.dumps(context, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    if hashlib.sha256(canonical.encode("utf-8")).hexdigest() != row["evidence_hash"]: raise SystemExit("INSPECTOR_EVIDENCE_HASH_MISMATCH")
    cap, _ = replay_coach_max_output_tokens()
    return context, ReplayCoachOpenAIService.request_kwargs(row["requested_model"], json.dumps(context, default=str), cap), row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trade-date"); parser.add_argument("--symbol"); parser.add_argument("--analysis-id", type=int)
    parser.add_argument("--output", required=True); parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(); target = Path(args.output)
    if target.exists() and not args.overwrite: raise SystemExit("Output exists; use --overwrite.")
    if args.analysis_id is not None:
        context, request, row = build_persisted_request(args.analysis_id)
        args.trade_date, args.symbol = str(row["trade_date"]), row["normalized_symbol"] or row["symbol"]
    else:
        if not args.trade_date or not args.symbol: raise SystemExit("Provide --analysis-id or both --trade-date and --symbol.")
        context, request = build_request(args.trade_date, args.symbol)
        row = {"id": None, "context_version": context.get("context_version"), "prompt_version": ReplayCoachOpenAIService.PROMPT_VERSION, "coach_schema_version": ReplayCoachOpenAIService.COACH_SCHEMA_VERSION}
    errors = validate(context, request, args.trade_date, args.symbol)
    if errors: raise SystemExit("Validation errors: " + ", ".join(errors))
    payload = json.dumps(request, ensure_ascii=False, separators=(",", ":"))
    target.write_text(payload, encoding="utf-8")
    schema_bytes = len(json.dumps(request["text"]["format"]["schema"], separators=(",", ":")).encode())
    print(f"analysis_id={row['id']} trade_date={args.trade_date} symbol={args.symbol} trade_id={context['executed_trade']['trade_id']} evidence_hash_matches=True context_version={row['context_version']} prompt_version={row['prompt_version']} coach_schema_version={row['coach_schema_version']} stock_candle_count={len(context['stock']['candles'])} market_candle_count={len(context['market']['candles'])} executed_trade_present=True executed_trade_side={context['executed_trade']['side']} model={request['model']} max_output_tokens={request['max_output_tokens']} input_character_count={sum(len(item['content']) for item in request['input'])} input_byte_count={sum(len(item['content'].encode()) for item in request['input'])} schema_name={request['text']['format']['name']} schema_bytes={schema_bytes} request_fingerprint={hashlib.sha256(payload.encode()).hexdigest()} output_file={target.resolve()} provider_called=False")

if __name__ == "__main__": main()
