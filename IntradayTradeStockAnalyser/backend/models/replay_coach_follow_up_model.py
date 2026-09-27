"""Contracts for persisted Replay Coach follow-up conversations."""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ReplayCoachMessageRole(str, Enum): USER = "USER"; ASSISTANT = "ASSISTANT"
class ReplayCoachMessageStatus(str, Enum): PROCESSING = "PROCESSING"; COMPLETED = "COMPLETED"; FAILED = "FAILED"
class ReplayCoachMessageClaimResult(str, Enum): CREATED = "CREATED"; EXISTING_PROCESSING = "EXISTING_PROCESSING"; EXISTING_COMPLETED = "EXISTING_COMPLETED"; EXISTING_FAILED = "EXISTING_FAILED"
class ReplayCoachFollowUpIntent(str, Enum):
    EXECUTED_TRADE_EXPLANATION="EXECUTED_TRADE_EXPLANATION"; FULL_SESSION_PLAN_EXPLANATION="FULL_SESSION_PLAN_EXPLANATION"; PLAN_COMPARISON="PLAN_COMPARISON"; CALCULATION_EXPLANATION="CALCULATION_EXPLANATION"; CHART_EVIDENCE="CHART_EVIDENCE"; TRADING_CONCEPT="TRADING_CONCEPT"; NEXT_TRADE_LESSON="NEXT_TRADE_LESSON"; CLARIFICATION_REQUIRED="CLARIFICATION_REQUIRED"; GENERAL_FOLLOW_UP="GENERAL_FOLLOW_UP"
class ReplayCoachFeedbackRating(str, Enum): HELPFUL="HELPFUL"; NEEDS_IMPROVEMENT="NEEDS_IMPROVEMENT"
class ReplayCoachFeedbackReason(str, Enum):
    CLEAR_NUMERICAL_EXPLANATION="CLEAR_NUMERICAL_EXPLANATION"; CLEAR_CHART_REFERENCE="CLEAR_CHART_REFERENCE"; GOOD_PLAN_COMPARISON="GOOD_PLAN_COMPARISON"; EASY_TO_UNDERSTAND="EASY_TO_UNDERSTAND"; ACTIONABLE_LESSON="ACTIONABLE_LESSON"; CORRECT_CALCULATION="CORRECT_CALCULATION"; DID_NOT_ANSWER="DID_NOT_ANSWER"; TOO_GENERIC="TOO_GENERIC"; MISSING_PRICES_OR_CALCULATIONS="MISSING_PRICES_OR_CALCULATIONS"; MISSING_CHART_TIMES="MISSING_CHART_TIMES"; INCORRECT_FACT_OR_CALCULATION="INCORRECT_FACT_OR_CALCULATION"; CONFUSED_EXECUTED_AND_SUGGESTED_PLAN="CONFUSED_EXECUTED_AND_SUGGESTED_PLAN"; USED_FUTURE_INFORMATION="USED_FUTURE_INFORMATION"; DIFFICULT_TO_UNDERSTAND="DIFFICULT_TO_UNDERSTAND"; TOO_MUCH_INFORMATION="TOO_MUCH_INFORMATION"; OTHER="OTHER"

HELPFUL_REASONS={"CLEAR_NUMERICAL_EXPLANATION","CLEAR_CHART_REFERENCE","GOOD_PLAN_COMPARISON","EASY_TO_UNDERSTAND","ACTIONABLE_LESSON","CORRECT_CALCULATION","OTHER"}
NEEDS_IMPROVEMENT_REASONS={"DID_NOT_ANSWER","TOO_GENERIC","MISSING_PRICES_OR_CALCULATIONS","MISSING_CHART_TIMES","INCORRECT_FACT_OR_CALCULATION","CONFUSED_EXECUTED_AND_SUGGESTED_PLAN","USED_FUTURE_INFORMATION","DIFFICULT_TO_UNDERSTAND","TOO_MUCH_INFORMATION","OTHER"}

class FollowUpQuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    client_request_id: str = Field(min_length=1, max_length=100)
    @field_validator("question", "client_request_id")
    @classmethod
    def trimmed(cls, value):
        value=value.strip()
        if not value: raise ValueError("must not be empty")
        return value

class FollowUpProviderAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    answer: str = Field(min_length=1, max_length=12000)
    inferred_intent: ReplayCoachFollowUpIntent
    evidence_times: list[str] = Field(default_factory=list)
    @field_validator("answer")
    @classmethod
    def answer_trimmed(cls, value):
        value=value.strip()
        if not value: raise ValueError("answer must not be empty")
        return value

class ReplayCoachFeedbackRequest(BaseModel):
    rating: ReplayCoachFeedbackRating
    reason_code: Optional[ReplayCoachFeedbackReason] = None
    comment: Optional[str] = Field(default=None, max_length=12000)
    @field_validator("comment")
    @classmethod
    def comment_trimmed(cls, value): return value.strip() if value is not None else None
    @model_validator(mode="after")
    def reason_matches_rating(self):
        if self.reason_code:
            allowed=HELPFUL_REASONS if self.rating == ReplayCoachFeedbackRating.HELPFUL else NEEDS_IMPROVEMENT_REASONS
            if self.reason_code.value not in allowed: raise ValueError("reason_code is not valid for rating")
        return self
