import pytest
from pydantic import ValidationError
from backend.models.replay_coach_follow_up_model import FollowUpQuestionRequest, ReplayCoachFeedbackRequest

def test_question_requires_trimmed_content_and_client_request_id():
    assert FollowUpQuestionRequest(question="  Why? ", client_request_id="request-1").question == "Why?"
    with pytest.raises(ValidationError): FollowUpQuestionRequest(question=" ", client_request_id="request-1")

def test_feedback_reason_must_match_rating():
    with pytest.raises(ValidationError): ReplayCoachFeedbackRequest(rating="HELPFUL", reason_code="TOO_GENERIC")
    assert ReplayCoachFeedbackRequest(rating="NEEDS_IMPROVEMENT", reason_code="OTHER", comment="Changed completely").comment == "Changed completely"
