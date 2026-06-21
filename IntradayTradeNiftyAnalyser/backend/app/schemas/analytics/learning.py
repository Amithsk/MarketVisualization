#IntradayTradeNiftyAnalyser/backend/app/schemas/analytics/learning.py
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ====================================================
# SUMMARY
# ====================================================

class SummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trade_date: date

    summary_text: str

    analysis_status: str

    rule_config_version: str

    created_at: datetime


# ====================================================
# SUGGESTION
# ====================================================

class SuggestionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trade_date: date

    rule_name: str

    current_value: float

    suggested_value: float

    support_metric: str

    impact: float

    confidence: float

    priority: str

    created_at: datetime


# ====================================================
# JOB STATUS
# ====================================================

class JobStatusSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    execution_id: str

    trade_date: date

    status: str

    start_time: datetime

    end_time: Optional[datetime] = None

    last_updated_at: datetime


# ====================================================
# RESPONSE
# ====================================================

class LearningResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trade_date: str

    summary: Optional[SummarySchema] = None

    suggestions: list[SuggestionSchema] = []

    job_status: Optional[JobStatusSchema] = None