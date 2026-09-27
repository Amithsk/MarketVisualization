from sqlalchemy import text

class ReplayCoachFeedbackRepository:
    @staticmethod
    def get_by_assistant_message_id(db, assistant_message_id):
        return db.execute(text("SELECT * FROM replay_coach_message_feedback WHERE assistant_message_id=:id"), {"id":assistant_message_id}).mappings().first()
    @classmethod
    def upsert_for_assistant_message(cls, db, assistant_message_id, feedback):
        message=db.execute(text("SELECT m.id,m.role,m.status,m.reply_to_message_id,u.role user_role FROM replay_coach_message m LEFT JOIN replay_coach_message u ON u.id=m.reply_to_message_id WHERE m.id=:id FOR UPDATE"), {"id":assistant_message_id}).mappings().first()
        if not message or message["role"] != "ASSISTANT" or message["status"] != "COMPLETED" or message["user_role"] != "USER":
            db.rollback(); raise ValueError("feedback requires a completed assistant answer")
        db.execute(text("INSERT INTO replay_coach_message_feedback (assistant_message_id,rating,reason_code,comment) VALUES (:id,:rating,:reason,:comment) ON DUPLICATE KEY UPDATE rating=VALUES(rating),reason_code=VALUES(reason_code),comment=VALUES(comment),updated_at=CURRENT_TIMESTAMP(6)"), {"id":assistant_message_id,"rating":feedback.rating.value,"reason":feedback.reason_code.value if feedback.reason_code else None,"comment":feedback.comment})
        db.commit(); return cls.get_by_assistant_message_id(db,assistant_message_id)
