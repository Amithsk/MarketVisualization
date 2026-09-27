"""Short-transaction persistence for Replay Coach questions and answers."""
import json
from sqlalchemy import text


class ReplayCoachMessageRepository:
    @staticmethod
    def load_completed_analysis_snapshot(db, analysis_id: int):
        row=db.execute(text("SELECT id,status,analysis_json,evidence_json,evidence_hash,context_version,prompt_version,schema_version,coach_schema_version,model FROM replay_coach_analysis WHERE id=:id"), {"id":analysis_id}).mappings().first()
        if not row or row["status"] != "COMPLETED": return None
        result=dict(row)
        for key in ("analysis_json","evidence_json"):
            if isinstance(result[key], str): result[key]=json.loads(result[key])
        return result

    @staticmethod
    def find_by_client_request_id(db, analysis_id, client_request_id):
        return db.execute(text("SELECT * FROM replay_coach_message WHERE analysis_id=:analysis_id AND client_request_id=:client_request_id"), {"analysis_id":analysis_id,"client_request_id":client_request_id}).mappings().first()

    @classmethod
    def claim_user_message(cls, db, analysis_id, question, client_request_id):
        parent=db.execute(text("SELECT id,status FROM replay_coach_analysis WHERE id=:id FOR UPDATE"), {"id":analysis_id}).mappings().first()
        if not parent or parent["status"] != "COMPLETED": db.rollback(); return None, "ANALYSIS_UNAVAILABLE"
        existing=cls.find_by_client_request_id(db, analysis_id, client_request_id)
        if existing: db.commit(); return existing, f"EXISTING_{existing['status']}"
        next_sequence=db.execute(text("SELECT COALESCE(MAX(sequence_number),0)+1 FROM replay_coach_message WHERE analysis_id=:id FOR UPDATE"), {"id":analysis_id}).scalar_one()
        db.execute(text("INSERT INTO replay_coach_message (analysis_id,sequence_number,role,content,status,client_request_id) VALUES (:analysis_id,:sequence_number,'USER',:content,'PROCESSING',:client_request_id)"), {"analysis_id":analysis_id,"sequence_number":next_sequence,"content":question,"client_request_id":client_request_id})
        db.commit(); return cls.find_by_client_request_id(db, analysis_id, client_request_id), "CREATED"

    @staticmethod
    def get_assistant_reply(db, user_message_id):
        return db.execute(text("SELECT * FROM replay_coach_message WHERE reply_to_message_id=:id AND role='ASSISTANT'"), {"id":user_message_id}).mappings().first()

    @classmethod
    def complete_with_assistant_message(cls, db, analysis_id, user_message_id, answer, intent, evidence_times, response_id, model, prompt_version, usage):
        db.execute(text("SELECT id FROM replay_coach_analysis WHERE id=:id FOR UPDATE"), {"id":analysis_id})
        user=db.execute(text("SELECT * FROM replay_coach_message WHERE id=:id AND analysis_id=:analysis_id FOR UPDATE"), {"id":user_message_id,"analysis_id":analysis_id}).mappings().first()
        if not user: db.rollback(); raise ValueError("user message not found")
        existing=cls.get_assistant_reply(db,user_message_id)
        if existing: db.commit(); return existing
        if user["role"] != "USER" or user["status"] != "PROCESSING": db.rollback(); raise ValueError("message is not processing user question")
        sequence=db.execute(text("SELECT COALESCE(MAX(sequence_number),0)+1 FROM replay_coach_message WHERE analysis_id=:id FOR UPDATE"), {"id":analysis_id}).scalar_one()
        db.execute(text("INSERT INTO replay_coach_message (analysis_id,sequence_number,role,content,status,reply_to_message_id,inferred_intent,evidence_times_json,provider_response_id,model,prompt_version,input_tokens,output_tokens,total_tokens,completed_at) VALUES (:analysis_id,:sequence,'ASSISTANT',:answer,'COMPLETED',:user_id,:intent,CAST(:times AS JSON),:response_id,:model,:prompt_version,:input_tokens,:output_tokens,:total_tokens,CURRENT_TIMESTAMP(6))"), {"analysis_id":analysis_id,"sequence":sequence,"answer":answer,"user_id":user_message_id,"intent":intent,"times":json.dumps(evidence_times),"response_id":response_id,"model":model,"prompt_version":prompt_version,"input_tokens":usage.get("input_tokens"),"output_tokens":usage.get("output_tokens"),"total_tokens":usage.get("total_tokens")})
        db.execute(text("UPDATE replay_coach_message SET status='COMPLETED', completed_at=CURRENT_TIMESTAMP(6) WHERE id=:id"), {"id":user_message_id}); db.commit()
        return cls.get_assistant_reply(db,user_message_id)

    @staticmethod
    def fail_user_message(db, user_message_id, safe_error_code, failure_reason=None):
        db.execute(text("UPDATE replay_coach_message SET status='FAILED',safe_error_code=:code,failure_reason=:reason,completed_at=CURRENT_TIMESTAMP(6),updated_at=CURRENT_TIMESTAMP(6) WHERE id=:id AND role='USER' AND status='PROCESSING'"), {"id":user_message_id,"code":safe_error_code[:100],"reason":(failure_reason or safe_error_code)[:1000]}); db.commit()

    @staticmethod
    def list_messages_by_analysis_id(db, analysis_id):
        return db.execute(text("SELECT m.*, f.id feedback_id,f.rating feedback_rating,f.reason_code feedback_reason_code,f.comment feedback_comment FROM replay_coach_message m LEFT JOIN replay_coach_message_feedback f ON f.assistant_message_id=m.id WHERE m.analysis_id=:id ORDER BY m.sequence_number ASC"), {"id":analysis_id}).mappings().all()
