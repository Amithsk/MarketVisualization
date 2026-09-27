from backend.services.replay_coach_follow_up_service import ReplayCoachFollowUpService


def _row(identifier, sequence, role, status, reply=None):
    return {"id": identifier, "analysis_id": 56, "sequence_number": sequence, "role": role, "status": status, "reply_to_message_id": reply, "content": f"message-{identifier}"}


def test_context_includes_only_completed_pairs_and_current_question_once():
    current = _row(7, 7, "USER", "PROCESSING")
    history = [_row(1, 1, "USER", "COMPLETED"), _row(2, 2, "ASSISTANT", "COMPLETED", 1), _row(3, 3, "USER", "FAILED"), _row(4, 4, "USER", "PROCESSING"), _row(5, 5, "USER", "COMPLETED"), _row(6, 6, "ASSISTANT", "FAILED", 5), current]
    snapshot = {"analysis_json": {"executed_trade_analysis": {}, "best_full_session_plan": {}, "key_learning": {}, "limitations": []}, "evidence_json": {}, "evidence_hash": "hash", "context_version": "v"}
    context = ReplayCoachFollowUpService._context(snapshot, history, current)
    assert context["SECTION 3 — PREVIOUS COMPLETED CONVERSATION"] == [{"role": "USER", "content": "message-1"}, {"role": "ASSISTANT", "content": "message-2"}]
    assert context["SECTION 4 — CURRENT QUESTION"] == "message-7"
